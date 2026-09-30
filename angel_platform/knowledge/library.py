from __future__ import annotations
from pathlib import Path
import json, re, hashlib, zipfile, io, shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SEED_FILE = ROOT / "seed_cards.json"
EXPANSION_FILE = ROOT / "expansion_cards.json"
DATA = Path.home() / "Angel_Platform"
KNOWLEDGE_FILE = DATA / "knowledge_cards.json"
FEEDBACK_FILE = DATA / "feedback.json"
FIELD_GUIDES = ROOT / "field_guides"
USER_KNOWLEDGE = DATA / "knowledge"
PACKS_DIR = USER_KNOWLEDGE / "packs"
FILES_DIR = USER_KNOWLEDGE / "files"
INDEX_DIR = USER_KNOWLEDGE / "index"
INDEX_FILE = INDEX_DIR / "index.json"
for _path in (PACKS_DIR, FILES_DIR, INDEX_DIR):
    _path.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return default

def _save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def _safe_rel(value: str) -> Path:
    raw = str(value or "").replace("\\", "/").strip().lstrip("/")
    path = Path(raw)
    if not raw or path.is_absolute() or ".." in path.parts:
        raise ValueError("Unsafe knowledge path.")
    if path.suffix.lower() != ".md":
        raise ValueError("Knowledge files must use the .md extension.")
    return path


