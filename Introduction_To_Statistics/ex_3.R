library(ggplot2)

setwd("D:\\knou\\Introduction_To_Statistics")

##################################################

##함수를 이용해서 히스토그램 그리기

#hist(x, breaks, main, xlab, ylab, xlim, ylim....)\
#x : 데이터벡터
#break : 계급에 대한 정보, 계급의 개수, 계급을 나누는 값들의 벡터
#main : 그래프의 제목
#xlab,ylab: 축의 제목
#xlim, ylim : 축의 범위 

#예제 2-6
score<-c(93, 83, 91, 68, 75, 87, 89, 96, 97, 67, 83, 81, 87, 80, 64,
         83, 88, 76, 91, 78, 72, 80, 69, 80, 84, 71, 91, 81, 88, 73)

hist(score)
hist(score, main = "중간고사 영어점수")

#예제 2-7

rv<-c(0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9,
      
      1, 1, 1.8,
      2, 2.1, 2.3, 2.4, 2.8, 2.9,
      3, 3.2, 3.3, 3.5, 3.8, 3.8, 3.9,
      4, 4.2, 4.4, 4.5,
      5.1, 5.3, 5.3, 5.4,
      14, 17, 18, 19,
      21, 21, 23, 25, 27, 28, 32, 34, 36,
      41, 42, 44, 48, 49,
      51, 54, 59,60, 61, 62, 80,
      240)

hist(rv)
hist(rv, main = "", xlab="CRP", ylab = "Frequency", breaks = 20) #20계급
hist(rv, main = "", xlab="CRP", ylab = "Frequency", breaks = seq(0,240,20)) # 0 240까지 20계급을 나눠라


#예제 2-8
set.seed(2021)
rn<-c(rnorm(100, 5, 2), rnorm(100, 10, 2)) 
#rnorm(100, 5, 2) : 평균이 5, 표준편차가 2인 정규분포를 따르는 난수 생성
#rnorm(100, 10, 2) : 평균이 10, 표준표차가 2인 정규분포를 따르는 난수 
#할때마다 다른 난수가 발생 그래서 set.seed(2021)을 사용하면 동일한 난수 발생

hist(rn)
hist(rn, breaks = 20, main = "", xlab="value")
hist(rn, breaks = 5, main = "", xlab="value")

#예제 2-9
age<-c(57, 61, 47, 57, 48, 58, 57, 61, 54, 50, 68, 51)

##################################################

##상자 그림 그리기

#boxplot(x.....)
#x: 데이터 벡터값

#예제 2-15
age<-c(57, 61, 47, 57, 48, 58, 57, 61, 54, 50, 68, 51)
boxplot(age, ylab="Age")


#예제 2-16
member<-c(92, 107, 180, 90, 78, 91, 102, 88, 106, 125, 95, 102, 162)
boxplot(member, ylab="Number of board members")
#r이 판단하여 특이점 표기

##################################################

## x가 데이터 벡터일때
#평균 : mean(x)
#분산 : var(x)
#표준편차 : sd(x)
#중앙값 : median(x)
#다섯수치요약 : fivenum(x)
#사분위수 범위 : IQR(x)
#범위 : range(x)


#예제 2-15
member<-c(92, 107, 180, 90, 78, 91, 102, 88, 106, 125, 95, 102, 162)
mean(member)
var(member)
sd(member)
median(member)
fivenum(member)
IQR(member)
range(member)
hist(member, breaks = 10)
