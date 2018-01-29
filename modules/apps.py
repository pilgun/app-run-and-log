import logging

import os

from modules import config

from modules.done_list_handler import list_handler

def get_apps_to_process(app_repository_path):
    all_apps_list = os.listdir(app_repository_path)
    raw_apps_list = [x for x in all_apps_list if is_raw_app(x)]
    apps_to_process = set(raw_apps_list)
    done_project_names = list_handler.get_done_project_names()
    logging.info('==========done_list_file======================================================================================================================================')
    logging.info(f'DONE LIST SIZE: {len(done_project_names)}')
    logging.debug(f'DONE LIST CONTENT: {done_project_names}')
    if not config.IGNORE_DONE_LIST:
        apps_to_process = apps_to_process - set(done_project_names)
    else:
        logging.info("IGNORING DONE LIST")
    logging.debug(f'Apps to process: {apps_to_process}')
    done_project_count = len(set(done_project_names))
    overall_project_count = len(set(raw_apps_list))
    return apps_to_process, done_project_count, overall_project_count


def is_raw_app(path):
    basename = os.path.basename(path)
    return basename.endswith(".apk")



def get_fail_counter(done_list_file):
    done_list_file.seek(0)
    fail_counter = done_list_file.read().count('FAIL')
    return fail_counter
