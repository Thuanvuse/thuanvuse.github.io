from datetime import datetime
import time

def tao_day_so(n):
    return [int(time.time() * 1000) + i for i in range(n)]

# Tạo dãy 10 số dựa trên thời gian thực
day_so = tao_day_so(10)
print(day_so)

timestamp = int(time.time() * 1000)// 1000  # Chuyển từ milliseconds sang seconds
date_time = datetime.utcfromtimestamp(timestamp)
print(date_time)  # Kết quả theo UTC
timestamp = int(time.time() * 1000)// 1000 
print(timestamp)

https://m.okvip19.live/api/lottery/lotteryByDaily
https://m.okvip19.live/api/lottery/getLuckyDrawInfoByDaily
