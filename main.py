import logging.config

import os
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
from modules import shellhelper


def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


def get_parser():
    parser = argparse.ArgumentParser(
        description="A simple install/launch automated tester. Reports the \
            apps that successfully run on a chosen device.")
    subparsers = parser.add_subparsers(dest='subcmd',
                                       metavar="<command>",
                                       help="-help-")
    parser_run = subparsers.add_parser("run", help="Runs a single app.")
    parser_run.add_argument("apk_path",
                            metavar="<apk_path>",
                            help="Path to apk.")

    parser_run_dir = subparsers.add_parser("bundle",
                                           help="Runs a dir of apps.")
    parser_run_dir.add_argument("input_dir",
                                metavar="<input_dir>",
                                help="Set of applications to install and run.")
    parser_run_dir.add_argument("-o",
                                "--output_dir",
                                metavar="<output_dir>",
                                help="A directory for test results.",
                                required=True)
    parser_run_dir.add_argument(
        "-w",
        "--wait",
        metavar="<wait>",
        help="Wait for activity or crash for N seconds (3 sec by default).",
        required=False,
        default=config.WAIT_ACTIVITY)
    return parser


def main():
    setup_logging()
    parser = get_parser()
    args = parser.parse_args()
    run_actions(parser, args)


def run_actions(parser, args):
    if args is None:
        args = parser.parse_args()
    if args.subcmd == "run":
        directory, filename = os.path.split(args.apk_path)
        apk = Apk(filename, directory)
        shellhelper.install(apk.path)
        Agent.run_main_activity(apk)
        input("Press Enter...")
        shellhelper.uninstall(apk.package)
    elif args.subcmd == "run_dir":
        start_testing(args.input_dir, args.output_dir, args.wait)
    else:
        parser.print_usage()


def start_testing(input_dir, output_dir, wait):
    """ A simple install/launch automated tester. Reports the apps that 
    successfully run on a chooen device.
    """
    logging.info("START EXPERIMENT")
    logging.info("INPUT: {}".format(input_dir))
    logging.info("OUTPUT: {}".format(output_dir))

    agent = Agent(output_dir)
    list_handler = agent.get_done_list_handler()
    apps_to_process, done_project_count, overall_apps = apps.get_apps_to_process(
        input_dir, list_handler)
    counter = done_project_count
    fail_counter = list_handler.get_fail_counter()

    for app_name in apps_to_process:
        logging.info(
            '================================================================================================================================================'
        )
        counter += 1
        logging.info(
            f'{app_name}: {counter} OF {overall_apps}, FAIL TO RUN: {fail_counter}'
        )
        apk = Apk(app_name, input_dir)
        fail_counter = run_single_app(apk,
                                      list_handler,
                                      agent,
                                      fail_counter=fail_counter,
                                      overall_apps=overall_apps)
    agent.close_crash_report()
    list_handler.close()


def run_single_app(apk, list_handler, agent, fail_counter=0, overall_apps=1):
    tester = Tester(apk, agent)
    try:
        tester.test(manual=False)
    except ErrorInstallingException:
        fail_counter += 1
        logging.exception(f'Cannot install app {apk.name}')
        list_handler.write(apk.name, Status.FAIL, reason='INSTALLATION ERROR')
    except NotEnoughSpaceException:
        logging.exception(
            f'Cannot install app {apk.name} because there is not enough space. \
                Stopping tool. Please, wipe data, then run tool again')
        sys.exit()
    except AbsentActivityException:
        fail_counter += 1
        logging.exception(f'Absent main activity for app {apk.name}')
        tester.uninstall()
        list_handler.write(apk.name, Status.FAIL, reason='ABSENT ACTIVITY')
    except UserExitException:
        logging.info(f'User has chosen to exit while testing {apk.name}')
        list_handler.write(apk.name, Status.UNDEFINED, reason='USER_EXIT')
        tester.uninstall()
        sys.exit()
    except ErrorUninstallingException:
        logging.exception(f'Cannot uninstall {apk.name}')
        list_handler.write(apk.name, Status.SUCCESS, comment='UNINSTALL ERROR')
    except BaseException:
        fail_counter += 1
        logging.exception(f'Exception for app {apk.name}')
        tester.uninstall()
        list_handler.write(apk.name, Status.FAIL, reason='UNKNOWN')
    return fail_counter


if __name__ == "__main__":
    main()
