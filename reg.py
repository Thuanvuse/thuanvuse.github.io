import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import random
import string

# Nhập token ViOTP
viotp_token = input("Nhập ViOTP token: ").strip()

# Danh sách key có thể dùng
danh_sach_key = []

while True:
    key = input("Nhập key (Enter để bỏ qua): ").strip()
    if key == "":
        print("Bỏ qua, không thêm gì cả.")
    else:
        danh_sach_key.append(key)
        print(f"Đã thêm key: {key}")
    
    tiep_tuc = input("Tiếp tục? (y/n): ").strip().lower()
    if tiep_tuc != "y":
        break

print("\nDanh sách key đã nhập:")
for k in danh_sach_key:
    print(k)

danh_sach_cho = {}
lock = threading.Lock()

def tra_lai_key(key, timestamp_lay):
    thoi_gian_da_troi = time.time() - timestamp_lay
    thoi_gian_con_lai = max(0, 60 - thoi_gian_da_troi)

    def hoan_tra():
        time.sleep(thoi_gian_con_lai)
        with lock:
            if key in danh_sach_cho:
                del danh_sach_cho[key]
                danh_sach_key.append(key)
                print(f"✅ Key được trả lại sau đủ 60s: {key}")

    threading.Thread(target=hoan_tra, daemon=True).start()

def lay_ip():
    with lock:
        if not danh_sach_key:
            print("❌ Hết key khả dụng, vui lòng đợi...")
            time.sleep(50)
        key = danh_sach_key.pop(0)
        timestamp_lay = time.time()
        danh_sach_cho[key] = timestamp_lay

    try:
        response = requests.get(f"https://api.kiotproxy.com/api/v1/proxies/new?key={key}")
        proxy = response.json()
        ip = proxy['data']['http']
        print(f"✅ IP lấy được: {ip} từ key {key}")
        return ip, key, timestamp_lay
    except Exception as e:
        print(f"❌ Lỗi khi lấy IP với key {key}: {e}")
        with lock:
            del danh_sach_cho[key]
            danh_sach_key.append(key)
        return None, None, None

def tao_chuoi_random():
    chu_cai = random.choices(string.ascii_lowercase, k=9)
    so = random.choice(string.digits)
    chu_cai.insert(4, so)
    return ''.join(chu_cai)

def get_captcha_text(driver):
    text = ""
    while len(text) < 4:
        img_element = driver.find_element(By.CLASS_NAME, "codeImage")
        base64_data = img_element.get_attribute("src").replace(" ", "").replace("\n", "").replace("\t", "")
        try:
            url = "http://103.77.242.210:8000/ocr"
            headers = {"accept": "application/json"}
            data = {"image": base64_data}
            response = requests.post(url, headers=headers, data=data)
            text = response.json().get('data', '')
            print(text)
        except:
            time.sleep(1)
    return text

def dang_ky_tai_khoan(vitri):
    TAK = tao_chuoi_random()
    print(f"🔧 Tạo tài khoản: {TAK}")

    proxy, key, timestamp_lay = lay_ip()
    if not proxy:
        return

    payload = {
        "profile_name": f"{TAK}",
        "group_name": "new",
        "browser_core": "chromium",
        "browser_name": "Chrome",
        "browser_version": "129.0.6533.73",
        "is_random_browser_version": False,
        "raw_proxy": proxy,
        "startup_urls": "https://m.okvip19.live/personal",
        "is_masked_font": True,
        "is_noise_canvas": True,
        "is_noise_webgl": True,
        "is_noise_client_rect": True,
        "is_noise_audio_context": True,
        "is_random_screen": True,
        "is_masked_webgl_data": True,
        "is_masked_media_device": True,
        "is_random_os": True,
        "os": "Windows 8",
        "webrtc_mode": 2,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post("http://127.0.0.1:19995/api/v3/profiles/create", data=json.dumps(payload), headers=headers)
        ID = response.json()['data']['id']
    except:
        print("❌ Lỗi khi tạo profile.")
        tra_lai_key(key, timestamp_lay)
        return

    try:
        url = f"http://127.0.0.1:19995/api/v3/profiles/start/{ID}?win_pos={vitri}&win_scale=0.25&win_size=290,1200"
        json_data = requests.get(url).json()
        remote_debugging_address = json_data["data"]["remote_debugging_address"]
        driver_path = json_data["data"]["driver_path"]
        options = webdriver.ChromeOptions()
        options.debugger_address = remote_debugging_address
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://m.okvip19.live/register?backRoute=/personal")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập tài khoản"]'))).send_keys(TAK)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập mật khẩu"]'))).send_keys(TAK + "123")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập lại mật khẩu"]'))).send_keys(TAK + "123")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập email"]'))).send_keys(TAK + "123@gmail.com")

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập mã xác nhận"]'))).send_keys(get_captcha_text(driver))

        buom = requests.get(f"https://api.viotp.com/request/getv2?token={viotp_token}&serviceId=733&network=VINAPHONE").json()
        sodienthoai = buom['data']['phone_number']
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập số điện thoại"]'))).send_keys(sodienthoai)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'van-checkbox__icon')]"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Bước tiếp theo')]]"))).click()
        time.sleep(5)

        if driver.current_url.startswith("https://m.okvip19.live/registerStep"):
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="send sendStyle1"]'))).click()
            IDdd = buom['data']['request_id']
            sothime = 0
            while True:
                get = requests.get(f"https://api.viotp.com/session/getv2?requestId={IDdd}&token={viotp_token}").json()['data']['Code']
                print(get)
                if get is None:
                    time.sleep(3)
                    sothime += 5
                    if 120 <= sothime <= 122:
                        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="send sendStyle1"]'))).click()
                    if sothime > 250:
                        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
                        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/delete/{ID}")
                        break
                else:
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Nhập mã xác nhận"]'))).send_keys(get)
                    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Đăng ký'] and not(contains(@class, 'disabled'))]"))).click()
                    break
        else:
            print("❌ Không phải link cần kiểm tra.")
            time.sleep(3)
            requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
            requests.get(f"http://127.0.0.1:19995/api/v3/profiles/delete/{ID}")
        tra_lai_key(key, timestamp_lay)
    except Exception as e:
        print(f"❌ Lỗi selenium: {e}")
        time.sleep(3)
        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/delete/{ID}")
        tra_lai_key(key, timestamp_lay)

# Nhập số acc muốn tạo
NhapSoAccMuoonTao = int(input("Nhập số Acc muốn tạo (bội của 10): "))
for _ in range(NhapSoAccMuoonTao // 10):
    positions = ["0,0", "400,0", "700,0", "1000,0", "1300,0", "1600,0", "1900,0", "2100,0", "0,100", "400,100"]
    with ThreadPoolExecutor(max_workers=10) as executor:
        for pos in positions:
            executor.submit(dang_ky_tai_khoan, pos)
