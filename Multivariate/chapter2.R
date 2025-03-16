#1988년 서울 올림픽 육상 여성 7종 경기 결과

# 1. 자료 가져오기
install.packages("HSAUR2")
library(HSAUR2)
data(heptathlon)
head(heptathlon)
# 요약
summary(heptathlon)
# csv로 저장하기 
write.csv(heptathlon, file="D:/knou/Multivariate/data/heptathlon.csv")

# 2. 자료변형하기 
# 멀리뛰기, 창던지기, 포환던지기와 같은 데이터는 값이 클수록 좋은 점수이다
# 그런데 hurdles, run200m, run800m은 작은 값일수록 좋은 점수이기 때문에 자료를 변형
# 최대값에서 해당하는 기록을 빼면 값이 클수록 좋은값으로 변환해 줌
heptathlon$hurdles = max(heptathlon$hurdle) - heptathlon$hurdles
heptathlon$run200m = max(heptathlon$run200m) - heptathlon$run200m
heptathlon$run800m = max(heptathlon$run800m) - heptathlon$run800m


# 3. 주성분 분석
# 8번째 열을 제거하고 나머지 열만 선택 =>score 열 제거
hep_data = heptathlon[,-8]

#princomp() : 주성분 분석(PCA)을 수행하는 함수 (R에서 사용됨)
#hep_data : PCA를 수행할 데이터 (8번째 열을 제거한 육상 선수 데이터)
#cor=T : 상관행렬을 사용하여 PCA를 수행
#기본적으로 princomp()는 공분산 행렬을 사용하지만, 각 변수가 다른 단위를 가지는 경우 cor=T로 설정하면 표준화된 값(Z-score)을 기반으로 분석하게 됩니다.
#scores=T : 각 데이터의 주성분 점수를 저장 

hep_pca = princomp(hep_data, cor=T, scores=T)
#생성한 PCA 결과 객체의 구성 요소
names(hep_pca)
#"sdev" (Standard Deviations, 주성분들의 표준 편차
#"loadings" (주성분 로딩, Principal Component Loadings) 가중치
# "center" (데이터 평균,
# "scale" (변수들의 표준 편차
# n.obs" (관측치 개수
# "scores" (주성분 점수
# call : 재현성을 위해 원래 사용한 함수 호출 내용을 저장

# 4. 주성분분석 결과 
# 1) 결과 요약
summary(hep_pca)

#표준편차 제곱하여 고유값 구하기
eig_val = hep_pca$sdev^2

#스크리 그림과 주성분 계수
screeplot(hep_pca, type="lines", pch=19, main="scree plot")

#누적분선그림 그리기 
# 각 주성분이 전체 데이터의 분산에서 차지하는 비율
hep_var = hep_pca$sdev^2
hep_var_ratio = hep_var/sum(hep_var)
round(hep_var_ratio,3) # 소수점ㅅ 3자리까지 반올림

#cumsum : 각 주성분까지의 누적 분산 비율을 계산
plot(cumsum(hep_var_ratio), type='b', pch=19, xlab="Component", ylab='Cumulative Proportion')
title('Varian Explained')

#첫 번째(PC1)와 두 번째(PC2) 주성분에 대한 로딩 계수(가중치)를 출력
# 값이 높을수록 영향을 많이 준다 마이너스는 주성분과 반대 방향으로 작용
#longjump (0.456), hurdles (0.453), run200m (0.408), run800m (0.375), highjump (0.377) 관련성이 높음 => 달리기와 점프 관련성이 높음
# javelin (-0.842): PC2에서 압도적으로 중요한 변수 => 청던지기와 밀접한 관계

hep_pca$loadings[,c(1:2)]


#3) 주성분 점수 및 행렬도 
hep_pca$scores[, c(1:2)]
# highjump, run800, hurdles, longjump가 서로 가까운데 위치 벡터 방향도 비슷 
# run200, shot이 가깝게 위치, javelin은 다른 변수들과 다른 위치
# 가까운 거리와 방향일수록 변수들의 상관성이 높다 
biplot(hep_pca, cex=0.7, col=c("Red","Blue"))
title("Biplot")


# 주성분분석2
beer = read.csv("D:/knou/Multivariate/data/beer.csv")
summary(beer)

# 상관계수행렬 및 산점도 행렬 보기 
# 가격, 크기, 알코올함량이 상관계수가 높음 
# 평판은 다른 변수들과 상관계수가 비교적 높은 않으며, 다른 변수들과 모두 음의 상관계수를 나타냈다
round(cor(beer),2)

# 산점도 행렬
# color vs. aroma: 비교적 점들이 선형적으로 증가하는 경향이 있어 보이며, 양의 상관관계를 가질 가능성이 있음
# aroma vs. taste: 비슷한 경향을 보이며, aroma가 높을수록 taste도 높아지는 양의 상관관계가 존재할 가능성이 있음
plot(beer, pch=19)

# 주성분분석 실행
# cor = F는 공분산 이용, score=F : 각 케이스의 주성분 성분을 포함하라는 의미
beer_pca = princomp(beer, cor=F, scores=F)
beer_pca

# 결과 요약
# 첫번째 주성분이 47% 두번째 37% 설명력을 가짐
summary(beer_pca)

# 스크리 그림 및 주성분 계수
screeplot(beer_pca, type="lines", pch=19)
# 스크리 그림에서 주성분을 3개로 판단하여 1:3까지 계수 확인
beer_pca$loadings[,c(1:3)]




