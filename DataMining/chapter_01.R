################ productivity pre-processing ##############

prod <- read.csv("D:/knou/DataMining/data/productivityORG.csv")
prod$date <- as.Date(prod$date, format='%m/%d/%Y') # 날짜 형식 지정
prod$quarter <- factor(prod$quarter)             # 분기 데이터를 범주형으로 변환
prod$department <- factor(prod$department)       # 부서 데이터를 범주형으로 변환
prod$day <- factor(prod$day)                     # 요일 데이터를 범주형으로 변환
prod$team <- factor(prod$team)                   # 팀 데이터를 범주형으로 변환
summary(prod)                                    # 데이터 기초 통계량 확인
attach(prod)                                     # 변수명을 직접 사용하기 위해 고정: 데이터이름$변수이름 => 변수 이름만 써도 가능
# 이상치 확인을 위한 박스플롯 시각화 (3행 4열 구성)
par(mfrow=c(3,4))
boxplot(target, col="cyan3", xlab="Target Productivity")
boxplot(smv, col="cyan3", xlab="Standard Minute Value")
boxplot(wip, col="cyan3", xlab="Work in Progress")
boxplot(over_time, col="cyan3", xlab="Overtime")
boxplot(incentive, col="cyan3", xlab="Incentive")
boxplot(idle_time, col="cyan3", xlab="Idle TIme")
boxplot(idle_men, col="cyan3", xlab="Idle Men")
boxplot(numchange, col="cyan3", xlab="Number of Changes in Style")
boxplot(numworkers, col="cyan3", xlab="Number of Workers")
boxplot(productivity, col="cyan3", xlab="Productivity")


# IQR(사분위수 범위)을 이용한 이상치 기준 계산
dout <- rep(0,15)  # 상한 임계값 저장용 벡터
dout2 <- rep(0,15) # 하한 임계값 저장용 벡터
for (i in 6:15){
  t3 <- quantile(prod[,i], 0.75)  # 3사분위수
  t1 <- quantile(prod[,i], 0.25)  # 1사분위수
  tq <- IQR(prod[,i])             # 사분위수 범위(IQR)
  dout[i] <- t3 + 1.5*tq          # 상한선: Q3 + 1.5*IQR
  dout2[i] <- t1 - 1.5*tq         # 하한선: Q1 - 1.5*IQR
}

# 이상치가 있는 행 식별
outindex <- matrix(0, 1197, 15)
for (i in 1:1197) {
  for (j in 6:15) {
    # 계산된 상/하한선을 벗어나면 1로 표시
    if (prod[i,j] > dout[j] || prod[i,j] < dout2[j]) outindex[i,j] <- 1
  }
}

# 이상치가 없는 행만 추출 및 불필요한 열 제거
prod2 <- prod[apply(outindex, 1, sum) == 0, ] # 모든 변수에서 이상치가 0인 행만 선택
prodnew <- prod2[, -c(1, 11:13)]               # 날짜 및 일부 변수 제거
head(prodnew)
write.csv(prodnew, "D:/knou/DataMining/data/productivityREG.csv", quote=F, row.names=F)

detach(prod) # 고정 해제


##########wine quality pre-rocessing###################

wine <- read.csv("D:/knou/DataMining/data/winequalityORG.csv")

attach(wine)

# 수치형 변수들에 대한 박스플롯 시각화
par(mfrow=c(3,4))
boxplot(fixed, col="cyan3", xlab="Fixed Acidity")
boxplot(volatile, col="cyan3", xlab="Volatile Acidity")
boxplot(citric, col="cyan3", xlab="Citric Acid")
boxplot(residsugar, col="cyan3", xlab="Residual Sugar")
boxplot(chlorides, col="cyan3", xlab="Chlorides")
boxplot(freeSD, col="cyan3", xlab="Free Sulfur Dioxide")
boxplot(totalSD, col="cyan3", xlab="Total Sulfur Dioxide")
boxplot(density, col="cyan3", xlab="Density")
boxplot(pH, col="cyan3", xlab="pH")
boxplot(sulphates, col="cyan3", xlab="Sulphates")
boxplot(alcohol, col="cyan3", xlab="Alcohol")

# IQR 기준으로 이상치 경계값 계산
dout <- rep(0,12)
dout2 <- rep(0,12)
for (i in 1:11){
t3 <- quantile(wine[,i], 0.75)
t1 <- quantile(wine[,i], 0.25)
tq <- IQR(wine[,i], 0.75)
dout[i] <- t3 + 1.5*tq
dout2[i] <- t1 - 1.5*tq
}

# 이상치 존재 여부 체크 (행: 1599개, 열: 12개 대상)
outindex <- matrix(0,1599, 12)
for (i in 1:1599)
for (j in 1:11){
if (wine[i,j] > dout[j] || wine[i,j] < dout2[j]) outindex[i,j] <- 1
}

# 정제된 데이터 저장
wine2 <- wine[apply(outindex, 1, sum) == 0, ] # 깨끗한 데이터만 추출
table(wine2$quality) # 품질 등급별 빈도 확인
write.csv(wine2, "D:/knou/DataMining/data/winequalityCLASS.csv", quote=F, row.names=F)
detach(wine)


############## dummy #######################
#install.packages("dummy")

library(dummy)
prod =  read.csv("D:/knou/DataMining/data/productivityREG.csv")
summary(prod)

# 범주형 변수를 factor로 재설정
prod$quarter = factor(prod$quarter)
prod$department = factor(prod$department)
prod$day = factor(prod$day)
prod$team = factor(prod$team)
summary(prod)

# 1~4번째 열(quarter, department, day, team)을 대상으로 더미 변수 생성
dvar = c(1:4)
prod2 = dummy(x=prod[,dvar])

# 다중공선성 방지를 위해 각 범주군에서 기준이 되는 열 하나씩 제거
# 다중공선성이란? 독립변수들 사이에 강한 상관관계가 나타나는 현상
# 즉, 원인 변수들이 서로 너무 비슷해서 통계 모델이 "어떤 변수가 진짜 원인인지" 갈피를 잡지 못하게 되는 상태
prod2 = prod2[,-c(5, 7, 13, 25)]

# 기존 데이터에서 범주형 열을 빼고 생성된 더미 변수 열을 합침
prod = cbind(prod[,-dvar], prod2)

# 최종 확인: 모든 열을 숫자형으로 강제 변환 (모델 입력 준비 완료)
for(i in 1: ncol(prod)) if(!is.numeric(prod[,i])) prod[,i] = as.numeric(prod[,i])