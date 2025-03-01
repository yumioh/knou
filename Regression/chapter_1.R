# 1. 단순회귀모형

## 1.1 회귀분석이란?
#- 독립변수(설명변수) : 다른 변수에 영향을 주는 변수 X
#- 종속변수(반응변수) : 독립 변수에 의하여 영향을 받는 변수 Y
#- 회귀분석 : 독립변수와 종속 변수 간의 함수관계를 규명하는 통계적인 분석방법

## 1.2 단순회귀모형

# 1.2.1 산점도
setwd("D:/knou")
getwd()

market = read.csv("./Regression/data/market-1.csv")
market

plot(market$X, market$Y, xlab="인테리어비", ylab="총판매액", pch=19)
title("인테리어비와 판매액의 산점도")
market_lm = lm(Y~X, data=market)
abline(market_lm, col="red")

# 1.2.2 단순회귀모형
# 설명변수 x, 반응변수 y의 관계가 직선의 형태를 가지는 경우 
# Y = B0+B1X 

# 관찰된 값들은 정확히 직선의 식 위에 있지 않아 오차항 e를 도입하면 
# Y = B0+B1X+e

# B0는 절편 개수, B1은 기술을 계수로 미지의 상수 e는 오차항으로 평균 e=0, var(e) = a^2인 정규 분포를 따르는 확률 변수로 가정
# 단순이라는 의미는 회귀계수로 볼때 선형이라고 독립변수가 하나이므로 단순회귀 모형이라고 함

#1.3.1 최소제곱법
# Y = B0+B1X 

# 표본 산점의 인테리어비와 총 판매액 자료에 대해서 회귀직선을 구하고 
# 산점도 위에 회귀 직선 그리기
market_lm = lm(Y~X, data=market)
summary(market_lm)

# 이값의 추정값은 y = 0.3282.2.1497x

# 회귀직선 그래프 그리기 
plot(market$X, market$Y, xlab="인테리어비", ylab="총판매액", pch=19)
title("인테리어비와 판매액의 산점도")
abline(market_lm, col="red")
identify(market$X, market$Y, n=10) 

#잔차 
# nammes는 market_lm의 결과 변수를 보여주는 기능
names(market_lm)

#잔차 출력
market_lm$residuals

#잔차의 합
sum(market_lm$residuals)

#독립 변수 X와 잔차(residuals)의 곱의 합을 계산
sum(market$X * market_lm$residuals)

# 
# 산점도 그리기
plot(market$X, market$Y, xlab="인테리어비", ylab="총판매액", pch=19)
title("인테리어비와 판매액의 산점도")

# 회귀직선 추가
abline(market_lm, col="red")

# 평균점(Xbar, Ybar) 계산
Xbar = mean(market$X)
Ybar = mean(market$Y)

# 평균점 추가 (par(new=TRUE) 사용 불필요)
points(Xbar, Ybar, pch=17, cex=2.0, col="RED")
text(Xbar, Ybar, "(8.85,19.36)", pos=3) # pos=3: 위쪽에 텍스트 표시

# 회귀식 텍스트 추가
fx <- "Y-hat = 0.33 + 2.215 * X"
text(locator(1), fx)  # 마우스 클릭한 곳에 텍스트 출력

#1.4.1 분산분석표에 의한 f검정
anova(market_lm)

# a=0.05 유의수준에서 f기각역 값은?
qf(0.95, 1,13)

#유의 확률
1-pf(192.9,1,13)

summary(market_lm)

# 결정계수 
cor_xy = cor(market$X, market$Y)
round(cor_xy^2, 4)
