import logging.config

import sys
import yaml

from modules import agent
from modules import apps
from modules import config
from modules.done_list_handler import list_handler, Status
from modules.entities import Apk
from modules.exceptions import AbsentActivityException, ManifestNotFoundException, UserExitException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
from modules.tester import Tester


def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


def main():
    logging.info("START EXPERIMENT")
    apps_to_process, done_project_count, overall_apps = apps.get_apps_to_process(config.APK_REPOSITORY)
    counter = done_project_count
    fail_counter = list_handler.get_fail_counter()
    for app_name in apps_to_process:
        logging.info('================================================================================================================================================')
        apk = Apk(app_name)
        tester = Tester(apk)
        try:
            counter += 1
            logging.info(f'{app_name}: {counter} OF {overall_apps}, FAIL TO RUN: {fail_counter}')
            tester.test(manual=False)
        except ErrorInstallingException:
            fail_counter += 1
            logging.exception(f'Cannot install app {app_name}')
            list_handler.write(app_name, Status.FAIL, reason='INSTALLATION ERROR')
        except NotEnoughSpaceException:
            logging.exception(f'Cannot install app {app_name} because there is not enough space. Stopping tool. Please, wipe data, then run tool again')
            sys.exit()
        except AbsentActivityException:
            fail_counter += 1
            logging.exception(f'Absent main activity for app {app_name}')
            tester.uninstall()
            list_handler.write(app_name, Status.FAIL, reason='ABSENT ACTIVITY')
        except ManifestNotFoundException:
            fail_counter += 1
            logging.error(f'Manifest not found for app {app_name}')
            list_handler.write(app_name, Status.FAIL, reason='MANIFEST NOT FOUND')
            tester.uninstall()
        except UserExitException:
            logging.info(f'User has chosen to exit while testing {app_name}')
            list_handler.write(app_name, Status.UNDEFINED, reason='USER_EXIT')
            tester.uninstall()
            sys.exit()
        except ErrorUninstallingException:
            logging.exception(f'Cannot uninstall {app_name}')
            list_handler.write(app_name, Status.SUCCESS, comment='UNINSTALL ERROR')
        except BaseException:
            fail_counter += 1
            logging.exception(f'Exception for app {app_name}')
            tester.uninstall()
            list_handler.write(app_name, Status.FAIL, reason='UNKNOWN')
    agent.close_crash_report()
    list_handler.close()


if __name__ == "__main__":
    setup_logging()
    main()
