import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from factor_analyzer import FactorAnalyzer

med = pd.read_csv("D:\knou\Multivariate\data\medFactor.csv")
#print(med)

# 요약 통계량
#print(med.describe())

# 초기인자분석 : 회전없이 요인 분석 varimax, promax 자주 사용
fa = FactorAnalyzer(rotation=None)
#help(FactorAnalyzer)
fa.fit(med) # med 데이터 모델 적합

#고유값 및 분산 반환 : 데이터의 분산을 얼마나 설명하는지 나타냄
ev, v = fa.get_eigenvalues() 
#print(ev)

plt.scatter(range(1, len(ev)+1), ev)
plt.plot(range(1, len(ev)+1), ev)
plt.title('Scree Plot')
plt.xlabel('Factors')
plt.ylabel('Eigenvalue')
plt.grid()
#plt.show()

#인자수를 3개로 한 인자 분석 : 회전 varimax, pricipal 요인 추출 방식(주성분법)
fa_varimax = FactorAnalyzer(n_factors=3, rotation="varimax", method="principal")
fa_varimax.fit(med)
#print(fa_varimax.loadings_)

#인자공통성
#print(fa_varimax.get_communalities())

#인자분석
#print(fa_varimax.get_factor_variance())

#인자수를 3개로 한 인자 분석 : 회전 oblimin, pricipal 요인 추출 방식(주성분법)
fa_oblimin = FactorAnalyzer(n_factors=3, rotation="oblimin", method="principal")
fa_oblimin.fit(med)
print(fa_oblimin.loadings_)

#인자공통성
print(fa_oblimin.get_communalities())

#인자분석
print(fa_oblimin.get_factor_variance())

