#문제2-(1)

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
#SBP 히스토그램 그리기 
ggplot(bio_data2)+
  #히스토그램을 20간격으로 표기
  geom_histogram(aes(x = SBP), breaks=seq(0,220,20), fill="skyblue")+
  ggtitle("SBP Histogram")+ #제목
  xlab("mmHg")+ #x축
  ylab("Frequency")+ #y축 
  theme(plot.title = element_text(hjust = 0.5)) #제목 가운데 정렬

#문제2-(2)

#췌장암 환자 156명 전체의 수축기 혈압의 중앙값 : 114.6479
median(bio_data2$SBP)

# 데이터 준비 및 통계치 계산
stats <- bio_data2 %>%
  summarise(
    Min = min(SBP), #최소값 
    Q1 = quantile(SBP, 0.25), #제1사분위수
    Median = median(SBP), #중앙값
    Q3 = quantile(SBP, 0.75), #제3사분위수
    Max = max(SBP) #최대값
  ) %>%
  gather(Key, Value) 

# ggplot을 사용하여 박스플롯 생성 및 통계치 표기
p <- ggplot(bio_data2, aes(x = factor(1), y = SBP)) +
  geom_boxplot() + #박스플롯 
  geom_point(data = stats, aes(y = Value), size = 2, color = "red") + #점 표시
  geom_text(data = stats, aes(y = Value, label = round(Value, 2)), 
            hjust = 2, vjust = -0.5, color = "red", size = 3) +  #텍스트레이블
  theme(
    axis.title.x = element_blank(),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    legend.position = "none"
  )  # 테마 설정을 간소화

# 그래프 출력
print(p)

#문제2-(3) 95% 신뢰구간 : [109.94, 121.86] 
t.test(bio_data2$SBP)
