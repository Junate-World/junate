@echo off
echo SendGrid Password Recovery Testing
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import requests, smtplib" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install requests python-dotenv
)

echo.
echo Starting SendGrid tests...
echo.

REM Run the test script
python test_sendgrid.py

echo.
echo Tests completed!
pause
