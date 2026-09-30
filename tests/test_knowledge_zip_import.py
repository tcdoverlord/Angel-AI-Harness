import io
import json
import zipfile
from pathlib import Path

from angel_platform.knowledge import library


def test_markdown_only_zip_imports_without_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(library, "PACKS_DIR", tmp_path / "packs")
    monkeypatch.setattr(library, "FILES_DIR", tmp_path / "files")
    monkeypatch.setattr(library, "INDEX_DIR", tmp_path / "index")

    blob = io.BytesIO()
    with zipfile.ZipFile(blob, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "KnowledgeBase-LocalAI-Angel_V1.0.1/ANGEL_DEVELOPMENT/00_README.md",
            "# Angel Knowledge\n\nLocalAI knowledge.",
        )
        z.writestr(
            "KnowledgeBase-LocalAI-Angel_V1.0.1/ANGEL_DEVELOPMENT/01_ANGEL_FOUR_PILLARS.md",
            "# Four Pillars\n\nWaits, Alignment, Containment, Repair.",
        )

    result = library._safe_extract_zip(blob.getvalue())

    assert result["documents"] == 2
    assert result["manifest_generated"] is True
    pack = library.PACKS_DIR / result["id"]
    assert (pack / "manifest.json").exists()
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "KnowledgeBase-LocalAI-Angel_V1.0.1"
    assert len(list(pack.rglob("*.md"))) == 2


def test_standard_manifest_pack_still_imports(tmp_path, monkeypatch):
    monkeypatch.setattr(library, "PACKS_DIR", tmp_path / "packs")
    monkeypatch.setattr(library, "FILES_DIR", tmp_path / "files")
    monkeypatch.setattr(library, "INDEX_DIR", tmp_path / "index")

    blob = io.BytesIO()
    with zipfile.ZipFile(blob, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "KnowledgePack/manifest.json",
            json.dumps({
                "name": "Angel Architecture",
                "version": "1.0.0",
                "category": "Architecture",
            }),
        )
        z.writestr(
            "KnowledgePack/knowledge/architecture.md",
            "# Architecture\n\nKnowledge-first Angel.",
        )

    result = library._safe_extract_zip(blob.getvalue())

    assert result["name"] == "Angel Architecture"
    assert result["documents"] == 1
