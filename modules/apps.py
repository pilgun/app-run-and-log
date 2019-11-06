from loguru import logger
import os

from modules import config


def get_apps_to_process(all_apps_paths, list_handler):
    all_apps_paths = sorted(all_apps_paths)
    raw_apps_list = [x for x in all_apps_paths if is_raw_app(x)]

    apps_to_process = []
    done_project_names = list_handler.get_done_project_names()
    logger.info('==========done_list_file======================================================================================================================================')
    logger.info(f'DONE LIST SIZE: {len(done_project_names)}')
    logger.debug(f'DONE LIST CONTENT: {done_project_names}')
    if not config.IGNORE_DONE_LIST:
        # temporarty hack for ella os.path.basename(f)[:-4] => f[51:-21]
        apps_to_process = [f for f in raw_apps_list if f[51:-21] not in done_project_names]
    else:
        logger.info("IGNORING DONE LIST")
    logger.debug(f'Apps to process: {apps_to_process}')
    done_project_count = len(done_project_names)
    overall_project_count = len(raw_apps_list)
    return apps_to_process, done_project_count, overall_project_count


def is_raw_app(path):
    basename = os.path.basename(path)
    return basename.endswith(".apk")


def get_fail_counter(done_list_file):
    done_list_file.seek(0)
    fail_counter = done_list_file.read().count('FAIL')
    return fail_counter


def get_all_file_paths(dir_path):
    paths = []
    for (p, dirs, files) in os.walk(dir_path):
        full_paths = [os.path.join(p, f) for f in files]
        paths.extend(full_paths)
    return paths


def read_apps_list(path):
    with open(path, 'r') as f:
        return [p.strip() for p in f.readlines()]