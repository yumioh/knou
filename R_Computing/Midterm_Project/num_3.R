#어느 스터디 12명의 시험결과가 82,65,73,72,91,83,66,71,80,55,79,96와 같다
#1)x라는 객체에 점수를 입력하여 12개의 원소를 갖는 벡터 생성
x <- c(82,65,73,72,91,83,66,71,80,55,79,96)
x
length(x)

#2) 12개의 NA를 갖는 grade라는 객체 생성
#방법1
grade <- rep(c(NA),12)
grade
#방법2
grade2 <- rep(c(NA),length=12)
grade2

#3) x에 입력된 점수를 하나씩 읽으면서 90점 이상이면 A, 80점이상면 B,
#70점 이상이면 C, 60점 이상 D, 60점 미만 F으로 grade에 저장

#x,grade의 값을 열방향으로 결합하여 데이터프레임 생성
scoreBorad <- data.frame(score = x,grade = grade)
scoreBorad

#case_when 사용을 위한 패키지 설치
#install.packages("dplyr")
#패키지 로드
library(dplyr)

scoreBorad$grade <- case_when(
  scoreBorad$score >= 90 ~"A",
  scoreBorad$score >= 80 ~"B",
  scoreBorad$score >= 70 ~"C",
  scoreBorad$score >= 60 ~"D",
  TRUE ~ "F"
)
scoreBorad
