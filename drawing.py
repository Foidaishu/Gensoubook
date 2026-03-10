"""
Gensoubook — Drawing Canvas
Pen, highlighter, shapes, eraser, undo/redo, export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QColorDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QPoint, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QCursor,
    QBrush, QPainterPath
)

from core.theme import DARK


# ─────────────────────────────────────────────
#  Canvas widget
# ─────────────────────────────────────────────
class Canvas(QWidget):
    changed = pyqtSignal()

    TOOLS = ["pen", "highlighter", "marker", "eraser", "line", "rect", "ellipse", "arrow"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.tool       = "pen"
        self.color      = QColor(DARK["accent"])
        self.size       = 3
        self.opacity    = 1.0

        self._pixmap    = None
        self._history   = []          # list of QPixmap snapshots
        self._redo_stack = []
        self._drawing   = False
        self._last_pt   = QPointF()
        self._start_pt  = QPointF()
        self._overlay   = None        # temp pixmap for shape preview

    def resizeEvent(self, event):
        if self._pixmap is None or self._pixmap.isNull():
            self._pixmap = QPixmap(self.size())
            self._pixmap.fill(QColor(DARK["panel_bg"]))
        else:
            # Expand canvas when resized
            new_px = QPixmap(self.size())
            new_px.fill(QColor(DARK["panel_bg"]))
            p = QPainter(new_px)
            p.drawPixmap(0, 0, self._pixmap)
            p.end()
            self._pixmap = new_px
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        if self._pixmap:
            p.drawPixmap(0, 0, self._pixmap)
        if self._overlay:
            p.drawPixmap(0, 0, self._overlay)
        p.end()

    # ── Mouse ────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing  = True
            self._start_pt = event.position()
            self._last_pt  = event.position()
            self._snapshot()
            if self.tool in ("pen", "highlighter", "marker", "eraser"):
                self._draw_point(event.position())

    def mouseMoveEvent(self, event):
        if not self._drawing:
            return
        pt = event.position()
        if self.tool in ("pen", "highlighter", "marker", "eraser"):
            self._draw_line(self._last_pt, pt)
            self._last_pt = pt
        else:
            # Shape preview
            self._overlay = QPixmap(self.size())
            self._overlay.fill(Qt.GlobalColor.transparent)
            p = QPainter(self._overlay)
            self._apply_pen(p, preview=True)
            self._draw_shape(p, self._start_pt, pt)
            p.end()
        self.update()

    def mouseReleaseEvent(self, event):
        if not self._drawing:
            return
        self._drawing = False
        pt = event.position()
        if self.tool not in ("pen", "highlighter", "marker", "eraser"):
            # Commit shape
            p = QPainter(self._pixmap)
            self._apply_pen(p)
            self._draw_shape(p, self._start_pt, pt)
            p.end()
            self._overlay = None
        self.update()
        self.changed.emit()

    # ── Drawing internals ────────────────────────
    def _draw_point(self, pt: QPointF):
        p = QPainter(self._pixmap)
        self._apply_pen(p)
        p.drawPoint(pt.toPoint())
        p.end()
        self.update()

    def _draw_line(self, a: QPointF, b: QPointF):
        p = QPainter(self._pixmap)
        self._apply_pen(p)
        p.drawLine(a.toPoint(), b.toPoint())
        p.end()
        self.update()

    def _apply_pen(self, painter: QPainter, preview: bool = False):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self.color)

        if self.tool == "eraser":
            color = QColor(DARK["panel_bg"])
            pen_size = self.size * 6
            painter.setPen(QPen(color, pen_size, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        elif self.tool == "highlighter":
            color.setAlpha(70)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(color, self.size * 8, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        elif self.tool == "marker":
            color.setAlpha(200)
            painter.setPen(QPen(color, self.size * 2, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
        else:
            if preview:
                color.setAlpha(160)
            painter.setPen(QPen(color, self.size, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

    def _draw_shape(self, painter: QPainter, a: QPointF, b: QPointF):
        x1, y1 = int(a.x()), int(a.y())
        x2, y2 = int(b.x()), int(b.y())
        if self.tool == "line":
            painter.drawLine(x1, y1, x2, y2)
        elif self.tool == "rect":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        elif self.tool == "ellipse":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        elif self.tool == "arrow":
            self._draw_arrow(painter, a, b)

    def _draw_arrow(self, painter: QPainter, a: QPointF, b: QPointF):
        import math
        painter.drawLine(a.toPoint(), b.toPoint())
        angle = math.atan2(b.y()-a.y(), b.x()-a.x())
        size = 14
        for sign in (1, -1):
            ax = b.x() - size * math.cos(angle - sign * math.pi / 7)
            ay = b.y() - size * math.sin(angle - sign * math.pi / 7)
            painter.drawLine(b.toPoint(), QPointF(ax, ay).toPoint())

    # ── History ──────────────────────────────────
    def _snapshot(self):
        if self._pixmap:
            self._history.append(self._pixmap.copy())
            if len(self._history) > 50:
                self._history.pop(0)
            self._redo_stack.clear()

    def undo(self):
        if self._history:
            self._redo_stack.append(self._pixmap.copy())
            self._pixmap = self._history.pop()
            self.update()

    def redo(self):
        if self._redo_stack:
            self._history.append(self._pixmap.copy())
            self._pixmap = self._redo_stack.pop()
            self.update()

    def clear(self):
        self._snapshot()
        if self._pixmap:
            self._pixmap.fill(QColor(DARK["panel_bg"]))
        self.update()
        self.changed.emit()

    # ── Export ───────────────────────────────────
    def to_bytes_png(self) -> bytes:
        import io
        from PyQt6.QtCore import QBuffer, QIODevice
        buf = QBuffer()
        buf.open(QIODevice.OpenMode.WriteOnly)
        self._pixmap.save(buf, "PNG")
        return bytes(buf.data())

    def get_pixmap(self) -> QPixmap:
        return self._pixmap


# ─────────────────────────────────────────────
#  Drawing Panel (toolbar + canvas)
# ─────────────────────────────────────────────
class DrawingPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_toolbar())

        self.canvas = Canvas()
        self.canvas.changed.connect(self.changed.emit)
        layout.addWidget(self.canvas)

    def _build_toolbar(self):
        bar = QWidget()
        bar.setFixedHeight(38)
        bar.setStyleSheet(f"background:{DARK['toolbar']}; border-bottom:1px solid {DARK['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(4)

        # Tool buttons
        tools = [
            ("✒️", "pen",         "Pen"),
            ("🖊️", "highlighter", "Highlighter"),
            ("🖋️", "marker",      "Marker"),
            ("⬜", "rect",        "Rectangle"),
            ("⭕", "ellipse",     "Ellipse"),
            ("╱",  "line",        "Line"),
            ("→",  "arrow",       "Arrow"),
            ("⌫",  "eraser",      "Eraser"),
        ]

        self._tool_btns = {}
        for icon, tool_id, tip in tools:
            btn = QPushButton(icon)
            btn.setFixedSize(28, 28)
            btn.setToolTip(tip)
            btn.setCheckable(True)
            btn.setChecked(tool_id == "pen")
            btn.setStyleSheet(self._tool_btn_style())
            btn.clicked.connect(lambda _, t=tool_id: self._set_tool(t))
            lay.addWidget(btn)
            self._tool_btns[tool_id] = btn

        # Separator
        sep = QFrame()
        sep.setFixedSize(1, 20)
        sep.setStyleSheet(f"background:{DARK['border']};")
        from PyQt6.QtWidgets import QFrame
        lay.addWidget(sep)

        # Color picker
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.setToolTip("Pick color")
        self._update_color_btn(QColor(DARK["accent"]))
        self.color_btn.clicked.connect(self._pick_color)
        lay.addWidget(self.color_btn)

        # Size slider
        size_lbl = QLabel("Size:")
        size_lbl.setStyleSheet(f"color:{DARK['text_muted']}; font-size:11px;")
        lay.addWidget(size_lbl)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 20)
        self.size_slider.setValue(3)
        self.size_slider.setFixedWidth(80)
        self.size_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background:{DARK['border']}; height:4px; border-radius:2px;
            }}
            QSlider::handle:horizontal {{
                background:{DARK['accent']}; width:12px; height:12px;
                border-radius:6px; margin:-4px 0;
            }}
        """)
        self.size_slider.valueChanged.connect(lambda v: setattr(self.canvas, 'size', v))
        lay.addWidget(self.size_slider)

        lay.addStretch()

        # Undo / Redo / Clear
        for icon, tip, cb in [("↩", "Undo", self.canvas.undo), ("↪", "Redo", self.canvas.redo), ("🗑", "Clear canvas", self.canvas.clear)]:
            btn = QPushButton(icon)
            btn.setFixedSize(28, 28)
            btn.setToolTip(tip)
            btn.setStyleSheet(self._tool_btn_style())
            btn.clicked.connect(cb)
            lay.addWidget(btn)

        # Export
        exp_btn = QPushButton("⬇ Export")
        exp_btn.setFixedHeight(26)
        exp_btn.setToolTip("Export as PNG")
        exp_btn.setStyleSheet(self._tool_btn_style(text=True))
        exp_btn.clicked.connect(self._export)
        lay.addWidget(exp_btn)

        return bar

    def _set_tool(self, tool_id: str):
        self.canvas.tool = tool_id
        for tid, btn in self._tool_btns.items():
            btn.setChecked(tid == tool_id)

    def _pick_color(self):
        col = QColorDialog.getColor(self.canvas.color, self, "Pick Color")
        if col.isValid():
            self.canvas.color = col
            self._update_color_btn(col)

    def _update_color_btn(self, color: QColor):
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background:{color.name()}; border:2px solid {DARK['border']};
                border-radius:4px;
            }}
            QPushButton:hover {{ border-color:{DARK['accent']}; }}
        """)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Drawing", "", "PNG Image (*.png);;SVG File (*.svg)"
        )
        if path:
            if path.endswith(".svg"):
                # Basic SVG export
                px = self.canvas.get_pixmap()
                # Save as PNG first then note SVG is future
                px.save(path.replace(".svg", ".png"), "PNG")
            else:
                self.canvas.get_pixmap().save(path, "PNG")

    # Public API
    def clear_canvas(self):
        self.canvas.clear()

    def _tool_btn_style(self, text=False):
        padding = "4px 10px" if text else "2px"
        return f"""
            QPushButton {{
                background:transparent; border:none; border-radius:5px;
                padding:{padding}; color:{DARK['text_muted']}; font-size:13px;
            }}
            QPushButton:hover {{ background:{DARK['hover']}; color:{DARK['text_primary']}; }}
            QPushButton:checked {{ background:{DARK['active']}; color:{DARK['accent']}; }}
        """

# import needed for separator in toolbar
from PyQt6.QtWidgets import QFrame
