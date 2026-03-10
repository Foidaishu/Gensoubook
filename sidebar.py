"""
Gensoubook — Sidebar
Real file tree, context menus, new note/folder buttons.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QMenu, QDialog, QComboBox,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction

from core.theme import DARK
from core import filesystem as fs


# ─────────────────────────────────────────────
#  New item dialog
# ─────────────────────────────────────────────
class NewItemDialog(QDialog):
    def __init__(self, parent=None, mode="note"):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("New Folder" if mode == "folder" else "New Note")
        self.setFixedSize(360, mode == "note" and 200 or 140)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Folder name" if self.mode == "folder" else "Note title"
        )
        layout.addRow("Name:", self.name_edit)

        if self.mode == "note":
            self.template_combo = QComboBox()
            for key, (label, _) in fs.TEMPLATES.items():
                self.template_combo.addItem(label, key)
            layout.addRow("Template:", self.template_combo)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)
        self.name_edit.setFocus()

    def get_result(self):
        name = self.name_edit.text().strip()
        if self.mode == "folder":
            return name, None
        template = self.template_combo.currentData()
        return name, template


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
class Sidebar(QWidget):
    # Signals
    note_opened   = pyqtSignal(str)   # path
    note_deleted  = pyqtSignal(str)   # path
    workspace_changed = pyqtSignal(str)

    def __init__(self, workspace: str = "", parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.trash_dir = ""
        self.setMinimumWidth(190)
        self.setMaximumWidth(320)
        self._build_ui()
        if workspace:
            self.load_workspace(workspace)

    # ── Build UI ────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background:{DARK['sidebar_bg']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_top_bar())
        layout.addWidget(self._build_search_bar())
        layout.addWidget(self._build_tree())
        layout.addWidget(self._build_bottom_nav())

    def _build_top_bar(self):
        bar = QWidget()
        bar.setFixedHeight(50)
        bar.setStyleSheet(f"background:{DARK['sidebar_bg']}; border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 8, 0)

        icon = QLabel("✦")
        icon.setStyleSheet(f"color:{DARK['accent']}; font-size:16px;")
        title = QLabel("Gensoubook")
        title.setStyleSheet(f"color:{DARK['text_primary']}; font-weight:700; font-size:14px;")

        lay.addWidget(icon)
        lay.addSpacing(6)
        lay.addWidget(title)
        lay.addStretch()

        # New note btn
        self.new_note_btn = QPushButton("＋")
        self.new_note_btn.setFixedSize(28, 28)
        self.new_note_btn.setToolTip("New note")
        self.new_note_btn.setStyleSheet(self._icon_btn_style())
        self.new_note_btn.clicked.connect(self._on_new_note)

        # New folder btn
        self.new_folder_btn = QPushButton("📁")
        self.new_folder_btn.setFixedSize(28, 28)
        self.new_folder_btn.setToolTip("New folder")
        self.new_folder_btn.setStyleSheet(self._icon_btn_style())
        self.new_folder_btn.clicked.connect(self._on_new_folder)

        lay.addWidget(self.new_folder_btn)
        lay.addWidget(self.new_note_btn)
        return bar

    def _build_search_bar(self):
        container = QWidget()
        container.setStyleSheet(f"background:{DARK['sidebar_bg']};")
        lay = QHBoxLayout(container)
        lay.setContentsMargins(10, 6, 10, 6)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Search notes...")
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background:{DARK['hover']}; border:1px solid {DARK['border']};
                border-radius:6px; color:{DARK['text_primary']};
                padding:5px 10px; font-size:12px;
            }}
            QLineEdit:focus {{ border-color:{DARK['accent']}; }}
        """)

        # Debounce timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._run_search)
        self.search_edit.textChanged.connect(lambda: self._search_timer.start(300))

        lay.addWidget(self.search_edit)
        return container

    def _build_tree(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(14)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemDoubleClicked.connect(self._on_item_double_click)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background:{DARK['sidebar_bg']}; border:none; outline:none;
                padding:4px 2px; color:{DARK['text_primary']}; font-size:13px;
            }}
            QTreeWidget::item {{ padding:5px 6px; border-radius:6px; margin:1px 4px; }}
            QTreeWidget::item:hover {{ background:{DARK['hover']}; }}
            QTreeWidget::item:selected {{ background:{DARK['active']}; color:{DARK['accent']}; }}
        """)
        return self.tree

    def _build_bottom_nav(self):
        nav = QWidget()
        nav.setFixedHeight(46)
        nav.setStyleSheet(f"background:{DARK['sidebar_bg']}; border-top:1px solid {DARK['border']};")
        lay = QHBoxLayout(nav)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(2)

        nav_items = [
            ("⭐", "Favorites"),
            ("🏷️", "Tags"),
            ("🗑️", "Trash"),
            ("⚙️", "Settings"),
        ]
        for icon, tip in nav_items:
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setToolTip(tip)
            btn.setStyleSheet(self._icon_btn_style(16))
            lay.addWidget(btn)

        lay.addStretch()
        return nav

    # ── Workspace loading ────────────────────────
    def load_workspace(self, path: str):
        self.workspace = path
        self.trash_dir = str(fs.Path(path).parent / ".gensoubook_trash")
        self.refresh()

    def refresh(self):
        self.tree.clear()
        if not self.workspace:
            return
        items = fs.list_workspace(self.workspace)
        for item in items:
            self.tree.addTopLevelItem(self._make_tree_item(item))
        self.tree.expandAll()

    def _make_tree_item(self, data: dict) -> QTreeWidgetItem:
        kind = data["kind"]
        icon = fs.NOTE_ICONS.get(kind, "📄")
        name = data["name"]
        item = QTreeWidgetItem([f"{icon}  {name}"])
        item.setData(0, Qt.ItemDataRole.UserRole, data)

        if kind == "folder":
            for child in data.get("children", []):
                item.addChild(self._make_tree_item(child))

        # Muted color for board
        if kind == "board":
            item.setForeground(0, __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(DARK["accent"]))

        return item

    # ── Actions ──────────────────────────────────
    def _on_new_note(self):
        folder = self._selected_folder() or self.workspace
        if not folder:
            return
        dlg = NewItemDialog(self, mode="note")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, template = dlg.get_result()
            if template:
                path = fs.create_note(folder, template, name)
                self.refresh()
                self.note_opened.emit(path)

    def _on_new_folder(self):
        parent = self._selected_folder() or self.workspace
        if not parent:
            return
        dlg = NewItemDialog(self, mode="folder")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, _ = dlg.get_result()
            if name:
                fs.create_folder(parent, name)
                self.refresh()

    def _on_item_double_click(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data["kind"] in ("note", "board"):
            self.note_opened.emit(data["path"])

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        kind = data.get("kind")
        path = data.get("path")

        menu = QMenu(self)

        if kind == "folder":
            a_new_note = menu.addAction("📄  New Note Here")
            a_new_folder = menu.addAction("📁  New Subfolder")
            menu.addSeparator()
            a_rename = menu.addAction("✏️  Rename")
            a_delete = menu.addAction("🗑️  Delete Folder")

            action = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if action == a_new_note:
                dlg = NewItemDialog(self, mode="note")
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    name, template = dlg.get_result()
                    if template:
                        p = fs.create_note(path, template, name)
                        self.refresh()
                        self.note_opened.emit(p)
            elif action == a_new_folder:
                dlg = NewItemDialog(self, mode="folder")
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    name, _ = dlg.get_result()
                    if name:
                        fs.create_folder(path, name)
                        self.refresh()
            elif action == a_rename:
                self._inline_rename(item, kind="folder", path=path)
            elif action == a_delete:
                self._confirm_delete_folder(path)

        elif kind in ("note", "board"):
            a_open   = menu.addAction("📖  Open")
            a_rename = menu.addAction("✏️  Rename")
            menu.addSeparator()
            a_delete = menu.addAction("🗑️  Move to Trash")

            action = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if action == a_open:
                self.note_opened.emit(path)
            elif action == a_rename:
                self._inline_rename(item, kind="note", path=path)
            elif action == a_delete:
                fs.delete_note(path, self.trash_dir)
                self.refresh()
                self.note_deleted.emit(path)

    def _inline_rename(self, item, kind, path):
        self.tree.editItem(item, 0)

    def _confirm_delete_folder(self, path):
        reply = QMessageBox.question(
            self, "Delete Folder",
            "Move this folder and all its contents to trash?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            fs.delete_folder(path, self.trash_dir)
            self.refresh()

    # ── Search ───────────────────────────────────
    def _run_search(self):
        query = self.search_edit.text().strip()
        if not query or not self.workspace:
            self.refresh()
            return
        results = fs.search_notes(self.workspace, query)
        self.tree.clear()
        for r in results:
            item = QTreeWidgetItem([f"📄  {r['title']}"])
            item.setData(0, Qt.ItemDataRole.UserRole, {
                "kind": "note", "name": r["title"], "path": r["path"]
            })
            if r["snippet"]:
                item.setToolTip(0, f"…{r['snippet']}…")
            self.tree.addTopLevelItem(item)

    # ── Helpers ──────────────────────────────────
    def _selected_folder(self) -> str | None:
        item = self.tree.currentItem()
        if not item:
            return None
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data["kind"] == "folder":
            return data["path"]
        # If a note is selected, return its parent folder
        if data and data["kind"] in ("note", "board"):
            return str(fs.Path(data["path"]).parent)
        return None

    def _icon_btn_style(self, size=14):
        return f"""
            QPushButton {{
                background:transparent; border:none; border-radius:6px;
                font-size:{size}px; padding:2px;
                color:{DARK['text_muted']};
            }}
            QPushButton:hover {{
                background:{DARK['hover']}; color:{DARK['text_primary']};
            }}
        """
