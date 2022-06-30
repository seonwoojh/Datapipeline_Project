# 필요한 라이브러리
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time as time
import urllib.request
import random
from time import sleep
import datetime as dt
import pandas as pd

# Driver 창 켜기

driver = webdriver.Chrome("C:/Users/swjh9523/Desktop/crawler/chromedriver.exe") # Chromedriver PATH
driver.get("https://story.kakao.com/")
driver.maximize_window()
time.sleep(3)

username = '01095236212'
password = 'xhdrP123@'

element_id = driver.find_element_by_name("email")
element_id.send_keys(username)
element_password = driver.find_element_by_name("password")
element_password.send_keys(password)

time.sleep(1.5)

##로그인버튼 클릭
driver.find_element_by_css_selector('button.btn_g.btn_confirm.submit').click()

time.sleep(3)

# --------------------- 로그인까지 완료 2021-07-08

# 해시태그 검색창 들어가기
keyword = input('검색할 단어를 입력하세요 : ')  # Search #
count = 10

url = "https://story.kakao.com/hashtag/{}/".format(keyword)

driver.get(url)
time.sleep(5)

SCROLL_PAUSE_SEC = 0.5
#
# # 스크롤 높이 가져옴
# last_height = driver.execute_script("return document.body.scrollHeight")
#
# while True:
#     # 끝까지 스크롤 다운
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#     # 1초 대기
#     time.sleep(SCROLL_PAUSE_SEC)
#
#     # 스크롤 다운 후 스크롤 높이 다시 가져옴
#     new_height = driver.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         break
#     last_height = new_height


list = driver.find_elements_by_css_selector('.img_thumb._img')
action = ActionChains(driver)
action.move_to_element(list[0]).perform()

#홈으로 올라가기 추가

# 카카오스토리 크롤링
seq = 0
start = time.time()
# 데이터를 저장할 Dictionary
kakao_dict = {'id': [],'date': [], 'text': [], 'tag': []}

for j in range(count):
    time.sleep(3)
    list = driver.find_elements_by_css_selector('.img_thumb._img')
    action = ActionChains(driver)
    action.move_to_element(list[j]).click().perform()
    # driver.find_elements_by_css_selector('.img_thumb._img')[j].click()
    time.sleep(3)

    # id수집 - 이름
    info_id = driver.find_element_by_css_selector('a.pf_name').text
    kakao_dict['id'].append(info_id)
    driver.implicitly_wait(5)

    # 시간 수집
    time_raw = driver.find_element_by_css_selector('span.time').text
    kakao_dict['date'].append(time_raw)
    driver.implicitly_wait(5)

    # text 수집

    content = driver.find_element_by_css_selector('div._content').text.split()
    text = []
    for i in range(len(content)):
        if '#' in content[i]:
            pass
        else:
            text.append(content[i])
    clean_text = ' '.join(text)
    kakao_dict['text'].append(clean_text)
    driver.implicitly_wait(5)

    # hashtag 수집
    hash = driver.find_element_by_css_selector('div._content').text.split()
    hashtags = []
    for i in range(len(hash)):
        if '#' in hash[i]:
            hashtags.append(hash[i])
        else:
            pass
    kakao_dict['tag'].append(hashtags)
    time.sleep(3)
    driver.find_element_by_css_selector('._btnClose').click()
    time.sleep(3)

df = pd.DataFrame.from_dict(kakao_dict)
df.to_excel('C:/Users/swjh9523/Desktop/crawler/result/kakao_story/' + keyword + "_results.xlsx")