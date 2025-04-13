# 필요한 패키지 설치
install.packages("nnet")
install.packages("NeuralNetTools")

# 패키지 불러오기
library(nnet)
library(NeuralNetTools)

# 데이터 불러오기 및 준비
set.seed(123)  # 재현 가능하도록 고정
data(iris)


### 1번 
# 종별 25개씩 무작위 추출하여 학습 데이터 구성
train_data <- do.call(rbind, lapply(split(iris, iris$Species), function(df) df[sample(1:nrow(df), 25), ]))
test_data <- iris[!rownames(iris) %in% rownames(train_data), ]


# 나머지를 테스트 데이터로 설정
test_data <- iris[-train_idx, ]

# 신경망 모형 학습 (은닉 노드 3개, 반복 최대 500회)
nn_model <- nnet(Species ~ ., data = train_data, size = 3, decay = 5e-4, maxit = 500)


### 2번 

# 테스트 데이터 입력변수만 사용하여 예측 수행
pred <- predict(nn_model, test_data[, 1:4], type = "class")

# 실제 값과 예측값 비교표 출력
conf_mat <- table(Predicted = pred, Actual = test_data$Species)
print(conf_mat)

# 분류 정확도 계산 및 출력
accuracy <- mean(pred == test_data$Species)
cat("2번 결과 - 분류 정확도:", round(accuracy * 100, 2), "%\n")


### 3번 
# 신경망 구조 시각화
plotnet(nn_model)

