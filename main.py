from modules import apps
from modules import config
from modules import adbhelper
from modules import agent
import os
import logging

def main():
    logging.basicConfig(filename='log.log',level=logging.DEBUG)
    done_list_path = os.path.join(config.APK_REPOSITORY, "installer_done_list.txt")

    with open(done_list_path, 'a+') as done_list_file:
        apps_to_process = apps.get_apps_to_process(config.APK_REPOSITORY, done_list_file)

        for app in apps_to_process:
            adbhelper.install(app.path)
            agent.run_main_activity(app)
            print("Press: c - crashed, s - successed")
            key = agent.wait_key()
            while key is not 's' or key is not 'c':
                print("Press: c - crashed, s - successed")
                key = agent.wait_key()
            agent.register_crash(app, key)
            adbhelper.uninstall(app.package)


if __name__ == "__main__":
    main()
