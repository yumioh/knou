#3. 데이터프레임
# 데이터프레임은 열들이 서로 다른 형태의 객체를 가질 수 있음
# 데이터 프레임은 형태(mode)가 일반화된 행렬(matrix)
# 하나의 객체에 여러 종류의 자료가 들어갈 수 있음
# 각 열은 각각 변소와 대응
# 분석이나 모형 설정에 적합한 자료 객체

#기본함수
# read.table(file, header = FALSE, sep="") : 외부 텍스트 파일 부를 때
# data.frame(객체1, 객체2...) : 여러 종류의 객체들을 서로 결함 (성격이 다른 데이터들)
# as.data.frame(대상객체) : 다른 형태의 자료객체를 데이터 프레임의 형태로 변화 (수치형 행렬)
# write.csv(대상객체) -> ,라 구분 / write.table(객체) -> sep =","을 주지 않으면 행부분이 공백으로 저장

#예제 : read.table("d:stroy.txt", rownames = "num", header = T)
#rownames : 데이터의 num이라는 변수가 행 이름
#header = T : 첫번째줄이 변수명임을 의미

char1 <- rep(LETTERS[1:3], c(2,2,1))
#LETTERS : a,b,c 생성
char1
num1 <- rep(1:3,c(2,2,1))
num1

test1 <- data.frame(char1, num1)
test1

#예제 3-24
a1 <- c("a","b","c","d","e","f","g","h","i","j","k","l","n","m","o")
dim(a1) <- c(5,3)

data1 <- as.data.frame(a1)
data1

#데이터프레임의 결합
#cbind: 옆으로 합치기 , rbind: 아래로 합치기, merge : 병합하기

#column bind : 옆으로 붙임
cbind(test1, data1)


char1 <- rep(LETTERS[1:3], c(1,2,2))
#LETTERS : a,b,c 생성
char1
num1 <- rep(1:3,c(1,1,3))
num1

test2 <- data.frame(char1, num1)
test2
test1

#변수명이 동일하야함 : 아래에 붙임
rbind(test1, test2)

merge(test1, data1)
#같은 함수를 사용하면 같은 변수에 대해서 한번만 출력
# 알파벳 순서로 정렬되고 나머지 변수들은 옆으로 나열