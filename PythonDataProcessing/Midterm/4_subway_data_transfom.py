import pandas as pd
import glob

'''
2) Transform & Load : 데이터 변환 및 데이터 적재
'''

# CSV로 저장한 데이터를 합치기 
file_path = "D:/knou/PythonDataProcessing/Midterm/"
all_files = glob.glob(file_path + "seoul_subway_on_*.csv")

# 모든 파일을 순서대로 읽어와 하나의 리스트에 담기 
data = [] 
for filename in all_files :
    df = pd.read_csv(filename, index_col=0, header=0)
    data.append(df)

# 리스트에 담긴 모든 데이터프레임을 하나로 합치기
total_df = pd.concat(data, axis=0, ignore_index=True)

# 108건
print(f"총 데이터 건수: {len(total_df)}건")
print(total_df.head())

# 데이터 요약 및 결측치 확인
print(total_df.info())
print(total_df.isnull().sum())

# '사용월' 컬럼에 값이 없는 (NaN) 행을 모두 제거
total_df.dropna(subset=['사용월'], inplace=True)
# 사용월에 float64 타입이라 소수점을 제거하고 string 타입으로 변경
total_df['사용월'] = total_df['사용월'].astype('int64')
total_df['사용월'] = total_df['사용월'].astype('str')

# print(total_df.info())
print(total_df.head())

# 승하차와 시간대별 구분하기 만들기
# 기준이 될 컬럼 지정
id_vars = ['사용월', '호선명', '역명']

# 시간대별 컬럼들을 지정
value_vars = ['04-05시 승차', '04-05시 하차', '05-06시 승차', '05-06시 하차', '06-07시 승차', '06-07시 하차', '08-09시 승차', '08-09시 하차',
              '09-10시 승차', '09-10시 하차', '10-11시 승차', '10-11시 하차', '11-12시 승차', '11-12시 하차', '12-13시 승차', '12-13시 하차',
              '13-14시 승차', '13-14시 하차', '14-15시 승차', '14-15시 하차', '15-16시 승차', '15-16시 하차', '16-17시 승차', '16-17시 하차',
              '17-18시 승차', '17-18시 하차', '18-19시 승차', '18-19시 하차', '19-20시 승차', '19-20시 하차', '20-21시 승차', '20-21시 하차',
              '21-22시 승차', '21-22시 하차', '22-23시 승차', '22-23시 하차', '23-24시 승차', '23-24시 하차', '00-01시 승차', '00-01시 하차',
              '01-02시 하차', '01-02시 승차']

# pd.melt() 함수로 데이터 구조 변경
df_melt = pd.melt(total_df, id_vars=id_vars, value_vars=value_vars,
                  var_name='시간대_구분', value_name='인원수')

# '시간대'와 '승하차' 컬럼을 분리
df_melt['시간대'] = df_melt['시간대_구분'].str.slice(0, 5) # '04-05시'
df_melt['구분'] = df_melt['시간대_구분'].str.slice(6, 9)  # '승차' 또는 '하차'

# 연도별, 월별 분석을 위해 '연도'와 '월' 컬럼을 추가
df_melt['연도'] = df_melt['사용월'].str[:4]
df_melt['월'] = df_melt['사용월'].str[4:]

# 불필요한 '시간대_구분' 컬럼을 삭제
df_final = df_melt.drop(columns=['시간대_구분'])

print(df_final.head())
print(df_final.isnull().sum())

# 데이터 적재 : 호선명과 역명을 제외한 나머지 컬럼만 저장
df_final[['연도','월','시간대','인원수','구분']].to_csv('D:/knou/PythonDataProcessing/Midterm/subway_final.csv', encoding='utf-8-sig', index=False)