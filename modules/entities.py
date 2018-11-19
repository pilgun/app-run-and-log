import csv
import glob
import os
import re
import subprocess

from bbox.AndroidManifest import AndroidManifest
from modules import config, shellhelper
from modules.exceptions import ManifestNotFoundException


class Csv(object):

    def __init__(self, csv_path):
        if os.path.exists(csv_path):
            self.csvfile = open(csv_path, 'a', newline='')
        else:
            self.csvfile = open(csv_path, 'w', newline='')
            self.writer.writerow(['Package', 'Status'])
        self.writer = csv.writer(self.csvfile)

    def write_row(self, app, status):
        self.writer.writerow([app, status])
        self.csvfile.flush()

    def close(self):
        self.csvfile.close()

    def get_lines(self):
        self.csvfile.seek(0)
        return len(self.csvfile.readlines())

    def get_crashes(self):
        self.csvfile.seek(0)
        crash_count = self.csvfile.read().count(',c')
        return crash_count

csv = Csv(config.CRASHES_CSV)


class Apk:
    def __init__(self, name):
        self.path = os.path.join(config.APK_REPOSITORY, name)
        self.name = name
        self.package = shellhelper.get_package(self.path)
        self.manifest = None
        self.activity = None

    def init_manifest(self):
        self.activity = get_apk_properties(self.path).activity

    def get_android_manifest_path(self, sources_path):
        android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
        # android_manifest_path = os.path.join(sources_path, self.name.split('.apk')[0]+'.xml')
        if not os.path.exists(android_manifest_path):
            android_manifest_path = os.path.join(sources_path, "src", "main", "AndroidManifest.xml")
            if not os.path.exists(android_manifest_path):
                try:
                    android_manifest_path = self.search_for_manifest(sources_path)
                except StopIteration:
                    raise ManifestNotFoundException()
                if not os.path.exists(android_manifest_path):
                    raise Exception("Manifest not found")
        return android_manifest_path

    def search_for_manifest(self, sources_path):
        generator = glob.iglob(f'{sources_path}/**/AndroidManifest.xml', recursive=True)
        android_manifest_path = next(generator)
        return android_manifest_path

apk_info_pattern = re.compile("([^\>]*)package: name='(?P<package>.*?)'\
([^\>]*)launchable-activity: name='(?P<activity>.*?)'([^\>]*)")

def get_apk_properties(path):
    info_cmd = "{} dump badging {}".format(config.AAPT_PATH, path)
    out = subprocess.check_output(info_cmd, shell=True).decode('utf-8')
    matched = re.match(apk_info_pattern, out)

    package_name = matched.group('package')
    package_sdkversion = ""
    package_targetsdkversion = ""
    package_activity = matched.group('activity')

    return apkinfo(package_name, package_sdkversion, package_targetsdkversion, package_activity)

class apkinfo(object):
    """Properties of the apk file."""
    def __init__(self, package=None, sdkversion=None, targetsdkverion=None, activity=None):
        self.package = package
        self.sdkversion = sdkversion
        self.targetsdkversion = targetsdkverion
        self.activity = activity

    def __repr__(self):
        return "{} {} {} {}".format(self.package, self.sdkversion, self.targetsdkversion, self.activity)