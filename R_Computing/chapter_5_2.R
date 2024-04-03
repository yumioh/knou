#2)리스트
#리스트를 구성하는 성분은 서로 다른 형태의 원소를 가질 수 있고, 길이도 다를 수 있음
#행렬과 배열은 동일한 형태의 원소로 이루어진 객체

a <- 1:10
b <- 11:15

#리스트를 구성하는 성분의 이름
klist <- list(vec1 =a, vec2 = b, descrip = "example") #리스트 생성
klist

#리스트의 성분 개수
length(klist)
#자료 형태
mode(klist)
#각 성분의 이름
names(klist)
