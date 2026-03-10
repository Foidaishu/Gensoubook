# ✦ Gensoubook

> A personal, offline notebook app built with Python and PyQt6.  
> Write notes, sketch ideas, and organize everything — no cloud, no accounts, just your machine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![Version](https://img.shields.io/badge/Version-v0.2-purple?style=flat-square)

---

## 📸 Preview

> v0.2 — Bug fixes: focus mode, unsaved state, star/tag system, whiteboard zoom & pan

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

## 📋 Changelog

### v0.2 — Bug Fix Release
> Released: March 2026

#### 🐛 Bugs Fixed
| # | Bug | Fix |
|---|-----|-----|
| 1 | Clicking "✕ Exit Focus" button did nothing | Fixed state conflict in `_toggle_focus` — flag is now set inside enter/exit methods, not before |
| 2 | Freshly opened note immediately showed "Unsaved" | `set_content()` now blocks signals during `setPlainText` to prevent spurious `textChanged` firing |
| 3 | Word count showed ~2× the actual count on first open | Same root cause as #2 — word count timer now triggered once manually after load, cleanly |
| 4 | No way to star or tag a note | Right-click context menu now has ⭐ Add to Favorites, 🏷️ Add Tag, ✕ Remove Tag, and ✏️ Rename |
| 5 | Inline code `` ` `` button was invisible in the formatting bar | Label changed to `` `cd` `` with explicit minimum width so it renders visibly |
| 6 | Whiteboard canvas was fixed-size with no zoom or pan | Full transform system added — scroll to zoom, middle-mouse or Space+drag to pan, toolbar zoom controls |

#### ✨ Bonus Addition (v0.2)
- **✏️ Rename note** — available in right-click context menu, pre-fills current title

---

### v0.1 — Initial Release
> Released: March 2026

#### ✅ What Shipped

**App Shell**
- First-launch workspace picker — choose any folder on your machine
- Workspace is remembered between sessions
- Dark theme with purple accent (`#c084fc`)
- Window title updates with current note name
- Auto-save every 4 seconds

**Sidebar**
- File tree that reads real folders and `.note` files from disk
- Create new notes with template picker (Blank, Journal, Meeting, Whiteboard, Table)
- Create new folders
- Right-click context menu (open, new note here, new subfolder, delete)
- Move notes/folders to trash (soft delete — not permanent)
- Live search across all note content
- Double-click to open a note
- ⭐ Favorites, 🏷️ Tags, 🗑️ Trash, ⚙️ Settings panels in bottom nav

**Text Editor**
- Plain text / Markdown editing
- Formatting toolbar (Bold, Italic, Strikethrough, H1–H3, Bullet, Numbered, Todo, Code block, Inline code, Divider)
- Word and character count (live)
- Focus mode (hides toolbar and sidebar, ESC to exit)
- Unsaved indicator with auto-save

**Drawing Canvas**
- Pen, Highlighter, Marker, Eraser tools
- Shape tools: Rectangle, Ellipse, Line, Arrow
- Color picker + brush size slider
- Undo / Redo (50-step history)
- Clear canvas
- Export canvas as PNG

**File Formats**
- `.note` — JSON format storing text blocks and metadata
- `.board` — JSON format for whiteboard state
- Templates: Blank, Daily Journal, Meeting Notes, Whiteboard, Table Note

---

## ✅ Current State (v0.2)

### Working
- [x] Workspace setup and persistence
- [x] Dark theme, sidebar, folder tree
- [x] Write / Draw tab switching
- [x] Drawing canvas — pen, shapes, eraser, color, size
- [x] Whiteboard opens without crashing
- [x] Focus mode — enters via button, exits via button or ESC
- [x] Star notes as favorites (⭐ in right-click menu)
- [x] Tag notes (🏷️ in right-click menu), remove tags, filter by tag in sidebar
- [x] Rename notes from right-click menu
- [x] Inline code button visible in formatting bar
- [x] Whiteboard zoom (scroll wheel, ＋/－ buttons, 1:1 reset) and pan (middle-mouse or Space+drag)
- [x] Note open no longer triggers false "Unsaved" or double word count

---

## 🔜 What's Coming

### High Priority
- [ ] **Markdown live preview** — toggle between raw markdown and rendered view
- [ ] **Inline table editor** — create tables with rich cell types, resize columns, add/remove rows
- [ ] **Export to PDF / Markdown** — save notes outside the app
- [ ] **Version history** — restore older versions of a note

### Medium Priority
- [ ] **Light mode toggle**
- [ ] **Daily journal mode** — auto-create a note for today on launch
- [ ] **Trash panel** — browse and restore trashed notes from the sidebar
- [ ] **Drag and drop** files between folders

### Lower Priority
- [ ] **Custom accent colors / themes**
- [ ] **Font customization** (size, family, line spacing)
- [ ] **Print note**

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
  "tags": ["journal", "favorite"],
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
    { "type": "stroke", "points": [[100, 200]], "color": "#c084fc", "width": 3 }
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
