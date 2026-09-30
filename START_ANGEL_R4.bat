@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "REPO=%~dp0"
set "PIDFILE=%REPO%angel-r4.pid"
set "LOG=%REPO%angel-r4-start.log"
set "URL=http://127.0.0.1:8765/"

title Angel R4 Context Integrity - START

cd /d "%REPO%" || goto :error

echo ============================================================
echo          ANGEL R4 CONTEXT INTEGRITY - START
echo ============================================================
echo Folder: %REPO%
echo.

if not exist "%REPO%run_angel_4_2.py" (
    echo ERROR: run_angel_4_2.py was not found.
    echo.
    echo Copy this test package into the Angel Platform 4.4.3
    echo Alpha1 root, or run this BAT from that root.
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    pause
    exit /b 1
)

set "ENABLE_PROVENANCE_V1=true"
set "ANGEL_R4_ADAPTER=tests.r4_live_adapter"

if exist "%PIDFILE%" (
    for /f "usebackq delims=" %%P in ("%PIDFILE%") do (
        tasklist /FI "PID eq %%P" | find "%%P" >nul 2>&1
        if not errorlevel 1 (
            echo Angel appears to already be running with PID %%P.
            echo Open %URL%
            pause
            exit /b 0
        )
    )
    del /q "%PIDFILE%" >nul 2>&1
)

echo Starting Angel Platform...
echo ENABLE_PROVENANCE_V1=%ENABLE_PROVENANCE_V1%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p=Start-Process -FilePath 'python' -ArgumentList '.\run_angel_4_2.py' -WorkingDirectory '%REPO%' -PassThru; Set-Content -Path '%PIDFILE%' -Value $p.Id; Write-Host ('Angel PID: ' + $p.Id)" ^
  > "%LOG%" 2>&1

if errorlevel 1 goto :error

echo.
echo Waiting for Angel Web UI on %URL%
powershell -NoProfile -Command ^
  "$ok=$false; 1..30 | %% { try { Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -TimeoutSec 2 | Out-Null; $ok=$true; break } catch { Start-Sleep -Seconds 1 } }; if($ok){exit 0}else{exit 1}"

if errorlevel 1 (
    echo.
    echo WARNING: Angel did not answer within 30 seconds.
    echo Check: %LOG%
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Angel R4 runtime is READY.
echo Web UI: %URL%
echo PID file: %PIDFILE%
echo Log: %LOG%
echo ============================================================
echo.
start "" "%URL%"
pause
exit /b 0

:error
echo.
echo ERROR: Angel could not be started.
echo Log: %LOG%
pause
exit /b 1
