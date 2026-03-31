import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 깨짐 방지 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

weather_df = pd.read_csv(f'./PythonDataProcessing/Midterm_2/data/weather_data_gwangjin_preprocessing.csv')

plt.figure(figsize=(12, 6)) # 그래프 크기 설정

# 시계열 그래프 그리기
sns.lineplot(data=weather_df, x='msurDt', y='pm10Value', marker='o', label='미세먼지(PM10)')
sns.lineplot(data=weather_df, x='msurDt', y='pm25Value', marker='s', label='초미세먼지(PM2.5)')

plt.title('광진구 대기질 시간별 변동 추이')
plt.xlabel('측정 날짜')
plt.ylabel('농도 (㎍/㎥)')
plt.xticks(rotation=45) # 날짜 겹침 방지를 위해 45도 회전
plt.legend() # 범례 표시
plt.grid(True, linestyle='--', alpha=0.6) # 격자 추가
plt.show()