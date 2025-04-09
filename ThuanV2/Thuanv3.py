import requests
import random
import hashlib
import json
import time
from datetime import datetime

import random
import time

def fake_headers_realistic(user_agent=None, referer=None, x_forwarded_for=None, x_real_ip=None):
    default_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.64",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    ]
    
    default_referers = [
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://www.facebook.com/",
        "https://twitter.com/",
        "https://www.youtube.com/"
    ]
    
    user_agent = user_agent or random.choice(default_user_agents)
    referer = referer or ""
    # Giả lập địa chỉ IP nếu không truyền vào
    x_forwarded_for = x_forwarded_for or f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    x_real_ip = x_real_ip or f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "DNT": "1",  # Do Not Track Request
        "TE": "Trailers",
        "token": referer,
        "Origin": "https://api.okvip.center",
        "X-Requested-With": "XMLHttpRequest",
        "X-Forwarded-For": x_forwarded_for,  
        "X-Real-IP": x_real_ip
    }

    # Giả lập khoảng thời gian delay giữa các yêu cầu để tránh bị phát hiện
    time.sleep(random.uniform(0.5, 2))  # Delay từ 0.5s đến 2s
    
    return headers

def get_captcha_text():
    text=""
    while len(text) < 4:
        try:
            IMG = requests.get("https://m.okvip19.live/api/accountLogin/captcha").json()
            img_src = IMG['data']['image']
            uuid = IMG['data']['uuid']
            url = "http://103.77.242.210:8000/ocr"
            headers = {"accept": "application/json"}
            data = {"image": img_src}
            response = requests.post(url, headers=headers, data=data)
            text = response.json().get('data', '')
            print(text)
        except:
            time.sleep(1)
    return uuid,text
def login_to_account(account, password, proxy=None):
    uuid, code = get_captcha_text()

    # List of fake user agents
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36",
        "Mozilla/5.0 (Android 10; Mobile; rv:83.0) Gecko/83.0 Firefox/83.0",
        "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; HUAWEI P30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Safari/537.36"
    ]

   
    useragent= random.choice(user_agents)
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    password = md5_hash.hexdigest()

    url = "https://m.okvip19.live/api/accountLogin/doLogin"
    headers = {
        "authority": "m.okvip19.live",
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi-VN,vi;q=0.9",
        "content-type": "application/json",
        "locale": "vi_vn",
        "origin": "https://m.okvip19.live",
        "priority": "u=1, i",
        "referer": "https://m.okvip19.live/login",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "signature": "9sbUYlr1qjdxfPJh+mWz9lX1ywtRb0mvDYBjHdaF+q8=",
        "user-agent": useragent
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
        return token,useragent
    elif response.json()['message'] == 'Mã xác nhận sai':
        login_to_account(account, password, proxy=None)
    else:
        return None
def get_account_info(token, proxy=None):
    url = "https://m.okvip19.live/api/account/accountInfo"
    headers = {"token": token}
    
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)
    
    return response.json()

def get_game_id(token, proxy=None):
    url = 'https://m.okvip19.live/api/activityCollect/getListAvailable'
    headers = {"token": token}
    
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)
    
    return response.json()['data'][0]['id']

def get_lotteryId(token, proxy=None):
    url = 'https://m.okvip19.live/api/activityCollect/getListAvailable'
    headers = {"token": token}
    
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)
    
    return response.json()['data'][0]['lotteryId']

def draw_words(token, proxy=None):
    account_info = get_account_info(token, proxy)
    account_id = account_info['data']['id']
    game_id = get_game_id(token, proxy)
    lotteryId = get_lotteryId(token, proxy)
    url = "https://m.okvip19.live/api/activityCollect/get"
    headers = {
        "authority": "m.okvip19.live",
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi-VN,vi;q=0.9",
        "content-length": "28",  
        "content-type": "application/json",
        "locale": "vi_vn",
        "origin": "https://m.okvip19.live",
        "token": token,
    }
    
    data = {"id": game_id}
    data2 = {"raffleId": lotteryId}
    
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
    
    draw_times = response.json()['data']['drawTimes']
    
    for _ in range(int(draw_times)):
        if proxy:
            response = requests.post('https://m.okvip19.live/api/activityCollect/drawWord', headers=headers, json=data, proxies=proxies)
        else:
            response = requests.post('https://m.okvip19.live/api/activityCollect/drawWord', headers=headers, json=data)
        print(response.text)
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
    
    synthesisTimes = response.json()['data']['synthesisTimes']
    for _ in range(int(synthesisTimes)):
        if proxy:
            response = requests.post('https://m.okvip19.live/api/activityCollect/mergeWord', headers=headers, json=data, proxies=proxies)
            response2 = requests.post('https://m.okvip19.live/api/lottery/lottery', headers=headers, json=data2, proxies=proxies)

        else:
            response = requests.post('https://m.okvip19.live/api/activityCollect/mergeWord', headers=headers, json=data)
            response2 = requests.post('https://m.okvip19.live/api/lottery/lottery', headers=headers, json=data2)
        print(response.text)
        print(response2.text)
