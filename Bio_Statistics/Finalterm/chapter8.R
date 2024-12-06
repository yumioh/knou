setwd("C:/workplace/knou/Bio_Statistics/Finalterm")
data <- read.csv("./data/biostat_ex_data.csv")
data.head()
library(dplyr)

#로지스틱 회귀 :확률값(0,1 사이)을 예측하기 위해 로짓함수 사용 => 종속변수(설명변수)가 이진형인 경우에 분석 가능
#              0,1에 들어갈 확률값을 계산