import logging
import os
import sys
import re
from modules import shellhelper
from modules.entities import Csv, csv
from modules.exceptions import AbsentActivityException, UserExitException

FATAL_LOG_LINE1 = "AndroidRuntime: FATAL EXCEPTION: main"
FATAL_LOG_LINE2 = "AndroidRuntime: Process: {}"

def run_main_activity(apk):
    main_activity_name = apk.activity
    if main_activity_name is None:
        raise AbsentActivityException
    #logging.debug(f'Manifest path: {apk.manifest.pathAndroidManifest}')
    shellhelper.clean_log()
    shellhelper.start_activity_explicitly(apk.package, main_activity_name)


def read_status_from_experimenter():
    print("Press: c - crashed, s - successed, e - exit")
    key = wait_key()
    while key != 's' and key != 'c' and key != 'e':
        print("Press: c - crashed, s - successed, e - exit")
        key = wait_key()
    if key == 'e':
        raise UserExitException()
    return key


def report_status(app, status):
    csv.write_row(app, status)
    if status == 'c':
        #pass
        shellhelper.save_log(app)

def report_error_automatically(app):
    log_path = shellhelper.save_log(app)
    text = shellhelper.read_log(log_path)
    error = check_error(text, app)
    if error:
        csv.write_row(app, "fatal")
        return True
    csv.write_row(app, "ok")
    return False

def check_error(text, app):
    '''Checks is there is Fatal exception message in the log file.'''
    re_line1 = re.search(FATAL_LOG_LINE1, text)
    pattern_line2 = re.escape(FATAL_LOG_LINE2.format(app))
    re_line2 = re.search(pattern_line2, text)
    return (re_line1 is not None) & (re_line2 is not None)

def close_crash_report():
    csv.close()


def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result.decode('utf-8')
