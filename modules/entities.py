import csv
import glob
import os
import re
import subprocess

from pyaxmlparser import APK

class Csv(object):
    def __init__(self, csv_path):
        self.csvfile = open(csv_path, 'a+', newline='')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(['Package', 'Status'])

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


class Apk:
    def __init__(self, path):
        self.path = path 
        self.apk = APK(self.path)
        # temporarty hack for ella os.path.basename(path) => path[51:-21]
        self.name = path[51:-21]
        self.package = self.apk.package
        self.activity = self.apk.get_main_activity()
