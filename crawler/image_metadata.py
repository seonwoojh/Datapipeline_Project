from PIL import Image

imgfile = 'C:/Users/swjh9523/Desktop/KakaoTalk_20220627_102915688_01.jpg'
img = Image.open(imgfile)
meta_data = img._getexif()
print(meta_data)