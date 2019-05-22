# app-run-and-log

This is the very basic automated testing pipeline for Android. Its only purpose 
is to find *healthy* apps and to filter out all the apps that could not be 
tested (therefore, not healthy) on your particular device or emulator. 
Not healthy apps affect the evaluation of dynamic analysis tools effectiveness.

**_Healthy_** app is the app that can be installed onto selected device and does
not crash upon startup.

# Testing flow

- install
- run the main activity or monkey
- uninstall
- report if the app failed to install or crashed upon startup time
- proceed with the next app

# Launching
1. Create config.py based on config.py.sample before launching the app.
2. Prepare device/emulator.

```shell
$ pip install -e .
$ app_run_and_log run <apk_path> # run a single app
```

# Examples

1.  Launch all apps from a directory.
```shell
$ app_run_and_log run_dir <input_dir> -o <output_dir> 
```
2. Run monkey on every app with 1000 events (see config.py for defaults).
```shell
$ app_run_and_log run_dir <input_dir> -o <output_dir> --monkey -e 1000
```

## License

Copyright © 2018 SnT, University of Luxembourg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the files under this repository except in compliance with 
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.