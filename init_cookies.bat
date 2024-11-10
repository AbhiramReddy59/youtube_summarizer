@echo off
setlocal enabledelayedexpansion

echo Starting cookie update...

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Run the Python script and log output
python update_cookies.py > logs\initial_cookie_update.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo Cookie update completed successfully
) else (
    echo Cookie update failed with error code %ERRORLEVEL%
    echo Check logs\initial_cookie_update.log for details
)

:: Check if cookies.txt was created
if exist "cookies.txt" (
    echo cookies.txt file was created successfully
) else (
    echo Warning: cookies.txt file was not created
    echo Please check the logs for errors
)

echo Initial cookie update completed
endlocal