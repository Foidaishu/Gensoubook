"""
Gensoubook — Text Editor Panel
Markdown-aware editor with formatting toolbar, word count, focus mode.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QKeySequence

from core.theme import DARK


class TextEditorPanel(QWidget):
    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._focus_mode = False
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.fmt_bar = self._build_fmt_bar()
        layout.addWidget(self.fmt_bar)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Start writing...\n\n"
            "# Heading 1\n## Heading 2\n**bold**  *italic*  `code`\n"
            "- list item\n- [ ] todo item"
        )
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background:{DARK['panel_bg']}; border:none;
                color:{DARK['text_primary']};
                font-family:'Cascadia Code','Fira Code','Consolas',monospace;
                font-size:14px; padding:28px 36px;
                selection-background-color:{DARK['accent_soft']};
            }}
        """)
        layout.addWidget(self.editor)

        self.status_bar = self._build_status_bar()
        layout.addWidget(self.status_bar)

    def _build_fmt_bar(self):
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background:{DARK['toolbar']}; border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(2)

        fmt_actions = [
            ("B",    "Bold",          self._fmt_bold),
            ("I",    "Italic",        self._fmt_italic),
            ("~~",   "Strikethrough", self._fmt_strike),
            ("|",    None,            None),               # separator
            ("H1",   "Heading 1",     lambda: self._fmt_heading(1)),
            ("H2",   "Heading 2",     lambda: self._fmt_heading(2)),
            ("H3",   "Heading 3",     lambda: self._fmt_heading(3)),
            ("|",    None,            None),
            ("• ",   "Bullet list",   self._fmt_bullet),
            ("1. ",  "Numbered list", self._fmt_numbered),
            ("☑",   "Todo item",     self._fmt_todo),
            ("|",    None,            None),
            ("</>",  "Code block",    self._fmt_code_block),
            ("`",    "Inline code",   self._fmt_inline_code),
            ("---",  "Divider",       self._fmt_divider),
        ]

        self._fmt_buttons = []
        for label, tip, callback in fmt_actions:
            if label == "|":
                sep = QFrame()
                sep.setFixedSize(1, 20)
                sep.setStyleSheet(f"background:{DARK['border']};")
                lay.addWidget(sep)
            else:
                btn = QPushButton(label)
                btn.setFixedHeight(24)
                btn.setToolTip(tip or "")
                btn.setStyleSheet(self._fmt_btn_style())
                if callback:
                    btn.clicked.connect(callback)
                lay.addWidget(btn)
                self._fmt_buttons.append(btn)

        lay.addStretch()

        # Focus mode toggle
        self.focus_btn = QPushButton("⛶  Focus")
        self.focus_btn.setFixedHeight(24)
        self.focus_btn.setToolTip("Toggle focus mode")
        self.focus_btn.setStyleSheet(self._fmt_btn_style())
        self.focus_btn.clicked.connect(self._toggle_focus)
        lay.addWidget(self.focus_btn)

        return bar

    def _build_status_bar(self):
        bar = QWidget()
        bar.setFixedHeight(26)
        bar.setStyleSheet(f"background:{DARK['toolbar']}; border-top:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 12, 0)

        self.wc_label = QLabel("0 words  ·  0 chars")
        self.wc_label.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px;")

        self.save_label = QLabel("Saved")
        self.save_label.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px;")

        lay.addWidget(self.wc_label)
        lay.addStretch()
        lay.addWidget(self.save_label)
        return bar

    def _connect_signals(self):
        self._wc_timer = QTimer()
        self._wc_timer.setSingleShot(True)
        self._wc_timer.timeout.connect(self._update_word_count)
        self.editor.textChanged.connect(lambda: self._wc_timer.start(300))
        self.editor.textChanged.connect(self.content_changed.emit)

    # ── Public API ───────────────────────────────
    def set_content(self, text: str):
        self.editor.setPlainText(text)

    def get_content(self) -> str:
        return self.editor.toPlainText()

    def mark_saved(self):
        self.save_label.setText("Saved")
        self.save_label.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px;")

    def mark_unsaved(self):
        self.save_label.setText("● Unsaved")
        self.save_label.setStyleSheet(f"color:{DARK['warning']}; font-size:11px;")

    # ── Formatting helpers ───────────────────────
    def _wrap_selection(self, prefix: str, suffix: str = ""):
        cursor = self.editor.textCursor()
        suffix = suffix or prefix
        selected = cursor.selectedText()
        if selected:
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.editor.setTextCursor(cursor)

    def _prepend_line(self, prefix: str):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText(prefix)

    def _fmt_bold(self):        self._wrap_selection("**")
    def _fmt_italic(self):      self._wrap_selection("*")
    def _fmt_strike(self):      self._wrap_selection("~~")
    def _fmt_inline_code(self): self._wrap_selection("`")
    def _fmt_bullet(self):      self._prepend_line("- ")
    def _fmt_numbered(self):    self._prepend_line("1. ")
    def _fmt_todo(self):        self._prepend_line("- [ ] ")
    def _fmt_divider(self):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        cursor.insertText("\n\n---\n\n")
        self.editor.setTextCursor(cursor)

    def _fmt_heading(self, level: int):
        self._prepend_line("#" * level + " ")

    def _fmt_code_block(self):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        cursor.insertText(f"```\n{selected or ''}\n```")

    def _toggle_focus(self):
        self._focus_mode = not self._focus_mode
        self.fmt_bar.setVisible(not self._focus_mode)
        self.status_bar.setVisible(not self._focus_mode)
        self.focus_btn.setText("✕ Exit Focus" if self._focus_mode else "⛶  Focus")
        if self._focus_mode:
            self.editor.setStyleSheet(f"""
                QTextEdit {{
                    background:{DARK['bg']}; border:none;
                    color:{DARK['text_primary']};
                    font-family:'Cascadia Code','Fira Code','Consolas',monospace;
                    font-size:15px; padding:60px 20%;
                    selection-background-color:{DARK['accent_soft']};
                }}
            """)
        else:
            self.editor.setStyleSheet(f"""
                QTextEdit {{
                    background:{DARK['panel_bg']}; border:none;
                    color:{DARK['text_primary']};
                    font-family:'Cascadia Code','Fira Code','Consolas',monospace;
                    font-size:14px; padding:28px 36px;
                    selection-background-color:{DARK['accent_soft']};
                }}
            """)

    def _update_word_count(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.wc_label.setText(f"{words:,} words  ·  {chars:,} chars")

    def _fmt_btn_style(self):
        return f"""
            QPushButton {{
                background:transparent; border:none; border-radius:4px;
                padding:2px 7px; color:{DARK['text_muted']}; font-size:11px; font-weight:600;
            }}
            QPushButton:hover {{
                background:{DARK['hover']}; color:{DARK['text_primary']};
            }}
            QPushButton:pressed {{ background:{DARK['active']}; }}
        """
