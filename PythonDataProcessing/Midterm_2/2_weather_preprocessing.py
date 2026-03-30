import pandas as pd
import numpy as np

'''
2-2] 데이터 변환
 - 수치 데이터를 float 또는 int 형태로 변환
 - 해당 데이터는 시간이 없는 날짜 형태로 '주말/평일' 구분 컬럼 추가

'''

# 1. 데이터 불려오기
weather_df = pd.read_csv("./PythonDataProcessing/Midterm_2/data/weather_data_gwangjin.csv")
print('--- float 변경 전 데이터 정보 ---')
print(weather_df.info())

# 2. 수치형으로 변환할 컬럼 리스트 정의
numeric_cols = ['so2Value', 'coValue', 'pm10Value', 'no2Value', 'o3Value', 'pm25Value']

# 3. 데이터 타입 변환
for col in numeric_cols:
    # errors='coerce' 옵션은 숫자로 바꿀 수 없는 데이터를 NaN으로 처리
    weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')
print('--- float 변경 후 데이터 정보 ---')
print(weather_df.info())

# 4. 날짜 컬럼을 datetime 객체로 변환 
weather_df['msurDt'] = pd.to_datetime(weather_df['msurDt'])

# 2. 요일 정보 추출 
weather_df['weekday_num'] = weather_df['msurDt'].dt.weekday

# 3. 주말/평일 구분 파생 변수 생성
weather_df['day_type'] = np.where(weather_df['weekday_num'] >= 5, '주말', '평일')

# 4. 결과 확인 
print(weather_df[['msurDt', 'day_type']].head(10))

# 5. 실제 요일 이름 확인용 컬럼 추가
weather_df['day_name'] = weather_df['msurDt'].dt.day_name()

weather_df.to_csv(f'./PythonDataProcessing/Midterm_2/data/weather_data_gwangjin_preprocessing.csv', index=False, encoding='utf-8-sig')