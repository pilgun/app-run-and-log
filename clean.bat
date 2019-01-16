@echo off
echo "Removing logs."
del done_list.txt
rd /s /q logs
del crashes.csv
del log.log