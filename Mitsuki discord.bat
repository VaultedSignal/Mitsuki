@echo off
title Mitsuki AI Companion - Discord Gateway

:: Navigate to project directory (just in case)
cd /d "%~dp0"

:: Activate virtual environment if it exists in .venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Run the startup script that boots up the Discord bot
python run_mitsuki_discord.py

pause