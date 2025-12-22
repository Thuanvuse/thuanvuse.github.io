# pip install PyQt6 requests
import sys
import os
import uuid
import hashlib
import math
from datetime import datetime, timedelta, date

import requests

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QUrl
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath,
    QDesktopServices
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
    QMessageBox, QDialog, QLineEdit, QFormLayout
)

# =========================
# CONFIG
# =========================
TELE_URL = "https://t.me/+qJARWJhWEI1hOGFl"

# MỐC CỐ ĐỊNH: 15:00 ngày 22/12/2025 (giờ VN/Asia/Bangkok)
TARGET_DT = datetime(2025, 12, 22, 15, 0, 0)

TITLE_MAIN = "🛠️ BẢO TRÌ TOOL SS3"
TITLE_SUB  = "TỚI 15:00 22/12/2025"

BRANDS = ["okgif", "okvote", "okvip"]

NOTE_TEXT = (
    "⚠️ CHÚ Ý:\n"
    "• Bạn cần có GPM để chạy AN TOÀN cho nick OKVIP của bạn.\n"
    "• Dùng GPM để đăng nhập lấy token, sau đó chạy ẩn mượt mà.\n"
    "• Hỗ trợ đồng thời ~100 luồng (nhẹ, hiệu quả).\n"
    f"• Hệ sinh thái: {', '.join(BRANDS)}"
)

GPM_PING_URL = "http://127.0.0.1:19995/api/v3/profiles?"

HELLO_URL = "https://raw.githubusercontent.com/Thuanvuse/thuanvuse.github.io/refs/heads/main/hello.py"

# Demo code chạy thử (an toàn hơn: bạn tự dán nội dung hello.py vào đây nếu muốn chạy)
CODE_DEMO = r"""# DÁN NỘI DUNG hello.py VÀO ĐÂY NẾU MUỐN CHẠY
print("Hello SS3 demo!")
"""

# Lưu ý: để lộ user/pass trong code là rủi ro. Bạn cân nhắc chuyển sang file cấu hình/DB nếu dùng thật.
MA_may_da_duoc_kich_hoat = {
    # Ví dụ: thiết bị thuê 30 ngày
    # expires_at: NGÀY HẾT HẠN theo định dạng YYYY-MM-DD (tính theo giờ Việt Nam, không tính giờ)
    "d7093738c24062a8": {
        "username": "admin",
        "password": "thuanadmin",
        "expires_at": "2029-12-05",
        "SoLuong": 100
    },
    # Thiết bị thuê 7 ngày
    "d27c7078c1b600c6": {
        "username": "hung1409",
        "password": "hung2006",
        "expires_at": "2025-12-30",
        "SoLuong": 30
    },
    # Thiết bị thuê 30 ngày
    "9a8aed8e71cbcdef": {
        "username": "hehe1601",
        "password": "789456456Su",
        "expires_at": "2025-12-10",
        "SoLuong": 30
    },
    # Thiết bị thuê 7 ngày
    "703503837aff938a": {
        "username": "echdepzai",
        "password": "echvn123",
        "expires_at": "2026-01-03",
        "SoLuong": 50
    },
    "1d168402a9f1afc1": {
        "username": "tho123",
        "password": "tho123",
        "expires_at": "2050-01-03",
        "SoLuong": 30
    },
    "954a5e1f685a7d46": {
        "username": "Anhtri0409",
        "password": "Taolatri0409",
        "expires_at": "2025-12-17",
        "SoLuong": 30
    },
    "87d01e411f92c4f7": {
        "username": "phamtranthienkhai",
        "password": "Pttk123",
        "expires_at": "2025-12-19",
        "SoLuong": 30
    },
    "0f80315d3971036e": {
        "username": "kienkhe1234",
        "password": "kienkhe123",
        "expires_at": "2025-12-20",
        "SoLuong": 30
    },
    "9890bbf812c2ecfd": {
        "username": "minduc2404",
        "password": "Daz124578",
        "expires_at": "2025-12-6",
        "SoLuong": 30
    },
    "ffa76e91e767cfb3": {
        "username": "np70664",
        "password": "123",
        "expires_at": "2026-1-03",
        "SoLuong": 30
    },
    "97e235cdd8d870e2": {
        "username": "hoakieu15",
        "password": "123",
        "expires_at": "2026-12-8",
        "SoLuong": 30
    },
    "e536f1fc03f37c92": {
        "username": "buinek",
        "password": "123",
        "expires_at": "2026-12-8",
        "SoLuong": 30
    },
    "e517a734593832fd": {
        "username": "lyhaiss2k",
        "password": "ns25112007",
        "expires_at": "2026-12-12",
        "SoLuong": 30
    },
    "3c6a74554204ff61": {
        "username": "palo00",
        "password": "Kingktv123@",
        "expires_at": "2025-12-14",
        "SoLuong": 30
    },
    "50863a5eaed8c5e8": {
        "username": "vip",
        "password": "vip8987",
        "expires_at": "2030-12-14",
        "SoLuong": 30
    },
    "7713b134f005e91b": {
        "username": "vip",
        "password": "vipjqka",
        "expires_at": "2030-12-14",
        "SoLuong": 300
    },"32b2eb25fb61f39a": {
        "username": "anhvu1010",
        "password": "anhvux2005",
        "expires_at": "2025-12-17",
        "SoLuong": 30
    },"f99daa774eb8c16d": {
        "username": "KENDU",
        "password": "123123",
        "expires_at": "2026-01-10",
        "SoLuong": 300
    }
}

