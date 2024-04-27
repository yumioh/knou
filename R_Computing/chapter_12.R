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
install.packages("jpeg")
library(jpeg)

sales.amount <- c(1.5,2.3,5.4,7.5,9,8)

img <- readJPEG("c:/data/image.jpg")

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



