library(magrittr)
library(forecast)
library(ggplot2)

# 2. 코드 재실행
wn %>% ggtsdisplay(main="", theme=theme_bw())

library(magrittr)

set.seed(123456)
nn = 52*4
# Time Series(시계열) 데이터를 만들기 위한 가장 기본적인 함수
# frequency : 1년(한 주기) 당 데이터의 개수
# start : 데이터 시작 시점
# rnorm : 정규분포 난수
wn = ts(rnorm(nn), start=1970, frequency = 4)

# 백색잡음 만들기
plot(wn, main="", xlab="", ylab="백색잡음", col="steelblue")
abline(h=0, lty=2, col='gray')

# 자기상관함수 : 오늘의 데이터가 어제의 데이터와 얼마나 닮았는지 
# 점선(신뢰구간) : 파란 점선 안에 막대가 있다면 통계적으로 의미 있는 상관관계가 없음
# 천천히 감소하는 막대 : 추세가 있는 신호
# 물결치는 막대 : 계정설이나 주기적인 패턴이 있음
# 첫번째 막대만 길고 나머지는 뚝 떨어짐 : 백색잡음에 가깝거나 이전 데이터의 영향이 거의 없음
# acf를 계산하는 이유 ? 시계열 분석 모델을 돌리기 전에 데이터가 안정적인지 확인을 위함
acf(wn, maim="", col='steelblue', xlab="")

# 오늘의 영향력을 수학적으로 제거하고, 오늘과 그저께 사이의 직접적인 상관관계 측정
# 시계열 모델을 만들 때 자기회귀 부분의 차수를 결정하는 결정적인 힌트가 되기 때문
pacf(wn, main="", col ="steelblue", xlab="")

# 융박스 검증 : 단순한 무작위 노이즈인가 아니면 분석할 가치가 있는 패턴이 남아 있는가를 
# 통계적으로 검정하는 함수
# 귀무가설 : 데이터가 서로 독립적이다 = 백색잡음
# 대립가설 : 데이터 간에 유의미한 상관관계가 있다 => 분석할 패턴이 있음
# lag : 시차의 개수 10 ~ 20
# pvalue가 0.05 이하 귀무가설 기각
# pvalue가 0.05 이상 귀무가설 채택
# x-squared 값이 작으면 자기 상관이 없다 
Box.test(wn, lag=8, type="Ljung")


wn %>% ggtsdisplay(main="", theme=theme_bw())
