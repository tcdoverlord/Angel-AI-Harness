# Angel Platform 4.3.1-G — Chat Network Error Fix

## Defect

The Windows build could launch the Angel UI successfully but display:

`Angel error: network error`

when sending a chat message.

## Root Cause

The `/api/chat` handler uses `time.perf_counter()` for context/request diagnostics, but `server.py` did not import the `time` module.

The exception occurred after the HTTP response headers were opened and before the streaming `try` block could handle it. The browser therefore saw a dropped/incomplete HTTP connection and reported a generic network error instead of an application error.

## Fix

- Added the missing `time` import.
- Added chat preflight exception logging to `Angel_Platform/angel_server_errors.log`.
- Added structured HTTP 500 reporting for failures before model execution.
- Updated the browser client to display backend error details for non-2xx chat responses.
- Added a regression smoke test that exercises `/api/chat` with Ollama disabled.

## Validation

- 85 tests passed.
- Python compileall passed.
- Direct `/api/chat` smoke request returned HTTP 200 and the expected offline fallback response.

## Scope

This is a targeted Release Candidate defect fix. No conversation architecture, storage schema, UI design, confidence model, summary behavior, or model-selection behavior was changed.

Windows EXE packaging was not executed in this Linux validation environment.
