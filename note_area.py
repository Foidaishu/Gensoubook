"""
Gensoubook — Note Editor Area
Combines title bar, Write/Draw tabs, autosave, and file I/O.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from core.theme import DARK
from core import filesystem as fs
from ui.editor import TextEditorPanel
from ui.drawing import DrawingPanel


class NoteEditorArea(QWidget):
    title_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path     = None
        self._data     = None
        self._dirty    = False
        self._build_ui()
        self._setup_autosave()

    # ── Build UI ────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_title_bar())
        layout.addWidget(self._build_tab_bar())

        self.stack = QStackedWidget()
        self.text_panel = TextEditorPanel()
        self.draw_panel = DrawingPanel()
        self.stack.addWidget(self.text_panel)   # 0
        self.stack.addWidget(self.draw_panel)   # 1
        layout.addWidget(self.stack)

        # Connect change signals
        self.text_panel.content_changed.connect(self._on_changed)
        self.draw_panel.changed.connect(self._on_changed)

    def _build_title_bar(self):
        bar = QWidget()
        bar.setFixedHeight(54)
        bar.setStyleSheet(f"background:{DARK['panel_bg']}; border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(24, 0, 16, 0)

        self.title_edit = QLineEdit("Untitled")
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                background:transparent; border:none;
                color:{DARK['text_primary']}; font-size:18px; font-weight:700;
                padding:0;
            }}
            QLineEdit:focus {{ color:{DARK['accent']}; }}
        """)
        self.title_edit.textChanged.connect(self._on_title_changed)
        lay.addWidget(self.title_edit)
        lay.addStretch()

        self.meta_label = QLabel("Auto-saved")
        self.meta_label.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px;")
        lay.addWidget(self.meta_label)

        # Export button
        exp_btn = QPushButton("⬇ Export")
        exp_btn.setFixedHeight(28)
        exp_btn.setStyleSheet(f"""
            QPushButton {{
                background:{DARK['hover']}; border:1px solid {DARK['border']};
                border-radius:5px; padding:2px 12px;
                color:{DARK['text_muted']}; font-size:11px;
            }}
            QPushButton:hover {{ border-color:{DARK['accent']}; color:{DARK['text_primary']}; }}
        """)
        lay.addWidget(exp_btn)
        return bar

    def _build_tab_bar(self):
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{DARK['tab_bg']}; border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(0)

        self._tab_btns = []
        tabs = [("✍️  Write", 0), ("🎨  Draw", 1)]
        for label, idx in tabs:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(idx == 0)
            btn.setFixedHeight(36)
            btn.setStyleSheet(self._tab_btn_style())
            btn.clicked.connect(lambda _, i=idx: self._switch_tab(i))
            lay.addWidget(btn)
            self._tab_btns.append(btn)

        lay.addStretch()
        return bar

    # ── Public API ───────────────────────────────
    def open_note(self, path: str):
        """Load a note/board from disk."""
        self._path = path
        try:
            self._data = fs.read_note(path)
        except Exception:
            self._data = {"type": "note", "title": "Untitled", "tags": [], "blocks": [{"type": "text", "value": ""}]}

        title = self._data.get("title", "Untitled")
        self.title_edit.setText(title)
        self.title_changed.emit(title)

        # Load text content
        text_blocks = [b["value"] for b in self._data.get("blocks", []) if b.get("type") == "text"]
        self.text_panel.set_content("\n\n".join(text_blocks))
        self.text_panel.mark_saved()

        # Modified time
        modified = self._data.get("modified", "")
        if modified:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(modified)
                self.meta_label.setText(f"Saved {dt.strftime('%b %d, %H:%M')}")
            except Exception:
                self.meta_label.setText("Saved")

        self._dirty = False

        # Switch to appropriate tab
        if self._data.get("type") == "board":
            self._switch_tab(1)
        else:
            self._switch_tab(0)

    def save_now(self):
        if not self._path or not self._data:
            return
        # Update text block
        content = self.text_panel.get_content()
        self._data["title"] = self.title_edit.text().strip() or "Untitled"

        # Preserve non-text blocks, replace text blocks
        non_text = [b for b in self._data.get("blocks", []) if b.get("type") != "text"]
        self._data["blocks"] = [{"type": "text", "value": content}] + non_text

        try:
            fs.save_note(self._path, self._data)
            self.text_panel.mark_saved()
            from datetime import datetime
            self.meta_label.setText(f"Saved {datetime.now().strftime('%H:%M:%S')}")
            self._dirty = False
        except Exception as e:
            self.meta_label.setText(f"Save failed: {e}")

    # ── Internals ────────────────────────────────
    def _on_changed(self):
        self._dirty = True
        self.text_panel.mark_unsaved()
        self.meta_label.setText("Unsaved changes")

    def _on_title_changed(self, text: str):
        self._dirty = True
        self.title_changed.emit(text)

    def _switch_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_btns):
            btn.setChecked(i == idx)

    def _setup_autosave(self):
        self._autosave_timer = QTimer()
        self._autosave_timer.setInterval(4000)   # every 4 seconds
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    def _autosave(self):
        if self._dirty and self._path:
            self.save_now()

    def _tab_btn_style(self):
        return f"""
            QPushButton {{
                background:transparent; border:none;
                border-bottom:2px solid transparent;
                padding:0 20px; color:{DARK['text_muted']}; font-size:12px;
                height:36px;
            }}
            QPushButton:checked {{
                border-bottom:2px solid {DARK['accent']};
                color:{DARK['text_primary']};
                background:{DARK['tab_active']};
            }}
            QPushButton:hover {{ color:{DARK['text_primary']}; background:{DARK['hover']}; }}
        """
