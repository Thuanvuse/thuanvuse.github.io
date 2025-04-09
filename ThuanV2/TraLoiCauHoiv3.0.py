import requests
import time
import queue
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

import pickle
import os

CONFIG_FILE = "config.pkl"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "rb") as f:
            return pickle.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "wb") as f:
        pickle.dump(config, f)

def get_user_input():
    config = load_config()
    
    if config:
        use_old = input("Bạn có muốn sử dụng cấu hình cũ không? (y/n): ").strip().lower()
        if use_old == 'y':
            return config

    # Nhập cấu hình mới
    thuandeptraivip = "m.okvip" + input("Nhập URL Muốn Xuất: ")
    thuandeptraivip2 = input("Nhập Số Luông: ")
    thuandeptraivip3 = input("Nhập Số Lần Chạy >=1: ")

    config = (thuandeptraivip, thuandeptraivip2, thuandeptraivip3)
    save_config(config)
    return config

# Chạy chương trình
thuandeptraivip, thuandeptraivip2, thuandeptraivip3 = get_user_input()

# Kiểm tra lại trước khi sử dụng
try:
    so_lan = int(thuandeptraivip3)
    so_luong = int(thuandeptraivip2)
except ValueError:
    print("Lỗi: Số lần chạy hoặc số luồng không hợp lệ.")
    exit(1)






def Checkluotquay(driver):
    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, f'//img[@src="https://{thuandeptraivip}.live/assets/png/start.2025020503362.png"]')))
        return True
    except:
        return False
