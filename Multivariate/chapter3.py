import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 데이터 불려오기 
deug = pd.read_csv("D:/knou/Multivariate/data/deug.csv", index_col=False)
deug = deug.iloc[:, 1:] # unnamed 삭제하기 위해

# 1. 9개 변수들을 기술통계량으로 요약하라 
#print(round(deug.describe(),2))

# 2.9개의 변수들 사이의 상관계수행렬을 구하라
cor_matrix = deug.corr()
#print(cor_matrix)

# 3. 고윳값을 구하고, 그 고윳값이 확보하는 정보의 양 및 누적정보의 양을 구하라 
# 변수 표준화 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(deug)

# PCA 실행
pca = PCA()
pca.fit(X_scaled)

# 고윳값 구하기
eigenvalues = pca.explained_variance_
#print("고윳값:\n", eigenvalues)

# 5. 각 고윳값이 설명하는 정보의 양 (설명력)
explained_var = pca.explained_variance_ratio_
#print("\n설명력 (정보의 양):\n", explained_var)

# 6. 누적 설명력
cumulative_var = np.cumsum(explained_var)
#print("\n누적 설명력:\n", cumulative_var)


# 4. 1보다 큰 고윳값의 수와 그 고윳값들이 확보하는 누적정보의 양을 구하라 
# 고윳값의 수
num_ev = sum(ev > 1 for ev in eigenvalues)
#print("1보다 큰 고윳값의 수",num_ev)

#누적정보의 양
cum = sum(explained_var[:num_ev])
#print("누적정보의 양", cum)

# 5. sceeplot을 그리고 해석하라
# 주성분 번호를 맞춰주기 위함
components = np.arange(1, len(eigenvalues) + 1)
plt.title("Scree Plot")
plt.xlabel('Components')
plt.ylabel('Explained Variance')
plt.plot(components, eigenvalues, marker='o', linestyle='-', color='blue')
plt.xticks(components)
plt.grid(True)
#plt.show()


# 6. 위 결과를 이용하여 주성분을 구하라 
# 3개의 주성분만 추출
pca_6 = PCA(n_components=3)
pca_deug = pca_6.fit_transform(X_scaled)

# 주성분분산 (고윳값)
print("고윳값:", pca_6.explained_variance_)

# 주성분분산 비율
print("설명력:", pca_6.explained_variance_ratio_)

# 주성분분산계수 : 로딩
print("주성분 구성:")
print(np.round(pca_6.components_, 3)) 

# 주성분점수
print("주성분 점수:")
print(pca_deug[0:5, :])

# 7. biplot을 그려보고 주성분 특징을 정리하라 
X = StandardScaler().fit_transform(deug)
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(X)

# biplot
plt.figure(figsize=(10, 7))
plt.scatter(principalComponents[:, 0], principalComponents[:, 1], alpha=0.6)
for i, var in enumerate(deug.columns):
    plt.arrow(0, 0, pca.components_[0, i]*3, pca.components_[1, i]*3,
              color='r', alpha=0.7, head_width=0.05)
    plt.text(pca.components_[0, i]*3.2, pca.components_[1, i]*3.2, var, color='r')

plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
plt.title("Biplot of PCA")
plt.grid()
plt.show()
