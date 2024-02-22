@echo off
title Windows Iot Gateway Activation Script
REM call ".\venv\Scripts\activate.bat"
cd src

pip show aenum > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: aenum package is not installed
	echo Installing...
	pip install aenum
)
pip show asgiref > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: asgiref package is not installed
	echo Installing...
	pip install asgiref
)

pip show certifi > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: certifi package is not installed
	echo Installing...
	pip install certifi
)

pip show charset-normalizer > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: charset-normalizer package is not installed
	echo Installing...
	pip install charset-normalizer
)

pip show click > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: click package is not installed
	echo Installing...
	pip install click
)

REM Check if python-can is installed
pip show color-log > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: color-log package is not installed
	echo Installing...
	pip install color-log
)

pip show colorama > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: colorama package is not installed
	echo Installing...
	pip install colorama
)

pip show dataclasses > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: dataclasses package is not installed
	echo Installing...
	pip install dataclasses
)

pip show h11 > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: h11 package is not installed
	echo Installing...
	pip install h11
)

pip show idna > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: idna package is not installed
	echo Installing...
	pip install idna
)

pip show importlib-metadata > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: importlib-metadata package is not installed
	echo Installing...
	pip install importlib-metadata
)

pip show typing_extensions > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: typing_extensions package is not installed
	echo Installing...
	pip install typing_extensions
)

pip show urllib3 > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: urllib3 package is not installed
	echo Installing...
	pip install urllib3
)

pip show windows-curses > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: windows-curses package is not installed
	echo Installing...
	pip install windows-curses
)

pip show wrapt > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: wrapt package is not installed
	echo Installing...
	pip install wrapt
)

pip show zipp > nul 2>&1
if %errorlevel% neq 0 (
	echo Error: zipp package is not installed
	echo Installing...
	pip install zipp
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
