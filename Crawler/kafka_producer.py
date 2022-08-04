#!/usr/bin/python3
import os
import time
import json
from kafka import KafkaProducer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import re

def chromeWebdriver():
    user_agent = 'Mozilla/5.0 (X11; Linux X86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent={0}'.format(user_agent))
    driver = webdriver.Chrome('./chromedriver',options=options)

    return driver

url=os.environ.get("url")
topic=os.environ.get("topic")
server=os.environ.get("server")
print(url)
print(topic)
print(server)
driver = chromeWebdriver()
driver.get(url)
time.sleep(2)

comment=[]
star=[]
date=[]

num = 2

producer = KafkaProducer(acks=1, compression_type='gzip', bootstrap_servers=server, value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'))

start=time.time()

try:
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
                                        comment.append(lis.text)

                                        #star
                                        liss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/em'.format(cmt))
                                        star.append(liss.text)

                                        #date
                                        lisss = driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/div[2]/div/div[3]/div[6]/div/div[3]/div/div[2]/ul/li[{}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[2]/span'.format(cmt))
                                        date.append(lisss.text)
                                        comment[0]=re.sub(',', '', comment[0])

                                        tmp={'topic':topic, 'star':star.pop(), 'comment':comment.pop(), 'date':date.pop()}
                                        producer.send(topic, value=tmp)

                                        producer.flush()

                                num += 1
                                if num == 13:
                                        num = 2

                except NoSuchElementException:
                        print("elapsed :", time.time() - start)
                        tmp={'status':'Success', 'elapsed':time.time()-start}
                        producer.send(topic, value=tmp)
                        driver.quit()



        except ElementNotInteractableException:
                print("elapsed :", time.time() - start)
                tmp={'status':'Success', 'elapsed':time.time()-start}
                producer.send(topic,value=tmp)
                driver.quit()

except:
    tmp={'status':'Failed', 'elapsed':time.time()-start}
    producer.send(topic,value=tmp)
