import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


'''
문제1] 웹스크래핑을 통한 데이터 수집 : BeautifulSoup을 활용

'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

#이메일 처리
def email_reg(content) -> str:
    result = re.sub('[\w.+-]+@[\w-]+\.[\w.-]+', '', content)
    return result

#날짜형식 변경
def remove_time_prefix(input_str) :
  if any([x in input_str for x in ["오전", "오후"]]):
    #기사입력, 오후, 오전 반환
    date_time_str = re.sub(r'기사입력|오후 |오전 ', '', input_str).strip()
    print(date_time_str)
    #기사입력 2025.10.01. 오후 05:21
    try :
        # 날짜 및 시간 형식의 문자열을 날짜 객체로 파싱
        date_time = datetime.strptime(date_time_str, "%Y.%m.%d. %H:%M")
        # 날짜 부분만 추출
        date = date_time.strftime("%Y.%m.%d")
    except ValueError: #올바른 형식으로 파싱 할수 없는 경우 None 반환
      return None
  else :
      date_time = datetime.strptime(input_str, "%Y-%m-%d %H:%M:%S")
      date = date_time.strftime("%Y.%m.%d")
  return date

#네이버 뉴스기사 정보 가져오기 
def get_news(URL) :
  res = requests.get(URL, headers=headers)  #URL을 사용하여 요청 및 응답 받기
  soup = BeautifulSoup(res.text, "html.parser") # BeautifulSoup을 이용하여 파싱

  title_element = "" # 기사 제목
  date_element = "" # 기사 날짜
  media_element = "" # 언론사
  content_element = "" # 기사 내용 변수
  #특정 HTML 요소를 선택하여 뉴스 정보 추출
  if soup.select_one("h2#title_area span") != None: # 일반 기사
    title_element = soup.select_one("h2#title_area span") # 기사 제목
    date_element = soup.select_one("span.media_end_head_info_datestamp_time") # 기사 날짜
    media_element = soup.select_one("a.media_end_head_top_logo img") # 언론사명
    content_element = soup.select_one("div#newsct_article") # 기사 내용
  else : # 불필요한 내용을 줄이기 위해 연예, 스포츠 뉴스 제외
    return None
  
  if title_element: # 기사 제목 추출
    title = title_element.text.strip()
  else:
    title = "No Title Found"

  if date_element and 'data-date-time' in date_element.attrs: # 기사 날짜 추출
    date = date_element['data-date-time'].strip() # 공백 처리
  elif date_element :
    date = date_element.text.strip()
  else:
    date = "No Date Found"

  if media_element and 'title' in media_element.attrs: # 언론명 추출
    media = media_element['title'].strip() # 공백 처리
  elif media_element and 'alt' in media_element.attrs :
    media = media_element['alt'].strip() # 공백 처리
  else:
    media = "No Media Found"
  
  if content_element: #기사 내용 추출
    content = content_element.text.strip() # 공백 처리
    content = re.sub(r'[\r\n\t\"\'\,]', '', content) #불필요한 문자 제거
  else:
    content = "No Content Found"
    
  print(title, URL) 
  return (title, remove_time_prefix(date), media, email_reg(content))

#뉴스 리스트 들고 오기
def get_news_list(keyword, toDate, fromDate) :
    news = []
    #뉴스 리스트 페이지
    for date in pd.date_range(toDate, fromDate) : #수집 날짜 설정
      str_d = date.strftime("%Y.%m.%d") # 날짜 형식 
      page = 1 # 1 페이지부터 가져오기
      while True:
        start = (page-1) * 10 + 1 # 마지막 페이지까지 
        print(page)
        #네이버 뉴스 검색을 위한 매개변수들을 조합하여 생성한 쿼리 문자열로 해당하는 날짜, 키워드, 페이지 값 넣음
        URL = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query='+ keyword 
        + '&sort=1&photo=0&field=0&pd=3&ds='+str_d+'&de='+str_d 
        +'&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from'  
        + str_d.replace(".","")+'to'+str_d.replace(".","")+',a:all&start='+str(start) 
        print(URL)
        # URL을 사용하여 HTTP GET 요청을 보내고 응답
        res = requests.get(URL,headers = headers)
        # BeautifulSoup을 이용하여 파싱
        soup = BeautifulSoup(res.text, "html.parser")

        # 해당하는 페이지에 검색할 페이지가 없는 경우
        if soup.select_one("div.not_found02"):
          print("크롤링 끝")
          break
        
        #<ul> 중 클래스 이름이 list_news인 것을 찾고, 모든 <li> 요소를 선택
        news_list = soup.select("ul.list_news li")
        #뉴스 목록 중에 a태그의 href 속성을 추출하여 해당 기사 url 얻음
        for item in news_list :
          if len(item.select("div.info_group a")) == 2 :
            news.append(get_news(item.select("div.info_group a")[1]['href']))
        page += 1 # 다음페이지로
        #get_news로 가져온 뉴스 데이터를 데이터프레임(제목, 날짜, 신문사, 내용)으로 저장
    return pd.DataFrame(news, columns=['title','date','media','content'])
    #return news

# 원하는 키워드, 검색 날짜
keyword = "빅데이터"
toDate = "2025.10.01"
fromDate = "2025.10.08"

rows = get_news_list(keyword, toDate, fromDate)

#data 폴더에 csv로 파일 저장
rows.to_csv('D:/knou/PythonDataProcessing/Midterm/webscraping_2510.csv', encoding='utf-8-sig')