# 모형평가 관련 R함수 

# 1) 연속형 목표변수의 데이터 분할 (sample) 특정 크기만큼의 데이터를 임의로 선택 
# 2) 이항형 목표변수의 데이터 분할 (createDataPartition(y, p=0.5, list=True)) : caret에서 제공하는 함수로서 데이터를 훈련용과 검증용 그룹 분할
# 3) 예측함수(prediction) : 예측값 계산시 사용 
# 4) 예측측도함수(performance) : 예측력을 계산할때 사용. tpr: 민감도, fpr: 특이도, acc/err : 예측정확도, 오분류ㅜ율

# 모든 입력변수를 포함한 선형회귀모형을 훈련 데이터로 적합 후, 단계적 변수선택법에 의해 유의한 입력변수만 선택한 최적의 모형 선택
# 예측값을 계산하고 실제값과의 차이를 제곱평균한 평균제곱차로 값 산출 

# 의류생산성 데이터 : quarter, department, day, team 범주형 
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

# 1. 의류 생산성 데이터에 회귀 모형 적합 및 예측결과
fit.reg = lm(productivity~., data = prod.train) # productivity: 종속변수, 나머지 설명변수
fit.step.reg = step(fit.reg, direction = "both", trace=FALSE) 
#step : 변수 자동선택, direction = "both" : 전진 선택 + 후진 제거, trace = FALSE는 중간 과정 출력을 생략
pred.reg = predict(fit.step.reg, newdata = prod.test, type="response")
mean((prod.test$productivity - pred.reg)^2)  # MSE
mean(abs(prod.test$productivity - pred.reg)) # MAE

library(rpart)

# 2. 회귀 트리 모델

# 결정 트리 모델을 만들기 전에 트리 방식고 가지치기 조건을 조절하기 위함
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


#3. 신경망 
install.packages("neuralnet")
library(neuralnet)
library(dummy)

dvar = c(1:4)
prod2 = dummy(x=prod[,dvar]) # 1~4열에 대해 더미 변수로 변환
prod2 = prod2[, c(5,7,13,25)] # 일부 열만 선택
prod2 = cbind(prod[,-dvar], prod2) # 선택한 열을 제외하고 새로운 데이터프레임 만들기

# 숫자형태가 아닌걸 numberic로 변환
for(i in 1: ncol(prod2)) if(!is.numeric(prod2[,i]))
  prod2[,i] = as.numeric(prod2[,i])

set.seed(1234)
train.index = sample(1:nrow(prod2), round(0.7*nrow(prod2)))
prod2.train = prod2[ train.index,] # 훈련데이터                            
prod2.test  = prod2[-train.index,] # 테스트데이터

max1 = apply(prod2.train, 2, max) # 열의 방향에서 최대값
min1 = apply(prod2.train, 2, min) # 열의 방향에서 최소값

# 정규화 0~1스케일링
sdat.train = scale(prod2.train, center = min1, scale = max1 - min1)
sdat.train = as.data.frame(sdat.train)

sdat.test = scale(prod2.test, center = min1, scale = max1 - min1)
sdat.test = as.data.frame(sdat.test)

vname = names(sdat.train) # 모든 변수 이름을 저장

# as.formula : 회귀수식 종석변수 ~ 독립변수1 + 독립변수2 ....
# paste : 문자열 연결 함수, as.formula : 문자열로 자동 생성 후, 공식적인 formula 객체로 바꿔주는 함수
f = as.formula(paste("productivity ~", paste(vname[!vname %in% "productivity"], collapse = " + ")))

# 3. 신경망 모델 학습 
# data : 훈련데이터
# hidden : 은닉층
# linear.output=T : 출력값을 연속형
fit.nn = neuralnet(f, data=sdat.train, hidden=c(3,1), linear.output=T) 

# 신경망 모델 neuralnet으로 만든것 
pred.nn = predict(fit.nn, sdat.test) 
# 역정규화 original = normalized * (max - min) + min => 정규화된 0~1값을 원래 단위로 변환
# productivity의 변수 위치가 7
pred.nn = pred.nn*(max1[7]-min1[7])+min1[7]

mean((prod.test$productivity - pred.nn)^2)  # MSE 
mean(abs(prod.test$productivity - pred.nn)) # MAE 


# 4. 랜덤포레스트로 학습하기 
library(randomForest)

