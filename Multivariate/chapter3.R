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
med_varimax = principal(med_data, nfactors = 3, rotate = "varimax", scores = T, method = "regression")
med_varimax
