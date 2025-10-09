import requests
from bs4 import BeautifulSoup
import pandas as pd

# API 정보 설정 : 2호선 뚝섬역 2025년 1월~9월 데이터 수집
api_key = "4678496e6d696f763132365a6f70475a"
subway_line = "2호선"
subway_stn = "뚝섬"

# 수집한 모든 데이터를 저장할 빈 리스트 생성
all_data = []

for month in range(1, 10) :
    # subway_date를 매월 새로 생성 
    # month를 두자리 숫자로 만들기 위해 포맷칭 사용
    subway_date = f'2025{month:02d}'
    
    # 1회 호출시 최대 1000건까지 가능
    url = f'http://openapi.seoul.go.kr:8088/{api_key}/xml/CardSubwayTime/1/1000/{subway_date}/{subway_line}/{subway_stn}'
    
    print(f"------ {subway_date} 데이터 수집 시작 --------")

    # requests 라이브러리를 이용해 API 호출
    response = requests.get(url)

    if response.status_code == 200 :
        soup = BeautifulSoup(response.content, "xml")
    
        # 각 월의 데이터를 한 줄씩 추출
        rows = soup.find_all("row")
        
         # 추출한 데이터를 딕셔너리 형태로 만들어 all_data 리스트에 추가
        for row in rows:
            data = {
                '사용월': row.find('USE_MM').text,
                '호선명': row.find('SBWY_ROUT_LN_NM').text,
                '역명': row.find('STTN').text,
                '04-05시 승차': int(row.find('HR_4_GET_ON_NOPE').text),
                '04-05시 하차': int(row.find('HR_4_GET_OFF_NOPE').text),
                '05-06시 승차': int(row.find('HR_5_GET_ON_NOPE').text),
                '05-06시 하차': int(row.find('HR_5_GET_OFF_NOPE').text),
                '06-07시 승차': int(row.find('HR_6_GET_ON_NOPE').text),
                '06-07시 하차': int(row.find('HR_6_GET_OFF_NOPE').text),
                '07-08시 승차': int(row.find('HR_7_GET_ON_NOPE').text),
                '07-08시 하차': int(row.find('HR_7_GET_OFF_NOPE').text),
                '08-09시 승차': int(row.find('HR_8_GET_ON_NOPE').text),
                '08-09시 하차': int(row.find('HR_8_GET_OFF_NOPE').text),
                '09-10시 승차': int(row.find('HR_9_GET_ON_NOPE').text),
                '09-10시 하차': int(row.find('HR_9_GET_OFF_NOPE').text),
                '10-11시 승차': int(row.find('HR_10_GET_ON_NOPE').text),
                '10-11시 하차': int(row.find('HR_10_GET_OFF_NOPE').text),
                '11-12시 승차': int(row.find('HR_11_GET_ON_NOPE').text),
                '11-12시 하차': int(row.find('HR_11_GET_OFF_NOPE').text),
                '12-13시 승차': int(row.find('HR_12_GET_ON_NOPE').text),
                '12-13시 하차': int(row.find('HR_12_GET_OFF_NOPE').text),
                '13-14시 승차': int(row.find('HR_13_GET_ON_NOPE').text),
                '13-14시 하차': int(row.find('HR_13_GET_OFF_NOPE').text),
                '14-15시 승차': int(row.find('HR_14_GET_ON_NOPE').text),
                '14-15시 하차': int(row.find('HR_14_GET_OFF_NOPE').text),
                '15-16시 승차': int(row.find('HR_15_GET_ON_NOPE').text),
                '15-16시 하차': int(row.find('HR_15_GET_OFF_NOPE').text),
                '16-17시 승차': int(row.find('HR_16_GET_ON_NOPE').text),
                '16-17시 하차': int(row.find('HR_16_GET_OFF_NOPE').text),
                '17-18시 승차': int(row.find('HR_17_GET_ON_NOPE').text),
                '17-18시 하차': int(row.find('HR_17_GET_OFF_NOPE').text),
                '18-19시 승차': int(row.find('HR_18_GET_ON_NOPE').text),
                '18-19시 하차': int(row.find('HR_18_GET_OFF_NOPE').text),
                '19-20시 승차': int(row.find('HR_19_GET_ON_NOPE').text),
                '19-20시 하차': int(row.find('HR_19_GET_OFF_NOPE').text),
                '20-21시 승차': int(row.find('HR_20_GET_ON_NOPE').text),
                '20-21시 하차': int(row.find('HR_20_GET_OFF_NOPE').text),
                '21-22시 승차': int(row.find('HR_21_GET_ON_NOPE').text),
                '21-22시 하차': int(row.find('HR_21_GET_OFF_NOPE').text),
                '22-23시 승차': int(row.find('HR_22_GET_ON_NOPE').text),
                '22-23시 하차': int(row.find('HR_22_GET_OFF_NOPE').text),
                '23-24시 승차': int(row.find('HR_23_GET_ON_NOPE').text),
                '23-24시 하차': int(row.find('HR_23_GET_OFF_NOPE').text),
                '00-01시 승차': int(row.find('HR_0_GET_ON_NOPE').text),
                '00-01시 하차': int(row.find('HR_0_GET_OFF_NOPE').text),
                '01-02시 승차': int(row.find('HR_1_GET_ON_NOPE').text),
                '01-02시 하차': int(row.find('HR_1_GET_OFF_NOPE').text)
            }
            
            # 해당 데이터 저장
            all_data.append(data)
            
        print(f"성공: {len(rows)}건 수집 완료")       
    else:
        print(f"실패: {subway_date} 데이터 수집 중 오류 발생 (상태 코드: {response.status_code})")

#--- 수집 완료 후 데이터프레임으로 변환 ---
df = pd.DataFrame(all_data)

# 결과 확인
print("\n--- 최종 수집 결과 (상위 5개) ---")
print(df.head())
print(f"\n총 {len(df)}건의 데이터가 수집되었습니다.")