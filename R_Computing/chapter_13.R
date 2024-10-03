#레이더 차트 : 타입별 특성치를 나열해 두고 어떤 타입을 우위를 두고 있는가를 알 수 있음

install.packages("doBy")
library(doBy)
library(MASS)

#summaryBy : 데이터를 요약하고 그룹별 특징을 보여주는 데 사용
#FUN: 계산할 요약 통계량을 지정하는 리스트
#(6개의 변수)전체 데이터셋를 뽑아서 Type별로 나눠라 c(mean) 평균값을 보여줘
mean_by_Type2 <- summaryBy(MPG.highway + RPM + Horsepower + Weight + Length + Price ~ Type, data=Cars93, FUN =c(mean))

mean_by_Type2

#레이터 차트 작성을 위한 데이터 가공
#6개 각 변수의 최대값과 최소값을 구하기 위해 apply함수 이용

#모든행을 택하고 [,c(2:7)]
#c(2:7)은 2부터 7까지의 숫자 벡터를 생성하는 함수
# 따라서 이 부분은 2부터 7까지의 열을 선택하여 출력
# 일부 데이터만 저장
df2 <- mean_by_Type2[,c(2:7)]

df2

#함수 구현
df_radarchart <- function(df) {
  df <- data.frame(df)
  dfmax <- apply(df, 2, max) #2이면 열, 1이면 행의 작업 수행 데이터를 요약하거나 변환하기 위해 사용
  dfmin <- apply(df, 2, min) #
  as.data.frame(rbind(dfmax, dfmin, df)) 
  #rbind(dfmax, dfmin, df): dfmax, dfmin, df 세 개의 데이터프레임을 행으로 결합
  #다른 형식의 객체를 데이터프레임으로 변환할 때 사용
}

mean_by_Type <- df_radarchart(df2)

mean_by_Type

#mean_by_Type 데이터프레임의 행 이름이 'max', 'min', 그리고 Cars93 데이터프레임의 'Type' 열에 있는 고유한 값들로 변경
row.names(mean_by_Type) <- c('max','min',names(table(Cars93$Type)))

install.packages("fmsb")
library(fmsb)


radarchart(df = mean_by_Type, #the data frame to be used to draw chart
           seg=6, #레이더 차트의 분할 수(축을 몇 개의 세그먼트로 나눌 것인지)를 지정
           pty=16, #레이더 차트의 유형
           pcol=1:6, #레이더 차트의 선 색상
           plty=1, #선 유형
           plwd=2, #선 두께
           title = c("Radar chart by car types")
           )
#범례
#col = c(1:6) : 선의 색상을 1에서 6까지의 색상 인덱스로 지정
legend("topleft", legend = mean_by_Type2$Type, col = c(1:6), lty=1, lwd=2)

#오각 레이더 차트 

dat <- Cars93[2:6, c('Price','Horsepower','Turn.circle','Rear.seat.room','Luggage.room')]

datmax <- apply(dat, 2, max)
datmin <- apply(dat, 2, min)
dat <- rbind(datmax, datmin, dat)

radarchart(dat, seg=5, plty=1, vlabels=c('Price','Horsepower','U-trun space\n(feet)'
            ,'Rear seat room\n(inches)','Luggage capacity\n(cubin feet)'), 
           title="5 segments, with specified vlabels", 
            vlcex=0.8, #축 레이블의 크기를 조절
           pcol=rainbow(5))

#Cars93[2:6,'Make'] : Cars93 데이터프레임의 2번부터 6번 열에 있는 Make 열의 값을 사용
legend("topleft", legend = Cars93[2:6,'Make'], col = rainbow(5), lty=1, lwd=1)





