#1. 단변수(univariate)범주(category)형자료 

library(MASS)
#1993년 미국에서 판매되는 93종의 자동차에 대한 여러 정보를 포함
head(Cars93) 

#기본막대그래프
#with(데이터셋, 데이터의 변수(Cars93$Type))
tab <- with(Cars93, table(Type))

#col : color, legend : 범례
barplot(tab, main="Type of Car", xlab="Type", ylab="Number of Car", col=1:6, 
        legend=c('Sporty','Van','Compact','Large','Midsize','Small'),
        names.arg=c('Sporty','Van','Compact','Large','Midsize','Small'))


#side형 막대그래프
#xtabs : crosstable(교차테이블)
tab <- with(Cars93, xtabs(~Type+AirBags))

barplot(tab, col=rainbow(6), legend =c('Compact','Large','Midsize','Small','Sporty','Van'),
        xlab = "AirBags", ylab="Number of Cars", beside = TRUE)

#stacked 막대그림
barplot(tab, col=rainbow(6), legend = c('Compact','Large','Midsize','Small','Sporty','Van'),
        ylab="Number of Cars", beside = FALSE)

#주석의 위치가 변경된 stacked 막대 그림
barplot(tab, col = rainbow(6), legend = c('Compact','Large','Midsize','Small','Sporty','Van'),
        xlim = c(0, ncol(tab)+2), xlab="AirBags", ylab="Number of Cars", 
        args.legend=list(x=ncol(tab)+2, y=max(colSums(tab)), bty="n"))

#파이차트
tab2 <- with(Cars93, table(Type))
pie(tab2, col=topo.colors(6))

names(tab2) <-  c('Compact','Large','Midsize','Small','Sporty','Van')
pie(tab2, col=topo.colors(6))
