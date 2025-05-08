data7 = read.csv("D:/knou/Multivariate/data/data7-1.csv")
data7_g1 = data7[data7$group=='g1', -1] #1열을 제외하고 g1인 행만 선택
data7_g2 = data7[data7$group=='g2', -1] #1열을 제외하고 g2인 행만 선택

head(data7_g1,2)

g1_mean = sapply(data7_g1, mean) # 각 열에 대한 평균값 구함
g2_mean = sapply(data7_g2, mean)
g1_mean
g2_mean

n1 = nrow(data7_g1) #행의 개수
n2 = nrow(data7_g1)

cov_g1 = cov(data7_g1)
cov_g2 = cov(data7_g2)

cov_g1 # 공분산의 행렬
cov_g2 

# 두 그룹을 통합한 공분산행렬 : 샘플 수를 고려해서 가중 평균을 내야하여 자유도 조정이 들어감
cov_g = ((n1-1)*cov_g1 + (n2-1)*cov_g2) / (n1+n2-2)

# g의 공분산의 역행렬
# 두급룹의 평균 벡터 차이 (중심 간 거리 벡터)
b = solve(cov_g) %*% (g2_mean - g1_mean)

y1_mean = g1_mean %*% b
y2_mean = g2_mean %*% b

# 두 그룹 평균의 중간값(분류의 기준)
yc = (y1_mean + y2_mean)/2

case1 = data7_g1[1,]
case1 = as.matrix(case1)

# y1 > yc이므로 g2로 판별 
y1 = case1 %*% b



