import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

'''
문제1-1] 웹스크래핑을 통한 데이터 수집 
 - 수집항목 : 기사 제목, 날짜, 언론사명, 요약문(있는 경우)
 - 수집한 데이터를 webscraping_2510.csv로 저장
 - 구조가 통일된 네이버 뉴스만 수집
 - 단, 네이버 뉴스는 스크롤을 내려야 다음 페이지가 로딩되는 방식이라 검색 결과의 첫 페이지만 수집 가능합니다.
'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

# 네이버 뉴스 URL을 받아 제목, 날짜, 언론사, 기사 본문을 수집하는 함수
def get_news(URL) : # 입력 : 수집할 네이버 뉴스 기사의 URL의 주소 
    
    res = requests.get(URL, headers=headers) # URL의 HTML 전체를 가져옴
    soup = BeautifulSoup(res.text, "html.parser") # HTML을 파싱하여 soup을 생성
    
    # 1. 제목 추출
    title_element = soup.select_one("h2#title_area span") 
    title = title_element.text.strip() if title_element else "No Title Found"
    
    # 2. 날짜 추출
    date_element = soup.select_one("span.media_end_head_info_datestamp_time")
    date = date_element.text.strip() if date_element else "No Date Found"
    print(date)
    
    # 3. 언론사 추출
    media_element = soup.select_one("a.media_end_head_top_logo img")
    media = media_element['alt'].strip() if media_element else "No Media Found"
    
    # 4. 본문 추출
    content_element = soup.select_one("div#newsct_article")
    if content_element :
        content = content_element.text.strip()
        content = re.sub(r'[\r\n\t\"\'\,]', '', content) # 본문 내용에서 줄바꿈, 탭 등 불필요한 문자 제거
    else :
        "No Content Found"
        
    print(f'수집완료 : {title} ({URL})')
    print(f'언론사: {media}')
    print(f'날짜: {date}')
    return (title, date, media, content)

# 특정 키워드와 기간으로 네이버 뉴스 검색 결과 목록을 순회하며 뉴스 수집
def get_news_list(keyword, to_date, from_date) : # 입력 : 검색할 키워드, 시작일, 종료일
    news = [] # 수집할 뉴스 URL 저장할 리스트
    
    for date in pd.date_range(to_date, from_date) :
        str_d = date.strftime("%Y.%m.%d")

        print(f"\n--- {str_d} 날짜의 뉴스 수집 시작 ---")
    
        # 날짜와 키워드로 검색 결과 url 생성
        URL = f'https://search.naver.com/search.naver?ssc=tab.news.all&query={keyword}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={str_d}&de={str_d}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom{str_d}to{str_d}&is_sug_officeid=0&office_category=0&service_area=0$start=20'
    
        # 뉴스 목록 가져오기
        res = requests.get(URL,headers = headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 뉴스 목록에서 뉴스 기사에 해당하는 태그만 추출
        links = soup.select("div.group_news a[nocr='1']")
       
        # 뉴스 링크만 추출
        href_list = [a["href"] for a in links if a.has_attr("href")]
        
        # 'n.news.naver.com'을 포함하는 링크만 추출
        # 언론사별로 다른 HTML 구조를 파싱하는 복잡함을 피하고, 구조가 통일된 네이버뉴스 페이지만을 대상으로 하기 위함
        naver_news_list = [href for href in href_list if 'n.news.naver.com' in href]
        print(naver_news_list)        
        
        #뉴스 목록 해당 기사 url 얻음
        for url in naver_news_list :
            news.append(get_news(url))
        #get_news로 가져온 뉴스 데이터를 데이터프레임(제목, 날짜, 신문사, 내용)으로 저장
        print(news)
    return pd.DataFrame(news, columns=['title','date','media','content'])
        
    
# 키워드, 날짜 설정
# 네이버 뉴스는 자바스크립트로 스크롤 시 다음 페이지를 로딩하여 beautifulsoup으로 여러 페이지 뉴스 기사를 수집하는데 한계
keyword = "양자컴퓨팅"
to_date = "2025.10.01"
from_date = "2025.10.08"

rows = get_news_list(keyword, to_date, from_date)

# 총 70건 저장
rows.to_csv('D:/knou/PythonDataProcessing/Midterm/webscraping_2510.csv', encoding='utf-8-sig')
print(f"\n CSV 저장 완료 (총 {len(rows)}건)")