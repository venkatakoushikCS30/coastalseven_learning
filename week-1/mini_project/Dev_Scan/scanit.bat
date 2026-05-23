@echo off
setlocal enabledelayedexpansion

set /p target_dir="Enter folder path: "
:: Strip hidden drag-and-drop quotes
set target_dir=!target_dir:"=!

python cli.py "!target_dir!"
pause
