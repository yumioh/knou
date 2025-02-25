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