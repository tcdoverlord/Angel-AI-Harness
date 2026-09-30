# Windows EXE Build Fix — 4.3.1-G RC

## Problem addressed

The previous Windows builder could close immediately when `py` was unavailable or when a dependency/PyInstaller step failed. That made the failure look like the batch file simply "fizzed" and disappeared.

## Fix

`build_windows_exe.bat` now:

- Detects either the Windows `py` launcher or `python` on PATH.
- Reuses or creates `.venv` explicitly.
- Writes a persistent `build_windows_exe.log` beside the batch file.
- Stops at the exact failing stage.
- Verifies the expected EXE exists.
- Keeps the command window open on both success and failure.
- Uses the canonical `AngelPlatform.spec` for the onedir build.

The equivalent script under `scripts/` was updated to the same diagnostic builder so the two entry points do not silently behave differently.

## Expected output

After a successful build:

`dist\\AngelPlatform\\AngelPlatform.exe`

If the build fails, do not close the window before reading the displayed error. The full log is:

`build_windows_exe.log`
