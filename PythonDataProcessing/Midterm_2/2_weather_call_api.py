import os
from dotenv import load_dotenv
import pandas as pd
import requests
import datetime as dt

load_dotenv()

api_key = os.getenv('PUBLIC_API_KEY')

## 시군구별 실시간 평균정보 조회 
## 디코딩된 키값을 사용하여 API 호출
url = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getMsrstnAcctoRDyrg'


# 모든 데이터를 담을 리스트
all_items = []

i = 1

while True:
    # PARAMS 설정
    params = {
        'serviceKey': api_key,
        'pageNo': i,
        'numOfRows': 100,
        'inqBginDt' : '20251101',
        'inqEndDt': '20260229',
        'msrstnName' : '광진구',
        'returnType': 'JSON'
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
if all_items:
    df = pd.DataFrame(all_items)
    # 폴더가 존재하는지 확인 후 저장 (없으면 에러 방지용)
    save_path = './PythonDataProcessing/Midterm_2/data/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    df.to_csv(f'{save_path}weather_data_gwangjin.csv', index=False, encoding='utf-8-sig')
    print("CSV 저장 완료!")