from __future__ import annotations
import threading
from angel_platform.app import main as run_ui
from angel_platform.engineering.api import run as run_api

def main():
    api = run_api()
    threading.Thread(target=api.serve_forever, daemon=True).start()
    print("Angel 4.2 Engineering API: http://127.0.0.1:8780")
    print("Angel 4.2 Unified Workspace: http://127.0.0.1:8765")
    run_ui()

if __name__ == "__main__":
    main()
