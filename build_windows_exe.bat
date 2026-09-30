@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "LOG=%~dp0build_windows_exe.log"
set "PYEXE="

echo ============================================================
echo Angel Platform 4.4.3-EBR-R4 - Windows EXE Builder
echo ============================================================
echo.
echo Working directory: %CD%
echo Build log: %LOG%
echo.

echo [%date% %time%] BUILD START > "%LOG%"
echo Working directory: %CD% >> "%LOG%"

rem ------------------------------------------------------------
rem 1. Locate a usable Python launcher.
rem ------------------------------------------------------------
echo [1/6] Locating Python...
where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >> "%LOG%" 2>&1
    if not errorlevel 1 set "PYBASE=py -3"
)

if not defined PYBASE (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version >> "%LOG%" 2>&1
        if not errorlevel 1 set "PYBASE=python"
    )
)

if not defined PYBASE goto :python_missing

echo Python launcher: !PYBASE!
echo Python launcher: !PYBASE! >> "%LOG%"

rem ------------------------------------------------------------
rem 2. Create/reuse virtual environment.
rem ------------------------------------------------------------
echo [2/6] Creating or reusing virtual environment...
if not exist ".venv\Scripts\python.exe" (
    !PYBASE! -m venv .venv >> "%LOG%" 2>&1
    if errorlevel 1 goto :venv_failed
)

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" goto :venv_failed

"%PY%" --version
"%PY%" --version >> "%LOG%" 2>&1

rem ------------------------------------------------------------
rem 3. Install build dependencies.
rem ------------------------------------------------------------
echo [3/6] Installing build dependencies...
"%PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 goto :pip_failed
"%PY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 goto :pip_failed
"%PY%" -m pip install --upgrade pyinstaller >> "%LOG%" 2>&1
if errorlevel 1 goto :pip_failed

echo Dependencies installed.

rem ------------------------------------------------------------
rem 4. Validate source.
rem ------------------------------------------------------------
echo [4/6] Validating Python source...
"%PY%" -m compileall -q angel_platform run_angel_4_2.py >> "%LOG%" 2>&1
if errorlevel 1 goto :compile_failed

echo Source validation passed.

rem ------------------------------------------------------------
rem 5. Build onedir EXE from the canonical spec.
rem ------------------------------------------------------------
echo [5/6] Building AngelPlatform.exe...
if exist build rmdir /s /q build >> "%LOG%" 2>&1
if exist dist rmdir /s /q dist >> "%LOG%" 2>&1

"%PY%" -m PyInstaller --noconfirm --clean AngelPlatform.spec >> "%LOG%" 2>&1
if errorlevel 1 goto :pyinstaller_failed

if not exist "dist\AngelPlatform\AngelPlatform.exe" goto :exe_missing

rem ------------------------------------------------------------
rem 6. Success.
rem ------------------------------------------------------------
echo [6/6] BUILD SUCCESSFUL.
echo.
echo EXE: %CD%\dist\AngelPlatform\AngelPlatform.exe
echo Log: %LOG%
echo.
echo [%date% %time%] BUILD SUCCESSFUL >> "%LOG%"
echo The build completed successfully.
goto :done

:python_missing
echo.
echo ERROR: Python 3 was not found.
echo Install Python 3.10+ and make sure either "py" or "python" is available on PATH.
echo See: %LOG%
goto :fail

:venv_failed
echo.
echo ERROR: Could not create the .venv environment.
echo See the detailed error in: %LOG%
goto :fail

:pip_failed
echo.
echo ERROR: Dependency installation failed.
echo Check internet access, Python version, and the detailed log:
echo %LOG%
goto :fail

:compile_failed
echo.
echo ERROR: Python source validation failed.
echo See: %LOG%
goto :fail

:pyinstaller_failed
echo.
echo ERROR: PyInstaller failed to build the EXE.
echo See the detailed build log:
echo %LOG%
goto :fail

:exe_missing
echo.
echo ERROR: PyInstaller returned success but the EXE was not found.
echo Expected:
echo %CD%\dist\AngelPlatform\AngelPlatform.exe
echo See: %LOG%
goto :fail

:fail
echo.
echo ============================================================
echo BUILD FAILED - THIS WINDOW WILL STAY OPEN
echo ============================================================
echo.
echo Press any key to close.
pause >nul
endlocal
exit /b 1

:done
echo ============================================================
echo BUILD FINISHED - THIS WINDOW WILL STAY OPEN
echo ============================================================
echo.
echo Press any key to close.
pause >nul
endlocal
exit /b 0
