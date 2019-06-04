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


class Reporter(object):
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.create_output_dir(output_dir)

    def create_output_dir(self, path):
        if not os.path.exists(path):
            message = "Create \'{}\' in current directory? [y/n]: " if path == config.OUTPUT_DIR else "Create \'{}\' directory? [y/n]: "
            user_choice = input(message.format(path))
            if user_choice.lower() in ["y", "yes"]:
                os.makedirs(path)
            elif user_choice.lower() in ["n", "no"]:
                print("Aborting operation!")
                raise UserExitException()
            else:
                print("Your choice is not correct! Exiting!")
                raise UserExitException()

    def done_status(self, name, status):
        pass

    def report_status(self, app, status):
        pass

    def save_log(self, app):
        shellhelper.save_log(self.output_dir, app)

    def report_error(self, path, app):
        pass


class BundleReporter(Reporter):
    def __init__(self, output_dir):
        super().__init__(output_dir)
        self.logs_dir = os.path.join(output_dir, config.LOGS_DIR)
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        self.done_list_path = os.path.join(output_dir, config.DONE_LIST)
        self.done_list_handler = DoneListHandler(self.done_list_path)
        self.csv_report = Csv(os.path.join(output_dir, config.CRASHES_CSV))

    def done_status(self, name, status):
        self.done_list_handler.write(name, status)

    def close_crash_report(self):
        self.csv_report.close()

    def report_status(self, app, status):
        self.csv_report.write_row(app, status)
        if status == 'c':
            #pass
            shellhelper.save_log(self.output_dir, app)

    def save_log(self, app):
        return shellhelper.save_log(self.logs_dir, app)

    @staticmethod
    def check_error(text, app):
        '''Checks is there is Fatal exception message in the log file.'''
        re_line1 = re.search(FATAL_LOG_LINE1, text)
        pattern_line2 = re.escape(FATAL_LOG_LINE2.format(app))
        re_line2 = re.search(pattern_line2, text)
        return (re_line1 is not None) & (re_line2 is not None)

    def report_error(self, path, app):
        text = shellhelper.read_log(path)
        error = self.check_error(text, app)
        if error:
            self.csv_report.write_row(app, "fatal")
            return
        self.csv_report.write_row(app, "ok")
        return

    def report_error_automatically(self, app):
        log_path = self.save_log(app)
        self.report_error(log_path, app)
        return log_path


class Agent(object):
    def __init__(self):
        pass

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
    def __init__(self):
        super().__init__()

    def run(self, apk):
        main_activity_name = apk.activity
        if main_activity_name is None:
            raise AbsentActivityException
        shellhelper.clean_log()
        shellhelper.start_activity_explicitly(apk.package, main_activity_name)


class MonkeyAgent(Agent):
    def __init__(self, seed, throttle, event_num):
        super().__init__()
        self.seed = seed
        self.throttle = throttle
        self.event_num = event_num

    def run(self, apk):
        shellhelper.run_monkey(apk.package, self.seed, self.throttle,
                               self.event_num)
