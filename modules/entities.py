import csv
import glob
import os

from bbox.AndroidManifest import AndroidManifest
from modules import config, shellhelper
from modules.exceptions import ManifestNotFoundException


class Csv(object):

    def __init__(self, csv_path='crashes.csv'):
        if os.path.exists('crashes.csv'):
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

csv = Csv()


class Apk:
    def __init__(self, name):
        self.path = os.path.join(config.APK_REPOSITORY, name)
        self.name = name
        self.package = shellhelper.get_package(self.path)
        self.manifest = None

    def init_manifest(self):
        sources_path = os.path.join(config.SOURCES_REPOSITORY, self.name.split('.apk')[0])
        manifest_path = self.get_android_manifest_path(sources_path)
        self.manifest = AndroidManifest(manifest_path)

    def get_android_manifest_path(self, sources_path):
        android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
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
