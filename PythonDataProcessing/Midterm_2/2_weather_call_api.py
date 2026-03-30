import os
from dotenv import load_dotenv
import pandas as pd
import requests
import datetime as dt

'''
문제2-1]  API를 활용하여 데이터 추출
수집 항목 : 공공데이터포털에서 한국환경공단_에어코리아_대기오염통계 현황에서 측정소별 실시간 일평균 정보 
수집 기간 : 2025-11-01 ~ 2026-02-28 (3개월치 데이터 제공)
지역 : 광진구
데이터 형태 : JSON

'''

load_dotenv()
api_key = os.getenv('PUBLIC_API_KEY')

## 시군구별 실시간 평균정보 조회 
## 디코딩된 키값을 사용하여 API 호출
url = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getMsrstnAcctoRDyrg'

all_items = []
i = 1 # 2페이지라 페이징 처리

while True:
    # PARAMS 설정
    params = {
        'serviceKey': api_key,
        'pageNo': i,
        'numOfRows': 100,
        'inqBginDt' : '20251101',
        'inqEndDt': '20260228',
        'msrstnName' : '광진구',
        'returnType': 'json'
    }
    
    try:
        res = requests.get(url, params=params)
        weather_data = res.json()
        
        header = weather_data['response']['header']
        body = weather_data['response'].get('body')
        print(body)
        
        # 1. API 응답 성공 여부 확인
        if header['resultCode'] != "00":
            print(f"API Error: {header['resultMsg']}")
            break
            
        items = body['items']
        
        # 2. 데이터가 더 이상 없으면 루프 종료
        if not items:
            print(f"데이터 수집 완료. 총 {i-1}페이지 수집됨.")
            break
            
        # 데이터 리스트에 추가
        all_items.extend(items)
        print(f"{i}페이지 수집 중...")
        
        # 3. 전체 데이터 개수와 현재까지 수집된 개수 비교 (선택 사항)
        if len(all_items) >= int(body['totalCount']):
            break
            
        i += 1
        
    except Exception as e:
        print(f"오류 발생: {e}")
        break

# 4. 수집된 모든 데이터를 하나의 DataFrame으로 합쳐서 저장
df = pd.DataFrame(all_items)    
df.to_csv(f'./PythonDataProcessing/Midterm_2/data/weather_data_gwangjin.csv', index=False, encoding='utf-8-sig')
