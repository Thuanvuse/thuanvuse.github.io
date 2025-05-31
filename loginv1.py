import requests
import time
import queue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# In màu nếu terminal hỗ trợ ANSI
def in_mau(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

print(in_mau("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "36"))
print(in_mau("🌀 TOOL AUTO BY THUẬN ĐẸP TRAI VIP PRO 🌀", "35"))
print(in_mau("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "36"))

thuandeptraivip2 = int(input(in_mau("👉 Nhập Số Luồng Đi Em Gái: ", "33")))
thuandeptraivip3 = int(input(in_mau("🔁 Nhập Số Lần Chạy Lại Luôn Nè Cưng Ơiiii: ", "33")))

print(in_mau("\n🚀 Đang Kiểm Tra Phiên Bản...", "34"))
time.sleep(1)
print(in_mau("✅ Bạn Đang Sử Dụng Phiên Bản Mới Nhất!", "32"))
print(in_mau("🥳 Chúc Bạn Đít Sướng Và Săn Acc Thành Công!\n", "35"))
print(in_mau("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "36"))
def get_captcha_text(driver, tokenanticapcha):
    solan = 0
    text = ""
    while len(text) < 4:
        solan += 1
        if solan >= 5:
            try:
                driver.find_element(By.CLASS_NAME, "codeImage").click()
                print("click Đổi Captcha")
                time.sleep(2)
            except:
                print("click captcha Thất bại")
            solan = 0

        try:
            img_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "codeImage"))
            )
            src = img_element.get_attribute("src")
            if "base64," not in src:
                print("Không phải ảnh base64")
                continue
            base64_data = src.split("base64,", 1)[1]

            payload = {
                "apikey": tokenanticapcha,
                "img": base64_data,
                "type": 14
            }

            response = requests.post("https://anticaptcha.top/api/captcha", json=payload)

            if response.ok:
                data = response.json()
                if data.get("success"):
                    print("Captcha giải được:", data["captcha"])
                    text = data["captcha"]
                else:
                    print("Lỗi:", data.get("message"))
            else:
                print("Lỗi HTTP:", response.status_code)

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

    return text
    
def create_position_queue():


    q = queue.Queue()
    y = 0
    for x in range(0, 7150*2, 550):
        if x >= 7150:
            q.put((x-7150, 1400))
        else:
            q.put((x, 0))
    return q
position_queue = create_position_queue()
active_sessions = {}  # Lưu ID của profile và vị trí của nó

def get_position():
    global position_queue
    if position_queue.empty():
        position_queue = create_position_queue()  # Reset lại hàng đợi nếu rỗng
    return position_queue.get()

def open_chrome(ID, TEN,tokenanticapcha):
    try:
        global active_sessions
        ToaDO_X, ToaDO_Y = get_position()
        active_sessions[ID] = (ToaDO_X, ToaDO_Y)
        print(f"🟢 Mở trình duyệt cho {TEN} tại tọa độ ({ToaDO_X}, {ToaDO_Y})")
        url = f"http://127.0.0.1:19995/api/v3/profiles/start/{ID}?win_scale=0.25&win_size=290,1300"
        json_data = requests.get(url).json()
        remote_debugging_address = json_data["data"]["remote_debugging_address"]
        driver_path = json_data["data"]["driver_path"]
        options = webdriver.ChromeOptions()
        options.debugger_address = remote_debugging_address
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://m.okvip19.live/login")
        time.sleep(5)
        Solanlam = 0
        TrangThai = False
        while Solanlam <= 6:
            try:
                try:
                    driver.find_element(By.XPATH, '//div[@class="user_name"]')
                    TrangThai = True
                except:
                    driver.find_element(By.XPATH, '//input[@placeholder="Nhập mã xác nhận"]')
                Solanlam = 100
            except:
                driver.refresh()
                Solanlam += 1
                driver.refresh()
                time.sleep(3)
        if Solanlam == 100 and TrangThai == False:
              
            try:
                input_field = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập mã xác nhận"]'))
                )
                input_field.send_keys(get_captcha_text(driver,tokenanticapcha))
            except Exception as e:
                luu_loi(TEN, f"Lỗi khi nhập mã xác nhận: {e}")
            time.sleep(2)

            button = driver.find_element(By.XPATH, '//button[@type="submit"]')
            button.click()
            
            time.sleep(5)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="user_name"]')))
            print(f"{TEN} Xong!")
           
            time.sleep(1)
            requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")

        else:
            if TrangThai == False:
                print(f"{TEN} Đéo Load Được Trang")
                luu_loi(TEN, "Không load được trang")
            else:
                driver.find_element(By.XPATH, '//div[@class="user_name"]')
                TrangThai = True
                print(f"{TEN} Xong!")
                time.sleep(1)
                requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
        time.sleep(2)
        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
    except:
        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")

import requests

def in_mau(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# ────────── TOKEN XỬ LÝ ────────── #
file_token = "token.txt"

try:
    with open(file_token, "r") as f:
        old_token = f.read().strip()
    chon = input(in_mau("🔁 Bạn có muốn sử dụng lại token cũ không? (c/k): ", "33")).strip().lower()
    if chon == "c":
        tokenanticapcha = old_token
    else:
        tokenanticapcha = input(in_mau("🔐 Vui Lòng Nhập API Token Captcha (https://anticaptcha.top/): ", "33")).strip()
        with open(file_token, "w") as f:
            f.write(tokenanticapcha)
except FileNotFoundError:
    tokenanticapcha = input(in_mau("🔐 Vui Lòng Nhập API Token Captcha (https://anticaptcha.top/): ", "33")).strip()
    with open(file_token, "w") as f:
        f.write(tokenanticapcha)

# ────────── KIỂM TRA SỐ DƯ ────────── #
try:
    response = requests.get(f"https://anticaptcha.top/api/getbalance?apikey={tokenanticapcha}")
    balance = response.json().get("balance", "Không xác định")
    print(in_mau(f"💰 Số Tiền Của Bạn Còn: {balance}", "32"))
except Exception as e:
    print(in_mau(f"❌ Đã xảy ra lỗi khi kiểm tra số dư: {e}", "31"))

# ────────── LẤY DANH SÁCH PROFILE ────────── #
try:
    a = requests.get("http://127.0.0.1:19995/api/v3/profiles?per_page=99999&sort=0").json()
except Exception as e:
    print(in_mau(f"⚠️ Không thể lấy danh sách profiles: {e}", "31"))
    a = {}

# ────────── NHẬP DANH SÁCH PROFILE MUỐN CHẠY ────────── #
stt = 0
ChayBiLoi = []

print(in_mau("\n🔧 CHỌN CÁCH NHẬP PROFILE:", "36"))
print(in_mau(" [1] Nhập thủ công", "36"))
print(in_mau(" [2] Nhập theo dãy số", "36"))

checkcu = int(input(in_mau("👉 Nhập lựa chọn của bạn (1 hoặc 2): ", "33")))

if checkcu == 1:
    while True:
        stt += 1
        them = input(in_mau(f"➕ Nhập Tên Trình Duyệt Muốn Chạy [hoặc gõ 'ALL' để dừng] <{stt}>: ", "35")).strip()
        if them.lower() != "all" and them:
            ChayBiLoi.append(them)
        else:
            break
else:
    st1 = int(input(in_mau("🔢 Nhập Điểm Bắt Đầu: ", "33")))
    st2 = int(input(in_mau("🔢 Nhập Điểm Kết Thúc: ", "33")))
    for x in range(st1, st2 + 1):
        ChayBiLoi.append(x)
        print(in_mau(f"✅ Đã thêm profile số: {x}", "32"))

# ────────── TỔNG KẾT ────────── #
print(in_mau("\n📋 Danh sách profile đã chọn:", "36"))
print(in_mau(str(ChayBiLoi), "36"))




for x in range(int(thuandeptraivip3)):
    with ThreadPoolExecutor(max_workers=int(thuandeptraivip2)) as executor:
        for profile in a["data"]:
            ID = profile["id"]
            TEN = profile["name"]
            if ChayBiLoi:
                for x in ChayBiLoi:
                    if int(TEN) == int(x):  # Ép kiểu để so sánh đúng
                        executor.submit(open_chrome, ID, TEN,tokenanticapcha)
            else:  # Nếu chọn "all", chạy luôn
                executor.submit(open_chrome, ID, TEN,tokenanticapcha)