def _chunk(text: str, size: int = 1100, overlap: int = 160):
    clean = re.sub(r"\r\n?", "\n", str(text or "")).strip()
    if not clean:
        return []
    pieces=[]
    start=0
    while start < len(clean):
        end=min(len(clean), start+size)
        if end < len(clean):
            boundary=max(clean.rfind("\n\n", start, end), clean.rfind(". ", start, end))
            if boundary > start+size//2:
                end=boundary+2 if clean[boundary:boundary+2]==". " else boundary
        piece=clean[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(clean): break
        start=max(start+1, end-overlap)
    return pieces


def _user_documents():
    docs=[]
    if FILES_DIR.exists():
        for path in sorted(FILES_DIR.rglob("*.md")):
            try:
                text=path.read_text(encoding="utf-8")
            except OSError:
                continue
            rel=path.relative_to(FILES_DIR).as_posix()
            docs.append({"path":rel,"title":path.stem.replace("-"," ").replace("_"," ").title(),"content":text,"source":"user"})
    if PACKS_DIR.exists():
        for pack in sorted(PACKS_DIR.iterdir()):
            if not pack.is_dir(): continue
            root=pack/"knowledge"
            if not root.exists(): root=pack
            for path in sorted(root.rglob("*.md")):
                try: text=path.read_text(encoding="utf-8")
                except OSError: continue
                rel=path.relative_to(pack).as_posix()
                docs.append({"path":f"packs/{pack.name}/{rel}","title":path.stem.replace("-"," ").replace("_"," ").title(),"content":text,"source":"pack","pack":pack.name})
    return docs


def reindex_user_knowledge():
    chunks=[]
    documents=_user_documents()
    for doc in documents:
        for idx, piece in enumerate(_chunk(doc["content"])):
            chunks.append({"id":hashlib.sha256(f'{doc["path"]}:{idx}'.encode()).hexdigest()[:16],"path":doc["path"],"title":doc["title"],"text":piece,"chunk":idx,"source":doc["source"],"pack":doc.get("pack","")})
    payload={"version":1,"indexed_at":datetime.now(timezone.utc).isoformat(),"documents":len(documents),"chunks":len(chunks),"chunks_data":chunks}
    _save(INDEX_FILE,payload)
    return payload


def _load_user_index():
    data=_load(INDEX_FILE,{})
    if not isinstance(data,dict) or not isinstance(data.get("chunks_data"),list):
        return reindex_user_knowledge()
    return data


def knowledge_center():
    idx=_load_user_index()
    docs=_user_documents()
    categories=sorted({p.split("/")[1] for p in [d["path"] for d in docs] if len(p.split("/"))>2 and p.startswith("packs/")} | {"Custom" if d["source"]=="user" else "Packs" for d in docs})
    packs=[]
    if PACKS_DIR.exists():
        for pack in sorted(PACKS_DIR.iterdir()):
            if not pack.is_dir(): continue
            manifest=_load(pack/"manifest.json",{})
            packdocs=[d for d in docs if d.get("pack")==pack.name]
            packs.append({"name":manifest.get("name",pack.name),"id":pack.name,"version":manifest.get("version","1.0.0"),"author":manifest.get("author",""),"description":manifest.get("description",""),"category":manifest.get("category","General"),"documents":len(packdocs),"chunks":sum(len(_chunk(d["content"])) for d in packdocs),"last_indexed":idx.get("indexed_at","")})
    return {"root":str(USER_KNOWLEDGE),"documents":len(docs),"chunks":idx.get("chunks",0),"indexed_at":idx.get("indexed_at",""),"categories":categories,"packs":packs,"files":[{"path":d["path"],"title":d["title"],"source":d["source"],"pack":d.get("pack","")} for d in docs]}


def _resolve_user_file(rel: str):
    path=Path(str(rel or "").replace("\\","/").lstrip("/"))
    if not path.parts or ".." in path.parts:
        raise ValueError("Unsafe knowledge path.")
    if path.parts[0]=="packs":
        if len(path.parts)<3: raise ValueError("Invalid pack path.")
        target=PACKS_DIR / path.parts[1] / Path(*path.parts[2:])
        root=(PACKS_DIR/path.parts[1]).resolve()
    else:
        rel = Path(*path.parts[1:]) if path.parts[0]=="files" else path
        target=FILES_DIR / rel
        root=FILES_DIR.resolve()
    target=target.resolve()
    if root not in target.parents and target != root: raise ValueError("Unsafe knowledge path.")
    if target.suffix.lower()!=".md": raise ValueError("Knowledge files must be Markdown.")
    return target


def read_user_document(rel: str):
    path=_resolve_user_file(rel)
    if not path.exists(): raise FileNotFoundError(rel)
    return {"path":str(path.relative_to(USER_KNOWLEDGE).as_posix()),"content":path.read_text(encoding="utf-8")}


def write_user_document(rel: str, content: str):
    safe=_safe_rel(rel)
    if safe.parts and safe.parts[0] == "packs":
        if len(safe.parts) < 3:
            raise ValueError("Invalid pack document path.")
        pack_root = (PACKS_DIR / safe.parts[1]).resolve()
        if not pack_root.exists() or not pack_root.is_dir():
            raise FileNotFoundError(f"Knowledge pack not found: {safe.parts[1]}")
        target = (pack_root / Path(*safe.parts[2:])).resolve()
        if pack_root not in target.parents:
            raise ValueError("Unsafe knowledge path.")
    else:
        target=FILES_DIR/safe
        if FILES_DIR.resolve() not in target.resolve().parents:
            raise ValueError("Unsafe knowledge path.")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(str(content or ""),encoding="utf-8")
    reindex_user_knowledge()
    return read_user_document(str(target.relative_to(USER_KNOWLEDGE).as_posix()))


def delete_user_document(rel: str):
    target=_resolve_user_file(rel)
    if not target.exists(): raise FileNotFoundError(rel)
    target.unlink()
    reindex_user_knowledge()
    return True


def delete_knowledge_pack(pack_id: str):
    clean = str(pack_id or "").strip()
    if not clean or clean in {".", ".."} or "/" in clean or "\\" in clean:
        raise ValueError("Invalid knowledge pack ID.")
    target = (PACKS_DIR / clean).resolve()
    root = PACKS_DIR.resolve()
    if root not in target.parents:
        raise ValueError("Unsafe knowledge pack path.")
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError(clean)
    shutil.rmtree(target)
    index = reindex_user_knowledge()
    return {"deleted": clean, "index": index}


def create_category(name: str):
    clean=re.sub(r"[^A-Za-z0-9 _-]","",str(name or "")).strip()
    if not clean: raise ValueError("Category name is required.")
    target=FILES_DIR/clean
    target.mkdir(parents=True,exist_ok=True)
    return clean


def _safe_extract_zip(blob: bytes):
    """Import a knowledge ZIP.

    Standard packs may contain manifest.json and a knowledge/ directory.
    For convenience, Angel also accepts a Markdown-only ZIP (including a
    top-level wrapper directory) and creates a minimal manifest automatically.
    This makes existing knowledge archives usable without requiring a developer
    to rebuild the ZIP first.
    """
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        if not names:
            raise ValueError("Knowledge ZIP is empty.")

        files = []
        manifests = []
        top_levels = set()

        for name in names:
            norm = name.replace("\\", "/").lstrip("/")
            parts = Path(norm).parts
            if not norm or not parts:
                continue
            if ".." in parts or Path(norm).is_absolute():
                raise ValueError("Knowledge pack contains an unsafe path.")
            if name.endswith("/"):
                continue

            suffix = Path(norm).suffix.lower()
            if suffix not in {".md", ".json", ".png", ".jpg", ".jpeg", ".webp"}:
                # Ignore common archive metadata rather than failing the
                # entire import.
                continue

            files.append((name, norm))
            if Path(norm).name.lower() == "manifest.json":
                manifests.append(name)

            if len(parts) > 1:
                top_levels.add(parts[0])

        md_files = [(name, norm) for name, norm in files
                    if Path(norm).suffix.lower() == ".md"]

        if not md_files:
            raise ValueError("Knowledge ZIP does not contain any Markdown (.md) documents.")

        manifest_data = {}
        manifest_source = None

        # Prefer a manifest at the archive root, then any manifest supplied by
        # a wrapper directory.
        manifest_candidates = sorted(
            manifests,
            key=lambda n: (len(Path(n.replace("\\", "/")).parts), n.lower())
        )
        for manifest_name in manifest_candidates:
            try:
                candidate = json.loads(z.read(manifest_name).decode("utf-8"))
                if isinstance(candidate, dict):
                    manifest_data = candidate
                    manifest_source = manifest_name
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, OSError):
                continue

        # A manifest is optional for backwards-compatible Markdown archives.
        # If one is missing, derive a sensible pack name from the archive's
        # wrapper directory or the first Markdown document.
        if manifest_data:
            derived_name = str(manifest_data.get("name") or "").strip()
        else:
            derived_name = ""

        if not derived_name:
            if len(top_levels) == 1:
                derived_name = next(iter(top_levels))
            else:
                derived_name = Path(md_files[0][1]).stem

        pack_name = re.sub(r"[^A-Za-z0-9 _.-]", "", derived_name).strip()
        pack_name = pack_name or "Knowledge Pack"

        folder = re.sub(r"[^A-Za-z0-9_-]+", "-", pack_name.lower()).strip("-")
        folder = folder or "knowledge-pack"

        # Avoid silently merging a newly imported pack into an existing pack
        # when the same name is imported again.
        dest = PACKS_DIR / folder
        if dest.exists() and any(dest.iterdir()):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            dest = PACKS_DIR / f"{folder}-{stamp}"
            folder = dest.name

        dest.mkdir(parents=True, exist_ok=True)

        for name, norm in files:
            target = (dest / Path(norm)).resolve()
            root = dest.resolve()
            if root not in target.parents and target != root:
                raise ValueError("Knowledge pack contains an unsafe path.")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))

        # Standardize metadata even when the incoming archive was simply a
        # folder of Markdown files.
        manifest_path = dest / "manifest.json"
        if not manifest_path.exists():
            generated = {
                "name": pack_name,
                "version": str(manifest_data.get("version") or "1.0.0"),
                "author": str(manifest_data.get("author") or ""),
                "description": str(
                    manifest_data.get("description")
                    or "Imported Markdown knowledge pack."
                ),
                "category": str(manifest_data.get("category") or "General"),
            }
            manifest_path.write_text(
                json.dumps(generated, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            manifest_data = generated
        else:
            # If a nested manifest was used, expose the normalized metadata at
            # the pack root for the Knowledge Center.
            try:
                root_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if isinstance(root_manifest, dict):
                    manifest_data = root_manifest
            except (OSError, json.JSONDecodeError):
                pass

        # If the archive did not use the standard knowledge/ directory,
        # _user_documents() already supports Markdown anywhere inside the pack.
        document_count = len(list(dest.rglob("*.md")))
        return {
            "name": str(manifest_data.get("name") or pack_name),
            "id": folder,
            "documents": document_count,
            "manifest_generated": manifest_source is None,
        }


def cards():
    seed = _load(SEED_FILE, [])
    expansion = _load(EXPANSION_FILE, [])
    custom = _load(KNOWLEDGE_FILE, [])
    by_id = {str(x.get("id")): x for x in seed if isinstance(x, dict) and x.get("id")}
    for item in expansion:
        if isinstance(item, dict) and item.get("id"):
            by_id[str(item["id"])] = item
    for item in custom:
        if isinstance(item, dict) and item.get("id"):
            by_id[str(item["id"])] = item
    # Field guides are indexed as local knowledge documents. The full files remain
    # on disk; indexing a bounded excerpt keeps chat retrieval responsive.
    if FIELD_GUIDES.exists():
        for path in sorted(FIELD_GUIDES.glob("*.md")):
            try:
                body = path.read_text(encoding="utf-8")
            except OSError:
                continue
            item_id = "field-guide-" + path.stem
            by_id[item_id] = {
                "id": item_id,
                "title": path.stem.replace("-", " ").title(),
                "tags": ["field-guide", path.stem],
                "content": body[:12000],
                "source": str(path.name),
            }
    for doc in _user_documents():
        by_id["user-" + hashlib.sha256(doc["path"].encode()).hexdigest()[:16]] = {
            "id": "user-" + hashlib.sha256(doc["path"].encode()).hexdigest()[:16],
            "title": doc["title"], "tags": ["user-knowledge", doc["path"]],
            "content": doc["content"][:16000], "source": doc["path"]
        }
    return list(by_id.values())

def search(query: str, limit: int = 4):
    terms = {x for x in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", str(query).lower())}
    ranked = []
    for card in cards():
        hay = " ".join([
            str(card.get("title", "")),
            " ".join(map(str, card.get("tags", []))),
            str(card.get("content", "")),
        ]).lower()
        score = sum(2 if term in str(card.get("tags", [])).lower() else 1 for term in terms if term in hay)
        if score:
            ranked.append((score, card))
    ranked.sort(key=lambda pair: (-pair[0], str(pair[1].get("title", ""))))
    return [card for _, card in ranked[:max(1, min(int(limit), 10))]]

def context_for(query: str, limit: int = 6):
    """Build a bounded retrieval context so a large library cannot overflow the model context window."""
    found = search(query, limit)
    if not found:
        return ""
    lines = ["Relevant Angel Knowledge Library context (retrieved, not authoritative live state):"]
    budget = 7600
    used = 0
    for card in found:
        title = str(card.get("title", "Untitled"))
        content = re.sub(r"\s+", " ", str(card.get("content", ""))).strip()
        snippet = content[:1700]
        block = f"- {title}: {snippet}"
        if used + len(block) > budget:
            break
        lines.append(block)
        used += len(block)
    lines.append("Use retrieved knowledge as background. Do not claim it proves a live system state.")
    return "\n".join(lines)

def record_feedback(message: str, rating: str, note: str = "", conversation_id: str = ""):
    allowed = {"helpful", "incorrect", "incomplete", "correction"}
    rating = str(rating).strip().lower()
    if rating not in allowed:
        raise ValueError("Feedback rating must be helpful, incorrect, incomplete, or correction.")
    records = _load(FEEDBACK_FILE, [])
    records.append({
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "rating": rating,
        "message": str(message)[:4000],
        "note": str(note)[:4000],
        "conversation_id": str(conversation_id)[:200],
        "time": datetime.now(timezone.utc).isoformat(),
    })
    _save(FEEDBACK_FILE, records[-500:])
    return records[-1]["id"]

def status():
    return {"seed_cards": len(_load(SEED_FILE, [])), "expansion_cards": len(_load(EXPANSION_FILE, [])), "total_cards": len(cards()), "feedback_file": str(FEEDBACK_FILE)}
