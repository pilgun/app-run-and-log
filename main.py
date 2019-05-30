import os
import sys
import argparse
from loguru import logger

from modules import apps
from modules import config
from modules import arg_parser
from modules.agent import Agent, ActivityAgent, MonkeyAgent
from modules.done_list_handler import Status
from modules.entities import Apk
from modules.exceptions import AbsentActivityException, UserExitException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
from modules.tester import Tester
from modules import shellhelper


def setup_logging():
    logger.add("log.log", format="{time} - {level} - {message}")


def main():
    setup_logging()
    parser = arg_parser.get_parser()
    args = parser.parse_args()
    run_actions(parser, args)


def run_actions(parser, args):
    if args is None:
        args = parser.parse_args()
    if args.subcmd:
        agent = MonkeyAgent(
            args.output_dir, config.MONKEY_SEED, config.MONKEY_THROTTLE,
            args.events) if args.monkey else ActivityAgent(args.output_dir)
    if args.subcmd == "run":
        directory, filename = os.path.split(args.apk_path)
        apk = Apk(filename, directory)
        logger.info("START - {}".format(apk.package))
        tester = Tester(apk, agent)
        tester.test(manual=False)
    elif args.subcmd == "run_dir":
        start_testing(args.input_dir, agent, args.wait)

    else:
        parser.print_usage()


def start_testing(input_dir, agent, wait):
    """ A simple install/launch automated tester. Reports the apps that 
    successfully run on a chooen device.
    """
    logger.info("START EXPERIMENT")
    logger.info("INPUT: {}".format(input_dir))
    logger.info("OUTPUT: {}".format(agent.output_dir))

    list_handler = agent.get_done_list_handler()
    apps_to_process, done_project_count, overall_apps = apps.get_apps_to_process(
        input_dir, list_handler)
    counter = done_project_count
    fail_counter = list_handler.get_fail_counter()

    for app_name in apps_to_process:
        logger.info(
            '================================================================================================================================================'
        )
        counter += 1
        logger.info(
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
        logger.exception(f'Cannot install app {apk.name}')
        list_handler.write(apk.name, Status.FAIL, reason='INSTALLATION ERROR')
    except NotEnoughSpaceException:
        logger.exception(
            f'Cannot install app {apk.name} because there is not enough space. \
                Stopping tool. Please, wipe data, then run tool again')
        sys.exit()
    except AbsentActivityException:
        fail_counter += 1
        logger.exception(f'Absent main activity for app {apk.name}')
        tester.uninstall()
        list_handler.write(apk.name, Status.FAIL, reason='ABSENT ACTIVITY')
    except UserExitException:
        logger.info(f'User has chosen to exit while testing {apk.name}')
        list_handler.write(apk.name, Status.UNDEFINED, reason='USER_EXIT')
        tester.uninstall()
        sys.exit()
    except ErrorUninstallingException:
        logger.exception(f'Cannot uninstall {apk.name}')
        list_handler.write(apk.name, Status.SUCCESS, comment='UNINSTALL ERROR')
    except BaseException:
        fail_counter += 1
        logger.exception(f'Exception for app {apk.name}')
        tester.uninstall()
        list_handler.write(apk.name, Status.FAIL, reason='UNKNOWN')
    return fail_counter


if __name__ == "__main__":
    main()
