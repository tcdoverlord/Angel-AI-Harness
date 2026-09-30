from __future__ import annotations
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timezone
from angel_platform.execution import SafeExecutor
from urllib.parse import quote, urlparse, parse_qs
import json, urllib.request, platform, shutil, sys, os, subprocess, uuid, re, shlex, zipfile, tempfile, html, base64, hashlib, hmac, secrets, threading, traceback, time
from angel_platform.web_search import search_web
from angel_platform.knowledge.library import (context_for, cards, search as search_knowledge, record_feedback, status as knowledge_status, knowledge_center, reindex_user_knowledge, read_user_document, write_user_document, delete_user_document, delete_knowledge_pack, create_category, _safe_extract_zip)
from angel_platform.capabilities.registry import inventory as capability_inventory
from angel_platform.storage.database import get_database
from angel_platform.storage.conversation_store import ConversationStore
from angel_platform.storage.storage_review import run_storage_review, storage_decision
from angel_platform.context_engine import ContextAssembler
from angel_platform.conversation_intelligence import ConversationIntelligence
from angel_platform.evidence_confidence import EvidenceConfidence
from angel_platform.evidence_backed_reasoning import EvidenceBackedReasoning
from angel_platform.conversation_summary import ConversationSummaryService
from angel_platform.engineering.lifecycle import KnowledgeEngineeringLifecycle


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent

# Persistent per-user storage: survives new source folders and rebuilt EXEs.
# On Windows this resolves to C:\Users\<current-user>\Angel_Platform.
USER_DATA = Path.home() / "Angel_Platform"
LEGACY_DATA = PROJECT / "data"
DATA = USER_DATA
DATA.mkdir(parents=True, exist_ok=True)

def _migrate_legacy_file(name: str) -> None:
    legacy = LEGACY_DATA / name
    current = DATA / name
    if legacy.exists() and not current.exists():
        try:
            current.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy, current)
        except OSError:
            pass

for _persistent_name in (
    "chat_history.json", "activity.json", "modules.json", "removed_modules.json",
):
    _migrate_legacy_file(_persistent_name)

# Initialize the database before any migration work. SQLite is now the source of truth
# for conversations; chat_history.json remains as a compatibility/export copy.
_DATABASE = get_database()
_CONVERSATIONS = ConversationStore(_DATABASE)
_ENGINEERING = KnowledgeEngineeringLifecycle()
try:
    _DATABASE.migrate_history_json(DATA / "chat_history.json")
except Exception:
    pass

HISTORY = DATA / "chat_history.json"  # legacy import/compatibility only
CONVERSATIONS_DIR = DATA / "conversations"
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
ACTIVITY = DATA / "activity.json"


MODULES_FILE = DATA / "modules.json"
REMOVED_MODULES_FILE = DATA / "removed_modules.json"
BACKUP_DIR = DATA / "backups" / "module_library"
SECURE_DIR = DATA / "secure"
# User-owned module storage.  Git repositories must not live inside the
# application/source directory so an Angel update cannot replace or lock them.
MODULES_DIR = USER_DATA / "modules"
GITHUB_MODULES_DIR = MODULES_DIR / "github_modules"
VAULT_FILE = SECURE_DIR / "github_vault.json"
SECURE_DIR.mkdir(parents=True, exist_ok=True)
_UNLOCKED_GITHUB_TOKEN = None
_PENDING_EXECUTIONS = {}
_HISTORY_LOCK = threading.RLock()
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
MODULES_DIR.mkdir(parents=True, exist_ok=True)
GITHUB_MODULES_DIR.mkdir(parents=True, exist_ok=True)

MODULES = [
    {"id":"angel-ai","name":"Angel AI","category":"Core","repo":"tcdoverlord/Angel-AI","description":"Local-first AI, memory, knowledge, voice and conversations."},
    {"id":"gitforge","name":"GitForge","category":"Development","repo":"tcdoverlord/GitForge-by-TCDOVERLORD","description":"Git and GitHub project workflow automation."},
    {"id":"script-gui-exe","name":"Script GUI EXE Pipeline","category":"Development","repo":"tcdoverlord/Script_GUI_EXE_Pipeline","description":"Package supported GUI scripts into distributable Windows executables."},
    {"id":"bluetooth-doctor","name":"Bluetooth & Phone Link Doctor","category":"Windows","repo":"tcdoverlord/Windows-Bluetooth-PhoneLink-Doctor","description":"Windows Bluetooth and Phone Link diagnostics and repair workflow."},
    {"id":"windows-maintenance","name":"Windows Maintenance Toolkit","category":"Windows","repo":"tcdoverlord/windows-maintenance-toolkit","description":"Maintenance and cleanup workflows."},
    {"id":"network-hardening","name":"Network Hardening Toolkit","category":"Windows","repo":"tcdoverlord/powershell-network-hardening-bootstrap","description":"Approved network and hardening workflows."},
    {"id":"wifi-toggle","name":"Wi-Fi Toggle Control","category":"Windows","repo":"tcdoverlord/WiFi-Toggle-Control-System","description":"Connectivity control workflow."},
    {"id":"safeusb","name":"SafeUSB Eject","category":"Utilities","repo":"tcdoverlord/SafeUSB-Eject-by-TCDOVERLORD","description":"Safe removable-drive ejection workflow."},
    {"id":"hyperv-backup","name":"Hyper-V Backup","category":"Virtualization","repo":"tcdoverlord/hyperv-backup-bootstrap","description":"Virtual machine backup workflow."},
    {"id":"vm-recovery","name":"Color-Coded VM Recovery","category":"Virtualization","repo":"tcdoverlord/color-coded-vm-recovery","description":"VM lifecycle and recovery organization."},
    {"id":"obs-safe-launch","name":"OBS Safe Launch","category":"Creator","repo":"tcdoverlord/obs-safe-launch-utility","description":"OBS launch and plugin safety workflow."},
    {"id":"opensceneforce","name":"OpenSceneFORCE","category":"Creator","repo":"tcdoverlord/OpenSceneFORCE","description":"Creator scene and automation project."},
    {"id":"creator-automation","name":"Creator Automation Lab","category":"Creator","repo":"tcdoverlord/Creator-Automation-Infrastructure-Lab","description":"Creator infrastructure and automation."},
    {"id":"cidr","name":"CIDR Block IP Calculator","category":"Networking","repo":"tcdoverlord/CIDR-Block-IP-Calculator","description":"Networking and subnet calculations."},
    {"id":"password-generator","name":"256-Bit Password Generator","category":"Utilities","repo":"tcdoverlord/256-Bit-Password-Generator","description":"Local password generation utility."},
    {"id":"heic","name":"HEIC to JPG Converter","category":"Utilities","repo":"tcdoverlord/heic-to-jpg-converter-windows","description":"Image conversion utility."},
    {"id":"volumeguardian","name":"VolumeGuardian","category":"Utilities","repo":"tcdoverlord/VolumeGuardian-by-TCDOVERLORD","description":"Volume and storage utility."},
    {"id":"stimtake","name":"StimTake Studio","category":"Projects","repo":"tcdoverlord/StimTake-Studio","description":"Creator infrastructure project."},
]


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, value):
    """Durably save JSON without losing the previous valid file on interruption."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False)
    temp = path.with_name(path.name + ".tmp")
    backup = path.with_name(path.name + ".bak")
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            shutil.copy2(path, backup)
        os.replace(temp, path)
    finally:
        if temp.exists():
            try:
                temp.unlink()
            except OSError:
                pass


def _conversation_title_from_message(message: str) -> str:
    text = re.sub(r"\s+", " ", str(message or "").strip())
    return (text[:70] or "New Chat")


def create_conversation(title: str = "New Chat") -> dict:
    conversation_id = uuid.uuid4().hex
    return _CONVERSATIONS.create(conversation_id, title)


def ensure_conversation(conversation_id: str | None, title: str = "New Chat") -> str:
    candidate = str(conversation_id or "").strip()
    if candidate and _CONVERSATIONS.get(candidate):
        return candidate
    return create_conversation(title).get("id")


def conversation_history(conversation_id: str, limit: int = 100) -> list[dict]:
    return _CONVERSATIONS.messages(conversation_id, limit)


def _conversation_history_path(conversation_id: str) -> Path:
    """Return the dedicated JSON snapshot path for one conversation."""
    safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", str(conversation_id or "default")) or "default"
    return CONVERSATIONS_DIR / f"{safe_id}.json"


def _write_conversation_snapshot(conversation_id: str) -> int:
    """Materialize one conversation as an independent human-readable JSON file.

    SQLite remains authoritative; these files are durable per-conversation
    snapshots for portability, inspection, backup, and recovery.
    """
    messages = _CONVERSATIONS.messages(conversation_id, 1000)
    conversation = _CONVERSATIONS.get(conversation_id) or {"id": conversation_id}
    payload = {
        "conversation": conversation,
        "messages": messages,
        "storage": "sqlite-authoritative",
        "snapshot_version": 1,
    }
    save_json(_conversation_history_path(conversation_id), payload)
    return len(messages)


def _sync_conversation_snapshots() -> None:
    """Backfill per-conversation JSON snapshots from the authoritative database."""
    try:
        for conversation in _CONVERSATIONS.list(500):
            _write_conversation_snapshot(str(conversation.get("id", "")))
    except Exception:
        # Snapshot materialization must never prevent Angel from starting.
        pass


def append_history(record):
    """Persist a message in SQLite and update only that conversation's JSON snapshot."""
    with _HISTORY_LOCK:
        role = str(record.get("role", "system"))
        content = str(record.get("content", ""))
        conversation_id = str(record.get("conversation_id", "default"))
        metadata = dict(record.get("metadata") or {})
        message_id = None
        if content:
            message_id = _CONVERSATIONS.append(conversation_id, role, content, metadata)
        _write_conversation_snapshot(conversation_id)
        return message_id


# Backfill independent snapshots for conversations already present in SQLite.
_sync_conversation_snapshots()


def _migrate_modules_to_user_storage() -> None:
    """Move known Git modules out of old application folders into user storage.

    The catalog may contain installed_path values from older Angel builds.
    Migration is conservative: move only when the legacy source exists and the
    new destination does not. Never delete a legacy copy automatically when a
    conflict exists.
    """
    custom = load_json(MODULES_FILE, [])
    if not isinstance(custom, list):
        return
    changed = False
    for module in custom:
        if not isinstance(module, dict) or not module.get("id"):
            continue
        target = GITHUB_MODULES_DIR / str(module["id"])
        recorded = str(module.get("installed_path") or "").strip()
        legacy = Path(recorded) if recorded else None
        if target.exists() and target.is_dir():
            if recorded != str(target):
                module["installed_path"] = str(target)
                changed = True
            continue
        if not legacy or not legacy.exists() or not legacy.is_dir():
            continue
        # Only migrate repositories that were outside the new user-owned root.
        try:
            legacy.resolve().relative_to(GITHUB_MODULES_DIR.resolve())
            continue
        except ValueError:
            pass
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy), str(target))
            module["installed_path"] = str(target)
            changed = True
        except OSError:
            # Keep the catalog untouched if a module is locked/in use. It can be
            # migrated on a later launch without risking the existing repository.
            continue
    if changed:
        save_custom_modules(custom)


def module_records():
    custom = load_json(MODULES_FILE, [])
    removed = set(load_json(REMOVED_MODULES_FILE, []))
    known = {m["id"] for m in MODULES}
    merged = [dict(m) for m in MODULES if m.get("id") not in removed]
    for item in custom:
        if item.get("id") in removed:
            continue
        if item.get("id") not in known:
            merged.append(item)
        else:
            for existing in merged:
                if existing.get("id") == item.get("id"):
                    existing.update(item)
    return merged


def save_custom_modules(items):
    save_json(MODULES_FILE, items)


# Existing catalogs can reference repositories from older Angel source folders.
# Migrate them after the persistence helpers are defined and before request handling.

def set_module_removed(module_id, removed=True):
    ids = set(load_json(REMOVED_MODULES_FILE, []))
    if removed:
        ids.add(module_id)
    else:
        ids.discard(module_id)
    save_json(REMOVED_MODULES_FILE, sorted(ids))


def remove_module_from_catalog(module_id):
    module = get_module(module_id)
    if not module:
        return None
    save_custom_modules([x for x in load_json(MODULES_FILE, []) if x.get("id") != module_id])
    set_module_removed(module_id, True)
    log_activity(f"Removed module: {module['name']}")
    return module


