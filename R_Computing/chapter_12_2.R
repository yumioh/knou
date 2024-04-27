##ggplot 그래프 그리기 
install.packages("ggplot2")
library(MASS)
library(ggplot2)
#qplot 산점도
head(Cars93)
qplot(Horsepower, Price, data=Cars93, color=AirBags, size=AirBags)

#subgroup 산점도
# Man.trans.avail=='No' 인경우 no ,yes로 표시하고 그걸 manual에 넣어라
Cars93$manual <- with(Cars93, ifelse(Man.trans.avail=='No', 'Manual_Trans_No', 'Manual_Trans_Yes'))

#'Horsepower'와 'Price' 변수를 사용하여 산점도를 그리고, 'Origin'에 따라 다른 패널에 그래프를 표시
#또한 Origin에 따라 서로 다른 패널에 그래프를 나누어 표시
#Horsepower, Price: x축과 y축에 사용될 변수
#manual~Origin: 이것은 패널을 그리는 방법을 지정 ~ 기호는 '패널을 구분할 열'을 나타냄
# manual: 이 부분은 그래프의 열 Origin: 이 부분은 그래프의 행
#facets(열1~열2) 그래프를 여러 개의 패널로 나누어서 표시할 때 사용
#열1은 열의 값에 따라 그래프를 수직으로 나누는 열
#열2는 열의 값에 따라 그래프를 수평으로 나누는 열
with(Cars93, qplot(Horsepower, Price, data=Cars93, facets=manual~ Origin))

#qplot을 이용한 확률밀도 함수 
#geom="density" : 막대형태를 부드럽게 연결해라 
#fill=Origin: 원산지(Origin)에 따라 색상을 구분
#alpha=I(.2): 투명도
#theme(plot.title = element_text(hjust=0.5)): 그래프의 제목을 가운데 정렬
qplot(Fuel.tank.capacity, data=Cars93, geom="density", fill=Origin, alpha=I(.2),
      main="fuel tank capacity by origin", 
      xlab="fuel tank capacity (us gallons)", ylab="density")+
      theme(plot.title = element_text(hjust=0.5))

#회귀선 추가 산점도 -1
#회귀계수를 계산할 필요없이 회귀선 추가
# +를 연결해주면 부과적인 표현 방법 적용
# geom_smooth : 회귀선을 추가 geom_point: 산점도
#se=FALSE 신뢰대 표현 안하고 싶으면 이옵션 넣기 
ggplot(Cars93, aes(x=Horsepower, y=Price))+geom_point(shape=16)+geom_smooth(method=lm, se=FALSE)

#geom = c("point", "smooth"): 점과 선형 회귀선(부드러운 추세선)
# 앞선 직선으로 표현 한것으로 스무드하게 곡선을 만듬 
#hjust=그래프의 제목을 0.50은 왼쪽 정렬, 1은 오른쪽 정렬, 0.5는 가운데 정렬

qplot(Horsepower, Price, data=Cars93, geom=c("point", "smooth"), color=Origin, main="Price vs Horsepower by Origin",
      xlab="Horsepower", ylab="Price") + theme(plot.title = element_text(hjust=0.5))

#qplot을 한번에 작성 qqplot은 +으로 옵션표현 추가

#연속형 변수가 추가된 산점도 
#연속형 변수 width를 색깔로 표현
#scale_color_gradient(low = "yellow", high = "red"): 점의 색상을 그래디언트로 지정
ggplot(Cars93, aes(x=Horsepower, y=Price, color=Width))+
  geom_point(shape=16)+scale_color_gradient(low="yellow", high="red")

#사용자 색지정 연속형 변수 산점도 
# 무지개 색으로 표현
ggplot(Cars93, aes(x=Horsepower, y=Price, color=Width))+geom_point(shape=16)+
  scale_color_gradientn(colours = rainbow(5))


#명목형 변수가 추가 되는 경의 산점도
#색지정을 위해 RColorBrewer라는 패키지의 Dark2라는 palette 사용
library(RColorBrewer)

#aes(x = Horsepower, y = Price, shape = AirBags, color = AirBags): x축에 'Horsepower', y축에 'Price'를 매핑하고, 
#점의 모양과 색상을 'AirBags' 열의 값에 따라 지정
#cale_shape_manual(values = c(16, 17, 18)): 점의 모양을 수동으로 지정합니다. 
#여기서는 16, 17, 18번 모양을 각각 'AirBags' 열의 값에 따라 사용
#색상 팔레트를 설정 : Dark2' 팔레트
ggplot(Cars93, aes(x=Horsepower, y=Price, shape=AirBags, color=AirBags)) +
  geom_point(size=3)+scale_shape_manual(values=c(16,17,18)) +
  scale_color_brewer(palette="Dark2")

#명목형 변수가 추가되는 경우의 산점도 -2
#회귀선을 그리기 위해 옵션 geom_Smooth(method=lm, se=FALSE)
#산점도에 회귀선 추가
ggplot(Cars93, aes(x=Horsepower, y=Price, shape=AirBags, color=AirBags)) +
  geom_point(size=3)+scale_shape_manual(values=c(16,17,18)) +
  scale_color_brewer(palette="Dark2") + geom_smooth(method=lm, se=FALSE)

#회귀선을 연장하기 위해 옵션 fullrange=TRUE
#fullrange = TRUE는 그래프 전체 범위에 걸쳐 회귀선을 그리도록 지정
ggplot(Cars93, aes(x=Horsepower, y=Price, shape=AirBags, color=AirBags)) +
  geom_point(size=3)+scale_shape_manual(values=c(16,17,18)) +
  scale_color_brewer(palette="Dark2") + geom_smooth(method=lm, se=FALSE, fullrange=TRUE)



