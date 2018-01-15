import os
from bbox.AndroidManifest import AndroidManifest

def run_main_activity(sources_path):
    manifest_path = get_android_manifest_path(sources_path)
    manifest = AndroidManifest(manifest_path)
    main_activity = manifest.getMainActivity()
       

def get_android_manifest_path(sources_path):
    android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(android_manifest_path):
        android_manifest_path = os.path.join(sources_path, "src", "main", "AndroidManifest.xml")
        if not os.path.exists(android_manifest_path):
            #todo: search for manifest
            raise Exception("Manifest not found")
    return android_manifest_path

