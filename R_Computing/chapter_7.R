#R함수
#기본으로 제공하는 수치적 함수
#pi, sin(), cos(), tan(), asin(), acos(), atan(), log(), log10(), exp(), sqrt()
#min(), max(), range(x) == c(min(x), max(x)), 
#****pmin(v1, v2): 두벡터의 원소들의 같은 위치에서 작은 값, pmax() :두 벡터의 원소들의 위치 자리에서 큰값

#내장되어 있는 통계함수
#mean() : 평균, sd(): 표준편차, var():분산, median():중앙값, quantile(x,p) : %에 해당하는 값, cor(x,y): 상관계수

#조건문
#1. if ~ else
x <- c(1,2,3,4)
y <- c(2,1,4,5)

if(sum(x) < sum(y)) {
  print(mean(x))
} else {
  print(mean(y))
}

#x의 길이가 5라는 조건하에 x의 합이 10이면 length =5, sum=10을 출력
#x의 길이가 5가 아니면 length=4, sum=10을 출력 

if (length(x) == 5) {
  if (sum(x)==10) {
    print("length =5, sum=10")
  } 
} else {
  print("length = 4, sum=10")
}

#x의 길이가 4라는 조건하에 x의 합이 10이면 length=4 ,sum=10
#10이 아니면 length=5, sum=10

if (length(x) == 4) {
  if(sum(x)==10) {
    print("length=4 ,sum=10")
  }
} else {
  print("length=5 ,sum=10")
}

#ifelse 조건문

#동일한 벡터 x,y를 정의하고 x가 y보다 작으면 x값을 반환 그렇지 않으면 y값 반환
ifelse(x<y, x, y)

#****x-y의 합이 0보다 크면 positive, 작으면 negative 0보다 크지고 작지도 않으면 zero
ifelse(sum(x-y)>0, "positive", ifelse(sum(x-y) < 0,"negative","zero")) 
       
#switch : 매개변수값이 정수값을 갖게 되면 이정수값에 해당하는 순서의 실행문을 수행
#switch(매개변수, 실행문1, 실행문2,....)

#****for 반복문
#for(변수 in 반복횟수)
#초기값 정의 안해도 됨
for(j in 1:5)
  print(rep(j,j))

#1~10번까지 더하기
x <- 0
for(i in 1:10){
  x <- x+i
}
x

#while(조건) : {실행문}
#초기값 정의
i <- 1
while (i <=5) {
  print(rep(i,i))
  i <- i+1
}

#repeat : 반복문 break를 만나면 반복수행을 멈추고 작업 종료 
#초기값 정의 
i <- 1
repeat{
  if(i>5){#5보다 크면 break
    break
    }
  print(rep(i,i))
  i <- i+1
}

#예제
#repeat 반복문을 실행하여 1에서 10까지 합 구하기 
value <- 0 # 결과값
x <- 1 #횟수
repeat {
  if(x > 10) break
  value <- value+x
  x <- x+1 
}
value

#break 분기문 : 루프를 탈출하는 제어문
#중첩 루프가 사용되었을 경우, break가 위치한 해당 루프에서만 빠져 나오게 된다는 점 유의

#예시) 1~10까지 합을 구하는 루프에서 합이 25이하가 되는 시점까지 각 단계별 합계를 출력
x <- 0
for (i in 1:10){
  x <- x + i
  if(x > 25) break #25보다 크다면 break 문 수행하여 반복문 나옴
  print(x)
}

#for 반복문을 중첩 반복문 형태로 사용하여 결과 출력

for(a in 1:3){
  for(b in 1:9)
  cat(a,"*",b,"=",a*b,"\n")
  a < a+1
}

#next 분기문 : break문보다 더 강제적인 제어문
#반복문을 수행하더라도 조건을 충족하면 next 이후의 실행문을 수행하지 않고 계속 건너뛰게 됨

#while문과 next분기문을 실행하여 1 ~ 10까지 변수값을 증가시키되 8보다 작을때까지는 
#값을 출력하지 않고 8이상 값과 이들의 합 출력
k <- 1
value2 <- 0
while(k < 10){
  k <- k+1
  if(k<8) next #next 이후의 명령은 if문의 조건이 충족되는 한 아래 문장 미수행
  print(k)
  value2 <- value2+k
}


