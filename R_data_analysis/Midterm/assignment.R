install.packages("cherryblossom")
library(cherryblossom)
head(run09)

# 문제1) 참가자 중 여성이면서 성씨(last name)가 Park인 참가자는 총 몇 명인가? 
sum(run09$gender == "F" & run09$last == "Park")

install.packages("tidyverse")
library(tidyverse)
# 문제2)여성인 참가자 중 나이(age)가 결측인 참가자가 1명 있다. 이 참가자의 나이는 사실 40세라고 하자. 
# 여성 참가자 전체를 나이를 기준으로 35세 이상인 그룹과 35세 미만인 그룹으로 나누는 변수를 생성하시오. 
# 각 그룹에는 몇 명의 참가자가 있는가? (3점)

run_f <- run09 %>% filter(gender == "F") %>% 
  mutate(age=replace(age, is.na(age), 40), age.group = as.factor(ifelse(age >=35, 1, 0)))
summary(run_f)

library(ggplot2)
# 문제3) 여성인 참가자만 고려했을 때, 2번 문항에서 생성한 나이 그룹 별로 경기 기록(net_time)의 
# 분포가 어떻게 다른지 나타내는 상자 그림을 그리시오. 그래프의 제목으로 본인의 학번을 출력하시오.
ggplot(data=run_f) + 
  geom_boxplot(aes(x=age.group, y=net_time)) +
  labs(title = "202435-367763") + 
  theme(plot.title = element_text(hjust = 0.5))

# 문제4) 여성인 참가자만 고려했을 때, 2번 문항에서 생성한 나이 그룹 별로 
# 경기 기록(net_time)의 평균이 다른지 t-검정을 수행하시오.
t.test(net_time~age.group, data=run_f)

# 문제5) 여성 참가자 중에서 경기 기록(net_time)이 90 미만인 참가자의 비율은 전체의 몇 퍼센트인가?
sum(run_f$net_time < 90) / nrow(run_f)

# 문제6) 여성 참가자의 경기 기록(net_time)의 분포를 나타내는 히스토그램을 그리시오. 
# 그래프의 제목으로 본인의 학번을 출력하시오. (4점)
ggplot(data=run_f) +
  geom_histogram(aes(x=net_time)) +
  labs(title = "202435-367763") + 
  theme(plot.title = element_text(hjust = 0.5))

# 문제7) 여성 참가자의 데이터를 이용하여, 나이(age)를 가로축으로 하고, 
# 경기 기록(net_time)을 세로축으로 하는 산점도를 그리시오. 
# 그래프의 제목으로 본인의 학번을 출력하시오
ggplot(data=run_f) +
  geom_point(mapping = aes(x=age, y=net_time)) +
  labs(title = "202435-367763") + 
  theme(plot.title = element_text(hjust = 0.5))


# 문제8) 여성 참가자의 데이터를 이용하여, 나이(age)를 독립변수로, 
# 경기 기록(net_time)을 종속변수로 하는 선형회귀분석을 수행하시오. 
# 회귀직선의 기울기는 얼마인가? 
run <- lm(net_time~age, data=run_f)
summary(run)




