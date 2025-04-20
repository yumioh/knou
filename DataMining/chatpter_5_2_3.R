########### 2번 풀이
install.packages("neuralnet")
library(neuralnet)
set.seed(130)

# 난수 시드 설정
set.seed(130)

# 1. 100개 데이터 포인트 생성
x_100 <- seq(0, 1, length.out = 100)
y_100 <- sin(3 * pi * x_100 / 4)
data_100 <- data.frame(x = x_100, y = y_100)

# 2. 1000개 데이터 포인트 생성
x_1000 <- seq(0, 1, length.out = 1000)
y_1000 <- sin(3 * pi * x_1000 / 4)
data_1000 <- data.frame(x = x_1000, y = y_1000)

# 3. 신경망 모형 적합 (100개 데이터)
# 연속적인 실수값을 예측하는 문제로 회귀문제이므로 linear.output=T
nn_100 <- neuralnet(y ~ x, data = data_100, hidden = 5, linear.output=T)

# 4. 신경망 모형 적합 (1000개 데이터)
nn_1000 <- neuralnet(y ~ x, data = data_1000, hidden = 5, linear.output = T)

# 적합한 모형 결과 보기
plot(nn_100)
plot(nn_1000)

# 데이터로 훈련한 모델의 예측
pred_100 <- predict(nn_100, data.frame(x = x_100))
pred_1000 <- predict(nn_1000, data.frame(x = x_1000))

# 예측값 출력
plot(1:100, pred_100)
lines(y_100, col="red")

plot(1:1000, pred_1000)
lines(y_1000, col="blue")


# 필요한 패키지 설치
install.packages("nnet")
install.packages("NeuralNetTools")

# 패키지 불러오기
library(nnet)
library(NeuralNetTools)

# 데이터 불러오기 및 준비
set.seed(123)  # 재현 가능하도록 고정
data(iris)

head(iris)

### 3번 
# 종별 25개씩 무작위 추출하여 학습 데이터 구성
# 종별로 데이터 분리
setosa_data <- iris[iris$Species == "setosa", ]
versicolor_data <- iris[iris$Species == "versicolor", ]
virginica_data <- iris[iris$Species == "virginica", ]

# 각 종별로 25개씩 임의 선택 (원래 각 종별 50개씩 있음)
setosa_indices <- sample(1:nrow(setosa_data), 25)
versicolor_indices <- sample(1:nrow(versicolor_data), 25)
virginica_indices <- sample(1:nrow(virginica_data), 25)

# 선택된 데이터 합치기
selected_data <- rbind(
  setosa_data[setosa_indices, ],
  versicolor_data[versicolor_indices, ],
  virginica_data[virginica_indices, ]
)

# 범주형 변수를 0과 1로 변환 (원-핫 인코딩)
iris_sub <- cbind(selected_data,
                  setosa = as.numeric(selected_data$Species == "setosa"),
                  versicolor = as.numeric(selected_data$Species == "versicolor"),
                  virginica = as.numeric(selected_data$Species == "virginica"))

# 신경망 모형 학습
nn_model <- neuralnet(
  setosa + versicolor + virginica ~ Sepal.Length + Sepal.Width + Petal.Length + Petal.Width,
  data = iris_sub,
  hidden = c(2,3), 
  linear.output = FALSE  # 분류 문제이므로 FALSE
)

# 신경망 시각화
plot(nn_model, rep = "best")

# 나머지 25개씩 → 테스트셋
test_data <- rbind(
  setosa_data[setosa_indices, ],
  versicolor_data[versicolor_indices, ],
  virginica_data[virginica_indices, ]
)

# 예측 수행
# 입력변수 4개 : Sepal.Length Sepal.Width Petal.Length Petal.Width 
test_input <- test_data[, 1:4]
predict_iris <- compute(nn_model, test_input)$net.result

# 실제 예측값  : predict_iris$net.result
# which.max는 각 행(샘플)에서 가장 높은 값의 열 번호를 찾아주는 함수
# 예: [0.97, 0.01, 0.02] → 1 (setosa), [0.01, 0.95, 0.03] → 2 (versicolor)
predicted_class <- apply(predict_iris, 1, which.max)

# 실제 클래스
actual_test_class <- as.numeric(factor(test_data$Species, levels = c("setosa", "versicolor", "virginica")))

# 혼동행렬과 정확도
conf_mat <- table(Predicted = predicted_class, Actual = actual_test_class)

# 훈련 데이터 정확도: 98.67 %
# mean(TRUE/FALSE)는 TRUE = 1, FALSE = 0
accuracy <- mean(predicted_class == actual_test_class)
cat("훈련 데이터 정확도:", round(accuracy * 100, 2), "%\n")

plot(nn_model, rep = "best")

