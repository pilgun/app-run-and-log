import argparse
from modules import config


def add_single_parse_arguments(parser):
    parser.add_argument("apk_path",
                        metavar="<apk_path>",
                        help="path to apk package")
    parser.add_argument("-o",
                        "--output_dir",
                        metavar="<output_dir>",
                        help="a directory for test results",
                        required=False,
                        default=config.OUTPUT_DIR)
    add_monkey_parser(parser)


def add_monkey_parser(parser):
    parser.add_argument("-m",
                        "--monkey",
                        action="store_true",
                        help="runs monkey")
    parser.add_argument("-e",
                        "--events",
                        help="generates N monkey events",
                        default=config.MONKEY_EVENTS)


def add_bundle_parse_arguments(parser):
    parser.add_argument("input_dir",
                        metavar="<input_dir>",
                        help="a directory of applications to install and run")
    parser.add_argument("-o",
                        "--output_dir",
                        metavar="<output_dir>",
                        help="a directory for test results",
                        required=False,
                        default=config.OUTPUT_DIR)
    parser.add_argument(
        "-w",
        "--wait",
        metavar="<wait>",
        help="wait for activity or crash for N seconds (3 sec by default).",
        required=False,
        default=config.WAIT_ACTIVITY)
    add_monkey_parser(parser)


def add_list_parse_arguments(parser):
    parser.add_argument("input_list",
                        metavar="<input_list>",
                        help="list of paths to apks")
    parser.add_argument("-o",
                        "--output_dir",
                        metavar="<output_dir>",
                        help="a directory of test results",
                        required=False,
                        default=config.OUTPUT_DIR)
    parser.add_argument("-w",
                        "--wait", metavar="<wait>",
                        help="wait for activity or crash for N seconds (3 sec by default).",
                        required=False,
                        default=config.WAIT_ACTIVITY)
    add_monkey_parser(parser)


def get_parser():
    parser = argparse.ArgumentParser(description="A simple install/launch \
        automated tester. Reports the apps that successfully run on a chosen device.")
    subparsers = parser.add_subparsers(dest='subcmd',
                                       metavar="<command>",
                                       help="- help -")
    run_single = subparsers.add_parser("run", help="runs a single app")
    add_single_parse_arguments(run_single)
    run_dir = subparsers.add_parser("run_dir",
                            help="sequentially runs all apps from a directory")
    add_bundle_parse_arguments(run_dir)
    run_list = subparsers.add_parser("run_list", help="runs apps in from a list")
    add_list_parse_arguments(run_list)
    return parser