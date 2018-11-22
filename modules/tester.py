import os
import time
from modules import config
from modules import shellhelper, agent
from modules.decorators import log
from modules.done_list_handler import list_handler, Status

class Tester:
    def __init__(self, apk, api_level=0):
        self.apk = apk
        self.api_level = api_level
        if not os.path.exists(config.LOGS_DIR):
            os.makedirs(config.LOGS_DIR)
        if api_level == 0:
            self.api_level = shellhelper.get_api_level()
        print("API LEVEL: {}".format(self.api_level))

    @log('WRITE SUCCESS')
    def write_success(self):
        list_handler.write(self.apk.name, Status.SUCCESS)

    @log('UNINSTALL')
    def uninstall(self):
        shellhelper.uninstall(self.apk.package)

    @log('REPORT')
    def report_status(self, manual=True):
        if manual:
            status = agent.read_status_from_experimenter()
            agent.report_status(self.apk.package, status, self.api_level)
        else: 
            time.sleep(config.WAIT_ACTIVITY)
            agent.report_error_automatically(self.apk.package, self.api_level)
    
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
        self.report_status(manual)
        self.uninstall()
        self.write_success()
