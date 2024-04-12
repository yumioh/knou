#단변수 연속형 자료(몸무게 등)

library(MASS)
#1993년 미국에서 판매되는 93종의 자동차에 대한 여러 정보를 포함
head(Cars93) 

#오른쪽으로 치우친 분포
#히스토그램
with(Cars93, hist(MPG.highway, xlab="MPG in Highway", main="MPG in Highway"))

#install.packages("vcd")
library(vcd)
summary(Arthritis)
head(Arthritis)

#density 함수 사용
#확률밀도 함수 그림
with(Arthritis, plot(density(Age)))

#확률밀도함수 값을 이전에 그렸던 히스토그램에 overlay그리기
#probability : 히스토그램의 각 막대의 높이가 데이터의 비율을 나타내도록 하는 옵션
with(Cars93, hist(MPG.highway, xlab="MPG in Highway", main ="MPG in Hightway", probability=T))
#lwd :선의 두께를 지정하는 매개변수
with(Cars93, lines(density(MPG.highway), col='red', lwd=5))


#Quantile-Quantile plot
#특정 분포를 따르는지 아닌지 qq그림을 통해서 살펴볼수 있음
#자료의 분포를 가정했을때 얻은 백분위수 값과 샘플 백분위수 값을 x-y축에 도시하여
#y=x 직선상에 자료가 위치하고 있으면 자료가 가정한 특정 분포를 따른다고 해석

#qqnorm : 정규 분포의 분위수-분위수 플롯을 생성하는 R의 함수입니다. 
#이 그래프는 표본 데이터의 분포가 정규 분포와 얼마나 유사한지를 시각적으로 평가하는 데 사용
#이론값과 실제값이 비슷하면 직선형이 나온다
with(Cars93, qqnorm(Turn.circle, main="QQ plot of Turn.circle \n (U-turn space, feet)"))
#qqline() 함수는 qqnorm() 함수와 함께 사용되어 정규분포의 분위수-분위수 플롯(Quantile-Quantile plot)에 대각선을 추가
with(Cars93, qqline(Turn.circle, col="orange", lwd=3))

