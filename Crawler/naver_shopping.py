from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import pandas as pd
import numpy
from random import random
from random import uniform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def chromeWebdriver():
  #chrome_service = ChromeService(executable_path=ChromeDriverManager().install())
  chrome_service = ChromeService(executable_path=r'D:/Downloads/chromedriver')
  options = Options()
  options.add_experimental_option('detach', True)
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
  options.add_argument(f'user-agent={user_agent}')
  
  driver = webdriver.Chrome(service=chrome_service, options=options)
  return driver

url = 'https://smartstore.naver.com/newyorkwoodbury/products/3005303161?NaPm=ct%3Dl5lw29pk%7Cci%3Dfe8d4348e070f05ce0f4521158b7ba63b72b49da%7Ctr%3Dsls%7Csn%3D589004%7Chk%3Db2db02fec6479f543658eac16437ac29f572c72f'
#url = 'https://smartstore.naver.com/newyorkwoodbury/products/6828703302?NaPm=ct%3Dl5m6eagg%7Cci%3D04dba46fc9dfd607c4768b6059320a6195e1ffb6%7Ctr%3Dslsl%7Csn%3D589004%7Chk%3D42a4d253ee2cac4c5f934709cc9f5430a714d892'
#url = 'https://smartstore.naver.com/youlovelondon/products/5542794701?NaPm=ct%3Dl5m6npyo%7Cci%3Da9a9463693b10d07263e30784f648289a4758025%7Ctr%3Dslsl%7Csn%3D1092991%7Chk%3De29fc03e2923dabd7811a803ab1ef19010c1aa55'
driver = chromeWebdriver()
driver.get(url)
time.sleep(2)


comment=[]
star=[]
date=[]

num = 2

save_path = r'D:\`'

try:
  try:
    while True:
      time.sleep(1)
      tmp = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/div/div/a[{}]'.format(num))
      tmp.send_keys("\n")

      for cmt in range(1,21):
        #comment
        time.sleep(1)
        lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span'.format(cmt))

        if lis.text == '한달사용기':
          lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span[2]'.format(cmt))
          if lis.text == '재구매':
            lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span[3]'.format(cmt))
        elif lis.text == '재구매':
          lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span[2]'.format(cmt))
        print(lis.text)
        comment.append(lis.text)

        #star
        liss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/em'.format(cmt))
        star.append(liss.text)

        #date
        lisss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[2]/span'.format(cmt))
        date.append(lisss.text)

      num += 1
      if num == 13:
        num = 2
  except NoSuchElementException:
    df = pd.DataFrame({
  									 'comment' : comment,
                     'star' : star,
                     'date' : date,
                     })
    df.index = df.index+1

    # to_csv 저장
    df.to_csv(save_path + 'shopping.csv' , encoding='utf-8-sig')
    print('save done')
except ElementNotInteractableException:
  df = pd.DataFrame({
  									 'comment' : comment,
                     'star' : star,
                     'date' : date,
                     })
  # 인덱스 1부터 실행
  df.index = df.index+1

  # to_csv 저장
  df.to_csv(save_path + 'shopping.csv' , encoding='utf-8-sig')
  print('save done')

#for page in range(2, 13):
#  tmp = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/div/div/a[{}]'.format(page))
#  tmp.send_keys("\n")
#
#  for cmt in range(1,21):
#    #comment
#    lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span'.format(cmt))
#    if lis.text == '한달사용기' or lis.text == '재구매':
#      lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span[2]'.format(cmt))
#      if lis.text == '재구매':
#        lis = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[2]/div/span[3]'.format(cmt))
#    
#    comment.append(lis.text)
#
#    #star
#    liss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/em'.format(cmt))
#    star.append(liss.text)
#
#    #date
#    lisss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[2]/span'.format(cmt))
#    date.append(lisss.text)
#
#    driver.find_element(By.XPATH, '//*[@id="REVIEW"]/div/div[3]/div/div[2]/div/div/a[12]')

print(comment)
print(star)
print(date)

driver.quit()