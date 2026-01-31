import sys
import time
import random
import re
import threading
import requests
import winsound
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QSplitter, QFrame,
    QScrollArea, QGroupBox, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

# --- Cấu hình chung ---

DEFAULT_API_HOST = "http://127.0.0.1:19053"
DEFAULT_BROWSER_VERSION = "129.0.6668.59"
CREATE_PROFILE_PATH = "/api/v3/profiles/create"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 50

# UI scale factor (1.0 = 100%). Set to 0.5 to reduce UI by 50%.
UI_SCALE = 0.8

# --- Tên file cấu hình ---
CONFIG_FILE = "gui_config.json"

# Danh sách họ và tên Việt Nam
ho_list = ["le", "lam", "mai", "dao", "son", "nam", "bao", "han", "yen", "hoa", "lan", "ha", "hue", "tam", "tuan", "tien", "tung", "toan", "khan", "kieu", "phat", "phuc", "quoc", "quyn", "ngan", "ngoc", "hieu", "hung", "hien", "thao", "thuy", "thanh", "thang", "truc", "trung", "trinh", "trieu", "trang", "vu", "vo", "do", "du", "vi", "luu", "cao", "mac", "sam", "tat"]
ten_list = ["anh", "binh", "chau", "dung", "dat", "giang", "ha", "hai", "hanh", "hieu", "hung", "lan", "linh", "minh", "nam", "ngoc", "phat", "phuc", "quang", "quoc", "son", "thao", "thuy", "tam", "tai", "bao", "cam", "dao", "dien", "dinh", "duc", "giao", "hao", "hoa", "hoai", "huan", "khan", "kien", "kieu", "long", "luan", "mai", "manh", "ngan", "nhan", "nhat", "sang", "tan", "thien", "thinh", "thoa", "thuc", "tien", "tinh", "trang", "trieu", "trinh", "truc", "trung", "tuan", "tung", "tu", "van", "viet", "vy", "yen"]

def random_ten_viet():
    while True:
        ho = random.choice(ho_list)
        dem = random.choice(ten_list)
        ten = random.choice(ten_list)
        num = str(random.randint(100, 999))
        username = f"{ho}{dem}{ten}{num}".lower()
        if len(username) < 16:
            return username

def random_mat_khau(username):
    return f"{username}@z"

def get_viotp_balance(token):
    try:
        resp = requests.get(f"https://api.viotp.com/users/balance?token={token}", timeout=10).json()
        return resp.get("data", {}).get("balance", 0)
    except Exception as e:
        # print("Failed to fetch balance:", e)
        return 0

def ensure_files_exist():
    """Đảm bảo các file cần thiết tồn tại"""
    # Tạo file fid.txt nếu chưa có
    if not os.path.exists("fid.txt"):
        with open("fid.txt", "w", encoding="utf-8") as f:
            f.write("")  # File trống ban đầu

    # Tạo file ACC.txt nếu chưa có
    if not os.path.exists("ACC.txt"):
        with open("ACC.txt", "w", encoding="utf-8") as f:
            f.write("")  # File trống ban đầu

class LogRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.append(text.strip())

    def flush(self):
        pass

class ProxyCheckWorker(QThread):
    """Worker thread for proxy checking operations to prevent UI freezing"""
    finished = pyqtSignal(str)  # result message
    log_signal = pyqtSignal(str)  # log messages

    def __init__(self, operation, keys, configs=None):
        super().__init__()
        self.operation = operation  # 'single' or 'all'
        self.keys = keys
        self.configs = configs

    def run(self):
        try:
            if self.operation == 'single':
                result = self.check_single_proxy()
            elif self.operation == 'all':
                result = self.check_all_proxies()
            else:
                result = "❌ Lỗi: Operation không hợp lệ"

            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"❌ Lỗi: {str(e)}")

    def check_single_proxy(self):
        """Check proxy for first key or first config's key"""
        if not self.keys:
            return "❌ Không có KEYS nào để check proxy!"

        if self.configs:
            # Lấy key từ config đầu tiên
            first_config = self.configs[0]
            key_index = first_config.get("kito_key_index", 0)
            if key_index >= len(self.keys):
                key_index = 0  # Fallback to first key
            key = self.keys[key_index]
        else:
            # Check key đầu tiên
            key_index = 0
            key = self.keys[0]

        # Ẩn một phần key để bảo mật
        masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else key

        self.log_signal.emit(f"🔍 Đang check proxy cho key {masked_key} (index {key_index})...")

        try:
            response = requests.get(f"https://api.kiotproxy.com/api/v1/proxies/current?key={key}", timeout=10)
            data = response.json()

            if data.get("success") and data.get("code") == 200:
                proxy_data = data["data"]
                real_ip = proxy_data.get("realIpAddress", "N/A")
                http = proxy_data.get("http", "N/A")
                socks5 = proxy_data.get("socks5", "N/A")
                location = proxy_data.get("location", "N/A")
                ttl = proxy_data.get("ttl", 0)
                expiration = proxy_data.get("expirationAt", 0)

                # Chuyển TTL thành phút:giây
                minutes = ttl // 60
                seconds = ttl % 60
                ttl_display = f"{minutes}:{seconds:02d}" if ttl > 0 else "N/A"

                return f"""
🔍 THÔNG TIN PROXY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Real IP: {real_ip}
🌐 HTTP Proxy: {http}
🔒 SOCKS5 Proxy: {socks5}
📍 Location: {location}
⏱️ TTL còn lại: {ttl_display}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            elif data.get("code") == 40001050:  # PROXY_NOT_FOUND_BY_KEY
                return f"⚠️ Key {masked_key}: Chưa tạo proxy"
            else:
                error_msg = data.get("message", "Lỗi không xác định")
                return f"❌ Key {masked_key}: {error_msg}"

        except requests.RequestException as e:
            return f"❌ Lỗi network khi check proxy: {str(e)}"
        except Exception as e:
            return f"❌ Lỗi không xác định: {str(e)}"

    def check_all_proxies(self):
        """Check proxy for all keys"""
        if not self.keys:
            return "❌ Không có KEYS nào để check proxy!"

        self.log_signal.emit(f"🔍 Đang check proxy cho tất cả {len(self.keys)} keys...")

        results = []
        success_count = 0
        error_count = 0

        for i, key in enumerate(self.keys):
            try:
                # Ẩn một phần key để bảo mật
                masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else key

                self.log_signal.emit(f"🔍 Checking key {masked_key} (index {i})...")
                response = requests.get(f"https://api.kiotproxy.com/api/v1/proxies/current?key={key}", timeout=10)
                data = response.json()

                if data.get("success") and data.get("code") == 200:
                    proxy_data = data["data"]
                    real_ip = proxy_data.get("realIpAddress", "N/A")
                    location = proxy_data.get("location", "N/A")
                    ttl = proxy_data.get("ttl", 0)

                    # Chuyển TTL thành phút:giây
                    minutes = ttl // 60
                    seconds = ttl % 60
                    ttl_display = f"{minutes}:{seconds:02d}" if ttl > 0 else "N/A"

                    result = f"✅ Key {masked_key}: IP {real_ip} ({location}) - TTL {ttl_display}"
                    results.append(result)
                    success_count += 1

                elif data.get("code") == 40001050:  # PROXY_NOT_FOUND_BY_KEY
                    result = f"⚠️ Key {masked_key}: Chưa tạo proxy"
                    results.append(result)
                    error_count += 1
                else:
                    error_msg = data.get("message", "Lỗi không xác định")
                    result = f"❌ Key {masked_key}: {error_msg}"
                    results.append(result)
                    error_count += 1

            except requests.RequestException as e:
                result = f"❌ Key {masked_key}: Lỗi network - {str(e)}"
                results.append(result)
                error_count += 1
            except Exception as e:
                result = f"❌ Key {masked_key}: Lỗi không xác định - {str(e)}"
                results.append(result)
                error_count += 1

            # Thêm delay nhỏ giữa các requests để tránh rate limiting
            time.sleep(0.1)

        # Tạo summary
        total_count = len(self.keys)
        summary = f"""
