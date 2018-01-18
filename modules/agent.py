import logging
import os
import sys

from modules import adbhelper
from modules.entities import Csv

csv = Csv()


def run_main_activity(apk):
    main_activity_name = apk.manifest.getMainActivity()
    logging.debug(f'Manifest path: {apk.manifest.pathAndroidManifest}')
    adbhelper.start_activity_explicitly(apk.manifest.packageName, main_activity_name)


def register_crash(app, status):
    csv.write_row(app, status)


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
