#행렬 : 동일한 형태로 구성된 2차원 데이터 구조
#벡터와 마찬가지로 수치형, 문자형, 논리형 중 하나의 원소만 갖는다 

#행렬의 속성
#length : 자료의 개수, mode : 자료의 형태, dim:행열의 개수, dimnames: 행열의 이름
matr <- matrix(1:9, nrow=3) :#3열3행 행렬 생성, nrow:행의 개수, ncol :열의 개수
matr

length(matr) #원소의 개수
mode(matr) #원소의 형태
dim(matr) #행렬의 개수 

#matrix : 함수를 직접 생성
#cbind : 벡터를 병함
#rbind : 벡터를 병함
#dim : 차원을 직접 지정

#byrow를 true로 들어가 row방향으로 들어감 default = 열방향
#martrix(data, nrow=, ncol=, byrow=FALSE, dimnames = NULL)
v1 <- c(1:3)
v2 <-c(4:6)
v3 <- c(1:6)
cbind(v1, v2)
rbind(v1, v2)
dim(v3) <- c(2, 3) #행렬을 직접 지정하여 원래 값에서 overwrite되어 출력

r1 <- c(1:3)
r2 <- c(4:6)
r3 <- c(7:9)

rbind(r1,r2,r3) #행의 기준으로 결합
cbind(r1,r2,r3) #열의 기준으로 결함

ma <- 1:9
dim(ma) <- c(3,3)

#[]을 이용하여 일부 원소 추출
#apply(행렬, 조건, FUN,....) : 행열 연산
#sweep(행렬, 조건, STATS, FUN="-",....) : 행열 연산

#1~9까지 원소를 갖는 행 기준의 3행3열 행렬을 만듬
matr2 <- matrix(1:9,ncol=3, byrow=T) #행기준으로 3열 행렬 생성
matr2
matr2[,3]
matr2[1,]
matr2[matr2[,3]>4,2] #3열에서 4보다 큰 해의 값중 2열 모든 값
matr2[2,3] #2행3열 값 추출

height <- c(140, 155, 142, 175)
size1 <- matrix(c(130, 26, 110, 24, 118, 25, 112, 25), ncol=2, byrow=T,
                 dimnames=list(c("LEE","KIM","PARK","CHOI"),c("WEIGHT","waist"))) #행렬이름 부여
size <- cbind(size1, height)
size

colnames <- apply(size,2,mean) # 2: 열의 연산, 1이면 행의 연산
colnames

colvar <- apply(size, 2, var) #2: 열의 분산
colvar

rowvar <- apply(size, 1, var) #행의 분산
rowvar

#sweep(size, 1, c(1,2,3,4), "*") #각 행에 1,2,3,4 더해줌
#sweep(size, 1, c(1,2,3,4), "-")

#행렬 연산과 관련된 함수
# t(A) : 전치행렬 구하는 함수
# %*% : 행렬의 곱셈 A%*%B
#solve : 역행렬


#1~4까지의 값을 갖는 열 기준 행렬 m1과 
#5~8까지의 값을 갖는 열 기준의 행렬 m2를 생성하고 
#두행렬의 곱 
#m1의 전치 행렬 및 m1의 역행렬 구하기 

m1 <- matrix(c(1:4), nrow=2)
m2 <- matrix(c(5:8), nrow=2)
mul <- m1%*%m2
mul

solve(m1)
t(m1)

