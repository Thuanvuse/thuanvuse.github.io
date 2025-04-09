import requests
import json
import re

response = requests.get("https://raw.githubusercontent.com/Thuanvuse/thuanvuse.github.io/refs/heads/main/kimochitokuda.txt")

text = response.text

cauHoiVaTraLoi = json.loads(text)

print(len(cauHoiVaTraLoi['cauHoiVaTraLoi']))
def process_question(driver, cauHoiVaTraLoi):
    try:
        question_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".containner .title"))
        )
        question_text = question_element.text.strip()

        # Tìm câu trả lời tương ứng trong dữ liệu JSON
        best_match = next((item for item in cauHoiVaTraLoi if item["question"] == question_text), None)

        if best_match:
            answer_text = best_match["answer"]

            # Tìm và click vào lựa chọn trả lời
            for option in driver.find_elements(By.CSS_SELECTOR, ".list .li"):
                if answer_text in option.text:
                    option.click()
                    print(f"Đã chọn đáp án: {answer_text}")
                    time.sleep(3)
                    return
        
        # Nếu không tìm thấy câu trả lời, ghi câu hỏi vào file và chọn đáp án C
        with open("Cauhoithieu.txt", "a", encoding="utf-8") as f:
            f.write(f"{question_text}\n")
        print(f"Câu hỏi chưa có đáp án: {question_text}, chọn C")
        
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='C']"))
        )
        element.click()
        time.sleep(3)
    
    except Exception as e:
        print(f"Lỗi khi lấy câu hỏi hoặc trả lời: {e}")