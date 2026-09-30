@echo off
title Mitsuki AI Companion
echo Starting Mitsuki...

:: Navigate to project directory (just in case)
cd /d "%~dp0"

:: Activate virtual environment if it exists in .venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Run the Python module
python -m mitsuki.main

pause