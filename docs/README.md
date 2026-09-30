# Angel Platform 4.2.1 — Organized Build Structure

This build keeps runtime/application files and build entry points in the project root while moving project documentation and historical release material into `docs/`.

## Root
- Runtime source and application packages
- `build_windows_exe.bat`
- `RUN_WINDOWS.bat`
- `AngelPlatform.spec`
- Python entry points
- `requirements.txt` / `pyproject.toml`
- `README.md`
- `LICENSE.md`
- `SAFE_POINT_SHA256.txt`

## docs/releases
Current and historical release notes, build notes, UI improvement notes, and release artifacts.

## docs/architecture
Architecture decisions, governance, program handbook, requirements architecture, and repository references.

## docs/planning
Implementation plans, migration plans, roadmaps, epics, sprint plans, and rollout/RACI planning.

## docs/qa
QA catalog, requirements traceability, risk mitigation, and safe-execution validation material.

## docs/manifests
Historical build manifests.

## docs/build
Build-specific README and captured build output.

## docs/archive
Older 3.x routing/history notes retained for reference.

No application source code was moved. Build/runtime paths remain relative to the project root.
