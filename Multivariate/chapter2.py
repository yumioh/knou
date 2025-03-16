import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

heptathlon = pd.read_csv("D:/knou/Multivariate/data/heptathlon.csv")
#print(heptathlon.head())
#print(heptathlon.columns)

#기술통계량 구하기 - 소수점 이하 2자리까지 반올림
round(heptathlon.describe(), 2)

# 변환 : 변수최대값 - 변수값
heptathlon.hurdles = np.max(heptathlon.hurdles) - heptathlon.hurdles
heptathlon.run200m = np.max(heptathlon.run200m) - heptathlon.run200m
heptathlon.run800m = np.max(heptathlon.run800m) - heptathlon.run800m

#print(heptathlon.head())

# 분석변수 선택하기 
feature = ['hurdles', 'highjump', 'shot', 'run200m', 'longjump', 'javelin', 'run800m']
hep_data = heptathlon[feature]


# 파이썬에서 PCA 분석을 하기 전에 데이터를 표준화(Z-score 정규화)
# StandardScaler()는 각 열(변수)을 평균 0, 표준 편차 1로 변환하는 역할
x = StandardScaler().fit_transform(hep_data)

# 주성분분석
# PCA : 사이킷런(Scikit-learn)에서 제공하는 주성분 분석(PCA) 함수
# 주성분 개수를 hep_data의 전체 열 개수로 설정
pca_init = PCA(n_components=len(hep_data.columns))
pca_init.fit(x)


# 스크리 그림 그리기 
# explained_variance_는 각 주성분(PC)이 설명하는 실제 분산 크기를 반환
# '-o' :  각 주성분의 설명된 분산 크기를 선과 점으로 시각화
plt.title("scree plot")
plt.xlabel("component")
plt.ylabel("explained variance")
plt.plot(pca_init.explained_variance_, '-o') 
plt.show()

# 파이썬 주성분분석

# 주성분의 수를 2개로 하여 주성분 실행
pca = PCA(n_components=2)
# pca 속성 확인
print(dir(pca))
# fit_transform : 원래 데이터를 PCA를 이용해 새로운 좌표(주성분 점수)로 변환하는 과정
hep_pca = pca.fit_transform(x)


#주성분분석
# 데이터의 변동성을 나타냄 => 값이 높을수록 설명력이 높음
# [4.64611996 1.24408391]
print(pca.explained_variance_)

# 주성분분산 비율 
# 데이터의 변동성에서 차지하는 비율 
# [0.63718217 0.17061722] => PC1, PC2가 데이터의 약 80%를 설명
print(pca.explained_variance_ratio_)

# 주성분계수
# 각 원래 변수가 PC1, PC2를 구성하는 정도(가중치)
# PC1 : Longjump (-0.4562), hurdles (-0.4529), run200m (-0.4079)가 PC1에 크게 기여 => 주로 점프 달리기 
# PC2 : javelin (0.8417)이 매우 큰 값 → PC2는 창던지기(javelin) 특성을 주로 반영
print(np.round(pca.components_),3)


# 주성분 점수
# 각 데이터(선수)가 주성분(PC) 공간에서 어디에 위치하는지 나타냄
# 선수1 : -4.2064 → PC1(스피드 & 점프 능력)에서 낮은 점수
# 선수2 : C1에서 낮은 값 → 스피드 & 점프 능력 낮음
# 선수5 : PC2의 값이 크므로 투척능 력이 높은 선수
print(hep_pca[0:5,])

# PCA의 고유벡터는 임의적으로 결정될 수 있음. 부호는 영향을 미치지 않고 계수의 크기와 상대적 패턴이 중요