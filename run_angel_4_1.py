from __future__ import annotations
import threading
import time
import webbrowser

from angel_platform.app import main as run_ui
from angel_platform.engineering.api import run as run_api

def main():
    api = run_api()
    threading.Thread(target=api.serve_forever, daemon=True).start()
    print("Angel 4.1 Engineering API: http://127.0.0.1:8780")
    print("Canonical contract: http://127.0.0.1:8780/openapi.yaml")
    # Keep the established Angel UI as the primary application.
    run_ui()

if __name__ == "__main__":
    main()
