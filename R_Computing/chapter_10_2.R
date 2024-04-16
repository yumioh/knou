#install.packages("yarrr")
#install.packages("gridExtra") : ggplot 그래프를 여러개 보여주기 위한 패키지
library(yarrr)
library(MASS)
library(gridExtra)

head(Cars93)
#Parate Plot
#박스플롯과 그림이 유사하지만 상자가 아닌 호리병 모양으로 나옴
# 범주형이 2종류
# origin : usa, non-usa
# drivetrain : 4wd, front, rear
# main : 제목
#inf.method="iqr" : 사분위수 표현
# point.o : 데이터의 포인터의 크기(0-1사이) 0에 가까울수록 데이터 포인트가 작아지고 1에 가까울수록 데이터 포인터가 큼
pirateplot(formula = MPG.city ~ Origin + DriveTrain, point.o = 0.5,
           data=Cars93, 
           main="City MPG by Origin and Drive Train", 
           inf.method="iqr")


#그룹별 확률밀도함수 그리기
#고속도로 연비 분포
#geom_densit : 확률밀도 그리는 함수
#labs : x,y lable 지정
#ggtitle : 제목
#theme : 모양 
#hjust = 0.5: 가로 방향(수평)으로 텍스트를 가운데로 정렬하는 것을 지정합니다. 
#hjust는 수평 정렬을 나타내는 매개변수로, 0은 왼쪽, 1은 오른쪽, 0.5는 가운데를 의미
ggplot(Cars93, aes(x=MPG.highway)) + geom_density(aes(group=Type, colour=Type))+
  labs(x="MPG.highway", y="Density")+
  ggtitle("Desity of MPG in Highway by Type")+
  theme(plot.title = element_text(hjust=0.5))


#확률 밀도 함수 배경색 변경(회색 -> 흰색)
ggplot(Cars93, aes(x=MPG.highway)) + geom_density(aes(group=Type, colour=Type))+
  labs(x="MPG.highway", y="Density")+
  ggtitle("Desity of MPG in Highway by Type")+
  theme(plot.title = element_text(hjust=0.5))+
  theme_bw()


#그림을 배열하기 위해서는 par(mfrow=c(2,2)) 옵션을 사용할 수 있는데 ggplot2패키지에서 사용 불가능
#그래서 gridExtra 패키지 사용

p1 <- ggplot(Cars93, aes(x=MPG.highway)) + geom_density(aes(group=Type, colour=Type))+
  labs(x="MPG.highway", y="Density")+
  ggtitle("Desity of MPG in Highway by Type")+
  theme(plot.title = element_text(hjust=0.5))+
  theme_bw()


p2 <- ggplot(Cars93, aes(x=MPG.highway)) + geom_density(aes(group=Origin, colour=Origin))+
  labs(x="MPG.highway", y="Density")+
  ggtitle("Desity of MPG in Highway by Origin")+
  theme(plot.title = element_text(hjust=0.5))+
  theme_bw()

#exrpession : 그래프을 더 이쁘게 만들기 위한 함수

p3 <- ggplot(Cars93, aes(x=MPG.highway)) + 
  geom_density(aes(group=Man.trans.avail, colour=Man.trans.avail))+
  labs(x=expression("MPG"^highway), y=expression("Density"[value]))+
  ggtitle("Desity of MPG in Highway \n by Manual transsmission availability")+
  theme(plot.title = element_text(hjust=0.5))+
  theme_bw()


p4 <-  ggplot(Cars93, aes(x=MPG.highway)) + 
  geom_density(aes(group=Man.trans.avail, colour=Man.trans.avail))+
  labs(x=expression("MPG"^highway), y=expression("Density"[value]))+
  ggtitle(expression(paste("Desity of MPG(",mu,")")^Highway))+
  theme(plot.title = element_text(hjust=0.5))+
  theme_bw()


#4개 그래프를 동시에 보여줌 2행 2열
grid.arrange(p1,p2,p3,p4, ncol=2, nrow=2)




