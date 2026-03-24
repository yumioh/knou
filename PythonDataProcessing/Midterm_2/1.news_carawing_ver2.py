import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

'''
문제1-1] 웹스크래핑을 통한 데이터 수집
 - 서로 다른 두 개의 키워드와 기간을 설정하여 다음 뉴스에서 기사 제목, 날짜, 언론사명, 요약문(있는 경우)을 수집
 - 수집항목 : 기사 제목, 언론사명, 요약문(있는 경우)
 - 수집범위 : 3월1일 ~ 3월 15일까지 10페이지씩 수집
 - 결과파일 : data/newsscraping.csv로 저장
'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

sd_str = "20260301000000"
ed_str = "20260301235959"
keyword = "중앙화"
start = 1

URL = f'https://search.daum.net/search?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q={keyword}&sd={sd_str}&ed={ed_str}&period=u&p={start}'


res = requests.get(URL,headers=headers, verify=False) # URL의 HTML 전체를 가져옴
soup = BeautifulSoup(res.text, "html.parser") # HTML을 파싱하여 soup을 생성   

title_element = soup.select_one("div.item-title a") 
title = title_element.text.strip() if title_element else "No Title Found"
    
# 2. 날짜
date_element = soup.select_one("span.gem-subinfo .txt_info")
date = date_element.text.strip() if date_element else "No Date Found"
print(date)

media_element = soup.select_one("div.inner_header .tit_item")
media = media_element.text.strip() if media_element else "No Media Found"
print(media)

# 4. 요약문
content_element = soup.select_one("p.conts-desc a")
if content_element :
    content = content_element.get_text(strip=True)
    content = re.sub(r'[\r\n\t\"\'\,]', '', content) # 요약문 내용에서 줄바꿈, 탭 등 불필요한 문자 제거
else :
    "No Content Found"
    
print(content)    

'''뉴스 데이터 제목, 날짜, 요약문, 미디어까지 추출 확인 완료'''



def get_news(URL) : 
    

    
    # 1. 제목
    title_element = soup.select_one("h2#title_area span") 
    title = title_element.text.strip() if title_element else "No Title Found"
    
    # 2. 날짜
    date_element = soup.select_one("span.media_end_head_info_datestamp_time")
    date = date_element.text.strip() if date_element else "No Date Found"
    print(date)
    
    # 3. 언론사
    media_element = soup.select_one("a.media_end_head_top_logo img")
    media = media_element['alt'].strip() if media_element else "No Media Found"
    
    # 4. 요약문
    content_element = soup.select_one("div#newsct_article")
    if content_element :
        content = content_element.text.strip()
        content = re.sub(r'[\r\n\t\"\'\,]', '', content) # 요약문 내용에서 줄바꿈, 탭 등 불필요한 문자 제거
    else :
        "No Content Found"
        
    print(f'날짜: {date}, 제목 : {title} ({URL})')
    print(f'언론사: {media}')
    print(f'요약문 : {content}')
    return (title, date, media, content)


def get_news_list(keyword, toDate, fromDate) :
    news = []
    for date in pd.date_range(toDate, fromDate) :
      sd_str = date.strftime("%Y%m%d") + "000000"
      ed_str = date.strftime("%Y%m%d") + "235959"
      
      page = 1 ## 페이징처리
      while True:
        start = (page-1) * 10 + 1
        URL = f'https://search.daum.net/search?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q={keyword}&sd={sd_str}&ed={ed_str}&period=u&p={start}'
        res = requests.get(URL,headers = headers)
        soup = BeautifulSoup(res.text, "html.parser")

        #해당하는 페이지에 검색할 페이지가 없는 경우
        if soup.select_one("div.not_found02"):
          print("크롤링 끝")
          break

        news_list = soup.select("ul.list_news li")
        
        for item in news_list :
          if len(item.select("div.info_group a")) == 2 :
            news.append(get_news(item.select("div.info_group a")[1]['href']))
        page += 1
        
        print(f"수집 중: {date.strftime('%Y-%m-%d')}의 {page}페이지")
    return pd.DataFrame(news, columns=['title','date','media','content'])

#원하는 키워드, 검색 날짜
keyword = "중앙화"
toDate = "2026.03.01"
fromDate = "2026.03.01"

## rows = get_news_list(keyword, toDate, fromDate)

#data 폴더에 csv로 파일 저장
## rows.to_csv('D:/knou/PythonDataProcessing/Midterm_2/data/newsscraping_26.csv', encoding='utf-8-sig')
