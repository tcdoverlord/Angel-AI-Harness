@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "REPO=%~dp0"
set "PIDFILE=%REPO%angel-r4.pid"

title Angel R4 Context Integrity - STOP

cd /d "%REPO%" || goto :error

echo ============================================================
echo           ANGEL R4 CONTEXT INTEGRITY - STOP
echo ============================================================
echo.

if not exist "%PIDFILE%" (
    echo No Angel PID file was found.
    echo The process may already be stopped.
    pause
    exit /b 0
)

for /f "usebackq delims=" %%P in ("%PIDFILE%") do set "PID=%%P"

if not defined PID (
    del /q "%PIDFILE%" >nul 2>&1
    echo Invalid PID file removed.
    pause
    exit /b 0
)

echo Stopping Angel PID %PID%...
taskkill /PID %PID% /T /F >nul 2>&1

if errorlevel 1 (
    echo Angel process was already stopped or could not be found.
) else (
    echo Angel stopped.
)

del /q "%PIDFILE%" >nul 2>&1

echo.
echo Persistent project data was not deleted.
echo.
pause
exit /b 0

:error
echo ERROR: Could not enter the Angel directory.
pause
exit /b 1
