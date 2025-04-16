auto = read.csv("D:/knou/Multivariate/data/auto.csv")
head(auto)

#1. 표준화 변수 만들기 
X = auto[,-1]
autoName = auto[,1]

# z-표준화 => 평균 0, 표준편차 1로 변환
# 각 열의 평균을 빼서 중심 0으로 이동
# scale =True : 각 열을 표준편차로 나눔 (분산 1)
zX = scale(X, center=TRUE, scale=TRUE)

# 0-1 Transformation
# 1이면 행단위, 2이면 열단위로 연산 => 각 열에서 최대/최소값을 계산
maxX = apply(X,2,max)
minX = apply(X,2,min)

# 0-1변환 변수로 최소값이 0 최대값이 1로 변환된 변수 => 스케일을 동일하게 맞추기 위함 
z01X = scale(X, center=minX, scale=maxX - minX)

# Z-표준화는 "이 값이 평균에서 얼마나 떨어졌는가?"를 보는 정규성 기반의 정규화
# 0-1 정규화는 "이 값이 전체 범위에서 어디쯤 위치했는가?"를 보는 절대적인 위치 기준의 정규화

#2. 거리행렬 만들기 

# dist : 관측치 간의 거리 행렬을 계산
z01_dist = dist(z01X, method = "euclidean")
z01_dist = as.matrix(z01_dist)
colnames(z01_dist) = autoName
rownames(z01_dist) = autoName
z01_dist

#3. cmdscale 실행
# cmdscale: 거리행렬을 입력 받아 좌표 형태로 배치하는 기법 k는 차수
mds1 = cmdscale(z01_dist, k=2)
plot(mds1[,1], mds1[,2], type='n', xlab='', ylab='', main='cmdscale(Auto)')
text(mds1[,1], mds1[,2], rownames(z01_dist), cex=0.9)
abline(h=0, v=0, lty=2)

install.packages("smacof")
library(smacof)

# mdf: 다차원척도법 수행
mds2 = mds(z01_dist, ndim=2)
names(mds2)

plot(mds2$conf[,1], mds2$conf[,2], type='n', xlab='', ylab='', main="smacof(Auto)")
text(mds2$conf[,1], mds2$conf[,2], rownames(z01_dist), cex=0.9)
abline(h=0, v=0, lty=2)

# mds로 원래 거리 행렬과과 저차원에 재구성된 좌표로부터 계산한 거리 행렬 사이의 불일치 정도 
# 0 에 가까울수록 원래 거리 구조를 잘 보존 0.05 이하면 매우 휼륭함
mds2$stress


#스크리그림 그리기 => 2개가 적당
mds2_1 = mds(z01_dist, ndim=1)
mds2_2 = mds(z01_dist, ndim=2)
mds2_3 = mds(z01_dist, ndim=3)
mds2_4 = mds(z01_dist, ndim=4)
stress = c(mds2_1$stress, mds2_2$stress, mds2_3$stress, mds2_4$stress)
plot(stress, type="l")
points(stress, cex=0.9)


