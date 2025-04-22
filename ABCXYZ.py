import sys
import threading
import time
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMenu, QInputDialog, QLabel, QSpinBox, QHBoxLayout
from PyQt6.QtGui import QContextMenuEvent, QColor

import requests
import random
import hashlib
import json
import time
import concurrent.futures
import re
from datetime import datetime
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
                responsediem=requests.get("https://m.okvip7.live/api/wallet/getWallet",headers=headers, proxies=proxies ).json()
                
                print(responsediem)
                self.log_signal.emit(f"Đang xử lý tài khoản: {account[2]}")
                account[5] =f"{responsediem["data"]['integral']}"  # Giả lập điểm
                account[6] = "Hoàn thành Lấy Điểm"
                self.update_signal.emit(row, account[5])  
                self.log_signal.emit(f"Đã hoàn thành tài khoản: {account[2]}")
            except:
                print(account[2])



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.accounts = []  # Dữ liệu tài khoản
        self.threads = []  # Danh sách luồng đang chạy

        self.init_ui()
        self.load_accounts_from_file()
        self.start_auto_save()

    def init_ui(self):
        self.setWindowTitle("Quản lý tài khoản")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Token", "Proxy", "User", "Pass", "F_ID", "Điểm", "Status", "Note"])
        self.table.setStyleSheet("QTableWidget {font-size: 14px;}")
        layout.addWidget(self.table)
        self.spinbox = QSpinBox(self)
        self.spinbox.setRange(1, 10)
        self.spinbox.setValue(1)
        self.spinbox.setStyleSheet("QSpinBox {font-size: 14px;}")
        layout.addWidget(self.spinbox)
        status_layout = QHBoxLayout()
        self.log_label = QLabel(self)
        self.log_label.setStyleSheet("QLabel {font-size: 12px; color: green;}")
        status_layout.addWidget(self.log_label)
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("QLabel {font-size: 12px; color: blue;}")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        self.table.setColumnWidth(6, 280)
        self.table.setColumnWidth(7, 80)
        self.total_points_label = QLabel("Tổng điểm: 0 | Tổng tài khoản: 0 | Điểm cao nhất: 0", self)
        self.total_points_label.setStyleSheet("QLabel {font-size: 14px; color: red;}")
        self.total_points_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_points_label)


        self.setLayout(layout)

    def load_accounts_from_file(self):
        try:
            # Xóa bảng và danh sách cũ
            self.table.setRowCount(0)
            self.accounts.clear()

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
        TokenGetsl = menu.addAction("Get Token CHọn")
        ChAyAll= menu.addAction("Chạy ALL")

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
        if action == TokenGetsl:
            luong = threading.Thread(target=self.TokenGetsl)
            luong.start()
        if action == ChAyAll:
            luong = threading.Thread(target=self.ChAyAll)
            luong.start()
    def ChAyAll(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def chay_20_mot_luot():
            def xu_ly_row(row):
                self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Đầu"))
                self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Trả Lời Câu Hỏi"))
                self.CheckLuotTraLoiall(row)
                self.table.setItem(row, 6, QTableWidgetItem(f"Bắt Quay Chữ"))

                self.CheckGhepChuall(row)
                self.table.setItem(row, 6, QTableWidgetItem(f"Hoàn Thành Thành Công Tất Cả!"))

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(xu_ly_row, row) for row in range(self.table.rowCount())]
                for future in as_completed(futures):
                    pass  # bạn có thể xử lý kết quả hoặc log tại đây nếu cần
        chay_20_mot_luot()

    def TokenGetsl(self):
        def login_to_account(account, password, proxy,f_id):
            import requests
            import random
            import hashlib
            import json
            import time
            import concurrent.futures
            import re
            passwordf=password
            uuid, code = get_captcha_text()
            md5_hash = hashlib.md5()
            md5_hash.update(password.encode('utf-8'))
            password = md5_hash.hexdigest()
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
                "password": password,
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
                response = requests.post(url, headers=headers, json=data, proxies=proxies)
            else:
                response = requests.post(url, headers=headers, json=data)
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
        def get_captcha_text():
            solan = 0
            text = ""
            while len(text) < 4 or kiem_tra_ky_tu(text):
                solan += 1
                if solan >= 2:
                    try:IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha").json()
                    except:pass
                    solan = 0
                try:
                    IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha").json()
                    img_src = IMG['data']['image']
                    uuid = IMG['data']['uuid']
                    url = "http://103.77.242.210:8000/ocr"
                    headers = {"accept": "application/json"}
                    data = {"image": img_src}
                    response = requests.post(url, headers=headers, data=data)
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
            def login_to_account(account, password, proxy,f_id):
                passwordf=password
                uuid, code = get_captcha_text()
                md5_hash = hashlib.md5()
                md5_hash.update(password.encode('utf-8'))
                password = md5_hash.hexdigest()
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
                    "password": password,
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
                    response = requests.post(url, headers=headers, json=data, proxies=proxies)
                else:
                    response = requests.post(url, headers=headers, json=data)
                # Kiểm tra phản hồi
                if response.json()['message'] == 'Thao tác thành công':
                    token = response.json()['data']['token']
                    return f'{token}|{proxy}|{account}|{passwordf}|{f_id}'
                elif response.json()['message'] == 'Mã xác nhận sai':
                    login_to_account(account, password, proxy,f_id)
                else:
                    return None
            def kiem_tra_ky_tu(chuoi):
                return not re.match("^[a-zA-Z0-9]+$", chuoi)
            def get_captcha_text():
                solan = 0
                text = ""
                while len(text) < 4 or kiem_tra_ky_tu(text):
                    solan += 1
                    if solan >= 5:
                        try:
                            IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha").json()
                        except:
                            pass
                        solan = 0

                    try:
                        IMG = requests.get("https://m.okvip7.live/api/accountLogin/captcha").json()

                        img_src = IMG['data']['image']
                        uuid = IMG['data']['uuid']
                        url = "http://103.77.242.210:8000/ocr"
                        headers = {"accept": "application/json"}
                        data = {"image": img_src}

                        response = requests.post(url, headers=headers, data=data)
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
                headers=headers, proxies=proxies, timeout=20).json()
            luot = response['data']['surplusNumber']
            self.table.setItem(row, 6, QTableWidgetItem(f"Còn {luot} lượt"))
            account[6] = f"Còn {luot} lượt"
            self.update_log(f"{account[2]} còn {luot} lượt trả lời.")
            for cac in range(int(luot)):
                DanhSachCauHoi = requests.get('https://m.okvip7.live/api/activityQuestion/getQuestionList',headers=headers, proxies=proxies, timeout=20).json()['data']
                delay_time = random.randint(20, 35)
                for delay in range(delay_time, -1, -1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay}"))
                    time.sleep(1)
                date_time = int(time.time())
                recordNo = requests.get('https://m.okvip7.live/api/activityQuestion/startAnswerQuestion',headers=headers, proxies=proxies, timeout=20).json()['data']['recordNo']
                dataTraloi = {
                    "answerList": lay_answer_list(),
                    "timeStart": date_time,
                    "recordNo": recordNo
                }
                response = requests.post('https://m.okvip7.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi, proxies=proxies, timeout=20)
                print(response.json())
                time.sleep(3)
            print("Kimochi")
            CheckLuotQuay=requests.get("https://m.okvip7.live/api/lottery/getLuckyDrawBaseInfo",headers=headers , proxies=proxies , timeout=20).json()
            data2 = {"raffleId": CheckLuotQuay['data']['raffleId']}
            CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/getLuckyDrawInfoByDaily",headers=headers , proxies=proxies , timeout=20).json()['data']['drawCount']
            print(CheckLuotQuay)
            for xx in range(int(CheckLuotQuay)):
                CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/lotteryByDaily",headers=headers, json=data2 , proxies=proxies , timeout=20).json()
                delay_time = random.randint(5,6)
                for delay in range(delay_time, -1, -1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{CheckLuotQuay["data"]['prizeInfo']['prizeName']}]"))
                    time.sleep(1)
            self.table.setItem(selected_row, 6, QTableWidgetItem(f"Xong!"))

        except Exception as e:
            self.update_log(f"Lỗi kiểm tra lượt: {e}")
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
                    headers=headers, proxies=proxies, timeout=20).json()
                luot = response['data']['surplusNumber']
                self.table.setItem(row, 6, QTableWidgetItem(f"Còn {luot} lượt"))
                account[6] = f"Còn {luot} lượt"
                self.update_log(f"{account[2]} còn {luot} lượt trả lời.")
                for cac in range(int(luot)):
                    DanhSachCauHoi = requests.get('https://m.okvip7.live/api/activityQuestion/getQuestionList',headers=headers, proxies=proxies, timeout=20).json()['data']
                    delay_time = random.randint(20, 35)
                    for delay in range(delay_time, -1, -1):
                        self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay}"))
                        time.sleep(1)
                    date_time = int(time.time())
                    recordNo = requests.get('https://m.okvip7.live/api/activityQuestion/startAnswerQuestion',headers=headers, proxies=proxies, timeout=20).json()['data']['recordNo']
                    dataTraloi = {
                        "answerList": lay_answer_list(),
                        "timeStart": date_time,
                        "recordNo": recordNo
                    }
                    response = requests.post('https://m.okvip7.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi, proxies=proxies, timeout=20)
                    print(response.json())
                    time.sleep(3)
                print("Kimochi")
                CheckLuotQuay=requests.get("https://m.okvip7.live/api/lottery/getLuckyDrawBaseInfo",headers=headers , proxies=proxies , timeout=20).json()
                data2 = {"raffleId": CheckLuotQuay['data']['raffleId']}
                CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/getLuckyDrawInfoByDaily",headers=headers , proxies=proxies , timeout=20).json()['data']['drawCount']
                print(CheckLuotQuay)
                for xx in range(int(CheckLuotQuay)):
                    CheckLuotQuay=requests.post("https://m.okvip7.live/api/lottery/lotteryByDaily",headers=headers, json=data2 , proxies=proxies , timeout=20).json()
                    delay_time = random.randint(5,6)
                    for delay in range(delay_time, -1, -1):
                        self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{CheckLuotQuay["data"]['prizeInfo']['prizeName']}]"))
                        time.sleep(1)
                self.table.setItem(selected_row, 6, QTableWidgetItem(f"Xong!"))

            except Exception as e:
                self.update_log(f"Lỗi kiểm tra lượt: {e}")
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
            response = requests.get('https://m.okvip7.live/api/activityCollect/getListAvailable', headers=headers, proxies=proxies, timeout=20).json()
            idGame = response['data'][0]['id']
            data = {"id": idGame}
            draw_response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=20).json()
            draw_times = draw_response['data']['drawTimes']
            status_text = f"Lượt ghép chữ còn lại: {draw_times}"
            self.status_label.setText(status_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(status_text))  # Cập nhật cột Status (index = 3)
            for _ in range(int(draw_times)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/drawWord', headers=headers, json=data, proxies=proxies, timeout=20)
                print(response.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response.json()["data"]['textName']}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=20)
            synthesisTimes = response.json()['data']['synthesisTimes']
            data2 = {"raffleId": requests.get("https://m.okvip7.live/api/activityCollect/getListAvailable", headers=headers, proxies=proxies, timeout=20).json()['data'][0]['lotteryId']}
            for _ in range(int(synthesisTimes)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/mergeWord', headers=headers, json=data, proxies=proxies, timeout=20)
                response2 = requests.post('https://m.okvip7.live/api/lottery/lottery', headers=headers, json=data2, proxies=proxies, timeout=20)
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
            response = requests.get('https://m.okvip7.live/api/activityCollect/getListAvailable', headers=headers, proxies=proxies, timeout=20).json()
            idGame = response['data'][0]['id']
            data = {"id": idGame}
            draw_response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=20).json()
            draw_times = draw_response['data']['drawTimes']
            status_text = f"Lượt ghép chữ còn lại: {draw_times}"
            self.status_label.setText(status_text)
            self.table.setItem(selected_row, 6, QTableWidgetItem(status_text))  # Cập nhật cột Status (index = 3)
            for _ in range(int(draw_times)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/drawWord', headers=headers, json=data, proxies=proxies, timeout=20)
                print(response.text)
                for delay in range(5,-1,-1):
                    self.table.setItem(selected_row, 6, QTableWidgetItem(f"Delay {delay} [{response.json()["data"]['textName']}]"))  # Cập nhật cột Status (index = 3)
                    time.sleep(1)
            response = requests.post("https://m.okvip7.live/api/activityCollect/get", headers=headers, json=data, proxies=proxies, timeout=20)
            synthesisTimes = response.json()['data']['synthesisTimes']
            data2 = {"raffleId": requests.get("https://m.okvip7.live/api/activityCollect/getListAvailable", headers=headers, proxies=proxies, timeout=20).json()['data'][0]['lotteryId']}
            for _ in range(int(synthesisTimes)):
                response = requests.post('https://m.okvip7.live/api/activityCollect/mergeWord', headers=headers, json=data, proxies=proxies, timeout=20)
                response2 = requests.post('https://m.okvip7.live/api/lottery/lottery', headers=headers, json=data2, proxies=proxies, timeout=20)
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
