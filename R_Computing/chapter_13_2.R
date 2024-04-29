#고밀도 자료에 대한 그림

library(ggplot2)

summary(diamonds)

#stat_bin2d(): x와 y 축을 이용하여 2차원 히스토그램을 생성하는 함수 
#bins: bin(구간) 수를 설정
#가로 전체 영역을 25개의 상자로 구분
#테두리 색을 grey
#aes : 매핑할 데이터
ggplot(diamonds, aes(carat, price)) + stat_bin2d(bins = 25, colour="grey50")

#축의 범위를 0 ~ 6까지 증가
ggplot(diamonds, aes(carat, price)) + stat_bin2d(bins = 40 , colour="grey50") +
  scale_x_continuous(limits = c(0,6))


#색지정
ggplot(diamonds, aes(carat, price)) + stat_bin2d(bins = 40 , colour="grey50") +
  scale_x_continuous(limits = c(0,6)) + ggtitle("Price vs Carat") + 
  theme(plot.title = element_text(hjust = 0.5))+
  scale_fill_gradientn(colours = c("yellow","green","blue","red")) + 
  labs(x ="carat", y="price")

#고밀도 자료에 대한 일반 산점도 

install.packages("SwissAir")
library(SwissAir)

dim(AirQual)

#자료가 몰려있는 특정영역에 대한 파악이 어려움 하단은 일반 산점도
#ad.WS 풍속 데이터,ad.O3 : 오존 데이터
with(AirQual, plot(ad.WS ~ ad.O3, xlab='03', ylab='WS')) 

#smoothScatter 이용한 고밀도 산점도
with(AirQual, smoothScatter(ad.O3, ad.WS, main = "Scastter plot by smoothed densities",xlab='03', ylab='WS')) 

#install.packages("hexbin")
library(hexbin)

#고밀도 자료에 대한 육면 상자 그림
# smoothScatter과 그림이 비슷
with(AirQual, plot(hexbin(ad.O3, ad.WS, xbin=100),main = "Hexagona I binnging", xlab='03', ylab='WS' ))
#bin 사이즈 줄임 육각형이 더 커짐
with(AirQual, plot(hexbin(ad.O3, ad.WS, xbin=30),main = "Hexagona I binnging", xlab='03', ylab='WS' ))


install.packages("IDPmisc")
library(IDPmisc)

#고밀도 자료를 이미지 산점도 그림
with(AirQual, iplot(ad.O3, ad.WS, xlab='03', ylab='WS', 
                    main = "image Scastter plot with \n color indicationg desity", ))


#다변수 이미지 산점도
#3가지 변수를 뽑아서 보기
ipairs(subset(AirQual, select=c(ad.O3, ad.WS, ad.WD)))



