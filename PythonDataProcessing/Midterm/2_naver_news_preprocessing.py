import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt

'''
문제1-2] 간단한 데이터 분석 
 - 일자별 기사수 집계 
 - 언론사별 기사수 top 10
 - 제목에 가장 많이 등장한 단어 top 20 (불용어 제외)

'''

# 저장한 데이터 들고 오기 
naver_news_data = pd.read_csv("D:/knou/PythonDataProcessing/Midterm/webscraping_2510.csv", index_col=0)
print(naver_news_data.head())

# ================  일자별 기사수 집계 ================ 
# 날짜만 추출 (예: '2025.10.07. 오전 6:01' → '2025.10.07.')
naver_news_data['date_only'] = naver_news_data['date'].astype(str).str.extract(r'(\d{4}\.\d{2}\.\d{2}\.)')
daily_counts = naver_news_data['date_only'].value_counts().sort_index()
print('일자별 기사 개수')
print(daily_counts)

# ================  언론사별 기사 수 상위 10개 ================ 
top_press = naver_news_data['media'].value_counts().head(10)
print("언론사별 기사수 TOP 10:")
print(top_press)

press_top10= pd.DataFrame(top_press, columns=["media", "count"])

# ================  제목에 가장 많이 등장한 단어 top 20 ================ 
# 모든 제목 합치기
all_titles = " ".join(naver_news_data['title'].dropna())

# 특수문자 제거
clean_text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", all_titles)

# 공백기준으로 단어 나누기
words = clean_text.split()

# 불용어 목록
stopwords = {'기자','뉴스','속보','단독','인터뷰','영상','사진','출처','오늘','내일','지난','이번','관련','정부','국회','한국','대한','위해','올해', '차지', '3인', '덕분'}

# 불용어 제거
clean_words = [w for w in words if w not in stopwords and len(w) > 1]

# 단어 빈도수 계산
word_counts = Counter(clean_words)
top20 = word_counts.most_common(20)

print("제목에 가장 많이 등장한 단어 TOP 20:")
for w, c in top20:
    print(f"{w}: {c}")

df_top20 = pd.DataFrame(top20, columns=["word", "count"])

# =============== 결과 그래프 그리기 ===============

# 그래프 설정 (폰트 한글 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic' 

# 일자별 기사 수 
daily_count_df = daily_counts.reset_index()
daily_count_df.columns = ["date_only", "count"]

plt.figure(figsize=(8,4))
plt.bar(daily_count_df['date_only'], daily_count_df['count'], color='orange')
plt.title("일자별 기사 수")
plt.xlabel("날짜")
plt.ylabel("기사 개수")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# 언론사별 기사 수 상위 10개
top_press_df = top_press.reset_index()
top_press_df.columns = ["media", "count"]

plt.figure(figsize=(8,4))
plt.bar(top_press_df['media'], top_press_df['count'], color='violet')
plt.title("언론사별 기사 수 상위 10개")
plt.xlabel("언론사")
plt.ylabel("개수")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# 제목에 가장 많이 등장한 단어
plt.figure(figsize=(10,5))
plt.bar(df_top20['word'], df_top20['count'], color='skyblue')
plt.title("제목에 가장 많이 등장한 단어 TOP 20")
plt.xlabel("단어")
plt.ylabel("등장 횟수")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

