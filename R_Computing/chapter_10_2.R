library(ggplot2)
library(MASS) #car93
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
p






