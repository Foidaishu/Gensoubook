"""
Gensoubook — Welcome / Empty State Panel
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from core.theme import DARK


class WelcomePanel(QWidget):
    new_note_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{DARK['panel_bg']};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        glyph = QLabel("✦")
        glyph.setStyleSheet(f"color:{DARK['accent']}; font-size:52px; background:transparent;")
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Gensoubook")
        title.setStyleSheet(f"color:{DARK['text_primary']}; font-size:24px; font-weight:700; background:transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Your personal spellbook.\nSelect a note or create a new one.")
        sub.setStyleSheet(f"color:{DARK['text_muted']}; font-size:13px; background:transparent; line-height:1.7;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        new_btn = QPushButton("  ＋  New Note")
        new_btn.setFixedSize(160, 40)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background:{DARK['accent_soft']}; border:1px solid {DARK['accent']};
                border-radius:8px; color:{DARK['accent']};
                font-size:13px; font-weight:600;
            }}
            QPushButton:hover {{
                background:{DARK['accent_dim']}; color:{DARK['text_primary']};
            }}
        """)
        new_btn.clicked.connect(self.new_note_requested.emit)

        tips = QLabel("Tip: Right-click a folder in the sidebar to create notes inside it.")
        tips.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px; background:transparent;")
        tips.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(glyph)
        layout.addSpacing(10)
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(sub)
        layout.addSpacing(20)
        layout.addWidget(new_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(32)
        layout.addWidget(tips)
