#단계구분도 : 특정 변수 값에 따라 지역의 색깔이 달라지는 지도 maps, maptools 패키지가 설치 필요
install.packages("maps")


#버전이 맞지 않아 다운로드 불가능하여 이와 같은 방법으로 다운로드
url <- "https://cran.r-project.org/src/contrib/Archive/maptools/maptools_1.1-8.tar.gz"
download.file(url, "maptools_1.1-8.tar.gz", mode = "wb")

library(ggplot2)
library(maps)
library(maptools)
library(sf)

#설치한 패키지 내용
sessionInfo()

#2018년 전국지역안전등급 자료
safety = read.csv('D://knou//R_Computing//data_2018_지역안전등급_1.csv', header = T)
safety

#통계지리정보서비스를 접속하여 우리나라의 행정 구역 지역 다운로드
map <- read.csv('D://knou//R_Computing//mapv2_final_seoul_1.csv', header=T)
map


#단계구분도 (chroleth map)
#region 코드를 saftt자료의 region 코드와 결합하여 
#단계구분도를 그리기 위해선 ggplot의 geom_map옵션을 사용
#geom_map : 지도를 만들어줌
#map = 지리데이터
#x=map$long x축값 y=map$lat y축값 : 즉 x,y축이 잘려나가지 않도록 하기 위함
#coord_fixed() : 축 비율 고정 아무것도 없으며 1:1 비율
#xlim : x범위
ggplot(safety,aes(map_id=region,fill=교통사고))+
  geom_map(map=map,alpha=0.3, colour='snow4',size=0.1)+
  theme(legend.position=c(0.9,0.3))+labs(title="교통사고안전등급")+
  theme(plot.title=element_text(hjust=0.5))+
  scale_fill_gradientn(colours=c('white','orange','red'))+
  expand_limits(x=map$long,y=map$lat)+coord_fixed()+
  theme(axis.ticks = element_blank(), axis.text.y = element_blank())+
  theme(axis.ticks = element_blank(), axis.text.x = element_blank())+
  xlab("")+ylab("")+ xlim(80000,750000)

#전국의 화재안전등급에 대한 자료를 이용하여 단계구분도를 작성
#scale_fill_gradientn 구분을 위한 색상 설정
#aes : 데이터의 속성과 시각적 특성을 연결하는 데 사용
# 1. x와 y 축의 매핑: 데이터 프레임의 특정 열을 x축 또는 y축에 매핑합니다.
# 2. 색상과 크기 매핑: 데이터에 따라 색상이나 크기를 다르게 표현합니다.
# 3. 도형 모양: 점 또는 선의 모양을 데이터 열을 기준으로 다양하게 설정합니다.
# 4. 그룹화: 그룹별로 다른 모양이나 색상으로 데이터를 표현하는 데 활용됩니다.

ggplot(safety, aes(map_id=region, fill = 화재)) +
  geom_map(map=map, alpha=0.5, colour = 'white', size=0.0) +
  theme(legend.position = 'right')+
  scale_fill_gradientn(colours = c('yellow','red'))+labs(title = "화재안전등급") +
  theme(plot.title = element_text(hjust=0.5)) +
  expand_limits(x=map$long, y=map$lat) + coord_fixed() + theme(axis.ticks = element_blank(), axis.text.y =element_blank()) + 
  theme(axis.ticks=element_blank(), axis.text.x=element_blank())+ xlab("")+ylab("") +xlim(80000,700000)

#단계구분도-3
young_d <- read.csv('D://knou//R_Computing//data_seoul_child.csv', header=T, fileEncoding = "CP949" )
young_d
map_seoul <- read.csv('D://knou//R_Computing//mapv2_final_seoul_1.csv', header = T)

#map_seoul 데이터셋에서 시군구명 열의 고유한 값을 추출하는 방법
#table 함수는 map_seoul 데이터셋의 시군구명 열에서 각 시군구명별 빈도수를 계산 -> 테이블 객체로 반환
#name : names 함수는 table 결과에서 각 시군구명(테이블의 이름)을 추출하여 문자열 벡터로 반환

pro.list <- names(table(map_seoul$시군구명))

#빈벡터생성
xx<-vector();
yy<-vector()

#위도 경도 좌표 계산
#subset : 정 조건에 맞는 부분 집합을 추출하는 데 사용되는 함수 
# 특정 열 또는 조건을 기준으로 행을 필터링
for(jj in 1:length(pro.list)){
  #현재 시군구명에 해당하는 데이터만 추출하여 
  #각 시군구별 평균 경도와 위도를 저장
  xx[jj] <- mean(subset(map_seoul,시군구명 == pro.list[jj])$long)
  yy[jj] <- mean(subset(map_seoul, 시군구명 == pro.list[jj])$lat)
}

#cbind : 세 개의 벡터를 열(column)로 병합하여 하나의 행렬 또는 데이터 프레임을 만드는 코드
tab.x.y <- cbind(pro.list, xx, yy)

#young_d 데이터 프레임을 첫 번째 열에 따라 오름차순으로 정렬
#young_d[,1]은 young_d 데이터 프레임의 첫 번째 열을 의미
#정렬된 순서에 해당하는 인덱스(ix 값)를 반환
#ix는 정렬된 값에 해당하는 행 번호 추출
data5<-young_d[sort.int(young_d[,1],index.return=T)$ix,]

ggplot(young_d,aes(map_id=region,fill=영유아보육시설)) + 
  geom_map(map=map_seoul,alpha=0.3,colour='white',size=0.1)+ 
  theme(legend.position=c(0.1,0.8))+ scale_fill_gradientn(colours=c('yellow','red'))+ 
  expand_limits(x=map_seoul$long,y=map_seoul$lat)+ coord_fixed()+ 
  labs(x = "",y = "",title = "영유아보육시설")+ theme(plot.title = element_text(hjust = 0.5))+ 
  theme(axis.ticks = element_blank(), axis.text.y=element_blank())+ 
  theme(axis.ticks = element_blank(),axis.text.x=element_blank())+ 
  geom_text(x=xx,y=yy+400,label=data5$영유아보육시설,size=3,col=4)+ 
  geom_text(x=xx,y=yy-600,label=pro.list,size=3,col=1)