class(c)
# productivity을 예측하는 randomForest 모델 학습
# productivity : 종속변수 ~ 나머지 모든 변수 
# data=prod.train : 학습 데이터 셋
# ntree : 생성할 트리 개수
# mtry : 각 트리의 분기점에서 무작위로 고를 독립변수 수 
# importance : 훈련 후 각 변수의 중요도를 확인 가능
# na.action = na.omit  : 결측값 무시
fit.rf = randomForest(productivity ~ .,data=prod.train, ntree = 100, mtry=5, importance=T, na.action=na.omit)

# 학습된 모델을 사용해 테스트 데이터 셋으로 값 예측
# response는 회귀일 경우 예측된 수치값
pred.rf = predict(fit.rf, newdata = prod.test , type="response")
mean((prod.test$productivity - pred.rf)^2)  # MSE
mean(abs(prod.test$productivity - pred.rf)) # MAE

# mse성능비교: MSE가 작을수록 성능이 좋음 => 랜덤포레스트
mean((prod.test$productivity - pred.reg)^2)  # 선형회귀
mean((prod.test$productivity - pred.tree)^2) # 결정트리
mean((prod.test$productivity - pred.nn)^2)   # 신경망
mean((prod.test$productivity - pred.rf)^2)   # 랜덤포레스트

# MAE 성능비교 : MAEs가 작을수록 성능이 좋음 => 랜덤 포레스트
mean(abs(prod.test$productivity - pred.reg)) 
mean(abs(prod.test$productivity - pred.tree))
mean(abs(prod.test$productivity - pred.nn))   
mean(abs(prod.test$productivity - pred.rf)) 

# 그래프 그리기
par(mfrow=c(2,2), pty="s")

# x,y축 범위
a = min(prod.test$productivity) 
b = max(prod.test$productivity)

# 의류생상선 데이터의 관측값과 예측값의 산점도
plot(prod.test$productivity, pred.reg, xlim=c(a,b), ylim=c(a,b), xlab="Observed", ylab="Predicted", main="Regression")
abline(a=0, b=1, lty=2) # 선스타일 점선 : lty=2

plot(prod.test$productivity, pred.tree, xlim=c(a,b), ylim=c(a,b), xlab="Observed", ylab="Predicted", main="Decision Tree")
abline(a=0, b=1, lty=2)

plot(prod.test$productivity, pred.nn, xlim=c(a,b), ylim=c(a,b), xlab="Observed", ylab="Predicted", main="Neural Network")
abline(a=0, b=1, lty=2)

plot(prod.test$productivity, pred.rf, xlim=c(a,b), ylim=c(a,b), xlab="Observed", ylab="Predicted", main="Random Forests")
abline(a=0, b=1, lty=2)

install.packages("devtools")
devtools::install_version("parallelly", version = "1.44.0", type = "source")
devtools::install_version("future", version = "1.49.0")


### 와인데이터 ##########
install.packages("sparsevctrs")
install.packages("lava")

install.packages("recipes", type = "binary")
install.packages("hardhat", type = "binary")

install.packages("caret")
library(caret)

wine = read.csv("D:/knou/DataMining/data/winequalityCLASS.csv")

cutoff = 0.5

set.seed(1234)
train.index = createDataPartition(wine$quality, p=0.7, list=FALSE)
wine.train = wine[train.index,]
wine.test = wine[-train.index,]

## 1. 로지스틱회귀

# 1. 모델 학습 : 
# 로직스틱회귀(glm)
# 종속변수 : quality
# 이항분류 모델 : family=binomial(link="logit")
fit.reg = glm(quality~., family=binomial(link="logit"), data=wine.train)

# 2. 단계별 선택법 
# direction="both" : 전진 선택 + 후진 제거 방식 모두 사용
# 전진선택 : 아무 변수도 없는 상태에서 출발해서 유의미한 변수 추가
# 후진 제거 : 모든 변수를 포함하고 덜 중요한 변수 제거 
# both : 변수 추가 후 다른 변수가 더이상 중요하지 않게 되면 제거(추가, 제거 반복)
# trace=FALSE : 중간 결과를 콘솔 출력 안함
fit.step.reg = step(fit.reg, direction="both", trace=FALSE)

# 3. 예측수행 
# predict함수로 wine.test에 대한 확률값 계산
# type="response" : 0,1 사이의 확률값 반환
p.test.reg = predict(fit.step.reg, newdata=wine.test, type="response")

# 이진 분류 처리 
# cutoff값을 기준으로 1,0의 값으로 처리 
yhat.test.reg = ifelse(p.test.reg > cutoff, 1, 0)

# 테이블 만들기
tab = table(wine.test$quality, yhat.test.reg, dnn=c("Observed","Predicted"))
print(tab)           


