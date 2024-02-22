@echo off
title Windows Iot Gateway Activation Script
REM call ".\venv\Scripts\activate.bat"
cd src

REM Check if python-can is installed
pip show python-can > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Python-CAN package is not installed
	echo Installing...
	pip install python-can
)

REM Check if requests is installed
pip show requests > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Requests package is not installed
	echo Installing...
	pip install requests
)

REM Check if numpy is installed
pip show numpy > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Numpy package is not installed
	echo Installing...
	pip install numpy
)

REM Check if watchdog is installed
pip show watchdog > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Watchdog package is not installed
	echo Installing...
	pip install watchdog
)

REM Check if uvicorn is installed
pip show uvicorn > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Uvicorn package is not installed
	echo Installing...
	pip install uvicorn
)

REM Check if paho-mqtt is installed
pip show paho-mqtt > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Paho-mqtt package is not installed
	echo Installing...
	pip install paho-mqtt
)

REM Check if colorlog is installed
pip show colorlog > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: Colorlog package is not installed
	echo Installing...
	pip install colorlog
)

start "Sensors Client" python.exe "sensor_devices.py"
start "IoT Gateway" python.exe "app.py"
