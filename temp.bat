@echo off
title Temp Script
call ".\venv\Scripts\activate.bat"
cd src
cmd /k "app.py"