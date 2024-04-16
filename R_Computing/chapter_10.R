#그래픽스1
#단변수 범주형 자료와 단변수 연속형 자료의 표현

library(MASS)
head(Cars93) 
#상자그림 
#IQR (q3 - q1) = (q1-1.15*IQR,q1+1.15*IQR)로 구할 수 있음
# minprice 가격 : 연속형 자료
# ~ Airbags의 모든 범주의 구분하여 보여줘라
boxplot(Min.Price~AirBags, data=Cars93)

#driver only그룹 분포 출력하기 
#subset(부분집합)
#airbags에서 driver only만 뽑아내서 주요 통계량을 보여줘 
summary(subset(Cars93, AirBags=="Driver only")$Min.Price)

#색상지정
#ylim : c(최소, 최대) 범위

boxplot(Min.Price~AirBags, data=Cars93, 
        names=c("Driver & Passenger","Driver only","None"),
        col=c("orange","cyan","yellow"), 
        ylab="Minimu Price", xlab="Airbag", 
        ylim=c(0,50), boxwex =0.25)


#상자그림 역순
#상자 그림 순서는 변수 그룹의 알파벳 순서
#at = c(3,2,1)와 같이 순서 지정
#names : 각 박스플롯의 이름들
#boxwex : 모든 박스들의 가로 크기
boxplot(Min.Price~AirBags, data=Cars93, 
        names=c("Driver & Passenger","Driver only","None"),
        col=c("orange","cyan","yellow"),
        at=c(3,2,1),
        ylab="Minimu Price", xlab="Airbag", 
        ylim=c(0,50), boxwex =0.25)
