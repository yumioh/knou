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
  geom_histogram(aes(x = SBP), breaks=seq(0,220,20), fill="skyblue")+
  ggtitle("SBP Histogram")+ #제목
  xlab("mmHg")+ #x축
  ylab("Frequency")+ #y축 
  theme(plot.title = element_text(hjust = 0.5)) #제목 가운데 정렬