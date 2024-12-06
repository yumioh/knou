setwd("C:/workplace/knou/Bio_Statistics/Finalterm")
data <- read.csv("./data/biostat_ex_data.csv")
data.head()
library(dplyr)

data4 <- data %>% mutate_at(vars(sex, Recur, stage, smoking, obesity, Recur_1y, post.CA19.9.binary, post.CA19.9.3grp),
as.factor) %>% mutate(HTN = as.factor(ifelse(CEA>5,1,0)), log.CEA=log(CEA), log.post.CEA= log(post.CEA))
xtabs(~post.CA19.9.binary+Recur_1y, data=data4)
library(epiR)
epi.tests(xtabs(~post.CA19.9.binary+Recur_1y, data=data4)[2:1,2:1])

# 민감도(Sensitivity) : 실제 질병이 있는 환자 중 81% 양성으로 판별한 비율 => 검사가 실제 양성을 판별할 수 있는 나타냄
# 특이도(Specificity) : 실제 질병이 없는 사람 중 50%를 올바르게 음성으로 판별 => 검사가 실제로 음성을 얼마나 판별하는지 의미 
# 양성예측도(Positive Predictive Value, PPV) : 양성 결과를 받은 사람 중 46%가 실제로 질병이 있음 => 양성이라고 판단했을때 실제 양성인 경우
# 음성예측도(Negative Predictive Value, NPV) : 음성 결과를 받은 사람 중 84%가 실제로 질병이 없음 -> 음성이라고 판단했을때 실제 음성인 경우
# 양성가능도비 (Positive Likelihood Ratio, PLR): 질병이 있는 사람이 질병이 없는 사람보다 약 1.63배 더 양성 결과를 받을 가능성
# 음성가능도비 (Negative Likelihood Ratio, NLR): 질병이 없는 사람이 질병이 있는 사람보다 약 0.37배 더 음성 결과를 받을 가능성이 있음
# 전체 정확도 (Correctly Classified Proportion): 전체 사례 중 61%를 정확히 분류

# ROC 곡선 
# ROC 곡선이 뚱뚱할수록 진단 검사의 능력이 뛰어난 편

install.packages("pROC")
library(pROC)

fit <- roc(Recur_1y~post.CA19.9, data=data4)
plot(fit)

coords(fit, x="best", best.method="youden")
