# 문제1) 다음은 13개 시중은행 대한 편리성, 신속성, 친절, 능률, 쾌적, 자동화 등 
# 점수를 나타내고 있는 자료이다 (R언어)

# 데이터 불려오기
banks_info = read.csv("D:/knou/Multivariate/data/ex1-1.csv")
head(banks_info)
summary(banks_info)

#1) 각 변수들의 히스토그램을 그리고 설명하라 
par(mfrow = c(2, 3))  # 2행 3열로 그래프 배치
hist(banks_info$convenience, main="convenience", xlab = "score")
hist(banks_info$accuracy, main = "accuracy", xlab = "score")
hist(banks_info$kindness, main = "kindness",  xlab = "score")
hist(banks_info$efficiency, main = "efficiency", xlab = "score")
hist(banks_info$pleasant, main = "pleasant", xlab = "score")
hist(banks_info$automatic, main = "automatic", xlab = "score")

#2) 산점도행렬 및 상관계수행렬을 구하고, 변수들의 관계를 설명하시오 

# 산점도 행렬 그리기
pairs(banks_numeric)

# 상관계수행렬 그리기(소수점 3번째짜리까지)
# 첫번째 열 빼기 
banks_numeric <- banks_info[, -1]
round(cor(banks_numeric, use="complete.obs"),3)

#3) 별 그림 및 얼굴그림을 그리고 설명하시오
# 별그림 그리기 
banks_numeric
stars(banks_numeric, labels = banks_info$name)


