import requests
import re
import os

from fontTools.ttLib import TTFont  # 解析字体文件的包
from PIL import Image, ImageDraw, ImageFont  #绘制图片
import pytesseract   #文字识别库
import numpy

header = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cookie": "_lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=16c47c01fafc8-07aac54d06158d-e343166-144000-16c47c01fafc8; _lxsdk=16c47c01fafc8-07aac54d06158d-e343166-144000-16c47c01fafc8; _hc.v=825e3bfc-d05a-6e37-660c-0cba50dc559e.1564571869; s_ViewType=10; cy=16; cityid=16; cye=wuhan; cy=5; cye=nanjing; _lxsdk_s=16c52116a9d-0a5-da0-bb3%7C%7C25"
}
def seedRequest(url):
    response = requests.get(url ,headers=header)
    response.encoding = "utf-8"
    print(response.status_code)
    return response

def downloadFontFile(): #向解析页面获得css的href，发送请求，对css正则匹配出字体的url，下载字体文件
    cssUrl = "http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/92b88886eb6a3d468078043ccd49b99e.css"
    css_response = seedRequest(cssUrl)
    fontUrl = re.findall('@font-face{font-family: "PingFangSC-Regular-review";src.*?format.*?url\("(.*?)"\);}',css_response.text,re.S)[0]
    print(fontUrl)
    font_response = seedRequest("http:"+fontUrl)
    fontPath = os.path.join(os.getcwd(),os.path.basename(fontUrl))
    with open(fontPath,"wb") as fp:
        fp.write(font_response.content)
    return fontPath

def fontConvert(fontPath):     #将web下载的字体文件解析，返回其编码和汉字的对应关系
    font = TTFont(fontPath)  # 打开文件
    codeList = font.getGlyphOrder()[2:]
    im = Image.new("RGB", (1800, 1000), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(fontPath, 40)
    count = 15
    arrayList = numpy.array_split(codeList,count)   #将列表切分成15份，以便于在图片上分行显示
    for t in range(count):
        newList = [i.replace("uni", "\\u") for i in arrayList[t]]
        text = "".join(newList)
        text = text.encode('utf-8').decode('unicode_escape')
        dr.text((0, 50 * t), text, font=font, fill="#000000")
    # im.save("sss.jpg")
    #  = Image.open("sss.jpg")      #可以将图片保存到本地，以便于手动打开图片查看
    result = pytesseract.image_to_string(im, lang="chi_sim")
    result = result.replace(" ","").replace("\n","")
    codeList = [i.replace("uni","&#x")+";" for i in codeList]
    return dict(zip(codeList,list(result)))

if __name__ == "__main__":
    fontDict = fontConvert(downloadFontFile())
    print(fontDict)