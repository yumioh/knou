#ggplot2
# - geom 계열 함수 여러개를 병렬적으로 추가
# - geom 계열이 몸체를, coord 계열이 좌표측을 이루는 구조
# - ggplot()함수와 geom 계열함수는 반드시 포함되어야 하는 필수적 요소

library(tidyverse)
library(ggplot2)

view(mtcars)

#rownames_to_column 함수를 사용하여 mtcars 데이터셋의 행 이름(자동차 모델 이름)을 열로 변환
mtcars1 <- as_tibble(rownames_to_column(mtcars))
ggplot(mtcars1, aes(hp, mpg, color=cyl))

# ggplot()함수 : 일반적으로 함수 내에 시각화 대상이 되는 데이터, 축의 설정, 그래프의 색깔, 투명도, 선 패턴 등 큰 틀을 매핑하는 aes() 함수가 위치 
# aes(데이터맵핑) x축 : hp, y축 : mpg factor함수는 범주형으로 변환
# geom_point() : 산점도 그리기 hp,mpg에 따라 점의 위치를 정하고 factor 함수에 따라 색상이 달라짐
#6-1,2,3
ggplot(mtcars1, aes(hp,mpg,color=factor(cyl)))+
  geom_point()


#geom 계열 함수 : 기존 그래프에다가 데이터에 적합된 비선형 함수를 추가
#group=123은 모든 데이터 포인트를 하나의 그룹으로 간주하고 그 그룹에 대해 단일 추세선을 생성하라는 의미
# 주변에 표준 오차(standard error)를 나타내는 신뢰 구간(shaded confidence interval)을 그리지 않도록 설정
#6-5
ggplot(mtcars1, aes(hp,mpg,color=factor(cyl))) +
  geom_point() +
  geom_smooth(aes(group=123), se=FALSE)

#geom_text(), gemo_label() : 특정 관측치 값을 그래프 상에 명시적으로 출력할 필요가 있을때 사용
#show.leged=False 옵션을 지정해야 범례에 문자가 출력되는 오류 방지 
#너무 많은 레이블이 출력되어 식별에 어렵다면 데이터 프레임을 편집하여 선별적으로 몇개만 출력
#6-6
ggplot(mtcars1, aes(hp,mpg,color=factor(cyl))) +
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder")

#6-7
ggplot(mtcars1, aes(hp,mpg,color=factor(cyl))) +
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder")+
  geom_text(aes(label=rowname), show.legend = FALSE)

#geom_label : 함수는 데이터 포인트에 레이블을 추가
#(aes(label=row.names(mtcars)) : 각 데이터 포인트에 대한 행 이름을 레이블로 사용
#nudge_x와 nudge_y 옵션은 레이블의 위치를 조정하여 점에서 얼마나 떨어질지를 지정
#6-8
ggplot(mtcars1, aes(hp,mpg,color=factor(cyl))) +
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder")+
  geom_label(aes(label=rowname), nudge_x=2.5, nudge_y=1.5, label.size=0.25, show.legend=FALSE)


#geom_text와 geom_label차이: geom_text와 geom_label 기능은 거의 유사한대 박스안에 글자를 구분해서 넣고 싶을때 geom_label사용

#6-9
#row_number() : 각 그룹 내에서 데이터의 순서를 1부터 시작하는 숫자로 반환
#desc(mpg) :  mpg (마일 당 갤런수, 즉 연비) 값을 내림차순으로 정렬
# %>% 왼쪽 계산된 결과를 오른쪽
hmpg <- mtcars1 %>% group_by(cyl) %>% filter(row_number(desc(mpg))==1)
hmpg

ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) + 
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  geom_label(aes(label=rowname), data=hmpg, nudge_x=2.5, nudge_y=1.5, label.size=0.25, show.legend=FALSE)


#6-10 :x,y,범례 안보임
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) + 
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  scale_x_continuous(labels=NULL) + # x축의 레이블을 숨김
  scale_y_continuous(labels=NULL) + #y축의 레이블을 숨김
  scale_color_discrete(labels=NULL) #범례의 색상 레이블 숨김

#6-10 : 범례 보임
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) + 
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  scale_x_continuous(labels=NULL) + # x축의 레이블을 숨김
  scale_y_continuous(labels=NULL) #y축의 레이블을 숨김

