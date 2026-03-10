"""
Gensoubook — Workspace Setup Dialog
Shown on first launch to let the user choose their notes folder.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.theme import DARK
import os


class WorkspaceSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Gensoubook")
        self.setFixedSize(500, 320)
        self.setModal(True)
        self.selected_path = ""
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QDialog {{
                background:{DARK['panel_bg']};
                border:1px solid {DARK['border']};
                border-radius:12px;
            }}
            QLabel {{ color:{DARK['text_primary']}; border:none; background:transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(0)

        # Header
        icon = QLabel("✦")
        icon.setStyleSheet(f"color:{DARK['accent']}; font-size:36px; background:transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Gensoubook")
        title.setStyleSheet(f"color:{DARK['text_primary']}; font-size:20px; font-weight:700; background:transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Choose a folder where your notes will be saved.\nThis will be your personal spellbook — only on your device.")
        sub.setStyleSheet(f"color:{DARK['text_muted']}; font-size:12px; line-height:1.6; background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        layout.addWidget(icon)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(sub)
        layout.addSpacing(24)

        # Path picker
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select a folder...")
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet(f"""
            QLineEdit {{
                background:{DARK['hover']}; border:1px solid {DARK['border']};
                border-radius:6px; color:{DARK['text_primary']};
                padding:7px 12px; font-size:12px;
            }}
        """)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(34)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background:{DARK['hover']}; border:1px solid {DARK['border']};
                border-radius:6px; color:{DARK['text_primary']};
                padding:4px 16px; font-size:12px;
            }}
            QPushButton:hover {{ border-color:{DARK['accent']}; }}
        """)
        browse_btn.clicked.connect(self._browse)

        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)
        layout.addSpacing(8)

        # Suggest default
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "Gensoubook")
        suggest_btn = QPushButton(f"Use default: ~/Documents/Gensoubook")
        suggest_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:none;
                color:{DARK['accent']}; font-size:11px;
                text-align:left; padding:0;
            }}
            QPushButton:hover {{ color:{DARK['text_primary']}; }}
        """)
        suggest_btn.clicked.connect(lambda: self._set_path(default_path))
        layout.addWidget(suggest_btn)

        layout.addStretch()

        # Confirm button
        self.confirm_btn = QPushButton("Open Spellbook  →")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setObjectName("accent_btn")
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background:{DARK['accent_soft']}; border:1px solid {DARK['accent']};
                border-radius:8px; color:{DARK['accent']};
                font-size:14px; font-weight:600; padding:4px 20px;
            }}
            QPushButton:hover {{ background:{DARK['accent_dim']}; color:{DARK['text_primary']}; }}
            QPushButton:disabled {{
                background:{DARK['hover']}; border-color:{DARK['border']};
                color:{DARK['text_muted']};
            }}
        """)
        self.confirm_btn.clicked.connect(self.accept)
        layout.addWidget(self.confirm_btn)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Notes Folder")
        if path:
            self._set_path(path)

    def _set_path(self, path: str):
        self.selected_path = path
        self.path_edit.setText(path)
        self.confirm_btn.setEnabled(True)

    def get_path(self) -> str:
        return self.selected_path
