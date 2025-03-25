# 자동차 32종의 연비(결과변수)와 10가지 특성(설명변수)을 담고 있음
# 모든 설명변수는 연속형으로 가정하고 진행

# 데이터 불려오기 
data("mtcars")

summary(mtcars)

# 1)연비를 가장 잘 예측하는 단순회귀모형을 충분한 근거와 함께 제시
head(mtcars)

# 상관계수 확인 : wt, cyl, disp, hp 순으로 상관관계가 큼
cor(mtcars$mpg, mtcars[, -1])

# 산점도 행렬 그리기 
# 연비를 가장 잘 예측하는 변수(mpg) : disp, hp, drat가 선형 관계가 보임
# 단, cyl, gear, cs, am, carb는 범주형 함수로 선형 형태로 보이지 않음
pairs(mtcars)

# 상관계수 확인
wt_lm = lm(mpg~wt, data=mtcars)
cyl_lm = lm(mpg~cyl, data=mtcars)
disp_lm = lm(mpg~disp, data=mtcars)
hp_lm = lm(mpg~hp, data=mtcars)

summary(wt_lm)
summary(cyl_lm)
summary(disp_lm)
summary(hp_lm)

# 2) 연비 예측에 추가적으로 도움이 되는 변수를 하나 더 추가하여 중회귀모형을 적합하고자 힘
#    가장 도움이 되는 추가 변수를 선정하고 근거를 제시하시오 

install.packages("fmsb")
library(fmsb)

cor(mtcars$wt, mtcars$cyl)   # 강한 상관관계
cor(mtcars$wt, mtcars$hp)    # 선형 관계
cor(mtcars$wt, mtcars$drat)  # 음의 선형 관계 
cor(mtcars$wt, mtcars$qsec)  # 매우 낮은 상관관계

#
model_multi <- lm(mpg ~ wt + qsec + hp + disp, data = mtcars)

# VIF 계산
hp = VIF(lm(mpg ~ wt + hp, data = mtcars))
disp = VIF(lm(mpg ~ wt + disp, data = mtcars))
qsec = VIF(lm(mpg ~ wt + qsec, data = mtcars))

# qsec가 가장 낮은 상관관계를 갖고 있어서 
# 전체 회귀식 p-value는 이 회귀모형은 무의미하다. → 즉, 모든 설명변수의 계수가 0이다.
# 각 변수의 p-value는 해당 변수가 '종속변수(mpg)'에 선형적으로 영향을 주는가를 검정
qsec_multi <- lm(mpg ~ wt + qsec, data = mtcars)
disp_multi <- lm(mpg ~ wt + disp, data = mtcars)
summary(qsec_multi)
summary(disp_multi)

