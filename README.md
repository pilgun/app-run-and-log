# app-run-and-log

This is a very basic automated running pipeline for Android apps. It only finds *healthy* apps to do filtering of those that could not be teste (therefore, not healthy). Run on a device or an emulator.
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

```app_run_and_log or app-run-and-log```


# Examples

1.  Launch all apps from a directory. (not maintained)
```shell
$ app-run-and-log run_dir <input_dir> -o <output_dir>
```
2. Run monkey on every app with 1000 events (see config.py for defaults). (not maintained)
```shell
$ app_run_and_log run_dir <input_dir> -o <output_dir> --monkey -e 1000
$ app-run-and-log run_dir <input_dir> -o <output_dir> --monkey -e 1000
$ app_run_and_log launch -m -e 1 ./packages-list.txt -o out/ # launch already installed apps using monkey by feeding their package names from a list
```
3. Launch already installed apps using monkey by feeding their package names from a list
```
$ app_run_and_log launch -m -e 1 -o ./out/ ./packages-list.txt
```

## License

Copyright © from 2018 SnT, University of Luxembourg, Dr. Aleksandr Pilgun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the files under this repository except in compliance with 
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.