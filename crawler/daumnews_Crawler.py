from operator import concat
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


## 시작 날짜 정의 함수
def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end-start).days+1)]
    return dates

def input_date(day_start, day_end):
    day_list = []
    dates = date_range(day_start, day_end)
    for i in range(len(dates)):
        year = dates[i][:4]
        month = dates[i][5:7]
        day = dates[i][8:]
        day_list.append(year+month+day)
    return day_list

day_start = input("\n크롤링할 시작 날짜를 입력해주세요. ex) 2021-01-01: "" ")
day_end = input("\n크롤링할 마지막 날짜를  입력해주세요. ex) 2021-01-01: "" ")

page_start = int(input("\n크롤링할 시작 페이지를 입력해주세요. ex)1(숫자만입력):"))
page_end = int(input("\n크롤링할 종료 페이지를 입력해주세요. ex)1(숫자만입력):"))

crawl_day_list = input_date(day_start, day_end)
crawl_page_list = [x for x in range(page_start, page_end + 1)]


title=[]
url = []
text = []

for Day in crawl_day_list:
    for page in crawl_page_list:
        # print(f'https://news.daum.net/breakingnews/sports/golf?page={page}&regDate={Day}')
        # requests library를 통해 http 요청을 보내면 요청값의 소스에 해당하는 응답(response)을 받게 됨
        res = requests.get(f'https://news.daum.net/breakingnews/sports/golf?page={page}&regDate={Day}')


        # BeautifulSoup library를 통해 받아온 응답값(res.content)과 html 구문으로 나누어주는 'html.parser'를 인자값으로 넘겨주면 객체에 응답값이 html 구조로 정리됨
        soup = BeautifulSoup(res.content, 'html.parser')

        # html 정보가 저장된 soup 객체에서 기사 제목에 해당하는 부분의 요소만 선택


        # 기사 제목은 "html > body > div > main > section > ... > div > strong > a" 부분에 포함되어 있음

        # soup.select('div > strong > a')를 통해 'div > strong > a'에 해당하는 요소들만 불러올 수 있음
        items = soup.select('div > strong > a')
        items_text = soup.find_all("span" ,"link_txt")

        # 리스트의 첫번째 항목에서 text 부분만 추출하고 .strip() 함수를 통해 앞,뒤 공백을 제거
        items[0].text.strip()

        for k in range(len(items)):
            
            title.append(items[k].text.strip())
            url.append(items[k].attrs['href'])

        for v in range(len(items_text)):
            text.append(items_text[v].text)

list_sum = list(zip(title,url,text))

col = ['title','url', 'text']

df = pd.DataFrame(list_sum, columns=col)
df.to_csv('C:/Users/swjh9523/Desktop/crawler/result/daum_news/daum_new.csv', index=False,encoding='utf-8-sig')

