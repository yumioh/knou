import random as rd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib3

'''
문제1-1] 웹스크래핑을 통한 데이터 수집
 - 서로 다른 두 개의 키워드와 기간을 설정하여 다음 뉴스에서 기사 제목, 날짜, 언론사명, 요약문(있는 경우)을 수집
 - 수집항목 : 기사 제목, 언론사명, 요약문(있는 경우)
 - 수집범위 : 3월1일 ~ 3월 20일까지 5페이지씩 수집
 - 결과파일 : data/newsscraping.csv로 저장
'''

# secure 요청에 대한 경고 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://search.daum.net/',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

toDate = "2026-03-01"
fromDate = "2026-03-20"
keyword = "중앙화"

news_data = []
for date in pd.date_range(toDate, fromDate) :
    # 시간 포맷 맞추기
    sd_str = date.strftime("%Y%m%d") + "000000"
    ed_str = date.strftime("%Y%m%d") + "235959"
      
    for page in range(1, 5) :         
        
        URL = f'https://search.daum.net/search?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q={keyword}&sd={sd_str}&ed={ed_str}&period=u&p={page}'
        res = requests.get(URL,headers=headers, verify=False) 
        soup = BeautifulSoup(res.text, "html.parser")  

        print(f"--- {date.strftime('%Y-%m-%d')} 데이터 수집 중 ---")

        # 뉴스 리스트 들고 오기 
        news_items = soup.select("ul.c-list-basic > li")
        
        for item in news_items :
            #1. 제목
            title_element = item.select_one(".item-title") 
            title = title_element.text.strip() if title_element else "No Title Found"
            
            # 2. 날짜
            date_element = item.select_one(".gem-subinfo .txt_info")
            date_el = date_element.text.strip() if date_element else "No Date Found"

            # 3. 언론사
            media_element = item.select_one(".inner_header .tit_item")
            media = media_element.text.strip() if media_element else "No Media Found"

            # 4. 요약문
            content_element = item.select_one(".conts-desc")
            if content_element :
                content = content_element.get_text(strip=True)
                content = re.sub(r'[\r\n\t\"\'\,]', '', content) # 요약문 내용에서 줄바꿈, 탭 등 불필요한 문자 제거
            else :
                content = "None"
            
            news_data.append((date_el, title, media, content))

        # 페이지가 없는 경우 종료
        paging_area = soup.select_one(".inner_paging")
        if paging_area:
            # 현재 페이지 이후로 넘어갈 수 있는 있는지 확인
            next_page_links = paging_area.select("a.link_page")

            if not next_page_links:
                print(f"  {page}페이지가 마지막입니다.")
            break
        else:
            # 페이징 바 자체가 안 보인이면 1페이지 미만인 경우
            break

df =  pd.DataFrame(news_data, columns=['date','title','media','content'])
print(f"총 {len(df)}개의 기사 수집 완료")
df.to_csv(f'./PythonDataProcessing/Midterm_2/data/newsscraping_26_{keyword}.csv', encoding='utf-8-sig')
