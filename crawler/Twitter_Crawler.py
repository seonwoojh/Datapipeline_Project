# twitter api connect
consumer_key = "DNUzLXnRfZnXoVxkCiNQuczOs"
consumer_secret = "TMTkIaCI0fXBXRaEm4cVHaUqlL2zvXVCVO3n9ltIxVkSsmm3q9"  
access_token = "1323122806733762560-zj2lLfkRgKfRLjuJeFxQ54FOqGTn2O"
access_token_secret = "nsAYlZ1iIa9HpQBuuqFWzbEDcQrqegbLrM55gJzLHiVtf"

# import tweepy
# import datetime
# import threading
# import smtplib
# from email.mime.text import MIMEText
# import json
# import os

# def UCS(s):
#     return "".join((i if ord(i) < 10000 else '\dfffd' for i in s))

# pic = []
# max_tweets = 20
# searched_tweets = []
# last_id = -1

# def check_time(curr_hour):
#     dt = datetime.datetime.now()
#     celeb_Tweet = []
    
#     if curr_hour != dt.hour:
#         print(dt)
#         curr_hour = dt.hour
        
#         consumer_key = "DNUzLXnRfZnXoVxkCiNQuczOs"
#         consumer_secret = "TMTkIaCI0fXBXRaEm4cVHaUqlL2zvXVCVO3n9ltIxVkSsmm3q9"
        
#         auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#         access_token = "1323122806733762560-zj2lLfkRgKfRLjuJeFxQ54FOqGTn2O"
#         access_token_secret = "nsAYlZ1iIa9HpQBuuqFWzbEDcQrqegbLrM55gJzLHiVtf"
#         auth.set_access_token(access_token, access_token_secret)
#         api = tweepy.API(auth)
        
#         hour = 0
#         if curr_hour == 0:
#             hour = 24
#         else:
#             hour = curr_hour
            
#         while len(searched_tweets) < max_tweets:
#             count = max_tweets - len(searched_tweets)
            
#             try:
#                 public_tweets = api.home_timeline()
#                 if not public_tweets:
#                     break
#                 searched_tweets.extend(public_tweets)
#                 last_id = public_tweets[-1].id
                
#             except tweepy.TweepError as e:
#                 break
            
            
#         for i, tweet in enumerate(public_tweets):
#             print(i)
#             print(tweet.text)
#             print("\n")
#             celeb_Tweet.append("\n")
            
#  #여기서부턴 트위터 내에 있는 이미지를 크롤링
#             try:
#                 celeb_Tweet.append("★{0}번째 트윗★\n".format(i+1))
#                 celeb_Tweet.append(tweet.text + "\n")
#                 print(len(tweet.extended_entities['media']))
#                 for count in range(0, len(tweet.extended_entities['media'])):
#                     if tweet.extended_entities['media'][count]['type'] == 'photo':
#                         pic.append(tweet.extended_entities['media'][count]['media_url'])
#                         celeb_Tweet.append("\n")
#                         celeb_Tweet.append("▶▶▶{0}번째 사진:".format(count+1) + tweet.extended_entities['media'][count]['media_url'])
#                 celeb_Tweet.append("\n")
                
#             except: #try 구문 안에서 NG가 나더라도, except구문으로 이동한다
#                 celeb_Tweet.append("\n")
#                 print('0')
                
# #         mail_id = "tjswl950@gmail.com"
# #         mail_pw = "xhdrP123@"
        
# #         s = smtplib.SMTP("smtp.gmail.com", 587)
# #         s.starttls();
        
# #         s.login(mail_id, mail_pw)
        
# #         msg = MIMEText("".join(celeb_Tweet)) ## 리스트를 문자열로 바꾸는 방법은 join함수를 이용
        
# #         msg["Subject"] = "{0}월 {1}일, {2}시".format(dt.month, dt.day, dt.hour) + " " + "celeb Tweet"
# #         s.sendmail(mail_id, "메일주소", msg.as_string())
# #         s.close()
    
# #     threading.Timer(1, check_time, args=[curr_hour]).start()
    
    
# # if __name__ == "__main__":
# #     check_time(-1)
# print(celeb_Tweet)

from multiprocessing import AuthenticationError
from re import search
from winreg import QueryReflectionKey
import tweepy
from tweepy import OAuthHandler
import json
import wget
import os

consumer_key = "DNUzLXnRfZnXoVxkCiNQuczOs"
consumer_secret = "TMTkIaCI0fXBXRaEm4cVHaUqlL2zvXVCVO3n9ltIxVkSsmm3q9"  
access_token = "1323122806733762560-zj2lLfkRgKfRLjuJeFxQ54FOqGTn2O"
access_token_secret = "nsAYlZ1iIa9HpQBuuqFWzbEDcQrqegbLrM55gJzLHiVtf"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

query = input(u'해시태그 검색어를 입력하세요 :' )
max_tweets = int(input('검색하고 싶은 트윗 갯수를 입력하세요. : ' ))
searched_tweets = []
last_id = -1

while len(searched_tweets) < max_tweets:
    count = max_tweets - len(searched_tweets)
    new_tweets = api.search_tweets(q = query)
    if not new_tweets:
        break
    searched_tweets.extend(new_tweets)
    last_id = new_tweets[-1].id
pic = []

for a in searched_tweets:
    try:
        print(len(a.extended_entities['media']))
        for count in range(0, len(a.extended_entities['meida'])):
            if a.extended_entities['media'][count]['type'] == 'photo':
                pic.append(a.extended_entities['media'][count]['media_url'])
    except:
        print("0")
pic = list(set(pic))
print(pic)
# no = 0
# for b in pic:
#     no=no+1
#     try:
#         wget.download(b+":orig", "picture/"+str(no)+".jpg")
#     except:
#         pass