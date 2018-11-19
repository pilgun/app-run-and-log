import os
import time
from modules import config
from modules import shellhelper, agent
from modules.decorators import log
from modules.done_list_handler import list_handler, Status

class Tester:
    def __init__(self, apk):
        self.apk = apk
        if not os.path.exists(config.LOGS_DIR):
            os.makedirs(config.LOGS_DIR)

    @log('WRITE SUCCESS')
    def write_success(self):
        list_handler.write(self.apk.name, Status.SUCCESS)

    @log('UNINSTALL')
    def uninstall(self):
        shellhelper.uninstall(self.apk.package)

    @log('REPORT')
    def report_status(self):
        status = agent.read_status_from_experimenter()
        agent.report_status(self.apk.package, status)
    
    @log('REPORT AUTO')
    def report_status_automatically(self):
        agent.report_error_automatically(self.apk.package)

    @log('RUN ACTIVITY')
    def run(self):
        self.apk.init_manifest()
        agent.run_main_activity(self.apk)

    @log('INSTALL')
    def install(self):
        shellhelper.install(self.apk.path)

    def test(self, manual=True):
        self.install()
        self.run()
        if manual:
            self.report_status()
        else:
            time.sleep(config.WAIT_ACTIVITY)
            self.report_status_automatically()
        self.uninstall()
        self.write_success()


