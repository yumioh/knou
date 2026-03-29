import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

'''
문제1-2] 결측치 및 데이터 정제 
 - 요약문이 없는 기사를 찾고 처리 하기  => 요약문이 없는 기사 0개 
 - 특수문자나 불필요한 공백제거 전처리 
'''

# 저장한 데이터 들고 오기 
# 수집된 기사 개수 : 중앙화 137개 / 탈중앙화 102개
cex_news_df = pd.read_csv(f"./PythonDataProcessing/Midterm_2/data/newsscraping_26_중앙화.csv", index_col=0)
print(cex_news_df.head())
decex_news_df = pd.read_csv(f"./PythonDataProcessing/Midterm_2/data/newsscraping_26_탈중앙화.csv", index_col=0)
print(decex_news_df.head())

# content 컬럼의 값이 "None"인 행만 필터링
no_content_df = cex_news_df[cex_news_df['content'] == "None"]

# 결과 출력 : 내용이 없는 기사수는 모두 0개 
print(f"내용이 없는 기사 수 : {len(no_content_df)}개")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # 1. 한글, 영어, 숫자만 남기고 특수문자 제거
    text = re.sub(r'[^ \u3131-\u3163\uac00-\ud7a3a-zA-Z0-9]', ' ', text)
    # 2. 연속된 공백을 하나로 줄이고 앞뒤 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 중앙화 데이터 정제
cex_news_df['title'] = cex_news_df['title'].apply(clean_text)
cex_news_df['content'] = cex_news_df['content'].apply(clean_text)
# 정제된 데이터 csv 파일로 저장
cex_news_df.to_csv('./PythonDataProcessing/Midterm_2/data/clearning_중앙화.csv', encoding='utf-8-sig')

# 탈중앙화 데이터 정제
decex_news_df['title'] = decex_news_df['title'].apply(clean_text)
decex_news_df['content'] = decex_news_df['content'].apply(clean_text)
# 정제된 데이터 csv 파일로 저장
decex_news_df.to_csv('./PythonDataProcessing/Midterm_2/data/clearning_탈중앙화.csv', encoding='utf-8-sig')

'''
문제1-3] 비교 분석
 - 두 키워드간 언론사 분포 차이 
 - 제목에 등장하는 주요 단어 차이를 간단한 그래프나 표로 표현
'''

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 언론사별 개수 세기
cex_media = cex_news_df['media'].value_counts()
decex_media = decex_news_df['media'].value_counts()

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

sns.barplot(x=cex_media.values, y=cex_media.index, ax=axes[0], palette='Blues_r')
axes[0].set_title('중앙화 뉴스 언론사 Top 10')

sns.barplot(x=decex_media.values, y=decex_media.index, ax=axes[1], palette='Oranges_r')
axes[1].set_title('탈중앙화 뉴스 언론사 Top 10')

plt.tight_layout()
plt.show()

def get_top_words(df, column, n=10):
    words = ' '.join(df[column]).split()
    data = Counter([w for w in words if len(w) > 1]).most_common(n)
    return [x[0] for x in data], [x[1] for x in data]

c_w_labels, c_w_values = get_top_words(cex_news_df, 'title')
d_w_labels, d_w_values = get_top_words(decex_news_df, 'title')

fig2, axes2 = plt.subplots(1, 2, figsize=(15, 6))

sns.barplot(x=c_w_values, y=c_w_labels, ax=axes2[0], palette='Blues_r')
axes2[0].set_title('중앙화 뉴스 제목 키워드 Top 10')

sns.barplot(x=d_w_values, y=d_w_labels, ax=axes2[1], palette='Oranges_r')
axes2[1].set_title('탈중앙화 뉴스 제목 키워드 Top 10')

plt.tight_layout()
plt.show()