🔍 KẾT QUẢ CHECK PROXY ({total_count} keys)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Thành công: {success_count}
❌ Lỗi: {error_count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for result in results:
            summary += result + "\n"

        return summary.rstrip()


class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(str, int)  # stat_type, increment

    def __init__(self, keys, configs, api_host, browser_version, target_acc=0):
        super().__init__()
        self.keys = keys
        self.configs = configs
        self.api_host = api_host
        self.browser_version = browser_version
        self.running = True
        self.active_profiles = []  # Lưu trữ tất cả profile_id đang chạy
        self.active_drivers = []   # Lưu trữ tất cả driver instances
        self.profile_lock = threading.Lock()  # Thread-safe cho profile management
        # Target số lượng tài khoản cần tạo (0 = không giới hạn)
        self.target_acc = int(target_acc or 0)
        # Đếm số account đã tạo thành công bởi worker này (thread-safe)
        self._created_count = 0
        self._created_lock = threading.Lock()

    def stop(self):
        # Chỉ đặt flag để dừng; không thực hiện công việc nặng tại đây
        # để tránh block giao diện (GUI). Việc đóng profiles sẽ được
        # thực hiện trong thread khi run() kết thúc.
        self.running = False

    def close_all_profiles(self):
        """Đóng tất cả profiles đang chạy và xóa giao diện"""
        with self.profile_lock:
            total_items = len(self.active_drivers) + len(self.active_profiles)
            if total_items == 0:
                self.log_signal.emit("✅ Không có profiles/drivers nào cần đóng")
                return

            self.log_signal.emit(f"🛑 Đang đóng {len(self.active_drivers)} drivers và {len(self.active_profiles)} profiles...")

            # Đóng tất cả drivers
            closed_drivers = 0
            for driver in self.active_drivers[:]:  # Copy list để tránh lỗi khi remove
                try:
                    driver.quit()
                    closed_drivers += 1
                    self.log_signal.emit(f"✅ Đã đóng driver ({closed_drivers}/{len(self.active_drivers)})")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Lỗi đóng driver: {e}")

            # Đóng tất cả profiles qua API
            closed_profiles = 0
            session = requests.Session()
            session.headers.update(HEADERS)
            for profile_id in self.active_profiles[:]:  # Copy list để tránh lỗi khi remove
                try:
                    close_url = f"{self.api_host}/api/v3/profiles/close/{profile_id}"
                    resp = session.get(close_url, timeout=10)
                    if resp.status_code == 200:
                        closed_profiles += 1
                        self.log_signal.emit(f"✅ Đã đóng profile {profile_id} ({closed_profiles}/{len(self.active_profiles)})")
                    else:
                        self.log_signal.emit(f"⚠️ Không thể đóng profile {profile_id}")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Lỗi đóng profile {profile_id}: {e}")

            # Clear lists
            self.active_profiles.clear()
            self.active_drivers.clear()
            self.log_signal.emit(f"✅ Đã đóng tất cả {closed_drivers} drivers và {closed_profiles} profiles!")

    def run(self):
        # Chuyển đổi configs từ dict sang format cũ
        converted_configs = []
        for cfg in self.configs:
            converted_cfg = cfg.copy()
            converted_cfg["kito_key"] = self.keys[cfg["kito_key_index"]]
            converted_cfg["raw_proxy"] = f"kiot://{converted_cfg['kito_key']}:True"
            converted_configs.append(converted_cfg)

        # Start config server
        start_viotp_config_server()

        threads = []
        for cfg in converted_configs:
            if not self.running:
                break
            t = threading.Thread(target=self.worker_loop, args=(cfg,), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        # Khi tất cả worker threads con đã dừng, thực hiện cleanup nặng
        # trong chính WorkerThread (không trên main thread) để tránh
        # làm đơ giao diện người dùng.
        try:
            self.close_all_profiles()
        except Exception as e:
            self.log_signal.emit(f"⚠️ Lỗi khi đóng profiles sau khi dừng: {e}")

    def worker_loop(self, cfg):
        while self.running:
            try:
                self.run_instance(cfg)
            except Exception as e:
                error_msg = str(e)
                self.log_signal.emit(f"[{cfg['name']}] Worker loop error: {error_msg}")

                # Nếu lỗi proxy thì dừng luồng này
                if "Không thể kết nối tới proxy" in error_msg:
                    self.log_signal.emit(f"[{cfg['name']}] ❌ Lỗi proxy - Dừng luồng này!")
                    break

            time.sleep(2)

    def run_instance(self, cfg):
        # Copy toàn bộ logic từ run_instance gốc

        # ===== KIỂM TRA SỐ DƯ VÀ LẤY SỐ ĐIỆN THOẠI TRƯỚC KHI TẠO PROFILE =====
        provider = cfg.get("provider", "VIOTP")

        # Kiểm tra balance dựa trên provider
        if provider == "VIOTP":
            balance = get_viotp_balance(cfg['token_vio'])
            min_balance = 1600
        else:  # BOSSOTP
            try:
                url = f"https://bossotp.net/api/v4/users/me/balance?api_token={cfg.get('boss_token', '')}"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                balance = data.get("balance", 0)
                min_balance = 4000  # Giả sử giá dịch vụ BOSSOTP là 3500
            except:
                balance = 0
                min_balance = 4000

        if balance <= min_balance:
            self.log_signal.emit(f"[{cfg['name']}] 💰 Số dư {provider}: {balance} VND (cần > {min_balance} VND)")
            self.log_signal.emit(f"[{cfg['name']}] 🔄 Check balance mỗi 10 giây - tạo account ngay khi đủ tiền...")

            # Loop check balance mỗi 10 giây cho đến khi đủ hoặc bị stop
            check_count = 0
            while self.running:
                check_count += 1
                self.log_signal.emit(f"[{cfg['name']}] 🔍 Check balance lần {check_count}...")

                if provider == "VIOTP":
                    balance = get_viotp_balance(cfg['token_vio'])
                else:
                    try:
                        url = f"https://bossotp.net/api/v4/users/me/balance?api_token={cfg.get('boss_token', '')}"
                        resp = requests.get(url, timeout=10)
                        data = resp.json()
                        balance = data.get("balance", 0)
                    except:
                        balance = 0

                if balance > min_balance:
                    self.log_signal.emit(f"[{cfg['name']}] ✅ Số dư đủ: {balance} VND. Tiếp tục!")
                    break

                self.log_signal.emit(f"[{cfg['name']}] ⏳ Chưa đủ tiền ({balance} VND). Chờ 10 giây...")
                time.sleep(10)

            # Nếu bị stop thì thoát
            if not self.running:
                self.log_signal.emit(f"[{cfg['name']}] ⏹️ Dừng check balance do chương trình bị stop")
                return

        # ===== LẤY SỐ ĐIỆN THOẠI TRƯỚC KHI TẠO PROFILE =====
        self.log_signal.emit(f"[{cfg['name']}] 🔍 Đang tìm số điện thoại khả dụng...")

        phone_number = None
        request_id = None
        phone_check_count = 0

        while self.running and phone_number is None:
            phone_check_count += 1
            self.log_signal.emit(f"[{cfg['name']}] 🔄 Lần thử {phone_check_count}: Đang lấy số điện thoại...")

            phone_number, request_id = self.get_phone_number(cfg)

            if phone_number is None:
                self.log_signal.emit(f"[{cfg['name']}] ⏳ Không có số khả dụng. Chờ 10 giây rồi thử lại...")
                time.sleep(10)
            else:
                self.log_signal.emit(f"[{cfg['name']}] ✅ Đã có số điện thoại: {phone_number}")
                break

        # Nếu bị stop hoặc không có số thì thoát
        if not self.running:
            self.log_signal.emit(f"[{cfg['name']}] ⏹️ Dừng do chương trình bị stop")
            return
        if phone_number is None:
            self.log_signal.emit(f"[{cfg['name']}] ❌ Không thể lấy số điện thoại sau nhiều lần thử")
            return

        session = requests.Session()
        session.headers.update(HEADERS)
        profile_id = None
        driver = None
        try:
            payload = {
                "profile_name": f"ThuanOkVIPPro",
                "group_name": "All",
                "browser_core": "chromium",
                "browser_name": "Chrome",
                "browser_version": self.browser_version,
                "is_random_browser_version": False,
                "raw_proxy": cfg["raw_proxy"],
                "startup_urls": "https://m.okvipau.com/home",
                "is_masked_font": True,
                "is_noise_canvas": True,
                "is_noise_webgl": True,
                "is_noise_client_rect": True,
                "is_noise_audio_context": True,
                "is_random_screen": True,
                "is_masked_webgl_data": True,
                "is_masked_media_device": True,
                "is_random_os": True,
               
                "user_agent": random.choice([
                    # iPhone user agents
                    "MyApp/2.3.1 (iPhone; iOS 17.2; Scale/3.00) Alamofire/5.6 (com.example.myapp/231)",
                    "MyApp/1.9.0 (iPhone; iOS 16.6; Scale/3.00) CFNetwork/1240.0.4 Darwin/22.5.0",
                    "MyApp/3.0.0 (iPhone; iOS 17.0; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/5.0.2 (iPhone; iOS 17.1; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366",
                    "MyApp/4.2.0 (iPhone; iOS 16.7; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/6.1.0 (iPhone; iOS 17.3; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17A360",
                    "MyApp/3.5.0 (iPhone; iOS 16.4; Scale/3.00) CFNetwork/1333.0.4 Darwin/21.5.0",
                    "MyApp/7.0.0 (iPhone; iOS 17.4; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17B84",

                    # iPad user agents
                    "MyApp/4.1.0 (iPad; iOS 16.5; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/5.2.0 (iPad; iOS 17.0; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/3.8.0 (iPad; iOS 16.3; Scale/2.00) CFNetwork/1335.0.3 Darwin/21.4.0",
                    "MyApp/6.0.0 (iPad; iOS 17.2; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366",
                    "MyApp/4.5.0 (iPad; iOS 16.6; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",

                    # Different app names and versions
                    "Safari/605.1.15 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "Safari/605.1.15 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "Safari/605.1.15 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MobileSafari/604.1 CFNetwork/1333.0.4 Darwin/21.5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MobileSafari/604.1 CFNetwork/1240.0.4 Darwin/20.5.0 (iPad; CPU OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",

                    # Different iOS versions
                    "MyApp/2.1.0 (iPhone; iOS 15.7; Scale/3.00) CFNetwork/1335.0.3 Darwin/21.4.0",
                    "MyApp/3.2.0 (iPhone; iOS 15.5; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/4.0.0 (iPad; iOS 15.4; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "MyApp/5.5.0 (iPhone; iOS 14.8; Scale/3.00) CFNetwork/1240.0.4 Darwin/20.5.0",
                    "MyApp/6.5.0 (iPad; iOS 14.7; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",

                    # More recent versions
                    "MyApp/7.2.0 (iPhone; iOS 17.5; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17B84",
                    "MyApp/8.0.0 (iPad; iOS 17.4; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17A360",
                    "MyApp/9.1.0 (iPhone; iOS 17.3; Scale/3.00) CFNetwork/1406.0.4 Darwin/22.5.0",
                    "MyApp/10.0.0 (iPhone; iOS 17.2; Scale/3.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366",
                    "MyApp/11.0.0 (iPad; iOS 17.1; Scale/2.00) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
                ]),
            }
            url = f"{self.api_host}{CREATE_PROFILE_PATH}"
            resp = session.post(url, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                raise RuntimeError(f"Create profile failed: {data}")
            profile_id = data["data"]["id"]
            self.log_signal.emit(f"[{cfg['name']}] Created profile {profile_id}")

            # Thêm profile vào tracking list
            with self.profile_lock:
                self.active_profiles.append(profile_id)

            x, y = cfg.get("win_pos", (0, 0))
            start_url = f"{self.api_host}/api/v3/profiles/start/{profile_id}?win_pos={x},{y}&win_scale=0.4&win_size=368,868&addination_args=--app=https://m.okvipau.com/&addination_args=--mute-audio"
            resp = session.get(start_url, timeout=TIMEOUT)
            resp.raise_for_status()
            json_data = resp.json()

            if not json_data.get("success"):
                raise RuntimeError(f"Start profile failed: {json_data}")

            if not json_data.get("data"):
                raise RuntimeError(f"No data in start profile response: {json_data}")

            remote_debugging_address = json_data["data"]["remote_debugging_address"]
            driver_path = json_data["data"]["driver_path"]
            options = webdriver.ChromeOptions()
            options.debugger_address = remote_debugging_address
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            # Thêm driver vào tracking list
            with self.profile_lock:
                self.active_drivers.append(driver)

            driver.get("https://m.oklavip16.live/register?isIOSPure")

            # ===== ÁP DỤNG MOBILE EMULATION NGAY SAU KHI LOAD TRANG =====
            self.emulate_mobile_properties(driver, cfg)

            # ===== LẤY 1 FID + XÓA KHỎI FILE =====
            try:
                with open("fid.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if not lines:
                    self.log_signal.emit(f"[{cfg['name']}] ⚠️ fid.txt trống, bỏ qua bước FID")
                    fid = None
                else:
                    fid = lines[0].strip()
                    # Ghi lại file với các dòng còn lại
                    with open("fid.txt", "w", encoding="utf-8") as f:
                        f.writelines(lines[1:])

                if fid:
                    # ===== GHI FID VÀO localStorage + GẮN VÀO SRC =====
                    driver.execute_script("""
                        // lưu vào localStorage
                        localStorage.setItem('F-Id', arguments[0]);

                        // gắn fid vào src (nếu có)
                        let el = document.querySelector('[src]');
                        if (el) {
                            el.src = el.src + arguments[0];
                        }
                    """, fid)

                    # ===== (TÙY CHỌN) RELOAD ĐỂ ÁP DỤNG =====
                    driver.refresh()
                    # Áp dụng lại mobile emulation sau refresh
                    self.emulate_mobile_properties(driver, cfg)
                    self.mute_audio(driver, cfg)
                else:
                    self.mute_audio(driver, cfg)
            except Exception as e:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi xử lý FID (tiếp tục): {e}")
                self.mute_audio(driver, cfg)

            # Vòng lặp HOÀN CHỈNH: tạo thông tin mới và kiểm tra số điện thoại
            while self.running:
                self.log_signal.emit(f"[{cfg['name']}] \n🔄 Tạo thông tin đăng ký mới...")

                # Tạo thông tin đăng ký mới trong MỖI vòng lặp
                username = self.fill_random_username(driver, cfg)
                self.fill_passwords(driver, username, cfg)
                self.fill_email(driver, username, cfg)
                self.check_terms_checkbox(driver, cfg)

                self.log_signal.emit(f"[{cfg['name']}] 🔄 Điền số điện thoại đã có: {phone_number}")

                # Điền số điện thoại vào form
                if not self.fill_phone_number(driver, phone_number, cfg):
                    self.log_signal.emit(f"[{cfg['name']}] ❌ Không thể điền số điện thoại. Thoát chương trình.")
                    break

                # Click nút "Bước tiếp theo"
                if not self.click_next_step(driver, cfg):
                    self.log_signal.emit(f"[{cfg['name']}] ❌ Không thể click nút 'Bước tiếp theo'. Thoát chương trình.")
                    break

                # Chờ 2 giây để thông báo xuất hiện
                time.sleep(2)

                # Kiểm tra xem số điện thoại đã đăng ký chưa
                if self.check_phone_registered(driver, cfg):
                    # Nếu số đã được đăng ký, tải lại trang và lấy số mới nhưng KHÔNG đóng profile/driver.
                    self.log_signal.emit(f"[{cfg['name']}] 🔄 Số đã đăng ký. Reload trang, tạo thông tin mới và lấy số mới trong cùng profile...")

                    try:
                        driver.get("https://m.oklavip16.live/register?isIOSPure")  # Load lại trang từ đầu
                        # Áp dụng mobile emulation và tắt tiếng lại
                        try:
                            self.emulate_mobile_properties(driver, cfg)
                        except Exception:
                            pass
                        try:
                            self.mute_audio(driver, cfg)
                        except Exception:
                            pass
                        time.sleep(2)
                    except Exception as e:
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi khi reload trang: {e}. Sẽ đóng profile để an toàn.")
                        return

                    # Thử lấy số mới tại chỗ (không tạo profile mới). Nếu không có số, chờ 10s và thử lại.
                    new_phone = None
                    new_request_id = None
                    attempt = 0
                    while self.running and new_phone is None:
                        attempt += 1
                        self.log_signal.emit(f"[{cfg['name']}] 🔄 Lấy số mới tại chỗ (lần {attempt})...")
                        new_phone, new_request_id = self.get_phone_number(cfg)
                        if new_phone:
                            phone_number = new_phone
                            request_id = new_request_id
                            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã lấy số mới: {phone_number}. Tiếp tục điền thông tin trong cùng profile.")
                            break
                        else:
                            self.log_signal.emit(f"[{cfg['name']}] ⏳ Chưa có số mới, chờ 10 giây rồi thử lại...")
                            time.sleep(10)

                    # Nếu bị stop trong lúc chờ thì thoát
                    if not self.running:
                        self.log_signal.emit(f"[{cfg['name']}] ⏹️ Dừng do chương trình bị stop while waiting new phone")
                        return

                    # Nếu vẫn không lấy được số mới (vì lý do khác), thoát để worker_loop xử lý lại
                    if new_phone is None:
                        self.log_signal.emit(f"[{cfg['name']}] ❌ Không lấy được số mới trong profile này, thoát run_instance để thử lại.")
                        return

                    # Tiếp tục vòng lặp: lưu ý phone_number đã cập nhật, vòng while sẽ tiếp tục và tạo thông tin mới
                    continue

                # Nếu không có thông báo lỗi, kiểm tra đã chuyển sang registerStep chưa
                if self.check_register_step_url(driver, cfg):
                    self.log_signal.emit(f"[{cfg['name']}] 🎯 Đã chuyển sang trang OTP thành công!")

                    # Click nút "Gửi đi" và tự động giải captcha
                    if self.click_send_and_solve(driver, cfg):
                        self.log_signal.emit(f"[{cfg['name']}] ✅ Đã gửi OTP và giải captcha thành công!")

                        # Đã gửi OTP thành công, bắt đầu lấy OTP ngay lập tức
                        # (Không cần chờ toast "Gửi thành công" vì đã verify captcha thành công)
                        otp_started = True
                        self.log_signal.emit(f"[{cfg['name']}] 📨 Đã gửi OTP thành công, bắt đầu lấy OTP...")

                        # Biến để track trạng thái OTP
                        otp_received = False

                        # Nếu đã bắt đầu lấy OTP thì countdown
                        if otp_started:
                            self.log_signal.emit(f"[{cfg['name']}] 🔍 DEBUG: Vào countdown OTP")
                            self.log_signal.emit(f"[{cfg['name']}] 📱 Phone: {phone_number} | Request ID: {request_id}")

                            # Set timeout based on provider
                            provider = cfg.get("provider", "VIOTP")
                            otp_timeout = 130 if provider == "BOSSOTP" else 80
                            self.log_signal.emit(f"[{cfg['name']}] ⏱️ Bắt đầu đếm ngược {otp_timeout} giây chờ OTP...")

                            # Countdown từ timeout xuống 0
                            for remaining_time in range(otp_timeout, -1, -1):
                                if not self.running:
                                    break

                                provider = cfg.get("provider", "VIOTP")
                                get_code = None
                                try:
                                    if provider == "VIOTP":
                                        r = requests.get(f"https://api.viotp.com/session/getv2?requestId={request_id}&token={cfg['token_vio']}", timeout=10).json()
                                        get_code = r.get("data", {}).get("Code")
                                        self.log_signal.emit(f"[{cfg['name']}] 🔄 VIOTP OTP polled: {get_code} [{remaining_time}s còn lại]")
                                    else:
                                        token = cfg.get("boss_token") or ""
                                        check_url = f"https://bossotp.net/api/v4/rents/check?_id={request_id}&api_token={token}"
                                        r = requests.get(check_url, timeout=10).json()
                                        # BossOTP returns 'otp' field, extract number from sms_content if needed
                                        get_code = r.get("otp")
                                        if not get_code:
                                            # Try to extract OTP from sms_content (formats like "Mã OTP của bạn là: 123456")
                                            sms_content = r.get("sms_content", "")
                                            import re
                                            # Look for patterns like "123456", "OTP: 123456", "là: 123456", etc.
                                            otp_match = re.search(r'(?:OTP|otp|Mã|ma|là|:)[\s:]*(\d{4,6})', sms_content, re.IGNORECASE)
                                            if otp_match:
                                                get_code = otp_match.group(1)
                                            else:
                                                # Fallback: any 4-6 digit number
                                                otp_match = re.search(r'(\d{4,6})', sms_content)
                                                if otp_match:
                                                    get_code = otp_match.group(1)

                                        self.log_signal.emit(f"[{cfg['name']}] 🔄 BOSSOTP polled: {get_code} [{remaining_time}s còn lại] - status:{r.get('status')} - response:{r}")
                                except Exception as e:
                                    self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi khi poll OTP: {e}")

                                if get_code:
                                    # Điền OTP vào ô input
                                    otp_input = WebDriverWait(driver, 20).until(
                                        EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Hãy nhập mã xác nhận"]'))
                                    )
                                    otp_input.clear()
                                    otp_input.send_keys(get_code)
                                    self.log_signal.emit(f"[{cfg['name']}] ✅ Đã điền OTP: {get_code}")

                                    time.sleep(3)

                                    # Click nút "Đăng ký"
                                    register_button = WebDriverWait(driver, 15).until(
                                        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Đăng ký'] and not(contains(@class, 'disabled'))]"))
                                    )
                                    register_button.click()
                                    self.log_signal.emit(f"[{cfg['name']}] ✅ Đã click nút Đăng ký")

                                    time.sleep(3)

                                    # Lưu tài khoản vào file ACC.txt
                                    with open("ACC.txt", "a", encoding="utf-8") as f:
                                        f.write(f"{username}|{username}@\n")

                                    self.log_signal.emit(f"[{cfg['name']}] 💾 Đã lưu tài khoản: {username}|{username}@")
                                    self.stats_signal.emit('acc_success', 1)  # Tăng counter ACC tạo thành công
                                    # Cập nhật bộ đếm internal và kiểm tra target
                                    try:
                                        with self._created_lock:
                                            self._created_count += 1
                                            current_created = self._created_count
                                        if self.target_acc > 0 and current_created >= self.target_acc:
                                            self.log_signal.emit(f"[{cfg['name']}] 🎯 Đã đạt mục tiêu tạo {self.target_acc} acc — dừng tạo thêm.")
                                            # Đặt flag dừng, các worker loop sẽ thoát
                                            self.running = False
                                    except Exception:
                                        pass
                                    otp_received = True
                                    break

                                # Sleep 3 giây trước khi đếm tiếp (như user yêu cầu)
                                time.sleep(1)

                            # Nếu hết thời gian mà chưa có OTP
                            if not otp_received:
                                self.log_signal.emit(f"[{cfg['name']}] ⏰ OTP timeout - không nhận được mã trong {otp_timeout} giây")
                                self.log_signal.emit(f"[{cfg['name']}] 🚪 Đóng trình duyệt do hết thời gian chờ OTP")
                                break

                        if otp_received:
                            self.log_signal.emit(f"[{cfg['name']}] 🎉 Đăng ký thành công! Script hoàn thành.")
                            break
                        else:
                            self.log_signal.emit(f"[{cfg['name']}] ❌ Không thể hoàn tất đăng ký.OUT")
                            break

                    else:
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể gửi OTP hoặc giải captcha,OUT")
                        break

                else:
                    self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không xác định được trạng thái. Thử lại...")
                    time.sleep(2)

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] Lỗi: {e}")
        finally:
            try:
                if profile_id:
                    # Đóng profile qua API trước
                    try:
                        session = requests.Session()
                        session.headers.update(HEADERS)
                        close_url = f"{self.api_host}/api/v3/profiles/close/{profile_id}"
                        resp = session.get(close_url, timeout=10)
                        if resp.status_code == 200:
                            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã đóng profile {profile_id}")
                        else:
                            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể đóng profile {profile_id}")
                    except Exception as e:
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi đóng profile {profile_id}: {e}")

                    # Remove from tracking lists
                    with self.profile_lock:
                        if profile_id in self.active_profiles:
                            self.active_profiles.remove(profile_id)
                        if driver and driver in self.active_drivers:
                            self.active_drivers.remove(driver)
                    self.log_signal.emit(f"[{cfg['name']}] Removed profile {profile_id} from tracking")
            except Exception as e:
                self.log_signal.emit(f"[{cfg['name']}] Cleanup tracking exception: {e}")
            try:
                if driver:
                    driver.quit()
                    self.log_signal.emit(f"[{cfg['name']}] ✅ Đã đóng driver")
            except:
                pass

    # Copy các helper functions từ code gốc
    def get_phone_number(self, cfg):
        """Lấy số điện thoại ảo từ VIOTP"""
        try:
            provider = cfg.get("provider", "VIOTP")
            if provider == "VIOTP":
                network = cfg['network']
                if network == "ALL":
                    # Với VIOTP, thử từng network một (mở rộng danh sách theo yêu cầu)
                    networks_to_try = [
                        "MOBIFONE",
                        "VINAPHONE",
                        "VIETTEL",
                        "VIETNAMOBILE",
                        "ITELECOM",
                        "VODAFONE",
                        "WINTEL",
                        "METFONE",
                        "UNITEL",
                        "ETL",
                        "BEELINE",
                        "LAOTEL",
                        "GMOBILE",
                    ]
                else:
                    networks_to_try = [network]

                for try_network in networks_to_try:
                    self.log_signal.emit(f"[{cfg['name']}] 🔍 Thử network: {try_network}")

                    url = f"https://api.viotp.com/request/getv2?token={cfg['token_vio']}&serviceId={cfg['service_id']}&network={try_network}"
                    response = requests.get(url, timeout=10)
                    data = response.json()

                    self.log_signal.emit(f"[{cfg['name']}] 📱 VIOTP API Response ({try_network}): {data}")

                    if data.get('status_code') == 200:
                        phone_number = data['data']['phone_number']
                        request_id = data['data']['request_id']
                        self.log_signal.emit(f"[{cfg['name']}] ✅ Đã lấy số điện thoại (VIOTP - {try_network}): {phone_number}")
                        self.log_signal.emit(f"[{cfg['name']}] 📋 Request ID: {request_id}")
                        self.stats_signal.emit('phones_rented', 1)
                        return phone_number, request_id

                    # Nếu không phải lỗi hết số thì thử network khác
                    message = data.get('message', '')
                    if 'không có sẵn' not in message.lower():
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi {try_network}: {data}")
                        continue
                    else:
                        self.log_signal.emit(f"[{cfg['name']}] ⏳ Network {try_network} hết số, thử network khác...")

                # Nếu thử tất cả network mà vẫn không được
                self.log_signal.emit(f"[{cfg['name']}] ❌ Tất cả network VIOTP đều hết số khả dụng")
                return None, None
            else:
                # BOSSOTP flow
                token = cfg.get("boss_token") or ""
                if not token:
                    self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không có BOSSOTP token")
                    return None, None

                # Xử lý network selection
                network = cfg['network']
                if network == "ALL":
                    # Thử tất cả network tuần hoàn (mở rộng danh sách theo yêu cầu)
                    networks_to_try = [
                        "MOBIFONE",
                        "VINAPHONE",
                        "VIETTEL",
                        "VIETNAMOBILE",
                        "ITELECOM",
                        "VODAFONE",
                        "WINTEL",
                        "METFONE",
                        "UNITEL",
                        "ETL",
                        "BEELINE",
                        "LAOTEL",
                        "GMOBILE",
                    ]
                else:
                    networks_to_try = [network]

                for try_network in networks_to_try:
                    self.log_signal.emit(f"[{cfg['name']}] 🔍 Thử network: {try_network}")

                    url = f"https://bossotp.net/api/v4/rents/create?service_id={cfg['service_id']}&api_token={token}&network={try_network}"
                    try:
                        response = requests.get(url, timeout=10)
                        data = response.json()
                    except Exception as e:
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi network {try_network}: {e}")
                        continue

                    self.log_signal.emit(f"[{cfg['name']}] 📱 BOSSOTP API Response ({try_network}): {data}")

                    # Expected success returns rent_id and number
                    rent_id = data.get("rent_id") or data.get("data", {}).get("rent_id") or data.get("data", {}).get("rentId")
                    number = data.get("number") or data.get("data", {}).get("number")
                    if rent_id and number:
                        self.log_signal.emit(f"[{cfg['name']}] ✅ Đã lấy số điện thoại (BOSSOTP - {try_network}): {number}")
                        self.log_signal.emit(f"[{cfg['name']}] 📋 Rent ID: {rent_id}")
                        self.stats_signal.emit('phones_rented', 1)
                        return number, rent_id

                    # Nếu không phải lỗi "NO_NUMBER_AVAILABLE" thì thử network khác
                    error_msg = data.get('error') or data.get('code') or ''
                    if 'NO_NUMBER_AVAILABLE' not in error_msg:
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi {try_network}: {data}")
                        continue
                    else:
                        self.log_signal.emit(f"[{cfg['name']}] ⏳ Network {try_network} hết số, thử network khác...")

                # Nếu thử tất cả network mà vẫn không được
                self.log_signal.emit(f"[{cfg['name']}] ❌ Tất cả network đều hết số khả dụng")
                return None, None

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể lấy số điện thoại: {e}")
            return None, None

    def fill_phone_number(self, driver, phone_number, cfg):
        """Điền số điện thoại vào form"""
        if not phone_number:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không có số điện thoại để điền!")
            return False

        try:
            # Chờ và điền số điện thoại
            phone_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Nhập số điện thoại"]'))
            )
            phone_field.clear()
            phone_field.send_keys(phone_number)

            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã điền số điện thoại: {phone_number}")
            return True

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể điền số điện thoại: {e}")
            return False

    def click_next_step(self, driver, cfg):
        """Click nút 'Bước tiếp theo'"""
        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "van-button--primary") and .//span[contains(text(), "Bước tiếp theo")]]'))
            )
            next_button.click()
            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã click nút 'Bước tiếp theo'")
            return True

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể click nút 'Bước tiếp theo': {e}")
            return False

    def check_phone_registered(self, driver, cfg):
        """Kiểm tra xem số điện thoại đã đăng ký chưa"""
        try:
            # Chờ thông báo "Số điện thoại đã được đăng kí" xuất hiện trong 10 giây
            toast_message = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-popup__message"))
            )
               
            if toast_message:
                self.log_signal.emit(f"[{cfg['name']}] 📱 Số điện thoại đã được đăng ký - Cần tạo số mới")
                return True  # Số đã đăng ký

        except:
            pass  # Không có thông báo, tức là số điện thoại OK

        return False  # Số điện thoại chưa đăng ký

    def check_register_step_url(self, driver, cfg):
        """Kiểm tra xem đã chuyển sang trang registerStep chưa"""
        try:
            WebDriverWait(driver, 10).until(
                lambda d: "registerStep" in d.current_url
            )
            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã chuyển sang trang registerStep - Số điện thoại hợp lệ")
            return True

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Chưa chuyển sang trang registerStep: {e}")
            return False

    def click_send_and_solve(self, driver, cfg, retries=3, click_timeout=10):
        """
        FORCE click nút 'Gửi đi' (JS + mouse + touch) rồi xử lý captcha nếu xuất hiện
        """

        # ================= FORCE CLICK GỬI ĐI =================
        def force_click_gui_di(driver, timeout):
            end = time.time() + timeout

            js_click = r"""
            function clickGuiDi(){
                let el = [...document.querySelectorAll('span')]
                    .find(e => e.innerText && e.innerText.trim() === 'Gửi đi');

                if(!el){
                    el = document.evaluate(
                        "//span[normalize-space()='Gửi đi'] | //div[.//span[normalize-space()='Gửi đi']] | //button[.//span[normalize-space()='Gửi đi']]",
                        document, null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;
                }

                if(!el) return false;

                el.scrollIntoView({block:'center', behavior:'instant'});
                el.style.pointerEvents = 'auto';
                el.disabled = false;

                // mouse events
                el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
                el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
                el.dispatchEvent(new MouseEvent('click', {bubbles:true}));

                // touch events (mobile)
                try{
                    el.dispatchEvent(new TouchEvent('touchstart', {bubbles:true}));
                    el.dispatchEvent(new TouchEvent('touchend', {bubbles:true}));
                }catch(e){}

                return true;
            }
            return clickGuiDi();
            """

            while time.time() < end:
                try:
                    ok = driver.execute_script(js_click)
                    if ok:
                        self.log_signal.emit(f"[{cfg['name']}] 🔥 FORCE CLICK 'Gửi đi' thành công")
                        return True
                except Exception:
                    pass
                time.sleep(0.3)

            self.log_signal.emit(f"[{cfg['name']}] ❌ FORCE CLICK 'Gửi đi' thất bại")
            return False

        # ================= THỰC HIỆN CLICK =================
        if not force_click_gui_di(driver, click_timeout):
            return False

        # ================= CHỜ CAPTCHA (NẾU CÓ) =================
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".geetest_box_img_noops, .geetest_item, .geetest_panel")
                )
            )
            self.log_signal.emit(f"[{cfg['name']}] 🔐 Captcha xuất hiện, bắt đầu giải...")
        except Exception:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thấy captcha sau 20 giây → Lỗi gửi OTP, cần tạo profile mới")
            return False  # Trả về False để tạo profile mới

        # ================= GIẢI CAPTCHA =================
        for attempt in range(retries):
            try:
                solved = self.solve_geetest_match(driver, cfg, timeout=6)
            except Exception as e:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi solver: {e}")
                solved = False

            if solved:
                self.log_signal.emit(f"[{cfg['name']}] ✅ Captcha đã được giải thành công.")

                # ===== CHECK NÚT GỬI ĐI SAU KHI GIẢI CAPTCHA THÀNH CÔNG =====
                self.log_signal.emit(f"[{cfg['name']}] ⏳ Chờ 5 giây để kiểm tra nút 'Gửi đi'...")
                time.sleep(5)

                # Kiểm tra xem nút "Gửi đi" có text là "Gửi đi" không
                try:
                    gui_di_button = driver.execute_script("""
                        let el = [...document.querySelectorAll('span')]
                            .find(e => e.innerText && e.innerText.trim() === 'Gửi đi');

                        if(!el){
                            el = document.evaluate(
                                "//span[normalize-space()='Gửi đi'] | //div[.//span[normalize-space()='Gửi đi']] | //button[.//span[normalize-space()='Gửi đi']]",
                                document, null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                null
                            ).singleNodeValue;
                        }

                        return el ? el.innerText.trim() : null;
                    """)

                    if gui_di_button == "Gửi đi":
                        self.log_signal.emit(f"[{cfg['name']}] ⚠️ Nút 'Gửi đi' vẫn hiển thị - có thể bị rate limit!")
                        self.log_signal.emit(f"[{cfg['name']}] 🚪 Đóng trình duyệt để tránh spam...")
                        return False  # Trả về False để tạo profile mới
                    else:
                        self.log_signal.emit(f"[{cfg['name']}] ✅ Nút đã thay đổi, tiếp tục gửi OTP...")

                except Exception as e:
                    self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi kiểm tra nút: {e}")

                return True

            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Giải captcha thất bại lần {attempt+1}, refresh và thử lại...")

            # refresh captcha nếu có
            try:
                refresh = driver.find_element(By.CSS_SELECTOR, ".geetest_refresh")
                driver.execute_script("arguments[0].click();", refresh)
            except Exception:
                pass

            time.sleep(1.0)

        self.log_signal.emit(f"[{cfg['name']}] ❌ Không giải được captcha sau nhiều lần thử.")
        return False

    def solve_geetest_match(self, driver, cfg, timeout=8):
        """
        Giải captcha dạng 'Nhấp và hoán đổi để sắp hàng ba mục giống nhau liên tiếp'.
        Thuật toán:
          - Lấy danh sách 9 tile (theo order DOM)
          - Lấy background-image URL của mỗi tile
          - Thử hoán vị (swap) mọi cặp tile (i,j); nếu sau swap có dòng hoặc cột 3 ảnh giống nhau thì click hai tile đó để hoán đổi
        Trả về True nếu tìm và click swap thành công, False otherwise.
        """
        try:
            # Chờ captcha hiển thị
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".geetest_box_img_noops, .geetest_item"))
            )
        except Exception:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thấy captcha match xuất hiện.")
            return False

        try:
            # Lấy các element tile (DOM order)
            tiles = driver.find_elements(By.CSS_SELECTOR, ".geetest_item")
            if len(tiles) < 9:
                # thử lấy theo selector khác nếu cần
                tiles = driver.find_elements(By.CSS_SELECTOR, ".geetest_item_box_0_0, .geetest_item_box_0_1, .geetest_item_box_0_2, .geetest_item_box_1_0, .geetest_item_box_1_1, .geetest_item_box_1_2, .geetest_item_box_2_0, .geetest_item_box_2_1, .geetest_item_box_2_2")

            # Lấy URL ảnh cho mỗi tile
            imgs = []
            for el in tiles:
                # ưu tiên lấy computed style backgroundImage
                img = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundImage;", el)
                if not img:
                    img = el.get_attribute("style") or ""
                # Chuẩn hóa: url("...") -> ...
                if isinstance(img, str):
                    img = img.strip()
                    if img.startswith("url("):
                        img = img[4:].strip().strip('"').strip("'").strip(')')
                imgs.append(img)

            # Nếu không đủ 9 ảnh, abort
            if len(imgs) < 9:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không lấy đủ ảnh ({len(imgs)}).")
                return False

            # Helper: kiểm tra pattern 3 giống nhau trên hàng hoặc cột
            def has_three_in_line(arr):
                # arr là list length 9
                # hàng
                for r in range(3):
                    if arr[r*3] and arr[r*3] == arr[r*3+1] == arr[r*3+2]:
                        return True
                # cột
                for c in range(3):
                    if arr[c] and arr[c] == arr[c+3] == arr[c+6]:
                        return True
                return False

            # Thử swap mọi cặp (i<j)
            n = len(imgs)
            for i in range(n):
                for j in range(i+1, n):
                    trial = imgs.copy()
                    trial[i], trial[j] = trial[j], trial[i]
                    if has_three_in_line(trial):
                        # Click hai tile để hoán đổi (delay nhỏ giữa các click)
                        try:
                            tiles[i].click()
                            time.sleep(0.25)
                            tiles[j].click()
                            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã click swap tiles {i} <-> {j} để ghép 3 ảnh.")
                            # chờ kết quả captcha xử lý
                            time.sleep(1.2)
                            return True
                        except Exception as e:
                            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi khi click swap: {e}")
                            return False

            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không tìm được cặp swap nào tạo thành 3 ảnh giống nhau.")
            return False

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi khi giải captcha: {e}")
            return False

    def emulate_mobile_properties(self, driver, cfg):
        """Emulate mobile device properties để làm web chân thực như phone"""
        try:
            driver.execute_script("""
                // ===== MOBILE VIEWPORT EMULATION =====
                // Fake screen dimensions cho iPhone
                Object.defineProperty(screen, 'width', {value: 375, configurable: true});
                Object.defineProperty(screen, 'height', {value: 667, configurable: true});
                Object.defineProperty(screen, 'availWidth', {value: 375, configurable: true});
                Object.defineProperty(screen, 'availHeight', {value: 647, configurable: true}); // Minus status bar

                // Fake window dimensions
                Object.defineProperty(window, 'innerWidth', {value: 375, writable: true});
                Object.defineProperty(window, 'innerHeight', {value: 667, writable: true});
                Object.defineProperty(window, 'outerWidth', {value: 375, writable: true});
                Object.defineProperty(window, 'outerHeight', {value: 667, writable: true});

                // Fake device pixel ratio
                Object.defineProperty(window, 'devicePixelRatio', {value: 2.0, configurable: true});

                // ===== TOUCH CAPABILITIES =====
                // Fake touch support
                Object.defineProperty(navigator, 'maxTouchPoints', {value: 5, configurable: true});
                Object.defineProperty(navigator, 'ontouchstart', {value: null, configurable: true});
                Object.defineProperty(navigator, 'ontouchend', {value: null, configurable: true});
                Object.defineProperty(navigator, 'ontouchmove', {value: null, configurable: true});

                // Add touch event simulation
                let touchEvents = ['touchstart', 'touchend', 'touchmove'];
                touchEvents.forEach(eventType => {
                    document.addEventListener(eventType, function(e) {
                        // Prevent default mouse events when touch is present
                        e.preventDefault();
                    }, {passive: false});
                });

                // ===== DEVICE ORIENTATION =====
                // Fake orientation API
                Object.defineProperty(screen, 'orientation', {
                    value: {
                        angle: 0,
                        type: 'portrait-primary',
                        onchange: null
                    },
                    configurable: true
                });

                // Add orientation change event
                let orientationChangeEvent = new Event('orientationchange');
                window.addEventListener('orientationchange', function() {
                    // Swap dimensions when rotating
                    if (screen.orientation.angle === 90) {
                        Object.defineProperty(screen, 'width', {value: 667});
                        Object.defineProperty(screen, 'height', {value: 375});
                        Object.defineProperty(window, 'innerWidth', {value: 667});
                        Object.defineProperty(window, 'innerHeight', {value: 375});
                    } else {
                        Object.defineProperty(screen, 'width', {value: 375});
                        Object.defineProperty(screen, 'height', {value: 667});
                        Object.defineProperty(window, 'innerWidth', {value: 375});
                        Object.defineProperty(window, 'innerHeight', {value: 667});
                    }
                });

                // ===== MOBILE-SPECIFIC APIs =====
                // Fake vibration API
                navigator.vibrate = function(pattern) {
                    console.log('Mobile vibration simulated:', pattern);
                    return true;
                };

                // Fake battery API
                if (!navigator.getBattery) {
                    navigator.getBattery = function() {
                        return Promise.resolve({
                            charging: true,
                            chargingTime: Infinity,
                            dischargingTime: Infinity,
                            level: 0.85,
                            addEventListener: function() {},
                            removeEventListener: function() {}
                        });
                    };
                }

                // Fake media capabilities
                if (!navigator.mediaCapabilities) {
                    navigator.mediaCapabilities = {
                        decodingInfo: function() {
                            return Promise.resolve({
                                supported: true,
                                smooth: true,
                                powerEfficient: true
                            });
                        }
                    };
                }

                // ===== MOBILE NAVIGATOR PROPERTIES =====
                // Override navigator properties to look more mobile
                Object.defineProperty(navigator, 'platform', {value: 'iPhone', configurable: true});
                Object.defineProperty(navigator, 'product', {value: 'iPhone', configurable: true});
                Object.defineProperty(navigator, 'hardwareConcurrency', {value: 2, configurable: true});

                // Fake WebGL properties
                let canvas = document.createElement('canvas');
                let gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    let debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        // Fake mobile GPU info
                        gl.getParameter = (function(original) {
                            return function(parameter) {
                                if (parameter === debugInfo.UNMASKED_RENDERER_WEBGL) {
                                    return 'Apple A15 GPU';
                                }
                                if (parameter === debugInfo.UNMASKED_VENDOR_WEBGL) {
                                    return 'Apple Inc.';
                                }
                                return original.call(this, parameter);
                            };
                        })(gl.getParameter);
                    }
                }

                // ===== MOBILE CSS MEDIA QUERIES =====
                // Force mobile viewport meta tag if not present
                let viewport = document.querySelector('meta[name="viewport"]');
                if (!viewport) {
                    viewport = document.createElement('meta');
                    viewport.name = 'viewport';
                    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
                    document.head.appendChild(viewport);
                }

                // ===== FAKE MOBILE TIMING =====
                // Override performance timing to look more mobile
                if (window.performance && window.performance.timing) {
                    // Fake some timing values to look like mobile browser
                    let timing = window.performance.timing;
                    timing.domContentLoadedEventEnd = timing.domContentLoadedEventStart + 150;
                    timing.loadEventEnd = timing.loadEventStart + 300;
                }

                console.log('Mobile emulation applied successfully');
            """)

            self.log_signal.emit(f"[{cfg['name']}] 📱 Đã áp dụng mobile emulation - web giờ chân thực như phone!")

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi áp dụng mobile emulation: {e}")

    def mute_audio(self, driver, cfg):
        driver.execute_script("""
            document.querySelectorAll('audio, video').forEach(e => e.muted = true);
            setInterval(() => {
                document.querySelectorAll('audio, video').forEach(e => {
                    if (!e.muted) e.muted = true;
                });
            }, 300);
        """)
        self.log_signal.emit(f"[{cfg['name']}] ✅ Đã tắt tiếng trang web thành công!")

    def fill_random_username(self, driver, cfg):
        try:
            # Tạo username ngẫu nhiên: 8 chữ cái + 3 số
            letters = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8))
            numbers = ''.join(random.choice('0123456789') for _ in range(3))
            username = letters + numbers

            # Chờ element xuất hiện (tối đa 20 giây)
            username_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "van-field-1-input"))
            )

            # Xóa nội dung cũ và điền username mới
            # Dùng JS để gán trực tiếp tránh trường hợp send_keys append lỗi
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", username_field, username)

            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã điền username: {username}")
            return username

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể điền username: {e}")
            return None

    def fill_passwords(self, driver, username, cfg):
        if not username:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không có username để tạo mật khẩu!")
            return

        try:
            # Tạo mật khẩu = username + "@"
            password = username + "@"

            # Chờ và lấy element mật khẩu (van-field-2-input)
            password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "van-field-2-input"))
            )
            # Gán giá trị trực tiếp bằng JS để tránh append hay lỗi focus
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", password_field, password)

            # Chờ và lấy element xác nhận mật khẩu (van-field-3-input)
            confirm_password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "van-field-3-input"))
            )
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", confirm_password_field, password)

            # Xác thực lại trong DOM rằng giá trị đã được gán đúng
            actual_pwd = driver.execute_script("return document.getElementById('van-field-2-input').value;")
            actual_confirm = driver.execute_script("return document.getElementById('van-field-3-input').value;")
            if actual_pwd != password or actual_confirm != password:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi khi gán mật khẩu (pwd='{actual_pwd}' confirm='{actual_confirm}'), thử lại bằng send_keys.")
                password_field.clear()
                password_field.send_keys(password)
                confirm_password_field.clear()
                confirm_password_field.send_keys(password)

            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã điền mật khẩu: {password}")
            return password

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể điền mật khẩu: {e}")
            return None

    def fill_email(self, driver, username, cfg):
        if not username:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không có username để tạo email!")
            return

        try:
            # Tạo email = username + "@gmail.com"
            email = username + "@gmail.com"

            # Chờ và điền email (van-field-5-input)
            email_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "van-field-5-input"))
            )
            # Gán trực tiếp bằng JS để tránh trường hợp append hoặc duplicated input
            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", email_field, email)

            # Kiểm tra lại giá trị trong DOM, nếu không đúng thì fallback về send_keys
            actual_email = driver.execute_script("return document.getElementById('van-field-5-input').value;")
            if actual_email != email:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Email sau khi gán không đúng ('{actual_email}'), thử lại bằng send_keys.")
                email_field.clear()
                email_field.send_keys(email)

            self.log_signal.emit(f"[{cfg['name']}] ✅ Đã điền email: {email}")
            return email

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể điền email: {e}")
            return None

    def check_terms_checkbox(self, driver, cfg):
        try:
            # Chờ và click vào checkbox chấp nhận điều khoản
            # Tìm element checkbox theo class hoặc text
            checkbox = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".van-checkbox[role='checkbox']"))
            )

            # Kiểm tra xem đã được check chưa
            if not checkbox.get_attribute("aria-checked") == "true":
                checkbox.click()
                self.log_signal.emit(f"[{cfg['name']}] ✅ Đã tick checkbox chấp nhận điều khoản")
            else:
                self.log_signal.emit(f"[{cfg['name']}] ✅ Checkbox đã được tick sẵn")

            return True

        except Exception as e:
            self.log_signal.emit(f"[{cfg['name']}] ⚠️ Không thể tick checkbox: {e}")
            return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        # Thống kê
        self.stats = {
            'acc_success': 0,  # ACC tạo thành công
            'phones_rented': 0  # Tổng số đã thuê
        }
        # Trạng thái dừng
        self.is_stopping = False
        self.stop_timer = QTimer()
        self.stop_timer.timeout.connect(self.on_stop_timeout)
        self.init_ui()

    def on_provider_changed(self):
        """Ẩn/hiện input fields dựa trên provider được chọn"""
        provider = self.common_provider_combo.currentText()

        if provider == "VIOTP":
            # Hiện VIOTP inputs, ẩn BOSSOTP
            for i in range(self.viotp_row.count()):
                widget = self.viotp_row.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.boss_row.count()):
                widget = self.boss_row.itemAt(i).widget()
                if widget:
                    widget.hide()
        elif provider == "BOSSOTP":
            # Hiện BOSSOTP inputs, ẩn VIOTP
            for i in range(self.viotp_row.count()):
                widget = self.viotp_row.itemAt(i).widget()
                if widget:
                    widget.hide()
            for i in range(self.boss_row.count()):
                widget = self.boss_row.itemAt(i).widget()
                if widget:
                    widget.show()

    def init_ui(self):
        self.setWindowTitle("Reg Đa Luồng + GPM GUI v9 - Ultimate Edition")
        self.setGeometry(100, 100, int(500 * UI_SCALE), int(300 * UI_SCALE))

        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout chính
        main_layout = QVBoxLayout(central_widget)

        # === COMMON SETTINGS ===
        common_group = QGroupBox("⚙️ Cài đặt chung (áp dụng cho tất cả luồng)")
        common_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: rgba(76, 175, 80, 0.1);
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #81C784;
            }
        """)
        common_layout = QVBoxLayout(common_group)

        # Row 1: Provider Selection
        provider_row = QHBoxLayout()
        provider_row.addWidget(QLabel("🏪 Provider:"))
        self.common_provider_combo = QComboBox()
        self.common_provider_combo.addItems(["VIOTP", "BOSSOTP"])
        self.common_provider_combo.setCurrentText("VIOTP")
        self.common_provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_row.addWidget(self.common_provider_combo)
        provider_row.addStretch()
        common_layout.addLayout(provider_row)

        # Row 2: VIOTP Settings
        self.viotp_row = QHBoxLayout()
        self.viotp_row.addWidget(QLabel("VIOTP Token:"))
        self.common_token_input = QLineEdit("b5f70a870ef8437ab55b8e98968bc215")
        self.common_token_input.setPlaceholderText("Token API VIOTP")
        self.common_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.viotp_row.addWidget(self.common_token_input)

        self.viotp_row.addWidget(QLabel("Service ID:"))
        self.common_service_input = QLineEdit("841")
        self.common_service_input.setPlaceholderText("841")
        self.viotp_row.addWidget(self.common_service_input)
        common_layout.addLayout(self.viotp_row)

        # Row 3: BOSSOTP Settings
        self.boss_row = QHBoxLayout()
        self.boss_row.addWidget(QLabel("BOSSOTP Token:"))
        self.common_boss_token_input = QLineEdit("")
        self.common_boss_token_input.setPlaceholderText("API Token BOSSOTP (sk_...)")
        self.common_boss_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.boss_row.addWidget(self.common_boss_token_input)

        self.boss_row.addWidget(QLabel("Service ID:"))
        self.common_boss_service_input = QLineEdit("66650e049255470ed6f92ed4")
        self.common_boss_service_input.setPlaceholderText("66650e049255470ed6f92ed4 (OTP OKVIP)")
        self.boss_row.addWidget(self.common_boss_service_input)

        common_layout.addLayout(self.boss_row)

        # Row 2: Network
        common_row2 = QHBoxLayout()
        common_row2.addWidget(QLabel("Network:"))
        self.common_network_combo = QComboBox()
        # Network options cho cả VIOTP và BOSSOTP
        networks = [
            "ALL",
            "MOBIFONE",
            "VINAPHONE",
            "VIETTEL",
            "VIETNAMOBILE",
            "ITELECOM",
            "VODAFONE",
            "WINTEL",
            "METFONE",
            "UNITEL",
            "ETL",
            "BEELINE",
            "LAOTEL",
            "GMOBILE",
        ]
        self.common_network_combo.addItems(networks)
        self.common_network_combo.setCurrentText("ALL")  # Mặc định chọn ALL
        self.common_network_combo.setCurrentText("MOBIFONE")
        common_row2.addWidget(self.common_network_combo)
        common_row2.addStretch()

        # Balance / refresh controls
        balance_row = QHBoxLayout()
        self.balance_label = QLabel("Túi tiền OTP: Chưa kiểm tra")
        balance_row.addWidget(self.balance_label)
        self.refresh_balance_btn = QPushButton("🔄 Refresh Balance")
        self.refresh_balance_btn.clicked.connect(self.update_balance)
        balance_row.addWidget(self.refresh_balance_btn)
        common_layout.addLayout(balance_row)

        common_layout.addLayout(common_row2)

        # Initialize provider selection
        self.on_provider_changed()

        main_layout.addWidget(common_group)

        # === API HOST & KEYS ===
        api_keys_group = QGroupBox("🌐 API & Keys")
        api_keys_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: rgba(33, 150, 243, 0.1);
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #64B5F6;
            }
        """)
        api_keys_layout = QVBoxLayout(api_keys_group)

        # API Host row
        api_row = QHBoxLayout()
        api_row.addWidget(QLabel("API Host:"))
        self.api_host_input = QLineEdit(DEFAULT_API_HOST)
        self.api_host_input.setPlaceholderText("http://127.0.0.1:19053")
        api_row.addWidget(self.api_host_input)

        api_keys_layout.addLayout(api_row)

        # KEYS text area
        keys_layout = QVBoxLayout()
        keys_layout.addWidget(QLabel("Kito Proxy Keys (mỗi key 1 dòng):"))
        self.keys_text = QTextEdit()
        self.keys_text.setPlainText("")  # Will be loaded from config
        self.keys_text.setFont(QFont("Consolas", int(9 * UI_SCALE)))
        self.keys_text.setMaximumHeight(int(150 * UI_SCALE))
        keys_layout.addWidget(self.keys_text)

        api_keys_layout.addLayout(keys_layout)

        # === API KEYS | INDIVIDUAL CONFIGS (Side by side) ===
        api_configs_layout = QHBoxLayout()

        # Left side: API & Keys
        api_configs_layout.addWidget(api_keys_group)

        # Right side: Individual Configs
        configs_group = QGroupBox("🎯 Cấu hình riêng từng luồng")
        configs_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: rgba(76, 175, 80, 0.1);
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #81C784;
            }
        """)
        configs_layout = QVBoxLayout(configs_group)

        # Header với controls
        configs_header = QHBoxLayout()
        configs_header.addWidget(QLabel("📋 Configs:"))

        # Buttons for config management
        self.add_config_btn = QPushButton("➕ Add Config")
        self.add_config_btn.clicked.connect(lambda: self.add_config_form())
        self.add_config_btn.setToolTip("Thêm config mới với key index và vị trí tự động")

        self.clear_configs_btn = QPushButton("🗑️ Clear All")
        self.clear_configs_btn.clicked.connect(self.clear_all_configs)
        self.clear_configs_btn.setToolTip("Xóa tất cả configs")

        self.reset_layout_btn = QPushButton("🔄 Reset Layout")
        self.reset_layout_btn.clicked.connect(self.reset_window_layout)
        self.reset_layout_btn.setToolTip("Reset tất cả vị trí cửa sổ về layout tự động (9 luồng/hàng)")

        configs_header.addWidget(self.add_config_btn)
        configs_header.addWidget(self.clear_configs_btn)
        configs_header.addWidget(self.reset_layout_btn)
        configs_header.addStretch()
        configs_layout.addLayout(configs_header)

        # Scroll area for configs
        self.configs_scroll = QScrollArea()
        self.configs_scroll.setWidgetResizable(True)
        self.configs_scroll.setStyleSheet("""
            QScrollArea {
                background-color: rgba(35, 35, 35, 0.9);
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        self.configs_container = QWidget()
        self.configs_container.setStyleSheet("background-color: transparent;")
        self.configs_layout_inner = QVBoxLayout(self.configs_container)
        self.configs_scroll.setWidget(self.configs_container)
        self.configs_scroll.setMinimumHeight(int(200 * UI_SCALE))

        configs_layout.addWidget(self.configs_scroll)
        api_configs_layout.addWidget(configs_group)

        # Set stretch factors để cân bằng
        api_configs_layout.setStretchFactor(api_keys_group, 1)
        api_configs_layout.setStretchFactor(configs_group, 2)

        main_layout.addLayout(api_configs_layout)

        # Hidden text area for JSON (used internally)
        self.configs_text = QTextEdit()
        self.configs_text.setPlainText("")
        self.configs_text.hide()  # Hide from UI but keep for compatibility

        # Load default configs into form
        self.load_default_configs()

        # Header với các settings ở góc phải
        header_layout = QHBoxLayout()

        # Stats labels
        stats_layout = QVBoxLayout()
        self.acc_success_label = QLabel("✅ ACC TẠO THÀNH CÔNG: 0")
        self.acc_success_label.setStyleSheet(f"color: #4CAF50; font-weight: bold; font-size: {int(12 * UI_SCALE)}px;")
        stats_layout.addWidget(self.acc_success_label)

        self.phones_rented_label = QLabel("📞 TỔNG SỐ ĐÃ THUÊ: 0")
        self.phones_rented_label.setStyleSheet(f"color: #FF9800; font-weight: bold; font-size: {int(12 * UI_SCALE)}px;")
        stats_layout.addWidget(self.phones_rented_label)

        # Browser version input
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(QLabel("Browser Version:"))
        self.browser_version_input = QLineEdit(DEFAULT_BROWSER_VERSION)
        self.browser_version_input.setFont(QFont("Consolas", int(9 * UI_SCALE)))
        self.browser_version_input.setPlaceholderText("129.0.6668.59")
        self.browser_version_input.setFixedWidth(int(150 * UI_SCALE))
        browser_layout.addWidget(self.browser_version_input)

        # Target accounts input
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel("Target ACC (0 = no limit):"))
        self.target_acc_input = QSpinBox()
        self.target_acc_input.setRange(0, 1000000)
        self.target_acc_input.setValue(0)
        self.target_acc_input.setFixedWidth(int(120 * UI_SCALE))
        self.target_acc_input.setToolTip("Số lượng ACC muốn tạo. 0 = không giới hạn")
        target_layout.addWidget(self.target_acc_input)
        header_layout.addLayout(target_layout)

        # Balance controls
        balance_controls = QHBoxLayout()
        self.balance_label = QLabel("Túi tiền OTP: Đang tải...")
        self.balance_label.setStyleSheet(f"""
            QLabel {{
                color: #FFD700;
                font-weight: bold;
                font-size: {int(14 * UI_SCALE)}px;
                padding: {int(5 * UI_SCALE)}px {int(10 * UI_SCALE)}px;
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 5px;
            }}
        """)
        self.balance_label.setFixedHeight(int(30 * UI_SCALE))
        balance_controls.addWidget(self.balance_label)

        # Nút check số dư
        self.check_balance_btn = QPushButton("🔄")
        self.check_balance_btn.setToolTip("Check số dư ngay lập tức")
        self.check_balance_btn.setFixedSize(int(30 * UI_SCALE), int(30 * UI_SCALE))
        self.check_balance_btn.clicked.connect(self.update_balance)
        balance_controls.addWidget(self.check_balance_btn)

        header_layout.addLayout(stats_layout)
        header_layout.addLayout(browser_layout)
        header_layout.addLayout(balance_controls)
        main_layout.addLayout(header_layout)

        # Buttons row
        buttons_layout = QHBoxLayout()

        self.start_button = QPushButton("▶️ Bắt đầu")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(14 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.start_button.clicked.connect(self.start_worker)

        self.stop_button = QPushButton("⏹️ Dừng")
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(14 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #da190b;
            }}
        """)
        self.stop_button.clicked.connect(self.stop_worker)
        self.stop_button.setEnabled(True)  # Always enabled now

        self.open_acc_button = QPushButton("📂 Mở File ACC")
        self.open_acc_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(14 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        self.open_acc_button.clicked.connect(self.open_acc_file)

        self.reset_stats_button = QPushButton("🔄 Reset Stats")
        self.reset_stats_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #9C27B0;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(14 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7B1FA2;
            }}
        """)
        self.reset_stats_button.clicked.connect(self.reset_stats)

        # Single horizontal row for all function buttons (compact)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.open_acc_button)
        self.check_proxy_btn = QPushButton("🔍 Check PROXY")
        buttons_layout.addWidget(self.check_proxy_btn)
        self.check_proxy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FF9800;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(12 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F57C00;
            }}
        """)
        self.check_proxy_btn.setToolTip("Check thông tin proxy từ key đầu tiên")
        self.check_proxy_btn.clicked.connect(self.check_proxy_info)

        self.check_all_proxy_btn = QPushButton("🔍 Check All PROXY")
        buttons_layout.addWidget(self.check_all_proxy_btn)
        self.check_all_proxy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FF6B35;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(12 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E55A2B;
            }}
        """)
        self.check_all_proxy_btn.setToolTip("Check thông tin proxy từ tất cả keys")
        self.check_all_proxy_btn.clicked.connect(self.check_all_proxy_info)

        # Save config button (ensure it's created before adding)
        self.save_config_btn = QPushButton("💾 Lưu cấu hình")
        self.save_config_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(12 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.save_config_btn.clicked.connect(self.save_configuration)
        buttons_layout.addWidget(self.save_config_btn)
        buttons_layout.addWidget(self.reset_stats_button)

        # Clear log button (added to the controls row)
        self.clear_log_btn = QPushButton("🧹 Xóa Log")
        self.clear_log_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #607D8B;
                color: white;
                padding: {int(10 * UI_SCALE)}px {int(20 * UI_SCALE)}px;
                border: none;
                border-radius: 5px;
                font-size: {int(12 * UI_SCALE)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #546E7A;
            }}
        """)
        self.clear_log_btn.setToolTip("Xóa toàn bộ nội dung log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        buttons_layout.addWidget(self.clear_log_btn)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # LOG area (enlarged)
        log_layout = QVBoxLayout()
        header_h = QHBoxLayout()
        header_h.addWidget(QLabel("📋 LOG:"))
        header_h.addStretch()
        log_layout.addLayout(header_h)
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 12))
        self.log_text.setReadOnly(True)
        # Make log area larger and styled
        self.log_text.setMinimumHeight(380)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #333;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)
        main_layout.addLayout(log_layout)

        # (History table removed)

        # Timer để cập nhật số dư mỗi 5 giây
        self.balance_timer = QTimer()
        self.balance_timer.timeout.connect(self.update_balance)
        self.balance_timer.start(5000)  # 5 giây

        # Đặt màu nền tối cho log
        palette = self.log_text.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 200))
        self.log_text.setPalette(palette)

        # Load saved configuration (must be called after creating all UI elements)
        self.load_configuration()

        # Cập nhật số dư lần đầu
        self.update_balance()

    def load_default_configs(self):
        """Load default configs into form interface"""
        # Create one default config
        default_config = {
            "name": "Luồng 1",
            "kito_key_index": 0,
            "win_pos": [0, 0]
        }
        self.add_config_form(config_data=default_config)

    def add_config_form(self, config_data=None):
        """Add a new config form"""
        if config_data is None or not isinstance(config_data, dict):
            # Tự động tính toán key_index và window position
            current_count = len(self.get_all_configs())

            # Tính window position tự động (9 configs per row)
            win_x = (current_count % 9) * 500  # 0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000
            win_y = (current_count // 9) * 1000  # Tăng Y mỗi 9 configs

            config_data = {
                "name": f"Luồng {current_count + 1}",
                "kito_key_index": current_count,  # Tự động điền index theo thứ tự
                "win_pos": [win_x, win_y]
            }

        # Create config group box
        group = QGroupBox(f"Config {len(self.get_all_configs()) + 1}")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: rgba(68, 68, 68, 0.8);
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #BBB;
            }
        """)

        # Single row layout - tất cả controls trên 1 hàng
        row_layout = QHBoxLayout(group)

        # Name input
        row_layout.addWidget(QLabel("📋 Name:"))
        name_input = QLineEdit(config_data.get("name", ""))
        name_input.setPlaceholderText("Luồng 1")
        name_input.setMaximumWidth(120)
        row_layout.addWidget(name_input)

        # Key Index
        row_layout.addWidget(QLabel("🔑 Key:"))
        key_index = QSpinBox()
        key_index.setRange(0, 20)
        key_index.setValue(config_data.get("kito_key_index", 0))
        key_index.setMaximumWidth(80)
        row_layout.addWidget(key_index)

        # Window Position
        row_layout.addWidget(QLabel("📍 X:"))
        win_x = QSpinBox()
        win_x.setRange(0, 5000)
        win_x.setValue(config_data.get("win_pos", [0, 0])[0])
        win_x.setMaximumWidth(100)
        win_x.setToolTip("Vị trí ngang của cửa sổ browser")
        row_layout.addWidget(win_x)

        row_layout.addWidget(QLabel("Y:"))
        win_y = QSpinBox()
        win_y.setRange(0, 5000)
        win_y.setValue(config_data.get("win_pos", [0, 0])[1])
        win_y.setMaximumWidth(100)
        win_y.setToolTip("Vị trí dọc của cửa sổ browser")
        row_layout.addWidget(win_y)

        # Position preview
        preview_label = QLabel(f"📍 ({win_x.value()}, {win_y.value()})")
        preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(76, 175, 80, 0.2);
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: {int(2 * UI_SCALE)}px {int(8 * UI_SCALE)}px;
                color: #4CAF50;
                font-weight: bold;
                font-size: {int(11 * UI_SCALE)}px;
            }}
        """)
        preview_label.setMaximumWidth(120)

        # Connect spinbox changes to update preview
        def update_preview():
            preview_label.setText(f"📍 ({win_x.value()}, {win_y.value()})")

        win_x.valueChanged.connect(update_preview)
        win_y.valueChanged.connect(update_preview)

        row_layout.addWidget(preview_label)

        # Auto-layout info button
        info_btn = QPushButton("ℹ️ Auto")
        info_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: {int(2 * UI_SCALE)}px {int(8 * UI_SCALE)}px;
                font-size: {int(10 * UI_SCALE)}px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        info_btn.setToolTip("Tự động: 9 luồng/hàng, mỗi luồng cách 500px, hàng cách 1000px")
        info_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Auto Layout Info",
            "🎯 Layout tự động:\n"
            "• 9 luồng trên mỗi hàng ngang\n"
            "• Mỗi luồng cách nhau 500px\n"
            "• Hàng mới cách nhau 1000px\n"
            "• Vị trí: (index % 9 * 500, index // 9 * 1000)"
        ))
        row_layout.addWidget(info_btn)

        # Remove button
        remove_btn = QPushButton("❌")
        remove_btn.setMaximumWidth(60)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_config(group))
        row_layout.addWidget(remove_btn)

        # Common settings note (compact)
        note_label = QLabel("💡 Token/ServiceID/Network từ 'Cài đặt chung'")
        note_label.setStyleSheet(f"color: #888; font-size: {int(10 * UI_SCALE)}px; font-style: italic; margin-left: {int(10 * UI_SCALE)}px;")
        row_layout.addWidget(note_label)

        row_layout.addStretch()

        # Store references
        group._inputs = {
            'name': name_input,
            'key_index': key_index,
            'win_x': win_x,
            'win_y': win_y
        }

        self.configs_layout_inner.addWidget(group)
        self.update_configs_json()

    def remove_config(self, group):
        """Remove a config form"""
        group.setParent(None)
        group.deleteLater()
        self.update_configs_json()

    def clear_all_configs(self):
        """Clear all config forms"""
        while self.configs_layout_inner.count():
            item = self.configs_layout_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.update_configs_json()

    def reset_window_layout(self):
        """Reset tất cả window positions về layout tự động"""
        for i in range(self.configs_layout_inner.count()):
            group = self.configs_layout_inner.itemAt(i).widget()
            if hasattr(group, '_inputs'):
                inputs = group._inputs

                # Tính lại vị trí tự động
                win_x = (i % 9) * 500  # 9 configs per row
                win_y = (i // 9) * 1000  # Tăng Y mỗi 9 configs

                # Update spinbox values
                inputs['win_x'].setValue(win_x)
                inputs['win_y'].setValue(win_y)

        self.update_configs_json()
        self.log_text.append("🔄 Đã reset layout cửa sổ về mặc định!")

    def get_all_configs(self):
        """Get all configs from forms, combining common settings"""
        # Get common settings
        common_token = self.common_token_input.text() or "b5f70a870ef8437ab55b8e98968bc215"
        common_provider = self.common_provider_combo.currentText()
        common_network = self.common_network_combo.currentText()

        if common_provider == "VIOTP":
            common_service = self.common_service_input.text() or "841"
        else:  # BOSSOTP
            common_service = self.common_boss_service_input.text() or "66650e049255470ed6f92ed4"

        common_boss_token = self.common_boss_token_input.text().strip()

        configs = []
        for i in range(self.configs_layout_inner.count()):
            group = self.configs_layout_inner.itemAt(i).widget()
            if hasattr(group, '_inputs'):
                inputs = group._inputs
                config = {
                    "name": inputs['name'].text() or f"Luồng {i+1}",
                    "kito_key_index": inputs['key_index'].value(),
                    "token_vio": common_token,
                    "boss_token": common_boss_token,
                    "provider": common_provider,
                    "service_id": common_service,
                    "network": common_network,
                    "win_pos": [inputs['win_x'].value(), inputs['win_y'].value()]
                }
                configs.append(config)
        return configs

    def update_configs_json(self):
        """Update hidden JSON text area from forms"""
        configs = self.get_all_configs()
        self.configs_text.setPlainText(json.dumps(configs, indent=2, ensure_ascii=False))

    def update_balance(self):
        """Cập nhật số dư VIOTP mỗi 5 giây"""
        try:
            provider = self.common_provider_combo.currentText()
            if provider == "VIOTP":
                token = self.common_token_input.text().strip()
                if not token:
                    self.balance_label.setText("Túi tiền OTP: Chưa có token VIOTP")
                    return
                response = requests.get(f"https://api.viotp.com/users/balance?token={token}", timeout=10)
                data = response.json()
                if data.get("status_code") == 200 and data.get("success"):
                    balance = data["data"]["balance"]
                    formatted_balance = f"{balance:,}".replace(",", ".")
                    self.balance_label.setText(f"Túi tiền OTP: {formatted_balance} VND (VIOTP)")
                else:
                    self.balance_label.setText("Túi tiền OTP: Lỗi API VIOTP")
            else:
                # BOSSOTP
                token = self.common_boss_token_input.text().strip()
                if not token:
                    self.balance_label.setText("Túi tiền OTP: Chưa có token BOSSOTP")
                    return
                try:
                    # Sử dụng domain chính xác cho BOSSOTP
                    url = f"https://bossotp.net/api/v4/users/me/balance?api_token={token}"
                    resp = requests.get(url, timeout=10)
                    data = resp.json()
                    balance = data.get("balance", None)
                    if balance is not None:
                        formatted_balance = f"{balance:,}".replace(",", ".")
                        self.balance_label.setText(f"Túi tiền OTP: {formatted_balance} VND (BOSSOTP)")
                    else:
                        self.balance_label.setText("Túi tiền OTP: Lỗi API BOSSOTP")

                except Exception as e:
                    self.balance_label.setText(f"Túi tiền OTP: Lỗi kết nối BOSSOTP - {str(e)}")

        except json.JSONDecodeError:
            self.balance_label.setText("Túi tiền OTP: Lỗi JSON")
        except requests.RequestException as e:
            self.balance_label.setText("Túi tiền OTP: Mất kết nối")
        except Exception as e:
            self.balance_label.setText("Túi tiền OTP: Lỗi không xác định")

    def check_proxy_info(self):
        """Check thông tin proxy từ key đầu tiên - chạy trong background thread"""
        try:
            # Lấy keys từ KEYS text
            keys_text = self.keys_text.toPlainText().strip()
            if not keys_text:
                QMessageBox.warning(self, "Cảnh báo", "Không có KEYS nào để check proxy!")
                return

            keys = [line.strip() for line in keys_text.split('\n') if line.strip()]
            if not keys:
                QMessageBox.warning(self, "Cảnh báo", "Không có key hợp lệ nào!")
                return

            configs = self.get_all_configs()

            # Tạo worker thread để check proxy
            self.proxy_worker = ProxyCheckWorker('single', keys, configs)
            self.proxy_worker.log_signal.connect(self.append_log)
            self.proxy_worker.finished.connect(self.show_proxy_result)
            self.proxy_worker.start()

            # Disable button tạm thời
            self.check_proxy_btn.setEnabled(False)
            self.check_proxy_btn.setText("🔍 Đang check...")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khởi tạo: {str(e)}")

    def show_proxy_result(self, result):
        """Hiển thị kết quả proxy check"""
        try:
            # Re-enable button
            self.check_proxy_btn.setEnabled(True)
            self.check_proxy_btn.setText("🔍 Check PROXY")

            # Hiển thị kết quả
            if result.startswith("❌"):
                QMessageBox.critical(self, "Lỗi", result)
            elif result.startswith("⚠️"):
                QMessageBox.warning(self, "Cảnh báo", result)
            else:
                QMessageBox.information(self, "Thông tin Proxy", result)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi hiển thị kết quả: {str(e)}")

    def check_all_proxy_info(self):
        """Check thông tin proxy từ tất cả keys - chạy trong background thread"""
        try:
            # Lấy keys từ KEYS text
            keys_text = self.keys_text.toPlainText().strip()
            if not keys_text:
                QMessageBox.warning(self, "Cảnh báo", "Không có KEYS nào để check proxy!")
                return

            keys = [line.strip() for line in keys_text.split('\n') if line.strip()]
            if not keys:
                QMessageBox.warning(self, "Cảnh báo", "Không có key hợp lệ nào!")
                return

            # Tạo worker thread để check proxy
            self.proxy_worker = ProxyCheckWorker('all', keys)
            self.proxy_worker.log_signal.connect(self.append_log)
            self.proxy_worker.finished.connect(self.show_all_proxy_result)
            self.proxy_worker.start()

            # Disable button tạm thời
            self.check_all_proxy_btn.setEnabled(False)
            self.check_all_proxy_btn.setText("🔍 Đang check...")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khởi tạo: {str(e)}")

    def show_all_proxy_result(self, result):
        """Hiển thị kết quả check all proxy"""
        try:
            # Re-enable button
            self.check_all_proxy_btn.setEnabled(True)
            self.check_all_proxy_btn.setText("🔍 Check All PROXY")

            # Hiển thị kết quả trong dialog
            if len(result) < 2000:
                QMessageBox.information(self, "Kết quả Check All Proxy", result)
            else:
                # Nếu quá dài, hiển thị tóm tắt
                lines = result.split('\n')
                success_count = sum(1 for line in lines if line.startswith('✅'))
                error_count = sum(1 for line in lines if line.startswith('❌') or line.startswith('⚠️'))
                QMessageBox.information(self, "Kết quả Check All Proxy",
                                      f"Đã check hoàn thành. Xem chi tiết trong log.\n\n"
                                      f"✅ Thành công: {success_count}\n❌ Thất bại: {error_count}")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi hiển thị kết quả: {str(e)}")

    def save_configuration(self):
        """Lưu toàn bộ cấu hình hiện tại"""
        try:
            config_data = {
                "api_host": self.api_host_input.text().strip(),
                "browser_version": self.browser_version_input.text().strip(),
                "target_acc": int(self.target_acc_input.value()) if hasattr(self, 'target_acc_input') else 0,
                "keys": self.keys_text.toPlainText().strip(),
                "common_token": self.common_token_input.text().strip(),
                "common_boss_token": self.common_boss_token_input.text().strip(),
                "common_provider": self.common_provider_combo.currentText(),
                "common_service": self.common_service_input.text().strip(),
                "common_boss_service": self.common_boss_service_input.text().strip(),
                "common_network": self.common_network_combo.currentText(),
                "configs": self.get_all_configs(),
                "stats": self.stats.copy()
            }

            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình thành công!")
            self.log_text.append("💾 Đã lưu cấu hình thành công!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cấu hình:\n{str(e)}")
            self.log_text.append(f"❌ Lỗi lưu cấu hình: {e}")

    def load_configuration(self):
        """Tải cấu hình đã lưu"""
        try:
            if not os.path.exists(CONFIG_FILE):
                self.log_text.append("ℹ️ Không tìm thấy file cấu hình, sử dụng mặc định")
                return

            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Load settings
            self.api_host_input.setText(config_data.get("api_host", DEFAULT_API_HOST))
            self.browser_version_input.setText(config_data.get("browser_version", DEFAULT_BROWSER_VERSION))
            # Load target acc
            try:
                self.target_acc_input.setValue(int(config_data.get("target_acc", 0)))
            except Exception:
                self.target_acc_input.setValue(0)
            self.keys_text.setPlainText(config_data.get("keys", ""))

            # Load common settings
            self.common_token_input.setText(config_data.get("common_token", "b5f70a870ef8437ab55b8e98968bc215"))
            self.common_boss_token_input.setText(config_data.get("common_boss_token", ""))
            self.common_provider_combo.setCurrentText(config_data.get("common_provider", "VIOTP"))
            self.common_service_input.setText(config_data.get("common_service", "841"))
            self.common_boss_service_input.setText(config_data.get("common_boss_service", "66650e049255470ed6f92ed4"))
            self.common_network_combo.setCurrentText(config_data.get("common_network", "MOBIFONE"))

            # Load configs
            saved_configs = config_data.get("configs", [])
            if saved_configs:
                # Clear existing configs
                self.clear_all_configs()
                # Load saved configs
                for config in saved_configs:
                    self.add_config_form(config_data=config)

            # Load stats
            saved_stats = config_data.get("stats", {})
            self.stats.update(saved_stats)
            self.update_stats_display()

            self.log_text.append("📂 Đã tải cấu hình thành công!")

        except Exception as e:
            self.log_text.append(f"⚠️ Lỗi tải cấu hình: {e}")

    def update_stats(self, stat_type, increment=1):
        """Cập nhật thống kê"""
        if stat_type in self.stats:
            self.stats[stat_type] += increment
            self.update_stats_display()

    def update_stats_display(self):
        """Cập nhật hiển thị stats trên GUI"""
        self.acc_success_label.setText(f"✅ ACC TẠO THÀNH CÔNG: {self.stats['acc_success']}")
        self.phones_rented_label.setText(f"📞 TỔNG SỐ ĐÃ THUÊ: {self.stats['phones_rented']}")

    def on_stop_timeout(self):
        """Xử lý khi timer dừng kết thúc"""
        self.is_stopping = False
        self.stop_button.setText("⏹️ Dừng")
        self.stop_button.setEnabled(True)
        self.log_text.append("✅ Có thể dừng lại chương trình!")

    def start_worker(self):
        try:
            # Lấy API Host từ input
            api_host = self.api_host_input.text().strip()
            if not api_host:
                api_host = DEFAULT_API_HOST

            # Lấy Browser Version từ input
            browser_version = self.browser_version_input.text().strip()
            if not browser_version:
                browser_version = DEFAULT_BROWSER_VERSION

            # Parse KEYS
            keys_text = self.keys_text.toPlainText().strip()
            if not keys_text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập KEYS!")
                return
            keys = [line.strip() for line in keys_text.split('\n') if line.strip()]

            # Get CONFIGS from form
            configs = self.get_all_configs()
            if not configs:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm ít nhất 1 config!")
                return

            # Validate configs
            for cfg in configs:
                if cfg["kito_key_index"] >= len(keys):
                    QMessageBox.warning(self, "Cảnh báo", f"Config '{cfg['name']}' có key_index {cfg['kito_key_index']} vượt quá số lượng KEYS!")
                    return

            # Lấy target từ input
            target_acc = int(self.target_acc_input.value()) if hasattr(self, 'target_acc_input') else 0

            # Khởi tạo worker thread
            self.worker_thread = WorkerThread(keys, configs, api_host, browser_version, target_acc)
            self.worker_thread.log_signal.connect(self.append_log)
            self.worker_thread.stats_signal.connect(self.update_stats)
            self.worker_thread.start()

            self.start_button.setEnabled(False)
            self.log_text.append("🚀 Đã bắt đầu chạy chương trình!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khởi động:\n{str(e)}")
            self.log_text.append(f"❌ Lỗi khởi động: {e}")

    def stop_worker(self):
        # Kiểm tra nếu đang trong trạng thái dừng
        if self.is_stopping:
            self.log_text.append("⏳ Đang dừng, vui lòng chờ...")
            return

        if self.worker_thread and self.worker_thread.isRunning():
            # Đặt trạng thái đang dừng
            self.is_stopping = True
            self.stop_button.setText("⏸️ Đang dừng...")
            self.stop_button.setEnabled(False)
            self.log_text.append("⏳ Đang dừng chương trình, vui lòng chờ 30 giây...")

            # Dừng worker thread (không chay cleanup nặng ở main thread)
            try:
                self.worker_thread.stop()
            except Exception as e:
                self.log_text.append(f"⚠️ Lỗi khi gửi yêu cầu dừng: {e}")

            # Khởi 1 thread background nhẹ để đợi worker thực sự kết thúc và
            # thông báo (không làm gì nặng ở main thread).
            def wait_for_worker_and_log():
                try:
                    # chờ tối đa 20s để worker dừng; không block GUI
                    waited = 0
                    while self.worker_thread.isRunning() and waited < 20:
                        time.sleep(0.5)
                        waited += 0.5
                    if not self.worker_thread.isRunning():
                        # Emit a short message back on main thread using QTimer.singleShot
                        QTimer.singleShot(0, lambda: self.log_text.append("✅ Worker đã dừng. Cleanup được thực hiện trong thread."))
                    else:
                        QTimer.singleShot(0, lambda: self.log_text.append("⚠️ Worker vẫn chưa dừng sau 20s. Vui lòng kiểm tra."))
                except Exception as e:
                    QTimer.singleShot(0, lambda: self.log_text.append(f"⚠️ Lỗi khi chờ worker dừng: {e}"))

            threading.Thread(target=wait_for_worker_and_log, daemon=True).start()

            # Chờ 30 giây trước khi cho phép dừng lại
            self.stop_timer.start(30000)  # 30 giây

            # (history feature removed)

            # Vẫn enable start button ngay lập tức
            self.start_button.setEnabled(True)
        else:
            self.log_text.append("⚠️ Không có chương trình nào đang chạy!")

    def reset_stats(self):
        """Reset tất cả thống kê về 0"""
        self.stats = {
            'acc_success': 0,
            'phones_rented': 0
        }
        self.update_stats_display()
        self.log_text.append("🔄 Đã reset tất cả thống kê!")

    def open_acc_file(self):
        """Mở file ACC.txt bằng chương trình mặc định"""
        try:
            if os.path.exists("ACC.txt"):
                os.startfile("ACC.txt")  # Windows only
                self.log_text.append("📂 Đã mở file ACC.txt")
            else:
                QMessageBox.warning(self, "Cảnh báo", "File ACC.txt chưa tồn tại!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở file ACC.txt:\n{str(e)}")

    def append_log(self, text):
        self.log_text.append(text)

    def clear_log(self):
        """Clear the log area"""
        try:
            self.log_text.clear()
            # Keep a short system entry to show it was cleared
            self.log_text.append("🧹 Log đã được xóa.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xóa log: {e}")

    # (History update feature removed)

def start_viotp_config_server(port=19996):
    """Start a tiny HTTP server that exposes VIO OTP config from CONFIGS[0]."""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/viotp-config":
                try:
                    # Sử dụng config đầu tiên làm mặc định
                    cfg = {
                        "token": "b5f70a870ef8437ab55b8e98968bc215",
                        "service_id": "841",
                        "network": "MOBIFONE"
                    }
                    payload = {
                        "token": cfg.get("token", ""),
                        "service_id": cfg.get("service_id", ""),
                        "network": cfg.get("network", "")
                    }
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    def _serve():
        try:
            server = HTTPServer(("127.0.0.1", port), Handler)
            # print(f"[viotp-config] Serving VIO config on http://127.0.0.1:{port}/viotp-config")
            server.serve_forever()
        except Exception as e:
            # print(f"[viotp-config] Server error: {e}")
            pass

        t = threading.Thread(target=_serve, daemon=True)
        t.start()

def main():
    # Đảm bảo các file cần thiết tồn tại
    ensure_files_exist()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
