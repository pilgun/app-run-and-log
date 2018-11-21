import logging
import subprocess

from modules import config
from modules.exceptions import AbsentPackageException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
import os


def install(new_apk_path):
    cmd = '"%s" install -r "%s"' % (config.ADB_PATH, new_apk_path)
    try:
        out = request_pipe(cmd)
    except Exception as e:
        if 'not enough space' in str(e):
            raise NotEnoughSpaceException()
        raise ErrorInstallingException
    if 'Exception occurred while dumping' in out:
        raise ErrorUninstallingException


def uninstall(package):
    cmd = '"%s" uninstall "%s"' % (config.ADB_PATH, package)
    try:
        request_pipe(cmd)
    except Exception:
        raise ErrorUninstallingException


def get_package(path):
    cmd = "{} dump badging {}".format(config.AAPT_PATH, path)
    try:
        out = request_pipe(cmd)
    except Exception:
        raise AbsentPackageException()
    first_line = out.split('\n')[0]
    name_attribute = first_line.split(' ')[1]
    package = name_attribute.split('=')[1]
    package = package.replace("'", '')
    return package


def request_pipe(cmd):
    print(cmd)
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err

    if pipe.returncode > 0 :
        raise Exception("----------------------------------------------------\n\
Out: %s\nError: %s" % (out, err))

    return res.decode('utf-8')


def start_activity_explicitly(package_name, activity_name):
    # adb shell am start -n com.package.name/com.package.name.ActivityName
    logging.debug("Starting activity [%s] of the package [%s]..." % (activity_name, package_name))

    run_string = package_name + '/' + activity_name
    cmd = "{0} shell am start -n {1}".format(config.ADB_PATH, run_string)
    request_pipe(cmd)

def clean_log():
    cmd = "{0} logcat -c".format(config.ADB_PATH)
    request_pipe(cmd)

def dump_log(app, path):
    cmd = "{0} logcat *:E > {1} -d".format(config.ADB_PATH, path)
    request_pipe(cmd)

def save_log(app, api_level):
    file_path = os.path.join(config.LOGS_DIR, "{}.txt".format(app))
    if api_level < 20:
        save_log_onto_sdcard(app)
        pull_log(app, file_path)
    else:
        dump_log(app, file_path)
    return file_path

def save_log_onto_sdcard(app):
    cmd = "{} shell logcat -f /mnt/sdcard/{}.txt -d *:E".format(config.ADB_PATH, app)
    request_pipe(cmd)

def pull_log(app, file_path):
    cmd = "{} pull /mnt/sdcard/{}.txt {}".format(config.ADB_PATH, app, file_path)
    request_pipe(cmd)

def read_log(path):
    with open(path, 'r') as file:
        data = file.read()
        return data

def get_api_level():
    cmd = "{} shell getprop ro.build.version.sdk".format(config.ADB_PATH)
    api_level = int(request_pipe(cmd))
    return api_level