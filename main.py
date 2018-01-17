import logging.config
import os

import yaml

from modules import adbhelper
from modules import agent
from modules import apps
from modules import config
from modules.entities import Apk


def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


def main():
    done_list_path = config.DONE_LIST

    with open(done_list_path, 'a+') as done_list_file:
        apps_to_process = apps.get_apps_to_process(config.APK_REPOSITORY, done_list_file)
        logging.info("Start experiment")
        app_count = len(apps_to_process)
        counter = 0
        for app_name in apps_to_process:
            try:
                counter += 1
                apk = Apk(app_name)
                logging.info(f"Testing {app_name} {counter } of {app_count}")
                adbhelper.install(apk.path)
                agent.run_main_activity(apk)
                print("Press: c - crashed, s - successed")
                key = agent.wait_key()
                while key != 's' and key != 'c':
                    print("Press: c - crashed, s - successed")
                    key = agent.wait_key()
                agent.register_crash(apk.package, key)
                adbhelper.uninstall(apk.package)
                done_list_file.write(f'{app_name}: SUCCESS\n')
                done_list_file.flush()
            except BaseException:
                logging.exception(f'Exception for app {app_name}')
                done_list_file.write(f'{app_name}: FAIL\n')
                done_list_file.flush()

        agent.close_crash_report()


if __name__ == "__main__":
    setup_logging()
    main()
