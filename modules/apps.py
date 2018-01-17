import logging

import os

from modules import config


def get_apps_to_process(app_repository_path, done_list_file):
    all_apps_list = os.listdir(app_repository_path)
    raw_apps_list = [x for x in all_apps_list if is_raw_app(x)]
    apps_to_process = set(raw_apps_list)
    done_project_names = get_done_project_names(done_list_file)
    logging.info('==========done_list_file======================================================================================================================================')
    logging.info(f'DONE LIST SIZE: {len(done_project_names)}')
    logging.debug(f'DONE LIST CONTENT: {done_project_names}')
    if not config.IGNORE_DONE_LIST:
        logging.info("IGNORING DONE LIST")
        apps_to_process = apps_to_process - set(done_project_names)
    logging.debug(f'Apps to process: {apps_to_process}')
    return apps_to_process


def is_raw_app(path):
    basename = os.path.basename(path)
    return not basename.endswith("_instrumented.apk") and basename.endswith(".apk")


def get_done_project_names(done_list_file):
    done_list_file.seek(0)
    done_project_names = [line.split(': ')[0] for line in done_list_file.readlines()]
    return done_project_names


def get_fail_counter(done_list_file):
    done_list_file.seek(0)
    fail_counter = done_list_file.read().count('FAIL')
    return fail_counter