sum(diag(tab))/sum(tab) # 정확도 (120+142)/(120+48+48+142)
tab[2,2]/sum(tab[2,])   # 민감도 142/190
tab[1,1]/sum(tab[1,])   # 특이도 120/168


## 2. 결정 트리 

library(rpart)

# 트리생성시 사용할 하이퍼파라미터 설정 
# xval = 10 : 10겹 교차검증 
# cp = 0 : 초기엔 분할 허용 
# minsplit = 5 : 현 노드를 분할 하려면 최소 5개 노드 필요
my.control = rpart.control(xval=10, cp=0, minsplit=5)

# 결정트리 모델 생성 => 과적합
fit.tree = rpart(quality~., data=wine.train, method = "class", control = my.control)

# 복잡도 cp별로 교차검증 오차로 출력
# cp값이 작을수록 트리를 많이 분할, cp값이 클수록 간단한 트리 생성
# 평균오류률은 10번 교차검증 후 각 번의 예측 오류율을 평균해서 계산한 값
tmp = printcp(fit.tree)

# 최소 오류 위치 찾기 
k = which.min(tmp[,"xerror"])

# 해당하는 cp값 저장
cp.tmp = tmp[k,"CP"]

# 가지 치기 : 최적 cp값을 기준으로 불필요한 분할을 제거한 트리 생성 => 최적의 분류 트리 생성
fit.prun.tree = prune(fit.tree, cp=cp.tmp)

# [,1] : 클래스가 0일 확률
# [,2] : 클래스가 1일 확률
p.test.tree = predict(fit.prun.tree, newdata=wine.test, type="prob")[,2]

# 클래스 1, 0으로 분류
yhat.test.tree = ifelse(p.test.tree > cutoff, 1, 0)

