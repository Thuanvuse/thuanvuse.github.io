import sys
import threading
import time
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QInputDialog, QLabel, QSpinBox, QHBoxLayout,QPushButton 
from PyQt6.QtGui import QContextMenuEvent, QColor
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QBrush, QColor
import requests
import random
import hashlib
import json
import time
import concurrent.futures
import re
from PyQt6.QtWidgets import QComboBox
from datetime import datetime
from PyQt6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox

class ProxyCheckWorker(QThread):
    result_signal = pyqtSignal(int, str, bool)  # i, status, is_live

    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.accounts = accounts

    def run(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def check_single_proxy(i, acc):
            proxy_str = acc[1]
            status = "❌ [DIE]"
            for attempt in range(3):
                try:
                    host, port, user, pwd = proxy_str.split(":")
                    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
                    proxies = {"http": proxy_url, "https": proxy_url}
                    r = requests.get("https://geo.myip.link/", proxies=proxies, timeout=5)
                    ip_info = r.json()
                    status = f"✅ [LIVE] {ip_info['ip']} - {ip_info['country']} ({ip_info['city']})"
                    return i, status, True
                except:
                    continue
            return i, status, False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_single_proxy, i, acc) for i, acc in enumerate(self.accounts)]

            for future in as_completed(futures):
                i, status, is_live = future.result()
                self.result_signal.emit(i, status, is_live)

