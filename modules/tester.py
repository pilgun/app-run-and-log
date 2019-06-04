import os
import time
from modules import config
from modules import shellhelper
from modules.decorators import log
from modules.done_list_handler import Status


class Tester:
    def __init__(self, apk, agent, reporter, api_level=0):
        self.apk = apk
        self.api_level = api_level
        self.agent = agent
        self.reporter = reporter
        if api_level == 0:
            self.api_level = shellhelper.get_api_level()
        print("API LEVEL: {}".format(self.api_level))

    @log('WRITE SUCCESS')
    def write_success(self):
        self.reporter.done_status(self.apk.name, Status.SUCCESS)

    @log('UNINSTALL')
    def uninstall(self):
        shellhelper.uninstall(self.apk.package)

    @log('REPORT')
    def report_status(self, manual=True):
        if manual:
            status = self.agent.read_status_from_experimenter()
            self.reporter.report_status(self.apk.package, status)
        else:
            time.sleep(config.WAIT_ACTIVITY)
            self.reporter.save_log(self.apk.package)
    
    @log('RUN ACTIVITY')
    def run(self):
        self.agent.run(self.apk)

    @log('INSTALL')
    def install(self):
        shellhelper.install(self.apk.path)

    def test(self, manual=True):
        self.install()
        self.run()
        self.report_status(manual)
        self.uninstall()
        self.write_success()
