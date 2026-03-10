# ─────────────────────────────────────────────
#  Gensoubook — Theme
# ─────────────────────────────────────────────

DARK = {
    "bg":           "#13131a",
    "sidebar_bg":   "#1a1a24",
    "panel_bg":     "#16161e",
    "border":       "#2a2a3a",
    "accent":       "#c084fc",       # soft purple — Gensokyo mystic
    "accent_dim":   "#7c3aed",
    "accent_soft":  "#2d1f4a",
    "accent_glow":  "rgba(192,132,252,0.15)",
    "text_primary": "#ece8f4",
    "text_muted":   "#6b6880",
    "hover":        "#22222e",
    "active":       "#2a2040",
    "tab_bg":       "#1a1a24",
    "tab_active":   "#231e35",
    "toolbar":      "#16161e",
    "success":      "#6ee7b7",
    "warning":      "#fbbf24",
    "danger":       "#f87171",
    "scrollbar":    "#2a2a3a",
    "scrollbar_h":  "#4a3a6a",
}

STYLESHEET = f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background-color: {DARK['bg']};
    color: {DARK['text_primary']};
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
    border: none;
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {DARK['border']};
    width: 1px;
    height: 1px;
}}

/* ── Sidebar ── */
QTreeWidget {{
    background-color: {DARK['sidebar_bg']};
    border: none;
    outline: none;
    padding: 4px 2px;
    color: {DARK['text_primary']};
    font-size: 13px;
}}
QTreeWidget::item {{
    padding: 5px 6px;
    border-radius: 6px;
    margin: 1px 4px;
}}
QTreeWidget::item:hover {{
    background-color: {DARK['hover']};
}}
QTreeWidget::item:selected {{
    background-color: {DARK['active']};
    color: {DARK['accent']};
}}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    color: {DARK['text_muted']};
}}
QTreeWidget::branch {{
    background-color: transparent;
}}

/* ── Text Edit ── */
QTextEdit {{
    background-color: {DARK['panel_bg']};
    border: none;
    color: {DARK['text_primary']};
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 14px;
    padding: 28px 36px;
    selection-background-color: {DARK['accent_soft']};
    line-height: 1.7;
}}

/* ── Line Edit ── */
QLineEdit {{
    background-color: {DARK['hover']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    color: {DARK['text_primary']};
    padding: 6px 10px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {DARK['accent']};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {DARK['hover']};
    color: {DARK['text_primary']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {DARK['accent_soft']};
    border-color: {DARK['accent']};
}}
QPushButton:pressed {{
    background-color: {DARK['accent_dim']};
}}
QPushButton:disabled {{
    color: {DARK['text_muted']};
    border-color: {DARK['border']};
    background: transparent;
}}

/* ── Accent button ── */
QPushButton#accent_btn {{
    background-color: {DARK['accent_soft']};
    border: 1px solid {DARK['accent']};
    color: {DARK['accent']};
    font-weight: 600;
}}
QPushButton#accent_btn:hover {{
    background-color: {DARK['accent_dim']};
    color: {DARK['text_primary']};
}}

/* ── Toolbar ── */
QToolBar {{
    background-color: {DARK['toolbar']};
    border-bottom: 1px solid {DARK['border']};
    padding: 3px 8px;
    spacing: 2px;
}}
QToolBar QToolButton {{
    background: transparent;
    border: none;
    border-radius: 5px;
    padding: 4px 8px;
    color: {DARK['text_muted']};
    font-size: 12px;
}}
QToolBar QToolButton:hover {{
    background-color: {DARK['hover']};
    color: {DARK['text_primary']};
}}

/* ── Status bar ── */
QStatusBar {{
    background-color: {DARK['toolbar']};
    border-top: 1px solid {DARK['border']};
    color: {DARK['text_muted']};
    font-size: 11px;
    padding: 2px 10px;
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {DARK['scrollbar']};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {DARK['scrollbar_h']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

/* ── Dialog ── */
QDialog {{
    background-color: {DARK['panel_bg']};
    border: 1px solid {DARK['border']};
    border-radius: 10px;
}}
QDialog QLabel {{
    color: {DARK['text_primary']};
}}

/* ── ComboBox ── */
QComboBox {{
    background-color: {DARK['hover']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    padding: 5px 10px;
    color: {DARK['text_primary']};
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {DARK['accent']};
}}
QComboBox QAbstractItemView {{
    background-color: {DARK['panel_bg']};
    border: 1px solid {DARK['border']};
    color: {DARK['text_primary']};
    selection-background-color: {DARK['active']};
}}

/* ── SpinBox ── */
QSpinBox {{
    background-color: {DARK['hover']};
    border: 1px solid {DARK['border']};
    border-radius: 6px;
    padding: 5px 8px;
    color: {DARK['text_primary']};
}}
QSpinBox:focus {{ border-color: {DARK['accent']}; }}

/* ── Menu ── */
QMenu {{
    background-color: {DARK['panel_bg']};
    border: 1px solid {DARK['border']};
    border-radius: 8px;
    padding: 4px;
    color: {DARK['text_primary']};
}}
QMenu::item {{
    padding: 6px 20px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {DARK['active']};
    color: {DARK['accent']};
}}
QMenu::separator {{
    height: 1px;
    background: {DARK['border']};
    margin: 4px 8px;
}}

/* ── Tooltip ── */
QToolTip {{
    background-color: {DARK['panel_bg']};
    color: {DARK['text_primary']};
    border: 1px solid {DARK['border']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}}

/* ── MessageBox ── */
QMessageBox {{
    background-color: {DARK['panel_bg']};
    color: {DARK['text_primary']};
}}
"""
