import time
import selenium
import pandas as pd
from selenium import webdriver


# 크롤링 함수 정의
def get_post_info(keyword: str, start_date: str, end_date: str, pages: int) -> pd.DataFrame:
    total_header = []
    total_contents = []
    total_date = []
    # chromedriver path
    driver = webdriver.Chrome('C:/Users/swjh9523/Desktop/crawler/chromedriver.exe')

    for j in range(1, pages + 1):
        # first page
        first_url = f"https://section.blog.naver.com/Search/Post.nhn?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate=" \
                    f"{start_date}&endDate={end_date}&keyword={keyword}"
        # After first page
        loop_url = f"https://section.blog.naver.com/Search/" \
                   f"Post.nhn?pageNo={j}&rangeType=PERIOD&orderBy=sim&startDate=" \
                   f"{start_date}&endDate={end_date}&keyword={keyword}"
        driver.get(first_url)

        if j != 1:
            driver.get(loop_url)

        # loading...
        time.sleep(1.5)

        # crawling informations on each 7 contents
        # if any selector does not exist, that selector returns blank string
        for i in range(1, 8):
            time.sleep(1)
            try:
                head = driver.find_element_by_css_selector(
                    f"#content > section > div.area_list_search > div:nth-child({i}) > div > div.info_post > div.desc > a.desc_inner > strong > span").text
            except selenium.common.exceptions.NoSuchElementException:
                head = " "
            try:
                contents = driver.find_element_by_css_selector(
                    f"#content > section > div.area_list_search > div:nth-child({i}) > div > div.info_post > div.desc > a.text").text
            except selenium.common.exceptions.NoSuchElementException:
                contents = " "
            try:
                date = driver.find_element_by_css_selector(
                    f"#content > section > div.area_list_search > div:nth-child({i}) > div > div.info_post > div.writer_info > span.date").text
            except selenium.common.exceptions.NoSuchElementException:
                date = " "

            time.sleep(1)
            print(head)
            print(contents)
            print(date)
            total_header.append(head)
            total_contents.append(contents)
            total_date.append(date)

    return total_header, total_contents, total_date


# 검색 형태 지정 및 csv 파일로 저장
pages = int(input("몇 페이지 까지 크롤링 할까요? \n => ")) # pages = 12
keyword = input("검색하실 키워드를 입력해주세요 \n =>") # keyword = "KLPGA"
start_date = input("검색 시작일을 입력해주세요 ex) 2000-01-01 \n =>") # start_date = '2021-06-12'
end_date = input("검색 종료일을 입력해주세요 ex) 2000-01-01 \n =>") # end_date = '2022-06-12'

total_header, total_contents, total_date = get_post_info(keyword, start_date, end_date, pages)
data = {"header": total_header, "contents": total_contents, "date": total_date}

df = pd.DataFrame(data, columns=["header", "contents", "date"])
keyword = keyword.replace(" ", "_")
title = keyword+ "_" + str(pages) + "_" + "네이버블로그_크롤링.csv"

df.to_csv('C:/Users/swjh9523/Desktop/crawler/result/naver_blog/naver_{}_검색결과.csv'.format(keyword), encoding='utf-8-sig')