#6-11
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) + 
  geom_point() +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  scale_y_continuous(breaks = seq(10, 40, by=10)) 
  # breaks :  눈금 위치 지정
  # y축 구간을 10 ~ 40까지 10씩 증가하도록 구간 나눔

#6-12 
#시각화에서 축 범위와 색상 범례를 조절하는 데 사용
x_axis <- scale_x_continuous(limits = range(mtcars1$hp)) #x축의 범위를 설정 : 최소값~ 최대값 범위 
y_axis <- scale_y_continuous(limits = range(mtcars1$mpg)) #Y축의 범위를 설정 : 최소값 ~ 최대값 범위
col_legend <- scale_color_discrete(limits = unique(factor(mtcars1$cyl))) #중복된 항을 하나만 남기고 제거
#value값 확인
unique_cyl_values <- unique(factor(mtcars1$cyl))

ggplot(mtcars1, aes(x=hp, y=mpg, color=factor(cyl))) +
  geom_point() +  # 점으로 데이터 표시
  scale_x_continuous(limits = range(mtcars1$hp)) +  # x축 범위 설정 52 ~ 335
  scale_y_continuous(limits = range(mtcars1$mpg)) +  # y축 범위 설정 10.4 ~ 33.9
  scale_color_discrete(limits = unique(factor(mtcars1$cyl))) + # 색상 범례 설정
  labs(title="Relationship Between Horsepower and Fuel Efficiency",
       x="Horse Power", 
       y="Miles per Gallon", 
       color="Cylinder Number") 

#6-13
#그래프의 시각적 표현 영역을 조정
#데이터 자체를 자르거나 변형하지 않고, 보여지는 그래프의 좌표계 내에서 x축과 y축의 표시 범위만을 제한
#group=123은 모든 데이터 포인트를 하나의 그룹으로 간주하고 그 그룹에 대해 단일 추세선을 생성하라는 의미
ggplot(mtcars1, aes(hp,mpg, color=factor(cyl))) +
  geom_point()+
  geom_smooth(aes(group=123), se=FALSE) +
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  coord_cartesian(xlim=c(100,250), ylim=c(10,30)) #데이터를 필터링하지 않고 범위를 제한 :zooming

#6-14
#theme()함수를 이용하여 범례 위치 조정
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) +
  geom_point()+
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  theme(legend.position = "left") #범례 위치 조정

#guide_legend() : 다양한 매개변수를 통해 범례의 레이아웃과 스타일을 세부적으로 조정
#nrow=3 : 범례 내에서 항목을 나열할 행의 수를 지정
#범례에 표시되는 항목의 미적 속성을 오버라이드 size=5는 범례의 심볼(점, 선 등)의 크기를 5
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) +
  geom_point()+
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  theme(legend.position = "bottom")+
  guides(color=guide_legend(nrow=3, override.aes = list(size=5)))
 #nrow 범래 행수 조절

#6-15
#theme(legend.position = "bottom") + theme_classic(): 여기서 첫 번째 theme() 함수는 범례를 그래프 하단에 위치시킵니다. 
#theme_classic()는 클래식한 스타일의 테마를 적용하여 그리드 라인을 제거하고 배경을 깔끔하게 정리
#x축과 y축에 대한 축 라인이 검은색으로 표시
#축에 눈금선이 그려지며
#범례 디자인을 유지하고 싶으면 theme_classic() 뒤에 추가
#주로 그래프의 배경, 텍스트 스타일, 축 레이블의 스타일 등을 조정하는 데 사용
#guides 범례 영역
ggplot(mtcars1, aes(hp, mpg, color=factor(cyl))) +
  geom_point()+
  labs(title="Relationshp between Fule efficency and Horse Power", 
       x="Horse Power",
       y="Mile per Gallon",
       caption="Data Source : R", 
       color="Cylinder") +
  guides(color=guide_legend(nrow=1, override.aes = list(size=5)))+
  theme(legend.position = "bottom")+
  theme_classic()
  

#디자인 주제를 구현하는 함수
#theme_classic()
#theme_bw()
#theme_light()
#theme_linedraw()
#theme_dark()
#theme_gray()