# =========================
# HELPERS
# =========================
def get_device_id():
    """Lấy mã máy theo cách sinh và lưu cố định như trong APP.py"""
    device_file = os.path.expanduser("~/.device_id_thuan")
    try:
        if os.path.exists(device_file):
            with open(device_file, "r", encoding="utf-8") as f:
                device_id = f.read().strip()
                if device_id:
                    return device_id
        raw = str(uuid.getnode()) + os.environ.get("USERNAME", "") + os.environ.get("COMPUTERNAME", "")
        device_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
        with open(device_file, "w", encoding="utf-8") as f:
            f.write(device_id)
        return device_id
    except Exception:
        return str(uuid.uuid4())[:16]

def parse_date_loose(s: str) -> date:
    """Parse 'YYYY-M-D' or 'YYYY-MM-DD' safely -> date"""
    if not s:
        raise ValueError("empty date")
    parts = s.strip().split("-")
    if len(parts) != 3:
        raise ValueError("bad date format")
    y = int(parts[0])
    m = int(parts[1])
    d = int(parts[2])
    return date(y, m, d)

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

        f = QFont("Consolas", self._font_size, QFont.Weight.Black)
        p.setFont(f)

        path = QPainterPath()
        metrics = p.fontMetrics()
        text_w = metrics.horizontalAdvance(t)
        text_h = metrics.height()
        x = r.center().x() - text_w / 2
        y = r.center().y() + (text_h / 2) - metrics.descent()
        path.addText(QPointF(x, y), f, t)

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

        p.setPen(QPen(QColor(10, 10, 20, 220), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        for k in range(1, 7):
            offset = QPointF(k * 1.2, k * 1.3)
            shade = QColor(10, 10, 20, 130 - k * 12)
            p.setPen(QPen(shade, 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawPath(path.translated(offset))

        grad = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
        grad.setColorAt(0.00, QColor(240, 250, 255))
        grad.setColorAt(0.35, QColor(160, 220, 255))
        grad.setColorAt(0.70, QColor(210, 160, 255))
        grad.setColorAt(1.00, QColor(255, 170, 230))

        p.setPen(QPen(QColor(255, 255, 255, 180), 1.2))
        p.setBrush(QBrush(grad))
        p.drawPath(path)

        hi = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.top()))
        hi.setColorAt(0, QColor(255, 255, 255, 120))
        hi.setColorAt(1, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(hi))
        p.drawPath(path.translated(QPointF(-2.0, -3.0)))

        p.end()

# =========================
# LOGIN DIALOG
# =========================
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Check hạn sử dụng")
        self.setFixedSize(420, 180)

        self.ed_user = QLineEdit()
        self.ed_pass = QLineEdit()
        self.ed_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Tài khoản:", self.ed_user)
        form.addRow("Mật khẩu:", self.ed_pass)

        btn_ok = QPushButton("Kiểm tra")
        btn_cancel = QPushButton("Hủy")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn_ok)
        row.addWidget(btn_cancel)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(row)

    def creds(self):
        return self.ed_user.text().strip(), self.ed_pass.text()

# =========================
# MAIN WINDOW
# =========================
class VipCountdown(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SS3 OKVIP - VIP Countdown 5D")
        self.resize(980, 610)
        self.setMinimumSize(860, 560)

        # Title
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

        # 3D Countdown Row
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

        # Target info
        self.lb_target = QLabel("")
        self.lb_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_target.setStyleSheet("color: rgba(210,230,255,200); font-size: 12px;")

        # NOTE BOX
        self.note = QFrame()
        self.note.setObjectName("noteBox")
        self.note.setStyleSheet("""
            QFrame#noteBox{
                border-radius: 18px;
                background: rgba(8, 12, 24, 170);
                border: 1px solid rgba(160, 220, 255, 90);
            }
            QLabel{ background: transparent; }
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
                font-size: 18px;
                font-weight: 900;
                line-height: 1.35;
                padding: 16px 18px;
            }
        """)

        note_layout = QVBoxLayout(self.note)
        note_layout.setContentsMargins(14, 14, 14, 14)
        note_layout.addWidget(self.lb_note)

        # Buttons
        self.btn_tele = QPushButton("📣 VÀO GROUP TELE - NHẬN THÔNG BÁO")
        self.btn_tele.clicked.connect(self.open_tele)
        self._style_primary_btn(self.btn_tele)

        self.btn_check = QPushButton("🔐 CHECK HẠN SỬ DỤNG")
        self.btn_check.clicked.connect(self.check_license)
        self._style_dark_btn(self.btn_check)

        self.btn_gpm = QPushButton("🧩 THỬ KẾT NỐI GPM (127.0.0.1:19995)")
        self.btn_gpm.clicked.connect(self.test_gpm)
        self._style_dark_btn(self.btn_gpm)

        # self.btn_demo = QPushButton("🧪 THỬ NGHIỆM TRƯỚC SS3 (XEM CODE DEMO)")
        # self.btn_demo.clicked.connect(self.show_demo_code)
        # self._style_dark_btn(self.btn_demo)

        # Root layout
        root = QVBoxLayout()
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(12)
        root.addWidget(self.lb_title)
        root.addWidget(self.lb_sub)
        root.addSpacing(6)
        root.addLayout(row)
        root.addWidget(self.lb_target)
        root.addSpacing(6)
        root.addWidget(self.note)
        root.addWidget(self.btn_tele)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(self.btn_check)
        btn_row.addWidget(self.btn_gpm)
        root.addLayout(btn_row)

        # root.addWidget(self.btn_demo)

        self.setLayout(root)

        # Timer + background animation
        self._t = QTimer(self)
        self._t.timeout.connect(self.tick)
        self._t.start(1000)

        self._phase = 0.0
        self._anim = QTimer(self)
        self._anim.timeout.connect(self._animate_bg)
        self._anim.start(16)

        self.tick()

    # ---------- styles ----------
    def _style_primary_btn(self, btn: QPushButton):
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
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
        sh = QGraphicsDropShadowEffect(btn)
        sh.setBlurRadius(28)
        sh.setOffset(0, 10)
        sh.setColor(QColor(0, 0, 0, 160))
        btn.setGraphicsEffect(sh)

    def _style_dark_btn(self, btn: QPushButton):
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton{
                border: 1px solid rgba(160, 220, 255, 70);
                border-radius: 14px;
                padding: 12px 14px;
                color: rgba(240,250,255,235);
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 0.6px;
                background: rgba(10, 14, 28, 160);
            }
            QPushButton:hover{
                border: 1px solid rgba(255,255,255,120);
                background: rgba(16, 22, 44, 190);
            }
            QPushButton:pressed{
                background: rgba(6, 8, 18, 210);
            }
        """)
        sh = QGraphicsDropShadowEffect(btn)
        sh.setBlurRadius(22)
        sh.setOffset(0, 8)
        sh.setColor(QColor(0, 0, 0, 150))
        btn.setGraphicsEffect(sh)

    # ---------- layout helper ----------
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

    # ---------- buttons actions ----------
    def open_tele(self):
        QDesktopServices.openUrl(QUrl(TELE_URL))

    def check_license(self):
        dlg = LoginDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        user, pw = dlg.creds()
        if not user or not pw:
            QMessageBox.warning(self, "Thiếu thông tin", "Bạn nhập tài khoản và mật khẩu nhé.")
            return

        device_id = get_device_id()
        rec = MA_may_da_duoc_kich_hoat.get(device_id)

        if not rec:
            QMessageBox.critical(
                self, "Không tìm thấy thiết bị",
                f"Thiết bị này chưa được kích hoạt.\n\nDevice ID: {device_id}"
            )
            return

        if user != rec.get("username") or pw != rec.get("password"):
            QMessageBox.critical(self, "Sai thông tin", "Tài khoản hoặc mật khẩu không đúng.")
            return

        try:
            exp = parse_date_loose(str(rec.get("expires_at", "")).strip())
        except Exception:
            QMessageBox.critical(self, "Lỗi dữ liệu", "expires_at bị sai định dạng.")
            return

        today = datetime.now().date()
        remain = (exp - today).days
        so_luong = rec.get("SoLuong")

        if remain < 0:
            QMessageBox.critical(
                self, "Hết hạn",
                f"❌ Đã hết hạn.\nHạn: {exp.strftime('%d/%m/%Y')}\nDevice ID: {device_id}"
            )
            return

        QMessageBox.information(
            self, "OK",
            f"✅ Hợp lệ!\n"
            f"User: {user}\n"
            f"Hạn: {exp.strftime('%d/%m/%Y')}  (còn {remain} ngày)\n"
            f"SoLuong: {so_luong}\n"
            f"Device ID: {device_id}"
        )

    def test_gpm(self):
        try:
            r = requests.get(GPM_PING_URL, timeout=2.5)
            j = r.json()
            ok = (j.get("message") == "OK")
            if ok:
                QMessageBox.information(self, "Kết nối GPM", "✅ Thành công: GPM trả về message = OK")
            else:
                QMessageBox.warning(
                    self, "Kết nối GPM",
                    "❌ Không đúng phản hồi.\n"
                    "Hãy thử tắt/bật lại GPM.\n\n"
                    "Chúng tôi không thể kết nối tới GPM của bạn."
                )
        except Exception:
            QMessageBox.warning(
                self, "Kết nối GPM",
                "❌ Lỗi kết nối.\n"
                "Hãy thử tắt/bật lại GPM.\n\n"
                "Chúng tôi không thể kết nối tới GPM của bạn."
            )

    def show_demo_code(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Thử nghiệm trước SS3")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "Vì an toàn, app không tự tải code từ Internet rồi exec trực tiếp.\n\n"
            "Bạn có thể:\n"
            "1) Mở link hello.py để xem\n"
            "2) Dán nội dung hello.py vào biến CODE_DEMO trong file này rồi bấm 'Chạy demo'."
        )
        btn_open = msg.addButton("Mở link hello.py", QMessageBox.ButtonRole.ActionRole)
        btn_run  = msg.addButton("Chạy demo (CODE_DEMO)", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Đóng", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_open:
            QDesktopServices.openUrl(QUrl(HELLO_URL))
            return
        if clicked == btn_run:
            try:
                ns = {"__name__": "__demo__", "__file__": "<memory>"}
                exec(CODE_DEMO, ns, ns)
                QMessageBox.information(self, "Demo", "✅ Đã chạy CODE_DEMO (xem output trong terminal).")
            except Exception as ex:
                QMessageBox.critical(self, "Demo lỗi", f"Không chạy được demo:\n{ex}")

    # ---------- timers ----------
    def _animate_bg(self):
        self._phase += 0.015
        if self._phase > 9999:
            self._phase = 0.0
        self.update()

    def tick(self):
        now = datetime.now()
        target = TARGET_DT

        self.lb_target.setText(f"Thời gian kết thúc bảo trì: {target.strftime('%H:%M %d/%m/%Y')}")

        diff = int((target - now).total_seconds())
        if diff <= 0:
            self.d_days.setText("00")
            self.d_hh.setText("00")
            self.d_mm.setText("00")
            self.d_ss.setText("00")
            self.lb_title.setText("✅ KẾT THÚC BẢO TRÌ SS3!")
            self._t.stop()
            return

        d, h, m, s = sec_to_parts(diff)
        self.d_days.setText(f"{d:02d}")
        self.d_hh.setText(f"{h:02d}")
        self.d_mm.setText(f"{m:02d}")
        self.d_ss.setText(f"{s:02d}")

    # ---------- 5D background painting ----------
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        r = QRectF(self.rect())

        g = QLinearGradient(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
        g.setColorAt(0.0, QColor(7, 10, 20))
        g.setColorAt(0.35, QColor(12, 18, 40))
        g.setColorAt(0.70, QColor(22, 16, 48))
        g.setColorAt(1.0, QColor(10, 12, 26))
        p.fillRect(r, g)

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

        p.setPen(QPen(QColor(255, 255, 255, 12), 1))
        step = 46
        for x in range(0, int(r.width())+1, step):
            p.drawLine(x, 0, x, int(r.height()))
        for y in range(0, int(r.height())+1, step):
            p.drawLine(0, y, int(r.width()), y)

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
