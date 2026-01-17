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
    QScrollArea, QGroupBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

# --- Cấu hình chung ---

DEFAULT_API_HOST = "http://127.0.0.1:19053"
DEFAULT_BROWSER_VERSION = "129.0.6668.59"
CREATE_PROFILE_PATH = "/api/v3/profiles/create"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 50

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
        print("Failed to fetch balance:", e)
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

# KEYS mặc định
DEFAULT_KEYS = """Tiến Thuận VIP REG OKVIP"""

# CONFIGS mặc định
DEFAULT_CONFIGS = """[
]"""

class LogRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.append(text.strip())

    def flush(self):
        pass

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(str, int)  # stat_type, increment

    def __init__(self, keys, configs, api_host, browser_version):
        super().__init__()
        self.keys = keys
        self.configs = configs
        self.api_host = api_host
        self.browser_version = browser_version
        self.running = True

    def stop(self):
        self.running = False

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
                "os": "Windows 10",
                "webrtc_mode": 2,
               "user_agent": (
                    "MyGreatApp/1.4.2 (Linux; Android 14; Pixel 8 Build/TP1A.230624.014) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.0.0 Mobile Safari/537.36"
                ),
            }
            url = f"{self.api_host}{CREATE_PROFILE_PATH}"
            resp = session.post(url, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                raise RuntimeError(f"Create profile failed: {data}")
            profile_id = data["data"]["id"]
            self.log_signal.emit(f"[{cfg['name']}] Created profile {profile_id}")
            x, y = cfg.get("win_pos", (0, 0))
            start_url = f"{self.api_host}/api/v3/profiles/start/{profile_id}?win_pos={x},{y}&win_scale=0.4&win_size=368,868&addination_args=--app=https://m.okvipau.com/&addination_args=--mute-audio"
            resp = session.get(start_url)
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
            driver.get("https://m.oklavip16.live/register?isIOSPure")

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

                self.log_signal.emit(f"[{cfg['name']}] \n🔄 Đang tìm số điện thoại chưa đăng ký...")

                # Lấy số điện thoại ảo
                phone_number, request_id = self.get_phone_number(cfg)

                if not phone_number:
                    self.log_signal.emit(f"[{cfg['name']}] ❌ Không thể lấy số điện thoại. Thoát chương trình.")
                    break

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
                    self.log_signal.emit(f"[{cfg['name']}] 🔄 Số đã đăng ký. Load lại trang HOÀN TOÀN và tạo thông tin mới...")
                    driver.get("https://m.oklavip16.live/register?isIOSPure")  # Load lại trang từ đầu
                    self.mute_audio(driver, cfg)  # Tắt tiếng lại
                    time.sleep(3)  # Chờ trang load
                    continue  # Tiếp tục vòng lặp với thông tin hoàn toàn mới

                # Nếu không có thông báo lỗi, kiểm tra đã chuyển sang registerStep chưa
                if self.check_register_step_url(driver, cfg):
                    self.log_signal.emit(f"[{cfg['name']}] 🎯 Đã chuyển sang trang OTP thành công!")

                    # Click nút "Gửi đi" và tự động giải captcha
                    if self.click_send_and_solve(driver, cfg):
                        self.log_signal.emit(f"[{cfg['name']}] ✅ Đã gửi OTP và giải captcha thành công!")
                        self.stats_signal.emit('phones_rented', 1)  # Tăng counter tổng số đã thuê

                        # Chờ thông báo "Gửi thành công" và bắt đầu lấy OTP
                        otp_received = False
                        for _ in range(30):  # Chờ tối đa 30 giây
                            try:
                                toast = WebDriverWait(driver, 2).until(
                                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.van-toast__text"))
                                )
                                if "Gửi thành công" in toast.text:
                                    self.log_signal.emit(f"[{cfg['name']}] 📨 Nhận được thông báo 'Gửi thành công', bắt đầu lấy OTP...")

                                    sothime = 0
                                    self.log_signal.emit(f"[{cfg['name']}] 📱 Phone: {phone_number} | Request ID: {request_id}")

                                    while self.running:
                                        r = requests.get(f"https://api.viotp.com/session/getv2?requestId={request_id}&token={cfg['token_vio']}").json()
                                        get_code = r.get("data", {}).get("Code")

                                        thanhnunglon = 80 - int(sothime)
                                        self.log_signal.emit(f"[{cfg['name']}] 🔄 OTP polled: {get_code} [{thanhnunglon}s còn lại]")

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
                                            otp_received = True
                                            break

                                        else:
                                            time.sleep(3)
                                            sothime += 3

                                        if sothime > 80:
                                            self.log_signal.emit(f"[{cfg['name']}] ⏰ OTP timeout - không nhận được mã trong 80 giây")
                                            break

                                    break

                            except Exception as e:
                                pass

                            time.sleep(1)

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
                    requests.get(f"{self.api_host}/api/v3/profiles/close/{profile_id}")
                    requests.get(f"{self.api_host}/api/v3/profiles/delete/{profile_id}")
                    self.log_signal.emit(f"[{cfg['name']}] Closed and deleted profile {profile_id}")
            except Exception as e:
                self.log_signal.emit(f"[{cfg['name']}] Cleanup profile exception: {e}")
            try:
                if driver:
                    driver.quit()
            except:
                pass

    # Copy các helper functions từ code gốc
    def get_phone_number(self, cfg):
        """Lấy số điện thoại ảo từ VIOTP"""
        try:
            url = f"https://api.viotp.com/request/getv2?token={cfg['token_vio']}&serviceId={cfg['service_id']}&network={cfg['network']}"
            response = requests.get(url)
            data = response.json()

            self.log_signal.emit(f"[{cfg['name']}] 📱 API Response: {data}")

            if data.get('status_code') == 200:
                phone_number = data['data']['phone_number']
                request_id = data['data']['request_id']

                self.log_signal.emit(f"[{cfg['name']}] ✅ Đã lấy số điện thoại: {phone_number}")
                self.log_signal.emit(f"[{cfg['name']}] 📋 Request ID: {request_id}")

                self.stats_signal.emit('phones_rented', 1)  # Tăng counter tổng số đã thuê
                return phone_number, request_id
            else:
                self.log_signal.emit(f"[{cfg['name']}] ⚠️ Lỗi API: {data}")
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
                EC.visibility_of_element_located((By.XPATH, '//div[@role="dialog" and contains(@class, "van-toast") and .//div[contains(text(), "Số điện thoại đã được đăng kí")]]'))
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

    def init_ui(self):
        self.setWindowTitle("Reg Đa Luồng + GPM - GUI")
        self.setGeometry(100, 100, 1200, 800)

        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Thêm label hiển thị số dư VIOTP ở góc phải trên cùng
        self.balance_label = QLabel("Túi tiền OTP: Đang tải...")
        self.balance_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 10px;
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 5px;
            }
        """)
        self.balance_label.setFixedHeight(30)

        # Timer để cập nhật số dư mỗi 5 giây
        self.balance_timer = QTimer()
        self.balance_timer.timeout.connect(self.update_balance)
        self.balance_timer.start(5000)  # 5 giây

        # Cập nhật số dư lần đầu
        self.update_balance()

        # Layout chính
        main_layout = QVBoxLayout(central_widget)

        # Header với các settings ở góc phải
        header_layout = QHBoxLayout()

        # Stats labels
        stats_layout = QVBoxLayout()
        self.acc_success_label = QLabel("✅ ACC TẠO THÀNH CÔNG: 0")
        self.acc_success_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.acc_success_label)

        self.phones_rented_label = QLabel("📞 TỔNG SỐ ĐÃ THUÊ: 0")
        self.phones_rented_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.phones_rented_label)

        # Browser version input
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(QLabel("Browser Version:"))
        self.browser_version_input = QLineEdit(DEFAULT_BROWSER_VERSION)
        self.browser_version_input.setFont(QFont("Consolas", 9))
        self.browser_version_input.setPlaceholderText("129.0.6668.59")
        self.browser_version_input.setFixedWidth(150)
        browser_layout.addWidget(self.browser_version_input)

        header_layout.addLayout(stats_layout)
        header_layout.addLayout(browser_layout)
        header_layout.addStretch()  # Đẩy balance label sang bên phải
        header_layout.addWidget(self.balance_label)
        main_layout.addLayout(header_layout)

        # Splitter cho KEYS và CONFIGS
        splitter_top = QSplitter(Qt.Orientation.Horizontal)

        # Panel KEYS và API Host
        keys_widget = QWidget()
        keys_layout = QVBoxLayout(keys_widget)

        # API Host input
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API Host:"))
        self.api_host_input = QLineEdit(DEFAULT_API_HOST)
        self.api_host_input.setFont(QFont("Consolas", 10))
        self.api_host_input.setPlaceholderText("http://127.0.0.1:19053")
        api_layout.addWidget(self.api_host_input)
        keys_layout.addLayout(api_layout)

        # KEYS input
        keys_layout.addWidget(QLabel("KEYS (mỗi key một dòng):"))
        self.keys_text = QTextEdit()
        self.keys_text.setPlainText(DEFAULT_KEYS)
        self.keys_text.setFont(QFont("Consolas", 10))
        keys_layout.addWidget(self.keys_text)
        splitter_top.addWidget(keys_widget)

        # Panel CONFIGS (Form-based)
        configs_widget = QWidget()
        configs_layout = QVBoxLayout(configs_widget)

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

        # Row 1: VIOTP Token and Service ID
        common_row1 = QHBoxLayout()
        common_row1.addWidget(QLabel("VIOTP Token:"))
        self.common_token_input = QLineEdit("b5f70a870ef8437ab55b8e98968bc215")
        self.common_token_input.setPlaceholderText("Token API VIOTP")
        self.common_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        common_row1.addWidget(self.common_token_input)

        common_row1.addWidget(QLabel("Service ID:"))
        self.common_service_input = QLineEdit("841")
        self.common_service_input.setPlaceholderText("841")
        common_row1.addWidget(self.common_service_input)

        common_layout.addLayout(common_row1)

        # Row 2: Network
        common_row2 = QHBoxLayout()
        common_row2.addWidget(QLabel("Network:"))
        self.common_network_combo = QComboBox()
        self.common_network_combo.addItems(["MOBIFONE", "VIETTEL", "VINAPHONE", "VIETNAMOBILE"])
        self.common_network_combo.setCurrentText("MOBIFONE")
        common_row2.addWidget(self.common_network_combo)
        common_row2.addStretch()

        common_layout.addLayout(common_row2)
        configs_layout.addWidget(common_group)

        # === INDIVIDUAL CONFIGS ===
        # Header với controls
        configs_header = QHBoxLayout()
        configs_header.addWidget(QLabel("🎯 Cấu hình riêng từng luồng:"))

        # Buttons for config management
        self.add_config_btn = QPushButton("➕ Add Config")
        self.add_config_btn.clicked.connect(lambda: self.add_config_form())
        self.clear_configs_btn = QPushButton("🗑️ Clear All")
        self.clear_configs_btn.clicked.connect(self.clear_all_configs)

        configs_header.addWidget(self.add_config_btn)
        configs_header.addWidget(self.clear_configs_btn)
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
        self.configs_scroll.setMinimumHeight(200)
        configs_layout.addWidget(self.configs_scroll)

        # Hidden text area for JSON (used internally)
        self.configs_text = QTextEdit()
        self.configs_text.setPlainText(DEFAULT_CONFIGS)
        self.configs_text.hide()  # Hide from UI but keep for compatibility

        # Load default configs into form
        self.load_default_configs()
        splitter_top.addWidget(configs_widget)

        splitter_top.setSizes([400, 400])

        # Nút điều khiển
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.start_button = QPushButton("▶️ Bắt đầu")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_worker)

        self.stop_button = QPushButton("⏹️ Dừng")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_button.clicked.connect(self.stop_worker)
        self.stop_button.setEnabled(False)

        self.open_acc_button = QPushButton("📂 Mở File ACC")
        self.open_acc_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.open_acc_button.clicked.connect(self.open_acc_file)

        self.reset_stats_button = QPushButton("🔄 Reset Stats")
        self.reset_stats_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        self.reset_stats_button.clicked.connect(self.reset_stats)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.open_acc_button)
        buttons_layout.addWidget(self.reset_stats_button)
        buttons_layout.addStretch()

        # Panel LOG
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("LOG:"))
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        # Splitter chính
        splitter_main = QSplitter(Qt.Orientation.Vertical)
        splitter_main.addWidget(splitter_top)
        splitter_main.addWidget(buttons_widget)
        splitter_main.addWidget(log_widget)
        splitter_main.setSizes([300, 50, 450])

        main_layout.addWidget(splitter_main)

        # Đặt màu nền tối cho log
        palette = self.log_text.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 200))
        self.log_text.setPalette(palette)

    def update_balance(self):
        """Cập nhật số dư VIOTP mỗi 5 giây"""
        try:
            # Lấy token từ config đầu tiên trong CONFIGS
            configs = self.get_all_configs()
            if not configs:
                self.balance_label.setText("Túi tiền OTP: Chưa có config")
                return

            # Lấy token từ config đầu tiên
            first_config = configs[0]
            token = first_config.get("token_vio", "")
            if not token:
                self.balance_label.setText("Túi tiền OTP: Chưa có token")
                return

            # Gọi API lấy số dư
            response = requests.get(f"https://api.viotp.com/users/balance?token={token}", timeout=10)
            data = response.json()

            if data.get("status_code") == 200 and data.get("success"):
                balance = data["data"]["balance"]
                # Format số dư với dấu chấm ngăn cách
                formatted_balance = f"{balance:,}".replace(",", ".")
                self.balance_label.setText(f"Túi tiền OTP: {formatted_balance} VND")
            else:
                self.balance_label.setText("Túi tiền OTP: Lỗi API")

        except requests.RequestException as e:
            self.balance_label.setText("Túi tiền OTP: Mất kết nối")
        except Exception as e:
            self.balance_label.setText("Túi tiền OTP: Lỗi không xác định")

    def start_worker(self):
        try:
            # Parse KEYS
            keys_text = self.keys_text.toPlainText().strip()
            if not keys_text:
                self.log_text.append("❌ Vui lòng nhập KEYS!")
                return
            keys = [line.strip() for line in keys_text.split('\n') if line.strip()]

            # Get CONFIGS from form
            configs = self.get_all_configs()
            if not configs:
                self.log_text.append("❌ Vui lòng thêm ít nhất 1 config!")
                return

            # Validate configs
            for cfg in configs:
                if "kito_key_index" not in cfg:
                    self.log_text.append("❌ Thiếu kito_key_index trong config!")
                    return
                if cfg["kito_key_index"] >= len(keys):
                    self.log_text.append(f"❌ kito_key_index {cfg['kito_key_index']} vượt quá số lượng KEYS!")
                    return

            # Lấy API Host từ input
            api_host = self.api_host_input.text().strip()
            if not api_host:
                api_host = DEFAULT_API_HOST

            # Lấy Browser Version từ input
            browser_version = self.browser_version_input.text().strip()
            if not browser_version:
                browser_version = DEFAULT_BROWSER_VERSION

            # Reset trạng thái dừng
            self.is_stopping = False
            self.stop_button.setText("⏹️ Dừng")
            self.stop_button.setEnabled(True)
            self.stop_timer.stop()  # Dừng timer nếu đang chạy

            # Khởi tạo worker thread
            self.worker_thread = WorkerThread(keys, configs, api_host, browser_version)
            self.worker_thread.log_signal.connect(self.append_log)
            self.worker_thread.stats_signal.connect(self.update_stats)
            self.worker_thread.start()

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.log_text.append("🚀 Đã bắt đầu chạy chương trình!")

        except Exception as e:
            self.log_text.append(f"❌ Lỗi: {e}")

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

            # Dừng worker thread
            self.worker_thread.stop()

            # Chờ 30 giây trước khi cho phép dừng lại
            self.stop_timer.start(30000)  # 30 giây

            # Vẫn enable start button ngay lập tức
            self.start_button.setEnabled(True)
        else:
            self.log_text.append("⚠️ Không có chương trình nào đang chạy!")

    def append_log(self, text):
        self.log_text.append(text)

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
            import os
            if os.path.exists("ACC.txt"):
                os.startfile("ACC.txt")  # Windows only
                self.log_text.append("📂 Đã mở file ACC.txt")
            else:
                self.log_text.append("❌ File ACC.txt chưa tồn tại")
        except Exception as e:
            self.log_text.append(f"❌ Không thể mở file ACC.txt: {e}")

    def load_default_configs(self):
        """Load default configs into form interface"""
        try:
            configs = json.loads(DEFAULT_CONFIGS)
            for config in configs:
                # Only load individual fields, common settings are separate
                simplified_config = {
                    "name": config.get("name", ""),
                    "kito_key_index": config.get("kito_key_index", 0),
                    "win_pos": config.get("win_pos", [0, 0])
                }
                self.add_config_form(config_data=simplified_config)
        except json.JSONDecodeError:
            pass

    def add_config_form(self, config_data=None):
        """Add a new config form"""
        if config_data is None or not isinstance(config_data, dict):
            config_data = {
                "name": f"Luồng {len(self.get_all_configs()) + 1}",
                "kito_key_index": 0,
                "win_pos": [0, 0]
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

        layout = QVBoxLayout(group)

        # Row 1: Name and Key Index
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Name:"))
        name_input = QLineEdit(config_data.get("name", ""))
        name_input.setPlaceholderText("Luồng 1")
        row1.addWidget(name_input)

        row1.addWidget(QLabel("Key Index:"))
        key_index = QSpinBox()
        key_index.setRange(0, 20)
        key_index.setValue(config_data.get("kito_key_index", 0))
        row1.addWidget(key_index)

        # Remove button
        remove_btn = QPushButton("❌ Remove")
        remove_btn.clicked.connect(lambda: self.remove_config(group))
        row1.addWidget(remove_btn)

        layout.addLayout(row1)

        # Row 2: Window Position only
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Window X:"))
        win_x = QSpinBox()
        win_x.setRange(0, 3000)
        win_x.setValue(config_data.get("win_pos", [0, 0])[0])
        row2.addWidget(win_x)

        row2.addWidget(QLabel("Window Y:"))
        win_y = QSpinBox()
        win_y.setRange(0, 2000)
        win_y.setValue(config_data.get("win_pos", [0, 0])[1])
        row2.addWidget(win_y)

        row2.addStretch()
        layout.addLayout(row2)

        # Note about common settings
        note_label = QLabel("💡 Token, Service ID, Network được lấy từ phần 'Cài đặt chung' ở trên")
        note_label.setStyleSheet("color: #AAA; font-size: 11px; font-style: italic;")
        layout.addWidget(note_label)

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

    def get_all_configs(self):
        """Get all configs from forms, combining common settings"""
        # Get common settings
        common_token = self.common_token_input.text() or "b5f70a870ef8437ab55b8e98968bc215"
        common_service = self.common_service_input.text() or "841"
        common_network = self.common_network_combo.currentText()

        configs = []
        for i in range(self.configs_layout_inner.count()):
            group = self.configs_layout_inner.itemAt(i).widget()
            if hasattr(group, '_inputs'):
                inputs = group._inputs
                config = {
                    "name": inputs['name'].text() or f"Luồng {i+1}",
                    "kito_key_index": inputs['key_index'].value(),
                    "token_vio": common_token,
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
            print(f"[viotp-config] Serving VIO config on http://127.0.0.1:{port}/viotp-config")
            server.serve_forever()
        except Exception as e:
            print(f"[viotp-config] Server error: {e}")

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
