import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


'''
3) 인사이트 도출 및 시각화
 - 시간대별 평균 승하차 패턴
'''

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' 

#데이터 로드 
subway_df = pd.read_csv("D:/knou/PythonDataProcessing/Midterm/subway_final.csv", index_col=0)
subway_df = subway_df.reset_index()
print(subway_df.head())


# -----------시간대별 평균 승하차 패턴 시각화---------------
# 오전 8-9시 사이 하차 인원이 급증하고, 
# 오후 6-7시 사이 승차 인원이 급증하는 뚜렷한 패턴을 통해 성수역이 전형적인 업무 지구의 특성을 보임을 확인

# 시간대와 구분을 기준으로 평균 인원수 계산
hourly_pattern = subway_df.groupby(['시간대', '구분'])['인원수'].mean().reset_index()

# 시각화
plt.figure(figsize=(10, 6))
sns.lineplot(data=hourly_pattern, x='시간대', y='인원수', hue='구분', marker='o') 

plt.title('성수역 시간대별 평균 승하차 패턴', fontsize=18, pad=20)
plt.xlabel('시간대', fontsize=12)
plt.ylabel('평균 인원수', fontsize=12)
plt.xticks(rotation=45, ha='right') # x축 라벨 45도 회전
plt.grid(True) # 그리드 표시
plt.legend(title='구분', loc='upper left') # 범례 표시
plt.tight_layout()
plt.show()


# -----------지난 5년간 성수역 유동 인구 변화---------------
# 2020년 이후 매년 유동인구가 증가하며, 2024년에 30,998,599명으로 2020년 대비 약 68%로 증가함을 보여줌

# 연도를 기준으로 데이터를 그룹화하여 각 연도의 인원수를 모두 더함
yearly_total = subway_df.groupby('연도')['인원수'].sum().reset_index()

# 시각화
plt.figure(figsize=(10, 6))

# 막대그래프 그리기 x축 연도, y축은 인원
barplot = sns.barplot(data=yearly_total, x='연도', y='인원수', palette='viridis')

# 막대 위에 숫자 표시
# barplot.patches는 그래프의 각 막대 객체를 의미
for p in barplot.patches:
    barplot.annotate(f'{int(p.get_height()):,}', # 막대 높이
                     (p.get_x() + p.get_width() / 2., p.get_height()),  #텍스트 위치
                     ha = 'center', va = 'center', # 텍스트 중앙 정렬
                     xytext = (0, 9), # 텍스트 오프셋: 지정된 위치에서 y축 방향으로 9포인트만큼 위로 이동시켜 막대와 겹치지 않게 방지
                     textcoords = 'offset points')

plt.title('지난 5년간 성수역 연도별 총 이용객 변화', fontsize=16, pad=20)
plt.xlabel('연도', fontsize=12)
plt.ylabel('총 이용객 수 (명)', fontsize=12)
plt.ylim(0, yearly_total['인원수'].max() * 1.1) # y축에 여유 공간 주기
plt.show()


# -----------월별 평균 이용객 변화 ---------------
#  5월(봄)과 10월(가을)에 이용객 수가 다른 달에 비해 높게 나타나는 경향을 보임
# 이는 날씨가 좋은 계절에 인근의 '서울숲'이나 성수동의 다양한 팝업 스토어, 카페 등을 찾는 방문객이 증가하기 때문

# '연도'와 '월'을 기준으로 그룹화하여 월별 총 인원수 계산
yearly_monthly_total = subway_df.groupby(['연도', '월'])['인원수'].sum().reset_index()

# 결과 확인
# print(yearly_monthly_total.head())

# seaborn을 이용한 꺾은선 그래프 시각화
plt.figure(figsize=(14, 7))
plt.xticks(range(1, 13)) # x축 눈금을 모두 

# 'hue' 옵션에 '연도'를 지정하여 연도별로 다른 색상의 선을 그립니다.
sns.lineplot(
    data=yearly_monthly_total, 
    x='월', 
    y='인원수', 
    hue='연도', # 연도별로 선 색상 구분
    palette='colorblind', # 색상 팔레트 지정
    marker='o'
)

# 그래프 제목 및 라벨 설정
plt.title('성수역 연도별 월별 이용객 변화 추이', fontsize=16)
plt.xlabel('월', fontsize=12)
plt.ylabel('총 이용객 수 (단위: 백만 명)', fontsize=12)
plt.grid(True)
plt.legend(title='연도' , loc='upper left')
plt.show()
