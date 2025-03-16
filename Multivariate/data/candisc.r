library(candisc)
data71 = read.table("c:/data/mva/data7-1.txt", header=T)
data71.mod = lm(cbind(x1,x2,x3) ~ group, data=data71)
data71.mod

data71.can = candisc(data71.mod, data=data71)
data71.can

n = nrow(data71)
gr.decide = array(1,n)
score = data71.can$scores[,2]
a1 = abs(data71.can$means[1] - score )
a2 = abs(data71.can$means[2] - score )

for(i in 1:n)
  if(a1[i] >= a2[i] ) gr.decide[i] = 2

result = cbind(data71.can$score, gr.decide)
print(result)
table(result[,1], result[,3])


# iris data
iris.mod <- lm(cbind(Petal.Length, Sepal.Length, Petal.Width, Sepal.Width) ~ Species, data=iris)
iris.can <- candisc(iris.mod, data=iris)
#-- assign colors and symbols corresponding to species
col <- rep(c("red", "black", "blue"), each=50)
pch <- rep(1:3, each=50)
plot(iris.can, col=col, pch=pch)

heplot(iris.can)

# 1-dim plot
iris.can1 <- candisc(iris.mod, data=iris, ndim=1)
plot(iris.can1)

