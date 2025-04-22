import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import CCA
import matplotlib.pyplot as plt
import seaborn as sns

sales = pd.read_csv("D:/knou/Multivariate/data/sales.csv")
print(sales.head(3))

# 기술통계량 
sales_desc = sales.iloc[:,1:].describe()
print(sales_desc)

# 표준편차 보기 
print(sales_desc.loc['std'])

# 변수군 선택
xlist = ['X1', 'X2', 'X3', 'X4']
ylist = ['Y1', 'Y2', 'Y3']

exam = sales[xlist]
perform = sales[ylist]

print(exam.head())
print(perform.head())

# zscore 표준화 방법1
scaler = StandardScaler()
zexam = scaler.fit_transform(exam)
zperform = scaler.fit_transform(perform)

# z-score 표준화 방법 2
X_mc = (exam - exam.mean()) / exam.std()
Y_mc = (perform - perform.mean()) / perform.std()

print(X_mc.head())
print(Y_mc.head())

# 정준상관분석 
# cca 모델 생성 : 최대 3개의 쌍으로 정렬된 선형 조합을 찾겠다는 의미
ca = CCA(n_components=3)
# 학습단계(상관성이 높은 선형 조합 계산)
ca.fit(exam, perform)
# 좌표계로 변환
X_c, Y_c = ca.transform(exam, perform)

# 정준상관점수 데이터프레임 만들기
cc_res = pd.DataFrame({"CCX_1":X_c[:,0],
 "CCY_1":Y_c[:,0],
 "CCX_2":X_c[:,1],
 "CCY_2":Y_c[:,1],
 "CCX_3":X_c[:,2],
 "CCY_3":Y_c[:,2]})

# 정준상관점수 보기
print(cc_res.head())

# 제1 정준상관계수 : X의 첫 번째 정준성분과 Y의 첫 번째 정준성분 간의 상관계수를 구함
print(np.corrcoef(X_c[:,0],Y_c[:,0]))
# 제2 정준상관계수
print(np.corrcoef(X_c[:,1],Y_c[:,1])[0,1])
# 제3 정준상관계수
print(np.corrcoef(X_c[:,2],Y_c[:,2])[0,1])

# 제1정준상관계수 산점도
sns.scatterplot(x="CCX_1", y="CCY_1", data=cc_res)
plt.title('corr = %.4f' %  np.corrcoef(X_c[:,0], Y_c[:,0])[0,1])
#plt.show()

# 정준상관계수 : 변수 4개, 정준성분 3개
print(ca.x_weights_)

# 정준상관계수 : 변수 4개, 정준성분 3개
print(ca.y_weights_)

# 정준상관점수 구하기
# CCX_1 in <Py 6.4> from zvalue in <Py 6.3> and x_weights_
# -0.5578*0.356-0.644*0.1468-0.729*0.2457-0.926*0.889
# Out[75]: -1.2954453
# CCY_1 in <Py 6.4> from zvalue in <Py 6.3> and y_weights_
# -0.795*0.7246-1.0149*0.379-1.063*0.575
# Out[76]: -1.5719291