def Traloi(driver):
    

    questions_db = {

'''"Em yêu phút giây này. Thầy em tóc như bạc thêm" là những câu hát trong bài hát nào?''': '''Bụi phấn''',
'''"Ligue 1" là viết tắt Giải bóng đá của nước nào?''': '''Pháp''',
'''"Lạp xưởng" là gì?''': '''Một món ăn''',
'''"Mặt Trời của thi ca Nga" là ai?''': '''Puskin''',
'''"Nghe nói Cà Mau xa lắm. Ở cuối cùng bản đồ Việt Nam" là câu hát có trong bài hát nào?''': '''Áo mới Cà Mau''',
'''"Người anh hùng lấp lỗ châu mai" là nói về ai?''': '''Phan Đình Giót''',
'''"Ngồi khóc trên cây" là tác phẩm của nhà văn nào?''': '''Nguyễn Nhật Ánh''',
'''"Núi đôi Quản Bạ" là địa danh thuộc tỉnh nào?''': '''Hà Giang''',
'''The Toffees là biệt danh của câu lạc bộ bóng đá nào?''': '''Everton''',
'''"Tháp nghiêng Pisa" thuộc quốc gia nào trên thế giới?''': '''Ý''',
'''"Xứ sở vạn đảo" là nói về đất nước nào?''': '''Indonesia''',
'''"Đói cho sạch, rách cho thơm" khuyên con người điều gì?''': '''Sống trong sạch, ngay thẳng''',
'''10 đứa bé đang chơi trốn tìm, 4 đứa bị bắt, còn bao nhiêu đứa chưa bị bắt?''': '''5''',
'''50 ngôi sao trên quốc kỳ của nước Mỹ đại diện cho điều gì?''': '''Các tiểu bang''',
'''8 chữ vàng mà Bác Hồ dành tặng cho phụ nữ Việt Nam là gì?''': '''Anh hùng Bất khuất Trung hậu Đảm đang.''',
'''Ai có nhà di động đầu tiên?''': '''Rùa và ốc sên''',
'''Ai cũng biết đỉnh núi Everest cao nhất thế giới. Vậy trước khi đỉnh Everest được khám phá, đỉnh núi nào cao nhất thế giới?''': '''Everest''',
'''Ai là ca sĩ nổi tiếng với biệt danh "Hoạ mi tóc nâu"?''': '''Mỹ Tâm''',
'''Ai là ca sĩ đầu tiên đoạt giải thưởng "Ca sĩ của năm" tại Giải thưởng Làn Sóng Xanh?''': '''Mỹ Tâm''',
'''Ai là cầu thủ ghi bàn nhiều nhất trong lịch sử World Cup tính đến năm 2024?''': '''Miroslav Klose''',
'''Ai là cầu thủ ghi nhiều hat-trick nhất tại EPL tính đến năm 2022?''': '''Sergio Agũero''',
'''Ai là người chỉ huy chiến thắng Bạch Đằng năm 938?''': '''Ngô Quyền''',
'''Ai là người phát minh ra bóng đèn điện?''': ''' Thomas Edison''',
'''Ai là người phát minh ra thận nhân tạo?''': '''Willem Johan Kolff''',
'''Ai là người phụ nữ Việt Nam đầu tiên trở thành Chủ tịch Quốc hội?''': ''' Nguyễn Thị Kim Ngân''',
'''Ai là người phụ nữ nổi tiếng với vai trò lãnh đạo phong trào Đồng Khởi ở miền Nam Việt Nam?''': ''' Nguyễn Thị Định''',
'''Ai là người sáng lập nên nước Đông Ngô thời Tam quốc?''': '''Tôn Quyền''',
'''Ai là người sáng lập ra tập đoàn Microsoft?''': '''Bill Gates''',
'''Ai là người đầu tiên truyền bá môn võ Vịnh Xuân quyền ở Việt Nam?''': '''Nguyễn Tế Công''',
'''Ai là người đầu tiên đặt chân lên mặt trăng?''': ''' Neil Armstrong''',
'''Ai là người đặt tên nước ta là Việt Nam?''': '''Vua Gia Long''',
'''Ai là nữ anh hùng dân tộc nổi tiếng với câu nói: "Tôi muốn cưỡi cơn gió mạnh, đạp bằng sóng dữ, chém cá kình ở biển Đông"?''': ''' Nguyễn Thị Duệ''',
'''Ai là nữ chiến sĩ Việt Nam đầu tiên được phong cấp tướng?''': '''Nguyễn Thị Định''',
'''Ai là tác giả của "Lão Hạc"?''': '''Nam Cao''',
'''Ai là tác giả của bài thơ "Nam quốc sơn hà"?''': '''Lý Thường Kiệt''',
'''Ai là tác giả của bài thơ "Tây Tiến"?''': '''Quang Dũng''',
'''Ai là tác giả của tiểu thuyết "Chiến tranh và Hòa bình"?''': '''Fyodor Dostoevsky''',
'''Ai là tác giả của tiểu thuyết “Cuốn theo chiều gió”?''': '''Margaret Mitchell''',
'''Ai là tác giả của tác phẩm "Chuyện người con gái Nam Xương"?''': '''Nguyễn Dữ''',
'''Ai là tổng thống đầu tiên của Hoa Kỳ?''': '''George Washington''',
'''Ai là vị vua cuối cùng của Việt Nam?''': '''Vua Bảo Đại''',
'''Ai là đại sứ thương hiệu của LuongSonTV - Đối tác chiến lược của Liên Minh OKVIP?''': '''VĂN QUYẾN''',
'''Ai người công đức văn minh, Sớ dân xin chém bảy tên nịnh thần - Là ai?''': '''Chu Văn An''',
'''Ai được mệnh danh là "Vua bóng đá"?''': '''Pelé''',
'''Ba của Tèo gọi mẹ của Tý là em dâu, vậy ba của Tý gọi ba của Tèo là gì?''': '''Gọi là anh trai''',
'''Biển Đỏ nằm giữa hai lục địa nào?''': '''Châu Á Và Châu Phi''',
'''Biểu tượng năm vòng của Thế vận hội Olympic tượng trung cho điều gì?''': '''Năm châu lục''',
'''Biểu tượng phổ biến nhất của Halloween là gì?''': '''Quả bí ngô''',
'''Bundesliga là giải đấu thuộc quốc gia nào?''': '''Đức''',
'''Bài ca "Tiến Quân Ca" do ai sáng tác?''': '''Văn Cao''',
'''Bài hát "Như có Bác Hồ trong ngày vui đại thắng" do ai sáng tác?''': '''Phạm Tuyên''',
'''Bài hát Biết ơn chị Võ Thị Sáu là sáng tác của ai ?''': ''' Văn Cao''',
'''Bài thơ Núi Đôi của nhà thơ Vũ Cao lấy nguyên mẫu từ hình tượng nhân vật nữ chiến sĩ anh hùng nào?''': '''Trần Thị Bắc''',
'''Bài thơ về tiểu đội xe không kính là tác phẩm của ai?''': '''Phạm Tiến Duật''',
'''Bàn gì mà lại bước gần bước xa?''': '''Bàn chân''',
'''Bàn gì xe ngựa sớm chiều giơ ra?''': '''Bàn cờ''',
'''Bác Hồ đọc Tuyên ngôn Độc lập tại Quảng trường Ba Đình vào năm nào?''': '''1945''',
'''Bánh gì nghe tên đã thấy đau?''': '''Bánh tét''',
'''Bãi biển Sầm Sơn thuộc tỉnh nào?''': '''Thanh Hóa''',
'''Bình Trị Thiên khói lửa' là ca khúc của nhạc sĩ nào?''': '''Nguyễn Văn Thương''',
'''Bông gì không mọc từ cây?''': '''Bông tai''',
'''Bạch kê là gà lông trắng, huỳnh kê là gà lông vàng. Vậy ô kê là gì?''': '''Đồng ý''',
'''Bến cảng Nhà Rồng - nơi Bác Hồ ra đi tìm đường cứu nước nằm ở thành phố nào?''': '''TP Hồ Chí Minh''',
'''Bệnh gì bác sĩ bó tay?''': '''Bệnh gãy tay''',
'''Bệnh nào sau đây do vi-rút HIV gây ra?''': '''AIDS''',
'''Bộ phim kinh dị nổi tiếng có tên là "Halloween" được ra mắt vào năm nào?''': '''1978''',
'''Bộ phận nào trong cơ thể giúp lọc máu?''': '''Thận''',
'''Bộ phận nào trên cơ thể thằn lằn có khả năng mọc lại?''': '''Đuôi''',
'''CHỌN CÁC MẢNH GHÉP ĐỂ TẠO THÀNH LOGO MB66?''': '''/okvip/20240108210827_250138.png''',
'''CLB nào vô địch Serie A với thành tích bất bại trong mùa giải 2011-2012?''': '''Juventus''',
'''Ca sĩ nào dưới đây đã nhận được giải thưởng 'Huyền thoại Âm nhạc Châu Á' trong sự kiện Top Asia Corporate Ball 2014 tại Malaysia?''': '''Mỹ Tâm''',
'''Ca sĩ nào đã từng đoạt giải "Quán quân The Remix" mùa đầu tiên?''': '''Đông Nhi''',
'''Chiến dịch Hồ Chí Minh giải phóng miền Nam Việt Nam diễn ra vào năm nào?''': '''1975''',
'''Chiến dịch nào đã kết thúc cuộc kháng chiến chống Pháp (1945-1954)?''': '''Chiến dịch Điện Biên Phủ''',
'''Chiến dịch Điện Biên Phủ diễn ra vào năm nào?''': '''1954''',
'''Chiến thắng nào đã buộc Mỹ phải ký Hiệp định Paris năm 1973?''': '''Chiến thắng Hà Nội Điện Biên Phủ trên không''',
'''Chiếu truyền thống được dệt từ sợi gì?''': '''Cói''',
'''Châu lục nào có diện tích nhỏ nhất?''': '''Châu Úc''',
'''Châu lục nào có dân số đông nhất?''': '''Châu Á''',
'''Chú gấu trúc - nhân vật chính trong phim Kungfu Panda có tên là gì?''': '''Po''',
'''Chú gấu trúc – nhân vật chính trong phim Kungfu Panda có tên là gì?''': '''Po''',
'''Chơi chữ: Bông gì cứng nhất?''': '''Bông tê''',
'''Chơi chữ: Một cậu trai hỏi tên một cô gái. Cô gái trả lời tên cô giống như 12 bắp ngô. Hỏi tên cô gái là gì?''': '''Tố Nga''',
'''Chơi chữ: Xe nào không bao giờ giảm đi?''': '''Xe tăng''',
'''Chất nào là dẫn điện tốt nhất ?''': '''Bạc''',
'''Chất nào là nguồn năng lượng chính cho cơ thể người?''': '''Carbohydrate''',
'''Chất nào là thành phần chính của viên kim cương?''': '''Carbon''',
'''Chất nào sau đây có công thức hóa học là H2O?''': '''Nước''',
'''Chợ nào dùng để nhai?''': '''Chợ nổi Cái Răng''',
'''Chủ tịch Hồ Chí Minh đọc bản Tuyên ngôn Độc lập vào ngày 2/9/1945 tại đâu?''': '''Quảng trường Ba Đình''',
'''Chức vô địch World Cup 2010 thuộc về đội tuyển nào?''': '''Tây Ba Nha''',
'''Con chim hồng tước nhỏ' là biệt danh của cầu thủ nào?''': '''Garrincha''',
'''Con chó đen gọi là con chó mực, con chó vàng gọi là con chó phèn. Vậy con chó đỏ gọi là con chó gì?''': '''Con chó đỏ''',
'''Con gì biết đi nhưng người ta vẫn nói nó không biết đi?''': '''Con bò''',
'''Con gì còn đau khổ hơn hươu cao cổ bị viêm họng?''': '''Con rết bị đau chân''',
'''Con gì có cánh mà không có lông?''': '''Con diều''',
'''Con gì có đầu dê mà mình là ốc?''': '''Con dốc''',
'''Con gì sinh ra đã BÉO?''': '''Con cá mập''',
'''Con gì sống mũi mọc sừng. Mình mặc áo giáp khỏe không ai bằng?''': '''Tê giác''',
'''Con gì đi ngồi, đứng ngồi, nằm ngồi, ngủ cũng ngồi luôn là con gì?''': '''Con ếch''',
'''Con gì? Da thịt như than. Áo choàng như tuyết. Giúp người trị bệnh. Mà tên chẳng hiền?''': '''Gà ác''',
'''Con sông nào dài nhất châu Á?''': '''Sông Dương Tử''',
'''Con vật nào sau đây thường được ví là chậm chạp?''': '''Rùa''',
'''Con vật nào thường được liên tưởng đến sự xui xẻo trong Halloween?''': ''' Mèo đen''',
'''Con vật nào được nhắc đến trong câu thành ngữ sau: ''... ngồi đáy giếng''?''': '''Ếch''',
'''Coupe de France là tên của giải đấu nào?''': '''Cúp bóng đá Pháp''',
'''Cristiano Ronaldo đã giành bao nhiêu danh hiệu Champions League trong sự nghiệp của mình?''': '''5''',
'''Cung hoàng đạo nào bắt đầu từ ngày 23 tháng 8 đến ngày 22 tháng 9?''': '''Xử Nữ''',
'''Cuộc chiến tranh chống Tống lần thứ nhất diễn ra vào thời kỳ nào?''': ''' Thời Tiền Lê''',
'''Cuộc kháng chiến chống Mỹ cứu nước của nhân dân Việt Nam kết thúc thắng lợi vào năm nào?''': '''Năm 1975''',
'''Cuộc khởi nghĩa Lam Sơn (1418-1427) diễn ra dưới sự lãnh đạo của ai?''': '''Lê Lợi''',
'''Cuộc khởi nghĩa của Hai Bà Trưng diễn ra vào năm nào?''': '''40''',
'''Các dũng sĩ đấu bò tót thường phất tấm vải có màu gì?''': '''Đỏ''',
'''Cái gì bằng cái vung, vùng xuống ao, đào chẳng thấy, lấy chẳng được?''': '''BÓNG MẶT TRĂNG''',
'''Cái gì càng kéo càng ngắn?''': '''Điếu thuốc lá''',
'''Cái gì càng kéo càng ngắn?''': '''Điếu thuốc lá''',
'''Cái gì có kích thước bằng con voi nhưng chẳng nặng gram nào cả?''': '''Bóng con voi''',
'''Cái gì người mua biết, người bán biết, người xài không bao giờ biết?''': '''Quan tài''',
'''Cái gì trong trắng ngoài xanh. Trồng đậu, trồng hành rồi thả heo vào''': '''Bánh chưng''',
'''Câu hỏi nào mà không ai có thể trả lời “Vâng”?''': '''Mày chết rồi hả?''',
'''Câu hỏi: Cá mập có bao nhiêu răng trong suốt cuộc đời của chúng?''': '''30.000 răng''',
'''Câu hỏi: Mưa axit hình thành do sự kết hợp của các khí thải công nghiệp với điều gì trong không khí?''': '''Hơi Nước''',
'''Câu lạc bộ nào có biệt danh là "Bà Đầm Già"?''': '''Juventus''',
'''Câu lạc bộ nào giành chức vô địch Serie A trong mùa giải 2020-2021?''': '''Inter Milan''',
'''Câu lạc bộ nào vô địch Ligue 1 mùa giải 2020-2021?''': '''Lille OSC''',
'''Câu lạc bộ nào vô địch giải Ngoại hạng Anh 2015/2016?''': '''Leicester City''',
'''Câu lạc bộ nào đã lập kỷ lục vô địch UEFA Champions League liên tiếp trong ba mùa giải từ 2016 đến 2018?''': '''Real Madrid''',
'''Câu tục ngữ nào diễn tả việc học hỏi từ trải nghiệm thực tế sẽ thu được nhiều kiến thức bổ ích?''': '''"Đi một ngày đàng, học một sàng khôn"''',
'''Câu đố kiến thức : Chất nào thường được dùng để khử trùng nước bể bơi?？''': '''Clo''',
'''Câu đố kiến thức : Cách tốt nhất để giảm lượng rác thải nhựa là gì?''': '''Sử dụng sản phẩm tái sử dụng''',
'''Câu đố kiến thức : Cây xanh sử dụng khí gì để quang hợp?''': '''CO2''',
'''Câu đố kiến thức : Cầu vồng thường xuất hiện khi có điều kiện nào?''': '''Mưa và nắng''',
'''Câu đố kiến thức : Hành tinh nào trong hệ mặt trời của chúng ta có thời gian quay quanh mặt trời ngắn nhất?''': '''Sao Thủy''',
'''Câu đố kiến thức : Hành tinh nào trong hệ mặt trời của chúng ta là hành tinh lớn nhất?''': '''Sao Mộc''',
'''Câu đố kiến thức : Khi nào là thời điểm tốt nhất để tưới cây trong ngày hè?''': '''Buổi sáng sớm''',
'''Câu đố kiến thức : Khi nào một năm nhuận xuất hiện?''': '''Mỗi 4 năm''',
'''Câu đố kiến thức : Khi thời tiết lạnh, tại sao bạn thấy hơi thở của mình?''': '''Do hơi nước trong hơi thở ngưng tụ''',
'''Câu đố kiến thức : Loài vật nào có khả năng hồi sinh sau khi bị đông lạnh?''': '''Bọ gậy''',
'''Câu đố kiến thức : Loài động vật nào được biết đến là có tuổi thọ ngắn nhất?''': '''Chuồn chuồn''',
'''Câu đố kiến thức : Loại bóng đèn nào có tuổi thọ dài nhất?''': '''Đèn LED''',
'''Câu đố kiến thức : Loại bức xạ nào từ mặt trời gây ra hiện tượng rám nắng?''': '''Tia UV''',
'''Câu đố kiến thức : Loại chất nào được tiết ra khi bạn tập thể dục và giúp cảm thấy hạnh phúc hơn''': '''Endorphins''',
'''Câu đố kiến thức : Loại dầu nào nên tránh sử dụng trong nấu ăn vì nó chứa nhiều chất béo bão hòa?''': '''Dầu Dừa''',
'''Câu đố kiến thức : Loại gas nào thường được sử dụng trong bếp gas ở nhà để nấu ăn?''': '''Propane''',
'''Câu đố kiến thức : Loại gia vị nào là một phần của cây và được sử dụng trong nấu ăn để tăng hương vị?''': '''Quế''',
'''Câu đố kiến thức : Loại gia vị nào được biết đến với khả năng chống viêm và giảm đau?''': '''Nghệ''',
'''Câu đố kiến thức : Loại gia vị nào được làm từ những búp nụ chưa nở của cây?''': '''Đinh hương''',
'''Câu đố kiến thức : Loại gia vị nào được tạo ra từ các hạt của cây và thường được sử dụng trong nấu ăn?''': '''Tiêu đen''',
'''Câu đố kiến thức : Loại năng lượng nào là thân thiện nhất với môi trường?''': '''Năng lượng gió''',
'''Câu đố kiến thức : Loại nước uống nào là lựa chọn tốt nhất cho sức khỏe?''': '''Nước lọc''',
'''Câu đố kiến thức : Loại protein nào tốt cho sức khỏe và môi trường?''': '''Đậu và các sản phẩm từ đậu''',
'''Câu đố kiến thức : Loại quả nào sau đây không phải là một loại quả hạch?''': '''Táo Envy''',
'''Câu đố kiến thức : Loại thực vật nào giúp cải thiện chất lượng không khí trong nhà?''': '''Lưỡi hổ (cây thuốc mồng tơi)''',
'''Câu đố kiến thức : Loại vitamin nào cần thiết để duy trì sức khỏe của hệ thần kinh và hồng cầu?''': '''Vitamin B12''',
'''Câu đố kiến thức : Loại vitamin nào giúp cơ thể hấp thụ canxi hiệu quả hơn?''': '''Vitamin D''',
'''Câu đố kiến thức : Loại vitamin nào quan trọng cho sức khỏe của xương?''': '''Vitamin D''',
'''Câu đố kiến thức : Loại vitamin nào được sản xuất trong cơ thể người khi tiếp xúc với ánh sáng mặt trời?''': '''Vitamin D''',
'''Câu đố kiến thức : Loại đèn nào sử dụng năng lượng mặt trời thường gặp ở các khu vườn?''': '''Đèn năng lượng mặt trời''',
'''Câu đố kiến thức : Loại đèn nào tiết kiệm năng lượng nhất?''': '''Đèn LED''',
'''Câu đố kiến thức : Loại đồ uống nào có thể giúp giảm căng thẳng?''': '''Trà xanh''',
'''Câu đố kiến thức : Loại động vật nào giúp thụ phấn cho hoa?''': '''Ong''',
'''Câu đố kiến thức : Làm thế nào bạn có thể giảm lượng nước tiêu thụ ở nhà?''': '''Tất cả các phương án trên''',
'''Câu đố kiến thức : Làm thế nào để giảm sự phụ thuộc vào điện thoại thông minh?''': '''Đặt giới hạn thời gian sử dụng mỗi ngày''',
'''Câu đố kiến thức : Lợi ích của việc ăn nhiều rau xanh là gì?''': '''Giảm nguy cơ mắc bệnh mãn tính''',
'''Câu đố kiến thức : Lợi ích của việc đi bộ đều đặn là gì?''': '''Cải thiện sức khỏe tim mạch và cơ bắp''',
'''Câu đố kiến thức : Món "cá kho làng Vũ Đại" nổi tiếng thuộc tỉnh nào của Việt Nam?？''': '''Hà Nam''',
'''Câu đố kiến thức : Nhiệt độ lý tưởng để giặt quần áo bằng máy giặt là bao nhiêu để tiết kiệm năng lượng?''': '''30 độ C''',
'''Câu đố kiến thức : Nhiệt độ nào là lý tưởng để bảo quản thực phẩm trong tủ lạnh?''': '''4 độ C''',
'''Câu đố kiến thức : Nước có vai trò gì trong cơ thể?''': '''Giúp tất cả các tế bào, mô và cơ quan hoạt động''',
'''Câu đố kiến thức : Sử dụng loại túi nào là tốt nhất cho môi trường khi mua sắm?''': '''Túi vải tái sử dụng''',
'''Câu đố kiến thức : Trong các loại đá sau, đá nào là đá biến chất?''': '''Đá phiến''',
'''Câu đố kiến thức : Tác dụng của việc ngủ đủ giấc là gì?''': '''Cải thiện sức khỏe tổng thể và tinh thần''',
'''Câu đố kiến thức : Tác dụng của việc tập yoga đều đặn là gì?''': '''Cải thiện sức khỏe tinh thần và thể chất''',
'''Câu đố kiến thức : Tác dụng của việc đọc sách đối với não bộ là gì?''': '''Tăng cường khả năng tập trung và trí nhớ''',
'''Câu đố kiến thức : Tên gọi của hiện tượng mà trong đó mặt trăng che khuất mặt trời là gì?''': '''Nhật thực''',
'''Câu đố kiến thức : Tại sao bạn cần uống nhiều nước khi thời tiết nóng?''': '''Ngăn ngừa sự mất nước''',
'''Câu đố kiến thức : Tại sao bạn cần đội mũ bảo hiểm khi đi xe đạp?''': '''Để bảo vệ đầu trong trường hợp va chạm''',
'''Câu đố kiến thức : Tại sao bạn nên hạn chế tiêu thụ đường?''': '''Nó có thể dẫn đến tăng cân và các vấn đề sức khỏe khác''',
'''Câu đố kiến thức : Tại sao không nên dùng điện thoại trước khi đi ngủ?''': '''Có thể làm gián đoạn chu kỳ giấc ngủ''',
'''Câu đố kiến thức : Tại sao không nên để đồ điện tử như điện thoại di động trong phòng ngủ vào ban đêm?''': '''Chúng làm gián đoạn giấc ngủ''',
'''Câu đố kiến thức : Tại sao lá cây thay đổi màu sắc vào mùa thu?''': '''Do giảm sản xuất chlorophyll''',
'''Câu đố kiến thức : Tại sao nên tái chế giấy?''': '''Tất cả các phương án trên''',
'''Câu đố kiến thức : Tại sao việc phân loại rác thải quan trọng?''': '''Giảm tác động đến môi trường''',
'''Câu đố kiến thức : Tại sao việc tiếp xúc thường xuyên với ánh sáng tự nhiên là quan trọng?''': '''Nó Giúp Cải Thiện Tâm Trạng Và Giấc Ngủ''',
'''Câu đố kiến thức : Tại sao ăn nhiều rau quả lại tốt cho sức khỏe?''': '''Chúng Cung Cấp Nhiều Vitamin Và Khoáng''',
'''Câu đố kiến thức : Tập thể dục đều đặn có lợi ích gì?''': '''Cải thiện sức khỏe tâm thần và thể chất''',
'''Câu đố kiến thức : Uống nhiều nước có lợi ích gì cho cơ thể?''': '''Tăng cường chức năng thận''',
'''Câu đố kiến thức : Uống nước đầy đủ mỗi ngày có lợi ích gì đối với hệ tiêu hóa?''': '''Giúp hệ tiêu hóa hoạt động hiệu quả''',
'''Câu đố kiến thức : Vitamin C có vai trò gì trong cơ thể?''': '''Giúp xây dựng và duy trì mô liên kết, tăng cường hệ miễn dịch''',
'''Câu đố kiến thức : Vitamin D có vai trò gì trong việc bảo vệ xương?''': '''Giúp xương hấp thụ canxi''',
'''Câu đố kiến thức : Vitamin E có lợi ích gì đối với cơ thể?''': '''Có tác dụng chống oxy hóa''',
'''Câu đố kiến thức : Vitamin nào quan trọng cho sức khỏe của mắt?''': '''Vitamin A''',
'''Câu đố kiến thức : Vịnh Lăng Cô nổi tiếng thuộc tỉnh nào ở Việt Nam?''': '''Thừa Thiên Huế''',
'''Câu đố kiến thức : Ánh sáng mặt trời cung cấp loại năng lượng nào?''': '''Quang năng''',
'''Câu đố kiến thức : Âm thanh di chuyển nhanh nhất qua môi trường nào?''': '''Rắn''',
'''Câu đố kiến thức : Ăn cá giúp cung cấp nguồn gì cho cơ thể?''': '''Protein''',
'''Câu đố kiến thức : Ăn cá thường xuyên có lợi ích gì cho sức khỏe não bộ?''': '''Tăng cường chức năng nhận thức''',
'''Câu đố kiến thức : Ăn cá thường xuyên có thể cung cấp loại acid béo nào tốt cho tim?''': '''Acid omega-3''',
'''Câu đố kiến thức : Ăn cá thường xuyên có thể giúp giảm nguy cơ mắc bệnh gì?''': '''Bệnh Tim''',
'''Câu đố kiến thức : Ăn loại hạt nào có thể giúp cải thiện trí nhớ?''': '''Hạnh nhân''',
'''Câu đố kiến thức : Ăn loại trái cây nào giúp cung cấp nhiều chất xơ?''': '''Táo''',
'''Câu đố kiến thức : Ăn quả hạch như óc chó, hạnh nhân có lợi ích gì?''': '''Tăng cường sức khỏe tim mạch''',
'''Câu đố kiến thức : Ăn thực phẩm giàu chất xơ có lợi ích gì?''': '''Giúp kiểm soát cân nặng và cải thiện hệ tiêu hóa''',
'''Câu đố kiến thức : Ăn thực phẩm giàu omega-3 có lợi ích gì cho não?''': '''Cải thiện chức năng nhận thức''',
'''Câu đố kiến thức : Điều gì xảy ra nếu bạn không bảo dưỡng máy lạnh định kỳ?''': '''Giảm tuổi thọ của máy''',
'''Câu đố kiến thức : Điều gì xảy ra nếu bạn không tiêu thụ đủ các vitamin và khoáng chất?''': '''Có thể dẫn đến các vấn đề sức khỏe''',
'''Câu đố kiến thức : Đâu không phải là một loại năng lượng tái tạo?''': '''Năng lượng than đá''',
'''Câu đố kiến thức : Đâu không phải là một phương pháp tái chế?''': '''Chôn lấp rác thải''',
'''Câu đố kiến thức : Đâu là biện pháp hiệu quả để giảm ô nhiễm không khí trong nhà?''': '''Mở cửa sổ để không khí lưu thông''',
'''Câu đố kiến thức : Đâu là lợi ích của việc đi bộ hàng ngày?''': '''Cải thiện sức khỏe tim mạch''',
'''Câu đố kiến thức : Đơn vị nào được dùng để đo cường độ âm thanh?''': '''Decibel''',
'''Câu đố kiến thức : Động vật nào sau đây không phải là động vật xương sống?''': '''Sâu bướm''',
'''Câu đố kiến thức :"Bánh bột lọc" là món ăn truyền thống của tỉnh nào?''': '''Thừa Thiên Huế''',
'''Câu đố kiến thức :"Bánh canh chả cá" là món ăn đặc trưng của thành phố nào?''': '''Nha Trang''',
'''Câu đố kiến thức :"Bánh cuốn" là đặc sản của vùng nào ở Việt Nam?''': '''Hà Nội''',
'''Câu đố kiến thức :"Bánh cuốn" thường được làm từ loại bột nào?''': '''Bột gạo''',
'''Câu đố kiến thức :"Bánh khoái" là món ăn đặc trưng của tỉnh nào?''': '''Thừa Thiên Huế''',
'''Câu đố kiến thức :"Bánh xèo" thường được ăn kèm với gì?''': '''Nước mắm riêng''',
'''Câu đố kiến thức :"Bình Ngô đại cáo" được soạn vào thời gian nào?''': '''Đời Lê''',
'''Câu đố kiến thức :"Bún bò Huế" là món ăn truyền thống của vùng nào ở Việt Nam?''': '''Trung Bộ''',
'''Câu đố kiến thức :"Bún bò Huế" là món ăn đặc sản của tỉnh nào?''': '''Thừa Thiên Huế''',
'''Câu đố kiến thức :"Bún thang" là món ăn truyền thống của vùng nào?''': '''Hà Nội''',
'''Câu đố kiến thức :"Chiếc thuyền ngoài xa" là tác phẩm của nhà văn nào?''': '''Nguyễn Minh Châu''',
'''Câu đố kiến thức :"Chiến dịch Hồ Chí Minh" diễn ra vào năm nào, dẫn đến sự thống nhất đất nước?''': '''1975''',
'''Câu đố kiến thức :"Chí Phèo" là nhân vật trong tác phẩm nào?''': '''Chí Phèo''',
'''Câu đố kiến thức :"Cà phê Trung Nguyên" nổi tiếng từ vùng nào ở Việt Nam?''': '''Buôn Ma Thuột''',
'''Câu đố kiến thức :"Cà phê sữa đá" xuất phát từ vùng nào ở Việt Nam?''': '''Hồ Chí Minh''',
'''Câu đố kiến thức :"Cơm tấm" là món ăn đặc trưng của thành phố nào?''': '''Hồ Chí Minh''',
'''Câu đố kiến thức :"Hiệp định Paris" về Việt Nam được ký kết vào năm nào?''': '''1973''',
'''Câu đố kiến thức :"Lẩu mắm" là món ăn nổi tiếng của vùng nào ở Việt Nam?''': '''Đồng bằng sông Cửu Long''',
'''Câu đố kiến thức :"Mì Quảng" là món ăn đặc sản của tỉnh nào?''': '''Quảng Nam''',
'''Câu đố kiến thức :"Nem chua" là món ăn đặc trưng của tỉnh nào ở Việt Nam?''': '''Thanh Hóa''',
'''Câu đố kiến thức :"Nem rán" còn có tên gọi khác là gì ?''': '''Chả giò''',
'''Câu đố kiến thức :"Thằng Bờm" là tác phẩm văn học dân gian của vùng nào?''': '''Bắc Bộ''',
'''Câu đố kiến thức :"Thịt kho tàu" là món ăn truyền thống của dịp lễ nào ở Việt Nam?''': '''Tết Nguyên Đán''',
'''Câu đố kiến thức :"Truyện Kiều" là tác phẩm của tác giả nào?''': '''Nguyễn Du''',
'''Câu đố kiến thức :"Tắt đèn" là tác phẩm nổi tiếng của nhà văn nào?''': '''Ngô Tất Tố''',
'''Câu đố kiến thức :"Đất Rừng Phương Nam" là tác phẩm của ai?''': '''Đoàn Giỏi''',
'''Câu đố kiến thức :Ai là Hoàng đế cuối cùng của triều đại phong kiến Việt Nam?''': '''Bảo Đại''',
'''Câu đố kiến thức :Ai là anh hùng dân tộc đã chỉ huy trận Điện Biên Phủ?''': '''Võ Nguyên Giáp''',
'''Câu đố kiến thức :Ai là anh hùng dân tộc đã lãnh đạo cuộc khởi nghĩa Lam Sơn?''': '''Lê Lợi''',
'''Câu đố kiến thức :Ai là người lãnh đạo cuộc khởi nghĩa Lam Sơn chống quân Minh xâm lược?''': '''Lê Lợi''',
'''Câu đố kiến thức :Ai là người phát minh ra điện thoại?''': '''Alexander Graham Bell''',
'''Câu đố kiến thức :Ai là người sáng lập ra triều đại nhà Hồ?''': '''Hồ Quý Ly''',
'''Câu đố kiến thức :Ai là người đã thành lập Đảng Cộng sản Việt Nam?''': '''Hồ Chí Minh''',
'''Câu đố kiến thức :Ai là tác giả của bài hát "Nối vòng tay lớn"?''': '''Trịnh Công Sơn''',
'''Câu đố kiến thức :Ai là tác giả của tác phẩm "Vợ chồng A Phủ"?''': '''Tô Hoài''',
'''Câu đố kiến thức :Ai là tác giả của tác phẩm văn học "Số đỏ"?''': '''Vũ Trọng Phụng''',
'''Câu đố kiến thức :Ai là vị vua đầu tiên của nhà Nguyễn?''': '''Gia Long''',
'''Câu đố kiến thức :Biển nào lớn nhất Việt Nam?''': '''Biển Đông''',
'''Câu đố kiến thức :Cao nguyên Mộc Châu thuộc tỉnh nào của Việt Nam?''': '''Sơn La''',
'''Câu đố kiến thức :Cao nguyên đá Đồng Văn nổi tiếng thuộc tỉnh nào của Việt Nam?''': '''Hà Giang''',
'''Câu đố kiến thức :Chiến dịch Điện Biên Phủ giành thắng lợi vào năm nào ?''': '''1954''',
'''Câu đố kiến thức :Chế độ phong kiến ở Việt Nam chính thức kết thúc vào năm nào?''': '''1945''',
'''Câu đố kiến thức :Cù lao Chàm thuộc tỉnh nào của Việt Nam?''': '''Quảng Nam''',
'''Câu đố kiến thức :Cầu Rồng nằm ở thành phố nào của Việt Nam?''': '''Đà Nẵng''',
'''Câu đố kiến thức :Hồ Gươm (Hồ Hoàn Kiếm) nằm ở thành phố nào của Việt Nam?''': '''Hà Nội''',
'''Câu đố kiến thức :Hồ Tây là hồ nước ngọt lớn nhất nằm ở thành phố nào của Việt Nam?''': '''Hà Nội''',
'''Câu đố kiến thức :Hội nghị Diên Hồng được tổ chức vào thời kỳ nào?''': '''Trần''',
'''Câu đố kiến thức :Khu bảo tồn thiên nhiên nào ở Việt Nam là Di sản Thế giới?''': '''Phong Nha - Kẻ Bàng''',
'''Câu đố kiến thức :Món "bánh cuốn Thanh Trì" bắt nguồn từ khu vực nào ở Việt Nam?''': '''Hà Nội''',
'''Câu đố kiến thức :Món "phở bò" truyền thống không thể thiếu thành phần nào sau đây?''': '''Bánh phở''',
'''Câu đố kiến thức :Món ăn "giò lụa" thường được làm từ nguyên liệu chính nào?''': '''Thịt heo''',
'''Câu đố kiến thức :Nguyễn Trãi là tác giả của tác phẩm lịch sử nào nổi tiếng?''': '''Bình Ngô Đại Cáo''',
'''Câu đố kiến thức :Núi Bà Nà nổi tiếng với cáp treo nằm ở đâu?''': '''Đà Nẵng''',
'''Câu đố kiến thức :Sông Hương nổi tiếng thơ mộng chảy qua thành phố nào của Việt Nam?''': '''Huế''',
'''Câu đố kiến thức :Sông nào là con sông dài nhất miền Bắc Việt Nam?''': '''Sông Hồng''',
'''Câu đố kiến thức :Thành phố nào của Việt Nam được mệnh danh là "Thành phố ngàn hoa"?''': '''Đà Lạt''',
'''Câu đố kiến thức :Thác Bản Giốc thuộc tỉnh nào của Việt Nam?''': '''Cao Bằng''',
'''Câu đố kiến thức :Tác giả của tập thơ "Nhật ký trong tù" là ai?''': '''Hồ Chí Minh''',
'''Câu đố kiến thức :Tác phẩm "Dế Mèn Phiêu Lưu Ký" do ai sáng tác?''': '''Tô Hoài''',
'''Câu đố kiến thức :Tỉnh nào của Việt Nam có vịnh Vân Phong, một vịnh biển đẹp nổi tiếng?''': '''Khánh Hòa''',
'''Câu đố kiến thức :Tỉnh nào của Việt Nam có địa hình là đảo lớn nhất?''': '''Kiên Giang''',
'''Câu đố kiến thức :Tỉnh nào ở Việt Nam được mệnh danh là thủ phủ của cây cà phê?''': '''Đắk Lắk''',
'''Câu đố kiến thức :Vua nào xây dựng đền Angkor Wat?''': '''Suryavarman II''',
'''Câu đố kiến thức :Đèo Hải Vân nằm trên quốc lộ nào?''': '''Quốc lộ 1A''',
'''Câu đố kiến thức :Đèo Ngang nằm giữa hai tỉnh nào của Việt Nam?''': '''Quảng Bình và Hà Tĩnh''',
'''Câu đố kiến thức :Đảo Lý Sơn nằm ở tỉnh nào của Việt Nam?''': '''Quảng Ngãi''',
'''Câu đố kiến thức :Đảo Lý Sơn nổi tiếng với sản phẩm nào?''': '''Tỏi''',
'''Câu đố kiến thức :Đảo Phú Quốc thuộc tỉnh nào của Việt Nam?''': '''Kiên Giang''',
'''Câu đố kiến thức :Đỉnh Fansipan thuộc dãy núi nào?''': '''Dãy Hoàng Liên Sơn''',
'''Câu đố kiến thức :Đỉnh Langbiang nằm ở tỉnh nào của Việt Nam?''': '''Lâm Đồng''',
'''Câu đố kiến thức :Đỉnh Yên Tử nổi tiếng với lịch sử Phật giáo thuộc tỉnh nào?''': '''Quảng Ninh''',
'''Câu đố kiến thức :Đỉnh núi cao nhất Việt Nam là gì?''': '''Núi Phan Xi Păng''',
'''Câu đố kiến thức :Đỉnh núi nào là điểm cao nhất Đông Dương?''': '''Phan Xi Păng''',
'''Câu đố kiến thức :Địa đầu của Việt Nam ở phía Nam là điểm nào?''': '''Mũi Cà Mau''',
'''Câu đố kiến thức: Thành phố nào của Việt Nam được biết đến với tên gọi "Thành phố Hoa Phượng Đỏ"?''': '''Hải Phòng''',
'''Câu đố kiến thức: Ăn gì có thể giúp cải thiện sức khỏe của tim?''': '''Bơ''',
'''Cây gì càng trông càng thấy thấp?''': '''Cây nến''',
'''Cây gì càng đốt nhiều càng dài?''': '''Cây tre''',
'''Cây gì mà tên của nó nghe tên như đã chết. Nhưng trên thực tế nó vẫn sống và còn đơm hoa kết trái?''': '''Cây tiêu''',
'''Cây nào là nguồn gốc của chocolate?''': '''Cây ca cao''',
'''Cây nến đốt càng nhiều càng ngắn. Cây gì đốt càng nhiều càng dài?''': '''Cây tre''',
'''Có 1 đàn chim đậu trên cành, người thợ săn bắn cái rằm. Hỏi chết mấy con?''': '''15''',
'''Có 2 con mèo Vàng và con mèo Đen , con mèo Vàng bỏ con mèo Đen đi với con mèo Nâu, 13 năm sau con mèo Vàng về với con mèo Đen hỏi nó nói gì trước tiên''': '''Meo meo''',
'''Có 3 thằng lùn xếp hàng dọc đi vào hang. Thằng đi sau cầm 1 cái xô, thằng đi giữa cầm 1 cái xẻng, hỏi thằng đi trước cầm gì?''': '''Cầm đầu''',
'''Có bao nhiêu nữ thanh niên xung phong hi sinh ở Ngã Ba Đồng Lộc?''': '''10''',
'''Có câu 'Ăn chắc mặc...' gì?''': '''Bền''',
'''Có câu: "Dài lưng tốn ..." gì?''': '''Vải''',
'''Có câu: "Ăn chắc mặc ..." gì?''': '''Bền''',
'''Có câu: 'Của người phúc ... gì?''': '''Ta''',
'''Có câu: 'Hai năm rõ ...' mấy?''': '''Mười''',
'''Có một mảnh gỗ cần cắt ra làm 50 miếng. Thời gian để cắt được 1 miếng gỗ là 1 phút. Hỏi nếu cắt liên tục không nghỉ thì bao lâu sẽ cắt xong mảnh gỗ''': '''49 phút''',
'''Công chúa triều Trần được gả cho Vua Chiêm Chế Mân là ai?''': '''Huyền Trân''',
'''Công cụ tìm kiếm phổ biến nhất hiện nay là gì?''': '''Google''',
'''Công thức hóa học của nước là gì?''': '''H2O''',
'''Công ty nào phát triển hệ điều hành Windows?''': '''Microsoft''',
'''Công viên chủ đề nổi tiếng nào tổ chức Halloween Horror Nights hàng năm?''': ''' Disneyland''',
'''Cơ quan quyền lực nhà nước cao nhất ở nước ta hiện nay là?''': '''Quốc hội''',
'''Cầu Rồng là biểu tượng của thành phố nào ở Việt Nam?''': '''Đà Nẵng''',
'''Cầu thủ Francesco Totti đã thi đấu cho câu lạc bộ nào trong suốt sự nghiệp của mình?''': '''AS Roma''',
'''Cầu thủ Lionel Messi đã chuyển đến Ligue 1 vào năm nào?''': '''2021''',
'''Cầu thủ Ronaldinho giành Quả Bóng Vàng vào năm nào?''': '''2005''',
'''Cầu thủ ghi nhiều hat trick nhất trong một mùa giải tại EPL tính đến năm 2023?''': '''Alan Shearer''',
'''Cầu thủ nào có kiến tạo nhiều nhất tại giải Ngoại Hạng Anh tính đến năm 2022?''': '''Ryan Giggs''',
'''Cầu thủ nào ghi nhiều bàn thắng nhất trong lịch sử Champions League ( CÚP C1 )?''': '''Cristiano Ronaldo''',
'''Cầu thủ nào giành danh hiệu "Cầu thủ xuất sắc nhất Serie A" năm 2021-2022?''': '''Rafael Leão''',
'''Cầu thủ nào thi đấu nhiều mùa giải nhất tại giải Ngoại Hạng Anh tính đến mùa giải 2020-2021?''': '''Ryan Giggs''',
'''Cầu thủ nào thi đấu nhiều trận nhất tại giải Ngoại Hạng Anh tính đến năm 2021?''': '''Gareth Barry''',
'''Cầu thủ nào đã giành danh hiệu Vua phá lưới nhiều lần nhất trong Champions League?''': '''Cristiano Ronaido''',
'''Cầu thủ nào đã giành được nhiều Quả bóng Vàng nhất tính đến năm 2023?''': '''Lionel Messi''',
'''Cầu thủ xuất sắc nhất Ligue 1 mùa giải 2022-2023 là ai?''': '''Kylian Mbappé''',
'''Cắm vào run rẩy toàn thân, Rút ra nước chảy từ chân xuống sàn, Hỡi chàng công tử giàu sang, Cắm vào xin chớ vội vàng rút ra!''': '''Cái tủ lạnh''',
'''Cờ Thụy Sĩ có bao nhiêu màu ?''': '''2''',
'''Da cóc mà bọc bột lọc, Bột lọc mà bọc hòn than - Là quả gì?''': '''Quả nhãn''',
'''Da cóc mà bọc trứng gà, bổ ra thơm nức cả nhà muốn ăn - Là quả gì?''': '''Quả mít''',
'''Da trắng muốt. Ruột trắng tinh. Bạn với học sinh. Thích cọ đầu vào bảng? (Là cái gì?)''': '''Viên phấn''',
'''Di sản thiên nhiên nào của Việt Nam được UNESCO công nhận năm 1994?''': '''Vịnh Hạ Long''',
'''Di tích Cố đô Huế được công nhận là Di sản văn hóa thế giới vào năm nào?''': '''1993''',
'''Di tích lịch sử Văn Miếu - Quốc Tử Giám nằm ở thành phố nào?''': '''Hà Nội''',
'''Doha là thủ đô của quốc gia nào?''': '''Qatar''',
'''Dãy núi Andes nằm ở đâu?''': '''Nam Mỹ''',
'''Dãy núi dài nhất thế giới là gì?''': ''' Andes''',
'''Dừa sáp được coi là đặc sản của tỉnh nào ?''': '''Trà Vinh''',
'''Game show GHÉP CHỮ OKVIP có giới hạn thời gian không ?''': '''KHÔNG GIỚI HẠN, KHI NÀO GHÉP ĐỦ CHỮ OKVIP THÌ KHI ĐÓ SẼ ĐƯỢC TẶNG VÒNG QUAY MAY MẮN''',
'''Game show TRẢ LỜI CÂU HỎI CÓ THƯỞNG. Khoảng cách thời gian giữa các câu hỏi là bao lâu ?''': '''20 GIÂY''',
'''Gameshow CHIA SẺ CÓ QUÀ được hỗ trợ xét duyệt thông qua kênh hỗ trợ CSKH nào ?''': '''HỖ TRỢ QUA KÊNH TELEGRAM 24/7''',
'''Giống gà nổi tiếng với đôi chân to, xù xì ở Hưng Yên có tên gọi là gì?''': '''Gà Đông Tảo''',
'''Hai Bà Trưng đã khởi nghĩa chống lại ách đô hộ của triều đại nào?''': ''' Nhà Đông Hán''',
'''Hai cô nằm nghỉ hai phòng. Ngày thì mở cửa ra trông, đêm thì đóng cửa lấp trong ra ngoài. Đó là gì?''': '''Đôi mắt''',
'''Hai người đào trong hai giờ thì được một cái hố. Hỏi nếu một người đào trong một giờ thì được mấy cái hố''': '''Một cái hố''',
'''Hai nhà khoa học Konstantin Novoselov và Andre Geim đã giành giải Nobel về lĩnh vực gì?''': '''Vật lí''',
'''Halloween bắt nguồn từ nước nào?''': ''' Ireland''',
'''Halloween còn được biết đến với tên gọi gì khác?''': ''' Lễ hội ma quỷ''',
'''Halloween diễn ra vào ngày nào mỗi năm?''': ''' 31 tháng 10''',
'''Hiện nay, nước ta có bao nhiêu tỉnh mang từ 'Giang' ở cuối tên gọi?''': '''6''',
'''Hoa gì biết ăn, biết nói, biết hát …?''': '''Hoa hậu''',
'''Hoa hậu Hoàn vũ Việt Nam năm 2017 là ai?''': '''H’Hen Niê''',
'''Hoa hậu nào đã đăng quang Hoa hậu Hoàn vũ Việt Nam 2017?''': '''H’Hen Niê''',
'''Huyền thoại Hồ Gươm gắn liền với vị vua nào?''': '''Lê Lợi''',
'''Huyền thoại bóng đá Pelé là người nước nào?''': '''Brazil''',
'''Huấn luyện viên nào đã giành được nhiều chức vô địch Champions League nhất tính đến năm 2024?''': '''Carlo Ancelotti''',
'''Hành tinh nào gần Mặt Trời nhất?''': ''' Sao Thủy''',
'''Hãy cho biết ngọn núi trong hình là ngọn núi nào?''': '''Phú Sĩ''',
'''Hãy cho biết từ nào còn thiếu trong câu thành ngữ sau: "Dính như ..."?''': '''Sam''',
'''Hãy cho biết đây là các nhân vật trong phim hoạt hình nổi tiếng nào?''': '''Doraemon''',
'''Hãy cho biết động lực chính của Liên Minh OKVIP trên hành trình thiện nguyện nhiều năm nay là gì?''': '''Tất cả các ý trên''',
'''Hãy chọn các hoạt động từ thiện mà Liên Minh OKVIP đã từng tham gia?''': '''Tất cả các ý trên''',
'''Hình ảnh trên mặt sau tờ 200.000 Đồng là chỉ địa danh nào?''': '''Hòn Đỉnh Hương''',
'''Hạt rơi tới tấp, rãi khắp ruộng đồng, nhưng hạt rơi chẳng nảy mầm. Để bao hạt khác mừng thầm mọc xanh. (Là gì?)''': '''Hạt mưa''',
'''Hạt thanh long thường có màu gì?''': '''Đen''',
'''Hệ mặt trời có bao nhiêu hành tinh?''': '''8''',
'''Hồ Baikal, hồ nước ngọt sâu nhất thế giới, nằm ở đâu?''': '''Nga''',
'''Hồ nào là hồ nước ngọt sâu nhất thế giới?''': ''' Hồ Baikal''',
'''Hội An, một di sản văn hóa thế giới, nằm ở tỉnh nào?''': '''Quảng Nam''',
'''Hội viên có thể rút tiền tại Liên Minh OKVIP thông qua hình thức nào?''': '''Chuyển điểm tích luỹ đến tài khoản thành viên thuộc Liên Minh OKVIP''',
'''Hứng dừa là tác phẩm thuộc dòng tranh dân gian nào?''': '''Đông Hồ''',
'''Khi Beckham thực hiện quả đá phạt đền, anh ta sẽ sút vào đâu?''': '''Trái banh''',
'''Khi chưa ai biết nó thì nó vẫn là nó. Khi đã biết nó rồi thì nó không còn là nó nữa. Nó là gì?''': '''Bí mật''',
'''Khi liên kết tài khoản thành viên, cần những thông tin gì?''': '''Tên tài khoản và 4 số cuối điện thoại thành viên''',
'''Khi liên kết tài khoản thành viên, điều nào của tài khoản thành viên là không bắt buộc ?''': '''Tài khoản thành viên phải có tổng nạp trên 10 triệu.''',
'''Khi thái nhiều hành tây chúng ta thường bị làm sao?''': '''Cay mắt''',
'''Khi xem bóng trên trang LuongSonTV có tốn phí không ?''': '''HOÀN TOÀN MIỄN PHÍ''',
'''Khi đăng ký tài khoản hội viên OKVIP, thông tin nào là không bắt buộc ?''': '''Số tài khoản ngân hàng''',
'''Khu di tích Mỹ Sơn nằm ở tỉnh nào?''': '''Quảng Nam''',
'''Khu du lịch Tam Cốc - Bích Động thuộc tỉnh nào?''': '''Ninh Bình''',
'''Khu vực Đông Nam Á gồm có bao nhiêu quốc gia?''': '''11''',
'''Khẩu hiệu của Liên Minh OKVIP là gì?''': '''HÔM NAY 1 TỶ, NGÀY MAI 1000 TỶ''',
'''Khẩu hiệu của trang Giải Trí 78win - thuộc Liên Minh OKVIP là gì?''': '''CHIẾN THẮNG LÀ VÔ HẠN''',
'''Khẩu hiệu của trang Giải Trí MB66 - thuộc Liên Minh OKVIP là gì?''': '''MỘT BƯỚC LÀM GIÀU''',
'''Kim tự tháp Ai Cập nằm bên bờ sông nào?''': '''Sông Nile''',
'''Kim tự tháp Giza nằm ở quốc gia nào?''': ''' Ai Cập''',
'''La Habana (Havana) là thủ đô nước nào?''': '''Cuba''',
'''Lephet là món ăn của nước nào?''': '''Myanmar''',
'''Ligue 1 là giải đấu thuộc quốc gia nào?''': '''Pháp''',
'''Ligue 1 được thành lập vào năm nào?''': '''1932''',
'''Lionel Messi đã giành được bao nhiêu chức vô địch Champions League với Barcelona?''': '''4''',
'''Liên Minh OKVIP đã ký hợp đồng thương hiệu với câu lạc bộ nào?''': '''CLB Villarreal''',
'''Liên Minh OKVIP đã tham gia chương trình "Bếp ăn không đồng - kết nối yêu thương" ở đâu?''': '''Bệnh Viện Huyết Học và Truyền Máu Hà Nội''',
'''Loài chim nào có thể bay lùi?''': '''Chim ruồi''',
'''Loài chim nào không thể bay?''': '''Đà điểu''',
'''Loài chim nào nhỏ nhất sau đây?''': '''Chim ruồi''',
'''Loài vật nào sau đây được biết đến là chim báo bão ?''': '''Hải âu''',
'''Loài động vật nào có ngón tay giống con người đến mức để lại dấu vân tay giống vân tay người?''': ''' Koala''',
'''Loài động vật nào có tốc độ chạy nhanh nhất trên mặt đất?''': '''Báo''',
'''Loài động vật nào là biểu tượng của Australia?''': '''Chuột túi (Kangaroo)''',
'''Loài động vật nào lớn nhất trên Trái Đất?''': ''' Cá voi xanh''',
'''Loài động vật nào được cho là bạn đồng hành của phù thủy trong Halloween?''': ''' Mèo đen''',
'''Loại quả nào dưới đây thường được dùng để ngâm rượu?''': '''Táo mèo''',
'''Loại sóng nào được sử dụng để nấu chín thức ăn trong lò vi sóng?''': '''Sóng vi ba''',
'''Loại tế bào nào chịu trách nhiệm truyền tải tín hiệu trong cơ thể?''': '''Tế bào thần kinh''',
'''Loại đá nào được hình thành từ quá trình nung chảy và làm nguội magma?''': '''Đá mácma''',
'''Loại đá nào được hình thành từ xác động vật?''': '''Đá trầm tích hữu cơ''',
'''Loại đồ uống nào ban đầu được phát minh như một loại thuốc chữa bệnh?''': ''' Nước ép cam''',
'''Làng Vòng Hà Nội có đặc sản gì nổi tiếng?''': '''Cốm''',
'''Lập Duy Tân hội, sang Nhật cầu viện, Phát động phong trào Đông Du - Là ai?''': '''Phan Bội Châu''',
'''Lễ hội nào tương tự Halloween được tổ chức tại Mexico?''': ''' Día de los Muertos''',
'''Lễ hội nào ở Việt Nam được tổ chức để tưởng nhớ các vua Hùng?''': '''Lễ hội Đền Hùng''',
'''Lục địa nào có khí hậu lạnh giá quanh năm?''': '''Châu Nam Cực''',
'''MacKinnon đã đạt giải Nobel trong lĩnh vực nào?''': '''Hóa học''',
'''Myanmar thuộc châu lục nào?''': '''Châu Á''',
'''Màu nào sau đây hấp thụ nhiệt tốt nhất ?''': '''Đen''',
'''Màu sắc nào là màu của bầu trời vào một ngày nắng?''': ''' Xanh''',
'''Màu sắc truyền thống của Halloween là gì?''': ''' Đen và cam''',
'''Môn học nào nghiên cứu về sự sống và các loài sinh vật?''': ''' Sinh học''',
'''Môn học nào thường bao gồm việc giải các phương trình và bất phương trình?''': '''Toán học''',
'''Môn thể thao nào là phổ biến nhất trên thế giới?''': '''Bóng đá''',
'''Môn thể thao nào mà người thi đấu càng lùi càng thắng?''': '''Kéo co''',
'''Môn thể thao nào đã giúp Nguyễn Tiến Minh nổi tiếng trong thể thao Việt Nam?''': '''Cầu lông''',
'''Mũi Né là điểm du lịch nổi tiếng thuộc tỉnh nào của Việt Nam?''': '''Bình Thuận''',
'''Mạng xã hội nào được sáng lập bởi Mark Zuckerberg?''': '''Facebook''',
'''Mặt gì bằng phẳng thênh thang. Người đi muôn lối dọc ngang phố phường?''': '''Mặt đất''',
'''Mặt nào không bao giờ đứng yên, thuyền qua tàu lại suốt đêm suốt ngày?''': '''Mặt biển''',
'''Mỗi năm có 7 tháng 31 ngày. Đố bạn có bao nhiêu tháng có 28 ngày?''': '''12''',
'''Mỗi năm có 7 tháng 31 ngày. Đố bạn có bao nhiêu tháng có 28 ngày?''': '''12''',
'''Một ly thuỷ tinh đựng đầy nước, làm thế nào để lấy nước dưới đáy ly mà không đổ nước ra ngoài ?''': '''Ống hút''',
'''Một người phụ nữ 50 tuổi thì người đó có bao nhiêu ngày sinh nhật?''': '''Một ngày sinh nhật.''',
'''Một đàn chim 15 con đậu trên cây. Người thợ săn giơ súng bắn 5 phát, hỏi trên cây còn mấy con?''': '''0''',
'''Mục Tài trợ trên trang chủ có nội dung gì ?''': '''Giới thiệu các hoạt động ký kết của Liên Minh OKVIP với các đại sứ thương hiệu nổi tiếng toàn cầu.''',
'''Neymar là cầu thủ bóng đá nổi tiếng người nước nào?''': '''Brazil''',
'''Nghệ sĩ nào được mệnh danh là “Nữ hoàng nhạc pop Việt Nam”?''': '''Mỹ Tâm''',
'''Nguyên tố hóa học nào là kim loại nhẹ nhất?''': '''Liti''',
'''Nguyên tố nào có số nguyên tử là 6?''': '''Carbon''',
'''Nguyên tố nào nhẹ nhất trong bảng tuần hoàn?''': '''Hydro''',
'''Ngày Báo chí Cách mạng Việt Nam là ngày nào?''': '''21/06''',
'''Ngày Chủ tịch Hồ Chí Minh đọc Tuyên ngôn độc lập là ngày nào?''': '''02/09''',
'''Ngày Giải phóng miền Nam, thống nhất đất nước là ngày nào?''': '''30 tháng 4''',
'''Ngày Nhà giáo Việt Nam là ngày nào?''': '''20/11''',
'''Ngày Phụ nữ Việt Nam là ngày nào?''': '''20/10''',
'''Ngày Quốc khánh Việt Nam là ngày nào?''': '''02/09''',
'''Ngày Quốc tế Lao động là ngày nào?''': '''01/05''',
'''Ngày Quốc tế Thiếu nhi là ngày nào?''': '''01/06''',
'''Ngày Thương binh - Liệt sĩ Việt Nam là ngày nào?''': '''27/07''',
'''Ngày Thương binh Liệt sĩ Việt Nam được tổ chức vào ngày nào?''': '''27/7''',
'''Ngày Thầy thuốc Việt Nam là ngày nào?''': '''27/02''',
'''Ngày lễ Giỗ Tổ Hùng Vương được tổ chức vào ngày nào hàng năm?''': '''Mùng 10 tháng 3 âm lịch''',
'''Ngày quốc tế phụ nữ được tổ chức vào ngày nào?''': '''8/3''',
'''Ngày thành lập Hội Liên hiệp Phụ nữ Việt Nam?''': '''20/10/1930''',
'''Ngày thành lập Quân đội Nhân dân Việt Nam là ngày nào?''': '''22/12''',
'''Ngày thành lập Đoàn Thanh niên Cộng sản Hồ Chí Minh là ngày nào?''': '''26/03''',
'''Ngôn ngữ lập trình nào được sử dụng để phát triển ứng dụng Android?''': '''Java và Kotlin''',
'''Người da trắng tắm biển đen thì họ sẽ bị gì?''': '''Bị ướt''',
'''Người ta thường cho quả gì vào nước luộc rau muống để thành món canh chua?''': '''Sấu''',
'''Người ta thường sản xuất gốm từ loại đất nào?''': '''Đất sét''',
'''Người ta thường ví: 'Thơm như múi ...' gì?''': '''Mít''',
'''Người ta tin rằng điều gì sẽ xảy ra vào đêm Halloween?''': ''' Ranh giới giữa thế giới sống và chết trở nên mờ nhạt''',
'''Nhà thơ nào được gọi là "Bà chúa thơ Nôm"?''': ''' Hồ Xuân Hương''',
'''Nhà vô địch Bundesliga mùa giải 2023-2024 là đội bóng nào?''': '''Bayer Leverkusen''',
'''Nhân vật Thúy Kiều trong truyện Kiều mang họ gì?''': '''Vương''',
'''“Truyện Kiều” được tác giả viết bằng loại chữ gì?''': '''Nôm''',
'''Những câu thơ "Bàn tay ta làm nên tất cả / Có sức người sỏi đá cũng thành cơm" là của nhà thơ nào?''': '''Hoàng Trung Thông''',
'''Những lý do người dùng nên sử dụng dịch vụ giải trí trực tuyến ở OKVIP?''': '''Tất cả các ý trên''',
'''Những địa danh thành cổ Diên Khánh, hòn Chồng, dốc Lết... ở tỉnh thành nào?''': '''Khánh Hòa''',
'''Năm nhuận có bao nhiêu ngày ?''': '''366''',
'''Năm thành lập Hội Liên hiệp Phụ nữ Việt Nam là năm nào?''': '''1930''',
'''Năm ông cùng ở một nhà. Tình huynh nghĩa đệ vào ra thuận hòa. Bốn ông tuổi đã lên ba. Một ông đã già mới lại lên hai. Là gì?''': '''Bàn tay''',
'''Nơi dòng sông Lam, ranh giới tự nhiên giữa hai tỉnh Nghệ An và Hà Tĩnh, chảy ra biển Đông có tên là gì?''': '''Cửa Hội''',
'''Nơi nào có đường xá, nhưng không có xe cộ; có nhà ở, nhưng không có người; có siêu thị, công ty... nhưng không có hàng hóa... Đó là nơi nào??!!''': '''Ở bản đồ''',
'''Nơi nào trên trái đất mà đàn ông ở đó khổ nhất?''': '''Nam cực''',
'''Nơi nào được coi là điểm sâu nhất của Trái đất dưới mực nước biển?''': '''Rãnh Mariana''',
'''Nước nào nổi tiếng với tháp đồng hồ Big Ben?''': '''Anh''',
'''Nắng ba năm ta chưa hề bỏ bạn, Mưa một ngày sao bạn nỡ xa ta - Là cái gì?''': '''Cái bóng''',
'''Nắng lửa mưa dầu tôi đâu bỏ bạn. Tối lửa tắt đèn sao bạn lại bỏ tôi. Đó là cái gì?''': '''Cái bóng''',
'''Nếu chỉ có một que diêm, trong một ngày mùa đông giá rét. Bước vào căn phòng có một cây đèn, một bếp dầu và một bếp củi, bạn thắp gì trước tiên?''': '''Que diêm''',
'''Nữ chính trị gia nào đã đại diên Việt Nam kí hiệp định Pari?''': '''Nguyễn Thị Bình''',
'''Nữ chính trị gia nào đã đại diện Việt Nam kí hiệp định Paris?''': '''Nguyễn Thị Bình''',
'''Nữ hoàng đế đầu tiên của Việt Nam là ai?''': '''Lý Chiêu Hoàng''',
'''Nữ sĩ quan tình báo giỏi nhất Việt Nam trong thời kỳ kháng chiến là ai?''': '''Đinh Thị Vân''',
'''Nữ thi sĩ nổi tiếng nào của Việt Nam được mệnh danh là "Bà chúa thơ Nôm"?''': ''' Hồ Xuân Hương''',
'''OKVIP LÀ GÌ?''': '''LÀ MỘT TRANG LIÊN MINH CÁC TRANG GAME CÁ CƯỢC HÀNG ĐẦU THỊ TRƯỜNG.''',
'''OKVIP phát thưởng cho hội viên tham gia các hoạt động tại Liên Minh OKVIP qua hình thức nào?''': '''Đáp Án A Và B''',
'''Phim 'Quyên' được chuyển thể từ tiểu thuyết cùng tên của nhà văn nào?''': '''Nguyễn Văn Thọ''',
'''Phong trào "Cách mạng Tháng Mười" diễn ra tại quốc gia nào?''': '''Nga''',
'''Phía trước bạn là quảng trường xanh, sau lưng bạn là quảng trường trắng, vậy quảng trường đỏ ở đâu?''': '''Ở Nga''',
'''Phạm Tiến Duật là ai?''': '''Một nhà thơ''',
'''Quê của Nguyễn Thị Minh Khai một nữ chính trị gia nổi tiếng của Việt Nam ở đâu ?''': '''Vinh - Nghệ An''',
'''Quả nào bao trùm cả năm châu?''': '''Quả đất''',
'''Quần đảo Cayman nằm ở vùng biển nào trên thế giới?''': '''Caribe''',
'''Quần đảo nào dưới đây nằm trên Ấn Độ Dương?''': '''Seychelles''',
'''Quốc gia nào có bức tượng “Merlion” nửa sư tử nửa cá nổi tiếng?''': '''Singapore''',
'''Quốc gia nào có diện tích lớn nhất thế giới''': '''Nga''',
'''Quốc gia nào có diện tích nhỏ nhưng lại có mật độ dân số cao nhất thế giới?''': ''' Monaco''',
'''Quốc gia nào có diện tích nhỏ nhất thế giới?''': '''Vatican''',
'''Quốc gia nào có dân số đông nhất thế giới?''': '''Ấn Độ''',
'''Quốc gia nào có tên viết tắt là UAE?''': '''Các Tiểu Vương Quốc Ả Rập Thống Nhất''',
'''Quốc gia nào nổi tiếng với hoa tulip và cối xay gió?''': '''Hà Lan''',
'''Quốc gia nào nổi tiếng với nền văn hóa Maori?''': ''' New Zealand''',
'''Quốc gia nào nổi tiếng với nền văn hóa Samurai và hoa anh đào?''': '''Nhật Bản''',
'''Quốc gia nào sau đây không giáp biển?''': '''Áo''',
'''Quốc gia nào đã đô hộ Việt Nam trong suốt 1000 năm Bắc thuộc?''': '''Trung Quốc''',
'''Quốc hiệu đầu tiên của Việt Nam là gì?''': '''Văn Lang''',
'''Rằm Trung thu nằm trong tháng Âm lịch nào?''': '''Tháng tám''',
'''Santiago là thủ đô của nước nào?''': '''Chile''',
'''Sau khi gửi phản hồi, sau bao nhiêu lâu sẽ được xét duyệt và tặng thưởng ?''': '''Mỗi ngày đều tiến hành xét duyệt và trao thưởng trong vòng 24h kể từ khi gửi phản hồi.''',
'''Serie A là giải đấu bóng đá của quốc gia nào?''': '''Ý''',
'''Siêu cúp bóng đá Ý có tên tiếng Anh là gì?''': '''Supercoppa Italiana''',
'''Steffi Graf - nữ vận động viên quần vợt vĩ đại nhất thế kỉ 20 - là người nước nào?''': '''Đức''',
'''Sân vận động Thiên Trường nằm ở tỉnh nào?''': '''Nam Định''',
'''Sân vận động nào được chọn tổ chức trận chung kết UEFA Champions League 2024-2025?''': '''Allianz Arena''',
'''Sân vận động quốc gia Mỹ Đình nằm ở đâu?''': '''Hà Nội''',
'''Sông Mekong không chảy qua nước nào sau đây?''': '''Ecuador''',
'''Sông Trà Khúc nằm ở tỉnh nào?''': '''Quảng Ngãi''',
'''Sông gì vốn dĩ ồn ào?''': '''Sông La''',
'''Số lượng tuần trong một năm là bao nhiêu?''': '''52''',
'''Sở thú bị cháy, con gì chạy ra đầu tiên?''': '''Con người''',
'''Sự kiện ký kết hợp đồng thương hiệu với CLB Villarreal đã diễn ra tại đâu?''': '''Camino Miralcamp''',
'''Theo một câu ca dân gian thì hoa gì "gần bùn mà chẳng hôi tanh mùi bùn"?''': '''Hoa sen''',
'''Theo quan điểm của một số nước phương Tây thì con số nào sau đây thường gắn với sự xui xẻo, không may mắn?''': '''13''',
'''Theo truyền dân gian thì Ngưu Lang và Chức Nữ thường gặp nhau ở đâu?''': '''Cầu Ô Thước''',
'''Theo truyền thống, Halloween là dịp để tưởng nhớ ai?''': ''' Những người đã khuất''',
'''Thiên nga đen chủ yếu sống ở nước nào dưới đây?''': '''Australia''',
'''Thành Vạn An do ai xây dựng?''': '''Mai Hắc Đế''',
'''Thành ngữ nào sau đây có nghĩa là chi tiêu tiết kiệm, dành dụm?''': '''Thắt lưng buộc bụng''',
'''Thành phần chính của không khí là gì?''': '''Nitơ''',
'''Thành phố nào có dân số đông nhất thế giới?''': '''Tokyo''',
'''Thành phố nào có tòa nhà chọc trời cao nhất thế giới hiện nay?''': '''Dubai (Burj Khalifa)''',
'''Thành phố nào dưới đây ở châu Âu?''': '''Berlin''',
'''Thành phố nào là thủ đô của Hoa Kỳ?''': '''Washington, D.C.''',
'''Thành phố nào là thủ đô của Ý?''': ''' Rome''',
'''Thành phố nào được mệnh danh là "Kinh đô ánh sáng"?''': '''Paris''',
'''Thành phố nào được mệnh danh là "Thành phố ngàn hoa"?''': '''Đà Lạt''',
'''Thành phố nào được mệnh danh là "Thủ đô ngàn năm văn hiến"?''': '''Hà Nội''',
'''Thành phố nào ở Nga là nơi tổ chức Thế vận hội mùa đông năm 2014?''': '''Sochi''',
'''Thác nào nằm trên biên giới giữa Mỹ và Canada?''': ''' Thác Niagara''',
'''Thác nước Iguazu nằm trên biên giới của hai quốc gia nào?''': '''Brazil và Argentina''',
'''Thư tịch cổ của người Khmer được viết trên giấy làm từ loại lá nào?''': '''Lá buông''',
'''Thương hiệu giày nào được biết đến với slogan "Just Do It"?''': '''Nike''',
'''Thạt Luổng là công trình kiến trúc tiêu biểu của quốc gia nào?''': '''Lào''',
'''Thảm gì mà không có bất kỳ ai muốn bước lên?''': '''Thảm họa''',
'''Thế vận hội mùa hè 2016 được tổ chức tại đâu?''': '''Brazil''',
'''Thời kỳ nào được gọi là "Thời kỳ Bắc thuộc" trong lịch sử Việt Nam?''': '''Khi Việt Nam bị Trung Quốc đô hộ''',
'''Thủ đô của Ba Lan là thành phố nào?''': '''Warszawa''',
'''Thủ đô của nước nào nằm trên hai châu lục?''': '''Thổ Nhĩ Kỳ''',
'''Thứ gì mỗi ngày phải gỡ ra mới có công dụng?''': ''' Lịch treo tường''',
'''Triều đại nào đã đánh bại quân Nguyên Mông ba lần?''': ''' Nhà Trần''',
'''Trong 1 cuộc thi chạy, nếu bạn vượt qua người thứ 2 bạn sẽ đứng thứ mấy?''': '''Thứ hai''',
'''Trong Game Show GHÉP CHỮ OKVIP. Mỗi ngày hội viên có thể giúp lượt rút chữ cho cùng 1 người bạn bao nhiêu lần?''': '''1 LẦN''',
'''Trong Game show CHIA SẺ CÓ QUÀ. Khi chia sẻ công khai lên 5 hội nhóm Facebook, yêu cầu mỗi nhóm có bao nhiêu thành viên ?''': '''TRÊN 5000 THÀNH VIÊN''',
'''Trong Game show CHIA SẺ CÓ QUÀ. Khi chia sẻ lên 10 nhóm Tele công khai, yêu cầu mỗi nhóm có bao nhiêu thành viên ?''': '''TRÊN 5000 THÀNH VIÊN''',
'''Trong Game show CHIA SẺ CÓ QUÀ. Khi chia sẻ lên Facebook, yêu cầu Facebook cá nhân của hội viên cần có bao nhiêu bạn bè ?''': '''TRÊN 300 BẠN BÈ''',
'''Trong Game show CHIA SẺ CÓ QUÀ. Khi chia sẻ trên Tiktok, yêu cầu tài khoản Tiktok hội viên có bao nhiêu Fan ?''': '''TRÊN  100 FAN''',
'''Trong Game show MỜI BẠN BÈ. Mỗi ngày được mời tối đa bao nhiêu người bạn tham gia đăng ký?''': '''KHÔNG GIỚI HẠN, MỜI CÀNG NHIỀU BẠN BÈ, NHẬN CÀNG NHIỀU LƯỢT MỞ QUÀ VẠN MAY''',
'''Trong Game show TRẢ LỜI CÂU HỎI CÓ THƯỞNG. Mỗi lần cần trả lời đúng bao nhiêu câu để có thể nhận lượt MỞ QUÀ VẠN MAY?''': '''4/5 CÂU''',
'''Trong Game show TRẢ LỜI CÂU HỎI CÓ THƯỞNG. Mỗi lần trả lời đúng sẽ nhận được bao nhiêu lượt MỞ QUÀ VẠN MAY?''': '''1 LƯỢT''',
'''Trong Game show TRẢ LỜI CÂU HỎI CÓ THƯỞNG. Mỗi ngày đăng nhập sẽ nhận được bao nhiêu lần trả lời câu hỏi ?''': '''5''',
'''Trong Game show ĐIỂM DANH CÓ QUÀ. Cần liên kết tối thiểu bao nhiêu tài khoản thành viên liên minh thì mới được tham gia điểm danh ?''': '''LIÊN KẾT ÍT NHẤT 1 TÀI KHOẢN THÀNH VIÊN LIÊN MINH''',
'''Trong Game show ĐIỂM DANH CÓ QUÀ. Cần điểm danh đạt điều kiện gì để nhận được 10 lượt MỞ QUÀ VẠN MAY?''': '''ĐIỂM DANH LIÊN TIẾP ĐỦ 7 NGÀY''',
'''Trong Halloween, người ta thường chạm khắc gì lên quả bí ngô?''': '''Khuôn mặt đáng sợ''',
'''Trong Hoạt động ĐĂNG NHẬP LẦN ĐẦU CÓ QUÀ. Hội viên cần thực hiện các bước nào để có thể nhận phần quà chào mừng ?''': '''ĐĂNG KÝ TÀI KHOẢN, SAU ĐÓ TẢI APP OKVIP VÀ ĐĂNG NHẬP TÀI KHOẢN VÀO ỨNG DỤNG MỚI TẢI VỀ''',
'''Trong Hoạt động ĐĂNG NHẬP LẦN ĐẦU CÓ QUÀ. Hội viên sẽ được nhận được phần quà chào mừng là gì ?''': '''NHẬN 9 ĐIỂM THƯỞNG''',
'''Trong chiến dịch Điện Biên Phủ, người anh hùng nào đã lấy thân mình để cứu pháo?''': '''Tô Vĩnh Diện''',
'''Trong các nước sau đây, nước nào chưa từng là thành viên Khối Thịnh vượng chung Anh?''': '''Angola''',
'''Trong game show CHIA SẺ CÓ QUÀ, mỗi lần chia sẻ hợp lệ sẽ nhận được bao nhiêu lượt MỞ QUÀ VẠN MAY?''': '''5''',
'''Trong game show GHÉP CHỮ OKVIP. Có cho phép tặng chữ cái trong bộ sưu tập của mình cho bạn bè không?''': '''CHO PHÉP, TẶNG CHỮ KHÔNG GIỚI HẠN''',
'''Trong game show GHÉP CHỮ OKVIP. Hội viên mới đăng ký nhận được bao nhiêu lần rút chữ ?''': '''10 LẦN''',
'''Trong game show GHÉP CHỮ OKVIP. Mỗi lần bạn bè trợ giúp sẽ được bao nhiêu lần rút chữ ?''': '''2 LẦN''',
'''Trong game show GHÉP CHỮ OKVIP. Mỗi lần rút chữ sẽ nhận được bao nhiêu chữ cái ?''': '''NHẬN ĐƯỢC 1 CHỮ CÁI NGẪU NHIÊN''',
'''Trong game show GHÉP CHỮ OKVIP. Mỗi ngày hội viên có thể tặng số lần rút chữ cho tối đa bao nhiêu người bạn ? Tặng mỗi người tối đa bao nhiêu lượt rút chữ ?''': '''Tối đa 2 người bạn, mỗi người 1 lượt rút chữ''',
'''Trong game show GHÉP CHỮ OKVIP. Mỗi ngày, hội viên có thể giúp lượt rút chữ cho tối đa bao nhiêu người bạn ?''': '''2 NGƯỜI''',
'''Trong thế kỷ 21, đội bóng nào có số lần vô địch UEFA Champions League liên tiếp nhiều nhất hiện nay?''': '''Real Madrid''',
'''Trong tiếng Việt, từ nào có nghĩa là "mưa"?''': '''Mưa''',
'''Trong truyện "Aladdin và cây đèn thần", Aladdin tìm thấy đèn thần ở đâu?''': '''Trong căng hầm bí mật''',
'''Trong truyện "Cô bé Lọ Lem", đôi giày của Lọ Lem được làm từ gì?''': '''Thủy tinh''',
'''Trong truyện "Hoàng tử Ếch", điều gì xảy ra khi công chúa hôn con ếch?''': '''Con ếch biến thành hoàng tử''',
'''Trong truyện "Vua Midas", ông đã biến mọi thứ chạm vào thành gì?''': '''Vàng''',
'''Truyện Lục Vân Tiên là tác phẩm của ai?''': '''Nguyễn Đình Chiểu''',
'''Truyện ngắn 'Cái tết của những nhà đại văn hào' được Nguyễn Công Hoan viết vào giai đoạn nào?''': '''Trước Cách mạng Tháng Tám''',
'''Trên hang đá, dưới hang đá, giữa là con cá thờn bơn. Là cái gì?''': '''Cái miệng''',
'''Trên lá cờ của Thế vận hội - Olympic có bao nhiêu vòng tròn?''': '''5''',
'''Trò gì càng chơi càng ra nước?''': '''Chơi cờ''',
'''Trường đại học Harvard nằm ở bang nào của nước Mỹ?''': '''Massachusetts''',
'''Trận chung kết Giải Vô địch Bóng đá Đông Nam Á năm 2024 có sự góp mặt của đội bóng quốc gia nào?''': ''' Thái Lan''',
'''Trận chung kết UEFA Champions League 2019-2020 được tổ chức tại thành phố nào?''': '''Lisbon''',
'''Trận chung kết UEFA Champions League 2020-2021 được tổ chức tại thành phố nào?''': '''Porto''',
'''Trẻ em thường làm gì trong lễ Halloween?''': '''Đi xin kẹo ("Trick-or-Treat")''',
'''Tàu Titanic đã chìm vào năm nào?''': '''1912''',
'''Tác giả của "Harry Potter" là ai?''': ''' J.K. Rowling''',
'''Tác giả của "Số đỏ" là ai?''': ''' Vũ Trọng Phụng''',
'''Tác giả của bài thơ "Nam quốc sơn hà", được coi là bản "Tuyên ngôn độc lập" đầu tiên của Việt Nam, là ai?''': '''Lý Thường Kiệt''',
'''Tác giả của vở kịch nổi tiếng Romeo và Juliet là người của đất nước nào?''': '''Anh''',
'''Tác phẩm "Chí Phèo" do ai sáng tác?''': '''Nam Cao''',
'''Tác phẩm "Vợ nhặt" do ai viết?''': '''Kim Lân''',
'''Tên thật đầy đủ của Người anh hùng nhỏ tuổi Kim Đồng là gì?''': '''Nông Văn Dền''',
'''Tên tuổi ca sĩ Khánh Ly gắn liền với những ca khúc của nhạc sĩ nào?''': '''Trịnh Công Sơn''',
'''Tính đến năm 2022, huấn luyện viên nào đã dẫn dắt Manchester United giành nhiều chức vô địch Premier League nhất?''': '''Alex Ferguson''',
'''Tính đến năm 2024, câu lạc bộ nào giành nhiều chức vô địch Ligue 1 nhất?''': '''Paris Saint-Germain''',
'''Tôi có 4 cái chân, 1 cái lưng, nhưng không có cơ thể. Tôi là ai?''': '''CÁI GHẾ''',
'''Tôi có cả một hàm răng nhưng không có cái miệng nào cả? Tôi là ai?''': '''Cái cưa''',
'''Tượng Nhân sư là tượng nổi tiếng của quốc gia nào trên thế giới?''': '''Ai Cập''',
'''Tượng đài Mẹ Việt Nam Anh hùng nằm ở tỉnh nào?''': '''Quảng Nam''',
'''Tại Chuyên mục Phản hồi nhận thưởng, hội viên có thể gửi phản hồi về nội dung nào ?''': '''Bất kể nội dung gì liên quan tới OKVIP đều có thể gửi phản hồi. Liên Minh OKVIP luôn cởi mở tiếp nhận.''',
'''Tại Chuyên mục Phản hồi nhận thưởng, hội viên có thể nhận được phần quà gì ?''': '''Phản hồi được Liên Minh OKVIP áp dụng sẽ được tặng thưởng tùy theo giá trị đóng góp, có thể lên tới 9.999 điểm.''',
'''Tại Mỹ, Halloween được tổ chức lần đầu tiên vào thế kỷ nào?''': ''' Thế kỷ 19''',
'''Tại kỳ SEA Games nào, đội tuyển bóng đá nam Việt Nam giành huy chương vàng đầu tiên?''': '''SEA Games 2019''',
'''Tại sao người ta lại đeo mặt nạ vào lễ Halloween?''': ''' Để xua đuổi linh hồn xấu''',
'''Tại sao sư tử ăn thịt sống?''': '''Ứ ! Biết nấu''',
'''Tỉnh Vĩnh Phúc nổi tiếng với địa điểm du lịch nào?''': '''Tam Đảo''',
'''Tỉnh nào có di tích lịch sử của trận đánh lịch sử chống quân Mông Nguyên vào năm 1288?''': '''Quảng Ninh''',
'''Tỉnh nào là tỉnh có diện tích lớn nhất Việt Nam?''': '''Nghệ An''',
'''Tỉnh nào nổi tiếng với lễ hội đua bò Bảy Núi?''': '''An Giang''',
'''Tổ chức chính trị, xã hội quan trọng nhất của phụ nữ ở Việt Nam là gì?''': '''Hội Liên hiệp Phụ nữ Việt Nam.''',
'''Tổ chức nào điều hành các kỳ Olympic?''': '''IOC''',
'''Tổng bộ Liên Minh OKVIP có trụ sở ở đâu?''': '''Luân Đôn, Anh''',
'''Từ nào còn thiếu trong câu sau: 'Anh đi anh nhớ quê nhà. Nhớ canh ..., nhớ cà dầm tương'?''': '''Rau muống''',
'''Từ nào còn thiếu trong câu sau: 'Ráng ... có nhà thì giữ'?''': '''Mỡ gà''',
'''Từ nào còn thiếu trong câu sau: 'Đỏ như con ... luộc'?''': '''Tôm''',
'''Từ nào không sử dụng trong toán học?''': '''Tướng số''',
'''Từ nào sau đây viết đúng chính tả ?''': '''Trống trải''',
'''Từ nào, khi bỏ chữ cái đầu thì trở thành tên một quốc gia, còn khi bỏ chữ cái cuối thì trở thành tên một loài chim?''': '''Cúc''',
'''Viết tắt của Liên đoàn bóng đá Châu Á là gì?''': '''AFC''',
'''Việt Nam có đường bờ biển dài bao nhiêu km?''': '''3,260 km''',
'''Việt Nam gia nhập Liên Hợp Quốc vào năm nào?''': '''1977''',
'''Việt Nam nằm ở bán đảo nào?''': '''Đông Dương''',
'''Việt Nam thuộc khu vực địa lý của Châu Á nào?''': '''Đông Nam Á''',
'''Vua nào 7 tuổi lên ngôi, Việc dân việc nước trọn đời lo toan, Mở trường thi chọn quan văn, Lập Quốc Tử Giám luyện hàng danh nhân - Là vua gì?''': '''Lý Nhân Tông''',
'''Vua nào thuở bé chăn trâu. Trường Yên một ngọn cờ lau tập tành. Sứ quân dẹp loạn phân tranh. Dựng nền thống nhất sử xanh còn truyền?''': '''Đinh Bộ Lĩnh (Đinh Tiên Hoàng)''',
'''Vua nào thảo Chiếu dời đô?''': '''Lý Thái Tổ''',
'''Vào tháng nào con người sẽ ngủ ít nhất trong năm?''': '''Tháng 2''',
'''Vì tao tao phải đánh tao, vì tao tao phải đánh mày. Hỏi đang làm gì?''': '''Đập muỗi''',
'''Vùng đất Cà Mau còn được gọi là gì?''': '''Đất Mũi''',
'''Văn Miếu Quốc Tử Giám được coi là trường đại học đầu tiên của Việt Nam được xây dựng dưới triều đại nào?''': '''Nhà Lý''',
'''Vạn Lý Trường Thành nằm ở quốc gia nào?''': '''Trung Quốc''',
'''Vận động viên nào của Việt Nam đã không giành huy chương vàng môn bơi lội tại SEA Games 2019?''': '''Hoàng Quý Phước''',
'''Vận động viên nữ nào của Việt Nam đã giành huy chương vàng môn bơi lội tại SEA Games 2019?''': '''Nguyễn Thị Ánh Viên''',
'''Vị anh hùng nào đã lấy thân mình làm giá súng trong Chiến dịch Điện Biên Phủ 1954?''': '''Bế Văn Đàn''',
'''Vị vua nào của triều Lý trong thửa hàn vi ở chùa?''': '''Lý Thái Tổ''',
'''Vị vua nào sáng lập nhà Lý và dời đô về Thăng Long?''': '''Lý Thái Tổ''',
'''Vị vua nào đã làm hai câu thơ: “Xã tắc hai phen chồn ngựa đá. Non sông ngàn thủa vững âu vàng”?''': '''Trần Nhân Tông''',
'''Vị vua nào đã xây dựng Vạn Lý Trường Thành?''': '''Tần Thủy Hoàng''',
'''Vừa bằng một thước mà bước không qua. Là cái gì?''': '''Cái bóng''',
'''Vực Phun là thắng cảnh nằm ở tỉnh thành nào?''': '''Phú Yên''',
'''Xe nào không bao giờ giảm đi?''': '''Xe tăng''',
'''Xi rô có vị gì chủ đạo?''': '''Ngọt''',
'''Điền vào câu tục ngữ sau: "Khôn ăn cái, dại ăn ..."?''': '''Nước''',
'''Đâu không phải là một loại tế bào trên cơ thể con người?''': '''Tính cầu''',
'''Đâu không phải là một từ láy?''': '''Bẻ gãy''',
'''Đâu không phải là tên gọi một loại nhạc cụ dân gian Việt Nam?''': '''Đàn Ngũ''',
'''Đâu không phải là tên một môn võ thuật?''': '''Pokemon''',
'''Đâu là loài chim lớn nhất trên thế giới hiện nay?''': '''Đà điểu''',
'''Đâu là loài động vật con đực có thể mang thai?''': '''Cá ngựa''',
'''Đâu là một địa danh nổi tiếng ở Hà Nội?''': '''Gò Đống Đa''',
'''Đâu là thủ đô của Ấn Độ ?''': '''New Delhi''',
'''Đâu là tên của Cúp Nhà vua Tây Ban Nha?''': '''Copa del Rey''',
'''Đâu là tên gọi của một thương hiệu diêm lâu đời ở nước ta?''': '''Thống Nhất''',
'''Đâu là tên một cung hoàng đạo?''': '''Bọ cạp''',
'''Đâu là động vật có vú duy nhất biết bay?''': ''' Dơi''',
'''Đây là cầu thủ nổi tiếng nào?''': '''Cristiano Ronaldo''',
'''Đây là quốc kỳ của nước nào?''': '''Việt Nam''',
'''Đơn vị đo cường độ dòng điện là gì?''': '''Ampere''',
'''Đơn vị đo áp suất trong hệ SI là gì?''': '''Pascal''',
'''Đại dương lớn nhất thế giới là gì?''': ''' Thái Bình Dương''',
'''Đại dương nào lớn nhất trên thế giới?''': '''Thái Bình Dương''',
'''Đảo lớn nhất Việt Nam là đảo nào?''': '''Phú Quốc''',
'''Đảo quốc nào ở Ấn Độ Dương nổi tiếng với bãi biển trắng và nước biển trong xanh?''': ''' Maldives''',
'''Đất nước nào có môn thể thao quốc gia là đấu bò?''': ''' Tây Ban Nha''',
'''Đất nước nào có núi Phú Sĩ, biểu tượng văn hóa nổi tiếng?''': ''' Nhật Bản''',
'''Đất nước nào là quê hương của điệu nhảy Tango?''': '''Argentina''',
'''Đất nước nào được gọi là "xứ sở Mặt trời mọc"?''': ''' Nhật Bản''',
'''Đến năm 2022, cầu thủ nào đã ghi bàn thắng nhanh nhất trong lịch sử Serie A?''': '''Rafael Leão''',
'''Đền Thờ Mặt Trời Konark ở nước nào?''': '''Ấn Độ''',
'''Để trở thành thành viên của Liên Minh OKVIP, các trang giải trí trực tuyến cần đạt yêu cầu gì?''': '''Tất cả các ý trên''',
'''Để được màu da cam ta phải trộn 2 màu nào với nhau?''': '''Vàng và đỏ''',
'''Đỉnh Everest thuộc dãy núi nào?''': '''Himalaya''',
'''Đố mẹo : Một đàn chuột Điếc đi ngang qua, hỏi có mấy con?''': '''24''',
'''Đố vui : Cái gì khiến bạn già đi 1 năm chỉ trong một ngày?''': '''Sinh nhật''',
'''Đố vui : Thứ gì càng thêm thì giá trị càng mất?''': '''Lỗi''',
'''Đố vui : Cái gì bạn có thể bẻ gãy mà không cần chạm vào nó hoặc thấy nó?''': '''Lời hứa''',
'''Đố vui : Cái gì càng chia sẻ càng nhân lên?''': '''Kiến thức''',
'''Đố vui : Cái gì càng giữ càng phải buông?''': '''Hơi thở''',
'''Đố vui : Cái gì càng lấy lại càng mất nhiều?''': '''Thời gian''',
'''Đố vui : Cái gì càng nhìn kỹ, bạn càng không thấy?''': ''' Tương lai''',
'''Đố vui : Cái gì càng nóng càng co lại?''': '''Cao su''',
'''Đố vui : Cái gì càng sử dụng, càng tăng giá trị của nó?''': '''Kinh nghiệm''',
'''Đố vui : Cái gì không bao giờ đi lên nhưng luôn hướng xuống?''': '''Đồng hồ cát''',
'''Đố vui : Cái gì không bao giờ đi lùi, chỉ đi tới?''': '''Đồng hồ''',
'''Đố vui : Thứ gì bạn càng chia sẻ, nó càng mất đi?''': ''' Bí mật''',
'''Đố vui : Thứ gì bạn có thể nâng lên nhưng không thể chạm vào?''': '''Âm thanh''',
'''Đố vui : Thứ gì bạn có thể đập vỡ bằng một câu nói?''': '''Mối quan hệ''',
'''Đố vui : Thứ gì bạn luôn mang theo khi đi ra ngoài, nhưng luôn bị bỏ lại phía sau?''': '''Dấu chân''',
'''Đố vui : Thứ gì bạn phải giữ lấy, ngay cả khi đã cho đi?''': '''Lời hứa''',
'''Đố vui : Thứ gì càng to, bạn càng không thấy?''': '''Bóng tối''',
'''Đố vui : Thứ gì càng để lâu càng tốt?''': '''Rượu''',
'''Đố vui : Thứ gì có thể đi xuyên qua thủy tinh mà không làm vỡ nó?''': '''Ánh sáng''',
'''Đố vui : Thứ gì không mời mà tự đến, không đuổi mà tự đi?''': '''Cơn gió''',
'''Đố vui : Thứ gì luôn đi về phía sau nhưng không bao giờ đi về phía trước?''': '''Lịch sử''',
'''Đố vui : Thứ gì luôn ở giữa Paris?''': '''Chữ R''',
'''Đố vui : Bao nhiêu người muốn giữ nhưng cuối cùng đều mất đi ?''': '''Thanh xuân''',
'''Đố vui : Bạn làm việc gì đầu tiên mỗi sáng?''': '''MỞ MẮT''',
'''Đố vui : Con gì càng to càng nhỏ?''': '''CON CUA''',
'''Đố vui : Con gì mang được miếng gỗ lớn nhưng ko mang được hòn sỏi?''': '''CON SÔNG''',
'''Đố vui : Con gì đập thì sống, không đập thì chết?''': '''CON TIM''',
'''Đố vui : Con mèo nào cực kỳ sợ chuột?''': '''MÈO DOREMON''',
'''Đố vui : Con trai có gì quý nhất?''': '''NGỌC TRAI''',
'''Đố vui : Con đường dài nhất là đường nào?''': '''ĐƯỜNG ĐỜI''',
'''Đố vui : Cái gì bạn không thể ăn vào buổi sáng?''': '''Bữa tối''',
'''Đố vui : Cái gì luôn đi đến nhưng không bao giờ đến nơi?''': '''Ngày mai''',
'''Đố vui : Cái gì mà đi thì nằm, đứng cũng nằm, nhưng nằm lại đứng?''': '''BÀN CHÂN''',
'''Đố vui : Cái gì đen khi bạn mua nó, đỏ khi dùng nó và xám xịt khi vứt nó đi?''': '''THAN''',
'''Đố vui : Có 1 con gà trống đứng trên nóc nhà gáy hỏi nó đẻ được mấy trứng ?''': '''0 TRỨNG''',
'''Đố vui : Có con chuột lại cực kỳ sợ mèo. Con chuột nào vậy?''': '''CHUỘT NÀO CŨNG SỢ MÈO''',
'''Đố vui : Có cổ nhưng không có miệng là gì?''': '''CÁI ÁO''',
'''Đố vui : Có mặt ở khắp mọi nơi nhưng không thể nhìn thấy, khi không có nó bạn chết. Đó là cái gì?''': '''Không khí''',
'''Đố vui : Dài như quả chuối, cầm được một lát liền chảy nước là cái gì?''': '''CÂY KEM''',
'''Đố vui : Khi Ronaldo đá phạt đền sẽ sút vào vị trí nào?''': '''SÚT VÀO QUẢ BÓNG''',
'''Đố vui : Lịch nào dài nhất?''': '''LỊCH SỬ''',
'''Đố vui : Môn gì càng thắng càng thua?''': '''ĐUA XE ĐẠP''',
'''Đố vui : Núi nào mà bị chặt ra từng khúc?''': '''NÚI THÁI SƠN''',
'''Đố vui : Tay phải cầm được, nhưng tay trái không cầm được, là cái gì?''': '''TAY TRÁI''',
'''Đố vui : Trên lông dưới lông, tối lồng là một là cái gì?''': '''CON MẮT''',
'''Đố vui : Tôi có 4 cái chân, 1 cái lưng, nhưng không có cơ thể. Tôi là ai?''': '''CÁI GHẾ''',
'''Đố vui : Từ gì mà 100% nguời dân Việt Nam đều phát âm sai?''': '''TỪ SAI''',
'''Đố vui : Vừa bằng hạt đỗ, ăn giỗ cả làng. Là con gì?''': '''CON RUỒI''',
'''Đố vui : Đố bạn chuột nào đi bằng 2 chân?''': '''CHUỘT MICKEY''',
'''Đố vui :Con gì kêu "cạp cạp"?''': '''Con vịt''',
'''Đố vui :Cái gì bốn chân mà đi không được?''': '''Tất cả các đáp án trên''',
'''Đố vui :Cái gì dùng để ăn nhưng ăn mãi không hết?''': '''Cái bát''',
'''Đố vui :Loại củ/quả nào bỏ ngoài cười, bỏ trong khóc?''': '''Quả hành''',
'''Đố vui :Mặt trời mọc hướng nào?''': '''Đông''',
'''Đố vui: Cơ quan quan trọng nhất của phụ nữ là gì ?''': '''HỘI LIÊN HIỆP PHỤ NỮ''',
'''Đối tác thương hiệu AFA là Hiệp hội bóng đá quốc gia nào?''': '''Argentina''',
'''Đối tác thương hiệu AFA đã vô địch Copa America bao nhiêu lần?''': '''16''',
'''Đối tác thương hiệu AFA đã vô địch Wold Cup bao nhiêu lần?''': '''3''',
'''Đối tác thương hiệu Villareal CF có biệt danh là gì?''': '''Tàu Ngầm Vàng''',
'''Đối tác thương hiệu Villareal CF là câu lạc bộ thuộc quốc gia nào?''': '''Tây ban nha''',
'''Đối tác thương hiệu Villareal CF đã giành chức vô địch UEFA Europa League vào năm nào?''': '''2021''',
'''Đội bóng Lyon đã giành bao nhiêu chức vô địch Ligue 1 liên tiếp từ năm 2002 đến 2008?''': '''7 lần''',
'''Đội bóng nào là nhà vô địch UEFA Champions League mùa giải 2023-2024?''': '''Real Madrid''',
'''Đội bóng nào vô địch Ligue 1 mùa giải 2021-2022?''': '''Paris Saint-Germain''',
'''Đội bóng nào đã vô địch Bundesliga mùa giải 2022-2023?''': '''Bayern Munich''',
'''Đội bóng nào đã đánh bại Barcelona với tỷ số 8-2 trong một trận đấu loại trực tiếp UEFA Champions League?''': '''Bayern Munich''',
'''Đội bóng nào được biết đến với biệt danh “Les Olympiens”?''': '''Marseille''',
'''Đội ngũ CSKH của Liên Minh OKVIP làm việc trong khung giờ nào?''': '''Làm việc 24/7''',
'''Động Phong Nha - Kẻ Bàng nằm ở tỉnh nào?''': '''Quảng Bình''',
'''Động vật nào là loài có vú mà lại đẻ trứng?''': '''Thú mỏ vịt''',
'''Ở Việt Nam, rồng bay ở đâu?''': '''Thăng long''',
'''Ở Việt Nam, rồng đáp ở đâu?''': '''Hạ long''',
'''Ở đâu có 30 người đàn ông và 02 người phụ nữ chiến đấu với nhau?''': '''Ở trên bàn cờ vua''',
'''Ở đâu có tượng Nữ thần Tự Do?''': ''' New York''',
'''“Chiếu dời đô” là của ai?''': '''Lý Thái Tổ''',
'''“Người ta tạo ra vận mệnh chứ không phải vận mệnh tạo ra con người” là câu nói nổi tiếng của ai?''': '''Lê Quý Đôn''',
'''Con gì vừa bằng hạt đỗ, ăn giỗ cả làng? ''': '''Con ruồi''',
'''8 chữ vàng mà Bác Hồ dành tặng cho phụ nữ Việt Nam là gì?''': '''Anh hùng - Bất khuất - Trung hậu - Đảm đang.''',
'''Đèo Hải Vân nằm giữa hai tỉnh nào?''': '''Thừa Thiên Huế và Đà Nẵng''',
'''Hạt đường và hạt cát, hạt nào dài hơn?''': '''Hạt đường''',
'''Có 1 bà kia không biết bơi, xuống nước là bà chết. Một hôm bà đi tàu, bỗng nhiên tàu chìm, nhưng bà không chết.Tại sao (không ai cứu hết)?''': '''Bà đi tàu ngầm''',
'''Chú gấu trúc – nhân vật chính trong phim Kungfu Panda có tên là gì?''': '''Po''',
'''Câu đố kiến thức :Vịnh Hạ Long thuộc tỉnh nào của Việt Nam?''': '''Quảng Ninh''',
'''Lăm Vông là điệu múa nổi tiếng của đất nước nào?''': '''Lào''',
'''Bên trái đường có một căn nhà xanh, bên phải đường có một căn nhà đỏ. Vậy, nhà Trắng ở đâu ?''': '''Ở Mỹ''',
'''Neymar là cầu thủ bóng đá nổi tiếng người nước nào?''': '''Brazil''',
'''Vào mùa đông lá của cây bàng thường có màu gì?''': '''Đỏ''',
'''Trái với nghĩa chậm chạp là gì ?''': '''Nhanh nhẹn''',
'''Đâu không phải tên một loài cây?''': '''Cà lăm''',
'''Nghệ sĩ nào của Việt Nam nhận giải Nghệ sĩ châu Á xuất sắc nhất của Mnet Asian Music Awards 2015 (MAMA)?''': '''Đông Nhi''',
'''Bác Hồ viết "Lời kêu gọi toàn quốc kháng chiến" tại đâu?''': '''Làng Vạn Phúc''',
'''Ở Việt Nam hiện đang lưu hành bao nhiêu mệnh giá tiền polymer có giá trị thanh toán?''': '''6''',
'''Người đẹp nào đại diện cho Việt Nam tham gia Hoa hậu Hoàn vũ Thế giới 2015?''': '''Phạm Hương''',
'''Có câu: "Ăn cây táo rào cây ..." gì?''': '''Sung''',
'''Có câu: "Tam sao ..." gì?''': '''Thất lạc''',
'''Ngày 5/5 Âm lịch hàng năm là ngày gì?''': '''Tết Đoan Ngọ''',
'''Theo dương lịch, sau bao nhiêu năm lại có một năm nhuận?''': '''4''',
'''Ngạc ngư là tên gọi khác của con vật nào?''': '''Cá sấu''',
'''Nhạc sĩ nào sáng tác bài hát "Tiếng chày trên sóc Bom Bo"?''': '''Xuân Hồng''',
'''Trong các từ sau, từ nào không phải là từ láy?''': '''Bắn bia''',
'''Matcha là tên của một loại trà nổi tiếng của nước nào?''': '''Nhật Bản''',
'''Dụng cụ đo lượng mưa có tên gọi là gì ?''': '''Vũ kế''',
'''Số 3 được viết thế nào trong hệ nhị phân?''': '''11''',
'''Có câu mất bò mới lo.... gì ?''': '''Làm chuồng''',
'''Soju là loại rượu đặc trưng của quốc gia nào?''': '''Hàn Quốc''',
'''Đâu là tên gọi của một con đường buôn bán cổ xưa nổi tiếng?''': '''Con đường tơ lụa''',
'''Trái với nghĩa chậm chạp là gì ?''': '''Nhanh Nhẹn''',
'''Địa danh Machu Picchu thuộc quốc gia nào?''': '''Peru''',
'''Đâu là tên gọi một loại xương trên cơ thể người ?''': '''Bánh Chè''',
'''Người ta gọi những chỗ mặt đường hỏng lõm sâu xuống là gì?''': '''Ổ Gà''',
'''Có 2 người bạn 1 mù, 1 câm đi shopping. Câm mua cái nón thì lấy tay chỉ lên đầu và gõ gõ mấy cái còn Mù muốn mua kem đánh răng thì làm sao?''': '''Nói: Tôi muốn mua kem đánh răng''',
'''Lục địa nào là quê hương của những câu chuyện ngụ ngôn Timbuktu?''': '''Châu Phi''',
'''Cối xay gió là phát minh của nước nào ?''': '''Iran''',
'''Vào mùa đông lá của cây bàng thường có màu gì?''': '''Đỏ''',
'''Wimbledon là giải đấu thường niên của bộ môn nào?''': '''Quần vợt''',
'''Nghệ sĩ nào của Việt Nam nhận giải Nghệ sĩ châu Á xuất sắc nhất của Mnet Asian Music Awards 2015 (MAMA)?''': '''Đông Nhi''',
'''Đội tuyển nào đã thua Bồ Đào Nha trong trận chung kết Euro 2016?''': '''Pháp''',
'''Nước mắm Nam Ô là đặc sản nổi tiếng của vùng đất nào?''': '''Đà Nẵng''',
'''Bộ phận nào sau đây của cơ thể tiêu thụ oxi nhiều nhất?''': '''Não''',
'''Cướp biển còn được gọi với tên khác là gì?''': '''Hải Tặc''',
'''Đâu là một giải thưởng thuộc lĩnh vực điện ảnh?''': '''Mâm xôi vàng''',
'''Có câu: "Cố đấm ăn ..." gì?''': '''Xôi''',
'''Cối xay gió là phát minh của nước nào ?''': '''Iran''',
'''Thành phố hoa phượng đỏ là cách gọi khác về thành phố nào sau đây?''': '''Hải Phòng''',
'''Đâu là một giải thưởng thuộc lĩnh vực điện ảnh?''': '''Mâm xôi vàng''',
'''Lục địa nào là quê hương của những câu chuyện ngụ ngôn Timbuktu?''': '''Châu Phi''',
'''Từ nào sau đây chỉ đứa trẻ thông minh, có năng khiếu đặc biệt?''': '''Thần Đồng''',
'''Trong các từ sau, từ nào không phải là từ láy?''': '''Bắn bia''',
'''Cướp biển còn được gọi với tên khác là gì?''': '''Hải Tặc''',
'''"Quỷ đỏ" là biệt danh của câu lạc bộ bóng đá nào?''': '''Manchester United''',
'''Đội tuyển nào đã thua Bồ Đào Nha trong trận chung kết Euro 2016?''': '''Pháp''',
'''Từ nào sau đây viết đúng chính tả?''': '''Trả giá''',
'''Trong 1 hình chữ nhật có bao nhiêu góc vuông ?''': '''4''',
'''Có câu: "Tam sao ..." gì?''': '''Thất Bản''',
'''Brazil thuộc châu lục nào?''': '''Châu Mỹ''',
'''"Pháo thủ" là biệt danh của câu lạc bộ bóng đá nào?''': '''Arsenal''',
'''Matcha là tên của một loại trà nổi tiếng của nước nào?''': '''Nhật Bản''',
'''Thành phố nào sau đây ở châu Âu?''': '''Berlin''',
'''Ngày nào là ngày Quốc tế Lao động?''': '''1 tháng 5''',
'''"Lữ đoàn đỏ" là biệt danh của câu lạc bộ bóng đá nào?''': '''Liverpool''',
'''Từ nào sau đây viết đúng chính tả?''': '''Trả giá''',
'''Người đẹp nào đại diện cho Việt Nam tham gia Hoa hậu Hoàn vũ Thế giới 2015?''': '''Phạm Hương''',
'''Tỉnh nào sau đây ở miền Bắc nước ta?''': '''Thái Nguyên''',
'''"Kền kền trắng" là biệt danh của câu lạc bộ bóng đá nào?''': '''Real Madrid''',
'''Đâu là một khái niệm được sử dụng trong toán học?''': '''Quỹ Tích''',
'''Số 3 được viết thế nào trong hệ nhị phân?''': '''11''',
'''Oscar là giải thưởng danh giá trong lĩnh vực nào?''': '''Điện ảnh''',
'''"The Blues" là biệt danh của câu lạc bộ bóng đá nào?''': '''Chelsea''',
'''Cà phê Espresso có nguồn gốc từ nước nào ?''': '''Ý''',
'''Khí hậu Việt Nam là loại khí hậu là gì ?''': '''Nhiệt đới gió mùa''',
'''Có 2 người bạn 1 mù, 1 câm đi shopping. Câm mua cái nón thì lấy tay chỉ lên đầu và gõ gõ mấy cái còn Mù muốn mua kem đánh răng thì làm sao?''': '''Nói: Tôi muốn mua kem đánh răng''',
'''Thành phố hoa phượng đỏ là cách gọi khác về thành phố nào sau đây?''': '''Hải Phòng''',
'''Sông nào sau đây còn có tên gọi là sông Vân Cừ?''': '''Sông Bạch Đằng''',
'''Có câu mất bò mới lo.... gì ?''': '''Làm chuồng''',
'''Đâu là thủ đô của Ba Lan?''': '''''',
'''Từ nào sau đây khác nghĩa với ba từ còn lại?''': '''Sinh viên''',
'''Khí hậu Việt Nam là loại khí hậu là gì ?''': '''Nhiệt đới gió mùa''',
'''Tỉnh nào sau đây ở miền Bắc nước ta?''': '''Thái Nguyên''',
'''Ngày nào là ngày Quốc tế Lao động?''': '''1 tháng 5''',
'''Cà phê Espresso có nguồn gốc từ nước nào ?''': '''Ý''',
'''Trong 1 hình chữ nhật có bao nhiêu góc vuông ?''': '''4''',
'''Ai là cầu thủ ghi nhiều hat-trick nhất tại EPL tính đến năm 2023?''': '''Alan Shearer''',
'''"Thành phố hoa phượng đỏ" là cách gọi khác về thành phố nào sau đây?''': '''Hải Phòng''',
'''Truyện cổ tích "Cây tre trăm đốt" có câu thần chú gì?''': '''Khắc Nhập Khắc Xuất''',
'''"Hò khoan Lệ Thủy" là loại hình dân ca của tỉnh nào?''': '''Quảng Bình''',
'''Trong tín ngưỡng dân gian Việt Nam, Táo Quân lên chầu trời vào ngày nào?''': '''23 Tháng Chạp''',
'''Tổng thống da màu đầu tiên trong lịch sử Hoa Kỳ là ai?''': '''Barack Obama''',
'''Đâu là tỉnh thành không giáp biển?''': '''Sơn La''',
'''Chùa Một Cột tọa lạc ở đâu của nước ta?''': '''Hà Nội''',
'''Điền từ còn thiếu trong câu sau "Quân tử nhất ngôn, tứ ... nan truy"?''': '''Mã''',
'''Đâu là thú kéo xe cho ông già Noel?''': '''Tuần Lộc''',
'''Suối cá thần Cẩm Lương thuộc tỉnh nào?''': '''Thanh Hóa''',
'''Truyền thuyết "Con Rồng Cháu Tiên" giải thích điều gì?''': '''Nguồn Gốc Dân Tộc Việt Nam''',
'''Đâu là thủ đô của Thái Lan?''': '''Bangkok''',
'''Vườn Quốc gia Xuân Thủy thuộc tỉnh nào?''': '''Nam Định''',
'''"The Toffees" là biệt danh của câu lạc bộ bóng đá nào?''': '''Everton''',
'''Tranh dân gian Đông Hồ có nguồn gốc từ đâu?''': '''Bắc Ninh''',
'''Quân đội nước nào thả 2 quả bom nguyên tử xuống Nhật Bản trong Chiến tranh thế giới lẫn thứ hai?''': '''Mỹ''',
'''Truyền thuyết "Con Rồng Cháu Tiên" kể về nguồn gốc của dân tộc Việt Nam liên quan đến ai?''': '''Âu Cơ Và Lạc Long Quân''',
'''Ai là tác giả của bài hát Vợ người ta?''': '''Phan Mạnh Quỳnh''',
'''Sơn Tinh - Thủy Tinh là câu chuyện kể về điều gì?''': '''Cuộc Chiến Tranh Giành Công Chúa Mỵ Nương''',
'''Tam Quốc Diễn Nghĩa là tiểu thuyết nổi tiếng của tác giả nào?''': '''La Quán Trung''',
'''Một trong các bài hát nổi tiếng của Sơn Tùng MTP?''': '''LẠC TRÔI''',
'''Thám tử lừng danh Conan là truyện của tác giả nước nào?''': '''Nhật Bản''',
'''Nhân vật nào trong truyền thuyết dân gian Việt Nam cưỡi ngựa sắt đánh giặc?''': '''Thánh Gióng''',
'''Đờn ca tài tử là loại hình nghệ thuật truyền thống của vùng nào?''': '''C''',
'''Hát Xoan là loại hình nghệ thuật của tỉnh nào?''': '''Phú Thọ''',
'''Làng nghề truyền thống Bát Tràng nổi tiếng với sản phẩm gì?''': '''C''',
'''Màu sắc chủ đạo trang phục của ông già Noel''': '''Đỏ - Trắng''',
'''Quân đội nước nào thả 2 quả bom nguyên tử xuống Nhật Bản trong Chiến tranh thế giới lần thứ hai?''': '''Mỹ''',
    

    }
    try:process_question(driver, questions_db)
    except:pass
    
    try:process_question(driver, questions_db)
    except:pass

    try:process_question(driver, questions_db)
    except:pass

    try:process_question(driver, questions_db)
    except:pass

    try:process_question(driver, questions_db)
    except:pass
    time.sleep(1)


