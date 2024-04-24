#이변수 연속형 변수들에 대한 자료의 표현

#이변수 연속형 자료의 표현을 위한 기본 산점도의 옵션 : pch (1~25가지 모양 옵션)
#albine 회귀직선 추가 - 두변수간의 관계를 직선으로 표현
#lines : 직선추가 -영역의 선을 추가

#1. 기본산점도
library(MASS) #car93데이터

#with함수는 테이더 프레임 또는 리스트 변수를 변수 이름만으로 접근할 수 있게 해주는 함수
#원하는 데이터를 넣고 적용할 함수 넣어줌

with(Cars93, 
     plot(Price, MPG.city, main="Price vs MPG.city", xlab="Price", ylab="MPG in City",pch=19))

#회귀직선
#lm 선형회귀모양 적합
with(Cars93, 
     abline(lm(MPG.city~Price), col="red", lwd=2))

#lowess는 locally weighted scaaterplot smoother를 의미 : 실제 관측지에 따라 연결하는 선
with(Cars93, 
     lines(lowess(Price,MPG.city), col="blue", lwd=2))
#범례
#lwd : 범례 표시 라인 굵기 bty: 비율 설정
#bty = 'n' 범례 박스 없애기
legend(40,40, 
       lty = 1, col=c("red","blue"),c("regression","lowess"), lwd=2, bty = 'n')


#다변수의 요약

library(vcd) #관절염 데이터

#범주형 변수
summary(Arthritis)

#~Treatment+Improved의 의미 : Treatment와 Improved 상호작용을 나타냄
#Treatment : 처리조건 또는 실험군
#Improved : 결과를 나타내는 종속 변수
#subset은 데이터 프레임에서 특정 조건을 만족하는 행을 선택하기 위해 사용되는 파라미터
art <- xtabs(~Treatment+Improved, data=Arthritis, subset = Sex == "Female")
#gp=shading_max : 그래프의 색상 설정 중에서 최대 값을 강조하는 데 사용
art #교차표 작성
mosaic(art, gp=shading_max)

#모자이크 그림 
summary(Titanic)

#명목형 변수가 여러개 존재할떄 사용할 수 있는 모자이크 그림
#범주형 : 명목형과 순서형으로 나뉨

#다변수 범주
#shade=TRUE: 셀의 색상 지정->  이 차이가 클수록 색상이 진하게 표시
#legend= TRUE : 플롯에 사용된 색상과 해당하는 범주를 나타내는 범례가 플롯에 추가
mosaic(~Sex + Age + Survived, data=Titanic, main="Survival on the Titanic", shade=TRUE, legend= TRUE)

#다중산점도
#여러 변수를 산점도로 표현
#select 변수 선택
dat1 <- subset(Cars93, select=c(Min.Price, Price, Max.Price, MPG.city, MPG.highway))
pairs(dat1)

#단순산점도
with(Cars93, 
     plot(Price, MPG.city, xlab="Price", ylab="MPG in City", main="Mileage"))

#단순산점도 - 그룹산점도

#type='n' : 타입을 지정하지 않음.
#front, rear, 4wd를 색을 지정하여 찍음

with(Cars93, 
     plot(Price, MPG.city, xlab="Price", ylab="MPG in City",type='n'))

with(subset(Cars93, 
            DriveTrain=="Front"), points(Price, MPG.city, col="orange", pch=19))
with(subset(Cars93, 
            DriveTrain=="Rear"), points(Price, MPG.city, col="firebrick", pch=17))
with(subset(Cars93, 
            DriveTrain=="4WD"), points(Price, MPG.city, col="black", pch=8))

legend("topright",
       legend = c("Front","Rear","4WD"), col=c("orange","firebrick","black"), pch=c(19,17,8), bty="n")


#단순산점도 회귀선 추가 
#lm : 회귀 모형을 찾는 함수 

fit1 <- with(subset(Cars93, DriveTrain =="Front"), lm(MPG.city~Price))
fit2 <- with(subset(Cars93, DriveTrain =="Rear"), lm(MPG.city~Price))
fit3 <- with(subset(Cars93, DriveTrain =="4WD"), lm(MPG.city~Price))

#Cars93에서 DriveTrain이 "Front"인 행들을 선택 후  Price 열의 값 가지고 옴
xx1 <- subset(Cars93, DriveTrain=='Front')$Price
#coef: 회귀모델 계수 
#예측 값
yy1 <- fit1$coef[1]+fit1$coef[2]*xx1

xx2 <- subset(Cars93, DriveTrain=='Rear')$Price
yy2 <- fit2$coef[1]+fit2$coef[2]*xx2

xx3 <- subset(Cars93, DriveTrain=='4WD')$Price
yy3 <- fit3$coef[1]+fit3$coef[2]*xx3

#단순산점도 회귀선 추가하기 

with(Cars93, plot(Price, MPG.city, xlab='Price', ylab="MPG in City", type='n'))

with(subset(Cars93, DriveTrain=='Front'), points(Price, MPG.city, col='orange', pch=19))
with(subset(Cars93, DriveTrain=='Rear'), points(Price, MPG.city, col='firebrick', pch=17))
with(subset(Cars93, DriveTrain=='4WD'), points(Price, MPG.city, col='black', pch=8))

legend("topright",
       legend = c("Front","Rear","4WD"), col=c("orange","firebrick","black"), pch=c(19,17,8), bty="n")

lines(xx1, yy1, col='orange', lwd=2)
lines(xx2, yy2, col='firebrick', lwd=2)
lines(xx3, yy3, col='black', lwd=2)

#화면 그리드(2행2열)
#mfrow 행렬 설정하여 한 화면에 여러 그래프 표시
par(mfrow=c(2,2))

with(subset(Cars93, DriveTrain='Front'), plot(Price, MPG.city, col='orange', pcj=19, main='Front'))
with(subset(Cars93, DriveTrain='Rear'), plot(Price, MPG.city, col='black', pcj=17, main='Rear'))
with(subset(Cars93, DriveTrain='4WD'), plot(Price, MPG.city, col='firebrick', pcj=8, main='4WD'))

#qplot : 간단하고 빠르게 그래프 생성 가능
library(ggplot2)
#type : 차량의 형태를 의미
#생산지역과 에어백 여부 
qplot(Wheelbase, Width, data=Cars93, shape=Type, color=Type, 
      facets=Origin~AirBags, size=Length, xlab="Wheelbase", ylab="car width")

head(Cars93$Type)



