import os
import subprocess
from bbox.AndroidManifest import AndroidManifest


def run_main_activity(sources_path):
    manifest_path = get_android_manifest_path(sources_path)
    manifest = AndroidManifest(manifest_path)
    main_activity_name = manifest.getMainActivity()
    subprocess.run(f'adb shell am start -n {manifest.packageName}/{main_activity_name}')


def get_android_manifest_path(sources_path):
    android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(android_manifest_path):
        android_manifest_path = os.path.join(sources_path, "src", "main", "AndroidManifest.xml")
        if not os.path.exists(android_manifest_path):
            #todo: search for manifest
            raise Exception("Manifest not found")
    return android_manifest_path


def register_crash(app):
    print("todo: save in csv")

def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result