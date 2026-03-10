# ✦ Gensoubook

> A personal, offline notebook app built with Python and PyQt6.  
> Write notes, sketch ideas, and organize everything — no cloud, no accounts, just your machine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)

---

## 📸 Preview

> v0.1 — App shell, text editor, and drawing canvas

![Gensoubook Preview](preview.png)

---

## 🚀 Getting Started

### Requirements
- Python 3.10 or higher
- Windows (macOS/Linux untested but may work)

### Install & Run
```bash
pip install -r requirements.txt
python main.py
```

On first launch, Gensoubook will ask you to choose a folder where your notes will be saved.

### Build to .exe
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Gensoubook main.py
```
Your `.exe` will appear in the `dist/` folder.

---

## ✅ What's Working (v0.1)

### App Shell
- [x] First-launch workspace picker — choose any folder on your machine
- [x] Workspace is remembered between sessions
- [x] Dark theme with purple accent
- [x] Window title updates with current note name
- [x] Auto-save every 4 seconds

### Sidebar
- [x] File tree that reads real folders and `.note` files from disk
- [x] Create new notes with template picker (Blank, Journal, Meeting, Whiteboard, Table)
- [x] Create new folders
- [x] Right-click context menu (open, new note here, new subfolder, delete)
- [x] Move notes/folders to trash (soft delete — not permanent)
- [x] Live search across all note content
- [x] Double-click to open a note

### Text Editor
- [x] Plain text / Markdown editing
- [x] Formatting toolbar (Bold, Italic, Strikethrough, H1–H3, Bullet, Numbered, Todo, Code, Divider)
- [x] Word and character count (live)
- [x] Focus mode (hides toolbar and sidebar chrome)
- [x] Unsaved indicator
- [x] Auto-save

### Drawing Canvas
- [x] Pen, Highlighter, Marker, Eraser tools
- [x] Shape tools: Rectangle, Ellipse, Line, Arrow
- [x] Color picker
- [x] Brush size slider
- [x] Undo / Redo
- [x] Clear canvas
- [x] Export canvas as PNG

### File Formats
- [x] `.note` — JSON format storing text blocks and metadata
- [x] `.board` — JSON format for whiteboard objects (canvas state)
- [x] Templates: Blank, Daily Journal, Meeting Notes, Whiteboard, Table Note

---

## 🔧 Known Bugs (v0.1)

Found and documented through real usage testing.

| # | Bug | Status |
|---|-----|--------|
| 1 | Whiteboard template crashes on open | 🔴 Open |
| 2 | Clicking a folder shows all notes at root level instead of isolating folder contents | 🔴 Open |
| 3 | Formatting buttons (Bold, H1, H2, H3, etc.) only insert raw markdown syntax — no rich text rendering | 🔴 Open |
| 4 | Bullet list button inserts `"-"` instead of a proper bullet point | 🔴 Open |
| 5 | Code block button inserts raw ` ``` ` — should wrap selected text in a visible block | 🔴 Open |
| 6 | Draw tab crashes when first opened | 🟡 Partially fixed |
| 7 | Bottom nav buttons (⭐ ⭐ 🏷️ 🗑️ ⚙️) are non-functional — only right-click context menu works | 🔴 Open |
| 8 | Focus mode only hides the formatting bar — doesn't enter true distraction-free mode, and has no proper exit | 🔴 Open |
| 9 | Canvas pixmap not initialized before first paint event | 🟡 Partially fixed |

---

## 🔜 What's Coming

### High Priority
- [ ] **Inline table editor** — create tables with rich cell types (text, checkbox, dropdown, number), resize columns, add/remove rows
- [ ] **Table on whiteboard** — drop a table anywhere on the canvas as a floating object
- [ ] **Whiteboard mode** — infinite panning canvas, zoom, floating text boxes and shapes
- [ ] **Markdown live preview** — toggle between raw and rendered view

### Medium Priority
- [ ] **Tags & labels** — tag notes, filter sidebar by tag
- [ ] **Favorites** — star notes for quick access
- [ ] **Trash panel** — browse and restore trashed notes
- [ ] **Version history** — restore older versions of a note
- [ ] **Daily journal mode** — auto-create a note for today on launch
- [ ] **Rename notes** — inline rename from sidebar

### Lower Priority
- [ ] **Export to PDF**
- [ ] **Export to Markdown (.md)**
- [ ] **Print note**
- [ ] **Light mode toggle**
- [ ] **Custom accent colors / themes**
- [ ] **Font customization** (size, family, line spacing)
- [ ] **Drag and drop** files between folders

---

## 🗂️ Project Structure

```
Gensoubook/
├── main.py          ← Everything — single file app
├── requirements.txt
└── README.md
```

> Currently a single-file app for easy distribution. Will be refactored into modules as features grow.

---

## 📁 File Format Reference

### `.note` (text note)
```json
{
  "type": "note",
  "title": "My Note",
  "created": "2026-03-10T22:56:00",
  "modified": "2026-03-10T22:56:00",
  "tags": ["journal"],
  "blocks": [
    { "type": "text", "value": "# Hello\n\nThis is my note." }
  ]
}
```

### `.board` (whiteboard)
```json
{
  "type": "board",
  "title": "My Whiteboard",
  "canvas": { "zoom": 1.0, "offset_x": 0, "offset_y": 0 },
  "objects": [
    { "type": "stroke", "points": [[100, 200]], "color": "#c084fc", "width": 3 },
    { "type": "table", "x": 300, "y": 200, "columns": ["Task", "Done"], "rows": [["Write README", "✅"]] }
  ]
}
```

---

## 🛠️ Built With

- [Python](https://python.org) 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/) — UI framework
- JSON — note storage format
- [PyInstaller](https://pyinstaller.org) — packaging to `.exe`

---

## 📝 License

Personal project — feel free to fork and build on it.

---

*Gensoubook — named after Gensokyo, the world of Touhou Project.*  
*A spellbook for your thoughts.*
