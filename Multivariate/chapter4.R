# Beer Band

beer = read.csv("d:/knou/Multivariate/data/beerbrand.csv", header=T, row.names=1)
head(beer)
summary(beer)

# 데이터 표준화
zbeer = scale(beer)
apply(zbeer, 2, mean)

#거리행렬 계산 절차 
zbeer_euc = dist(beer)
zbeer_euc[1]

zbeer_man = dist(zbeer, "manhattan")
zbeer_man[1]

#최단 연결법
hc_s = hclust(zbeer_euc, method='single')
hc_s

# 덴드로그램 그리기 
# 관찰자 이름 정렬 : hang=-1
plot(hc_s, hang=-1)

#최장 연결법
hc_c = hclust(zbeer_euc, method='complete')
hc_c

plot(hc_c, hang=-1)

#중심 연결법
hc_cen = hclust(zbeer_euc, method='centroid')
hc_cen

plot(hc_cen, hang=-1)

#와드 연결법
hc_w = hclust(zbeer_euc, method='ward.D')
hc_w

plot(hc_w, hang=-1)

# 소속 군집 알기 
# 계층적 군집분석을 한 후 군집 수를 정함
# 각 개체에 소속 군집 id를 할당하려면 cutree함수 이용
# 중심연결법 후 군집 수를 2~4개로 하였을때 소속 군집을 할당

hc_cen24 = cutree(hc_cen, 2:4)
hc_cen24

# k평균 군집 분석
# 군집 수가 2개
kmc = kmeans(zbeer, centers=2)
kmc

# 소속 군집 산점도 
plot(zbeer, col=kmc$cluster, pch=16)

