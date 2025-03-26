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

# 2번문제 참고 코드
model_multi <- lm(mpg ~ wt + disp + cyl + hp + vs + qsec + am + carb + gear, data = mtcars)
model_multi


install.packages("fmsb")
library(fmsb)

# 2) 연비 예측에 추가적으로 도움이 되는 변수를 하나 더 추가하여 중회귀모형을 적합하고자 함
#    가장 도움이 되는 추가 변수를 선정하고 근거를 제시하시오 
# [변수 선택 하는 방법]
# - mpg와의 상관관계가 높을 것
# - wt와는 다르게 mpg에 독립적인 설명력을 제공할 것 (공선성이 낮을 것)
# - 다중회귀모형의 설명력을 실질적으로 높은 것

# mpg 간 상관계수 확인 
# cyl, disp는 상관계수가 높아 wt와 강한 상관관계가 있음
# 나머지는 중간정도의 상관관계로 가능성이 있어 보임
cor(mtcars$mpg, mtcars[, -1])

# wt와 상관관계 확인
# cyl, disp는 공성선이 높고, vs, qsec, am이 공선선이 낮거나 중간이라 선택 
cor(mtcars$wt, mtcars$disp) # 강한 상관 관계
cor(mtcars$wt, mtcars$cyl)  # 강한 상관 관계
cor(mtcars$wt, mtcars$hp)   # 중간 상관 관계 
cor(mtcars$wt, mtcars$vs)   # 중간 음의 상관관계 
cor(mtcars$wt, mtcars$drat) # 강한 음의 상관관계 
cor(mtcars$wt, mtcars$am)   # 중간 음의 상관관계
cor(mtcars$wt, mtcars$gear) # 중간 음의 상관관계
cor(mtcars$wt, mtcars$carb) # 중간 양의 상관관계
cor(mtcars$wt, mtcars$qsec) # 매우 낮은 상관관계

# VIF(분산팽창지수) 해당하는 값이 높다면 강하게 상관관계가 있음 
VIF(lm(mpg ~ wt + disp, data = mtcars))
VIF(lm(mpg ~ wt + cyl, data = mtcars))
VIF(lm(mpg ~ wt + hp, data = mtcars))
VIF(lm(mpg ~ wt + vs, data = mtcars))
VIF(lm(mpg ~ wt + am, data = mtcars))
VIF(lm(mpg ~ wt + gear, data = mtcars))
VIF(lm(mpg ~ wt + carb, data = mtcars))
VIF(lm(mpg ~ wt + qsec, data = mtcars))

# 전체 회귀식 p-value는 이 회귀모형은 무의미하다. → 즉, 모든 설명변수의 계수가 0이다.
# 각 변수의 p-value는 해당 변수가 '종속변수(mpg)'에 선형적으로 영향을 주는가를 검정
# hp, vs, am, qsec
qsec_multi <- lm(mpg ~ wt + qsec, data = mtcars)
vs_multi <- lm(mpg ~ wt + vs, data = mtcars)
am_multi <- lm(mpg ~ wt + am, data = mtcars)
hp_multi <- lm(mpg ~ wt + hp, data = mtcars)
summary(vs_multi)
summary(qsec_multi)
summary(am_multi)
summary(hp_multi)


# 3)원래 주회귀모형의 회귀계수 해석, 표준화 회귀분석 결과및 해석
#   표준화 해석이 적철치 않는 경우가 있다면 이유를 설명

# 표준화 : 단위에 의존하지 않고 두 변수 중 어떤 변수가 상대적으로 영향력이 큰지 비교 가능
lm(scale(mpg) ~ scale(wt) + scale(hp), data = mtcars)

lm(scale(mpg) ~ scale(wt) + scale(qsec), data = mtcars)
