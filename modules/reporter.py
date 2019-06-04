import os
import re
from modules import config
from modules import shellhelper
from modules.entities import Csv
from modules.done_list_handler import DoneListHandler
from modules.exceptions import UserExitException

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

