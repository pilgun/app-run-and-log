import csv
import glob
import os
import re
import subprocess

from pyaxmlparser import APK
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
    def __init__(self, name, input_dir):
        self.path = os.path.join(input_dir, name)
        self.apk = APK(self.path)
        self.name = name
        self.package = self.apk.package
        self.activity = self.apk.get_main_activity()
