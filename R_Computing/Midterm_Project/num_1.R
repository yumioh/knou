#1)자신의 학번의 각 자리로 이루어진 벡터 x를 정의하시요
x <- c(2,0,2,4,3,5,3,6,7,7,6,3)
x

#2)R통계함수를 이용하여 x의 평균, 분산, 중앙값을 구하시오
#평균1
mean(x)
#평균2
sum(x)/length(x)
#분산
var2 <-var(x)
round(var2, 2)
#중앙값
median(x)
#기초통계량
summary(x)

#3)자신이 정의한 벡터 x의 맨 끝자리를 결측지 NA로 바꾸어 벡터 y를 정의하시오
y <- replace(x,12,NA)
y

#4)추가된 결측치 NA를 제외하고, 벡터 y의 평균, 분산, 중앙값을 구하라
#NA 여부 판단
is.na(y)
#연산에서 NA 제외옵션, 
#평균
mean3 <- mean(y,na.rm = TRUE)
round(mean1,2)
#분산
var3 <- var(y,na.rm = TRUE)
round(var1, 2)
#중앙값
median(y,na.rm = TRUE)



