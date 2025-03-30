# 3-1) R을 이용하여 다음과 같이 주성분분석을 실시하고 분석하라 
library(ade4)
data(deug)
names(deug)
deug_tab = deug$tab
head(deug_tab)
# csv로 데이터 저장
write.csv(deug_tab, "D:/knou/Multivariate/data/deug.csv")

# 1) 9개 변수들을 기술통계량으로 요약하시오
install.packages("summarytools")
library(summarytools)
summary(deug_tab) # 요약통계량
descr(deug_tab) # 기술통계량

# 2) 9개 변수들 사이의 상관계수행렬 구하라 
round(cor(deug_tab),2)

# 3) 고윳값을 구하고 그 고윳값들이 확보하는 누적정보 양을 구하라
deug_cor <- round(cor(deug_tab),2)
# 고윳값 확인 : eigen(고윳값 함수)
result <- eigen(deug_cor)
result_values <- result$values
result_values 

# 고윳값들이 확보하는 정보량
prop_var <- result_values / sum(result_values)
prop_var

# 6. 누적 정보량
cum_prop_var <- cumsum(prop_var)
cum_prop_var

#3) 1보다 큰 고윳값의 수와 그 고윳값들이 확보하는 누적정보의 양을 구하라 
result_values
sum(result_values > 1)  # 결과: 3
sum(prop_var[1:3]) 

#4) 스크리 그림을 그리고 해석하라 
# PCA 실행 후 그림 그리기
# 체육점수가 낮어 스케일이 다를 수 있어 COR=TRUE로 함
deug = princomp(deug_tab, cor = TRUE, score = TRUE)
screeplot(deug, type = "lines", pch = 19, main = "Scree Plot of Exam Data")

# 5) 위 결과를 이용하여 주성분을 구하라
#해당하는 결과로 주성분은 3개로 판단함
deug = princomp(deug_tab, cor = TRUE, score = TRUE)
deug

# 기여도
loadings(deug)[, 1:3]

#	설명력 및 누적 설명력
summary(deug)

# 주성분 점수 (PC1, PC2, PC3)
pc_scores <- deug$scores[, 1:3]
head(pc_scores)


# 6) bioplot을 그려보고 주성분 특징을 정리하라
biplot(deug, cex=0.5, pch=16, main = "Biplot")