def process_question(driver, questions_db):
    try:
        question_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".containner .title"))
        )
        question_text = question_element.text.strip()

        best_match = next(((q, a) for q, a in questions_db.items() if q in question_text), None)

        if best_match:
            for option in driver.find_elements(By.CSS_SELECTOR, ".list .li"):
                if best_match[1] in option.text:
                    option.click()
                    time.sleep(3)
                    print("chọn")
                    return
        else:
            with open("Cauhoithieu.txt", "a+", encoding="utf-8") as f:
                f.write(f"{question_text}\n")
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='C']"))
            )
            element.click()
            time.sleep(20)
    except Exception as e:
        print(f"Lỗi khi lấy câu hỏi hoặc trả lời: {e}")
    
def create_position_queue():
    q = queue.Queue()
    y = 0
    for x in range(0, 10600, 530):
        if x >= 5300:
            q.put(( x - 5300, 900))
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

def CheckConLanTraLoiKhong(driver):
    """Kiểm tra xem có lượt trả lời câu hỏi nào không"""
    driver.get(f"https://{thuandeptraivip}.live/question?back=/gameshow")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@class="active" and text()="Bắt đầu trả lời câu hỏi"]'))
        )
        print("✅ Có lượt trả lời câu hỏi!")
        return True
    except:
        print("❌ Không có lượt trả lời câu hỏi!")
        return False

