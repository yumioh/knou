set.seed(123456);

# 데이터 생성 : 
## arima.sim : 가상의 ARIMA 모델 데이터를 만들어주는 시뮬레이션 함수
## order=c(1,1,1): AR(1), 1차 차분(I), MA(1) 성분을 각각 1개씩 갖는 모델
## ts: 시계열객체로 변환하여 r이 시간 데이터로 인식
arimal_sim = ts(arima.sim(list(order=c(1,1,1), ar=0.6, ma=0.6), n=nn))

## 추세 그래프 그리기
plot(arimal_sim, main="", xlab="", ylab="ARIMA(1,1,1)", col="steelblue")


## 주기성 분석 spectrum : 데이터를 주파수(Frequency) 영역으로 분해해서 어떤 주기가 강하게 나타나는지 봅
## spans=c(3,3): 그래프를 부드럽게 만들기 위해 이동평균(Smoothing)을 적용하는 옵션
# peak가 존재한다면 그 데이터에 특정 주기가 숨어 있음
spectrum(arimal_sim, spans=c(3,3), main="")

# 자기상관계수 : 현재와 과거 사이의 전반적인 상관관계 
acf(arimal_sim, main= "", col="steelblue")

# 부분자기상관계쑤 : 다른 시점의 영향을 제거한 순수한 상관관계
#  어떤 차수까지 유의미한지 파악 모델의 p값을 결정할때 사용 
pacf(arimal_sim, main= "", col="steelblue")