def create_module_backup():
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    filename = f"angel-module-library-{stamp}.zip"
    destination = BACKUP_DIR / filename
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        if MODULES_FILE.exists():
            archive.write(MODULES_FILE, "data/modules.json")
        else:
            archive.writestr("data/modules.json", "[]")
        if REMOVED_MODULES_FILE.exists():
            archive.write(REMOVED_MODULES_FILE, "data/removed_modules.json")
        else:
            archive.writestr("data/removed_modules.json", "[]")
        if GITHUB_MODULES_DIR.exists():
            for item in GITHUB_MODULES_DIR.rglob("*"):
                if item.is_file() and ".git" not in item.parts:
                    archive.write(item, str(Path("modules/github_modules") / item.relative_to(GITHUB_MODULES_DIR)))
    return destination


def list_module_backups():
    return sorted((p for p in BACKUP_DIR.glob("angel-module-library-*.zip") if p.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)


def restore_module_backup(filename):
    safe_name = Path(str(filename)).name
    if safe_name != filename or not re.fullmatch(r"angel-module-library-[0-9-]+\.zip", safe_name):
        raise ValueError("Invalid backup filename.")
    source = BACKUP_DIR / safe_name
    if not source.exists():
        raise FileNotFoundError("Backup was not found.")
    with zipfile.ZipFile(source) as archive:
        allowed = {"data/modules.json", "data/removed_modules.json"}
        if any(name not in allowed and not name.startswith("modules/github_modules/") for name in archive.namelist()):
            raise ValueError("Backup contains unsupported paths.")
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            archive.extractall(temp_path)
            modules_candidate = temp_path / "data/modules.json"
            removed_candidate = temp_path / "data/removed_modules.json"
            modules = json.loads(modules_candidate.read_text(encoding="utf-8"))
            removed = json.loads(removed_candidate.read_text(encoding="utf-8")) if removed_candidate.exists() else []
            if not isinstance(modules, list) or not isinstance(removed, list):
                raise ValueError("Backup data is invalid.")
            save_json(MODULES_FILE, modules)
            save_json(REMOVED_MODULES_FILE, removed)
            restored_files = 0
            source_modules = temp_path / "modules/github_modules"
            if source_modules.exists():
                for item in source_modules.rglob("*"):
                    if item.is_file():
                        target = GITHUB_MODULES_DIR / item.relative_to(source_modules)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target)
                        restored_files += 1
    log_activity(f"Restored module library backup: {safe_name}")
    return f"Restored module catalog and {restored_files} local module files from {safe_name}."


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:70] or "module"


def get_module(module_id):
    return next((m for m in module_records() if m.get("id") == module_id), None)


def custom_module(module_id):
    return next((m for m in load_json(MODULES_FILE, []) if m.get("id") == module_id), None)


def module_path(module):
    """Return the authoritative user-owned path for a GitHub module."""
    return GITHUB_MODULES_DIR / str(module["id"])


def persist_module(module):
    items = load_json(MODULES_FILE, [])
    items = [x for x in items if x.get("id") != module["id"]]
    items.append(module)
    save_custom_modules(items)


_migrate_modules_to_user_storage()


def detect_entrypoints(root):
    found = []
    for pattern, kind in [("*.html", "html"), ("*.htm", "html"), ("*.py", "python"), ("*.ps1", "powershell"), ("*.bat", "batch"), ("*.cmd", "batch"), ("*.exe", "exe")]:
        for item in sorted(root.glob(pattern))[:8]:
            found.append({"type": kind, "file": item.name})
    return found


def normalize_github_repo(value: str) -> str:
    """Normalize a GitHub URL or owner/name into owner/name."""
    raw = str(value or "").strip()
    raw = raw.replace("\r", "").replace("\n", "")
    raw = re.sub(r"^git@github\.com:", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^https?://github\.com/", "", raw, flags=re.IGNORECASE)
    raw = raw.removeprefix("github.com/")
    raw = raw.split("?", 1)[0].split("#", 1)[0].strip().strip("/")
    if raw.lower().endswith(".git"):
        raw = raw[:-4]
    raw = raw.strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", raw):
        return ""
    return raw


def friendly_module_name(repo_name: str) -> str:
    """Turn a repository name into a readable default module name."""
    text = re.sub(r"[-_]+", " ", str(repo_name or "")).strip()
    return text.title() or "GitHub Module"


def prepare_module(module):
    target = module_path(module)
    target.parent.mkdir(parents=True, exist_ok=True)
    repo_url = "https://github.com/" + module["repo"] + ".git"
    steps = []
    try:
        if (target / ".git").exists():
            proc = subprocess.run(["git", "-C", str(target), "pull", "--ff-only"], capture_output=True, text=True, timeout=120)
            steps.append("Updated existing repository")
        else:
            if target.exists() and any(target.iterdir()):
                return {"ok": False, "message": f"Target exists and is not an initialized Git repository: {target}"}
            proc = subprocess.run(["git", "clone", "--depth", "1", repo_url, str(target)], capture_output=True, text=True, timeout=180)
            steps.append("Cloned repository")
    except FileNotFoundError:
        return {"ok": False, "message": "Git was not found. Install Git, then try Prepare again."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "Git operation timed out."}
    except Exception as exc:
        return {"ok": False, "message": "Git operation failed: " + str(exc)}
    if proc.returncode != 0:
        return {"ok": False, "message": (proc.stderr or proc.stdout or "Git operation failed")[-4000:]}
    entrypoints = detect_entrypoints(target)
    module["installed_path"] = str(target)
    module["prepared"] = True
    module["entrypoints"] = entrypoints
    if not module.get("run_config") and entrypoints:
        first = entrypoints[0]
        module["run_config"] = {"type": first["type"], "file": first["file"], "args": ""}
    persist_module(module)
    log_activity(f"Prepared module: {module['name']}")
    return {"ok": True, "message": "\n".join(steps) + f"\nLocal path: {target}\nDetected entrypoints: {len(entrypoints)}", "module": module}


def find_web_entrypoint(module):
    target = module_path(module).resolve()
    if not target.exists() or not target.is_dir():
        legacy = Path(str(module.get("installed_path") or "")).expanduser()
        if legacy.exists() and legacy.is_dir():
            target = legacy.resolve()
    if not target.exists() or not target.is_dir():
        return None
    candidates = []
    for name in ("index.html", "index.htm", "main.html", "main.htm"):
        candidate = (target / name).resolve()
        if candidate.is_file() and target in candidate.parents:
            candidates.append(candidate)
    if not candidates:
        for candidate in sorted(target.glob("*.html")) + sorted(target.glob("*.htm")):
            if candidate.is_file() and target in candidate.resolve().parents:
                candidates.append(candidate.resolve())
    return candidates[0] if candidates else None


def run_module(module, config=None):
    target = module_path(module).resolve()
    if not target.exists() or not target.is_dir():
        # Compatibility fallback for a legacy repository that could not be moved
        # because it was locked/in use during startup.
        legacy = Path(str(module.get("installed_path") or "")).expanduser()
        if legacy.exists() and legacy.is_dir():
            target = legacy.resolve()
    if not target.exists() or not target.is_dir():
        return "Module is not prepared. Use Prepare Workspace first."
    cfg = config or module.get("run_config")
    if not cfg or not cfg.get("file"):
        return "No run configuration exists. Use Configure Run to select an entrypoint."
    kind, file_name = cfg.get("type", "command"), str(cfg.get("file", ""))
    candidate = (target / file_name).resolve()
    if target not in candidate.parents and candidate != target:
        return "Rejected: entrypoint must stay inside the module workspace."
    args = shlex.split(str(cfg.get("args", "")), posix=(os.name != "nt"))
    if kind == "python":
        command = [sys.executable, str(candidate), *args]
    elif kind == "powershell":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell: return "PowerShell was not found on this system."
        command = [shell, "-NoProfile", "-File", str(candidate), *args]
    elif kind == "batch":
        shell = shutil.which("cmd.exe") or shutil.which("cmd")
        if not shell: return "Windows command shell is unavailable on this system."
        command = [shell, "/d", "/c", str(candidate), *args]
    elif kind == "exe":
        command = [str(candidate), *args]
    else:
        return "Unsupported run type. Choose Python, PowerShell, Batch, or EXE."
    try:
        proc = subprocess.run(command, cwd=str(target), capture_output=True, text=True, timeout=90, shell=False)
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return f"Command: {' '.join(command)}\nExit code: {proc.returncode}\n\n{output[-12000:]}"
    except subprocess.TimeoutExpired:
        return "Execution stopped: 90-second timeout reached."
    except Exception as exc:
        return "Execution failed: " + str(exc)


def log_activity(message):
    items = load_json(ACTIVITY, [])
    items.insert(0, {"time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"), "message": message})
    save_json(ACTIVITY, items[:30])


CONTEXT_DIAGNOSTICS = DATA / "context_diagnostics.jsonl"
CONTEXT_TRACES = DATA / "context_traces.jsonl"
_CONTEXT_DIAGNOSTICS_LOCK = threading.RLock()

