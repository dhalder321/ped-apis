@echo off
REM Change to the directory where your script is located
cd C:\ped\ped-apis

REM Activate the virtual environment (if you have one)
REM call C:\path\to\your\venv\Scripts\activate.bat

REM Run the Python script
python ppt2Image-q-poller.py > ppt2Image-q-poller_stdout.log 2> ppt2Image-q-poller_stderr.log

REM Optionally, deactivate the virtual environment
REM deactivate
