#2)리스트
#리스트를 구성하는 성분은 서로 다른 형태의 원소를 가질 수 있고, 길이도 다를 수 있음
#행렬과 배열은 동일한 형태의 원소로 이루어진 객체

a <- 1:10
b <- 11:15

#리스트를 구성하는 성분의 이름
klist <- list(vec1 = a, vec2 = b, descrip = "example") #리스트 생성
klist

#리스트의 성분 개수
length(klist)
#자료 형태
mode(klist)
#각 성분의 이름 출력
names(klist)

#리스트를 생성하고 추출하는 방법은 행렬과 배열 등과 유사 
# - 특정한 성분을 추출하거나 성분 내의 특정 원소를 추출하려면 아래와 같은 연산자 사용
# - [[]]를 사용하여 리스트에서의 성분을 추출, 성분의 이름이 부여되였다면 $연산자로 구분 

list1 <- list("A", 1:8) #list 생성
list1

list1[[3]] <- list(c("T","F"))
list1[[3]] 

list1[[2]][9] <- 9
list1

list1[[3]] <- NULL

list1

list1[[2]] <- list1[[2]][-9]
list1


a <- c(1:10)
b <- c(11:15)

#변수에 example 문자 부여
nlist <- list(vec1 = a, vec2 = b,descrip = "example")
nlist

nlist$vec1
nlist$descrip

nlist[[2]][5]
nlist$vec2[c(2,3)]