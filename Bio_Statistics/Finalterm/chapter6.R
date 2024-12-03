#제6장 선형회귀분석

#상관계수
# 분산 : 한변수의 평균값 중심으로 퍼져 있는 것을 의미 공분산 : 두 변수의 평균값 중심으로 퍼져있는 평균 거리
# 상관계수 : 산점돔에서 점들이 얼마나 직선에 가까운가 정도를 나타내는데 쓰이는 측도
# 1. 피어슨 상관계수 : n개의 임의표본을 추출하여 얻은 x,y의 표본 상관계수 r를 사용하여, 모 상관계수 p를 추정
# - -1 <= r <= 1 : 
# - 표본 데이터를 산점도로 나타냈을 때, 모든 점이 정확히 한 직선 위에 위치하면  r은 1또는 -1
# - x,y의 측정 단위가 바뀌어도 r의 값은 바뀌지 않는다. = scale free
# - 특이점의 영향을 많이 받음
# - 표본 피어슨 상관계수는 직선 1개로 설명할 수 있는 선형관계만 나타님 

# 2. 스피어맨 상관계수 : 두 변수의 순위 사이의 통계적 의존성을 측정하는 비모수적 척도. 각 변수에 대해 순위를 매긴 값을 기반으로 상관관계를 측정 
# => 순서형 변수인 경우에도 용이. 두 변수간의 관계가 단조 함수로 얼마나 설명될 수 있는지 측정. 
# x=y, f(x) <= f(y) 증가. x>y f(x)>=f(y) : 감소함수
# - x,y의 측정 단위를 바꾸어도 r값은 바뀌지 않는다 => scael-free
# - 피어슨 상관계수에 비해 특이점의 영향을 덜 받음


setwd("C:/workplace/knou/Bio_Statistics/Finalterm")
data <- read.csv("./data/biostat_ex_data.csv")
data.head()
library(dplyr)
data3 <- data0 %>% mutate_at(vars(sex, Recur, stage, smoking, obesity, Recur_1y, post.CA19.9.binary, post.CA19.9.3grp), as.factor) %>% 
mutate(HTN=as.factor(ifelse(SBP>-140, 1, 0)), CEA.grp=as.factor(ifelse(CEA>5, 1,0)), post.CEA.grp=as.factor(ifelse(post.CEA>5,1,0)))

library(ggplot2)
ggplot(data3) + geom_point(aes(age, SBP))
cor(data3$age, data3$SBP)
cor(data3$age, data3$SBP, method="spearman")

#수술 전후 데이터 

ggplot(data3) + geom_point(aes(log(CEA), log(post.CEA)))
cor(log(data3$CEA), log(data3$post.CEA))
cor(data3$CEA, data3$post.CEA, method="spearman")

#2. 단순 선형 회귀 분석 
# 독립변수 x, 반응변수(종속, 결과)로 설정하여 두 변수 간의 함수적 관계를 알아보는 것을 회귀 분석

# 단순선형회귀 : 독립변수가 1개인 경우에 사용.
# 최소제곱법 : 오차를 최소화 시키는 방법으로 회귀계수(b0,b1)를 추정하는 기법 => 오차의 제곱의 합이 최소가 되는 b0,b1을 찾는 것이 목적

data4 <- data3 %>% mutate(log.CEA=log(CEA), log.post.CEA=log(post.CEA))
obj <- lm(log.post.CEA~log.CEA, data=data4)
summary(obj)

ggplot(data4, aes(log.CEA, log.post.CEA)) + geom_point() + geom_smooth(method = "lm")

data.new <- data.frame(log.CEA=c(1,2,3))
#독립변수가 특정한 값을 가질때 회귀직선이 추정하는 반응변수의 값을 계산할때
#회구분석의 결과를 저장하는 객체를 넣음
predict(obj, newdata=data.new)

#회귀직선이 예측하는 반응변수의 값과 실제 반응변수의 관측값이 가까우면 가까울수록 데이터를 잘 설명한다 

# 총 제곱합(SST) : 반응변수의 값이 평균으로 부터 얼마다 떨어져 있나? => 반응변수 자체의 변동을 의미
# 회귀제곱합(SSR) : 회귀직선이 평균으로부터 얼마나 떨어져 있는가? 
# 오차제곱합(SSE) : 반응변수 값이 회귀직선으로부터 얼마나 떨어져 있는가?
# SST = SSR+SSE : 데이터가 잘 설명할수록 총제곱합(SST) 중에 회귀제곱합(SSR)이 차지하는 비율(결정계수)이 크고 오차제곱합(SSE)의 비율은 작을 것
# 결정계수 R^2 = SSR/SST => 0과 1 사이의 값을 가짐

# 중선형회귀분석 : 2개이상인 선형회귀모형
# E(X|Y) = B0+B1+....
# 독립변수를 새로 추가할 때 마다 결정계수는 항상 커진다  => 보안된 척도가 필요 
# n: 데이터 개수 k: 설명변수(독립변수)

obj2 <- lm(SBP~age+weight, data=data4)
summary(obj2)

# 회귀분석 => 최소제곱법, 결정계수로 회귀모형의 설명력을 평가 하지 않음
# F검정은 두 집단간의 분사비를 나타낸 값
# 회귀제곱합 T를 자유도 k로 나눈것을 회귀평균제곱(MSR)
# 오차평균제곱(MSE) : 오차제곱합 SSE를 자유도 n-k-1로 나눈 것

# 회귀 SSR    k      MSR = SSR           F = MSR/MSE
# 오차 SSE   n-k-1   MSE = SSE / n-k-1
# 전체 SST   n-1

# 유의 확률은 귀마가설하에서 F-통계량이 자유도 k, n-k-1이 F분포를 따름
# 회귀분석 F-분석 : 
# 귀무가설 : 모든 회귀계수가 0이다 => 독립변수들이 종속변수를 설명하지 못함
# 상수항만 존재하는 모델이며, 모든 관측값이 Yi를 평균값으로 예측하는 단순한 모델

# 대립가설 : 적어도 하나의 독립변수가 종속변수를 설명하는데 유의한 영향을 미친다 
# yi를 평균값 y보다 더 잘 설명할 수 있는 회귀모형이 존재 

# f-검정 목적 : 회귀모형이 통계적으로 유의미한지 검정. 회귀모형 전체를 평가하는데 사용
# 귀무가설을 기각 : 회귀모형이 단순히 평균값만을 사용하는 모형보다 데이터 잘 설명
# 유의확률이 적을 수록 회귀모형이 데이터를 잘 설명될 가능성이 높음

#귀무가설이 참이면 단순히 평균값으로 예측, 기각하면 독립변수가 종속 변수를 설명하는데 유의한 영향을 미침

anova(obj)