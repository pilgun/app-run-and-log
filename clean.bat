@echo off
echo "Removing logs."
del done_list_acvtool.txt
rd /s /q logs_acvtool
del crashes_acvtool.csv
del log.log