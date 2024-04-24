
#나무지도 그림
#:vCOLOR에 대응되는 변수가 연속형 변수이기 때문에 TYPE=VALUE으로 지정
#만약 범주형이라면 TYPE="CATEGORICAL"로 지정
install.packages("treemap")
library(treemap)

data(GNI2014)
head(GNI2014)

#연속형인 경우 : 색이 진해지면 값이 크다
treemap(GNI2014, 
        index=c("continent", "iso3"), vSize = "population", vColor = "GNI", type="value")

#범주형인 경우 범주에 따라 구분에 따른 색상
treemap(Cars93, 
        index=c("Manufacturer", "Make"), vSize = "Price", vColor = "AirBags", type="categorical")

#풍선그림 
install.packages("gplots")
library(gplots)
dt <- with(Cars93, xtabs(~AirBags+Type))
#면적이 각 개수를 의미
#label=TRUE 풍선에 해당하는 값 출력(행렬값 모두 출력)
balloonplot(dt, main="Airbags by car", xlab="", ylab="", label=TRUE, show.margins = TRUE)

#두변수 모자이크 그림
library(graphics)
mosaicplot(dt, color=TRUE, las=1, main="Airbags by car type")

#다변수 모자이크 그림
mosaicplot(~DriveTrain + AirBags + Origin, 
           color=TRUE, las=1, main="DriveTrain by AirBags,Origin ", xlab="DriveTrain", data=Cars93)
















