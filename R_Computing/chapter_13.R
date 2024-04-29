#레이더 차트

install.packages("doBy")
library(doBy)
library(MASS)

#summaryBy : 데이터를 요약하고 그룹별 특징을 보여주는 데 사용
#FUN: 계산할 요약 통계량을 지정하는 리스트
#(6개의 변수)전체 데이터셋를 뽑아서 Type별로 나눠라 c(mean) 평균값을 보여줘
mean_by_Type2 <- summaryBy(MPG.highway + RPM + Horsepower + Weight + Length + Price ~ Type, data=Cars93, ㅊ=c(mean))

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
  dfmax <- apply(df, 2, max) #데이터를 요약하거나 변환하기 위해 사용
  dfmin <- apply(df, 2, min) #
  as.data.frame(rbind(dfmax, dfmin, df)) 
  #rbind(dfmax, dfmin, df): dfmax, dfmin, df 세 개의 데이터프레임을 행으로 결합
  #다른 형식의 객체를 데이터프레임으로 변환할 때 사용
}

mean_by_Type <- df_radarchart(df2)

mean_by_Type

row.names(mean_by_Type) <- c('max','min',names(table(Cars93$Type)))



