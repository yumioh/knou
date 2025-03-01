#문제2-(1)

#파일 읽고 저장하기 
setwd("D:/knou/Bio_Statistics/Midterm_Project")
bio_data <- read.csv("./biostat_ex_data.csv")
summary(bio_data)

#범주형 변수를 factor 형태로 저장하기 
#연속형 변수 numeric형태, 범주형 변수는 factor로 저장 후 분석하는 것이 적절
library(dplyr) #데이터 전처리를 담당하는 패키지
library(ggplot2)
#muate_at() : 지정한 변수들에 대해 계산식을 적용시키는 명령어
#파이프 함수 : 왼쪽에 있는 표현의 결과를 오른쪽에 있는 함수의 첫번째 인수로 전달
bio_data2 <- bio_data %>% mutate_at(vars(sex, Recur, stage, smoking, obesity, Recur_1y, post.CA19.9.binary,
              post.CA19.9.3grp), as.factor)

#수축기 혈압 분포를 히스토그램
hist(bio_data2$SBP, main = "SBP Histogram",
     xlab = "mmHg", ylab = "빈도", col="skyblue")

ggplot(bio_data2)+geom_histogram(aes(x = SBP), breaks=seq(0,220,20))


#췌장암 환자 156명 전체의 수축기 혈압의 중앙값 : 114.6479
median(bio_data2$SBP)

#췌장암 환자 박스 플롯
ggplot(bio_data2)+geom_boxplot(aes(x=1, y=SBP)) + scale_x_continuous(breaks = NULL) +
  theme(axis.title.x = element_blank())


# 박스플롯 생성 및 평균값 추가
p <- ggplot(bio_data2, aes(x=factor(1), y=SBP)) +
  geom_boxplot() +
  stat_summary(fun=mean, geom="point", shape=20, size=3, color="red") + # 평균값 표시
  theme(axis.title.x = element_blank(), axis.text.x = element_blank(), axis.ticks.x = element_blank()) # x축 레이블, 텍스트, 눈금 제거


summary(bio_data2$SBP)

#2-(3) 95% 신뢰구간 : [109.94, 121.86] 
mean(bio_data2$SBP)
t.test(bio_data2$SBP)

#3번
#(1) H0: 흡연자 모집단의 평균 수축기 혈압과 비흡연자 모집단의 평균 수축 혈압이 같다
#(2) H1 : 흡연 모집단의 평균 수축기 혈압과 비흡렵자 모집단의 평균 수축 혈압이 다르다
#(3)
# 일표본 TEST : 표본의 평균이 모집단의 평균과 같은지 검정
# 대응표본 TEST : 대응하는 두 표본의 평균 차이가 특정값과 같은지 비교(BEFRO-AFTER)
# 이표본 TEST : 표본의 평균이 같은지 검정 (두 데이터 세트를 갖고 비교)

t.test(SBP~smoking, data=bio_data2)

#p값이 0.1646으로 0.05보다 크므로 귀무가설 기각을 할수가 없다.
#t값은 검정통계량으로 두 집단의 차이의 평균을 표준오차(se)로 나눈값 
#[표준오차]와 표본평균사이의 차이의 비율
#신뢰구간 [-24.918002   4.333827]
#비흡자 평균 113.1939  흡연자 평균 123.4860 



library(ggplot2)
library(dplyr)

# 데이터 준비 및 통계치 계산
stats <- bio_data2 %>%
  summarise(
    Min = min(SBP),
    Q1 = quantile(SBP, 0.25),
    Median = median(SBP),
    Q3 = quantile(SBP, 0.75),
    Max = max(SBP)
  ) %>%
  gather(Key, Value)  # 데이터를 긴 형식으로 변경

# ggplot을 사용하여 박스플롯 생성 및 통계치 표기
p <- ggplot(bio_data2, aes(x = factor(1), y = SBP)) +
  geom_boxplot() +
  geom_point(data = stats, aes(y = Value), size = 2, color = "red") +  # 점 표시
  geom_text(data = stats, aes(y = Value, label = round(Value, 2)), hjust = 2, vjust = -0.5, color = "red", size = 3) +  # 텍스트 레이블
  theme(
    axis.title.x = element_blank(),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    legend.position = "none"
  )  # 테마 설정을 간소화

# 그래프 출력
print(p)
