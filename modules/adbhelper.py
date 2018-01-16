import config
import subprocess

def install(new_apk_path):
    cmd = '"%s" install -r "%s"' % (config.adb_path, new_apk_path)
    out = request_pipe(cmd)

    print(out)


def uninstall(package):
    cmd = '"%s" uninstall "%s"' % (config.adb_path, package)
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

    return res

def start_activity_explicitly(package_name, activity_name):
    #adb shell am start -n com.package.name/com.package.name.ActivityName 
    logger.debug("Starting activity [%s] of the package [%s]..." % (package_name, activity_name))

    run_string = package_name + '/' + activity_name
    cmd = "{0} shell am start -n {1}".format(config.adb_path, run_string)
    request_pipe(cmd)