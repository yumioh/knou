import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

'''
문제1-1] 웹스크래핑을 통한 데이터 수집
 - 서로 다른 두 개의 키워드와 기간을 설정하여 다음 뉴스에서 기사 제목, 날짜, 언론사명, 요약문(있는 경우)을 수집
 - 수집항목 : 기사 제목, 언론사명, 요약문(있는 경우)
 - 3월1일 ~ 3월 15일까지 10페이지씩 수집
 - 결과파일 : data/newsscraping.csv로 저장
'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def get_news(URL) : 
    
    res = requests.get(URL, headers=headers) # URL의 HTML 전체를 가져옴
    soup = BeautifulSoup(res.text, "html.parser") # HTML을 파싱하여 soup을 생성
    
    # 1. 제목
    title_element = soup.select_one("div.item-title a") 
    title = title_element.text.strip() if title_element else "No Title Found"
    
    # 2. 날짜
    date_element = soup.select_one("span.gem-subinfo .txt_info")
    date = date_element.text.strip() if date_element else "No Date Found"
    print(date)
    
    # 3. 언론사
    media_element = soup.select_one("div.inner_header tit_item")
    media = media_element.text.strip() if media_element else "No Media Found"
    
    # 4. 요약문
    content_element = soup.select_one("p.conts-desc clamp-g2 a")
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
      
    for page in range(1, 10) : ## 5페이지까지 처리
        URL = f'https://search.daum.net/search?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q={keyword}&sd={sd_str}&ed={ed_str}&period=u&p={page}'
        res = requests.get(URL,headers = headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
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

rows = get_news_list(keyword, toDate, fromDate)

#data 폴더에 csv로 파일 저장
rows.to_csv('D:/knou/PythonDataProcessing/Midterm_2/data/newsscraping_26.csv', encoding='utf-8-sig')
