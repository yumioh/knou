#네트워크 그림
#어떤 개체간의 관계를 선으로 연결한 그림 
#igraph 패키지를 설치하여 구현
#네트워크 그림에서 개체들은 vertex로 표현되고 각 개체 사이엥 연결된 선은 edge로 정의

install.packages("igraph")
library(igraph)

#그림을 두개를 동시에 보여주기 위함 
#화면 2개로 나눔 : 1행에 2열(가로로 두개 보여짐)
split.screen(figs=c(1,2))

#첫번째 스크린에 그림 보여줌
screen(1)
#방향성 없음 
#1,2 / 2,3 / 3,1 연결하라
#n은 노드의 수
g1 <- graph(edges = c(1,2,2,3,3,1), n=3, directed = F)
plot(g1)

#두번째 스크린
screen(2)
#방향성 있음
g1 <- graph(edges = c(1,2,2,3,3,1), n=3, directed = T) 
plot(g1)

#네트워크 그림 -2 isolated points
split.screen(figs = c(1,2))

#양방향의 화살이 생김
screen(1)
g1 <- graph(edges = c(1,2, 2,3, 3,1, 1,3), n=3)
plot(g1, edge.arrow.size=0.5)

#n=7 개체가 7개인데 3개만 방향성을 넣음
screen(2)
g2 <- graph(edges = c(1,2, 2,3, 3,1), n=7)
plot(g2, edge.arrow.size=0.5)

#네트워크 그림 vertex이름
#이름이 적힌 순서에 따라 방향성이 정해짐 
#문자로도 가능
g3 <- graph(c("seoul", "busan","busan","gwangju","gwangju", "seoul"))
plot(g3)


#네트워크 그림 디자인 주기 
#edge.arrow.size: 화살표의 크기
#vertex.color: 노드의 색상을 지정
#vertex.size: 노드의 크기
#vertex.frame.color: 노드 테두리의 색상
#vertex.label.color: 노드 레이블의 색상
#vertex.label.cex: 노드 레이블의 크기
#vertex.label.dist: 노드 레이블의 거리를 지정
#edge.curved: 에지를 곡선으로 그리는 정도
g4<-graph(c("Seoul", "Pusan", "Pusan", "Gwangju", "Gwangju", "Seoul", "Seoul",
            "Daegu", "Seoul", "Deajeon"), isolates=c("Sejong", "Ulsan") )
plot(g4, edge.arrow.size=0.5, vertex.color="gold", vertex.size=30, 
     vertex.frame.color="gray", vertex.label.color="black",
     vertex.label.cex=0.6, vertex.label.dist=2,edge.curved = 0.2)

#네트워크 그림

#연결된 모양이 출력
#edge는 일종의 선으로 서로의 관계를 나타냄
E(g4) 
#vertex : 꼭지점이므로 꼭지점에 위차한 이름이 나옴

#새로운 변수 입력
V(g4)$name
V(g4)$Type <- c("Special", "Metropolitan", "Metropolitan","Metropolitan", "Metropolitan","Multi-functional Administrative","Metropolitan")
V(g4)$Pop <- c(9.7, 3.4, 5.5, 2.4, 1.5, 4.27, 2.1) 

#선이기 때문에 5개 
E(g4)$traffic_volume <- c(2.8, 4.5, 8.7, 5.64, 4.9)
E(g4)$traffic <- c('train','plane','train','highway','highway')
E(g4)$ttype <- c('business','business','business','travel','travel')

#vertex.label.dis : 레이블을 그릴 때 노드로부터의 거리를 지정
#첫 번째 노드는 "pink"로 설정, 두 번째부터 다섯 번째 노드까지는 "skyblue"로 설정
#여섯 번째 노드는 "peru"로 설정, 일곱 번째 노드는 다시 "skyblue"로 설정
#edge.label = 엣지 레이블 출력
plot(g4,edge.arrow.size=0.5, vertex.label.color="black",
     vertex.label.dist=2, 
     vertex.color=c("pink", rep("skyblue",4),"peru", "skyblue"),edge.curved=0.2,
     edge.label = E(g4)$ttype)


#네트워크 그림 -6 엣지커브 다르게 지정
plot(g4, edge.arrow.size=1.5, vertex.label.color="black", vertex.label.dist=2, 
     vertex.color=c( "pink",rep("skyblue",4),"peru","skyblue"),  edge.curved=c(0.1,0.9,0.3,0.4,0.1 ))

#네트워크 그림 vertex size
plot(g4, edge.arrow.size=1.5, vertex.size=30, vertex.frame.color="gray", 
     vertex.label.color="black", vertex.label.cex=1.2, vertex.label.dist=3.5, edge.curved=0.2, 
     vertex.color=c( "pink",rep("skyblue",4),"peru","skyblue") )

#네트워크 그림 -7 line color

te <- c('train','plane','train','highway','highway')
line.col <- ifelse(te=='train',1,ifelse(te=='plane',2,3))
colrs <- c("black","maroon","blue") #1,2,3

plot(g4,edge.color=colrs[line.col], vertex.size=V(g4)$Pop*4, 
     vertex.frame.color="gray", vertex.label.color="black",
     vertex.label.cex=1.2, vertex.label.dist=3.5, edge.curved=0.2, 
     vertex.color=c("pink",rep("skyblue",4),"peru","skyblue"))


# edge curve 지정 및 legend 추가, population 반영
line.curve<-c(0.1,0.9,0.3,0.4,0.1 )

mycolrs<-c( "gold",rep("tomato",4),"lightpink","tomato")
plot(g4, edge.color=colrs[line.col], vertex.size=V(g4)$Pop*6,	
     vertex.frame.color="gray", vertex.label.color="black",
     vertex.label.cex=1.2,edge.curved=line.curve,vertex.color=mycolrs )

legend('topleft', c("Special","Metropolitan","Metropolitan Autonomous"),
       pch=21, pt.bg=c("gold","tomato","lightpink"), pt.cex=2, bty="n", ncol=1)
legend(x=-1.0,y=-1.2,c('train','plane','highway'),lty=1,lwd=2,col=colrs,bty="n",ncol=3)


