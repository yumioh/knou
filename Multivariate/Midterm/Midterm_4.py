import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from factor_analyzer import FactorAnalyzer

#데이터 불려오기 
df = pd.read_csv("D:/knou/Multivariate/data/favoritesujects.csv")
#print(df.head())

# subject 열 제외
subjects = df.drop(columns=["SUBJECT"], errors="ignore")

# 1. 유의한 인자 수와 그 인자들이 확보하는 정보의 양은 얼마인가?  
# 초기 인자 분석
fa = FactorAnalyzer(rotation=None)
fa.fit(subjects)

# 고윳값 구하기 
ev, v = fa.get_eigenvalues()
#print(ev)

# 고윳값 ≥ 1 인자 수
num_factors = np.sum(ev >= 1)
#print(f"\n유의한 인자 수 (고윳값 ≥ 1): {num_factors}")

# 설명력 
#print(f"\n 변수 설명력 : {fa.get_factor_variance()}")

# 2. 인자부하행렬을 구하고 varimax와 promax 방법을 이용하여 인자회전을 실시하고 결과를 비교하시오
fa_varimax = FactorAnalyzer(n_factors=2 ,rotation='varimax', method='principal')
fa_varimax.fit(subjects)

# 인자계수
# print("인자계수 : ", fa_varimax.loadings_)

# # 인자공통성
# print("인자공통성 : ", fa_varimax.get_communalities())

# # 인자고유분산 : t-분산
# print("인자고유분산 : t-분산 : ", fa_varimax.get_uniquenesses())

# # 인자분석
# print("인자분석 :", fa_varimax.get_factor_variance())

# 2. 인자부하행렬을 구하고 varimax와 promax 방법을 이용하여 인자회전을 실시하고 결과를 비교하시오
fa_promax = FactorAnalyzer(n_factors=2 ,rotation='promax', method='principal')
fa_promax.fit(subjects)

# # 인자계수
# print("인자계수 : ", fa_promax.loadings_)

# # 인자공통성
# print("인자공통성 : ", fa_promax.get_communalities())

# # 인자고유분산 : t-분산
# print("인자고유분산 : t-분산 : ", fa_promax.get_uniquenesses())

# # 인자분석
# print("인자분석 :", fa_promax.get_factor_variance())

# # 요인간 상관행렬
# print("요인간 상관행렬 :", fa_promax.structure_) 

# 3인자들에 적절한 이름 (Python 언어)