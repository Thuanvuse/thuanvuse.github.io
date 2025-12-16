import sys
import math
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QUrl
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath,
    QDesktopServices
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)

# =========================
# CONFIG
# =========================
TELE_URL = "https://t.me/+qJARWJhWEI1hOGFl"
TITLE_MAIN = "🚀 RA MẮT SS3"
TITLE_SUB  = "TOOL QUẢN LÝ OKVIP"
BRANDS = ["okgif", "okvote", "okvip"]

NOTE_TEXT = (
    "⚠️ CHÚ Ý:\n"
    "• Bạn cần có GPM để chạy AN TOÀN cho nick OKVIP của bạn.\n"
    "• Dùng GPM để đăng nhập lấy token, sau đó chạy ẩn mượt mà.\n"
    "• Hỗ trợ đồng thời ~100 luồng (nhẹ, hiệu quả).\n"
    f"• Hệ sinh thái: {', '.join(BRANDS)}"
)

def target_tomorrow_18(now: datetime) -> datetime:
    tomorrow = (now + timedelta(days=1)).date()
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day, 18, 0, 0)

def sec_to_parts(total: int):
    if total < 0:
        total = 0
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return d, h, m, s

# =========================
# VIP 3D DIGITS WIDGET
# =========================
class Digit3D(QLabel):
    """A label that paints 3D/glow digits."""
    def __init__(self, text="00", font_size=54):
        super().__init__(text)
        self._font_size = font_size
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(int(font_size * 1.55))
        self.setStyleSheet("background: transparent;")

    def setText(self, text: str) -> None:
        super().setText(text)
        self.update()

    def paintEvent(self, e):
        t = self.text()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        r = QRectF(self.rect())

        # font
        f = QFont("Consolas", self._font_size, QFont.Weight.Black)
        p.setFont(f)

        # Build text path
        path = QPainterPath()
        # Center baseline manually
        metrics = p.fontMetrics()
        text_w = metrics.horizontalAdvance(t)
        text_h = metrics.height()
        x = r.center().x() - text_w / 2
        y = r.center().y() + (text_h / 2) - metrics.descent()
        path.addText(QPointF(x, y), f, t)

        # Glow layers
        glow_colors = [
            QColor(120, 210, 255, 70),
            QColor(160, 120, 255, 55),
            QColor(255, 120, 220, 40),
        ]
        for i, c in enumerate(glow_colors, start=1):
            pen = QPen(c, 10 + i * 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)

        # Outer stroke (dark edge)
        p.setPen(QPen(QColor(10, 10, 20, 220), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        # "3D depth" offset layers
        for k in range(1, 7):
            offset = QPointF(k * 1.2, k * 1.3)
            shade = QColor(10, 10, 20, 130 - k * 12)
            p.setPen(QPen(shade, 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawPath(path.translated(offset))

        # Main fill gradient (inside digits)
        grad = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
        grad.setColorAt(0.00, QColor(240, 250, 255))
        grad.setColorAt(0.35, QColor(160, 220, 255))
        grad.setColorAt(0.70, QColor(210, 160, 255))
        grad.setColorAt(1.00, QColor(255, 170, 230))

        p.setPen(QPen(QColor(255, 255, 255, 180), 1.2))
        p.setBrush(QBrush(grad))
        p.drawPath(path)

        # Specular highlight
        hi = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.top()))
        hi.setColorAt(0, QColor(255, 255, 255, 120))
        hi.setColorAt(1, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(hi))
        p.drawPath(path.translated(QPointF(-2.0, -3.0)))

        p.end()

# =========================
# MAIN WINDOW
# =========================
class VipCountdown(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SS3 OKVIP - VIP Countdown 5D")
        self.resize(980, 560)
        self.setMinimumSize(860, 520)

        # ===== Title =====
        self.lb_title = QLabel(TITLE_MAIN)
        self.lb_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_title.setStyleSheet("""
            QLabel{
                color: rgba(255,255,255,240);
                font-size: 34px;
                font-weight: 900;
                letter-spacing: 2px;
            }
        """)

        self.lb_sub = QLabel(TITLE_SUB)
        self.lb_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_sub.setStyleSheet("""
            QLabel{
                color: rgba(230,245,255,230);
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 4px;
            }
        """)

        # ===== 3D Countdown Row =====
        self.d_days = Digit3D("00", font_size=52)
        self.d_hh   = Digit3D("00", font_size=52)
        self.d_mm   = Digit3D("00", font_size=52)
        self.d_ss   = Digit3D("00", font_size=52)

        def mk_unit(txt):
            lb = QLabel(txt)
            lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lb.setStyleSheet("color: rgba(220,240,255,200); font-size: 12px; font-weight: 700;")
            return lb

        box_days = self._wrap_digit(self.d_days, mk_unit("NGÀY"))
        box_hh   = self._wrap_digit(self.d_hh,   mk_unit("GIỜ"))
        box_mm   = self._wrap_digit(self.d_mm,   mk_unit("PHÚT"))
        box_ss   = self._wrap_digit(self.d_ss,   mk_unit("GIÂY"))

        row = QHBoxLayout()
        row.setSpacing(14)
        row.addWidget(box_days, 2)
        row.addWidget(box_hh, 2)
        row.addWidget(box_mm, 2)
        row.addWidget(box_ss, 2)

        # ===== Target info =====
        self.lb_target = QLabel("")
        self.lb_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_target.setStyleSheet("color: rgba(210,230,255,200); font-size: 12px;")

        # ===== NOTE BOX (big, not overlapped) =====
        self.note = QFrame()
        self.note.setObjectName("noteBox")
        self.note.setStyleSheet("""
            QFrame#noteBox{
                border-radius: 18px;
                background: rgba(8, 12, 24, 170);
                border: 1px solid rgba(160, 220, 255, 90);
            }
            QLabel{
                background: transparent;
            }
        """)
        note_shadow = QGraphicsDropShadowEffect(self.note)
        note_shadow.setBlurRadius(36)
        note_shadow.setOffset(0, 10)
        note_shadow.setColor(QColor(0, 0, 0, 170))
        self.note.setGraphicsEffect(note_shadow)

        self.lb_note = QLabel(NOTE_TEXT)
        self.lb_note.setWordWrap(True)
        self.lb_note.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lb_note.setStyleSheet("""
            QLabel{
                color: rgba(255,255,255,235);
                font-size: 16px;       /* TO HƠN */
                font-weight: 800;      /* ĐẬM HƠN */
                line-height: 1.35;
                padding: 14px 16px;    /* KHÔNG BỊ LẤP */
            }
        """)

        note_layout = QVBoxLayout(self.note)
        note_layout.setContentsMargins(14, 14, 14, 14)
        note_layout.addWidget(self.lb_note)

        # ===== Telegram button =====
        self.btn_tele = QPushButton("📣 VÀO GROUP TELE - NHẬN THÔNG BÁO")
        self.btn_tele.clicked.connect(self.open_tele)
        self.btn_tele.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tele.setStyleSheet("""
            QPushButton{
                border: 1px solid rgba(255,255,255,60);
                border-radius: 16px;
                padding: 14px 16px;
                color: rgba(255,255,255,240);
                font-size: 14px;
                font-weight: 900;
                letter-spacing: 1px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 rgba(60,180,255,170),
                    stop:0.5 rgba(170,120,255,170),
                    stop:1 rgba(255,120,220,170)
                );
            }
            QPushButton:hover{
                border: 1px solid rgba(255,255,255,140);
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 rgba(80,200,255,210),
                    stop:0.5 rgba(190,140,255,210),
                    stop:1 rgba(255,140,230,210)
                );
            }
            QPushButton:pressed{
                padding-top: 16px;
                padding-bottom: 12px;
                background: rgba(20, 30, 55, 210);
            }
        """)
        tele_shadow = QGraphicsDropShadowEffect(self.btn_tele)
        tele_shadow.setBlurRadius(28)
        tele_shadow.setOffset(0, 10)
        tele_shadow.setColor(QColor(0, 0, 0, 160))
        self.btn_tele.setGraphicsEffect(tele_shadow)

        # ===== Root layout =====
        root = QVBoxLayout()
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(14)
        root.addWidget(self.lb_title)
        root.addWidget(self.lb_sub)
        root.addSpacing(6)
        root.addLayout(row)
        root.addWidget(self.lb_target)
        root.addSpacing(6)
        root.addWidget(self.note)
        root.addWidget(self.btn_tele)
        self.setLayout(root)

        # ===== Timer =====
        self._t = QTimer(self)
        self._t.timeout.connect(self.tick)
        self._t.start(1000)
        self._phase = 0.0
        self._anim = QTimer(self)
        self._anim.timeout.connect(self._animate_bg)
        self._anim.start(16)  # ~60fps
        self.tick()

    def _wrap_digit(self, digit: QLabel, unit: QLabel) -> QWidget:
        card = QFrame()
        card.setStyleSheet("""
            QFrame{
                border-radius: 18px;
                background: rgba(8, 12, 24, 110);
                border: 1px solid rgba(255,255,255,35);
            }
        """)
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(28)
        sh.setOffset(0, 10)
        sh.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(sh)

        v = QVBoxLayout(card)
        v.setContentsMargins(12, 12, 12, 10)
        v.setSpacing(4)
        v.addWidget(digit)
        v.addWidget(unit)
        return card

    def open_tele(self):
        QDesktopServices.openUrl(QUrl(TELE_URL))

    def _animate_bg(self):
        self._phase += 0.015
        if self._phase > 9999:
            self._phase = 0.0
        self.update()

    def tick(self):
        now = datetime.now()
        target = target_tomorrow_18(now)
        self.lb_target.setText(f"Mốc ra mắt: 18:00 ngày mai ({target.strftime('%d/%m/%Y')})")

        diff = int((target - now).total_seconds())
        if diff <= 0:
            self.d_days.setText("00")
            self.d_hh.setText("00")
            self.d_mm.setText("00")
            self.d_ss.setText("00")
            self.lb_title.setText("✅ ĐÃ RA MẮT SS3!")
            self._t.stop()
            return

        d, h, m, s = sec_to_parts(diff)
        self.d_days.setText(f"{d:02d}")
        self.d_hh.setText(f"{h:02d}")
        self.d_mm.setText(f"{m:02d}")
        self.d_ss.setText(f"{s:02d}")

    # ===== 5D background painting =====
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        r = QRectF(self.rect())

        # Base gradient background (FIX: use QPointF)
        g = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
        g.setColorAt(0.0, QColor(7, 10, 20))
        g.setColorAt(0.35, QColor(12, 18, 40))
        g.setColorAt(0.70, QColor(22, 16, 48))
        g.setColorAt(1.0, QColor(10, 12, 26))
        p.fillRect(r, g)

        # Animated aurora blobs
        cx, cy = r.center().x(), r.center().y()
        t = self._phase

        def blob(x, y, radius, c1, c2):
            rg = QRadialGradient(QPointF(x, y), radius)
            rg.setColorAt(0.0, c1)
            rg.setColorAt(1.0, c2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(rg))
            p.drawEllipse(QPointF(x, y), radius, radius)

        blob(cx + math.cos(t*0.9)*260, cy + math.sin(t*1.1)*120, 220,
             QColor(80, 210, 255, 80), QColor(80, 210, 255, 0))
        blob(cx + math.sin(t*1.0)*220, cy + math.cos(t*0.8)*160, 260,
             QColor(190, 120, 255, 75), QColor(190, 120, 255, 0))
        blob(cx + math.cos(t*1.2)*180, cy + math.sin(t*0.7)*220, 240,
             QColor(255, 120, 210, 60), QColor(255, 120, 210, 0))

        # Subtle grid lines for "5D" vibe
        p.setPen(QPen(QColor(255, 255, 255, 12), 1))
        step = 46
        for x in range(0, int(r.width())+1, step):
            p.drawLine(x, 0, x, int(r.height()))
        for y in range(0, int(r.height())+1, step):
            p.drawLine(0, y, int(r.width()), y)

        # Border glow frame
        frame = QRectF(r.left()+10, r.top()+10, r.width()-20, r.height()-20)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(160, 220, 255, 45), 2))
        p.drawRoundedRect(frame, 22, 22)

        p.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VipCountdown()
    w.show()
    sys.exit(app.exec())