class ProxyCheckDialog(QDialog):
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kiểm Tra Proxy & Thay Proxy")
        self.setMinimumSize(600, 400)
        self.accounts = accounts
        self.results = []
        self.die_indexes = []
        self.results = []
        self.live_count = 0
        self.die_count = 0
        self.die_indexes = []


        layout = QVBoxLayout(self)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.replace_box = QTextEdit(self)
        self.replace_box.setPlaceholderText("Proxy mới - 1 dòng mỗi proxy")
        layout.addWidget(self.replace_box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.check_proxies()

    def check_proxies(self):
        self.worker = ProxyCheckWorker(self.accounts)
        self.worker.result_signal.connect(self.update_status)
        self.worker.start()
    def update_status(self, i, status, is_live):
        self.results.append(status)

        item = QTableWidgetItem(status)
        color = QColor("green") if is_live else QColor("red")
        item.setForeground(QBrush(color))
        self.parent().table.setItem(i, 6, item)

        if is_live:
            self.live_count += 1
        else:
            self.die_count += 1
            self.die_indexes.append(i)

        # Cập nhật summary
        summary = f"\nTổng proxy: {len(self.accounts)} | ✅ LIVE: {self.live_count} | ❌ DIE: {self.die_count}"
        self.result_text.setText("\n".join(self.results) + summary)


        def apply_proxy_replacements(self):
            new_proxies = [p.strip() for p in self.replace_box.toPlainText().splitlines() if p.strip()]
            for i, idx in enumerate(self.die_indexes):
                if i < len(new_proxies):
                    self.accounts[idx][1] = new_proxies[i]

class AccountWorker(QThread):
    update_signal = pyqtSignal(int, str)  # Cập nhật điểm cho tài khoản
    log_signal = pyqtSignal(str)  # Cập nhật log

    def __init__(self, accounts, selected_rows):
        super().__init__()
        self.accounts = accounts
        self.selected_rows = selected_rows

    def run(self):
        for row in self.selected_rows:
            try:
                account = self.accounts[row]
                token=account[0]
                proxy=account[1]
                f_id=account[4]
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                headers={
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": f_id,
                    "token": token,
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "referer": "https://m.okvip7.live/",
                }
                responsediem=requests.get("https://m.okvip7.live/api/wallet/getWallet",headers=headers, proxies=proxies , timeout=500).json()
                
                print(responsediem)
                self.log_signal.emit(f"Đang xử lý tài khoản: {account[2]}")
                account[5] =f"{responsediem["data"]['integral']}"  
                account[6] = "Hoàn thành Lấy Điểm"
                self.update_signal.emit(row, account[5])  
                self.log_signal.emit(f"Đã hoàn thành tài khoản: {account[2]}")
            except:
                print("Lỗi",account)





class LienKetWorker(QThread):
    result_signal = pyqtSignal(int, str, str)  # row, message, color

    def __init__(self, accounts, row, check_func, table):
        super().__init__()
        self.accounts = accounts
        self.row = row
        self.check_func = check_func
        self.table = table  # ✅ Thêm tham chiếu đến bảng

    def DangNhap(self, account, passwordf, proxy, f_id):
        def get_captcha_text(proxies):
            def is_invalid(text):
                return not re.match("^[a-zA-Z0-9]+$", text)

            text, uuid, tries = "", "", 0
            while len(text) < 4 or is_invalid(text):
                tries += 1
                try:
                    img = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies, timeout=500).json()
                    img_src, uuid = img['data']['image'], img['data']['uuid']
                    ocr_response = requests.post("http://103.77.242.210:8000/ocr", headers={"accept": "application/json"}, data={"image": img_src}, timeout=500).json()
                    text = ocr_response['data']
                except:
                    time.sleep(2)
            return uuid, text

        try:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {"http": proxy_address, "https": proxy_address}

            uuid, code = get_captcha_text(proxies)
            password_md5 = hashlib.md5(passwordf.encode('utf-8')).hexdigest()

            headers = {
                "authority": "m.okvip7.live",
                "accept": "application/json, text/plain, */*",
                "accept-language": "vi-VN,vi;q=0.9",
                "content-type": "application/json",
                "locale": "vi_vn",
                "origin": "https://m.okvip7.live",
                "priority": "u=1, i",
                "referer": "https://m.okvip7.live/login",
                "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user_agent": "Mozilla/5.0",
                "f-id": f_id
            }

            data = {
                "account": account,
                "password": password_md5,
                "code": code,
                "uuid": uuid,
                "device": "H5"
            }

            response = requests.post("https://m.okvip7.live/api/accountLogin/doLogin", headers=headers, json=data, proxies=proxies, timeout=500)
            if response.json()['message']=="Mã xác nhận sai":
                uuid, code = get_captcha_text(proxies)
                data = {
                    "account": account,
                    "password": password_md5,
                    "code": code,
                    "uuid": uuid,
                    "device": "H5"
                }
                response = requests.post("https://m.okvip7.live/api/accountLogin/doLogin", headers=headers, json=data, proxies=proxies, timeout=500)

            if response.json().get("message") == "Thao tác thành công":
                return response.json()["data"]["token"],"DONE"
            else:
                return None ,response.text
        except:
            return None,"Không Lý Do"

    def run(self):
        try:
            account = self.accounts[self.row]
            token = account[0]
            proxy = account[1]
            username = account[2]
            password = account[3]
            f_id = account[4]

            headers = {
                "authority": "m.okvip7.live",
                "accept": "application/json, text/plain, */*",
                "accept-language": "vi-VN,vi;q=0.9",
                "content-type": "application/json",
                "locale": "vi_vn",
                "origin": "https://m.okvip7.live",
                "priority": "u=1, i",
                "referer": "https://m.okvip7.live/login",
                "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user_agent": "Mozilla/5.0",
                "f-id": f_id,
                "token": token
            }

            proxy_url, port, user, pwd = proxy.split(':')
            proxy_address = f"http://{user}:{pwd}@{proxy_url}:{port}"
            proxies = {"http": proxy_address, "https": proxy_address}

            # Nếu chưa đăng nhập hợp lệ thì thử đăng nhập lại
            if not self.check_func(self.row):
                self.result_signal.emit(self.row, "[❌❌❌] Chờ Đăng Nhập Thử Lại", "red")
                token,log = self.DangNhap(username, password, proxy, f_id)
                if token is None:
                    self.result_signal.emit(self.row, "[❌❌❌] Đã Thử Đăng Nhập Nhưng Thất Bại", "red")
                    print(log)
                else:
                    self.table.setItem(self.row, 0, QTableWidgetItem(token))  # ✅ Ghi token mới vào cột 0
                    account[0] = token
                    headers["token"] = token
                    try:
                        response = requests.get("https://m.okvip7.live/api/wallet/getWallet", headers=headers, proxies=proxies, timeout=500).json()
                        diem = response['data']['integral']
                        self.result_signal.emit(self.row, f"[✅✅✅] Đã Đăng Nhập Lại [{diem}]", "green")
                    except:
                        self.result_signal.emit(self.row, "[❌❌❌] Gọi API Lấy Điểm Thất Bại", "red")
                return

            # Gọi API kiểm tra liên kết
            response = requests.get("https://m.okvip7.live/api/website/listForWallet", headers=headers, proxies=proxies, timeout=500).json()
            is_linked = any(site.get("isBind", False) for site in response.get("data", []))

            if is_linked:
                self.result_signal.emit(self.row, "✅ Đã Có Liên Kết", "green")
            else:
                self.result_signal.emit(self.row, "❌ Chưa Liên Kết", "red")
                fake = Faker('vi_VN')
                lock = threading.Lock()

                # Proxy settings
                proxy="180.214.239.215:20211:nhjv2q6b:nHjV2q6B"
                host, port, userss, pwd = proxy.split(":")
                proxy_url = f"http://{userss}:{pwd}@{host}:{port}"
                proxies = {"http": proxy_url, "https": proxy_url}

                # Global session
                session = requests.Session()
                session.headers = {
                    "Content-Type": "application/json",
                    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
                    "origin": "https://www.010070.com",
                    "priority": "u=1, i",
                    "referer": "https://www.010070.com/vit/home/index/in-play",
                    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-kzapi-domain": "www.010070.com",
                    "x-kzapi-language": "vit",
                    "x-kzapi-platform": "web",
                    "x-kzapi-timezone": "+07:00",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
                }

                # --- Functions ---

                def encrypt_data(data: str, public_key: str):
                    rsa_key = RSA.import_key(public_key)
                    cipher = PKCS1_v1_5.new(rsa_key)
                    encrypted_bytes = cipher.encrypt(data.encode())
                    return base64.b64encode(encrypted_bytes).decode()

                def get_encryption_key():
                    url = "https://www.010070.com/api/encryption-key"
                    payload = "{}"
                    response = session.post(url, data=payload)
                    if response.status_code == 200:
                        return response.json()['data']['publicKey']
                    else:
                        return None

                def random_string(length=10):
                    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

                def random_number(length=8):
                    return '9' + ''.join(random.choices(string.digits, k=length))

                def random_STK():
                    return ''.join(random.choices(string.digits, k=random.randint(9,12)))

                def get_random_name():
                    try:
                        url = 'https://story-shack-cdn-v2.glitch.me/generators/vietnamese-name-generator/'
                        response = requests.get(url)
                        random_sex = random.choice(['male', 'female'])
                        return response.json()['data'][random_sex]
                    except:
                        return 'Nguyen Van Thinh'

                def remove_accents(text: str):
                    if text:
                        return unidecode(text)
                    else:
                        return ''

                def add_card(bankCode: str, account: str, stk: str):
                    try:
                        url = "https://www.010070.com/api/add-bankcard"
                        payload = {
                            "bankCode": bankCode,
                            "account": account,
                            "card": stk,
                            "bankNode": "HA NOI",
                            "note": "",
                            "needSms": False,
                            "smsCode": "",
                            "smsPhoneNo": "",
                            "smsPhoneNoCountry": "vn",
                            "bankpassbook": "",
                            "addrA": "",
                            "addrB": "",
                            "ifsccode": ""
                        }
                        response = session.post(url, json=payload, proxies=proxies)
                        if response.status_code == 200 and response.json()['status'] == 0:
                            print(f"✅ Thêm bank thành công: {stk}")
                            return True
                        else:
                            print(f"❌ Thêm bank thất bại: {stk} | {response.json().get('message')}")
                            return False
                    except Exception:
                        traceback.print_exc()
                        return False

                def do_register():
                    try:
                        url = "https://www.010070.com/api/register-account-v2"
                        user = random_string(9)
                        fullname = get_random_name()
                        fullname = remove_accents(fullname).upper()
                        password = random_string(12) + '0a'
                        phone = random_number()
                        print(f"Đăng ký với: {user}, {password}, {fullname}")

                        payload = {
                            "verifycode": "",
                            "email": "",
                            "joinpwd": encrypt_data(password, get_encryption_key()),
                            "joiname": user,
                            "birthmonth": random.randint(1, 12),
                            "birthyear": random.randint(1980, 2005),
                            "jsessionid": random_string(32).upper(),
                            "birthday": None,
                            "fullname": fullname,
                            "nickname": "",
                            "agc": "12531",
                            "wdpassword": "",
                            "weixin": "",
                            "line": "",
                            "whatsapp": "",
                            "telegram": "",
                            "facebook": "",
                            "tiktok": "",
                            "x": "",
                            "zalo": "",
                            "google": "",
                            "skype": "",
                            "qq": "",
                            "regpath": "/vit/home/index/in-play",
                            "emailcode": "",
                            "smscode": "",
                            "autologin": "1",
                            "redirectedFromDomain": "www.010070.com",
                            "gpn": "",
                            "rfc": "",
                            "adminreferal": None,
                            "utm_code": None,
                            "visitor_id": None,
                            "captchaValidate": "",
                            "wtdCardBankCode": "",
                            "wtdCardBankName": "Tên ngân hàng",
                            "wtdCardNumber": "",
                            "uphonecountry": "vn",
                            "uphone": phone
                        }

                        response = session.post(url, json=payload, proxies=proxies)
                        if response.status_code == 200 and response.json()['status'] == 0:
                            user_token = response.json()['data']['_userToken']
                            session.headers['x-kzapi-User'] = user_token

                            # Thêm bank sau khi đăng ký
                            for _ in range(3):
                                stk = random_STK()
                                if add_card("VNVCB", fullname, stk):
                                    break

                            return user, password, fullname, phone
                        else:
                            print(f"❌ Đăng ký thất bại: {response.text}")
                            return False
                    except Exception:
                        traceback.print_exc()
                        return False

                def create_account_and_save():
                    status = do_register()
                    if status:
                        user, password, fullname, phone = status
                        print(f"✅ Tạo thành công: {user}")
                        return user,phone
                    else:
                        print("❌ Đăng ký thất bại.")

                gameAccount,fullPhone=create_account_and_save()
                gamePhone = fullPhone[-4:]

              
                # Tạo data gửi
                data = {
                    "gameAccount": gameAccount,
                    "gamePhone": gamePhone,
                    "websiteId": "1798608608416931842",
                    "memberCode": "OK9"
                }

                try:
                    response = requests.post(
                        "https://m.okvip7.live/api/wallet/bindGameAccount",
                        headers=headers,
                        proxies=proxies,
                        json=data,
                        timeout=20
                    )
                    message = response.json().get('message', '')
                    print(message)
                    self.result_signal.emit(self.row, f"{message}", "red")
                  
                except Exception as e:
                    print(f"Lỗi gửi request: {e}")
                    self.result_signal.emit(self.row, f"Lỗi gửi request: {e}", "red")
                response = requests.get("https://m.okvip7.live/api/website/listForWallet", headers=headers, proxies=proxies, timeout=500).json()
                is_linked = any(site.get("isBind", False) for site in response.get("data", []))

                if is_linked:
                    self.result_signal.emit(self.row, "✅ Đã Có Liên Kết", "green")
                else:
                    self.result_signal.emit(self.row, "❌ Chưa Liên Kết", "red")


        except Exception as e:
            self.result_signal.emit(self.row, f"❌ Lỗi: {str(e)}", "red")



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.accounts = []  # Dữ liệu tài khoản
        self.threads = []  # Danh sách luồng đang chạy

        self.init_ui()
        self.load_accounts_from_file()
        self.start_auto_save()
    def open_proxy_checker(self):
        dlg = ProxyCheckDialog(self.accounts, self)
        if dlg.exec():
            dlg.apply_proxy_replacements()
            self.reload_table()
            self.save_accounts_to_file()

    def init_ui(self):
        self.setWindowTitle("Quản lý tài khoản")
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout(self)

        # TABLE
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Token", "Proxy", "User", "Pass", "F_ID", "Điểm", "Status", "Note"])
        self.table.setStyleSheet("QTableWidget {font-size: 14px;}")
        layout.addWidget(self.table)

        # Spinbox số luồng
        self.spinbox = QSpinBox(self)
        self.spinbox.setRange(1, 10)
        self.spinbox.setValue(1)
        self.spinbox.setStyleSheet("QSpinBox {font-size: 14px;}")
        layout.addWidget(self.spinbox)

        # Status
        status_layout = QHBoxLayout()
        self.log_label = QLabel(self)
        self.log_label.setStyleSheet("QLabel {font-size: 12px; color: green;}")
        status_layout.addWidget(self.log_label)

        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("QLabel {font-size: 12px; color: blue;}")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

        # Label tổng điểm
        self.total_points_label = QLabel("Tổng điểm: 0 | Tổng tài khoản: 0 | Điểm cao nhất: 0", self)
        self.total_points_label.setStyleSheet("QLabel {font-size: 14px; color: red;}")
        self.total_points_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_points_label)

        # ============ NÚT MENU ============ 
        self.menu_button = QPushButton("☰ Menu", self)
        self.menu_button.setStyleSheet("QPushButton {font-size: 16px; padding: 8px;}")
        self.menu_button.clicked.connect(self.toggle_menu)
        layout.addWidget(self.menu_button)

        # Các nút chức năng (Ẩn ban đầu)
        self.theme_button = QPushButton("🌙 Chế độ Tối")
        self.sort_asc_button = QPushButton("🔼 Lọc điểm: Thấp → Cao")
        self.sort_desc_button = QPushButton("🔽 Lọc điểm: Cao → Thấp")
        self.reset_button = QPushButton("🔁 Reset vị trí ban đầu")
        self.proxy_check_button = QPushButton("🧪 Kiểm Tra Proxy")
        self.backup_button = QPushButton("🛡️ Backup Tài Khoản")
        self.status_filter_combo = QComboBox()

        for widget in [self.theme_button, self.sort_asc_button, self.sort_desc_button,
                       self.reset_button, self.proxy_check_button, self.backup_button, self.status_filter_combo]:
            widget.hide()  # Ẩn ban đầu
            layout.addWidget(widget)

        # Kết nối các nút với hành động
        self.theme_button.clicked.connect(self.toggle_theme)
        self.sort_asc_button.clicked.connect(self.sort_by_points_asc)
        self.sort_desc_button.clicked.connect(self.sort_by_points_desc)
        self.reset_button.clicked.connect(self.reset_table)
        self.proxy_check_button.clicked.connect(self.open_proxy_checker1)
        self.backup_button.clicked.connect(self.backup_accounts)
        self.status_filter_combo.currentTextChanged.connect(self.filter_by_status)

        # Bộ đếm trạng thái menu
        self.menu_open = False

        self.setLayout(layout)
    def toggle_menu(self):
        # Khi bấm nút MENU
        if self.menu_open:
            # Ẩn các nút chức năng
            self.theme_button.hide()
            self.sort_asc_button.hide()
            self.sort_desc_button.hide()
            self.reset_button.hide()
            self.proxy_check_button.hide()
            self.backup_button.hide()
            self.status_filter_combo.hide()
            self.menu_button.setText("☰ Menu")
        else:
            # Hiện các nút chức năng
            self.theme_button.show()
            self.sort_asc_button.show()
            self.sort_desc_button.show()
            self.reset_button.show()
            self.proxy_check_button.show()
            self.backup_button.show()
            self.status_filter_combo.show()
            self.menu_button.setText("✖ Đóng Menu")
        self.menu_open = not self.menu_open

    def backup_accounts(self):
        try:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"ACC_backup_{now}.txt"
            with open("ACC.txt", "r", encoding="utf-8") as f_original, open(backup_filename, "w", encoding="utf-8") as f_backup:
                f_backup.write(f_original.read())
            self.log_label.setText(f"Đã backup thành: {backup_filename}")
        except Exception as e:
            self.log_label.setText(f"Lỗi backup: {str(e)}")

    def filter_by_status(self, selected_status):
        if selected_status == "ALL":
            self.reload_table()
            return

        self.table.setRowCount(0)
        for acc in self.accounts:
            status = acc[6] if len(acc) > 6 else ""
            if selected_status == status:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, value in enumerate(acc):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)

    def update_status_filter(self):
        status_set = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 6)  # Cột status
            if item:
                status_set.add(item.text().strip())

        current = self.status_filter_combo.currentText()
        self.status_filter_combo.blockSignals(True)
        self.status_filter_combo.clear()
        self.status_filter_combo.addItem("ALL")
        self.status_filter_combo.addItems(sorted(status_set))
        self.status_filter_combo.setCurrentText(current)
        self.status_filter_combo.blockSignals(False)


    def sort_by_points_asc(self):
        self.accounts.sort(key=lambda acc: int(acc[5]) if acc[5].isdigit() else 0)
        self.reload_table()

    def sort_by_points_desc(self):
        self.accounts.sort(key=lambda acc: int(acc[5]) if acc[5].isdigit() else 0, reverse=True)
        self.reload_table()

    def reset_table(self):
        self.load_accounts_from_file()

    def reload_table(self):
        self.table.setRowCount(0)
        for data in self.accounts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
        self.update_status_filter()

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: white;
                }
                QTableWidget, QSpinBox, QLabel {
                    background-color: #1e1e1e;
                    color: white;
                    border: 1px solid #333;
                }
                QPushButton {
                    background-color: #333;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)
            self.theme_button.setText("☀️ Chế độ Sáng")
        else:
            self.theme = "light"
            self.setStyleSheet("")
            self.theme_button.setText("🌙 Chế độ Tối")


    def load_accounts_from_file(self):
        try:
            # Xóa bảng và danh sách cũ
            self.table.setRowCount(0)
            self.accounts.clear()
            self.update_status_filter()
            with open("ACC.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    data = line.strip().split("|")
                    while len(data) < 8:
                        data.append("")
                    self.accounts.append(data)
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    for col, value in enumerate(data):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.table.setItem(row, col, item)
                    self.table.setItem(row, 5, QTableWidgetItem(data[5] if data[5] else "0"))
                    self.table.setItem(row, 6, QTableWidgetItem(data[6] if data[6] else "Chưa xử lý"))
                    self.table.setItem(row, 7, QTableWidgetItem(data[7]))  # Note
                    self.update_status_filter()

        except Exception as e:
            self.log_label.setText(f"Lỗi khi đọc file: {str(e)}")

    def save_accounts_to_file(self):

        try:
            self.update_total_points()

            with open("ACC.txt", "w", encoding="utf-8") as f:
                for row in range(self.table.rowCount()):
                    values = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        values.append(item.text() if item else "")
                    f.write("|".join(values) + "\n")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_label.setText(f"Đã lưu lại thông tin vào file lúc {timestamp}.")
        except Exception as e:
            self.log_label.setText(f"Lỗi khi lưu file: {str(e)}")


    def update_total_points(self):
        total = 0
        max_point = 0
        count = self.table.rowCount()
        for row in range(count):
            item = self.table.item(row, 5)
            if item:
                try:
                    point = int(item.text())
                    total += point
                    if point > max_point:
                        max_point = point
                except ValueError:
                    continue
        self.total_points_label.setText(
            f"Tổng điểm: {total} | Tổng tài khoản: {count} | Điểm cao nhất: {max_point}"
        )


    def start_auto_save(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_accounts_to_file)
        self.timer.start(3000)  # Lưu lại sau mỗi 5 giây

    def show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu(self)
        load = menu.addAction("LOAD")

        add_note_action = menu.addAction("📝 Thêm Note")
        get_points_action = menu.addAction("🎯 Lấy Điểm")
        CheckLuotTraLoi = menu.addAction("🎯 Kiểm Tra Lượt Trả Lời")
        CheckGhepChu = menu.addAction("🧩 Kiểm Tra Lượt Ghép Chữ")
        TokenGet = menu.addAction("Get Token")
        ChAyAll= menu.addAction("Chạy ALL")
        Bu9diem=menu.addAction("Điểm Danh")
        lienkettaikhoan=menu.addAction("Login+Liên Kết + Lấy Điểm + Lấy Token")
        CheckCacLienKet=menu.addAction("Check Liên Kết")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == load:self.load_accounts_from_file()

        if action == add_note_action:
            selected_row = self.table.currentRow()
            note, ok = QInputDialog.getText(self, "Thêm Note", "Nhập note cho tài khoản:")
            if ok:
                self.table.setItem(selected_row, 7, QTableWidgetItem(note))
                self.save_accounts_to_file()

        if action == get_points_action:
            selected_rows = [index.row() for index in self.table.selectedIndexes()]

            if not selected_rows:  # Kiểm tra xem có tài khoản nào được chọn không
                return
            num_threads = self.spinbox.value()

            # Chạy nhiều luồng đồng thời
            self.run_multiple_threads(selected_rows, num_threads)
        if action == CheckLuotTraLoi:
            luong = threading.Thread(target=self.CheckLuotTraLoi)
            luong.start()

        if action == CheckGhepChu:
            luong = threading.Thread(target=self.CheckGhepChu)
            luong.start()
        
        if action == TokenGet:
            luong = threading.Thread(target=self.TokenGet)
            luong.start()
       
        if action == ChAyAll:
            luong = threading.Thread(target=self.ChAyAll)
            luong.start()
        if action == Bu9diem:
            luong = threading.Thread(target=self.Bu9diem)
            luong.start()
        if action == lienkettaikhoan:
            luong = threading.Thread(target=self.lienkettaikhoan)
            luong.start()
        if action == CheckCacLienKet:
            luong = threading.Thread(target=self.CheckCacLienKet)
            luong.start()
       
    def open_proxy_checker1(self):
        luong = threading.Thread(target=self.open_proxy_checker)
        luong.start()    
    def checkloginn(self):
        for row in range(self.table.rowCount()):
            try:
                token = self.table.item(row, 0).text()
                proxy=self.table.item(row, 1).text()
                Fidd=self.table.item(row, 4).text()
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                headers={
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": Fidd,
                    "token": token,
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "referer": "https://m.okvip7.live/",
                }
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                responsediem=requests.get("https://m.okvip7.live/api/wallet/getWallet",headers=headers, proxies=proxies , timeout=500).json()
                diem=responsediem['data']['integral']
                self.table.setItem(row, 5, QTableWidgetItem(f"{diem}"))
            except:pass
            self.table.setItem(row, 6, QTableWidgetItem(f"{responsediem}"))

    def CheckLoginssssss(self,row):
            try:
                token = self.table.item(row, 0).text()
                proxy=self.table.item(row, 1).text()
                Fidd=self.table.item(row, 4).text()
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                headers={
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": Fidd,
                    "token": token,
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "referer": "https://m.okvip7.live/",
                }
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                responsediem=requests.get("https://m.okvip7.live/api/wallet/getWallet",headers=headers, proxies=proxies , timeout=500).json()
                diem=responsediem['data']['integral']
                self.table.setItem(row, 5, QTableWidgetItem(f"{diem}"))
                return True
            except:
                return False



    
    def update_link_status(self, row, message, color):
        item = QTableWidgetItem(message)
        item.setForeground(QBrush(QColor(color)))
        self.table.setItem(row, 6, item)

    def lienkettaikhoan(self):
        from concurrent.futures import ThreadPoolExecutor

        def start_worker(row):
            worker = LienKetWorker(self.accounts, row, self.CheckLoginssssss, self.table)  # ✅ đã thêm self.table
            worker.result_signal.connect(self.update_link_status)
            worker.start()
            self.threads.append(worker)


        with ThreadPoolExecutor(max_workers=20) as executor:
            for row in range(self.table.rowCount()):
                executor.submit(start_worker, row)

    def Bu9diem(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def chay_20_mot_luot():
            def xu_ly_row(row):
                token = self.table.item(row, 0).text()
                proxy=self.table.item(row, 1).text()
                Fidd=self.table.item(row, 4).text()
                url = "https://m.okvip7.live/api/activitySignIn/singIn"

                headers = {
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "referer": "https://m.okvip7.live/login",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": Fidd,
                    "token": token
                }
                self.table.setItem(row, 6, QTableWidgetItem(f"sdasda2222222sdsa"))

                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                self.table.setItem(row, 6, QTableWidgetItem(f"Bú"))

                response = requests.post(url, headers=headers, proxies=proxies ,timeout=500)
                print(response.text)
                aaaaaaaaaaaa=response.json()["data"]["continueDays"]
                
                response = requests.get("https://m.okvip7.live/api/accountLogin/updateOnline", headers=headers, proxies=proxies ,timeout=500)
                self.table.setItem(row, 6, QTableWidgetItem(f"Điểm Danh Thành CÔng Ngày : {aaaaaaaaaaaa}"))

            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(xu_ly_row, row) for row in range(self.table.rowCount())]
                for future in as_completed(futures):
                    pass  # bạn có thể xử lý kết quả hoặc log tại đây nếu cần
        chay_20_mot_luot() 
    def CheckCacLienKet(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def chay_20_mot_luot():
            def xu_ly_row(row):
                token = self.table.item(row, 0).text()
                proxy=self.table.item(row, 1).text()
                Fidd=self.table.item(row, 4).text()
                headers = {
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "referer": "https://m.okvip7.live/login",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": Fidd,
                    "token": token
                }
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                response = requests.get("https://m.okvip7.live/api/website/listForWallet", headers=headers, proxies=proxies, timeout=500).json()
               # Lấy các giá trị isBind từ response
                MB66 = response['data'][0]["isBind"]
                OK9 = response['data'][1]["isBind"]
                s78win = response['data'][2]["isBind"]
                QQ88 = response['data'][3]["isBind"]
                F168 = response['data'][4]["isBind"]

                # Tạo danh sách tên ứng với giá trị True
                bindings = []
                if MB66: bindings.append("MB66")
                if OK9: bindings.append("OK9")
                if s78win: bindings.append("78win")
                if QQ88: bindings.append("QQ88")
                if F168: bindings.append("F168")

                # Hiển thị chuỗi kết quả, ngăn cách bằng " | "
                result_text = " | ".join(bindings)

                # Hiển thị trong bảng
                self.table.setItem(row, 7, QTableWidgetItem(result_text))

                self.table.setItem(row, 6, QTableWidgetItem(f"Hoàn Thành Lấy Liên Kết"))

            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(xu_ly_row, row) for row in range(self.table.rowCount())]
                for future in as_completed(futures):
                    pass  # bạn có thể xử lý kết quả hoặc log tại đây nếu cần
        chay_20_mot_luot()    
    def ChAyAll(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def chay_20_mot_luot():
            def xu_ly_row(row):
                self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Đầu"))
                self.table.setItem(row, 6, QTableWidgetItem(f"Check Token"))

                chechDangNhap=self.CheckLoginssssss(row)
                print(chechDangNhap)
                if chechDangNhap:
                    self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Trả Lời Câu Hỏi"))
                    self.CheckLuotTraLoiall(row)
                    self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Quay Chữ"))
                    self.CheckGhepChuall(row)
                    self.table.setItem(row, 6, QTableWidgetItem(f"💟💟💟💟💟!"))
                else:
                    self.table.setItem(row, 6, QTableWidgetItem(f"[💩]> Token Chết MẸ Rồi em!"))

            with ThreadPoolExecutor(max_workers=35) as executor:
                futures = [executor.submit(xu_ly_row, row) for row in range(self.table.rowCount())]
                for future in as_completed(futures):
                    pass  # bạn có thể xử lý kết quả hoặc log tại đây nếu cần
        chay_20_mot_luot()
    
    def TokenGetsl(self):
        def login_to_account(account, passwordf, proxy,f_id):
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {
                "http": proxy_address,
                "https": proxy_address
            }
            import requests
            import random
            import hashlib
            import json
            import time
            import concurrent.futures
            import re
            
            uuid, code = get_captcha_text(proxies)
            md5_hash = hashlib.md5()
            md5_hash.update(passwordf.encode('utf-8'))
            passwordf = md5_hash.hexdigest()
            print(uuid, code)
            url = "https://m.okvip7.live/api/accountLogin/doLogin"
            headers = {
                "authority": "m.okvip7.live",
                "accept": "application/json, text/plain, */*",
                "accept-language": "vi-VN,vi;q=0.9",
                "content-type": "application/json",
                "locale": "vi_vn",
                "origin": "https://m.okvip7.live",
                "priority": "u=1, i",
                "referer": "https://m.okvip7.live/login",
                "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "f-id": f_id
            }
            data = {
                "account": account,
                "password": passwordf,
                "code": code,
                "uuid": uuid,
                "device": "H5"
            }

            # Nếu proxy không phải là None, thêm vào tham số proxies
            if proxy:
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                response = requests.post(url, headers=headers, json=data, proxies=proxies ,timeout=20)
            else:
                response = requests.post(url, headers=headers, json=data,timeout=20)
            print(response.text)
            # Kiểm tra phản hồi
            if response.json()['message'] == 'Thao tác thành công':
                token = response.json()['data']['token']
                return f'{token}'
            elif response.json()['message'] == 'Mã xác nhận sai':
                login_to_account(account, password, proxy,f_id)
            else:
                return None
        def kiem_tra_ky_tu(chuoi):
            return not re.match("^[a-zA-Z0-9]+$", chuoi)
        def get_captcha_text(proxies):
            solan = 0
            text = ""
            while len(text) < 4 or kiem_tra_ky_tu(text):
                solan += 1
                if solan >= 2:
                    try:IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies ,timeout=20).json()
                    except:pass
                    solan = 0
                try:
                    IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies ,timeout=20).json()
                    img_src = IMG['data']['image']
                    uuid = IMG['data']['uuid']
                    url = "http://103.77.242.210:8000/ocr"
                    headers = {"accept": "application/json"}
                    data = {"image": img_src}
                    response = requests.post(url, headers=headers, data=data,timeout=20)
                    print(response.json()['data'])
                    text=response.json()['data']
                except:pass
                print("captcha: ",text)
            return uuid,text
        def LayToken(account, password, proxy,f_id):
            return login_to_account(account, password, proxy,f_id)
        for row in range(self.table.rowCount()):
            token = self.table.item(row, 0).text()
            proxy=self.table.item(row, 1).text()
            Taikhoan=self.table.item(row, 2).text()
            Matkhau=self.table.item(row, 3).text()
            Fidd=self.table.item(row, 4).text()
            tokennew=LayToken(Taikhoan, Matkhau, proxy,Fidd)
            self.table.setItem(row, 0, QTableWidgetItem(f"{tokennew}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"Đã Lấy Token Mới"))
            time.sleep(3)

     

            
    def TokenGet(self):
        selected_row = self.table.currentRow()
        selected_rows = [index.row() for index in self.table.selectedIndexes()]
        for row in selected_rows:
            account = self.accounts[row]
            token = account[0]
            proxy = account[1]
            password = account[3]
            tkkk = account[2]
            print(row)
            f_id = account[4]
            self.table.setItem(row, 6, QTableWidgetItem("Bắt đầu kiểm tra"))
            print(token,account,proxy,f_id)
            def login_to_account(account, passwordf, proxy,f_id):
                passwordfcc=passwordf
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {
                    "http": proxy_address,
                    "https": proxy_address
                }
                print(passwordf)
                uuid, code = get_captcha_text(proxies)
                md5_hash = hashlib.md5()
                md5_hash.update(passwordf.encode('utf-8'))
                passwordf = md5_hash.hexdigest()
                print(uuid, code,passwordf)
                url = "https://m.okvip7.live/api/accountLogin/doLogin"
                headers = {
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "referer": "https://m.okvip7.live/login",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": f_id
                }
                data = {
                    "account": account,
                    "password": passwordf,
                    "code": code,
                    "uuid": uuid,
                    "device": "H5"
                }

                # Nếu proxy không phải là None, thêm vào tham số proxies
                if proxy:
                    proxy_url, port, username, password = proxy.split(':')
                    proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                    proxies = {
                        "http": proxy_address,
                        "https": proxy_address
                    }
                    response = requests.post(url, headers=headers, json=data, proxies=proxies ,timeout=500)
                else:
                    response = requests.post(url, headers=headers, json=data,timeout=500)
                print(response.text)
                # Kiểm tra phản hồi
                if response.json()['message'] == 'Thao tác thành công':
                    token = response.json()['data']['token']
                    return f'{token}|{proxy}|{account}|{passwordfcc}|{f_id}'
                elif response.json()['message'] == 'Mã xác nhận sai':
                    login_to_account(account, password, proxy,f_id)
                else:
                    return None
            def kiem_tra_ky_tu(chuoi):
                return not re.match("^[a-zA-Z0-9]+$", chuoi)
            def get_captcha_text(proxies):
                solan = 0
                text = ""
                while len(text) < 4 or kiem_tra_ky_tu(text):
                    IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies ,timeout=500).json()
                    solan += 1
                    if solan >= 5:
                        try:
                            IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies ,timeout=500).json()
                        except:
                            pass
                        solan = 0

                    try:

                        IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha", proxies=proxies ,timeout=500).json()

                        img_src = IMG['data']['image']
                        uuid = IMG['data']['uuid']
                        url = "http://103.77.242.210:8000/ocr"
                        headers = {"accept": "application/json"}
                        data = {"image": img_src}

                        response = requests.post(url, headers=headers, data=data,timeout=500)
                        print(response.json()['data'])
                        text=response.json()['data']
                    except:
                        time.sleep(1)
                    print(text)
                return uuid,text
        aaa=login_to_account(tkkk,password,proxy,f_id)
        def thay_doi_dong(file_path, dong_muon_thay, noi_dung_moi):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                if dong_muon_thay < 1 or dong_muon_thay > len(lines):
                    print(f"Dòng {dong_muon_thay} không tồn tại trong tệp.")
                    return

                lines[dong_muon_thay - 1] = noi_dung_moi + '\n'

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)
                self.table.setItem(selected_row, 0, QTableWidgetItem(f"{noi_dung_moi}"))

                print(f"Đã thay đổi dòng {dong_muon_thay} thành: {noi_dung_moi}")
                self.save_accounts_to_file()
            except FileNotFoundError:
                print(f"Tệp {file_path} không tồn tại.")

        thay_doi_dong("ACC.txt", row+1, f"{aaa}")
        self.load_accounts_from_file()
    def CheckLuotTraLoiall(self,selected_row):
        row=selected_row
        import random
        def lay_answer_list():
            if not hasattr(lay_answer_list, "shuffled_answers") or lay_answer_list.index >= len(lay_answer_list.shuffled_answers):
                # Gộp toàn bộ 15 câu
                all_answers = [
                    {"id":"1813068590722039810","submitAnswer":"B"},
                    {"id":"1885293145245704194","submitAnswer":"D"},
                    {"id":"1813055126444163073","submitAnswer":"B"},
                    {"id":"1758663639615070209","submitAnswer":"D"},
                    {"id":"1785300906974543873","submitAnswer":"B"},
                    {"id":"1832001421560930305","submitAnswer":"C"},
                    {"id":"1862969516842795009","submitAnswer":"A"},
                    {"id":"1813061385461415937","submitAnswer":"C"},
                    {"id":"1852195947499892738","submitAnswer":"C"},
                    {"id":"1845597110031245313","submitAnswer":"A"},
                    {"id":"1852198018005479426","submitAnswer":"B"},
                    {"id":"1785310696345862145","submitAnswer":"B"},
                    {"id":"1785286596449697793","submitAnswer":"D"},
                    {"id":"1742430977931452417","submitAnswer":"D"},
                    {"id":"1839964599813079042","submitAnswer":"D"},
                    {"id":"1854143870443585537","submitAnswer":"D"},
                    {"id":"1785518438150995969","submitAnswer":"B"},
                    {"id":"1824048832353558530","submitAnswer":"C"},
                    {"id":"1832922633518604290","submitAnswer":"A"},
                    {"id":"1845605186754994177","submitAnswer":"A"},
                    {"id":"1910234836605042689","submitAnswer":"C"},
                    {"id":"1743642787544043521","submitAnswer":"C"},
                    {"id":"1839623537886142465","submitAnswer":"B"},
                    {"id":"1857079383320297474","submitAnswer":"B"},
                    {"id":"1758729048947089409","submitAnswer":"D"},
                    {"id":"1913734370549690370","submitAnswer":"A"},
                    {"id":"1790399254207328258","submitAnswer":"A"},
                    {"id":"1758658110029225986","submitAnswer":"B"},
                    {"id":"1857079675314675714","submitAnswer":"C"},
                    {"id":"1906204991478239234","submitAnswer":"B"},
                    {"id":"1813068590722039810","submitAnswer":"B"},
                    {"id":"1758661648285360129","submitAnswer":"C"},
                    {"id":"1900874100297801729","submitAnswer":"A"},
                    {"id":"1785309013456879617","submitAnswer":"A"}

                ]
                random.shuffle(all_answers)  # Trộn kỹ mỗi lần làm mới
                lay_answer_list.shuffled_answers = all_answers
                lay_answer_list.index = 0

            # Lấy 5 câu liên tiếp
            start = lay_answer_list.index
            end = start + 5
            result = lay_answer_list.shuffled_answers[start:end]
            lay_answer_list.index += 5
            return result

        
        account = self.accounts[row]
        token = account[0]
        proxy = account[1]
        f_id = account[4]
        self.table.setItem(row, 6, QTableWidgetItem("Bắt đầu kiểm tra"))
        try:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {"http": proxy_address, "https": proxy_address}
            headers = {
                "authority": "m.okvip7.live",
                "accept": "application/json, text/plain, */*",
                "accept-language": "vi-VN,vi;q=0.9",
                "content-type": "application/json",
                "locale": "vi_vn",
                "origin": "https://m.okvip7.live",
                "priority": "u=1, i",
                "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "f-id": f_id,
                "token": token,
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "referer": "https://m.okvip7.live/",
            }
            response = requests.get(
                "https://m.okvip7.live/api/activityQuestion/getActivityQuestionInfo",
                headers=headers, proxies=proxies, timeout=500).json()
            luot = response['data']['surplusNumber']
            self.table.setItem(row, 6, QTableWidgetItem(f"Còn {luot} lượt"))
            account[6] = f"Còn {luot} lượt"
            self.update_log(f"{account[2]} còn {luot} lượt trả lời.")
            for cac in range(int(luot)):
                DanhSachCauHoi = requests.get('https://m.okvip7.live/api/activityQuestion/getQuestionList',headers=headers, proxies=proxies, timeout=500).json()['data']
                delay_time = random.randint(20, 35)
                for delay in range(delay_time, -1, -1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay}"))
                    time.sleep(1)
                date_time = int(time.time())
                recordNo = requests.get('https://m.okvip7.live/api/activityQuestion/startAnswerQuestion',headers=headers, proxies=proxies, timeout=500).json()['data']['recordNo']
                dataTraloi = {
                    "answerList": lay_answer_list(),
                    "timeStart": date_time,
                    "recordNo": recordNo
                }
                response = requests.post('https://m.okvip7.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi, proxies=proxies, timeout=500)
                print(response.json())
                time.sleep(3)
            print("Kimochi")
            CheckLuotQuay=requests.get("https://m.okvip7.live/api/lottery/getLuckyDrawBaseInfo",headers=headers , proxies=proxies , timeout=500).json()
            data2 = {"raffleId": CheckLuotQuay['data']['raffleId']}
            CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/getLuckyDrawInfoByDaily",headers=headers , proxies=proxies , timeout=500).json()['data']['drawCount']
            print(CheckLuotQuay)
            for xx in range(int(CheckLuotQuay)):
                CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/lotteryByDaily",headers=headers, json=data2 , proxies=proxies , timeout=500).json()
                delay_time = random.randint(5,6)
                for delay in range(delay_time, -1, -1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{CheckLuotQuay["data"]['prizeInfo']['prizeName']}]"))
                    time.sleep(1)
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Xong!"))

        except Exception as e:
            self.update_log(f"Lỗi kiểm tra lượt:")
    def CheckLuotTraLoi(self):
        selected_row = self.table.currentRow()
        import random
        def lay_answer_list():
            if not hasattr(lay_answer_list, "shuffled_answers") or lay_answer_list.index >= len(lay_answer_list.shuffled_answers):
                # Gộp toàn bộ 15 câu
                all_answers = [
                    {"id":"1813068590722039810","submitAnswer":"B"},
                    {"id":"1885293145245704194","submitAnswer":"D"},
                    {"id":"1813055126444163073","submitAnswer":"B"},
                    {"id":"1758663639615070209","submitAnswer":"D"},
                    {"id":"1785300906974543873","submitAnswer":"B"},
                    {"id":"1832001421560930305","submitAnswer":"C"},
                    {"id":"1862969516842795009","submitAnswer":"A"},
                    {"id":"1813061385461415937","submitAnswer":"C"},
                    {"id":"1852195947499892738","submitAnswer":"C"},
                    {"id":"1845597110031245313","submitAnswer":"A"},
                    {"id":"1852198018005479426","submitAnswer":"B"},
                    {"id":"1785310696345862145","submitAnswer":"B"},
                    {"id":"1785286596449697793","submitAnswer":"D"},
                    {"id":"1742430977931452417","submitAnswer":"D"},
                    {"id":"1839964599813079042","submitAnswer":"D"},
                    {"id":"1854143870443585537","submitAnswer":"D"},
                    {"id":"1785518438150995969","submitAnswer":"B"},
                    {"id":"1824048832353558530","submitAnswer":"C"},
                    {"id":"1832922633518604290","submitAnswer":"A"},
                    {"id":"1845605186754994177","submitAnswer":"A"},
                    {"id":"1910234836605042689","submitAnswer":"C"},
                    {"id":"1743642787544043521","submitAnswer":"C"},
                    {"id":"1839623537886142465","submitAnswer":"B"},
                    {"id":"1857079383320297474","submitAnswer":"B"},
                    {"id":"1758729048947089409","submitAnswer":"D"},
                    {"id":"1913734370549690370","submitAnswer":"A"},
                    {"id":"1790399254207328258","submitAnswer":"A"},
                    {"id":"1758658110029225986","submitAnswer":"B"},
                    {"id":"1857079675314675714","submitAnswer":"C"},
                    {"id":"1906204991478239234","submitAnswer":"B"},
                    {"id":"1813068590722039810","submitAnswer":"B"},
                    {"id":"1758661648285360129","submitAnswer":"C"},
                    {"id":"1900874100297801729","submitAnswer":"A"},
                    {"id":"1785309013456879617","submitAnswer":"A"}

                ]
                random.shuffle(all_answers)  # Trộn kỹ mỗi lần làm mới
                lay_answer_list.shuffled_answers = all_answers
                lay_answer_list.index = 0

            # Lấy 5 câu liên tiếp
            start = lay_answer_list.index
            end = start + 5
            result = lay_answer_list.shuffled_answers[start:end]
            lay_answer_list.index += 5
            return result

        selected_rows = [index.row() for index in self.table.selectedIndexes()]
        for row in selected_rows:
            account = self.accounts[row]
            token = account[0]
            proxy = account[1]
            f_id = account[4]
            self.table.setItem(row, 6, QTableWidgetItem("Bắt đầu kiểm tra"))
            try:
                proxy_url, port, username, password = proxy.split(':')
                proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
                proxies = {"http": proxy_address, "https": proxy_address}
                headers = {
                    "authority": "m.okvip7.live",
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi-VN,vi;q=0.9",
                    "content-type": "application/json",
                    "locale": "vi_vn",
                    "origin": "https://m.okvip7.live",
                    "priority": "u=1, i",
                    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "f-id": f_id,
                    "token": token,
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "referer": "https://m.okvip7.live/",
                }
                response = requests.get(
                    "https://m.okvip7.live/api/activityQuestion/getActivityQuestionInfo",
                    headers=headers, proxies=proxies, timeout=500).json()
                luot = response['data']['surplusNumber']
                self.table.setItem(row, 6, QTableWidgetItem(f"Còn {luot} lượt"))
                account[6] = f"Còn {luot} lượt"
                self.update_log(f"{account[2]} còn {luot} lượt trả lời.")
                for cac in range(int(luot)):
                    DanhSachCauHoi = requests.get('https://m.okvip7.live/api/activityQuestion/getQuestionList',headers=headers, proxies=proxies, timeout=500).json()['data']
                    delay_time = random.randint(20, 35)
                    for delay in range(delay_time, -1, -1):
                        self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay}"))
                        time.sleep(1)
                    date_time = int(time.time())
                    recordNo = requests.get('https://m.okvip7.live/api/activityQuestion/startAnswerQuestion',headers=headers, proxies=proxies, timeout=500).json()['data']['recordNo']
                    dataTraloi = {
                        "answerList": lay_answer_list(),
                        "timeStart": date_time,
                        "recordNo": recordNo
                    }
                    response = requests.post('https://m.okvip7.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi, proxies=proxies, timeout=500)
                    print(response.json())
                    time.sleep(3)
                print("Kimochi")
                CheckLuotQuay=requests.get("https://m.okvip7.live/api/lottery/getLuckyDrawBaseInfo",headers=headers , proxies=proxies , timeout=500).json()
                data2 = {"raffleId": CheckLuotQuay['data']['raffleId']}
                CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/getLuckyDrawInfoByDaily",headers=headers , proxies=proxies , timeout=500).json()['data']['drawCount']
                print(CheckLuotQuay)
                for xx in range(int(CheckLuotQuay)):
                    CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/lotteryByDaily",headers=headers, json=data2 , proxies=proxies , timeout=500).json()
                    delay_time = random.randint(5,6)
                    for delay in range(delay_time, -1, -1):
                        self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{CheckLuotQuay["data"]['prizeInfo']['prizeName']}]"))
                        time.sleep(1)
                self.table.setItem(selected_row, 6, QTableWidgetItem(f"Xong!"))

            except Exception as e:
                self.update_log(f"Lỗi kiểm tra lượt:")
    def CheckGhepChu(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        account = self.accounts[selected_row]
        token = account[0]
        proxy = account[1]
        f_id = account[4]

        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }

        headers = {
            "authority": "m.okvip7.live",
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi-VN,vi;q=0.9",
            "content-type": "application/json",
            "locale": "vi_vn",
            "origin": "https://m.okvip7.live",
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "f-id": f_id,
            "token": token,
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://m.okvip7.live/",
        }

        try:
            response = requests.get('https://m.okvip7.live/api/activityCollect/getListAvailable', headers=headers, proxies=proxies, timeout=500).json()
            idGame = response['data'][0]['id']
            data = {"id": idGame}
            draw_response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=500).json()
            draw_times = draw_response['data']['drawTimes']
            status_text = f"Lượt ghép chữ còn lại: {draw_times}"
            self.status_label.setText(status_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(status_text))  # Cập nhật cột Status (index = 3)
            for _ in range(int(draw_times)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/drawWord', headers=headers, json=data, proxies=proxies, timeout=500)
                print(response.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response.json()["data"]['textName']}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=500)
            synthesisTimes = response.json()['data']['synthesisTimes']
            data2 = {"raffleId": requests.get("https://m.okvip7.live/api/activityCollect/getListAvailable", headers=headers, proxies=proxies, timeout=500).json()['data'][0]['lotteryId']}
            for _ in range(int(synthesisTimes)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/mergeWord', headers=headers, json=data, proxies=proxies, timeout=500)
                response2 = requests.post('https://m.okvip7.live/api/lottery/lottery', headers=headers, json=data2, proxies=proxies, timeout=500)
                print(response2.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response2.json()["data"]["prizeInfo"]["prizeName"]}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Ghép Chữ Hoàn Tất!"))  # Cập nhật cột Status (index = 3)

            account[6] = status_text  # Cập nhật dữ liệu tài khoản nếu cần
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Ghép Chữ Hoàn Tất!!"))

        except Exception as e:
            error_text = f"Lỗi: {str(e)}"
            self.status_label.setText(error_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(error_text))  # Cập nhật lỗi vào Status

    def CheckGhepChuall(self,selected_row):
        row=selected_row

        account = self.accounts[selected_row]
        token = account[0]
        proxy = account[1]
        f_id = account[4]

        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }

        headers = {
            "authority": "m.okvip7.live",
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi-VN,vi;q=0.9",
            "content-type": "application/json",
            "locale": "vi_vn",
            "origin": "https://m.okvip7.live",
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "f-id": f_id,
            "token": token,
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://m.okvip7.live/",
        }

        try:
            response = requests.get('https://m.okvip7.live/api/activityCollect/getListAvailable', headers=headers, proxies=proxies, timeout=500).json()
            idGame = response['data'][0]['id']
            data = {"id": idGame}
            draw_response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=500).json()
            draw_times = draw_response['data']['drawTimes']
            status_text = f"Lượt ghép chữ còn lại: {draw_times}"
            self.status_label.setText(status_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(status_text))  # Cập nhật cột Status (index = 3)
            for _ in range(int(draw_times)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/drawWord', headers=headers, json=data, proxies=proxies, timeout=500)
                print(response.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response.json()["data"]['textName']}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=500)
            synthesisTimes = response.json()['data']['synthesisTimes']
            data2 = {"raffleId": requests.get("https://m.okvip7.live/api/activityCollect/getListAvailable", headers=headers, proxies=proxies, timeout=500).json()['data'][0]['lotteryId']}
            for _ in range(int(synthesisTimes)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/mergeWord', headers=headers, json=data, proxies=proxies, timeout=500)
                response2 = requests.post('https://m.okvip7.live/api/lottery/lottery', headers=headers, json=data2, proxies=proxies, timeout=500)
                print(response2.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response2.json()["data"]["prizeInfo"]["prizeName"]}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Ghép Chữ Hoàn Tất!"))  # Cập nhật cột Status (index = 3)

            account[6] = status_text  # Cập nhật dữ liệu tài khoản nếu cần
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Ghép Chữ Hoàn Tất!!"))

        except Exception as e:
            error_text = f"Lỗi: {str(e)}"
            self.status_label.setText(error_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(error_text))  # Cập nhật lỗi vào Status


    def run_multiple_threads(self, selected_rows, num_threads):
        # Chia các tài khoản đã chọn thành nhóm nhỏ theo số lượng luồng
        chunks = [selected_rows[i:i + num_threads] for i in range(0, len(selected_rows), num_threads)]
        
        for chunk in chunks:
            worker = AccountWorker(self.accounts, chunk)
            worker.update_signal.connect(self.update_account_status)
            worker.log_signal.connect(self.update_log)  # Connect the log signal
            worker.start()
            self.threads.append(worker)  # Track the thread

    def update_account_status(self, row, points):
        self.table.setItem(row, 5, QTableWidgetItem(points))  # Cập nhật điểm
        self.table.setItem(row, 6, QTableWidgetItem("Hoàn thành"))  # Đánh dấu hoàn thành
        self.save_accounts_to_file()  # Lưu lại điểm sau khi cập nhật

    def update_log(self, log_message):
        self.log_label.setText(log_message)

    def contextMenuEvent(self, event):
        self.show_context_menu(event.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