def Run(token,proxy,password,account):
    print(f"Login successful! Token: {token}")
    draw_words(token, proxy)
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        CheckLuotQuay=requests.get("https://m.okvip19.live/api/activityQuestion/getActivityQuestionInfo",headers={"token": token} , proxies=proxies).json()['data']['surplusNumber']
    else:
        CheckLuotQuay=requests.get("https://m.okvip19.live/api/activityQuestion/getActivityQuestionInfo",headers={"token": token}).json()['data']['surplusNumber']
    print(CheckLuotQuay)
    for cac in range(int(CheckLuotQuay)):
        if proxy:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {
                "http": proxy_address,
                "https": proxy_address
            }
            DanhSachCauHoi = requests.get('https://m.okvip19.live/api/activityQuestion/getQuestionList',headers={"token": token}, proxies=proxies).json()['data']

        else:
            DanhSachCauHoi = requests.get('https://m.okvip19.live/api/activityQuestion/getQuestionList',headers={"token": token}).json()['data']

        listdapan = []
        for x in DanhSachCauHoi:
            CauHoi = x['title']
            Dapan = x['optionList']
            id = x['id']
            listdapan.append(id)

        # Lấy thời gian hiện tại (giây)
        date_time = int(time.time())
        # Lấy recordNo
        if proxy:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {
                "http": proxy_address,
                "https": proxy_address
            }
            recordNo = requests.get('https://m.okvip19.live/api/activityQuestion/startAnswerQuestion',headers={"token": token}, proxies=proxies).json()['data']['recordNo']

        else:
            recordNo = requests.get('https://m.okvip19.live/api/activityQuestion/startAnswerQuestion',headers={"token": token}).json()['data']['recordNo']
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi-VN,vi;q=0.9',
            'content-type': 'application/json',
            'token': token
        }
        dataTraloi = {
            "answerList": [{"id":"1862964568411324417","submitAnswer":"D"},{"id":"1785523542761570306","submitAnswer":"A"},{"id":"1845987816969232385","submitAnswer":"A"},{"id":"1785512864235552770","submitAnswer":"A"},{"id":"1790416418322706433","submitAnswer":"A"}],
            "timeStart": date_time,
            "recordNo": recordNo
        }
        time.sleep(3)
        if proxy:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {
                "http": proxy_address,
                "https": proxy_address
            }
            response = requests.post('https://m.okvip19.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi, proxies=proxies)

        else:
            response = requests.post('https://m.okvip19.live/api/activityQuestion/submitQuestion',headers=headers,json=dataTraloi)
        print(response.text)
        time.sleep(2)
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        CheckLuotQuay=requests.get("https://m.okvip19.live/api/lottery/getLuckyDrawBaseInfo",headers={"token": token} , proxies=proxies ).json()
    else:
        CheckLuotQuay=requests.get("https://m.okvip19.live/api/lottery/getLuckyDrawBaseInfo",headers={"token": token}).json()

    data2 = {"raffleId": CheckLuotQuay['data']['raffleId']}
    print(data2)
    if proxy:
        proxy_url, port, username, password = proxy.split(':')
        proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
        proxies = {
            "http": proxy_address,
            "https": proxy_address
        }
        CheckLuotQuay=requests.post("https://m.okvip19.live/api/lottery/getLuckyDrawInfoByDaily",headers={"token": token} , proxies=proxies ).json()['data']['drawCount']
    else:
        CheckLuotQuay=requests.post("https://m.okvip19.live/api/lottery/getLuckyDrawInfoByDaily",headers={"token": token}).json()['data']['drawCount']
    print(CheckLuotQuay)
    for xx in range(int(CheckLuotQuay)):
        if proxy:
            proxy_url, port, username, password = proxy.split(':')
            proxy_address = f"http://{username}:{password}@{proxy_url}:{port}"
            proxies = {
                "http": proxy_address,
                "https": proxy_address
            }
            CheckLuotQuay=requests.post("https://m.okvip19.live/api/lottery/lotteryByDaily",headers={"token": token}, json=data2 , proxies=proxies ).json()
        else:
            CheckLuotQuay=requests.post("https://m.okvip19.live/api/lottery/lotteryByDaily",headers={"token": token}, json=data2).json()
        print(CheckLuotQuay)
    response=requests.post("https://m.okvip19.live/api/activitySignIn/singIn",headers={"token": token})
    print(response.text)
ACC=["thuankhkhkhk206025|t29032006@|103.161.171.11:3158:proxy000015:Http9999"]

for cun in ACC:
    account = cun.split("|")[0]
    password = cun.split("|")[1]
    proxy = cun.split("|")[2]
    token = login_to_account(account, password)
    if token:
        Run(token,proxy,password,account)
    else:
        print("Login failed.")
