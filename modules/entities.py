import csv
import glob
import logging
import os

from bbox.AndroidManifest import AndroidManifest
from modules import config


class Csv(object):

    def __init__(self, csv_path='crashes.csv'):
        self.csvfile = open(csv_path, 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(['Package', 'Status'])

    def write_row(self, app, status):
        self.writer.writerow([app, status])

    def close(self):
        self.csvfile.close()


class Apk:
    def __init__(self, name):
        self.path = os.path.join(config.APK_REPOSITORY, name)
        self.name = name
        sources_path = os.path.join(config.SOURCES_REPOSITORY, name.split('.apk')[0])
        manifest_path = self.get_android_manifest_path(sources_path)
        logging.debug(manifest_path)
        self.manifest = AndroidManifest(manifest_path)
        self.package = self.manifest.packageName

    def get_android_manifest_path(self, sources_path):
        android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
        if not os.path.exists(android_manifest_path):
            android_manifest_path = os.path.join(sources_path, "src", "main", "AndroidManifest.xml")
            if not os.path.exists(android_manifest_path):
                android_manifest_path = self.search_for_manifest(sources_path)
                if not os.path.exists(android_manifest_path):
                    raise Exception("Manifest not found")
        return android_manifest_path

    def search_for_manifest(self, sources_path):
        generator = glob.iglob(f'{sources_path}/**/AndroidManifest.xml', recursive=True)
        android_manifest_path = next(generator)
        return android_manifest_path
