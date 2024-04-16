#그래픽스1
#단변수 범주형 자료와 단변수 연속형 자료의 표현

library(MASS)
head(Cars93) 
#상자그림 
#IQR (q3 - q1) = (q1-1.15*IQR,q1+1.15*IQR)로 구할 수 있음
# minprice 가격 : 연속형 자료
# ~ Airbags의 모든 범주의 구분하여 보여줘라
boxplot(Min.Price~AirBags, data=Cars93)

#driver only그룹 분포 출력하기 
#subset(부분집합)
#airbags에서 driver only만 뽑아내서 주요 통계량을 보여줘 
summary(subset(Cars93, AirBags=="Driver only")$Min.Price)

#색상지정
#ylim : c(최소, 최대) 범위

boxplot(Min.Price~AirBags, data=Cars93, 
        names=c("Driver & Passenger","Driver only","None"),
        col=c("orange","cyan","yellow"), 
        ylab="Minimu Price", xlab="Airbag", 
        ylim=c(0,50), boxwex =0.25)


#상자그림 역순
#상자 그림 순서는 변수 그룹의 알파벳 순서
#at = c(3,2,1)와 같이 순서 지정
#names : 각 박스플롯의 이름들
#boxwex : 모든 박스들의 가로 크기
boxplot(Min.Price~AirBags, data=Cars93, 
        names=c("Driver & Passenger","Driver only","None"),
        col=c("orange","cyan","yellow"),
        at=c(3,2,1),
        ylab="Minimu Price", xlab="Airbag", 
        ylim=c(0,50), boxwex =0.25)

#상자그림과 실제 자료의 데이터 값까지 확인 가능
#qplot이라는 함수에서 그룹변수와 y변수를 순서대로 지정
#geom =c(boxplot, jitter) 옵션을 통해서 상자그림 생성
#jitter는 실제 데이터를 상자위에 뿌려줌
#fill=airbags 옵션은 airbags 그룹별로 상자그림의 색을 자동으로 다르게 지정
#alpha = i(.2)는 상자의 투명도

head(Cars93)

#qplot으로 상자그림 그리기
qplot(AirBags, Min.Price, data=Cars93, 
      geom = c("boxplot","jitter"),
      fill=AirBags,
      ylab="Minimum Price", xlab="Airbags", alpha=I(.2))


#ggplot를 활용하여 상자그림 그리기
#ggplot(data) + geom_boxplot()
#aes() : 매핑할 변수 넣음. 
#예: aes(변수1, 변수2)라고 하면 x축을 변수1, y축을 변수 2
#aes(color = 변수3)이면 변수 3값의 기반으로 색상 설정
#scale_fill_viridis_d() : 색상 척도 함수
#부가적인 옵션을 +을 통해 추가할 수 있다
p <- ggplot(Cars93, aes(x = AirBags, y=Min.Price)) + 
  geom_boxplot(aes(fill=AirBags))+ scale_fill_viridis_d()

#상자의 주석을 생략하고 싶으면 option으로 theme(lenged.postion="none")추가
p + theme(legend.position = "none")+xlab("AirBags") + ylab("Minimu Price")