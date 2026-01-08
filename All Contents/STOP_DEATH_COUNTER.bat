@echo off
REM Stop Death Counter Daemon
REM This batch file stops the death counter daemon by creating a STOP file

cd /d "%~dp0"
echo. > STOP
echo STOP file created. Daemon should stop within a few seconds.
timeout /t 2 /nobreak >nul

if exist daemon.lock (
    echo Daemon may still be running. Checking lock file...
    for /f "tokens=*" %%i in (daemon.lock) do (
        echo Attempting to kill process %%i...
        taskkill /F /PID %%i >nul 2>&1
    )
    del daemon.lock >nul 2>&1
    echo Daemon stopped.
) else (
    echo Daemon is not running.
)

if exist STOP del STOP >nul 2>&1
pause

