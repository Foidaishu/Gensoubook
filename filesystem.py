"""
Gensoubook — File System Manager
Handles workspace selection, folder/file CRUD, .note and .board formats.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path


# ─── File type constants ───────────────────────────────────────────
NOTE_EXT   = ".note"
BOARD_EXT  = ".board"
CONFIG_DIR = Path.home() / ".gensoubook"
CONFIG_FILE = CONFIG_DIR / "config.json"

NOTE_ICONS  = {"note": "📄", "board": "🗺️", "folder": "📁"}

TEMPLATE_BLANK = {
    "type": "note",
    "title": "Untitled",
    "created": "",
    "modified": "",
    "tags": [],
    "blocks": [{"type": "text", "value": ""}]
}

TEMPLATE_JOURNAL = {
    "type": "note",
    "title": "",           # filled at creation
    "created": "",
    "modified": "",
    "tags": ["journal"],
    "blocks": [
        {"type": "text", "value": "## {date}\n\n**How was today?**\n\n\n\n---\n\n**What did I accomplish?**\n\n\n\n---\n\n**Tomorrow's focus:**\n\n"}
    ]
}

TEMPLATE_MEETING = {
    "type": "note",
    "title": "Meeting Notes",
    "created": "",
    "modified": "",
    "tags": ["meeting"],
    "blocks": [
        {"type": "text", "value": "## Meeting: {title}\n📅 Date: {date}\n\n---\n\n### 👥 Attendees\n- \n\n### 📋 Agenda\n1. \n\n### 📝 Notes\n\n\n### ✅ Action Items\n- [ ] \n\n### 📌 Next Meeting\n"}
    ]
}

TEMPLATE_WHITEBOARD = {
    "type": "board",
    "title": "Whiteboard",
    "created": "",
    "modified": "",
    "tags": [],
    "canvas": {"zoom": 1.0, "offset_x": 0.0, "offset_y": 0.0},
    "objects": []
}

TEMPLATE_TABLE = {
    "type": "note",
    "title": "Table Note",
    "created": "",
    "modified": "",
    "tags": [],
    "blocks": [
        {
            "type": "table",
            "columns": ["Column 1", "Column 2", "Column 3"],
            "col_types": ["text", "text", "text"],
            "col_widths": [150, 150, 150],
            "rows": [["", "", ""], ["", "", ""]],
            "style": {
                "header_highlight": True,
                "alternating_rows": False,
                "border_style": "solid"
            }
        }
    ]
}

TEMPLATES = {
    "blank":      ("📄 Blank Note",      TEMPLATE_BLANK),
    "journal":    ("📔 Daily Journal",   TEMPLATE_JOURNAL),
    "meeting":    ("🗒️ Meeting Notes",   TEMPLATE_MEETING),
    "whiteboard": ("🗺️ Whiteboard",      TEMPLATE_WHITEBOARD),
    "table":      ("🗃️ Table Note",      TEMPLATE_TABLE),
}


# ─── Config helpers ───────────────────────────────────────────────
def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get_workspace() -> str | None:
    return load_config().get("workspace")


def set_workspace(path: str):
    cfg = load_config()
    cfg["workspace"] = path
    save_config(cfg)


# ─── Workspace / folder helpers ──────────────────────────────────
def init_workspace(path: str):
    """Create the workspace folder with a Welcome note."""
    ws = Path(path)
    ws.mkdir(parents=True, exist_ok=True)
    welcome_path = ws / f"Welcome{NOTE_EXT}"
    if not welcome_path.exists():
        note = _base_note("note")
        note["title"] = "Welcome to Gensoubook"
        note["blocks"] = [{"type": "text", "value":
            "# Welcome to Gensoubook 📓\n\n"
            "This is your personal spellbook. Everything you write lives here.\n\n"
            "**Getting started:**\n"
            "- Create a folder with the `+` button\n"
            "- Create a new note inside any folder\n"
            "- Try the Whiteboard template for freeform ideas\n\n"
            "*Your notes are saved locally — no cloud, no accounts.*"
        }]
        _write_file(welcome_path, note)
    set_workspace(path)


def list_workspace(path: str) -> list[dict]:
    """Return a flat tree of folders and files in the workspace."""
    root = Path(path)
    if not root.exists():
        return []
    return _scan_dir(root)


def _scan_dir(directory: Path) -> list[dict]:
    items = []
    try:
        entries = sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                items.append({
                    "kind": "folder",
                    "name": entry.name,
                    "path": str(entry),
                    "children": _scan_dir(entry)
                })
            elif entry.suffix in (NOTE_EXT, BOARD_EXT):
                meta = _read_meta(entry)
                items.append({
                    "kind": meta.get("type", "note"),
                    "name": meta.get("title", entry.stem),
                    "path": str(entry),
                    "tags": meta.get("tags", []),
                    "modified": meta.get("modified", ""),
                })
    except PermissionError:
        pass
    return items


# ─── Note CRUD ───────────────────────────────────────────────────
def create_note(folder: str, template_key: str = "blank", title: str = "") -> str:
    """Create a new note from a template. Returns the file path."""
    import copy
    _, tmpl = TEMPLATES[template_key]
    note = copy.deepcopy(tmpl)

    now = _now()
    note["created"] = now
    note["modified"] = now

    if template_key == "journal":
        date_str = datetime.now().strftime("%A, %B %d %Y")
        note["title"] = date_str
        note["blocks"][0]["value"] = note["blocks"][0]["value"].replace("{date}", date_str)
    elif template_key == "meeting":
        note["title"] = title or "Meeting Notes"
        note["blocks"][0]["value"] = (
            note["blocks"][0]["value"]
            .replace("{title}", note["title"])
            .replace("{date}", datetime.now().strftime("%B %d, %Y"))
        )
    else:
        note["title"] = title or note["title"]

    ext = BOARD_EXT if note["type"] == "board" else NOTE_EXT
    filename = _safe_filename(note["title"]) + ext
    path = Path(folder) / filename
    # Avoid overwriting
    counter = 1
    while path.exists():
        path = Path(folder) / f"{_safe_filename(note['title'])}_{counter}{ext}"
        counter += 1

    _write_file(path, note)
    return str(path)


def read_note(path: str) -> dict:
    return _read_file(Path(path))


def save_note(path: str, data: dict):
    data["modified"] = _now()
    _write_file(Path(path), data)


def delete_note(path: str, trash_dir: str):
    """Move a note to the trash folder instead of hard deleting."""
    src = Path(path)
    trash = Path(trash_dir)
    trash.mkdir(parents=True, exist_ok=True)
    dest = trash / src.name
    counter = 1
    while dest.exists():
        dest = trash / f"{src.stem}_{counter}{src.suffix}"
        counter += 1
    shutil.move(str(src), str(dest))
    return str(dest)


def rename_note(path: str, new_title: str) -> str:
    """Rename a note file and update its title field. Returns new path."""
    p = Path(path)
    data = _read_file(p)
    data["title"] = new_title
    data["modified"] = _now()

    new_filename = _safe_filename(new_title) + p.suffix
    new_path = p.parent / new_filename
    counter = 1
    while new_path.exists() and new_path != p:
        new_path = p.parent / f"{_safe_filename(new_title)}_{counter}{p.suffix}"
        counter += 1

    _write_file(p, data)
    if new_path != p:
        p.rename(new_path)
    return str(new_path)


def create_folder(parent: str, name: str) -> str:
    folder = Path(parent) / _safe_filename(name)
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder)


def rename_folder(path: str, new_name: str) -> str:
    p = Path(path)
    new_path = p.parent / _safe_filename(new_name)
    p.rename(new_path)
    return str(new_path)


def delete_folder(path: str, trash_dir: str) -> str:
    src = Path(path)
    trash = Path(trash_dir)
    trash.mkdir(parents=True, exist_ok=True)
    dest = trash / src.name
    counter = 1
    while dest.exists():
        dest = trash / f"{src.name}_{counter}"
        counter += 1
    shutil.move(str(src), str(dest))
    return str(dest)


# ─── Search ──────────────────────────────────────────────────────
def search_notes(workspace: str, query: str) -> list[dict]:
    """Search all notes for query string. Returns list of matches."""
    results = []
    q = query.lower()
    for p in Path(workspace).rglob(f"*{NOTE_EXT}"):
        try:
            data = _read_file(p)
            title = data.get("title", "")
            content = " ".join(
                b.get("value", "") for b in data.get("blocks", [])
                if b.get("type") == "text"
            )
            if q in title.lower() or q in content.lower():
                # Find snippet
                idx = content.lower().find(q)
                snippet = content[max(0, idx-40):idx+80].strip() if idx >= 0 else ""
                results.append({
                    "title": title,
                    "path": str(p),
                    "snippet": snippet,
                    "tags": data.get("tags", []),
                    "modified": data.get("modified", ""),
                })
        except Exception:
            continue
    return results


# ─── Internal helpers ─────────────────────────────────────────────
def _base_note(kind: str) -> dict:
    now = _now()
    return {"type": kind, "title": "", "created": now, "modified": now, "tags": [], "blocks": []}


def _read_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_file(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_meta(path: Path) -> dict:
    """Read only the top-level fields (no blocks) for fast tree loading."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return {k: v for k, v in raw.items() if k != "blocks" and k != "objects"}
    except Exception:
        return {}


def _safe_filename(name: str) -> str:
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_()")
    cleaned = "".join(c if c in keep else "_" for c in name).strip()
    return cleaned[:80] or "untitled"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
