install.packages("psych")
library(psych)
# R을 이용한 인자분석
med_data = read.csv("D:/knou/Multivariate/data/medFactor.csv")
head(med_data)
summary(med_data)

# 초기 인자분석 
install.packages("GPArotation")
library(psych)

# principal : 주성분 분석 및 인자 분석 수행하는 함수
med_factor = principal(med_data, rotate="none")
names(med_factor)

# 주성분의 분산값
med_factor$values

#스크리 그래프 그리기 => 유효 인자 3~4개로 확인
plot(med_factor$values, type="b", pch=19)

#인자 회전
# h2 : 변수의 공통성
# u2 : 고유분산
# 유의한 인자 : RC1, RC2, RC3
# varimax : 행렬의 열을 기준으하여 큰 값은 더 크게, 작은 값은 더 작게 회전하는 방법 
med_varimax = principal(med_data, nfactors = 3, rotate = "varimax", scores = T, method = "regression")
med_varimax


#인자점수
head(med_varimax$scores)

#인자점수 계산
# oblimin : 인자값을 0 또는 1에 가깝도록 회전하는 방법
# method="regression" : 주성분 분석시 회귀 분석 사용
# scores = TRUE : 각 행별 인자점수를 계산
med_oblimin = principal(med_data, nfactors = 3, rotate = "oblimin", scores = T, method="regression")
med_oblimin

head(med_oblimin$scores)

#행렬도 그리기
biplot(med_varimax)

state = state.x77
summary(state)

#인자 분석 하기 
library(stats)

#인자부하값을 이용하여 고윳값을 구함함
state_fact0 = factanal(state, factors=4)
#벡터의 제곱합을 구하는 함수  
sosq = function(v) {sum(v^2)}
#요인 부하량 행렬 추출(행: 변수, 열: 요인)
loadings = as.matrix(state_fact0$loadings)
#각 요인별 고유값 계산 = 해당 열의 제곱합
# 1: 행 2: 열
eigne_value = apply(loadings, 2, sosq)
# 해당값이 클수록 해당 요인이 데이터를 더 많이 설명
eigne_value

#인자분석 실행
state_fact = factanal(state, factors=3, rotation="none") #회전 none
state_fact
state_fact1 = factanal(state, factors=3, rotation="varimax") #varimax 회전 
state_fact1
state_fact2 = factanal(state, factors=3, rotation="promax") #promax 회전 
state_fact2

# 공통성이 낮은 population 제외
state_fact1 = factanal(state[,-1], factors=3, rotation="varimax")
state_fact1



