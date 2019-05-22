import os
import sys
import re
import time
import subprocess
from loguru import logger
from modules import config
from modules import shellhelper
from modules.entities import Csv
from modules.done_list_handler import DoneListHandler
from modules.exceptions import AbsentActivityException, UserExitException

FATAL_LOG_LINE1 = "FATAL EXCEPTION:"
FATAL_LOG_LINE2 = "Process: {}"


class Agent(object):
    def __init__(self, output_dir):
        if not os.path.exists(output_dir):
            message = "Create \'{}\' in current directory? [y/n]: " if output_dir == config.OUTPUT_DIR else "Create \'{}\' directory? [y/n]: "
            user_choice = input(message.format(output_dir))
            if user_choice.lower() in ["y", "yes"]:
                os.makedirs(output_dir)
            elif user_choice.lower() in ["n", "no"]:
                print("Aborting operation!")
                raise UserExitException()
            else:
                print("Your choice is not correct! Exiting!")
                raise UserExitException()
        self.output_dir = output_dir
        self.logs_dir = os.path.join(output_dir, config.LOGS_DIR)
        self.done_list_path = os.path.join(output_dir, config.DONE_LIST)
        self.done_list_handler = DoneListHandler(self.done_list_path)
        self.csv_report = Csv(os.path.join(output_dir, config.CRASHES_CSV))

    def get_done_list_handler(self):
        return self.done_list_handler

    def run(self, apk):
        pass

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

    @staticmethod
    def wait_for_boot():
        cmd = "adb shell getprop dev.bootcomplete"
        res = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
        while res != '1':
            logger.info("wait for devices")
            time.sleep(5)
            comm = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE).communicate()
            if len(comm) > 0 and comm[0] != None:
                res = comm[0].strip()


class ActivityAgent(Agent):
    def __init__(self, output_dir):
        super().__init__(output_dir)

    def run(self, apk):
        main_activity_name = apk.activity
        if main_activity_name is None:
            raise AbsentActivityException
        shellhelper.clean_log()
        shellhelper.start_activity_explicitly(apk.package, main_activity_name)


class MonkeyAgent(Agent):
    def __init__(self, output_dir, seed, throttle, event_num):
        super().__init__(output_dir)
        self.seed = seed
        self.throttle = throttle
        self.event_num = event_num

    def run(self, apk):
        shellhelper.run_monkey(apk.package, self.seed, self.throttle,
                               self.event_num)
