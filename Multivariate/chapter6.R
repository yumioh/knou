sales = read.csv("D:/knou/Multivariate/data/sales.csv")
head(sales)

# 기술통계랑
summary(sales[,c(2:8)])

# 상관계수행렬 구하기

install.packages("ggplot2")
install.packages("GGally")
install.packages("CCA")
library(ggplot2)
library(GGally)
library(CCA)

exam = sales[,c(2:5)]
perform = sales[,c(6:8)]

# X1~X4 이루어진 객체 exam의 산점도 및 상관계수 구함
ggpairs(exam)


# X1~X4 이루어진 객체 exam의 산점도 및 상관계수 구함
ggpairs(exam)

# Y1~Y3 이루어진 객체 exam의 산점도 및 상관계수 구함
dev.new()
ggpairs(perform)

# 두 변수군 객체 exam과 perform의 상관계수행렬를 구하는 명령어
matcor(exam, perform)

# 정준상관분석 실행
cano_result = cc(exam, perform)
names(cano_result)

# 정준상관계수 저장 => 제 1,2정준상관계수가 값이 높아 유의미한 의미를 갖고 있음
cano_result$cor

# 정준상관분석 계수 결과
round(cano_result$xcoef, 3)

round(cano_result$ycoef, 3)

# 정준상관점수 & 정준변수부하 점수
cano_result$scores

# 정분변수 산점도 그리기 
w1 = cano_result$scores$xscores[,1]
y1 = cano_result$scores$yscores[,1]
cor(w1, y1)

plot(w1, y1, pch=19)

w2 = cano_result$scores$xscores[,2]
y2 = cano_result$scores$yscores[,2]
cor(w2, y2)

plot(w2, y2, pch=19)

# 3번은 상관관계가 낮음
w3 = cano_result$scores$xscores[,3]
y3 = cano_result$scores$yscores[,3]
cor(w3, y3)

plot(w3, y3, pch=19)







