import requests
import time
import queue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

thuandeptraivip2=10
thuandeptraivip3=1
print("Kiem Tra Phien Ban......\nBan Dang La Phien ban Moi Nhat")
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
tokenanticapcha=input("Vui Lòng Nhập API Token Captcha (https://anticaptcha.top/): ")
print(f"Số Tiền Của Bạn Còn:  " + requests.get(f"https://anticaptcha.top/api/getbalance?apikey={tokenanticapcha}").text)
a = requests.get("http://127.0.0.1:19995/api/v3/profiles?per_page=99999&sort=0").json()

stt = 0
ChayBiLoi = []
checkcu=int(input("Nhập Thủ Công [1] | Nhập Dây [2] : "))
if checkcu == 1:
    while True:
        stt += 1
        them = input(f"Nhập Trình Duyệt Muốn Chạy [ALL] <{stt}>: ").strip()

        if them.lower() != "all" and them:  
            ChayBiLoi.append(them)
        else:
            break
else:
    st1=int(input("Nhập Điểm Bắt Đầu: "))
    st2=int(input("Nhập Điểm Kết Thúc: "))
    for x in range(st1,st2+1,1):
        ChayBiLoi.append(x)
        print(x)





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
