from modules import shellhelper, agent
from modules.decorators import log
from modules.done_list_handler import list_handler, Status
import os
from modules import config


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

    @log('RUN ACTIVITY')
    def run(self):
        self.apk.init_manifest()
        agent.run_main_activity(self.apk)

    @log('INSTALL')
    def install(self):
        shellhelper.install(self.apk.path)

    def test(self):
        self.install()
        self.run()
        self.report_status()
        self.uninstall()
        self.write_success()


