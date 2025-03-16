disc.data = read.table("c:/data/mva/chap7_example.txt", header=T)
attach(disc.data)
gr1.data = disc.data[gr==1,]
gr2.data = disc.data[gr==2,]
gr1.X = gr1.data[,-1]
gr2.X = gr2.data[,-1]
gr1.X = as.matrix(gr1.X)
gr2.X = as.matrix(gr2.X)
cov(gr1.X)
cov(gr2.X)
n1 = nrow(gr1.X)
n2 = nrow(gr2.X)
gr.Cov = ((n1-1)*cov(gr1.X)+(n2-1)*cov(gr2.X))/(n1+n2-2)
gr.Cov
gr1.mean = apply(gr1.X, 2, mean)
gr2.mean = apply(gr2.X, 2, mean)
diff.mean = gr1.mean - gr2.mean
diff.mean
gr.Covi = solve(gr.Cov)
coeff = gr.Covi %*% diff.mean
round(coeff,3)


