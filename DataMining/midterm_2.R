# 데이터 불려오기
wine = read.csv("d:knou/DataMining/data/winequalityCLASS.csv", header=TRUE)
head(wine)

# 로지스틱 회귀적합 : quality(종속변수), 나머지 변수 독립변수  
# family = binomial : 이항분포 지정
fit_glm.all = glm(quality ~ ., family = binomial, data=wine)
# 단계적 선택법 적용
fit_glm.step = step(fit_glm.all, direction = "both")
# 모형 과정
fit_glm.step$anova
# 결과요약
summary(fit.step)

# 와인품질 데이터의 예측 : type="response" 예측결과 확률로 반환
p_glm = predict(fit_glm.step, newdata=wine, type="response") 
# 0.5 보다 크면 1, 작으면 0
cutoff = 0.5
yhat = ifelse(p_glm > cutoff, 1, 0)

# 실제값과 예측값을 하나의 테이블로 만들기
tab = table(wine$quality, yhat, dnn=c("Observed", "Predicted"))

# 정확도 : 전체 중 맞게 분류된 비율
sum(diag(tab)/sum(tab)) 
# 민감도 : 좋은 와인 맞춘 비율
tab[2,2]/sum(tab[2,])
# 특이도 : 나쁜 와인 맞춘 비율
tab[1,1]/sum(tab[1,])


# 다중회귀적합 : quality(종속변수), 나머지 변수 독립변수 
fit_lm.all = lm(quality ~ ., data=wine)
# 단계적 선택법 : both 적용하여 필요한 변수만 고름
fit_lm.step = step(fit_lm.all, direction = "both")
# 모형 과정
fit_lm.step$anova
# 결과요약
summary(fit_lm.step)

# 와인품질 데이터의 예측 : type="response" 예측결과 확률로 반환
p_lm = predict(fit_lm.step, newdata=wine, type="response") 

# MSE : 오차 크기의 평균적인 수준
mean((p_lm - wine$quality)^2)
# MAE : 예측값과 실제값 사이의 평균적인 차이
mean(abs(p_lm - wine$quality))