def open_chrome(ID, TEN):
    global active_sessions
    ToaDO_X, ToaDO_Y = get_position()
    active_sessions[ID] = (ToaDO_X, ToaDO_Y)
    print(f"🟢 Mở trình duyệt cho {TEN} tại tọa độ ({ToaDO_X}, {ToaDO_Y})")
    url = f"http://127.0.0.1:19995/api/v3/profiles/start/{ID}?win_pos={ToaDO_X},{ToaDO_Y}&win_scale=0.25&win_size=290,800"
    json_data = requests.get(url).json()
    remote_debugging_address = json_data["data"]["remote_debugging_address"]
    driver_path = json_data["data"]["driver_path"]
    options = webdriver.ChromeOptions()
    options.debugger_address = remote_debugging_address
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(f"https://{thuandeptraivip}.live/home")
        driver.get(f"https://{thuandeptraivip}.live/personal")
        time.sleep(5)
        TrangThaiDangNhap = False
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "user_name")))
        element_text = element.text.strip()
        if "Chưa đăng nhập !" in element_text:
            print("⚠️ Trình Duyệt Chưa Được Đăng Nhập Tài Khoản!")
        else:
            TrangThaiDangNhap = True
            print("✅ Tài Khoản Đã Đăng Nhập Thành Công!.")
            print(f"📌 Tên Tài Khoản: {element_text}")
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "integral")))
            diem_hien_tai = element.text.strip()
            print(f"📌 Điểm Hiện Tại : {diem_hien_tai}")
        CUTT=True
        if TrangThaiDangNhap:
            while CheckConLanTraLoiKhong(driver):
                element = WebDriverWait(driver, 20).until( EC.presence_of_element_located((By.XPATH, '//div[@class="active"]')))
                element.click()
                time.sleep(3)
                current_url = driver.current_url
                if current_url == f"https://{thuandeptraivip}.live/answer?time=20":
                    print("URL is correct!")
                    Traloi(driver)
                    time.sleep(5)
                elif current_url == f"https://{thuandeptraivip}.live/login":
                    CUTT=False
                    with open("TAiKHOAN.txt", "a", encoding="utf-8") as f:
                        f.write(f"{TEN}\n")
                        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
                        print("✅ Dữ liệu đã được ghi vào TAiKHOAN.txt")

                else:
                    print("URL is not correct, current URL is:", current_url)
        if CUTT:  
            driver.get(f"https://{thuandeptraivip}.live/personal")
            time.sleep(3)
            try:
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "user_name")))
                ten_tai_khoan = element.text.strip()
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "integral")))
                diem_sau_khi_hoan_thanh = element.text.strip()
                print(f"📌📌 Tên Tài Khoản: {ten_tai_khoan}")
                print(f"📌📌 Điểm Sau Khi Hoàn Thành: {diem_sau_khi_hoan_thanh}")
            except Exception as e:
                print("❌ Không Thể Truy Cập Trang Web!")
                with open("TAiKHOAN.txt", "a", encoding="utf-8") as f:
                    f.write(f"{TEN}\n")
                    requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
                    print("✅ Dữ liệu đã được ghi vào TAiKHOAN.txt")
            print(f"🔴 Đóng trình duyệt: {ID} tại tọa độ ({ToaDO_X}, {ToaDO_Y})")
    except Exception as e:
        print(f"⚠️ Lỗi khi chạy trình duyệt: ")
        with open("TAiKHOAN.txt", "a", encoding="utf-8") as f:
            f.write(f"{TEN}\n")
            requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
            print("✅ Dữ liệu đã được ghi vào TAiKHOAN.txt")
    finally:
        driver.quit()
        requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
        position_queue.put((ToaDO_X, ToaDO_Y))
        active_sessions.pop(ID, None)
    requests.get(f"http://127.0.0.1:19995/api/v3/profiles/close/{ID}")
