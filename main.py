"""
Gensoubook — All-in-one entry point
Works when all .py files are in the same folder.
"""

import sys
import os

# ── Make sure our own folder is on the path ──────────────────────
_HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, _HERE)

# ── Inline the theme so there's no import dependency ─────────────
DARK = {
    "bg":           "#13131a",
    "sidebar_bg":   "#1a1a24",
    "panel_bg":     "#16161e",
    "border":       "#2a2a3a",
    "accent":       "#c084fc",
    "accent_dim":   "#7c3aed",
    "accent_soft":  "#2d1f4a",
    "text_primary": "#ece8f4",
    "text_muted":   "#6b6880",
    "hover":        "#22222e",
    "active":       "#2a2040",
    "tab_bg":       "#1a1a24",
    "tab_active":   "#231e35",
    "toolbar":      "#16161e",
    "warning":      "#fbbf24",
    "border_h":     "#4a3a6a",
    "success":      "#6ee7b7",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK['bg']};
    color: {DARK['text_primary']};
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
    border: none;
}}
QSplitter::handle {{ background-color: {DARK['border']}; width:1px; height:1px; }}
QTreeWidget {{
    background-color: {DARK['sidebar_bg']}; border:none; outline:none;
    padding:4px 2px; color:{DARK['text_primary']}; font-size:13px;
}}
QTreeWidget::item {{ padding:5px 6px; border-radius:6px; margin:1px 4px; }}
QTreeWidget::item:hover {{ background-color:{DARK['hover']}; }}
QTreeWidget::item:selected {{ background-color:{DARK['active']}; color:{DARK['accent']}; }}
QTextEdit {{
    background-color:{DARK['panel_bg']}; border:none; color:{DARK['text_primary']};
    font-family:'Cascadia Code','Fira Code','Consolas',monospace;
    font-size:14px; padding:28px 36px;
    selection-background-color:{DARK['accent_soft']};
}}
QLineEdit {{
    background-color:{DARK['hover']}; border:1px solid {DARK['border']};
    border-radius:6px; color:{DARK['text_primary']}; padding:6px 10px; font-size:13px;
}}
QLineEdit:focus {{ border-color:{DARK['accent']}; }}
QPushButton {{
    background-color:{DARK['hover']}; color:{DARK['text_primary']};
    border:1px solid {DARK['border']}; border-radius:6px;
    padding:6px 14px; font-size:12px;
}}
QPushButton:hover {{ background-color:{DARK['accent_soft']}; border-color:{DARK['accent']}; }}
QPushButton:pressed {{ background-color:{DARK['accent_dim']}; }}
QPushButton:disabled {{ color:{DARK['text_muted']}; border-color:{DARK['border']}; background:transparent; }}
QStatusBar {{
    background-color:{DARK['toolbar']}; border-top:1px solid {DARK['border']};
    color:{DARK['text_muted']}; font-size:11px; padding:2px 10px;
}}
QScrollBar:vertical {{ background:transparent; width:6px; margin:0; }}
QScrollBar::handle:vertical {{
    background:{DARK['border']}; border-radius:3px; min-height:24px;
}}
QScrollBar::handle:vertical:hover {{ background:{DARK['border_h']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{ height:0; }}
QMenu {{
    background-color:{DARK['panel_bg']}; border:1px solid {DARK['border']};
    border-radius:8px; padding:4px; color:{DARK['text_primary']};
}}
QMenu::item {{ padding:6px 20px; border-radius:4px; }}
QMenu::item:selected {{ background-color:{DARK['active']}; color:{DARK['accent']}; }}
QMenu::separator {{ height:1px; background:{DARK['border']}; margin:4px 8px; }}
QToolTip {{
    background-color:{DARK['panel_bg']}; color:{DARK['text_primary']};
    border:1px solid {DARK['border']}; border-radius:4px;
    padding:4px 8px; font-size:11px;
}}
QDialog {{ background-color:{DARK['panel_bg']}; }}
QComboBox {{
    background-color:{DARK['hover']}; border:1px solid {DARK['border']};
    border-radius:6px; padding:5px 10px; color:{DARK['text_primary']}; font-size:12px;
}}
QComboBox:hover {{ border-color:{DARK['accent']}; }}
QComboBox QAbstractItemView {{
    background-color:{DARK['panel_bg']}; border:1px solid {DARK['border']};
    color:{DARK['text_primary']}; selection-background-color:{DARK['active']};
}}
QSpinBox {{
    background-color:{DARK['hover']}; border:1px solid {DARK['border']};
    border-radius:6px; padding:5px 8px; color:{DARK['text_primary']};
}}
QSpinBox:focus {{ border-color:{DARK['accent']}; }}
QMessageBox {{ background-color:{DARK['panel_bg']}; color:{DARK['text_primary']}; }}
"""

# ─────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────
import json
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStackedWidget, QStatusBar, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QPushButton, QLineEdit, QMenu, QDialog,
    QComboBox, QDialogButtonBox, QFormLayout, QMessageBox, QFileDialog,
    QSlider, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QPixmap, QAction
)

# ─────────────────────────────────────────────────────────────────
# FILESYSTEM
# ─────────────────────────────────────────────────────────────────
NOTE_EXT    = ".note"
BOARD_EXT   = ".board"
CONFIG_DIR  = Path.home() / ".gensoubook"
CONFIG_FILE = CONFIG_DIR / "config.json"
NOTE_ICONS  = {"note": "📄", "board": "🗺️", "folder": "📁"}

TEMPLATES = {
    "blank":      ("📄 Blank Note",     {"type":"note","title":"Untitled","tags":[],"blocks":[{"type":"text","value":""}]}),
    "journal":    ("📔 Daily Journal",  {"type":"note","title":"","tags":["journal"],"blocks":[{"type":"text","value":"## {date}\n\n**How was today?**\n\n\n\n---\n\n**What did I accomplish?**\n\n\n\n---\n\n**Tomorrow's focus:**\n\n"}]}),
    "meeting":    ("🗒️ Meeting Notes",  {"type":"note","title":"Meeting Notes","tags":["meeting"],"blocks":[{"type":"text","value":"## Meeting: {title}\n📅 {date}\n\n---\n\n### 👥 Attendees\n- \n\n### 📋 Agenda\n1. \n\n### 📝 Notes\n\n\n### ✅ Action Items\n- [ ] \n"}]}),
    "whiteboard": ("🗺️ Whiteboard",     {"type":"board","title":"Whiteboard","tags":[],"canvas":{"zoom":1.0,"offset_x":0,"offset_y":0},"objects":[]}),
    "table":      ("🗃️ Table Note",     {"type":"note","title":"Table Note","tags":[],"blocks":[{"type":"table","columns":["Column 1","Column 2","Column 3"],"col_types":["text","text","text"],"rows":[["","",""],["","",""]],"style":{"header_highlight":True,"alternating_rows":False,"border_style":"solid"}}]}),
}

def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except: pass
    return {}

def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

def get_workspace(): return load_config().get("workspace")
def set_workspace(path):
    cfg = load_config(); cfg["workspace"] = path; save_config(cfg)

def init_workspace(path):
    ws = Path(path); ws.mkdir(parents=True, exist_ok=True)
    welcome = ws / f"Welcome{NOTE_EXT}"
    if not welcome.exists():
        note = {"type":"note","title":"Welcome to Gensoubook","created":_now(),"modified":_now(),"tags":[],"blocks":[{"type":"text","value":"# Welcome to Gensoubook ✦\n\nThis is your personal spellbook. Everything you write lives here.\n\n**Getting started:**\n- Create a folder with the 📁 button\n- Create a new note inside any folder\n- Try the Whiteboard template for freeform ideas\n\n*Your notes are saved locally — no cloud, no accounts.*"}]}
        Path(welcome).write_text(json.dumps(note, indent=2), encoding="utf-8")
    set_workspace(path)

def list_workspace(path):
    root = Path(path)
    if not root.exists(): return []
    return _scan_dir(root)

def _scan_dir(directory):
    items = []
    try:
        for entry in sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name.lower())):
            if entry.name.startswith("."): continue
            if entry.is_dir():
                items.append({"kind":"folder","name":entry.name,"path":str(entry),"children":_scan_dir(entry)})
            elif entry.suffix in (NOTE_EXT, BOARD_EXT):
                meta = _read_meta(entry)
                items.append({"kind":meta.get("type","note"),"name":meta.get("title",entry.stem),"path":str(entry),"tags":meta.get("tags",[]),"modified":meta.get("modified","")})
    except PermissionError: pass
    return items

def create_note(folder, template_key="blank", title=""):
    import copy
    _, tmpl = TEMPLATES[template_key]
    note = copy.deepcopy(tmpl)
    now = _now(); note["created"] = now; note["modified"] = now
    if template_key == "journal":
        ds = datetime.now().strftime("%A, %B %d %Y"); note["title"] = ds
        note["blocks"][0]["value"] = note["blocks"][0]["value"].replace("{date}", ds)
    elif template_key == "meeting":
        note["title"] = title or "Meeting Notes"
        note["blocks"][0]["value"] = note["blocks"][0]["value"].replace("{title}", note["title"]).replace("{date}", datetime.now().strftime("%B %d, %Y"))
    else:
        if title: note["title"] = title
    ext = BOARD_EXT if note["type"] == "board" else NOTE_EXT
    path = Path(folder) / (_safe_fn(note["title"]) + ext)
    c = 1
    while path.exists():
        path = Path(folder) / f"{_safe_fn(note['title'])}_{c}{ext}"; c += 1
    path.write_text(json.dumps(note, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)

def read_note(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def save_note(path, data):
    data["modified"] = _now()
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def delete_note(path, trash_dir):
    src = Path(path); trash = Path(trash_dir); trash.mkdir(parents=True, exist_ok=True)
    dest = trash / src.name; c = 1
    while dest.exists(): dest = trash / f"{src.stem}_{c}{src.suffix}"; c += 1
    shutil.move(str(src), str(dest))

def create_folder(parent, name):
    f = Path(parent) / _safe_fn(name); f.mkdir(parents=True, exist_ok=True); return str(f)

def delete_folder(path, trash_dir):
    src = Path(path); trash = Path(trash_dir); trash.mkdir(parents=True, exist_ok=True)
    dest = trash / src.name; c = 1
    while dest.exists(): dest = trash / f"{src.name}_{c}"; c += 1
    shutil.move(str(src), str(dest))

def search_notes(workspace, query):
    results = []; q = query.lower()
    for p in Path(workspace).rglob(f"*{NOTE_EXT}"):
        try:
            data = read_note(str(p)); title = data.get("title","")
            content = " ".join(b.get("value","") for b in data.get("blocks",[]) if b.get("type")=="text")
            if q in title.lower() or q in content.lower():
                idx = content.lower().find(q)
                snippet = content[max(0,idx-40):idx+80].strip() if idx >= 0 else ""
                results.append({"title":title,"path":str(p),"snippet":snippet})
        except: continue
    return results

def _read_meta(path):
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return {k:v for k,v in raw.items() if k not in ("blocks","objects")}
    except: return {}

def _safe_fn(name):
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_()")
    return ("".join(c if c in keep else "_" for c in name).strip() or "untitled")[:80]

def _now(): return datetime.now().isoformat(timespec="seconds")


# ─────────────────────────────────────────────────────────────────
# SETUP DIALOG
# ─────────────────────────────────────────────────────────────────
class WorkspaceSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Gensoubook")
        self.setFixedSize(500, 320)
        self.setModal(True)
        self.selected_path = ""
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(0)

        icon = QLabel("✦")
        icon.setStyleSheet(f"color:{DARK['accent']}; font-size:36px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Gensoubook")
        title.setStyleSheet(f"color:{DARK['text_primary']}; font-size:20px; font-weight:700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Choose a folder where your notes will be saved.\nThis is your personal spellbook — stored only on your device.")
        sub.setStyleSheet(f"color:{DARK['text_muted']}; font-size:12px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        layout.addWidget(icon)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(sub)
        layout.addSpacing(24)

        row = QHBoxLayout(); row.setSpacing(8)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select a folder...")
        self.path_edit.setReadOnly(True)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(34)
        browse_btn.clicked.connect(self._browse)
        row.addWidget(self.path_edit); row.addWidget(browse_btn)
        layout.addLayout(row)
        layout.addSpacing(8)

        default = os.path.join(os.path.expanduser("~"), "Documents", "Gensoubook")
        sug = QPushButton(f"Use default: ~/Documents/Gensoubook")
        sug.setStyleSheet(f"QPushButton{{background:transparent;border:none;color:{DARK['accent']};font-size:11px;text-align:left;padding:0;}}QPushButton:hover{{color:{DARK['text_primary']};}}")
        sug.clicked.connect(lambda: self._set_path(default))
        layout.addWidget(sug)
        layout.addStretch()

        self.confirm_btn = QPushButton("Open Spellbook  →")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet(f"""
            QPushButton{{background:{DARK['accent_soft']};border:1px solid {DARK['accent']};
            border-radius:8px;color:{DARK['accent']};font-size:14px;font-weight:600;}}
            QPushButton:hover{{background:{DARK['accent_dim']};color:{DARK['text_primary']};}}
            QPushButton:disabled{{background:{DARK['hover']};border-color:{DARK['border']};color:{DARK['text_muted']};}}
        """)
        self.confirm_btn.clicked.connect(self.accept)
        layout.addWidget(self.confirm_btn)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Notes Folder")
        if path: self._set_path(path)

    def _set_path(self, path):
        self.selected_path = path
        self.path_edit.setText(path)
        self.confirm_btn.setEnabled(True)

    def get_path(self): return self.selected_path


# ─────────────────────────────────────────────────────────────────
# NEW ITEM DIALOG
# ─────────────────────────────────────────────────────────────────
class NewItemDialog(QDialog):
    def __init__(self, parent=None, mode="note"):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("New Folder" if mode == "folder" else "New Note")
        self.setFixedSize(360, 180 if mode == "note" else 130)
        self.setModal(True)
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Folder name" if mode == "folder" else "Note title")
        layout.addRow("Name:", self.name_edit)
        if mode == "note":
            self.tmpl_combo = QComboBox()
            for key, (label, _) in TEMPLATES.items():
                self.tmpl_combo.addItem(label, key)
            layout.addRow("Template:", self.tmpl_combo)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addRow(btns)
        self.name_edit.setFocus()

    def get_result(self):
        name = self.name_edit.text().strip()
        if self.mode == "folder": return name, None
        return name, self.tmpl_combo.currentData()


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    note_opened  = pyqtSignal(str)
    note_deleted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace = ""
        self.trash_dir = ""
        self.setMinimumWidth(190); self.setMaximumWidth(320)
        self.setStyleSheet(f"background:{DARK['sidebar_bg']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        layout.addWidget(self._top_bar())
        layout.addWidget(self._search_bar())
        self.tree = self._build_tree()
        layout.addWidget(self.tree)
        layout.addWidget(self._bottom_nav())

    def _icon_style(self, size=14):
        return f"QPushButton{{background:transparent;border:none;border-radius:6px;font-size:{size}px;padding:2px;color:{DARK['text_muted']};}}QPushButton:hover{{background:{DARK['hover']};color:{DARK['text_primary']};}}"

    def _top_bar(self):
        bar = QWidget(); bar.setFixedHeight(50)
        bar.setStyleSheet(f"background:{DARK['sidebar_bg']};border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(12,0,8,0)
        icon = QLabel("✦"); icon.setStyleSheet(f"color:{DARK['accent']};font-size:16px;")
        title = QLabel("Gensoubook"); title.setStyleSheet(f"color:{DARK['text_primary']};font-weight:700;font-size:14px;")
        lay.addWidget(icon); lay.addSpacing(6); lay.addWidget(title); lay.addStretch()
        nb = QPushButton("＋"); nb.setFixedSize(28,28); nb.setToolTip("New note")
        nb.setStyleSheet(self._icon_style()); nb.clicked.connect(self._new_note)
        fb = QPushButton("📁"); fb.setFixedSize(28,28); fb.setToolTip("New folder")
        fb.setStyleSheet(self._icon_style()); fb.clicked.connect(self._new_folder)
        lay.addWidget(fb); lay.addWidget(nb)
        return bar

    def _search_bar(self):
        c = QWidget(); c.setStyleSheet(f"background:{DARK['sidebar_bg']};")
        lay = QHBoxLayout(c); lay.setContentsMargins(10,6,10,6)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Search notes...")
        self.search_edit.setStyleSheet(f"QLineEdit{{background:{DARK['hover']};border:1px solid {DARK['border']};border-radius:6px;color:{DARK['text_primary']};padding:5px 10px;font-size:12px;}}QLineEdit:focus{{border-color:{DARK['accent']};}}")
        self._stimer = QTimer(); self._stimer.setSingleShot(True); self._stimer.timeout.connect(self._run_search)
        self.search_edit.textChanged.connect(lambda: self._stimer.start(300))
        lay.addWidget(self.search_edit); return c

    def _build_tree(self):
        t = QTreeWidget(); t.setHeaderHidden(True); t.setIndentation(14)
        t.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        t.customContextMenuRequested.connect(self._ctx_menu)
        t.itemDoubleClicked.connect(self._on_dbl)
        t.setStyleSheet(f"QTreeWidget{{background:{DARK['sidebar_bg']};border:none;outline:none;padding:4px 2px;color:{DARK['text_primary']};font-size:13px;}}QTreeWidget::item{{padding:5px 6px;border-radius:6px;margin:1px 4px;}}QTreeWidget::item:hover{{background:{DARK['hover']};}}QTreeWidget::item:selected{{background:{DARK['active']};color:{DARK['accent']};}}")
        return t

    def _bottom_nav(self):
        nav = QWidget(); nav.setFixedHeight(46)
        nav.setStyleSheet(f"background:{DARK['sidebar_bg']};border-top:1px solid {DARK['border']};")
        lay = QHBoxLayout(nav); lay.setContentsMargins(8,0,8,0); lay.setSpacing(2)
        # FIX BUG 7: connect each button to a real handler
        nav_actions = [
            ("⭐", "Favorites", self._show_favorites),
            ("🏷️", "Tags",      self._show_tags),
            ("🗑️", "Trash",     self._show_trash),
            ("⚙️", "Settings",  self._show_settings),
        ]
        for icon, tip, cb in nav_actions:
            b = QPushButton(icon); b.setFixedSize(30,30); b.setToolTip(tip)
            b.setStyleSheet(self._icon_style(16))
            b.clicked.connect(cb)
            lay.addWidget(b)
        lay.addStretch(); return nav

    def _show_favorites(self):
        self.tree.clear()
        if not self.workspace: return
        def _find(items):
            for it in items:
                if it["kind"] in ("note","board") and "favorite" in it.get("tags",[]):
                    node = self._make_item(it); self.tree.addTopLevelItem(node)
                if it["kind"] == "folder": _find(it.get("children",[]))
        _find(list_workspace(self.workspace))
        if self.tree.topLevelItemCount() == 0:
            empty = QTreeWidgetItem(["  No favorites yet"]); self.tree.addTopLevelItem(empty)

    def _show_tags(self):
        self.tree.clear()
        if not self.workspace: return
        tag_map = {}
        def _collect(items):
            for it in items:
                for tag in it.get("tags",[]):
                    tag_map.setdefault(tag, []).append(it)
                if it["kind"] == "folder": _collect(it.get("children",[]))
        _collect(list_workspace(self.workspace))
        if not tag_map:
            self.tree.addTopLevelItem(QTreeWidgetItem(["  No tags found"])); return
        for tag, notes in sorted(tag_map.items()):
            parent = QTreeWidgetItem([f"🏷️  {tag}"])
            for n in notes: parent.addChild(self._make_item(n))
            self.tree.addTopLevelItem(parent)
        self.tree.expandAll()

    def _show_trash(self):
        self.tree.clear()
        trash = Path(self.trash_dir)
        if not trash.exists():
            self.tree.addTopLevelItem(QTreeWidgetItem(["  Trash is empty"])); return
        found = False
        for p in trash.iterdir():
            if p.suffix in (NOTE_EXT, BOARD_EXT):
                found = True
                item = QTreeWidgetItem([f"🗑️  {p.stem}"])
                item.setData(0, Qt.ItemDataRole.UserRole, {"kind":"note","name":p.stem,"path":str(p)})
                self.tree.addTopLevelItem(item)
        if not found:
            self.tree.addTopLevelItem(QTreeWidgetItem(["  Trash is empty"]))

    def _show_settings(self):
        dlg = QDialog(self); dlg.setWindowTitle("Settings"); dlg.setFixedSize(360, 200)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(24,24,24,20); lay.setSpacing(12)
        lay.addWidget(QLabel("⚙️  Gensoubook Settings"))
        ws_lbl = QLabel(f"Workspace: {self.workspace}")
        ws_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;"); ws_lbl.setWordWrap(True)
        lay.addWidget(ws_lbl)
        change_btn = QPushButton("Change Workspace Folder")
        def _change():
            path = QFileDialog.getExistingDirectory(dlg, "Choose New Workspace")
            if path:
                set_workspace(path); self.load_workspace(path); dlg.accept()
        change_btn.clicked.connect(_change); lay.addWidget(change_btn)
        lay.addStretch()
        close_btn = QPushButton("Close"); close_btn.clicked.connect(dlg.accept); lay.addWidget(close_btn)
        dlg.exec()

    def load_workspace(self, path):
        self.workspace = path
        self.trash_dir = str(Path(path).parent / ".gensoubook_trash")
        self.refresh()

    def refresh(self):
        # Remember which folders were expanded
        expanded = set()
        def _collect(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and item.isExpanded():
                expanded.add(data.get("path",""))
            for i in range(item.childCount()):
                _collect(item.child(i))
        for i in range(self.tree.topLevelItemCount()):
            _collect(self.tree.topLevelItem(i))

        self.tree.clear()
        if not self.workspace: return
        for item in list_workspace(self.workspace):
            self.tree.addTopLevelItem(self._make_item(item))

        # FIX BUG 2: only re-expand folders that were open before, not everything
        def _restore(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("path","") in expanded:
                item.setExpanded(True)
            for i in range(item.childCount()):
                _restore(item.child(i))
        for i in range(self.tree.topLevelItemCount()):
            _restore(self.tree.topLevelItem(i))

    def _make_item(self, data):
        icon = NOTE_ICONS.get(data["kind"], "📄")
        item = QTreeWidgetItem([f"{icon}  {data['name']}"])
        item.setData(0, Qt.ItemDataRole.UserRole, data)
        if data["kind"] == "folder":
            for child in data.get("children", []):
                item.addChild(self._make_item(child))
        if data["kind"] == "board":
            item.setForeground(0, QColor(DARK["accent"]))
        return item

    def _sel_folder(self):
        item = self.tree.currentItem()
        if not item: return self.workspace
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data: return self.workspace
        if data["kind"] == "folder": return data["path"]
        return str(Path(data["path"]).parent)

    def _new_note(self):
        folder = self._sel_folder()
        dlg = NewItemDialog(self, "note")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, tmpl = dlg.get_result()
            if tmpl:
                path = create_note(folder, tmpl, name)
                self.refresh(); self.note_opened.emit(path)

    def _new_folder(self):
        parent = self._sel_folder()
        dlg = NewItemDialog(self, "folder")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, _ = dlg.get_result()
            if name: create_folder(parent, name); self.refresh()

    def _on_dbl(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data["kind"] in ("note","board"):
            self.note_opened.emit(data["path"])

    def _ctx_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        kind, path = data.get("kind"), data.get("path")
        menu = QMenu(self)
        if kind == "folder":
            a1 = menu.addAction("📄  New Note Here")
            a2 = menu.addAction("📁  New Subfolder")
            menu.addSeparator()
            a3 = menu.addAction("🗑️  Delete Folder")
            act = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if act == a1: self._new_note_in(path)
            elif act == a2: self._new_folder_in(path)
            elif act == a3: self._del_folder(path)
        elif kind in ("note","board"):
            a1 = menu.addAction("📖  Open")
            menu.addSeparator()
            # Read current tags from disk to show live state
            try: cur_tags = read_note(path).get("tags", [])
            except: cur_tags = []
            is_fav = "favorite" in cur_tags
            a_fav = menu.addAction("☆  Add to Favorites" if not is_fav else "⭐  Remove from Favorites")
            a_tag = menu.addAction("🏷️  Add Tag…")
            if cur_tags:
                rm_menu = menu.addMenu("✕  Remove Tag")
                rm_actions = {}
                for t in cur_tags:
                    rm_actions[rm_menu.addAction(t)] = t
            else:
                rm_menu = None; rm_actions = {}
            menu.addSeparator()
            a_rename = menu.addAction("✏️  Rename…")
            menu.addSeparator()
            a2 = menu.addAction("🗑️  Move to Trash")
            act = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if act == a1: self.note_opened.emit(path)
            elif act == a_fav: self._toggle_favorite(path)
            elif act == a_tag: self._add_tag(path)
            elif act in rm_actions: self._remove_tag(path, rm_actions[act])
            elif act == a_rename: self._rename_note(path, item)
            elif act == a2:
                delete_note(path, self.trash_dir)
                self.refresh(); self.note_deleted.emit(path)

    def _new_note_in(self, folder):
        dlg = NewItemDialog(self, "note")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, tmpl = dlg.get_result()
            if tmpl:
                path = create_note(folder, tmpl, name)
                self.refresh(); self.note_opened.emit(path)

    def _new_folder_in(self, parent):
        dlg = NewItemDialog(self, "folder")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, _ = dlg.get_result()
            if name: create_folder(parent, name); self.refresh()

    def _del_folder(self, path):
        r = QMessageBox.question(self, "Delete Folder", "Move folder and all contents to trash?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            delete_folder(path, self.trash_dir); self.refresh()

    def _toggle_favorite(self, path):
        try:
            data = read_note(path)
            tags = data.get("tags", [])
            if "favorite" in tags: tags.remove("favorite")
            else: tags.append("favorite")
            data["tags"] = tags
            save_note(path, data)
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not update favorite: {e}")

    def _add_tag(self, path):
        dlg = QDialog(self); dlg.setWindowTitle("Add Tag"); dlg.setFixedSize(300, 110)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(10)
        lay.addWidget(QLabel("Tag name:"))
        edit = QLineEdit(); edit.setPlaceholderText("e.g. work, ideas, reference")
        lay.addWidget(edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        lay.addWidget(btns); edit.setFocus()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            tag = edit.text().strip().lower()
            if not tag: return
            try:
                data = read_note(path)
                tags = data.get("tags", [])
                if tag not in tags: tags.append(tag)
                data["tags"] = tags
                save_note(path, data)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add tag: {e}")

    def _remove_tag(self, path, tag):
        try:
            data = read_note(path)
            tags = data.get("tags", [])
            if tag in tags: tags.remove(tag)
            data["tags"] = tags
            save_note(path, data)
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not remove tag: {e}")

    def _rename_note(self, path, item):
        dlg = QDialog(self); dlg.setWindowTitle("Rename Note"); dlg.setFixedSize(300, 110)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(10)
        lay.addWidget(QLabel("New title:"))
        edit = QLineEdit()
        try: edit.setText(read_note(path).get("title", ""))
        except: pass
        lay.addWidget(edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        lay.addWidget(btns); edit.setFocus(); edit.selectAll()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_title = edit.text().strip()
            if not new_title: return
            try:
                data = read_note(path)
                data["title"] = new_title
                save_note(path, data)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename: {e}")

    def _run_search(self):
        q = self.search_edit.text().strip()
        if not q or not self.workspace: self.refresh(); return
        self.tree.clear()
        for r in search_notes(self.workspace, q):
            item = QTreeWidgetItem([f"📄  {r['title']}"])
            item.setData(0, Qt.ItemDataRole.UserRole, {"kind":"note","name":r["title"],"path":r["path"]})
            if r["snippet"]: item.setToolTip(0, f"…{r['snippet']}…")
            self.tree.addTopLevelItem(item)


# ─────────────────────────────────────────────────────────────────
# TEXT EDITOR PANEL
# ─────────────────────────────────────────────────────────────────
class TextEditorPanel(QWidget):
    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._focus = False
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        layout.addWidget(self._fmt_bar())
        layout.addWidget(self._focus_bar())  # FIX BUG 8: always-visible focus bar
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start writing...\n\n# Heading 1\n**bold**  *italic*  `code`\n- list item\n- [ ] todo")
        self.editor.setStyleSheet(f"QTextEdit{{background:{DARK['panel_bg']};border:none;color:{DARK['text_primary']};font-family:'Cascadia Code','Fira Code','Consolas',monospace;font-size:14px;padding:28px 36px;selection-background-color:{DARK['accent_soft']};}}")
        layout.addWidget(self.editor)
        layout.addWidget(self._status_bar())
        self._wt = QTimer(); self._wt.setSingleShot(True); self._wt.timeout.connect(self._wc)
        self.editor.textChanged.connect(lambda: self._wt.start(300))
        self.editor.textChanged.connect(self.content_changed.emit)
        # FIX BUG 8: Escape key exits focus mode
        from PyQt6.QtGui import QKeySequence, QShortcut
        esc = QShortcut(QKeySequence("Escape"), self)
        esc.activated.connect(self._exit_focus)

    def _btn(self, label, tip, cb, width=None):
        b = QPushButton(label); b.setFixedHeight(24)
        if width: b.setFixedWidth(width)
        b.setToolTip(tip or "")
        b.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:4px;padding:2px 7px;color:{DARK['text_muted']};font-size:11px;font-weight:600;}}QPushButton:hover{{background:{DARK['hover']};color:{DARK['text_primary']};}}")
        if cb: b.clicked.connect(cb)
        return b

    def _sep(self):
        s = QFrame(); s.setFixedSize(1,20); s.setStyleSheet(f"background:{DARK['border']};"); return s

    def _fmt_bar(self):
        bar = QWidget(); bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{DARK['toolbar']};border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(10,0,10,0); lay.setSpacing(2)
        for lbl, tip, cb in [
            ("B","Bold",self._bold),("I","Italic",self._italic),("~~","Strikethrough",self._strike),
            ("|",None,None),
            ("H1","Heading 1",lambda:self._head(1)),("H2","Heading 2",lambda:self._head(2)),("H3","Heading 3",lambda:self._head(3)),
            ("|",None,None),
            ("•","Bullet list",self._bullet),("1.","Numbered list",self._numbered),("☑","Todo",self._todo),
            ("|",None,None),
            ("</>","Code block",self._code_block),("`cd`","Inline code",self._inline_code),("---","Divider",self._divider),
        ]:
            if lbl == "|": lay.addWidget(self._sep())
            elif lbl == "`cd`": lay.addWidget(self._btn(lbl, tip, cb, width=36))
            else: lay.addWidget(self._btn(lbl, tip, cb))
        lay.addStretch()
        # FIX BUG 8: focus button is now in a SEPARATE bar so it's never hidden
        self._fmtbar = bar; return bar

    def _focus_bar(self):
        # FIX BUG 8: dedicated always-visible bar that holds only the focus button
        bar = QWidget(); bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{DARK['toolbar']};border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(10,0,10,0)
        lay.addStretch()
        self.focus_btn = self._btn("⛶  Focus","Toggle focus mode (Esc to exit)",self._toggle_focus)
        lay.addWidget(self.focus_btn)
        self._focusbar = bar; return bar

    def _status_bar(self):
        bar = QWidget(); bar.setFixedHeight(26)
        bar.setStyleSheet(f"background:{DARK['toolbar']};border-top:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar); lay.setContentsMargins(12,0,12,0)
        self.wc_lbl = QLabel("0 words  ·  0 chars")
        self.wc_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;")
        self.save_lbl = QLabel("Saved")
        self.save_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;")
        lay.addWidget(self.wc_lbl); lay.addStretch(); lay.addWidget(self.save_lbl)
        self._sbar = bar; return bar

    def _wrap(self, pre, suf=None):
        # Raw markdown fallback (still stored as markdown in file)
        suf = suf or pre; cur = self.editor.textCursor(); sel = cur.selectedText()
        if sel:
            cur.insertText(f"{pre}{sel}{suf}")
        else:
            pos = cur.position()
            cur.insertText(f"{pre}{suf}")
            cur.setPosition(pos + len(pre))
            self.editor.setTextCursor(cur)

    def _prepend(self, pre):
        from PyQt6.QtGui import QTextCursor
        cur = self.editor.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.StartOfLine)
        # FIX BUG 3/4: check if prefix already there to avoid doubling
        cur.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line = cur.selectedText()
        cur.movePosition(QTextCursor.MoveOperation.StartOfLine)
        if not line.startswith(pre):
            cur.insertText(pre)

    # FIX BUG 3: Bold/Italic/Strike wrap selection with markers AND give visual hint
    def _bold(self): self._wrap("**")
    def _italic(self): self._wrap("*")
    def _strike(self): self._wrap("~~")
    def _inline_code(self): self._wrap("`")

    # FIX BUG 4: Bullet uses proper bullet character visually
    def _bullet(self): self._prepend("- ")
    def _numbered(self): self._prepend("1. ")
    def _todo(self): self._prepend("- [ ] ")
    def _head(self, n): self._prepend("#"*n+" ")

    def _divider(self):
        from PyQt6.QtGui import QTextCursor
        cur = self.editor.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.EndOfLine)
        cur.insertText("\n\n---\n\n")
        self.editor.setTextCursor(cur)

    # FIX BUG 5: Code block wraps selection cleanly and places cursor inside
    def _code_block(self):
        cur = self.editor.textCursor()
        sel = cur.selectedText()
        if sel:
            cur.insertText(f"```\n{sel}\n```")
        else:
            pos = cur.position()
            cur.insertText("```\n\n```")
            # Place cursor on the blank line inside the block
            cur.setPosition(pos + 4)
            self.editor.setTextCursor(cur)

    def _toggle_focus(self):
        if self._focus:
            self._exit_focus()
        else:
            self._enter_focus()

    def _enter_focus(self):
        self._focus = True
        self._fmtbar.setVisible(False)
        self._sbar.setVisible(False)
        self.focus_btn.setText("✕  Exit Focus")
        self.focus_btn.setStyleSheet(f"QPushButton{{background:{DARK['accent_soft']};border:1px solid {DARK['accent']};border-radius:4px;padding:2px 10px;color:{DARK['accent']};font-size:11px;font-weight:600;}}QPushButton:hover{{background:{DARK['accent_dim']};color:{DARK['text_primary']};}}")
        self.editor.setStyleSheet(f"QTextEdit{{background:{DARK['bg']};border:none;color:{DARK['text_primary']};font-family:'Cascadia Code','Fira Code','Consolas',monospace;font-size:15px;padding:60px 18%;selection-background-color:{DARK['accent_soft']};}}")
        # Hide sidebar via parent chain
        self._set_sidebar_visible(False)

    def _exit_focus(self):
        self._focus = False
        self._fmtbar.setVisible(True)
        self._sbar.setVisible(True)
        self.focus_btn.setText("⛶  Focus")
        self.focus_btn.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:4px;padding:2px 7px;color:{DARK['text_muted']};font-size:11px;font-weight:600;}}QPushButton:hover{{background:{DARK['hover']};color:{DARK['text_primary']};}}")
        self.editor.setStyleSheet(f"QTextEdit{{background:{DARK['panel_bg']};border:none;color:{DARK['text_primary']};font-family:'Cascadia Code','Fira Code','Consolas',monospace;font-size:14px;padding:28px 36px;selection-background-color:{DARK['accent_soft']};}}")
        self._set_sidebar_visible(True)

    def _set_sidebar_visible(self, visible):
        # Walk up to MainWindow and toggle sidebar
        w = self.parent()
        while w:
            if hasattr(w, 'sidebar'):
                w.sidebar.setVisible(visible); return
            w = w.parent() if hasattr(w, 'parent') else None

    def _wc(self):
        t = self.editor.toPlainText()
        w = len(t.split()) if t.strip() else 0
        self.wc_lbl.setText(f"{w:,} words  ·  {len(t):,} chars")

    def set_content(self, text):
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)
        self._wc()  # update word count once, cleanly, without triggering dirty
    def get_content(self): return self.editor.toPlainText()
    def mark_saved(self): self.save_lbl.setText("Saved"); self.save_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;")
    def mark_unsaved(self): self.save_lbl.setText("● Unsaved"); self.save_lbl.setStyleSheet(f"color:{DARK['warning']};font-size:11px;")


# ─────────────────────────────────────────────────────────────────
# DRAWING PANEL
# ─────────────────────────────────────────────────────────────────
CANVAS_SIZE = 4000  # virtual infinite canvas dimension

class Canvas(QWidget):
    changed = pyqtSignal()
    zoom_changed = pyqtSignal(float)  # emitted so toolbar can update label

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.tool = "pen"; self.color = QColor(DARK["accent"]); self.brush_size = 3
        # transform state
        self._zoom = 1.0
        self._offset = QPointF(0.0, 0.0)  # top-left of canvas in widget coords
        # drawing state
        self._px = None; self._hist = []; self._redo = []
        self._drawing = False; self._panning = False; self._space_held = False
        self._last = QPointF(); self._start = QPointF()
        self._pan_start = QPointF(); self._offset_start = QPointF()
        self._overlay = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ── virtual canvas ─────────────────────────────────────────────
    def _ensure_px(self):
        from PyQt6.QtCore import QSize
        sz = QSize(CANVAS_SIZE, CANVAS_SIZE)
        if self._px is None:
            self._px = QPixmap(sz); self._px.fill(QColor(DARK["panel_bg"]))

    # ── coordinate helpers ─────────────────────────────────────────
    def _to_canvas(self, widget_pt):
        """Map a widget-space QPointF to canvas-space QPointF."""
        return QPointF(
            (widget_pt.x() - self._offset.x()) / self._zoom,
            (widget_pt.y() - self._offset.y()) / self._zoom,
        )

    def _clamp_offset(self):
        """Keep at least 100px of canvas visible on each axis."""
        margin = 100
        max_x =  self.width()  - margin
        max_y =  self.height() - margin
        min_x = -(CANVAS_SIZE * self._zoom) + margin
        min_y = -(CANVAS_SIZE * self._zoom) + margin
        self._offset = QPointF(
            max(min_x, min(max_x, self._offset.x())),
            max(min_y, min(max_y, self._offset.y())),
        )

    # ── paint ───────────────────────────────────────────────────────
    def paintEvent(self, e):
        self._ensure_px()
        from PyQt6.QtGui import QTransform
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        t = QTransform()
        t.translate(self._offset.x(), self._offset.y())
        t.scale(self._zoom, self._zoom)
        p.setTransform(t)
        p.drawPixmap(0, 0, self._px)
        if self._overlay:
            p.drawPixmap(0, 0, self._overlay)
        p.end()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._clamp_offset()

    # ── zoom ────────────────────────────────────────────────────────
    def set_zoom(self, new_zoom, anchor=None):
        """Zoom keeping `anchor` (widget-space QPointF) fixed. Defaults to centre."""
        new_zoom = max(0.1, min(5.0, new_zoom))
        if anchor is None:
            anchor = QPointF(self.width() / 2, self.height() / 2)
        # adjust offset so the anchor point stays fixed
        ratio = new_zoom / self._zoom
        self._offset = QPointF(
            anchor.x() - ratio * (anchor.x() - self._offset.x()),
            anchor.y() - ratio * (anchor.y() - self._offset.y()),
        )
        self._zoom = new_zoom
        self._clamp_offset()
        self.zoom_changed.emit(self._zoom)
        self.update()

    def zoom_in(self):  self.set_zoom(self._zoom * 1.25)
    def zoom_out(self): self.set_zoom(self._zoom / 1.25)
    def zoom_reset(self): self._zoom=1.0; self._offset=QPointF(0,0); self.zoom_changed.emit(1.0); self.update()

    def wheelEvent(self, e):
        delta = e.angleDelta().y()
        if delta == 0: return
        factor = 1.15 if delta > 0 else 1/1.15
        self.set_zoom(self._zoom * factor, e.position())

    # ── pan (middle-mouse or Space+drag) ───────────────────────────
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space and not e.isAutoRepeat():
            self._space_held = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Space and not e.isAutoRepeat():
            self._space_held = False
            if not self._panning:
                self.setCursor(Qt.CursorShape.CrossCursor)

    # ── mouse ───────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.MiddleButton or            (e.button() == Qt.MouseButton.LeftButton and self._space_held):
            self._panning = True
            self._pan_start = e.position()
            self._offset_start = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            self._ensure_px()
            self._drawing = True
            cp = self._to_canvas(e.position())
            self._start = cp; self._last = cp
            self._snapshot()
            if self.tool in ("pen","highlighter","marker","eraser"):
                self._dot(cp)

    def mouseMoveEvent(self, e):
        if self._panning:
            delta = e.position() - self._pan_start
            self._offset = self._offset_start + delta
            self._clamp_offset()
            self.update(); return
        if not self._drawing: return
        cp = self._to_canvas(e.position())
        if self.tool in ("pen","highlighter","marker","eraser"):
            self._line(self._last, cp); self._last = cp
        else:
            self._overlay = QPixmap(CANVAS_SIZE, CANVAS_SIZE)
            self._overlay.fill(Qt.GlobalColor.transparent)
            p = QPainter(self._overlay); self._pen(p, True)
            self._shape(p, self._start, cp); p.end()
        self.update()

    def mouseReleaseEvent(self, e):
        if self._panning and (e.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton)):
            self._panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor if self._space_held else Qt.CursorShape.CrossCursor)
            return
        if not self._drawing: return
        self._drawing = False
        cp = self._to_canvas(e.position())
        if self.tool not in ("pen","highlighter","marker","eraser"):
            self._ensure_px()
            p = QPainter(self._px); self._pen(p); self._shape(p, self._start, cp); p.end()
            self._overlay = None
        self.update(); self.changed.emit()

    # ── draw helpers ────────────────────────────────────────────────
    def _dot(self, pt):
        self._ensure_px()
        p = QPainter(self._px); self._pen(p); p.drawPoint(pt.toPoint()); p.end(); self.update()

    def _line(self, a, b):
        self._ensure_px()
        p = QPainter(self._px); self._pen(p); p.drawLine(a.toPoint(), b.toPoint()); p.end(); self.update()

    def _pen(self, painter, preview=False):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self.color)
        if self.tool == "eraser":
            c = QColor(DARK["panel_bg"])
            painter.setPen(QPen(c, self.brush_size*6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        elif self.tool == "highlighter":
            c.setAlpha(70)
            painter.setPen(QPen(c, self.brush_size*8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        elif self.tool == "marker":
            c.setAlpha(200)
            painter.setPen(QPen(c, self.brush_size*2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
        else:
            if preview: c.setAlpha(160)
            painter.setPen(QPen(c, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

    def _shape(self, p, a, b):
        x1,y1,x2,y2 = int(a.x()),int(a.y()),int(b.x()),int(b.y())
        if self.tool == "line": p.drawLine(x1,y1,x2,y2)
        elif self.tool == "rect": p.setBrush(Qt.BrushStyle.NoBrush); p.drawRect(min(x1,x2),min(y1,y2),abs(x2-x1),abs(y2-y1))
        elif self.tool == "ellipse": p.setBrush(Qt.BrushStyle.NoBrush); p.drawEllipse(min(x1,x2),min(y1,y2),abs(x2-x1),abs(y2-y1))
        elif self.tool == "arrow": self._arrow(p, a, b)

    def _arrow(self, p, a, b):
        import math
        p.drawLine(a.toPoint(), b.toPoint())
        ang = math.atan2(b.y()-a.y(), b.x()-a.x())
        for s in (1,-1):
            ax = b.x()-14*math.cos(ang-s*math.pi/7); ay = b.y()-14*math.sin(ang-s*math.pi/7)
            p.drawLine(b.toPoint(), QPointF(ax,ay).toPoint())

    # ── history ─────────────────────────────────────────────────────
    def _snapshot(self):
        if self._px: self._hist.append(self._px.copy()); self._hist=self._hist[-50:]; self._redo.clear()

    def undo(self):
        if self._hist: self._redo.append(self._px.copy()); self._px=self._hist.pop(); self.update()
    def redo(self):
        if self._redo: self._hist.append(self._px.copy()); self._px=self._redo.pop(); self.update()
    def clear(self):
        self._snapshot(); self._ensure_px(); self._px.fill(QColor(DARK["panel_bg"])); self.update(); self.changed.emit()


class DrawingPanel(QWidget):
    changed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.canvas=Canvas(); self.canvas.changed.connect(self.changed.emit)
        self.canvas.zoom_changed.connect(self._on_zoom_changed)
        layout.addWidget(self._toolbar())
        layout.addWidget(self.canvas)

    def _tbtn(self, icon, tip, cb=None, checkable=False, checked=False, text=False):
        b=QPushButton(icon); b.setFixedSize(28,28) if not text else b.setFixedHeight(26)
        b.setToolTip(tip); b.setCheckable(checkable); b.setChecked(checked)
        b.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:5px;padding:{'4px 10px' if text else '2px'};color:{DARK['text_muted']};font-size:13px;}}QPushButton:hover{{background:{DARK['hover']};color:{DARK['text_primary']};}}QPushButton:checked{{background:{DARK['active']};color:{DARK['accent']};}}")
        if cb: b.clicked.connect(cb)
        return b

    def _toolbar(self):
        bar=QWidget(); bar.setFixedHeight(38)
        bar.setStyleSheet(f"background:{DARK['toolbar']};border-bottom:1px solid {DARK['border']};")
        lay=QHBoxLayout(bar); lay.setContentsMargins(10,0,10,0); lay.setSpacing(4)
        self._tbtns={}
        for icon,tid,tip in [("✒️","pen","Pen"),("🖊️","highlighter","Highlighter"),("🖋️","marker","Marker"),("⬜","rect","Rectangle"),("⭕","ellipse","Ellipse"),("╱","line","Line"),("→","arrow","Arrow"),("⌫","eraser","Eraser")]:
            b=self._tbtn(icon,tip,None,True,tid=="pen"); b.clicked.connect(lambda _,t=tid: self._tool(t))
            lay.addWidget(b); self._tbtns[tid]=b
        sep=QFrame(); sep.setFixedSize(1,20); sep.setStyleSheet(f"background:{DARK['border']};"); lay.addWidget(sep)
        self.cbtn=QPushButton(); self.cbtn.setFixedSize(24,24); self.cbtn.setToolTip("Color")
        self._upd_color(QColor(DARK["accent"])); self.cbtn.clicked.connect(self._color); lay.addWidget(self.cbtn)
        sl=QLabel("Size:"); sl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;"); lay.addWidget(sl)
        self.sld=QSlider(Qt.Orientation.Horizontal); self.sld.setRange(1,20); self.sld.setValue(3); self.sld.setFixedWidth(80)
        self.sld.setStyleSheet(f"QSlider::groove:horizontal{{background:{DARK['border']};height:4px;border-radius:2px;}}QSlider::handle:horizontal{{background:{DARK['accent']};width:12px;height:12px;border-radius:6px;margin:-4px 0;}}")
        self.sld.valueChanged.connect(lambda v: setattr(self.canvas,'brush_size',v)); lay.addWidget(self.sld)
        lay.addStretch()
        # zoom controls
        sep2=QFrame(); sep2.setFixedSize(1,20); sep2.setStyleSheet(f"background:{DARK['border']};"); lay.addWidget(sep2)
        lay.addWidget(self._tbtn("－","Zoom out (scroll wheel)",self.canvas.zoom_out))
        self.zoom_lbl=QLabel("100%"); self.zoom_lbl.setFixedWidth(40)
        self.zoom_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;"); self.zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.zoom_lbl)
        lay.addWidget(self._tbtn("＋","Zoom in (scroll wheel)",self.canvas.zoom_in))
        zr=self._tbtn("1:1","Reset zoom",self.canvas.zoom_reset,text=True); lay.addWidget(zr)
        sep3=QFrame(); sep3.setFixedSize(1,20); sep3.setStyleSheet(f"background:{DARK['border']};"); lay.addWidget(sep3)
        for icon,tip,cb in [("↩","Undo",self.canvas.undo),("↪","Redo",self.canvas.redo),("🗑","Clear",self.canvas.clear)]:
            lay.addWidget(self._tbtn(icon,tip,cb))
        eb=self._tbtn("⬇ Export","Export as PNG",self._export,text=True); lay.addWidget(eb)
        return bar

    def _on_zoom_changed(self, z):
        self.zoom_lbl.setText(f"{int(z*100)}%")

    def _tool(self, t):
        self.canvas.tool=t
        for tid,b in self._tbtns.items(): b.setChecked(tid==t)

    def _color(self):
        from PyQt6.QtWidgets import QColorDialog
        c=QColorDialog.getColor(self.canvas.color,self,"Color")
        if c.isValid(): self.canvas.color=c; self._upd_color(c)

    def _upd_color(self, c):
        self.cbtn.setStyleSheet(f"QPushButton{{background:{c.name()};border:2px solid {DARK['border']};border-radius:4px;}}QPushButton:hover{{border-color:{DARK['accent']};}}")

    def _export(self):
        path,_=QFileDialog.getSaveFileName(self,"Export","","PNG Image (*.png)")
        if path and self.canvas._px: self.canvas._px.save(path,"PNG")


# ─────────────────────────────────────────────────────────────────
# NOTE EDITOR AREA
# ─────────────────────────────────────────────────────────────────
class NoteEditorArea(QWidget):
    title_changed = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._path=None; self._data=None; self._dirty=False
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        layout.addWidget(self._title_bar())
        layout.addWidget(self._tab_bar())
        self.stack=QStackedWidget()
        self.text_panel=TextEditorPanel(); self.draw_panel=DrawingPanel()
        self.stack.addWidget(self.text_panel); self.stack.addWidget(self.draw_panel)
        layout.addWidget(self.stack)
        self.text_panel.content_changed.connect(self._dirty_flag)
        self.draw_panel.changed.connect(self._dirty_flag)
        self._at=QTimer(); self._at.setInterval(4000); self._at.timeout.connect(self._autosave); self._at.start()

    def _title_bar(self):
        bar=QWidget(); bar.setFixedHeight(54)
        bar.setStyleSheet(f"background:{DARK['panel_bg']};border-bottom:1px solid {DARK['border']};")
        lay=QHBoxLayout(bar); lay.setContentsMargins(24,0,16,0)
        self.title_edit=QLineEdit("Untitled")
        self.title_edit.setStyleSheet(f"QLineEdit{{background:transparent;border:none;color:{DARK['text_primary']};font-size:18px;font-weight:700;padding:0;}}QLineEdit:focus{{color:{DARK['accent']};}}")
        self.title_edit.textChanged.connect(lambda t: (self._dirty_flag(), self.title_changed.emit(t)))
        lay.addWidget(self.title_edit); lay.addStretch()
        self.meta_lbl=QLabel("Auto-saved")
        self.meta_lbl.setStyleSheet(f"color:{DARK['text_muted']};font-size:11px;")
        lay.addWidget(self.meta_lbl); return bar

    def _tab_bar(self):
        bar=QWidget(); bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{DARK['tab_bg']};border-bottom:1px solid {DARK['border']};")
        lay=QHBoxLayout(bar); lay.setContentsMargins(8,0,8,0); lay.setSpacing(0)
        self._tabs=[]
        for lbl,idx in [("✍️  Write",0),("🎨  Draw",1)]:
            b=QPushButton(lbl); b.setCheckable(True); b.setChecked(idx==0); b.setFixedHeight(36)
            b.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-bottom:2px solid transparent;padding:0 20px;color:{DARK['text_muted']};font-size:12px;height:36px;}}QPushButton:checked{{border-bottom:2px solid {DARK['accent']};color:{DARK['text_primary']};background:{DARK['tab_active']};}}QPushButton:hover{{color:{DARK['text_primary']};background:{DARK['hover']};}}")
            b.clicked.connect(lambda _,i=idx: self._tab(i)); lay.addWidget(b); self._tabs.append(b)
        lay.addStretch(); return bar

    def open_note(self, path):
        self._path=path
        try: self._data=read_note(path)
        except: self._data={"type":"note","title":"Untitled","tags":[],"blocks":[{"type":"text","value":""}]}
        self.title_edit.blockSignals(True)
        self.title_edit.setText(self._data.get("title","Untitled"))
        self.title_edit.blockSignals(False)
        texts=[b["value"] for b in self._data.get("blocks",[]) if b.get("type")=="text"]
        self.text_panel.set_content("\n\n".join(texts))
        self.text_panel.mark_saved()
        mod=self._data.get("modified","")
        try:
            dt=datetime.fromisoformat(mod)
            self.meta_lbl.setText(f"Saved {dt.strftime('%b %d, %H:%M')}")
        except: self.meta_lbl.setText("Saved")
        self._dirty=False
        # FIX BUG 1: use QTimer.singleShot to delay tab switch until widget is fully shown
        # This gives the canvas time to get a valid size before it paints
        target_tab = 1 if self._data.get("type")=="board" else 0
        QTimer.singleShot(0, lambda: self._tab(target_tab))

    def save_now(self):
        if not self._path or not self._data: return
        self._data["title"]=self.title_edit.text().strip() or "Untitled"
        non_text=[b for b in self._data.get("blocks",[]) if b.get("type")!="text"]
        self._data["blocks"]=[{"type":"text","value":self.text_panel.get_content()}]+non_text
        try:
            save_note(self._path,self._data)
            self.text_panel.mark_saved()
            self.meta_lbl.setText(f"Saved {datetime.now().strftime('%H:%M:%S')}")
            self._dirty=False
        except Exception as e: self.meta_lbl.setText(f"Error: {e}")

    def _dirty_flag(self): self._dirty=True; self.text_panel.mark_unsaved(); self.meta_lbl.setText("Unsaved")
    def _autosave(self):
        if self._dirty and self._path: self.save_now()
    def _tab(self, idx):
        self.stack.setCurrentIndex(idx)
        for i,b in enumerate(self._tabs): b.setChecked(i==idx)


# ─────────────────────────────────────────────────────────────────
# WELCOME PANEL
# ─────────────────────────────────────────────────────────────────
class WelcomePanel(QWidget):
    new_note = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{DARK['panel_bg']};")
        lay=QVBoxLayout(self); lay.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.setSpacing(0)
        g=QLabel("✦"); g.setStyleSheet(f"color:{DARK['accent']};font-size:52px;background:transparent;"); g.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t=QLabel("Gensoubook"); t.setStyleSheet(f"color:{DARK['text_primary']};font-size:24px;font-weight:700;background:transparent;"); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s=QLabel("Your personal spellbook.\nSelect a note or create a new one to begin."); s.setStyleSheet(f"color:{DARK['text_muted']};font-size:13px;background:transparent;"); s.setAlignment(Qt.AlignmentFlag.AlignCenter); s.setWordWrap(True)
        nb=QPushButton("  ＋  New Note"); nb.setFixedSize(160,40)
        nb.setStyleSheet(f"QPushButton{{background:{DARK['accent_soft']};border:1px solid {DARK['accent']};border-radius:8px;color:{DARK['accent']};font-size:13px;font-weight:600;}}QPushButton:hover{{background:{DARK['accent_dim']};color:{DARK['text_primary']};}}")
        nb.clicked.connect(self.new_note.emit)
        for w in [g,t]: lay.addWidget(w); lay.addSpacing(8 if w==g else 20)
        lay.addWidget(s); lay.addSpacing(20); lay.addWidget(nb,alignment=Qt.AlignmentFlag.AlignCenter)


# ─────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gensoubook")
        self.setMinimumSize(960,620); self.resize(1280,800)
        self.setStyleSheet(STYLESHEET)
        self._workspace=""; self._open_path=None
        self._build()
        self._check_workspace()

    def _build(self):
        c=QWidget(); self.setCentralWidget(c)
        root=QHBoxLayout(c); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.splitter=QSplitter(Qt.Orientation.Horizontal); self.splitter.setHandleWidth(1)
        self.sidebar=Sidebar(self)
        self.sidebar.note_opened.connect(self._open)
        self.sidebar.note_deleted.connect(self._on_del)
        self.splitter.addWidget(self.sidebar)
        self.rstack=QStackedWidget()
        self.welcome=WelcomePanel(); self.note_area=NoteEditorArea()
        self.rstack.addWidget(self.welcome); self.rstack.addWidget(self.note_area)
        self.splitter.addWidget(self.rstack)
        self.splitter.setStretchFactor(0,0); self.splitter.setStretchFactor(1,1)
        self.splitter.setSizes([230,1050]); root.addWidget(self.splitter)
        self.sb=QStatusBar()
        self.sb.setStyleSheet(f"background:{DARK['toolbar']};border-top:1px solid {DARK['border']};color:{DARK['text_muted']};font-size:11px;")
        self.setStatusBar(self.sb); self.sb.showMessage("✦  Gensoubook  ·  Ready")
        self.welcome.new_note.connect(self.sidebar._new_note)
        self.note_area.title_changed.connect(lambda t: self.setWindowTitle(f"{t}  —  Gensoubook"))

    def _check_workspace(self):
        ws=get_workspace()
        if ws and Path(ws).exists(): self._load(ws)
        else: self._setup()

    def _setup(self):
        dlg=WorkspaceSetupDialog(self)
        if dlg.exec():
            path=dlg.get_path()
            if path: init_workspace(path); self._load(path)
        else: sys.exit(0)

    def _load(self, path):
        self._workspace=path; self.sidebar.load_workspace(path)
        self.sb.showMessage(f"✦  Gensoubook  ·  {path}")

    def _open(self, path):
        self._open_path=path; self.note_area.open_note(path)
        self.rstack.setCurrentIndex(1); self.sb.showMessage(f"Editing: {Path(path).name}")

    def _on_del(self, path):
        if self._open_path==path:
            self.rstack.setCurrentIndex(0); self.setWindowTitle("Gensoubook"); self._open_path=None

    def closeEvent(self, e):
        if self.note_area._dirty and self.note_area._path: self.note_area.save_now()
        e.accept()


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app=QApplication(sys.argv)
    app.setApplicationName("Gensoubook")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    w=MainWindow(); w.show()
    sys.exit(app.exec())
