@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the app with optional source parameter
if "%1"=="" (
    python app.py
) else (
    python app.py %1
)

REM Keep the window open if there's an error
if errorlevel 1 pause 