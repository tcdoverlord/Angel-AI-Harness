@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "REPO=%~dp0"
cd /d "%REPO%" || goto :error

title Angel R4 A-13 A-15 Context Integrity Tests

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    pause
    exit /b 1
)

set "ENABLE_PROVENANCE_V1=true"
set "ANGEL_R4_ADAPTER=tests.r4_live_adapter"

echo ============================================================
echo       ANGEL R4 A-13 A-15 CONTEXT INTEGRITY TESTS
echo ============================================================
echo.
echo ENABLE_PROVENANCE_V1=%ENABLE_PROVENANCE_V1%
echo ANGEL_R4_ADAPTER=%ANGEL_R4_ADAPTER%
echo.

python -m pytest -q -m context_integrity

echo.
if errorlevel 1 (
    echo RESULT: CONTEXT INTEGRITY TESTS FAILED
    pause
    exit /b 1
)

echo RESULT: CONTEXT INTEGRITY TESTS PASSED
pause
exit /b 0

:error
echo ERROR: Could not enter the test directory.
pause
exit /b 1
