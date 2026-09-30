# Angel Platform 4.4.3-EBR-R4-ALPHA2

Full improvement build from 4.4.2-EBR-PROTOTYPE-R3.

Included:
- R4 response telemetry contract
- model invocation tracking
- response hash and preview
- ordered RAG state history
- terminal state telemetry
- suppression consistency between trace and diagnostics
- controlled conflict and retrieval-failure fixtures under TEST_MODE
- A-13/A-14/A-15 context-integrity tests, including async isolation
- Windows start/stop/test helper scripts
- conversational continuity guard for short acknowledgements and local sale/nap/buyer threads
- clearer retrieval UI wording: retrieved knowledge rather than generic evidence wording

No replacement of SQLite authority, no vector DB, no graph DB, and no retrieval architecture redesign.


Windows EXE packaging was updated to use `run_angel_4_2.py`, preserving the 8780 engineering API plus the 8765 Unified Workspace path used by R4 validation.
