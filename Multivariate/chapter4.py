import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans

import os
os.environ["OMP_NUM_THREADS"] = "1"

beerbrand = pd.read_csv("d:/knou/Multivariate/data/beerbrand.csv", index_col='name')
#print(beerbrand.describe())

zbeer = StandardScaler().fit_transform(beerbrand)

# 계측적 군집 분석 시행하기 : 최단 연결법 
slink = sch.linkage(zbeer, 'single')
print(slink)

# 덴드로그램 그리기 
plt.figure(figsize=(7,5))
sch.dendrogram(slink, leaf_rotation=80, leaf_font_size=8, labels=beerbrand.index)
plt.title("Dendrogram of Single linkage")
#plt.show()

# 와드연결법 
wlink = sch.linkage(zbeer, "ward")
plt.figure(figsize=(7,5))
sch.dendrogram(wlink, leaf_rotation=80, leaf_font_size=8, labels=beerbrand.index)
plt.title("Dendrogram of Ward's linkage")
#plt.show()

# 계층적 군집분석 : 중심연결법
clink = sch.linkage(zbeer, "centroid")
plt.figure(figsize=(7,5))
sch.dendrogram(clink, leaf_rotation=80, leaf_font_size=8, labels=beerbrand.index)
plt.title("Dendrogram of centroid linkage")
#plt.show()

# 소속군집알기
# affinity='euclidean' 자동으로 사용 가능
wcluster = AgglomerativeClustering(n_clusters=4, linkage="ward")

memeber = wcluster.fit_predict(zbeer)
print(memeber)

# 군집별 평균 계산
member1 = pd.DataFrame(memeber, columns=['cluster'], index=beerbrand.index)
data_combined = beerbrand.join(member1)
data_com = data_combined.groupby('cluster').mean()

print(data_com)

# 파이썬 k-mean 군집 분석
# k-mean 군집 = 2개
zbeer = StandardScaler().fit_transform(beerbrand)
kmc = KMeans(n_clusters=2)
kmc.fit(zbeer)

# 군집 중심 알기
# 각 변수(calories, sodium, alcohol, cost)에 대한 평균값 => 표준화된 값으로 상대적 위치임
print(kmc.cluster_centers_)

# 소속 군비 알기 
print(kmc.labels_)

# 소속 군집 산점도 그리기 
plt.figure(figsize=(5,5))
plt.scatter(x=beerbrand['calories'], y=beerbrand['sodium'], c=kmc.labels_)
plt.show()