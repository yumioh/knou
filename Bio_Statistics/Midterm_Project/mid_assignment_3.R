#컴퓨터 환경에 맞게 데이터를 읽고 저장
setwd("D:/knou/Bio_Statistics/Midterm_Project") 
bio_data <- read.csv("./biostat_ex_data.csv")
summary(bio_data)

#데이터 전처리를 담당하는 패키지
library(dplyr) 
#범주형 변수를 factor 형태로 저장하기 
bio_data2 <- bio_data %>% mutate_at(vars(sex, Recur, stage, smoking, obesity, 
                                         Recur_1y, post.CA19.9.binary,
                                         post.CA19.9.3grp), as.factor)

#문제3-(1) H0 : 흡연자 모집단의 평균 수축기 혈압과 비흡연자 모집단의 평균 수축 혈압이 같다
#문제3-(2) H1 : 흡연 모집단의 평균 수축기 혈압과 비흡렵자 모집단의 평균 수축 혈압이 다르다

#문제3-(3) 
# 일표본 TEST : 표본의 평균이 모집단의 평균과 같은지 검정
# 대응표본 TEST : 대응하는 두 표본의 평균 차이가 특정값과 같은지 비교(before-after)
# 이표본 TEST : 두 표본의 평균이 같은지 검정 (두 데이터 세트를 갖고 비교)

t.test(SBP~smoking, data=bio_data2)


#문제3-(4) 
#p값이 0.1646으로 0.05보다 크므로 귀무가설 기각을 할수가 없다.
#t값은 검정통계량으로 두 집단의 차이의 평균을 표준오차(se)로 나눈값 
#[표준오차]와 표본평균사이의 차이의 비율
#신뢰구간 [-24.918002   4.333827]
#비흡자 평균 113.1939  흡연자 평균 123.4860 