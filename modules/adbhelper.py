import logging
import subprocess

from modules import config


def install(new_apk_path):
    cmd = '"%s" install -r "%s"' % (config.ADB_PATH, new_apk_path)
    out = request_pipe(cmd)

    print(out)


def uninstall(package):
    cmd = '"%s" uninstall "%s"' % (config.ADB_PATH, package)
    out = request_pipe(cmd)

    print(out)


def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err

    if pipe.returncode > 0:
        raise Exception("----------------------------------------------------\n\
Out: %s\nError: %s" % (out, err))

    return res.decode('utf-8')


def start_activity_explicitly(package_name, activity_name):
    # adb shell am start -n com.package.name/com.package.name.ActivityName
    logging.debug("Starting activity [%s] of the package [%s]..." % (activity_name, package_name))

    run_string = package_name + '/' + activity_name
    cmd = "{0} shell am start -n {1}".format(config.ADB_PATH, run_string)
    request_pipe(cmd)
