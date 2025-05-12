# 모형평가 관련 R함수 

# 1) 연속형 목표변수의 데이터 분할 (sample) 특정 크기만큼의 데이터를 임의로 선택 
# 2) 이항형 목표변수의 데이터 분할 (createDataPartition(y, p=0.5, list=True)) : caret에서 제공하는 함수로서 데이터를 훈련용과 검증용 그룹 분할
# 3) 예측함수(prediction) : 예측값 계산시 사용 
# 4) 예측측도함수(performance) : 예측력을 계산할때 사용. tpr: 민감도, fpr: 특이도, acc/err : 예측정확도, 오분류ㅜ율

# 모든 입력변수를 포함한 선형회귀모형을 훈련 데이터로 적합 후, 단계적 변수선택법에 의해 유의한 입력변수만 선택한 최적의 모형 선택
# 예측값을 계산하고 실제값과의 차이를 제곱평균한 평균제곱차로 값 산출 

prod = read.csv("D:/knou/DataMining/data/productivityREG.csv")
head(prod)

prod$quarter = factor(prod$quarter)
prod$department = factor(prod$department)
prod$day = factor(prod$day)
prod$team = factor(prod$team)

set.seed(1234)
train.index = sample(1:nrow(prod), size = 0.7*nrow(prod), replace=F) # 1:nrow(prod) 인덱스 번호 생성
prod.train = prod[train.index,]
prod.test = prod[-train.index,] # -train.index: 해당 인덱스를 제외한 나머지 선택

# 의류 생산성 데이터에 회귀 모형 적합 및 예측결과
fit.reg = lm(productivity~., data = prod.train) # productivity: 종속변수, 나머지 설명변수
fit.step.reg = step(fit.reg, direction = "both", trace=FALSE) 
#step : 변수 자동선택, direction = "both" : 전진 선택 + 후진 제거, trace = FALSE는 중간 과정 출력을 생략

pred.reg = predict(fit.step.reg, newdata = prod.test, type="response")
mean((prod.test$productivity - pred.reg)^2)  # MSE
mean(abs(prod.test$productivity - pred.reg)) # MAE

library(rpart)

# 훈련데이터를 이용해 회귀 트리 모델을 만들고, 교차검증으로 가지치를 수행해 최적 모델을 얻는 과정

# rpart : 
# xval = 10 : 10겹 교차검증 훈련데이터를 10조각으로 나눔 그중 9개를 학습 1개를 검증용 => 이과정을 10번 반복해서 모든 조각을 한번씩 검증에 사용
# cp = 0 복잡도 가지치가 없이 트리를 최대한 분할 => 가지치기 없이 트리를 가능한 많이 분할
# minsplit : 노드 분할하기 위해 최소 5개 이상의 관측치가 있어야함 => 5개 이상일때만 분할허용
my.control = rpart.control(xval=10, cp=0, minsplit=5)

# 회귀트리만들기 
# method="anova"는 연속형 목표 변수에 사용하는 방식
fit.tree = rpart(productivity ~ ., data = prod.train, method="anova", control=my.control)

#트리모델 print
tmp = printcp(fit.tree)

# 교차검증에서 예측오차가 가장 작았던 트리 위치
k = which.min(tmp[,"xerror"])

# 예측 오차가 가장 작은 위치에서 cp값 저장 => 트리가 복잡해질수록 얼마나 가지치기를 할지 결정하는 기준값 기여도가 낮은건 잘라냄
cp.tmp = tmp[k,"CP"]

# 아까 만든 과적합 트리(fit.tree)를 cp.tmp 기준으로 가지치기
fit.prun.tree = prune(fit.tree, cp=cp.tmp)

# predict : 새로운 데이터에 대해 모델의 예측값을 계산
# type="vector" : 숫자를 벡터형태로 출력
pred.tree = predict(fit.prun.tree, newdata=prod.test, type="vector")
mean((prod.test$productivity - pred.tree)^2)  # MSE
mean(abs(prod.test$productivity - pred.tree)) # MAE