# Lấy danh sách profile từ API
a = requests.get("http://127.0.0.1:19995/api/v3/profiles?per_page=99999&sort=0").json()

# Sử dụng đa luồng để mở nhiều trình duyệt cùng lúc
stt = 0
ChayBiLoi = []
checkcu=int(input("Nhập Thủ Công [1] | Nhập Dây [2] : "))
if checkcu == 1:
    while True:
        stt += 1
        them = input(f"Nhập Trình Duyệt Muốn Chạy [ALL] <{stt}>: ").strip()

        if them.lower() != "all" and them:  # Kiểm tra input không rỗng và không phải "all"
            ChayBiLoi.append(them)
        else:
            break
else:
    st1=int(input("Nhập Điểm Bắt Đầu: "))
    st2=int(input("Nhập Điểm Kết Thúc: "))
    for x in range(st1,st2+1,1):
        ChayBiLoi.append(x)
        print(x)


 


for x in range(3):
    with ThreadPoolExecutor(max_workers=20) as executor:
        for profile in a["data"]:
            ID = profile["id"]
            TEN = profile["name"]
            if ChayBiLoi:  # Nếu có danh sách trình duyệt lỗi, kiểm tra trước khi chạy
                for x in ChayBiLoi:
                    if int(TEN) == int(x):  # Ép kiểu để so sánh đúng
                        executor.submit(open_chrome, ID, TEN)
            else:  # Nếu chọn "all", chạy luôn
                executor.submit(open_chrome, ID, TEN)