tab = table(wine.test$quality, yhat.test.tree, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix
sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity

## 3. 신경망 모형

install.packages("neuralnet")
library(neuralnet)
library(caret)

set.seed(1234)
train.index = createDataPartition(wine$quality, p=0.7, list=FALSE)
wine.train = wine[ train.index,] #train data
wine.test  = wine[-train.index,] #test data

max1 = apply(wine.train, 2, max) 
min1 = apply(wine.train, 2, min)

# 훈련 데이터 정규화
gdat.train = scale(wine.train, center = min1, scale = max1 - min1)
gdat.train = as.data.frame(gdat.train)

gdat.test = scale(wine.test, center = min1, scale = max1 - min1)
gdat.test = as.data.frame(gdat.test)

# 데이터프레임 모든 변수명 들고 오기
gn = names(gdat.train)
f = as.formula(paste("quality ~", paste(gn[!gn %in% "quality"], collapse = " + ")))

# 신경망 모델 만들기
# 은닉층 2개 노드, 두번째 은닉층 1개 노드 설명
# linear.output=F : 출력을 0~1사이의 확률값으로 반환(시그모이드 함수 사용)
fit.nn = neuralnet(f, data = gdat.train, hidden=c(2,1), linear.output=F) 

# 테스트 데이터 예측
p.test.nn = predict(fit.nn, gdat.test) 
yhat.test.nn = ifelse(p.test.nn > cutoff, 1, 0)

# 교차표 만들기
tab = table(gdat.test$quality, yhat.test.nn, dnn=c("Observed","Predicted"))
print(tab)             

#성능지표 계산
sum(diag(tab))/sum(tab) # 정확도
tab[2,2]/sum(tab[2,])   # 민감도
tab[1,1]/sum(tab[1,])   # 특이도

##3.배깅모형 적함 및 예측결과
library(rpart)
library(adabag)

# 범주형 변수가 아닌 경우 범주형으로 변경 => 판별분석, 로지스틱회귀, 분류모델에선 종속변수가 범주형이라야 정상적으로 작동
if(!is.factor(wine.train$quality)) wine.train$quality = factor(wine.train$quality) 
if(!is.factor(wine.test$quality)) wine.test$quality = factor(wine.test$quality)

my.control = rpart.control(xval = 0, cp=0, minsplit=5)

# method : 분류작업에 사용 예측 결과를 클래스 형태로 반환
fit.bag = bagging(quality ~ ., data = wine.train, mfinal=100, control=my.control)

# predict.bagging : 배깅 예측 함수 
# 1일 확률 : $prob[,2]
p.test.bag = predict.bagging(fit.bag, newdata=wine.test)$prob[,2]

# 기준 값에 따라 라벨링levels(wine.test$quality)[2] : 1, levels(wine.test$quality)[1] : 0
yhat.test.bag = ifelse(p.test.bag > cutoff, levels(wine.test$quality)[2], levels(wine.test$quality)[1])


tab = table(wine.test$quality, yhat.test.bag, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix
sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity


## 4. 부스팅모형
library(rpart)
library(adabag)

# factor :  범주형 데이터 저장
# level : factor 객체가 가질 수 있는 고유 범주를 나열할것 

# 범주형 아닌 경우 범주형으로 전환
if(!is.factor(wine.train$quality)) wine.train$quality = factor(wine.train$quality) 
if(!is.factor(wine.test$quality)) wine.test$quality = factor(wine.test$quality)

my.control = rpart.control(xval=0, cp=0, maxdepth=4)
# boos = TRUE 부트 방식 사용 / mfinal = 100 : 100개의 약한 학습기 생성
fit.boo = boosting(quality ~ ., data = wine.train, boos=T, mfinal=100, control=my.control)

p.test.boo = predict.boosting(fit.boo, newdata=wine.test)$prob[,2] #probabilities
yhat.test.boo = ifelse(p.test.boo > cutoff, levels(wine.test$quality)[2], levels(wine.test$quality)[1])

tab = table(wine.test$quality, yhat.test.boo, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix

sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity

## 5.랜덤포레스트

library(randomForest)

if(!is.factor(wine.train$quality)) wine.train$quality = factor(wine.train$quality) 
if(!is.factor(wine.test$quality)) wine.test$quality = factor(wine.test$quality)

# ntree : 트리개수

fit.rf = randomForest(quality ~ ., data = wine.train, ntree=100, mtry=5, importance=T, na.action=na.omit)

p.test.rf = predict(fit.rf, newdata=wine.test , type="prob")[,2] #probabilities
yhat.test.rf = ifelse(p.test.rf > cutoff, levels(wine.test$quality)[2], levels(wine.test$quality)[1])

# dnn : 행렬이름 
tab = table(wine.test$quality, yhat.test.rf, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix

sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity

### ROC and AUC 
install.packages("ROCR")
library(ROCR)

# Making predictions
# prediction() 함수는 ROC, AUC 등 다양한 성능지표 계산을 위한 입력 객체를 생성
# "tpr" : 민감도 / "fpr" : 1 - 특이도
print(class(p.test.reg))
pred.reg  = prediction(p.test.reg, wine.test$quality)  
perf.reg = performance(pred.reg,"tpr","fpr")
pred.tree = prediction(p.test.tree, wine.test$quality)
perf.tree = performance(pred.tree,"tpr","fpr")
pred.nn   = prediction(p.test.nn, wine.test$quality)  
perf.nn = performance(pred.nn,"tpr","fpr")
pred.bag  = prediction(p.test.bag, wine.test$quality) 
perf.bag = performance(pred.bag,"tpr","fpr")
pred.boo  = prediction(p.test.boo, wine.test$quality)
perf.boo = performance(pred.boo,"tpr","fpr")
pred.rf   = prediction(p.test.rf, wine.test$quality)  
perf.rf = performance(pred.rf,"tpr","fpr")


# Drawing ROCs : 값이 높을 수록 좋은 성능
plot(perf.reg,  lty=1, col=1, xlim=c(0,1), ylim=c(0,1),xlab="1-Specificity", ylab="Sensitivity", main="ROC Curve")
plot(perf.tree, lty=2, col=2, add=TRUE)
plot(perf.nn,   lty=3, col=3, add=TRUE)
plot(perf.bag,  lty=4, col=4, add=TRUE)
plot(perf.boo,  lty=5, col=5, add=TRUE)
plot(perf.rf,   lty=6, col=6, add=TRUE)

lines(x = c(0, 1), y = c(0, 1), col = "grey")
legend(0.6,0.3, c("Regression","Decision Tree","Neural Network","Bagging","Boosting","Random Forest"), lty=1:6, col=1:6)

# Computing AUCs : 값이 높을 수록 좋은 성능
performance(pred.reg, "auc")@y.values #Regression
performance(pred.tree,"auc")@y.values #Decision Tree
performance(pred.nn,  "auc")@y.values #Neural Network
performance(pred.bag, "auc")@y.values #Bagging
performance(pred.boo, "auc")@y.values #Boosting
performance(pred.rf,  "auc")@y.values #Random Forest
# 민감도는 배깅모형이 크고 특이도는 랜덤포레스트 모형이 가장 크다 => 예측정확도는 랜덤포레스트모형이 가장 크다





