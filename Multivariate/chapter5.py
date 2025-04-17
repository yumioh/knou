import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import pairwise_distances
from sklearn.manifold import MDS

# 데이터 읽기
auto = pd.read_csv("D:/knou/Multivariate/data/auto.csv")
auto.head()

# 변수 선택
X = auto.iloc[:, 1:]
# 각 케이스 이름
autoName = auto["autoName"]
autoName = list(autoName)

# z-표준화
zX = StandardScaler().fit_transform(X)
# 0-1 변환
scaler = MinMaxScaler()
z01X = scaler.fit_transform(X)

# 거리행렬 구하기 : 거리 행렬(Distance Matrix)"이란, 여러 개의 점들(또는 객체) 사이의 쌍(pairwise) 거리(distance)를 행렬 형태로 정리한 것
z01X_dist = pairwise_distances(z01X, metric='euclidean')
print(z01X_dist.shape)

# MDS 실행
cmds = MDS(n_components=2, random_state=0, dissimilarity='precomputed')
mds1 = cmds.fit(z01X_dist)
mds1_coords = cmds.fit_transform(z01X_dist)
print(mds1_coords)

# 그림 그리기
plt.figure()
plt.scatter(mds1_coords[:,0], mds1_coords[:,1], facecolors='none', edgecolors='none')
labels = autoName

# MDS 각 케이스에 라벨 붙이기
for label, x, y in zip (labels, mds1_coords[:,0], mds1_coords[:,1]) :
 plt.annotate(label, (x,y), xycoords='data')
 
plt.xlabel('First dimension')
plt.ylabel('Second dimension')
plt.title('Metric MDS')
plt.show()