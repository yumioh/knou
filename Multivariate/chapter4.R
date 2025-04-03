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
# 번호1 : 검정, 번호2 : 빨강
plot(zbeer, col=kmc$cluster, pch=16)

# k-평균 군집 데이터의 모든 변수를 그리기
pairs(zbeer, col=kmc$cluster, pch=16, cex.labels = 1.5)

# 데이터 읽기 및 표준화 
head(USArrests)

summary(USArrests)

#표준화
zUSArrests = scale(USArrests)

# 계측정 군집 분석 진행
# 유클리드 거리로 계산, 50개의 객체가 군집 분석 대상
# 평균 영결법 사용
hc_a = hclust(dist(zUSArrests), method="average")
hc_a

# 덴드로그램 그리기
plot(hc_a, hang=-1)

# 소속 군집 알기 
hcmember = cutree(hc_a, k=5)

# 각 군집별 중심점 찾기: 각 군집별로 입력변수들의 중심점 계산
data_combined = cbind(zUSArrests, hcmember)

# hcmember 열의 소속 군집이 같은 주끼리 입력변수들의 평균을 계산
aggregate(.~hcmember, data_combined, mean)

# k평균 군집 분석 
kmc1 = kmeans(zUSArrests, 4)

# 소속 군집 산점도
pairs(USArrests, col=kmc1$cluster, pch=16, cex.labels = 1.5)
