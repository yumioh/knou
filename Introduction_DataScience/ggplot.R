#ggplot2
# - geom 계열 함수 여러개를 병렬적으로 추가
# - geom 계열이 몸체를, coord 계열이 좌표측을 이루는 구조
# - ggplot()함수와 geom 계열함수는 반드시 포함되어야 하는 필수적 요소

library(tidyverse)
library(ggplot2)

#ggplot()함수 : 일반적으로 함수 내에 시각화 대상이 되는 데이터, 축의 설정, 그래프의 색깔, 투명도, 선 패턴 등 큰 틀을 매핑하는 aes() 함수가 위치 
