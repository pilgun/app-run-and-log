from modules import apps
from modules import config
from modules import adbhelper
import os
import logging

def main():
    logging.basicConfig(filename='log.log',level=logging.DEBUG)
    done_list_path = os.path.join(config.APK_REPOSITORY, "installer_done_list.txt")

    with open(done_list_path, 'a+') as done_list_file:
        apps_to_process = apps.get_apps_to_process(config.APK_REPOSITORY, done_list_file)

        
        for app in apps_to_process:
            adbhelper.install(app.path)
            run_main_activity(app)
            print("Crashed? Press y or n character:")
            key = ask_for_agree_key()
            if key == 'y':
                register_crash(app)
            if key == 'n':
                register_success(app)
            adbhelper.uninstall(app.package)


if __name__ == "__main__":
    main()
