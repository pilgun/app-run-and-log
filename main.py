import logging.config

import sys
import yaml
import argparse

from modules.agent import Agent
from modules import apps
from modules import config
from modules.done_list_handler import Status
from modules.entities import Apk
from modules.exceptions import AbsentActivityException, UserExitException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
from modules.tester import Tester


def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))

def get_parser():
    parser = argparse.ArgumentParser(description="A simple install/launch automated \
        tester. Reports the apps that successfully run on a choosen device.")
    parser.add_argument("-i", "--input_dir", metavar="<input_dir>", help="Set of \
        applications to install and run.", required=True)
    parser.add_argument("-o", "--output_dir", metavar="<output_dir>", 
        help="A directory for test results.", required=True)
    parser.add_argument("-w", "--wait", metavar="<wait>", help="Wait for activity \
        or crash for N seconds (3 sec by default).", required=False, default=config.WAIT_ACTIVITY)
    return parser

def main():
    setup_logging()
    parser = get_parser()
    args = parser.parse_args()
    run_actions(parser, args)

def run_actions(parser, args):
    if args is None:
        args = parser.parse_args()
    start_testing(args.input_dir, args.output_dir, args.wait)

def start_testing(input_dir, output_dir, wait):
    """ A simple install/launch automated tester. Reports the apps that 
    successfully run on a choosen device.
    """
    logging.info("START EXPERIMENT")
    logging.info("INPUT: {}".format(input_dir))
    logging.info("OUTPUT: {}".format(output_dir))

    agent = Agent(output_dir)
    list_handler = agent.get_done_list_handler()
    apps_to_process, done_project_count, overall_apps = apps.get_apps_to_process(input_dir, list_handler)
    counter = done_project_count
    fail_counter = list_handler.get_fail_counter()
    
    for app_name in apps_to_process:
        logging.info('================================================================================================================================================')
        apk = Apk(app_name, input_dir)
        tester = Tester(apk, agent)
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
    main()
