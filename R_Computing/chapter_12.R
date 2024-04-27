#두변간의 상관관계를 표현한 그래프 
#상관도 그림 : corrr 패키지 이용. 두 변수 조합에 대한 상관도를 색깔과 음영으로 파악
#magrittr 패키지 설치하여 파이프 연산자(%>%)를 이용하면 코드를 간소화할 수 있음
install.packages("corrr")
install.packages("magrittr")
#객체 or 데이터 %>% 함수

library(magrittr)
mtcars %>% head #head(mtcars) 수행
mtcars %>% tan %>% cos %>% sin %>% head %>% round(2) #== head(sin(cos(tan(mtcars))))
#mtcars 자료의 모든 변수에 모두 tangent 변환을 수행하고 
#cosine 변환을 한 다음 sine 변환 후 처음 6개값만 보인 후 
#소수점 셋째 자리에서 반올림 하라는 명령어

library(corrr)
mtcars %>% correlate() %>% fashion() # 상관계수 행렬(mtcars와 correlate의 상관관계를 행렬(fashion)로 만들어라)

mtcars %>% correlate() %>% rplot()


#상관도 네트워크 그림
#상관계수 절대값이 0.3 이상이면 네트워크로 표현
mtcars %>% correlate() %>% network_plot(min_cor =.3)

#네트워크 그림이 안나올시 오류시 보안 방법
#intall.package("ragg")
#library(ragg)
y <- mtcars %>% correlate() #그림 객체를 외부에 저장하고 다시 그림 부르기

#변수군집그림 : 유관한 변수들을 묶어주는 그림
install.packages("Hmisc")
library(Hmisc)
library(MASS)
temp <- Cars93[,c('Price','MPG.city','Horsepower','RPM','Length','Wheelbase')]
temp
#변수군집 그림 : varclus
#~. 모든 데이터 다 사용하겠다라는 의미
#similarity : 유사도 척도를 어떤걸로 할것인가? 대표적으로 spear 사용
plot(v <- varclus(~., data=temp, similarity="spear"))


#jpeg 그림 불려오기 
#install.packages("jpeg")
library(jpeg)

sales.amount <- c(1.5,2.3,5.4,7.5,9,8)

img <- readJPEG("c:/data/car.jpg")

plot(c(0.5,6.5), c(0,10), axes = F, cex.lab=1.3,
     type='n',xlab="Month",ylab="Sales (in million dollars)")
axis(1, at=c(1,2,3,4,5,6), labels = c('Jan','Feb','Mar','April','May','Jun'),cex.axis=1.2) #축

axis(2, at=c(0,2,4,6,8,10), labels = c('0','2','4','6','8','10'), cex.axis=1.2) #y축
lines(1:6, sales.amount, lwd =2, col="orange")

#rasterImage(왼쪽끝 위치, 오른쪽 끝 위치) :이미지 크기를 정함
#점으로 찍힌 위치에 그림이 대신 찍어줌
for(jj in 1:6){
  rasterImage(img, jj-0.3, sales.amount[jj]-0.3, jj+0.3, sales.amount[jj]+0.3)
}

#png 파일 읽기
install.packages("png")
library(png)

img <- readPNG("c:/data/car2.png")

#axes : x,y축 출력 여부 cex.lab :x,y축 이름 크기 조정
plot(c(1,6), c(15,46), cex.lab = 1.3, axes=T,
     type='n',xlab="Engine Size",ylab="MPG in City")

#x축 , y축, x축, y축
rasterImage(img, 0.7, 14.5, 6.1, 46.0)

#cex.axis: 각 축의 눈금 레이블 크기 조정
#1은 x축 at: 눈금을 표시할 위치 labels: 각 눈금 위치에 표시될 레이블
axis(1, at=c(1,2,3,4,5,6), labels = c('1','2','3','4','5','6'),cex.axis=1.2) #x축
axis(2, at=seq(15,45,by=5), labels = seq(15,45,by=5), cex.axis=1.2) #y축

#with(): 특정 데이터프레임을 사용하여 그래프를 그릴 때 유용한 함수
# subset(Cars93, Origin=='USA') : 'Cars93' 데이터프레임에서 'Origin'이 'USA'인 행만 선택
#points(): 산점도를 그리는 함수로, 이미 존재하는 그래프 위에 점을 추가
#col=4: 점의 색상 pch 점모양
with(subset(Cars93, Origin=='non-USA'), points(EngineSize, MPG.city, col=2, pch=16))
with(subset(Cars93, Origin=='USA'), points(EngineSize, MPG.city, col=4, pch=16))

#'topright': 범례를 그래프의 우측 상단에 배치
#bty='n': 범례의 테두리를 없애 줌
#col=c(2,4): 각 레이블에 대응하는 색상입니다. 여기서는 2와 4가 각각 'non-USA'와 'USA'를 나타냄
#lwd=2: 범례의 선의 너비를 설정
legend('topright', bty='n', c('non-USA','USA'), col=c(2,4), lwd=2, pch=16)

#pos=4: 텍스트의 위치를 지정
#2.3,35 : 텍스트 위치
#col=1: 텍스트의 색상을 지정
text(2.3, 35, pos=4, 'Cars in usa low mpgs in city, \nwhile having large engines compared \nto non-usa',
     col=1)


#파일 저장
#jpeg 문장을 실행시키고 그림을 그리고 난 후 다시 dev.off()실행
#저장 파일 형태에 따라 jpeg 함수 또는 pdf 함수 활용
#width=6, height=6: 그림의 가로와 세로 크기
#units='in': 가로와 세로의 단위를 인치로 설정
#bg='white': 그림의 배경색을 지정
jpeg(file = "mpg_engine_size.jpg", width=6, height=6, units='in', res=500, bg='white')
#dev.off(): 그림 그리기 작업이 끝난 후 저장 디바이스를 닫음
dev.off()

pdf(file = 'mpg_engine_size.pdf', width=6, height=6, bg="white", paper='special')
dev.off()

