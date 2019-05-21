from loguru import logger
import os
import sys
import re
from modules import config
from modules import shellhelper
from modules.entities import Csv
from modules.done_list_handler import DoneListHandler
from modules.exceptions import AbsentActivityException, UserExitException

FATAL_LOG_LINE1 = "FATAL EXCEPTION:"
FATAL_LOG_LINE2 = "Process: {}"

class Agent(object):
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.logs_dir = os.path.join(output_dir, config.LOGS_DIR)
        self.done_list_path = os.path.join(output_dir, config.DONE_LIST)
        self.done_list_handler = DoneListHandler(self.done_list_path)
        self.csv_report = Csv(os.path.join(output_dir, config.CRASHES_CSV))

    def get_done_list_handler(self):
        return self.done_list_handler
        
    @staticmethod
    def run_main_activity(apk):
        main_activity_name = apk.activity
        if main_activity_name is None:
            raise AbsentActivityException
        shellhelper.clean_log()
        shellhelper.start_activity_explicitly(apk.package, main_activity_name)

    @staticmethod
    def run_monkey_tester(package, seed, throttle, event_num):
        shellhelper.run_monkey(package, seed, throttle, event_num)

    @staticmethod
    def read_status_from_experimenter():
        print("Press: c - crashed, s - successed, e - exit")
        key = Agent.wait_key()
        while key != 's' and key != 'c' and key != 'e':
            print("Press: c - crashed, s - successed, e - exit")
            key = Agent.wait_key()
        if key == 'e':
            raise UserExitException()
        return key

    def report_status(self, app, status, api_level):
        self.csv_report.write_row(app, status)
        if status == 'c':
            #pass
            shellhelper.save_log(self.logs_dir, app, api_level)

    def report_error_automatically(self, app, api_level):
        log_path = shellhelper.save_log(self.logs_dir, app, api_level)
        text = shellhelper.read_log(log_path)
        error = self.check_error(text, app)
        if error:
            self.csv_report.write_row(app, "fatal")
            return True
        self.csv_report.write_row(app, "ok")
        return False


    @staticmethod
    def check_error(text, app):
        '''Checks is there is Fatal exception message in the log file.'''
        re_line1 = re.search(FATAL_LOG_LINE1, text)
        pattern_line2 = re.escape(FATAL_LOG_LINE2.format(app))
        re_line2 = re.search(pattern_line2, text)
        return (re_line1 is not None) & (re_line2 is not None)

    def close_crash_report(self):
        self.csv_report.close()

    @staticmethod
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
