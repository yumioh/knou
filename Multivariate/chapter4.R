# Beer Band

beer = read.csv("d:/knou/Multivariate/data/beerbrand.csv", header=T, row.names=1)
head(beer)
summary(beer)

# 데이터 표준화
zbeer = scale(beer)
apply(zbeer, 2, mean)