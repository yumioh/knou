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
            try:
                # 1. 기본 정보(사용월, 호선명, 역명)를 먼저 추가합니다.
                data = {
                    '사용월': row.find('USE_MM').text,
                    '호선명': row.find('SBWY_ROUT_LN_NM').text,
                    '역명': row.find('STTN').text,
                }

                # 2. API가 제공하는 시간 순서대로 리스트를 만듭니다. (4시~23시, 다음으로 0시~1시)
                hours = list(range(4, 24)) + list(range(0, 2))

                # 3. hours 리스트를 순회하며 시간대별 승하차 인원을 data 딕셔너리에 추가합니다.
                for hour in hours:
                    # 딕셔너리 키 생성 (예: '04-05시 승차')
                    ride_key = f'{hour:02d}-{(hour+1):02d}시 승차'
                    alight_key = f'{hour:02d}-{(hour+1):02d}시 하차'
                    
                    # XML 태그명 생성 (예: 'HR_4_GET_ON_NOPE')
                    ride_tag = f'HR_{hour}_GET_ON_NOPE'
                    alight_tag = f'HR_{hour}_GET_OFF_NOPE'
                    
                    # 생성된 키와 태그명을 이용해 데이터 추가
                    data[ride_key] = int(row.find(ride_tag).text)
                    data[alight_key] = int(row.find(alight_tag).text)
                
                # 4. 완성된 한 달치 데이터를 전체 리스트에 추가합니다.
                all_data.append(data)

            except Exception as e:
                print(f"데이터 처리 중 오류 발생: {e}, 해당 row를 건너뜁니다.")
                print(row)
                
#--- 수집 완료 후 데이터프레임으로 변환 ---
df = pd.DataFrame(all_data)

# 결과 확인
print("\n--- 최종 수집 결과 (상위 5개) ---")
print(df.head())
print(f"\n총 {len(df)}건의 데이터가 수집되었습니다.")