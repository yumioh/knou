#범주형 데이터 : 범주형 변수의 분포가 여러 그룹간에 같은지 다른지 검정

#분할표 : 변수 2개의 범주별 도수를 행렬 형태의 표로 나타낸 것

#예) 5.1 최장암 환자 데이터에서 수축기 혈압이 140이상인 환자 : 고혈압, 140미만: 정상 
# 고혈압 여부와 흡연 여부로 나눔


#default 경로 설정
setwd("C:/workplace/knou/Bio_Statistics/Finalterm")
getwd()
    data0 <- read.csv("./data/biostat_ex_data.csv")
library(dplyr)

# 140이상이면 1, 140미만이면 0 저장하여 HTN라는 이분형 변수로 저장
data2 <- data0 %>%
  mutate_at(vars(sex, Recur, stage, smoking, obesity, Recur_1y, post.CA19.9.binary, post.CA19.9.3grp), as.factor) %>%
  mutate(HTN = as.factor(ifelse(SBP >= 140, 1, 0)))

#흡연 여부를 나타내는 smoking 과 HTN 분할표 만들기 :xtabs는 변수 이름을 같이 출력
xtabs(~smoking+HTN, data=data2)

#상대위험도 :어떤 사건의 위험이 두 집단 간에 얼마나 차이가 있는지 비교 
# 즉, 한 집단이 다른 집단보다 특정 사건이 발생할 확률이 얼마나 더 높거나 낮은지 나타냄
#p1 : 위험요소에 노출된 경우 질별발생 확률
#p2 : 위험요소에 노출되지 않은 경우 질병발생 확률 
# 상대위험도(RR) : p1/p0
# 상대 위험도가 크면 위험요소에 노출 됐을때 질병이 걸릴 확률이 높고, 상대 위험도가 작으면 위험요소에 노출되더라도 질병의 위험이 낮아짐 

# 오즈(승산비, 교차비): 어떤 질병이 발생활 확률이 발생하지 않을 확률의 몇배인가?를 나타냄
#p1 : 위험요소에 노출된 집단의 질병 위험의 확률
#p0 : 위험요소에 노출되지 않은 집단의 질병 위험의 확률
# p(질병발생 확률) = p1 / (1-p1) = p0 / (1-p0)

# 위험이 증가하면 오즈도 증가  즉, 오즈비가 1보다 클경우 위험요소에 노출되면 질병의 위험이 높아지고, 1보다 작을 경우 질병의 위험이 낮아진다

install.packages("epiR")
library("epiR")

epi.2by2(xtabs(~smoking+HTN, data=data2)[2:1, 2:1])

#그룹간의 비교