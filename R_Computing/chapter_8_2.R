#함수의 저장

f1 <- function(x,y){
  return(x+y)
}

f2 <- function(x,y){
  return(x-y)
}

f <- f1
f(1,2)

f <- f2
f(1,2)


g <- function(h,x,y){
  h(x,y) 
}

#h의 의미 : h의 위치에 함수가 들어감

g(f1,1,2) #f1함수를 실행하라
g(f2,1,2) #f2함수를 실행하라

#매개변수가 없는 경우 
f0 <- function(){
  x <- c(1,2,3,4)
  y <- c(4,3,2,1)
  z <- x-y
  print(z)
}
#반드시 같이 괄호를 표시할것
f0()