def _estimate_tokens(text: str) -> int:
    """Conservative diagnostic estimate when no tokenizer is available."""
    return max(0, (len(str(text)) + 3) // 4)

def record_context_diagnostic(record: dict) -> None:
    payload = dict(record)
    payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    try:
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with _CONTEXT_DIAGNOSTICS_LOCK, CONTEXT_DIAGNOSTICS.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass

def record_context_trace(trace: dict) -> None:
    payload = dict(trace)
    payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    try:
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with _CONTEXT_DIAGNOSTICS_LOCK, CONTEXT_TRACES.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass

def load_context_traces(conversation_id: str | None = None, limit: int = 20) -> list[dict]:
    try:
        lines = CONTEXT_TRACES.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    result = []
    for line in reversed(lines):
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if conversation_id and str(item.get("conversation_id")) != str(conversation_id):
            continue
        result.append(item)
        if len(result) >= max(1, min(int(limit), 100)):
            break
    return result

def load_context_diagnostics(limit: int = 100) -> list[dict]:
    try:
        lines = CONTEXT_DIAGNOSTICS.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    result = []
    for line in lines[-max(1, min(int(limit), 500)):]:
        try:
            result.append(json.loads(line))
        except ValueError:
            continue
    return list(reversed(result))

def ollama_available():
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False


def ollama_stream(model, messages):
    payload = json.dumps({"model": model, "messages": messages, "stream": True}).encode()
    request = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=payload, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(request, timeout=180) as response:
        for line in response:
            if not line.strip():
                continue
            try:
                data = json.loads(line.decode())
                piece = data.get("message", {}).get("content", "")
                if piece:
                    yield piece
            except Exception:
                continue



def _derive_key(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000, dklen=32)

def _vault_load():
    return load_json(VAULT_FILE, None)

def _vault_encrypt(token, key, nonce):
    # AES-GCM is required for credential encryption; fail closed if unavailable.
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(key).encrypt(nonce, token.encode("utf-8"), b"angel-github-token-v1")

def _vault_decrypt(blob, key, nonce):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(key).decrypt(nonce, blob, b"angel-github-token-v1").decode("utf-8")

def vault_status():
    record = _vault_load()
    return {"configured": bool(record), "unlocked": _UNLOCKED_GITHUB_TOKEN is not None,
            "username": (record or {}).get("username", ""), "algorithm": "PBKDF2-SHA256 + AES-256-GCM"}

def normalize_github_username(value):
    """Accept a login or profile URL, then store only the GitHub login."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    if "github.com" in raw.lower():
        candidate = raw if raw.lower().startswith(("http://", "https://")) else "https://" + raw
        parsed = urlparse(candidate)
        parts = [part for part in parsed.path.split("/") if part]
        raw = parts[0] if parts else ""
    raw = raw.strip().strip("/").split("/", 1)[0]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", raw):
        raise ValueError("GitHub username must be a login such as tcdoverlord or a GitHub profile URL.")
    return raw


def setup_github_vault(username, token, password, confirmation, confirmed=False):
    global _UNLOCKED_GITHUB_TOKEN
    username = normalize_github_username(username)
    token = str(token or "").strip()
    if not username or not token:
        raise ValueError("GitHub username and token are required.")
    if len(password) < 12:
        raise ValueError("Master password must be at least 12 characters.")
    if password != confirmation:
        raise ValueError("Master password confirmation does not match.")
    if not confirmed:
        raise ValueError("Please confirm that you can remember or securely store your Angel Platform master password.")
    try:
        salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
        key = _derive_key(password, salt)
        encrypted = _vault_encrypt(token.strip(), key, nonce)
    except ImportError:
        raise RuntimeError("The cryptography package is required. Run: python -m pip install cryptography")
    verifier = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000, dklen=32)
    save_json(VAULT_FILE, {"version": 1, "username": username.strip(), "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(), "verifier": base64.b64encode(verifier).decode(),
        "ciphertext": base64.b64encode(encrypted).decode()})
    _UNLOCKED_GITHUB_TOKEN = token.strip()
    log_activity("Configured encrypted GitHub credential vault")
    return f"GitHub credential vault configured and unlocked for {username}. The token is encrypted at rest and is never displayed."

def unlock_github_vault(password):
    global _UNLOCKED_GITHUB_TOKEN
    record = _vault_load()
    if not record:
        raise ValueError("GitHub credential vault is not configured.")
    salt = base64.b64decode(record["salt"])
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000, dklen=32)
    if not hmac.compare_digest(candidate, base64.b64decode(record["verifier"])):
        raise ValueError("Incorrect master password.")
    key = _derive_key(password, salt)
    _UNLOCKED_GITHUB_TOKEN = _vault_decrypt(base64.b64decode(record["ciphertext"]), key, base64.b64decode(record["nonce"]))
    log_activity("Unlocked GitHub credential vault")
    return "GitHub credential vault unlocked for this Angel session."

def test_github_connection():
    """Verify the unlocked token against GitHub and return a safe diagnostic."""
    if not _UNLOCKED_GITHUB_TOKEN:
        raise ValueError("GitHub vault is locked. Create or unlock the vault first.")
    record = _vault_load() or {}
    expected_user = record.get("username", "")
    request = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Angel-Platform",
            "Authorization": "Bearer " + _UNLOCKED_GITHUB_TOKEN,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ValueError(f"GitHub API rejected the credential (HTTP {exc.code}). Check token validity, expiration, and permissions.")
        raise ValueError(f"GitHub API request failed (HTTP {exc.code}).")
    except Exception as exc:
        raise ValueError(f"Could not reach GitHub API: {exc}")
    login = str(payload.get("login", ""))
    if not login:
        raise ValueError("GitHub API returned no authenticated login.")
    if expected_user and login.lower() != expected_user.lower():
        raise ValueError(f"Token authenticated as {login}, but the vault username is {expected_user}.")
    log_activity(f"Verified GitHub API connection as {login}")
    return f"GitHub API connection verified. Authenticated as {login}."


def lock_github_vault():
    global _UNLOCKED_GITHUB_TOKEN
    _UNLOCKED_GITHUB_TOKEN = None
    return "GitHub credential vault locked."

def github_owner_from_message(message):
    """Resolve a GitHub owner from a URL or environment, without requiring credentials for public repos."""
    match = re.search(r"github\.com/([A-Za-z0-9_.-]+)(?:[/?#]|$)", message, re.IGNORECASE)
    return match.group(1) if match else os.environ.get("ANGEL_GITHUB_OWNER", "tcdoverlord")


def asks_for_github_repositories(message):
    """Require explicit repository-list intent; avoid hijacking ordinary conversation."""
    lower = message.lower().strip()
    repo_terms = ("github", "repo", "repos", "repository", "repositories")
    action_terms = (
        "list my", "show my", "display my", "find my", "which repositories",
        "what repositories", "list repositories", "show repositories",
        "list repos", "show repos", "my github repositories"
    )
    return any(term in lower for term in repo_terms) and any(term in lower for term in action_terms)


def _github_headers():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Angel-Platform"}
    if _UNLOCKED_GITHUB_TOKEN:
        headers["Authorization"] = "Bearer " + _UNLOCKED_GITHUB_TOKEN
    return headers


def github_api_get(url):
    request = urllib.request.Request(url, headers=_github_headers())
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def github_authentication_answer():
    if not _UNLOCKED_GITHUB_TOKEN:
        return ("GitHub authentication status: NOT VERIFIED.\n"
                "The encrypted vault is locked or not configured.\n"
                "No authenticated GitHub API request was made.")
    profile = github_api_get("https://api.github.com/user")
    login = profile.get("login") or "unknown"
    record = _vault_load() or {}
    expected = record.get("username") or "unknown"
    return ("GitHub authentication status: VERIFIED.\n"
            f"Authenticated login: {login}\n"
            f"Vault username: {expected}\n"
            "Credential source: encrypted Angel Platform vault\n"
            "API endpoint: GET /user\n"
            "Token value: hidden")


def github_readme_answer(message):
    match = re.search(r"(?:github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", message)
    owner, repo = (match.group(1), match.group(2)) if match else (github_owner_from_message(message), "Angel-AI")
    repo = repo.removesuffix(".git")
    url = f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/readme"
    payload = github_api_get(url)
    encoded = payload.get("content", "")
    import base64 as _b64
    try:
        content = _b64.b64decode(encoded).decode("utf-8", errors="replace") if encoded else ""
    except Exception:
        content = ""
    if not content:
        return f"README access succeeded for {owner}/{repo}, but no readable content was returned."
    mode = "authenticated" if _UNLOCKED_GITHUB_TOKEN else "public"
    return (f"README access succeeded via {mode} GitHub API access for {owner}/{repo}.\n\n"
            + content[:12000])


def github_repositories_answer(message):
    owner = github_owner_from_message(message)
    authenticated = bool(_UNLOCKED_GITHUB_TOKEN)
    if authenticated:
        url = "https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member"
    else:
        url = f"https://api.github.com/users/{quote(owner)}/repos?per_page=100&sort=updated"
    payload = github_api_get(url)
    if not isinstance(payload, list):
        raise ValueError("GitHub returned an unexpected response.")
    if not payload:
        scope = "accessible" if authenticated else "public"
        return f"I couldn't find any {scope} repositories for GitHub user {owner}."
    scope = "Authenticated accessible" if authenticated else "Public"
    lines = [f"{scope} GitHub repositories for {owner} ({len(payload)} found):", "",
             f"Access mode: {'authenticated vault' if authenticated else 'public lookup'}", ""]
    for index, repo in enumerate(payload, 1):
        name = repo.get("name") or "Unnamed repository"
        description = (repo.get("description") or "No description provided.").strip().replace("\n", " ")
        html_url = repo.get("html_url") or f"https://github.com/{owner}/{name}"
        language = repo.get("language") or "Not specified"
        visibility = repo.get("visibility") or ("private" if repo.get("private") else "public")
        lines.extend([f"{index}. {name}", f"   Description: {description}",
                      f"   Language: {language}", f"   Visibility: {visibility}", f"   Link: {html_url}", ""])
    return "\n".join(lines).rstrip()


def current_datetime_answer():
    now = datetime.now().astimezone()
    return (
        f"Current local date: {now.strftime("%A, %B %-d, %Y") if os.name != "nt" else now.strftime("%A, %B %#d, %Y")}\n"
        f"Current local time: {now.strftime("%I:%M:%S %p").lstrip("0")}\n"
        f"Timezone: {now.tzname() or "Local time"}"
    )



def asks_for_live_unintegrated_data(message: str) -> bool:
    """Legacy safety helper retained for compatibility with routing tests."""
    lowered = message.lower()
    return any(term in lowered for term in ("weather", "news", "stock", "current conditions"))

def live_data_guidance(message: str) -> str:
    return ("I will not invent live information. No live lookup was performed. "
            "Connect a verified provider or use the dedicated live-data route.")

def asks_for_current_weather(message: str) -> bool:
    """Recognize weather requests without requiring fragile wording.

    A weather request is routed to the verified provider instead of Ollama,
    because the local model cannot know live conditions on its own.
    """
    lowered = message.lower()
    weather_terms = (
        "weather", "forecast", "temperature", "rain", "snow", "wind",
        "sunny", "cloudy", "humidity", "outside", "conditions",
    )
    return any(term in lowered for term in weather_terms)

def asks_for_combined_datetime_weather(message: str) -> bool:
    return asks_for_datetime(message) and asks_for_current_weather(message)

def _extract_weather_location(message: str) -> str | None:
    """Extract an explicit weather location without swallowing trailing intent words."""
    match = re.search(
        r"\b(?:in|near|for)\s+(.+?)(?=\s+(?:for\s+)?(?:tomorrow|today|now|currently|right\s+now|please)\b|[?!.,]*$)",
        message,
        re.I,
    )
    if not match:
        return None

    candidate = match.group(1).strip(" .,!?\t")
    # Natural phrasing such as "for Indianapolis for tomorrow" leaves a
    # trailing "for" after the look-ahead removes "tomorrow".
    candidate = re.sub(r"\s+for$", "", candidate, flags=re.I).strip(" .,!?\t")
    return candidate or None


def asks_for_current_weather(message: str) -> bool:
    """Recognize weather requests without requiring fragile wording."""
    lowered = message.lower()
    weather_terms = (
        "weather", "forecast", "temperature", "rain", "snow", "wind",
        "sunny", "cloudy", "humidity", "outside", "conditions",
    )
    return any(term in lowered for term in weather_terms)

def asks_for_combined_datetime_weather(message: str) -> bool:
    return asks_for_datetime(message) and asks_for_current_weather(message)

def asks_for_tomorrow_weather(message: str) -> bool:
    """Detect requests for tomorrow's weather or forecast."""
    lowered = message.lower()
    return bool(re.search(r"\btomorrow\b", lowered)) and bool(re.search(
        r"\b(weather|forecast|temperature|rain|snow|wind|sunny|cloudy|humidity|conditions)\b",
        lowered,
    ))


def tomorrow_weather_answer(message: str, location_data=None) -> str:
    """Return a provider-backed forecast for tomorrow."""
    location = _extract_weather_location(message)
    coordinates = None

    if isinstance(location_data, dict):
        try:
            lat = float(location_data.get("latitude"))
            lon = float(location_data.get("longitude"))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                coordinates = (lat, lon)
        except (TypeError, ValueError):
            coordinates = None

    if coordinates and not location:
        latitude, longitude = coordinates
        place_name = str(location_data.get("label") or "your device location")
    else:
        if not location:
            # Keep the long-standing local default rather than silently using an
            # unrelated city when the browser has no usable location.
            location = "Beech Grove, IN"

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search?name="
            + quote(location)
            + "&count=1&language=en&format=json"
        )
        request = urllib.request.Request(
            geo_url,
            headers={"User-Agent": "Angel-Platform/3.3.5"}
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            geo = json.loads(response.read().decode("utf-8"))

        results = geo.get("results") or []
        if not results:
            return (
                f"I couldn't locate '{location}' for a forecast. "
                "Try including a city and state."
            )

        place = results[0]
        latitude = place["latitude"]
        longitude = place["longitude"]
        place_name = ", ".join(
            part for part in [place.get("name"), place.get("admin1"), place.get("country")]
            if part
        )

    forecast_url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=" + str(latitude)
        + "&longitude=" + str(longitude)
        + "&daily=temperature_2m_max,temperature_2m_min,"
          "weather_code,precipitation_probability_max,wind_speed_10m_max"
        + "&temperature_unit=fahrenheit"
        + "&wind_speed_unit=mph"
        + "&timezone=auto"
        + "&forecast_days=2"
    )

    request = urllib.request.Request(
        forecast_url,
        headers={"User-Agent": "Angel-Platform/3.3.5"}
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        forecast = json.loads(response.read().decode("utf-8"))

    daily = forecast.get("daily") or {}
    if not daily.get("time") or len(daily["time"]) < 2:
        return "The weather provider returned no forecast for tomorrow."

    codes = {
        0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
        45: "fog", 48: "depositing rime fog", 51: "light drizzle", 53: "drizzle",
        55: "dense drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
        71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
        81: "rain showers", 82: "heavy rain showers", 95: "thunderstorm",
        96: "thunderstorm with hail", 99: "thunderstorm with hail",
    }
    index = 1
    forecast_date = daily["time"][index]
    high = daily.get("temperature_2m_max", [None, None])[index]
    low = daily.get("temperature_2m_min", [None, None])[index]
    weather_code = daily.get("weather_code", [None, None])[index]
    rain_chance = daily.get("precipitation_probability_max", [None, None])[index]
    wind = daily.get("wind_speed_10m_max", [None, None])[index]
    description = codes.get(weather_code, "unlisted conditions")

    return (
        f"Verified forecast for {place_name} on {forecast_date}: "
        f"high {high}°F, low {low}°F, {description}, "
        f"precipitation probability {rain_chance}%, maximum wind {wind} mph. "
        "Provider: Open-Meteo."
    )

def live_datetime_weather_answer(message: str, location_data=None) -> str:
    """Return authoritative local time plus provider-backed weather."""
    date_part = current_datetime_answer()
    weather_part = weather_answer(message, location_data)
    return date_part + "\n\n" + weather_part

def weather_answer(message: str, location_data=None) -> str:
    """Retrieve current weather using explicit text or user-approved device coordinates.
    Never assumes a default city or reuses a previous location.
    """
    lowered = message.lower()
    location = None
    location = _extract_weather_location(message)

    coordinates = None
    if isinstance(location_data, dict):
        try:
            lat = float(location_data.get("latitude"))
            lon = float(location_data.get("longitude"))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                coordinates = (lat, lon)
        except (TypeError, ValueError):
            coordinates = None

    if coordinates:
        latitude, longitude = coordinates
        place = {"name": str(location_data.get("label") or "your device location"), "admin1": ""}
    elif location:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?name=" + quote(location) + "&count=1&language=en&format=json"
        request = urllib.request.Request(geo_url, headers={"User-Agent": "Angel-Platform/3.2.3"})
        with urllib.request.urlopen(request, timeout=8) as response:
            geo = json.loads(response.read().decode("utf-8"))
        results = geo.get("results") or []
        if not results:
            return f"I couldn't locate '{location}' for a weather lookup. Try including a city and state."
        place = results[0]
        latitude, longitude = place["latitude"], place["longitude"]
    else:
        # Preserve Angel's established local default instead of silently
        # returning an unrelated city.
        location = "Beech Grove, IN"

        geo_url = "https://geocoding-api.open-meteo.com/v1/search?name=" + quote(location) + "&count=1&language=en&format=json"
        request = urllib.request.Request(geo_url, headers={"User-Agent": "Angel-Platform/3.3.5"})
        with urllib.request.urlopen(request, timeout=8) as response:
            geo = json.loads(response.read().decode("utf-8"))

        results = geo.get("results") or []
        if not results:
            return f"I couldn't locate the default location '{location}'."

        place = results[0]
        latitude, longitude = place["latitude"], place["longitude"]

    forecast_url = (
        "https://api.open-meteo.com/v1/forecast?latitude=" + str(latitude) +
        "&longitude=" + str(longitude) +
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m" +
        "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto"
    )
    request = urllib.request.Request(forecast_url, headers={"User-Agent": "Angel-Platform/3.2.3"})
    with urllib.request.urlopen(request, timeout=8) as response:
        weather = json.loads(response.read().decode("utf-8"))
    current = weather.get("current") or {}
    if not current:
        return "The weather provider returned no current conditions."
    codes = {
        0:"clear sky", 1:"mainly clear", 2:"partly cloudy", 3:"overcast",
        45:"fog", 48:"depositing rime fog", 51:"light drizzle", 53:"drizzle",
        55:"dense drizzle", 61:"light rain", 63:"rain", 65:"heavy rain",
        71:"light snow", 73:"snow", 75:"heavy snow", 80:"rain showers",
        81:"rain showers", 82:"heavy rain showers", 95:"thunderstorm",
        96:"thunderstorm with hail", 99:"thunderstorm with hail"
    }
    description = codes.get(current.get("weather_code"), "unlisted conditions")
    return (
        f"Verified current weather for {place.get('name', location)}, {place.get('admin1', '')}: "
        f"{current.get('temperature_2m')}°F, feels like {current.get('apparent_temperature')}°F, "
        f"{description}, humidity {current.get('relative_humidity_2m')}%, "
        f"wind {current.get('wind_speed_10m')} mph. "
        f"Provider: Open-Meteo; observation time: {current.get('time')}."
    )

def asks_for_datetime(message):
    lower = message.lower()
    date_terms = ("what is the date", "what's the date", "current date", "today's date", "what day is it", "what date is it")
    time_terms = ("what time is it", "current time", "what's the time", "time right now", "date and time", "day and time")
    return any(term in lower for term in date_terms + time_terms) or (
        "today" in lower and any(term in lower for term in ("date", "day", "time"))
    )



def asks_for_action(message):
    """Detect a request that proposes an executable system action.

    Normal questions, repository discussion, explanations, and analysis stay in
    ordinary conversation. This gate exists only to route concrete executable
    requests through Angel's approval/verification safety path.
    """
    lower = message.lower().strip()
    action_terms = (
        "run a command", "execute command", "execute this", "run this",
        "run the command", "run powershell", "powershell command",
        "run a powershell", "terminal command", "system command",
        "execute the script", "execute this script", "run the script",
        "run this script", "run a diagnostic", "system diagnostic",
        "check whether ollama is running", "check if ollama is running",
        "check python version", "list installed software",
        "show actual command output",
    )
    return any(term in lower for term in action_terms)

def choose_ai_lane(message):
    """Select a cooperative lane label without requiring extra models or breaking the core."""
    lower = message.lower()
    deep_terms = ("debug", "architecture", "analyze", "research", "plan", "code", "security")
    fast_terms = ("hi", "hello", "thanks", "what time", "quick", "define")
    if any(term in lower for term in deep_terms):
        return "deep"
    if any(term in lower for term in fast_terms) and len(message.split()) <= 12:
        return "fast"
    return "balanced"


def _diagnostic_command_from_message(message):
    lower = message.lower()
    if "python --version" in lower or "python version" in lower:
        return ["python", "--version"]
    if "ollama" in lower and ("running" in lower or "version" in lower):
        return ["ollama", "--version"]
    return None


def _execution_workspace():
    root = DATA / "workspaces"
    root.mkdir(parents=True, exist_ok=True)
    workspace = root / "diagnostics"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def action_guidance(message):
    """Prepare a concrete action for approval without exposing an internal mode."""
    command = _diagnostic_command_from_message(message)
    if command:
        command_text = " ".join(command)
        _PENDING_EXECUTIONS["default"] = command
        return (
            "PROPOSED ACTION\n"
            f"Command: {command_text}\n"
            "Purpose: read-only diagnostic; it does not intentionally modify files.\n"
            "Status: NOT EXECUTED.\n"
            "To approve this exact command, reply: APPROVE\n"
            "No command was run for this response."
        )
    return (
        "PROPOSED ACTION\n"
        "Status: NOT EXECUTED.\n"
        "Execution requires explicit approval and a verified execution result.\n"
        "No command was run for this response."
    )


def approval_request(message):
    lower = message.lower().strip()
    return lower == "approve" or lower.startswith("approve:") or lower == "execute"


def execute_pending_approved():
    command = _PENDING_EXECUTIONS.pop("default", None)
    if not command:
        return "No pending command is available for approval. Ask Angel to prepare a diagnostic first."
    executor = SafeExecutor(DATA / "workspaces")
    result = executor.run(command, _execution_workspace(), approved=True)
    status = "SUCCEEDED" if result.succeeded else "FAILED/BLOCKED"
    return (
        "VERIFIED EXECUTION RESULT\n"
        f"Command: {' '.join(result.command)}\n"
        f"Execution ID: {result.execution_id}\n"
        f"Status: {status}\n"
        f"Return code: {result.return_code}\n"
        f"stdout: {result.stdout.strip() or '(none)'}\n"
        f"stderr: {result.stderr.strip() or '(none)'}\n"
        f"Notes: {'; '.join(result.notes) or '(none)'}"
    )


def capability_report():
    github_state = "Authenticated" if _UNLOCKED_GITHUB_TOKEN else "Locked / not configured"
    ollama_state = "Available" if ollama_available() else "Unavailable"
    return (
        "LIVE ANGEL CAPABILITIES: "
        f"Ollama={ollama_state}; GitHub API={github_state}; "
        "GitHub read operations=available when authenticated; "
        "system changes=approval required; credentials=encrypted and hidden."
    )


def is_windows_diagnostic_request(message):
    lower = message.lower()
    return any(term in lower for term in (
        "diagnose windows", "windows diagnostics", "check my windows tools",
        "check python", "check ollama", "tool inventory", "system diagnostics"
    ))


def github_401_answer():
    return (
        "GitHub HTTP 401 means authentication was rejected. "
        "I will not expose or print the stored token.\n\n"
        "Safe checks: verify that the encrypted vault is unlocked, confirm the "
        "credential is loaded without displaying it, and test GET /user. "
        "If /user returns 401, the token may be invalid, expired, or revoked. "
        "If the vault is locked, unlock it through Angel's vault controls. "
        "If authentication succeeds but a resource fails, check permissions "
        "and the requested repository or endpoint. No token was displayed "
        "and no system changes were made."
    )


def fallback(message):
    lower = message.lower()
    if approval_request(message):
        return execute_pending_approved()
    if asks_for_action(message):
        return action_guidance(message)
    if is_windows_diagnostic_request(message):
        return (
            "Windows-safe diagnostic commands (proposed, not executed):\n"
            "  python --version\n"
            "  Get-Command python\n"
            "  ollama --version\n"
            "  Get-Command ollama\n"
            "  ollama list\n"
            "  Invoke-RestMethod http://localhost:11434/api/tags\n"
            "No commands were executed. Approval is required before system execution."
        )
    if "github" in lower and "authenticated" in lower:
        try:
            return github_authentication_answer()
        except Exception as exc:
            return f"GitHub authentication test failed: {exc}"
    if "readme" in lower and ("github" in lower or "repository" in lower or "repo" in lower):
        try:
            return github_readme_answer(message)
        except Exception as exc:
            return f"GitHub README access failed: {exc}"
    if asks_for_github_repositories(message):
        try:
            return github_repositories_answer(message)
        except Exception as exc:
            return f"I couldn't retrieve the GitHub repositories right now: {exc}"
    if asks_for_datetime(message):
        return current_datetime_answer()
    if any(word in lower for word in ("health", "scan system")):
        return f"Platform: {platform.platform()}\nPython: {sys.version.split()[0]}\nWorkspace: {DATA / 'workspaces'}"
    if "module" in lower:
        return f"Angel has {len(module_records())} registered module definitions. Open Modules to inspect them, or ask me to find a module for a task."
    if "tool" in lower:
        return tool_inventory()
    if any(word in lower for word in ("build", "project")):
        return "I can prepare a project workspace and package a ZIP. Windows EXE compilation must run on Windows with PyInstaller."
    return "Ollama is unavailable, so I am in offline mode. I can still inspect the local workspace, review module definitions, and provide safe guidance."


def tool_inventory():
    names = ["python", "git", "ollama", "docker", "powershell", "pwsh", "pyinstaller"]
    return "\n".join(f"{name}: {shutil.which(name) or 'MISSING'}" for name in names)


def action_result(action, context=None):
    if action == "system_health":
        return "\n".join([f"Platform: {platform.platform()}", f"OS: {platform.system()} {platform.release()}", f"Architecture: {platform.machine()}", f"Python: {sys.version.split()[0]}", f"Workspace: {DATA / 'workspaces'}"])
    if action == "tool_inventory":
        return tool_inventory()
    if action == "module_scan":
        return "\n".join(f"• {m['name']} | {m['category']} | {m['repo']}" for m in module_records())
    if action == "workspace_status":
        workspace = DATA / "workspaces" / "active"
        workspace.mkdir(parents=True, exist_ok=True)
        return f"Workspace: {workspace}\nStatus: ready\nMode: user-controlled / temporary workspace"
    if action == "execution_policy":
        return "Execution profile: Balanced\nRoutine diagnostics are allowed. Privileged, destructive, network-changing, and system-wide actions require confirmation. AI-generated commands are never executed silently."
    if action == "memory_status":
        history = load_json(HISTORY, [])
        return f"Local conversation records: {len(history)}\nStorage: {HISTORY}\nMemory retention: local history enabled"
    if action == "module_prepare":
        module_id = str((context or {}).get("module_id", ""))
        module = get_module(module_id)
        if not module:
            return "Module preparation failed: module not found."
        result = prepare_module(dict(module))
        return result.get("message", "Preparation failed.")
    if action == "module_run":
        module = get_module(str((context or {}).get("module_id", "")))
        if not module:
            return "Module run failed: module not found."
        return run_module(module, (context or {}).get("config"))
    if action == "module_configure":
        module = get_module(str((context or {}).get("module_id", "")))
        if not module:
            return "Module configuration failed: module not found."
        cfg = (context or {}).get("config") or {}
        module["run_config"] = {"type": cfg.get("type", "python"), "file": cfg.get("file", ""), "args": cfg.get("args", "")}
        persist_module(module)
        return f"Saved run configuration for {module['name']}: {json.dumps(module['run_config'])}"
    if action == "module_remove":
        module_id = str((context or {}).get("module_id", ""))
        module = get_module(module_id)
        if not module:
            return "Module removal failed: module not found."
        remove_module_from_catalog(module_id)
        return f"Removed catalog entry: {module['name']}. Local files were preserved."
    if action == "module_import_preview":
        return "Module catalog prepared from your known TCDOVERLORD repository set. Import remains metadata-only until a repository is explicitly selected and cloned."
    if action == "build_zip":
        return "Build workspace prepared. Select a project in DevOps before packaging. No files were changed."
    if action == "build_exe":
        return "EXE build is available on Windows through build_windows_exe.bat and requires a local Python/PyInstaller environment."
    return f"Action '{action}' is registered but has no destructive implementation. No system changes were made."


def find_readme(module):
    target = Path(module.get("installed_path") or module_path(module))
    if target.exists() and target.is_dir():
        for name in ("README.md", "readme.md", "Readme.md", "README.markdown", "README.txt"):
            candidate = target / name
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8", errors="replace"), candidate.name
    return None, None


def inline_markdown(value):
    text = html.escape(value, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', text)
    return text


def markdown_to_html(markdown):
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output, code_lines = [], []
    in_code = False
    list_tag = None

    def close_list():
        nonlocal list_tag
        if list_tag:
            output.append(f"</{list_tag}>")
            list_tag = None

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines, in_code = [], False
            else:
                close_list(); in_code = True
            continue
        if in_code:
            code_lines.append(line); continue
        if not line.strip():
            close_list(); continue
        if line.startswith("### "):
            close_list(); output.append("<h3>" + inline_markdown(line[4:]) + "</h3>")
        elif line.startswith("## "):
            close_list(); output.append("<h2>" + inline_markdown(line[3:]) + "</h2>")
        elif line.startswith("# "):
            close_list(); output.append("<h1>" + inline_markdown(line[2:]) + "</h1>")
        elif re.match(r"^[-*+] ", line):
            if list_tag != "ul":
                close_list(); output.append("<ul>"); list_tag = "ul"
            output.append("<li>" + inline_markdown(line[2:]) + "</li>")
        elif re.match(r"^\d+\. ", line):
            if list_tag != "ol":
                close_list(); output.append("<ol>"); list_tag = "ol"
            output.append("<li>" + inline_markdown(re.sub(r"^\d+\. ", "", line)) + "</li>")
        else:
            close_list(); output.append("<p>" + inline_markdown(line) + "</p>")
    if in_code:
        output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    close_list()
    return "\n".join(output)


def readme_page(module, content, filename):
    title = html.escape(module.get("name", "Module README"))
    body = markdown_to_html(content)
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{title} · README</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#061321;color:#eaf4ff;font:16px/1.65 Segoe UI,Arial,sans-serif}}main{{max-width:1000px;margin:32px auto;padding:28px;background:#0b2032;border:1px solid #1b5b83;border-radius:14px;box-shadow:0 12px 40px #0008}}h1,h2,h3{{color:#58b9ff;line-height:1.25}}h1{{margin-top:0;border-bottom:1px solid #1b5b83;padding-bottom:14px}}a{{color:#69c7ff}}code{{background:#061321;padding:2px 5px;border-radius:4px}}pre{{overflow:auto;background:#04101c;border:1px solid #1b5b83;padding:16px;border-radius:8px}}li{{margin:5px 0}}.meta{{color:#91b4cc;font-size:13px;margin-bottom:24px}}</style></head><body><main><h1>{title}</h1><div class=\"meta\">{html.escape(filename)} · Local module documentation</div>{body}</main></body></html>"""


def _project_context(project_id: str | None) -> dict | None:
    pid = str(project_id or "").strip()
    if not pid:
        return None
    project = _DATABASE.get_project(pid)
    if not project:
        return None
    return {
        "project": {"id": project["id"], "name": project["name"]},
        "resolved_scope": {
            "knowledge": "all indexed Angel knowledge",
            "conversations": "project conversations",
            "files": [],
        },
        "override_applied": False,
        "scope_fingerprint": hashlib.sha256(json.dumps(project.get("retrieval_policy", {}), sort_keys=True).encode()).hexdigest()[:24],
    }


_CONVERSATION_INTELLIGENCE = ConversationIntelligence()
_EBR = EvidenceBackedReasoning(_DATABASE)
ENABLE_PROVENANCE_V1 = EvidenceBackedReasoning.feature_enabled()
TEST_MODE = str(os.getenv("TEST_MODE", "false")).strip().lower() in {"1", "true", "yes", "on", "enabled"}
_R4_TEST_LOCK = threading.Lock()
_R4_TEST_NEXT_RETRIEVAL = None
_CONVERSATION_SUMMARIES = ConversationSummaryService()

_CONTEXT_ASSEMBLER = ContextAssembler(
    capability_report=capability_report,
    knowledge_context=context_for,
    project_context=_project_context,
    estimate_tokens=_estimate_tokens,
)


def _r4_set_next_retrieval_mode(mode: str) -> None:
    global _R4_TEST_NEXT_RETRIEVAL
    with _R4_TEST_LOCK:
        _R4_TEST_NEXT_RETRIEVAL = mode

def _r4_take_next_retrieval_mode() -> str | None:
    global _R4_TEST_NEXT_RETRIEVAL
    with _R4_TEST_LOCK:
        mode = _R4_TEST_NEXT_RETRIEVAL
        _R4_TEST_NEXT_RETRIEVAL = None
        return mode

def _is_short_acknowledgement(message: str) -> bool:
    text = re.sub(r"\s+", " ", str(message or "").strip().lower())
    return text in {"yes", "yes i agree", "i agree", "i agree with that", "exactly", "that makes sense", "makes sense", "good point", "right", "correct", "okay", "ok", "sure", "yep", "yeah", "nope"}

def _has_local_conversation_topic(message: str, history: list[dict[str, Any]]) -> bool:
    terms = ("nap", "sleep", "rest", "buyer", "selling", "sell", "sale", "monitor", "bicycle", "bike", "alarm", "notification", "message me", "stay awake", "available")
    combined = (str(message) + " " + " ".join(str(x.get("content", "")) for x in history[-8:])).lower()
    return any(term in combined for term in terms)

def _response_source_for(route: str, model_invoked: bool) -> str:
    if route in {"deterministic_no_evidence", "deterministic_error", "deterministic_conflict", "ebr_validated", "tool_generated"}:
        return route
    return "llm_generated" if model_invoked else "deterministic_no_evidence"


def _record_runtime_observation(question: str, answer: str, project_id: str | None, model: str, knowledge_hits: list[dict], conversation_id: str) -> dict:
    project_context = _project_context(project_id)
    fingerprint_payload = []
    evidence_records = []
    for rank, hit in enumerate(knowledge_hits, 1):
        content = re.sub(r"\s+", " ", str(hit.get("content", ""))).strip()
        source = str(hit.get("source", hit.get("title", "Untitled")))
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        chunk_id = "chunk_" + hashlib.sha256((source + content_hash).encode("utf-8")).hexdigest()[:20]
        fingerprint_payload.append({"source": source, "hash": content_hash})
        evidence_records.append({
            "document": {"id": "doc_" + hashlib.sha256(source.encode()).hexdigest()[:16], "title": str(hit.get("title", "Untitled")), "source": source},
            "chunk": {"id": chunk_id, "rank": rank},
            "passage": content[:1800],
            "relevance_score": None,
            "usage_type": "retrieved",
            "retrieved": True,
            "referenced": False,
            "grounded": None,
            "token_count": max(1, len(content[:1800]) // 4),
        })
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode()).hexdigest()[:24]
    run = _ENGINEERING.record_rag_run(
        question,
        project_context=project_context,
        retrieval_config={
            "profile": "existing-angel-knowledge-search",
            "model": model,
            "candidate_count": len(knowledge_hits),
            "knowledge_retrieval": bool(knowledge_hits),
            "conversation_id": conversation_id,
            "context_budget_tokens": 7600,
        },
        index_fingerprint=fingerprint,
    )
    _ENGINEERING.store.update_rag_run_answer(run["id"], answer)
    evidence_ids=[]
    for evidence in evidence_records:
        record=_ENGINEERING.record_evidence(run["id"], evidence)
        evidence_ids.append(record["id"])
    return {
        "rag_run_id": run["id"],
        "project_context": project_context,
        "retrieved_count": len(evidence_records),
        "evidence_ids": evidence_ids,
        "context_tokens": max(0, len(" ".join(str(h.get("content", ""))[:1700] for h in knowledge_hits)) // 4),
        "evaluation_status": "not_evaluated",
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, obj, status=200):
        raw = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.startswith("/api/ebr/claim?"):
            params = parse_qs(urlparse(self.path).query)
            claim_id = str(params.get("id", [""])[0]).strip()
            conversation_id = str(params.get("conversation_id", [""])[0]).strip()
            if not ENABLE_PROVENANCE_V1:
                return self.send_json({"error": "EBR prototype is disabled.", "rag_status": "OFF"}, 404)
            if not claim_id or not conversation_id:
                return self.send_json({"error": "id and conversation_id are required."}, 400)
            return self.send_json(_EBR.audit_claim(claim_id, conversation_id))
        if self.path.startswith("/api/ebr/audit?"):
            params = parse_qs(urlparse(self.path).query)
            conversation_id = str(params.get("conversation_id", [""])[0]).strip()
            answer = str(params.get("answer", [""])[0])
            if not ENABLE_PROVENANCE_V1:
                return self.send_json({"error": "EBR prototype is disabled.", "rag_status": "OFF"}, 404)
            if not conversation_id:
                return self.send_json({"error": "conversation_id is required."}, 400)
            return self.send_json(_EBR.audit_answer(conversation_id, answer))
        if self.path.startswith("/api/module?"):
            from urllib.parse import parse_qs, urlparse
            module_id = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            module = next((m for m in module_records() if m["id"] == module_id), None)
            if not module:
                return self.send_json({"error": "Module not found"}, 404)
            detail = dict(module)
            detail.update({
                "status": "Registered / metadata available",
                "source": "GitHub repository reference",
                "inspection": ["Manifest metadata", "Category", "Repository", "Description"],
                "execution": "Not executed by inspection",
                "next_step": "Explicitly prepare or import this module before execution"
            })
            return self.send_json({"module": detail})
        if self.path.startswith("/api/module-web?"):
            from urllib.parse import parse_qs, urlparse
            module_id = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            module = get_module(module_id)
            if not module:
                return self.send_error(404, "Module not found")
            entry = find_web_entrypoint(module)
            if entry is None:
                return self.send_error(404, "No HTML entrypoint found. Prepare the module first.")
            try:
                raw = entry.read_bytes()
            except OSError:
                return self.send_error(404, "HTML entrypoint could not be read.")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path.startswith("/api/module-readme?"):
            from urllib.parse import parse_qs, urlparse
            module_id = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            module = get_module(module_id)
            if not module:
                return self.send_error(404, "Module not found")
            content, filename = find_readme(module)
            if content is None:
                page = readme_page(module, "# README unavailable\n\nPrepare this module first, then try again. A local README.md was not found.", "README unavailable")
                status = 404
            else:
                page = readme_page(module, content, filename)
                status = 200
            raw = page.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path.startswith("/api/modules/") or self.path.startswith("/api/vault/"):
            return self.send_json({"error":"Module/GitHub integrations are not included in this build."}, 404)
        if self.path == "/api/projects":
            return self.send_json({"projects": _DATABASE.list_projects()})
        if self.path.startswith("/api/projects/"):
            pid = self.path.rsplit("/", 1)[-1]
            project = _DATABASE.get_project(pid)
            if not project:
                return self.send_json({"error": "Project not found."}, 404)
            return self.send_json({"project": project})
        if self.path.startswith("/api/v1/engineering/latest-for-conversation/"):
            conversation_id = self.path.rsplit("/", 1)[-1]
            runs = _ENGINEERING.store.list_rag_runs(100)
            run = next((r for r in runs if str(r.get("retrieval_config", {}).get("conversation_id", "")) == conversation_id), None)
            return self.send_json({"rag_run": run})
        if self.path.startswith("/api/v1/engineering/inspect/"):
            rid = self.path.rsplit("/", 1)[-1]
            run = _ENGINEERING.store.get_rag_run(rid)
            if not run:
                return self.send_json({"error": "RAG Run not found."}, 404)
            evidence = _ENGINEERING.store.list_evidence(rid)
            evaluations = _ENGINEERING.store.list_evaluations(rid)
            measurements = _ENGINEERING.store.list_measurements(rag_run_id=rid)
            selected = sum(1 for item in evidence if item.get("evidence", {}).get("retrieved"))
            return self.send_json({
                "rag_run": run,
                "retrieval": {"candidates": run.get("retrieval_config", {}).get("candidate_count", 0), "selected": selected, "rejected": 0},
                "context": {"chunks": selected, "tokens": sum(int(item.get("evidence", {}).get("token_count", 0) or 0) for item in evidence)},
                "answer": run.get("answer"),
                "evidence": evidence,
                "evaluation": evaluations[-1] if evaluations else None,
                "measurements": measurements,
                "project_context": run.get("project_context"),
            })
        if self.path.startswith("/api/context/summary"):
            from urllib.parse import parse_qs, urlparse
            conversation_id = parse_qs(urlparse(self.path).query).get("conversation_id", [""])[0].strip()
            if not conversation_id:
                return self.send_json({"error": "conversation_id is required."}, 400)
            summary = _DATABASE.get_conversation_summary(conversation_id)
            if not summary:
                return self.send_json({"conversation_id": conversation_id, "summary": None}, 404)
            return self.send_json(summary)
        if self.path.startswith("/api/context/diagnostics"):
            return self.send_json({"diagnostics": load_context_diagnostics(100), "path": str(CONTEXT_DIAGNOSTICS)})
        if self.path == "/api/storage/status":
            return self.send_json({"stats": _CONVERSATIONS.stats(), "integrity_check": _CONVERSATIONS.integrity_check(), "authoritative_store": "SQLite", "compatibility_json": str(HISTORY)})
        if self.path == "/api/storage/review":
            review = run_storage_review()
            return self.send_json({"review": review, "decision": storage_decision(review)})
        if self.path == "/api/knowledge":
            return self.send_json({"status": knowledge_status(), "center": knowledge_center()})
        if self.path.startswith("/api/knowledge/file?"):
            from urllib.parse import parse_qs, urlparse
            rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
            try:
                return self.send_json(read_user_document(rel))
            except FileNotFoundError:
                return self.send_json({"error": "Knowledge document not found."}, 404)
            except Exception as exc:
                return self.send_json({"error": str(exc)}, 400)
        if self.path.startswith("/api/knowledge/search?"):
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            if not query.strip():
                return self.send_json({"error": "Knowledge query is required"}, 400)
            return self.send_json({"query": query, "results": search_knowledge(query, 8)})
        if self.path == "/api/capabilities":
            return self.send_json({"release": "3.3.2", "capabilities": capability_inventory()})
        if self.path.startswith("/api/search?"):
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            if not query.strip():
                return self.send_json({"error": "Search query is required"}, 400)
            try:
                results = [item.to_dict() for item in search_web(query, 5)]
                return self.send_json({"query": query, "results": results, "source": "DuckDuckGo HTML"})
            except Exception as exc:
                return self.send_json({"query": query, "results": [], "error": "Web search unavailable: " + str(exc)}, 502)
        if self.path == "/api/vault/status":
            return self.send_json({"error":"GitHub integration is not included in this build."}, 404)
        if self.path == "/api/conversations":
            return self.send_json({"conversations": _DATABASE.list_conversations(100)})
        if self.path.startswith("/api/conversations/"):
            conversation_id = self.path.split("/", 3)[3].split("?", 1)[0]
            if not conversation_id:
                return self.send_json({"error": "Conversation ID is required."}, 400)
            conversation = _DATABASE.get_conversation(conversation_id)
            if not conversation:
                return self.send_json({"error": "Conversation not found."}, 404)
            return self.send_json({"conversation": conversation, "messages": conversation_history(conversation_id, 1000)})
        if self.path.startswith("/api/workspace/summary"):
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(self.path).query)
            project_id = str(query.get("project_id", [""])[0] or "").strip()
            project = _DATABASE.get_project(project_id) if project_id else None
            conversation = None
            if project_id:
                # Prefer the current persisted conversation when it belongs to the requested project.
                conversation_id = str(query.get("conversation_id", [""])[0] or "").strip()
                if conversation_id:
                    conversation = _DATABASE.get_conversation(conversation_id)
            if not conversation:
                conversations = _DATABASE.list_conversations(100)
                conversation = next((x for x in conversations if str(x.get("project_id") or "") == project_id), None) if project_id else (conversations[0] if conversations else None)
            center = knowledge_center() or {}
            library_status = knowledge_status() or {}
            skills = capability_inventory() or []
            skill_names = [str(x.get("name") or x.get("id") or "Skill") for x in skills]
            tools = []
            online = bool(ollama_available())
            return self.send_json({
                "project": project,
                "conversation": conversation,
                "knowledge": {
                    "documents": int(center.get("documents") or 0),
                    "chunks": int(center.get("chunks") or 0),
                    "packs": len(center.get("packs") or []),
                    "cards": int(library_status.get("total_cards") or 0),
                },
                "memory": {"available": True},
                "skills": skill_names,
                "tools": tools,
                "model": {
                    "backend": "LocalAI/Ollama" if online else "Offline",
                    "name": "llama3.2:3b",
                    "context": "8K context",
                    "connected": online,
                },
                "retrieval_scope": "Project Knowledge" if project else "Indexed Knowledge",
            })
        if self.path == "/api/status":
            return self.send_json({
                "ollama": ollama_available(),
                "platform": platform.system(),
                "modules": 0,
                "history_count": int(_DATABASE.stats().get("messages", 0)),
                "model_name": "llama3.2:3b",
                "context_capacity": "8K context",
            })
        if self.path == "/api/modules":
            return self.send_json({"error":"Module integrations are not included in this build."}, 404)
        if self.path == "/api/history":
            # Compatibility endpoint retained for older clients. New UI uses /api/conversations.
            return self.send_json({"history": load_json(HISTORY, [])})
        if self.path == "/api/activity":
            return self.send_json({"activity": load_json(ACTIVITY, [])[:20]})
        if self.path == "/api/module-backups":
            return self.send_json({"backups": [{"name": p.name, "size": p.stat().st_size, "created": datetime.fromtimestamp(p.stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M")} for p in list_module_backups()]})
        if self.path.startswith("/api/module-backups/download?"):
            from urllib.parse import parse_qs, urlparse
            name = parse_qs(urlparse(self.path).query).get("name", [""])[0]
            safe = Path(name).name
            path = BACKUP_DIR / safe
            if safe != name or not path.exists() or not path.is_file():
                return self.send_error(404)
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{safe}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        requested = self.path.split("?", 1)[0]
        path = ROOT / "index.html" if requested in ("/", "/index.html") else ROOT / requested.removeprefix("/static/")
        if not path.exists() or not path.is_file():
            return self.send_error(404)
        content_type = {".html":"text/html", ".css":"text/css", ".js":"application/javascript", ".png":"image/png", ".svg":"image/svg+xml"}.get(path.suffix, "application/octet-stream")
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self.send_json({"error":"Invalid JSON"}, 400)
        if self.path == "/api/vault/setup":
            try:
                result = setup_github_vault(str(data.get("username","")), str(data.get("token","")), str(data.get("password","")), str(data.get("confirmation","")), bool(data.get("confirmed", False)))
                connection = test_github_connection()
                return self.send_json({"result": result + "\n" + connection, "status": vault_status()})
            except Exception as exc:
                return self.send_json({"error": "Vault setup failed: " + str(exc)}, 400)
        if self.path == "/api/vault/test":
            try:
                return self.send_json({"result": test_github_connection(), "status": vault_status()})
            except Exception as exc:
                return self.send_json({"error": "GitHub API test failed: " + str(exc)}, 400)
        if self.path == "/api/vault/unlock":
            try:
                result = unlock_github_vault(str(data.get("password","")))
                return self.send_json({"result": result, "status": vault_status()})
            except Exception as exc:
                return self.send_json({"error": "Vault unlock failed: " + str(exc)}, 400)
        if self.path == "/api/vault/lock":
            return self.send_json({"result": lock_github_vault(), "status": vault_status()})
        if self.path.startswith("/api/modules/") or self.path.startswith("/api/vault/"):
            return self.send_json({"error":"Module/GitHub integrations are not included in this build."}, 404)
        if self.path == "/api/projects":
            name = str(data.get("name", "")).strip()
            if not name:
                return self.send_json({"error": "Project name is required."}, 400)
            project_id = "project_" + uuid.uuid4().hex
            try:
                project = _DATABASE.create_project(project_id, name, str(data.get("description", "")), data.get("retrieval_policy") or {})
            except Exception as exc:
                return self.send_json({"error": "Project could not be created: " + str(exc)}, 400)
            log_activity(f"Created project: {name}")
            return self.send_json({"project": project}, 201)
        if self.path.startswith("/api/projects/") and self.path.endswith("/delete"):
            project_id = self.path[len("/api/projects/"):-len("/delete")].strip("/")
            if not project_id:
                return self.send_json({"error": "Project ID is required."}, 400)
            project = _DATABASE.get_project(project_id)
            if not project:
                return self.send_json({"error": "Project not found."}, 404)
            deleted = _DATABASE.delete_project(project_id)
            log_activity(f"Deleted project: {project['name']}")
            return self.send_json({"deleted": project_id, "project": deleted})
        if self.path == "/api/conversations/project":
            conversation_id = str(data.get("conversation_id", "")).strip()
            project_id = str(data.get("project_id", "")).strip()
            if not conversation_id or not _DATABASE.get_conversation(conversation_id):
                return self.send_json({"error": "Conversation not found."}, 404)
            if project_id and not _DATABASE.get_project(project_id):
                return self.send_json({"error": "Project not found."}, 404)
            _DATABASE.set_conversation_project(conversation_id, project_id)
            return self.send_json({"conversation": _DATABASE.get_conversation(conversation_id)})
        if self.path == "/api/knowledge/reindex":
            try:
                result = reindex_user_knowledge()
                log_activity(f"Knowledge index rebuilt: {result.get('documents',0)} documents / {result.get('chunks',0)} chunks")
                return self.send_json({"result": result, "center": knowledge_center()})
            except Exception as exc:
                return self.send_json({"error": "Knowledge reindex failed: " + str(exc)}, 400)
        if self.path == "/api/knowledge/category":
            try:
                name = create_category(str(data.get("name", "")))
                log_activity(f"Created knowledge category: {name}")
                return self.send_json({"category": name, "center": knowledge_center()})
            except Exception as exc:
                return self.send_json({"error": str(exc)}, 400)
        if self.path == "/api/knowledge/pack":
            try:
                pack_id = str(data.get("pack_id", "")).strip()
                result = delete_knowledge_pack(pack_id)
                log_activity(f"Deleted knowledge pack: {pack_id}")
                return self.send_json({"deleted": pack_id, "index": result["index"], "center": knowledge_center()})
            except FileNotFoundError:
                return self.send_json({"error": "Knowledge pack not found."}, 404)
            except Exception as exc:
                return self.send_json({"error": str(exc)}, 400)
        if self.path == "/api/knowledge/file":
            try:
                rel = str(data.get("path", "")).strip()
                content = str(data.get("content", ""))
                if data.get("delete"):
                    delete_user_document(rel)
                    log_activity(f"Deleted knowledge: {rel}")
                    return self.send_json({"deleted": rel, "center": knowledge_center()})
                doc = write_user_document(rel, content)
                log_activity(f"Saved knowledge: {rel}")
                return self.send_json({"document": doc, "center": knowledge_center()})
            except Exception as exc:
                return self.send_json({"error": str(exc)}, 400)
        if self.path == "/api/knowledge/import":
            try:
                imported=[]
                for item in data.get("files", []) or []:
                    rel = str(item.get("path", "")).strip()
                    if not rel.lower().endswith(".md"): continue
                    doc=write_user_document(rel, str(item.get("content", "")))
                    imported.append(doc["path"])
                pack=None
                encoded=data.get("zip_base64")
                if encoded:
                    import base64
                    raw=base64.b64decode(encoded, validate=True)
                    if len(raw)>100*1024*1024:
                        raise ValueError("Knowledge pack is larger than the 100 MB limit.")
                    pack=_safe_extract_zip(raw)
                result=reindex_user_knowledge()
                log_activity(f"Imported knowledge: {len(imported)} Markdown files" + (f" and pack {pack.get('name')}" if pack else ""))
                return self.send_json({"imported": imported, "pack": pack, "index": result, "center": knowledge_center()})
            except Exception as exc:
                return self.send_json({"error": "Knowledge import failed: " + str(exc)}, 400)
        if self.path == "/api/modules/backup":
            try:
                path = create_module_backup()
                return self.send_json({"name": path.name, "download": "/api/module-backups/download?name=" + path.name, "result": f"Created module library backup: {path.name}"})
            except Exception as exc:
                return self.send_json({"error": "Backup failed: " + str(exc)}, 500)
        if self.path == "/api/modules/restore":
            try:
                result = restore_module_backup(str(data.get("name", "")))
                return self.send_json({"result": result})
            except Exception as exc:
                return self.send_json({"error": "Restore failed: " + str(exc)}, 400)
        if self.path == "/api/modules/add":
            raw_repo = str(data.get("repo", "")).strip()
            repo = normalize_github_repo(raw_repo)
            if not repo:
                return self.send_json({"error": "Enter a valid GitHub repository URL or owner/name."}, 400)

            owner, repo_name = repo.split("/", 1)
            module_id = slugify(repo.replace("/", "-"))
            # Derive a friendly name automatically. Users should not have to fill
            # out display-name/category fields just to install a repository.
            name = str(data.get("name") or friendly_module_name(repo_name)).strip()
            category = str(data.get("category") or "Imported").strip() or "Imported"
            module = {
                "id": module_id,
                "name": name,
                "category": category,
                "repo": repo,
                "description": str(data.get("description") or "Imported GitHub module."),
                "source": "github",
                "prepared": False,
                "entrypoints": [],
            }

            # Add means add-and-prepare. Validate the public repository before
            # changing the catalog so a typo never creates a broken module entry.
            try:
                probe = subprocess.run(
                    ["git", "ls-remote", "https://github.com/" + repo + ".git"],
                    capture_output=True, text=True, timeout=30
                )
            except FileNotFoundError:
                return self.send_json({"error": "Git was not found. Install Git, then try Add again."}, 400)
            except subprocess.TimeoutExpired:
                return self.send_json({"error": "GitHub repository check timed out."}, 400)
            if probe.returncode != 0:
                detail = (probe.stderr or probe.stdout or "Repository not found or not accessible.").strip()
                return self.send_json({"error": f"GitHub repository could not be verified: {detail[-1200:]}"}, 400)

            set_module_removed(module_id, False)
            result = prepare_module(module)
            if not result.get("ok"):
                return self.send_json({"error": result.get("message", "Module installation failed."), "module": module}, 400)

            persist_module(module)
            log_activity(f"Added and prepared module: {name}")
            return self.send_json({"module": module, "result": result.get("message", "Module added and prepared.")})
        if self.path == "/api/modules/remove":
            module_id = str(data.get("module_id", ""))
            module = remove_module_from_catalog(module_id)
            if not module:
                return self.send_json({"error": "Module not found in the catalog."}, 404)
            return self.send_json({"result": f"Removed {module['name']} from catalog. Local files were preserved."})
        if self.path == "/api/feedback":
            try:
                feedback_id = record_feedback(
                    str(data.get("message", "")),
                    str(data.get("rating", "")),
                    str(data.get("note", "")),
                    str(data.get("conversation_id", "")),
                )
                log_activity("Angel feedback recorded")
                return self.send_json({"status": "saved", "feedback_id": feedback_id})
            except Exception as exc:
                return self.send_json({"error": "Feedback was not saved: " + str(exc)}, 400)
        if self.path == "/api/action":
            action = data.get("action", "")
            result = action_result(action, data)
            log_activity(f"Completed: {action}")
            return self.send_json({"result": result})
        if self.path == "/api/conversations":
            title = str(data.get("title", "New Chat")).strip() or "New Chat"
            conversation = create_conversation(title)
            project_id = str(data.get("project_id", "")).strip()
            if project_id and _DATABASE.get_project(project_id):
                _DATABASE.set_conversation_project(conversation["id"], project_id)
                conversation = _DATABASE.get_conversation(conversation["id"])
            return self.send_json({"conversation": conversation}, 201)
        if self.path == "/api/conversations/pin":
            conversation_id = str(data.get("conversation_id", "")).strip()
            if not _DATABASE.get_conversation(conversation_id):
                return self.send_json({"error": "Conversation not found."}, 404)
            pinned = bool(data.get("pinned", True))
            _DATABASE.set_conversation_pinned(conversation_id, pinned)
            log_activity(("Pinned" if pinned else "Unpinned") + " conversation")
            return self.send_json({"conversation": _DATABASE.get_conversation(conversation_id)})
        if self.path == "/api/conversations/delete":
            conversation_id = str(data.get("conversation_id", "")).strip()
            if not conversation_id:
                return self.send_json({"error": "Conversation ID is required."}, 400)
            deleted = _DATABASE.delete_conversation(conversation_id)
            if not deleted:
                return self.send_json({"error": "Conversation not found."}, 404)
            log_activity("Deleted conversation")
            return self.send_json({"deleted": conversation_id})
        if self.path == "/api/conversations/title":
            conversation_id = str(data.get("conversation_id", "")).strip()
            title = str(data.get("title", "Conversation")).strip()
            if not conversation_id:
                return self.send_json({"error": "Conversation ID is required."}, 400)
            if not _DATABASE.get_conversation(conversation_id):
                return self.send_json({"error": "Conversation not found."}, 404)
            _DATABASE.update_conversation_title(conversation_id, title)
            _write_conversation_snapshot(conversation_id)
            return self.send_json({"conversation": _DATABASE.get_conversation(conversation_id)})
        if self.path == "/api/test/ebr/conflict":
            if not TEST_MODE:
                return self.send_json({"error": "TEST_MODE is required."}, 404)
            _r4_set_next_retrieval_mode("conflict")
            return self.send_json({"ok": True, "fixture": "conflict"})
        if self.path == "/api/test/ebr/fail-next-retrieval":
            if not TEST_MODE:
                return self.send_json({"error": "TEST_MODE is required."}, 404)
            _r4_set_next_retrieval_mode("error")
            return self.send_json({"ok": True, "fixture": "retrieval_failure"})
        if self.path == "/api/chat":
            message = str(data.get("message", "")).strip()
            conversation_id = str(data.get("conversation_id", "")).strip()
            if not message:
                return self.send_json({"error": "Message is required."}, 400)
            try:
                existing_conversation = _DATABASE.get_conversation(conversation_id) if conversation_id else None
                conversation_id = ensure_conversation(conversation_id, _conversation_title_from_message(message))
                model = data.get("model", "llama3.2:3b")
                # Conversation ownership is authoritative. A selected workspace/project
                # in the browser must never silently rewrite an existing conversation.
                # A new conversation is global unless the conversation was explicitly
                # created with a project scope before the first message.
                persisted_conversation = _DATABASE.get_conversation(conversation_id)
                project_id = str((persisted_conversation or {}).get("project_id", "") or "").strip()
                lane = choose_ai_lane(message)
                # Conversation-recall questions are grounded in the active transcript.
                # Do not let unrelated background knowledge compete with the user's
                # immediately preceding messages.
                conversation_recall = ConversationIntelligence.is_context_recall_request(message)
                prior_history = conversation_history(conversation_id, 20)
                ebr_bounded_request = ENABLE_PROVENANCE_V1 and (
                    _EBR.is_evidence_bounded_request(message)
                    or _EBR.inherits_evidence_boundary(message, prior_history)
                )
                local_topic_continuity = _has_local_conversation_topic(message, prior_history)
                acknowledgement_turn = _is_short_acknowledgement(message)
                knowledge_retrieval_suppressed = bool(conversation_recall or ebr_bounded_request or local_topic_continuity or acknowledgement_turn)
                knowledge_hits = [] if knowledge_retrieval_suppressed else search_knowledge(message, 6)
                evidence_assessment = EvidenceConfidence.assess(message, knowledge_hits)
                # The database is authoritative. The browser no longer needs to send the
                # entire transcript, which prevents chats from bleeding into one another.
                user_message_id = append_history({"role":"user", "content":message, "time":datetime.now(timezone.utc).isoformat(), "conversation_id":conversation_id})
                ebr_created_claims = []
                if ENABLE_PROVENANCE_V1 and user_message_id is not None:
                    ebr_created_claims = _EBR.extract_from_message(
                        int(user_message_id), conversation_id, "user", message
                    )
                history = [
                    {"role": item["role"], "content": item["content"]}
                    for item in conversation_history(conversation_id, 20)
                    if item.get("role") in {"user", "assistant", "system"}
                ]
                conversation_state = _CONVERSATION_INTELLIGENCE.analyze(message, history)
                ebr_retrieval_request = message
                if ENABLE_PROVENANCE_V1 and not _EBR.request_key(message) and _EBR.inherits_evidence_boundary(message, prior_history):
                    for prior_item in reversed(prior_history):
                        if str(prior_item.get("role", "")).lower() == "user" and _EBR.is_evidence_bounded_request(str(prior_item.get("content", ""))):
                            ebr_retrieval_request = str(prior_item.get("content", ""))
                            break
                ebr_result = _EBR.retrieve(ebr_retrieval_request, conversation_id) if ENABLE_PROVENANCE_V1 else None
                r4_test_mode = _r4_take_next_retrieval_mode() if TEST_MODE and ENABLE_PROVENANCE_V1 else None
                if r4_test_mode == "error":
                    from angel_platform.evidence_backed_reasoning import EvidenceResult
                    ebr_result = EvidenceResult("ERROR", reason="Controlled R4 retrieval failure fixture triggered.")
                elif r4_test_mode == "conflict":
                    from angel_platform.evidence_backed_reasoning import EvidenceResult
                    ebr_result = EvidenceResult("CONFLICT_FOUND", reason="Controlled R4 contradictory-evidence fixture triggered.")
                total_conversation_messages = len(_CONVERSATIONS.messages(conversation_id, 1000))
                conversation_summary = None
                stored_summary = _DATABASE.get_conversation_summary(conversation_id)
                if total_conversation_messages >= 100:
                    needs_refresh = (
                        stored_summary is None
                        or total_conversation_messages - int(stored_summary.get("message_count", 0)) >= _CONVERSATION_SUMMARIES.REFRESH_INTERVAL
                    )
                    if needs_refresh:
                        all_messages = _CONVERSATIONS.messages(conversation_id, 1000)
                        generated_at = datetime.now(timezone.utc).isoformat()
                        summary = _CONVERSATION_SUMMARIES.generate(conversation_id, all_messages, generated_at)
                        _DATABASE.save_conversation_summary(conversation_id, summary.message_count, summary.as_dict(), generated_at)
                        stored_summary = _DATABASE.get_conversation_summary(conversation_id)
                    if stored_summary:
                        summary_payload = stored_summary.get("summary") or {}
                        summary_obj = _CONVERSATION_SUMMARIES.generate(
                            conversation_id,
                            [],
                            stored_summary.get("generated_at") or datetime.now(timezone.utc).isoformat(),
                        )
                        # Render the stored fields directly; originals remain in SQLite messages.
                        summary_obj.message_count = int(stored_summary.get("message_count", 0))
                        for field in ("decisions", "actions", "open_questions", "project_status", "important_context"):
                            setattr(summary_obj, field, list(summary_payload.get(field, [])))
                        conversation_summary = summary_obj.render()
            except Exception as exc:
                error_log = DATA / "angel_server_errors.log"
                details = traceback.format_exc()
                try:
                    with error_log.open("a", encoding="utf-8") as handle:
                        handle.write(f"\n[{datetime.now(timezone.utc).isoformat()}] /api/chat preflight failure\n{details}\n")
                except OSError:
                    pass
                log_activity(f"Chat preflight failure: {type(exc).__name__}: {exc}")
                return self.send_json({"error": f"Chat request failed before model execution: {type(exc).__name__}: {exc}"}, 500)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            request_started = time.perf_counter()
            try:
                assembly = _CONTEXT_ASSEMBLER.assemble(
                    request=message,
                    history=history,
                    model=str(model),
                    lane=lane,
                    project_id=project_id,
                    knowledge_hits=knowledge_hits,
                    evidence=([] if ebr_bounded_request else knowledge_hits),
                    supported_evidence=(list(ebr_result.claims) if ebr_result and ebr_result.status == "HIT_VALIDATED" else []),
                    inferences=[],
                    unknowns=([ebr_result.reason] if ebr_result and ebr_result.status == "NO_EVIDENCE" else ([] if not ebr_bounded_request else ["No provenance-backed evidence was found for this request."])),
                    suppress_background_knowledge=bool(ebr_bounded_request),
                    conversation_state=conversation_state.as_dict(),
                    confidence=evidence_assessment.as_dict(),
                    conversation_summary=conversation_summary,
                )
                prompt_messages = assembly.messages
                prompt_text = "\n".join(str(item.get("content", "")) for item in prompt_messages)
                diagnostic = {
                    "conversation_id": conversation_id,
                    "model": model,
                    "prompt_size_chars": len(prompt_text),
                    "prompt_token_estimate": assembly.token_estimates["total"],
                    "token_distribution": assembly.token_estimates,
                    "conversation_summary_included": bool(conversation_summary),
                    "conversation_summary_message_count": (stored_summary or {}).get("message_count", 0) if conversation_summary else 0,
                     "conversation_recall_request": conversation_recall,
                     "knowledge_retrieval_suppressed": knowledge_retrieval_suppressed,
                    "conversation_message_count": total_conversation_messages,
                    "history_messages_included": len(history),
                    "history_limit": assembly.trace["history_limit"],
                    "truncation_events": assembly.truncation_events,
                    "context_sources": {
                        "system_prompt": True,
                        "current_objective": True,
                        "current_message": True,
                        "conversation_history": bool(history),
                        "project_context": any(b["name"] == "project_context" for b in assembly.trace["context_blocks"]),
                        "project_context_available": bool(project_id),
                        "knowledge": any(b["name"] == "relevant_knowledge" for b in assembly.trace["context_blocks"]),
                        "evidence": any(b["name"] == "evidence" for b in assembly.trace["context_blocks"]),
                        "tool_output": any(b["name"] == "tool_results" for b in assembly.trace["context_blocks"]),
                        "memory": False,
                    },
                    "knowledge_chunks_included": len(knowledge_hits),
                    "project_context_included": any(b["name"] == "project_context" for b in assembly.trace["context_blocks"]),
                    "project_context_available": bool(project_id),
                    "evidence_included": any(b["name"] == "evidence" for b in assembly.trace["context_blocks"]),
                    "tool_output_included": any(b["name"] == "tool_results" for b in assembly.trace["context_blocks"]),
                    "confidence": evidence_assessment.as_dict(),
                    "evidence_count": evidence_assessment.evidence_count,
                    "evidence_source_count": evidence_assessment.source_count,
                    "conflicts_detected": evidence_assessment.conflicts_detected,
                    "support_strength": evidence_assessment.support_strength,
                    "request_started_at": datetime.now(timezone.utc).isoformat(),
                    "request_time_ms": None,
                    "response_time_ms": None,
                    "response_chars": None,
                    "status": "started",
                    "provenance_enabled": ENABLE_PROVENANCE_V1,
                    "ebr_created_claims": len(ebr_created_claims),
                    "rag_status": (ebr_result.status if ebr_result else "OFF"),
                    "rag_reason": (ebr_result.reason if ebr_result else "Provenance feature disabled."),
                    "rag_rejected": (list(ebr_result.rejected) if ebr_result else []),
                    "rag_state_history": (["SEARCHING"] + ([ebr_result.status] if ebr_result else [])),
                    "terminal_state": (ebr_result.status if ebr_result else "LOCAL"),
                    "response_source": None,
                    "model_invoked": False,
                    "model_name": None,
                    "response_hash": "",
                    "response_preview": "",
                }
                trace = dict(assembly.trace)
                trace["provenance_enabled"] = ENABLE_PROVENANCE_V1
                trace["rag_status"] = ebr_result.status if ebr_result else "OFF"
                trace["rag_reason"] = ebr_result.reason if ebr_result else "Provenance feature disabled."
                trace["retrieval_candidates"] = list(ebr_result.claims) if ebr_result else []
                trace["retrieval_rejected"] = list(ebr_result.rejected) if ebr_result else []
                trace["ebr_created_claims"] = ebr_created_claims
                trace["rag_state_history"] = ["SEARCHING"] + ([ebr_result.status] if ebr_result else [])
                trace["terminal_state"] = ebr_result.status if ebr_result else "LOCAL"
                trace["conversation_id"] = conversation_id
                trace["request"] = message
                trace["conversation_intelligence"] = conversation_state.as_dict()
                trace["confidence"] = evidence_assessment.as_dict()
                record_context_trace(trace)
                record_context_diagnostic(diagnostic)
                # Deterministic routes handle only verified application actions and
                # narrowly identifiable transcript-recall facts. The latter prevents
                # the model from inventing an answer when the requested fact can be
                # extracted exactly from the active conversation.
                record_context_diagnostic(diagnostic)
                response_route = "llm_generated"
                model_invoked = False
                model_name = None
                deterministic_recall = (
                    _CONVERSATION_INTELLIGENCE.deterministic_phrase_recall(message, history)
                    if conversation_recall and not ENABLE_PROVENANCE_V1 else None
                )
                if deterministic_recall is not None:
                    response_route = "tool_generated"
                    pieces = iter([deterministic_recall])
                elif approval_request(message):
                    response_route = "tool_generated"
                    pieces = iter([execute_pending_approved()])
                elif asks_for_action(message):
                    response_route = "tool_generated"
                    pieces = iter([action_guidance(message)])
                elif "github" in message.lower() and "authenticated" in message.lower() and "repositories" not in message.lower() and "repos" not in message.lower():
                    try:
                        pieces = iter([github_authentication_answer()])
                    except Exception as exc:
                        pieces = iter([f"GitHub authentication test failed: {exc}"])
                elif "readme" in message.lower() and ("github" in message.lower() or "repository" in message.lower() or "repo" in message.lower()):
                    try:
                        pieces = iter([github_readme_answer(message)])
                    except Exception as exc:
                        pieces = iter([f"GitHub README access failed: {exc}"])
                elif asks_for_github_repositories(message):
                    try:
                        pieces = iter([github_repositories_answer(message)])
                    except Exception as exc:
                        pieces = iter([f"I couldn't retrieve the GitHub repositories right now: {exc}"])
                elif is_windows_diagnostic_request(message):
                    response_route = "tool_generated"
                    pieces = iter([fallback(message)])
                elif ("http 401" in message.lower() or "401 unauthorized" in message.lower()
                      or "github api returned 401" in message.lower()):
                    pieces = iter([github_401_answer()])
                elif asks_for_tomorrow_weather(message):
                    try:
                        pieces = iter([
                            tomorrow_weather_answer(
                                message,
                                data.get("location")
                            )
                        ])
                    except Exception as exc:
                        pieces = iter([
                            f"I couldn't retrieve tomorrow's forecast right now. "
                            f"The lookup failed safely: {exc}"
                        ])
                elif asks_for_combined_datetime_weather(message):
                    try:
                        pieces = iter([live_datetime_weather_answer(message, data.get("location"))])
                    except Exception as exc:
                        pieces = iter([current_datetime_answer() + f"\\n\\nI couldn't retrieve live weather right now. The lookup failed safely: {exc}"])
                elif asks_for_current_weather(message):
                    try:
                        pieces = iter([weather_answer(message, data.get("location"))])
                    except Exception as exc:
                        pieces = iter([f"I couldn't retrieve live weather right now. The lookup failed safely: {exc}"])
                elif asks_for_datetime(message):
                    pieces = iter([current_datetime_answer()])
                else:
                    if ENABLE_PROVENANCE_V1 and ebr_bounded_request and ebr_result and ebr_result.status == "NO_EVIDENCE":
                        response_route = "deterministic_no_evidence"
                        pieces = iter([
                            "I do not have sufficient evidence to determine that project-specific fact. "
                            "No verified provenance-backed evidence was retrieved for this request."
                        ])
                    elif ENABLE_PROVENANCE_V1 and ebr_result and ebr_result.status == "ERROR":
                        response_route = "deterministic_error"
                        pieces = iter(["I could not complete evidence retrieval for this request. I will not substitute a guess for the missing retrieval result."])
                    elif ENABLE_PROVENANCE_V1 and ebr_result and ebr_result.status == "CONFLICT_FOUND":
                        response_route = "deterministic_conflict"
                        pieces = iter(["I found conflicting evidence for this request. I cannot select one source as authoritative without a traceable precedence rule."])
                    else:
                        response_route = "ebr_validated" if (ENABLE_PROVENANCE_V1 and ebr_result and ebr_result.status == "HIT_VALIDATED") else "llm_generated"
                        model_invoked = bool(ollama_available())
                        model_name = str(model) if model_invoked else None
                        pieces = ollama_stream(model, prompt_messages) if model_invoked else iter([fallback(message)])
                output = ""
                for piece in pieces:
                    output += piece
                    raw = piece.encode()
                    self.wfile.write(f"{len(raw):X}\r\n".encode() + raw + b"\r\n")
                    self.wfile.flush()
                append_history({"role":"assistant", "content":output, "time":datetime.now(timezone.utc).isoformat(), "conversation_id":conversation_id})
                if ENABLE_PROVENANCE_V1 and ebr_result and ebr_result.status == "HIT_VALIDATED":
                    diagnostic["rag_status"] = "INJECTED"
                    diagnostic["terminal_state"] = "HIT_VALIDATED"
                    diagnostic["rag_state_history"] = ["SEARCHING", "HIT", "HIT_VALIDATED", "INJECTED"]
                    diagnostic["rag_injected_claim_ids"] = [str(c.get("id")) for c in ebr_result.claims]
                    if response_route == "llm_generated":
                        response_route = "ebr_validated"
                elif ebr_result and ebr_result.status == "NO_EVIDENCE":
                    diagnostic["terminal_state"] = "NO_EVIDENCE"
                    diagnostic["rag_state_history"] = ["SEARCHING", "NO_EVIDENCE"]
                elif ebr_result and ebr_result.status == "ERROR":
                    diagnostic["terminal_state"] = "ERROR"
                    diagnostic["rag_state_history"] = ["SEARCHING", "ERROR"]
                elif ebr_result and ebr_result.status == "CONFLICT_FOUND":
                    diagnostic["terminal_state"] = "CONFLICT_FOUND"
                    diagnostic["rag_state_history"] = ["SEARCHING", "HIT", "CONFLICT_FOUND"]
                elif ebr_result:
                    diagnostic["terminal_state"] = ebr_result.status
                    diagnostic["rag_state_history"] = ["SEARCHING", ebr_result.status]
                diagnostic["response_source"] = _response_source_for(response_route, model_invoked)
                diagnostic["model_invoked"] = bool(model_invoked)
                diagnostic["model_name"] = model_name
                diagnostic["response_hash"] = hashlib.sha256(output.encode("utf-8")).hexdigest()
                diagnostic["response_preview"] = output[:200]
                diagnostic["request_time_ms"] = round((time.perf_counter() - request_started) * 1000, 2)
                diagnostic["response_time_ms"] = diagnostic["request_time_ms"]
                diagnostic["response_chars"] = len(output)
                diagnostic["status"] = "completed"
                trace["rag_status"] = diagnostic["rag_status"]
                trace["terminal_state"] = diagnostic["terminal_state"]
                trace["rag_state_history"] = list(diagnostic["rag_state_history"])
                trace["response_source"] = diagnostic["response_source"]
                trace["model_invoked"] = diagnostic["model_invoked"]
                trace["model_name"] = diagnostic["model_name"]
                trace["response_hash"] = diagnostic["response_hash"]
                trace["response_preview"] = diagnostic["response_preview"]
                record_context_trace(trace)
                record_context_diagnostic(diagnostic)
                try:
                    _record_runtime_observation(message, output, project_id, str(model), knowledge_hits, conversation_id)
                except Exception as engineering_exc:
                    log_activity(f"Knowledge Engineering observation skipped: {engineering_exc}")
                if len(history) <= 1:
                    _DATABASE.update_conversation_title(conversation_id, _conversation_title_from_message(message))
                log_activity("Angel AI response completed")
            except Exception as exc:
                raw = ("Ollama error: " + str(exc) + "\n" + fallback(message)).encode()
                self.wfile.write(f"{len(raw):X}\r\n".encode() + raw + b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            return
        self.send_error(404)

    def log_message(self, format, *args):
        return


def run(host="127.0.0.1", port=8765):
    return ThreadingHTTPServer((host, port), Handler)



