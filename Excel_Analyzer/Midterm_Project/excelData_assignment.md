엑셀데이터분석 실습과제물 (2024학년도)

# 1. 첨부된 강수량 자료는 A 지역과 B 지역의 1990년부터 2023년까지의 연강수량 자료이다. 이 자료를 엑셀과 KESS로 분석하여 다음 물음에 답하시오. 

## (1) 두 지역의 연도별 강수량 자료에 대해 꺾은선형 차트를 이용하여 전체적인 경향을 설명하시오.
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/561ff936-bfc2-45bb-a59d-cb6b44f0d7fb"/>
<p/>
 
> A,B지역의 공통점으로 두 지역 모두 연간 강수량의 그래프가 비슷한 선형의 모양이 가졌습니다. A,B 두지역은 모두 1990년도부터 2016년도까지 연간 강수량 차이가 보이지만 그 이후엔 점차 일정한 형태로 가고 있습니다. 2003년도 집중 호우와 태풍 매미로 인해 A, B지역의 둘 다 연간 강수량이 높게 나타났으며, 2017년 이후부터 비슷한 연간 강수량을 보입니다. 차이점으로 A지역은 2002년도에 연간 강수량이 크게 상승하였는데 그 해에 태풍 루사가 발생하여 영향을 미친 지역으로 보입니다. 그러나 2004년도부터는 점차 연간 강수량이 감소하여 일정한 강수량을 보입니다. 또한, 1995년도, 1997년도, 2011년도, 2016년도를 제외한 나머지 년도에선 A지역이 B지역보다 높은 강수량을 보입니다. B지역은 1990년도에 가장 높은 연간 강수량을 보인 이후 조금씩 감소하더니, 1995년~2003년도에 몇 번의 상승이 있었으나 2004년 이후에 강수량 변동폭이 작아지면서 2017년도 이후에 일정한 강수량을 볼 수 있습니다. 

## (2) 각 지역의 강수량에 대한 기술통계량을 구해 두 지역의 연강수량을 비교하시오. 
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/e1002ec1-022d-4b49-8a5f-dca17fe6578a"/>
<p/>
 
> A지역의 연간 강수량의 평균과 중앙값은 B지역에 비해 값이 높습니다. 이를 통해 1990년도 ~ 2023년도 기간 동안 A지역의 연간 강수량이 B지역에 비해 상대적으로 높다라는 것을 알 수 있습니다. 그러나 B지역의 표준편차, 변동계수, 사분위수 범위가 A지역에 비해 낮은데 이는 상대적으로 B지역의 강수량이 일정하다는 것을 알 수 있었습니다. A지역은 B지역보다 연간 강수량의 평균값이 높아 홍수, 태풍과 같이 예측하지 못한 자연재해가 발생 할 가능성이 높고, B지역은 A지역이 비해 변동이 적고, 비슷한 강수량을 보이는 지역인 것을 알 수 있었습니다. 

## (3) 각 지역의 연 강수량에 대한 줄기-잎 그림과 상자그림을 그려서 비교하시오.
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/b9767d32-68b8-400d-a97b-94341e693231"/>
<p/>
 
> 줄기-잎 그림을 기준으로 A지역의 중앙값은 1300mm이며, 1200 ~ 1300mm에 해당하는 강수량이 최빈값입니다. 2000mm 이상 강수량이 온 날은 2번이며, A지역에서 중간값에서 벗어난 값들이 B지역이 비해 많이 보입니다. B지역은 중앙값이 1200mm이며, 1100~1200mm에 해당하는 강수량이 최빈값입니다. 극단이상점으로 2000mm가 가장 높은 강수량임을 보이며, A지역에 비해 중앙값에 벗어난 값들이 적은 편입니다.
다음으로 상자 그림을 기준으로 A,B지역을 비교하면 B지역이 중앙값이 A지역 비해 높은 것을 보아 A지역이 B지역보다 높은 년간 강수량을 보이며, 또한, B지역은 보통이상점이 A지역이 비해 많은 것을 보입니다. B지역은 오른쪽 꼬리 긴 모양의 그래프로 변동폭이 크고, B지역은 정규분포와 비슷한 그래프로 일정한 강수량을 보인다는 것을 알 수 있습니다.


## (4) 두 지역의 연간 강수량에 대한 분석할 때 어느 지역의 강수량이 많다고 할 수 있는가?
> 연간 강수량의 평균을 비교해보면 A지역이 B지역보다 165.6546mm가 더 내렸다. 그래서 A지역이 B지역에 비해 연간 강수량이 더 높다는 것을 알 수 있습니다.


<p> 
 
# 2. 다음 물음에 답하시오.
 
<p/> 

## (1) 자유투 성공률이 80%인 어느 농구선수가 자유투를 시도하려고 한다. 20번의 자유투에서 성공한 횟수를 확률변수 로 정의할 때 확률변수 가 따르는 분포는 무엇인가? 18번 이상 성공하게 될 확률과 14번 이하 성공하게 될 확률은 각각 얼마인가?
<p/> 
 
> 이항분포는 연속된 n번째 독립적 시행에서 각 시행이 확률p을 가진 이산확률분포라고 한다. 그러므로 확률변수 X는 이항분포를 따른다. <p/> 
X = “20번의 자유투 중 성공할 확률”로 정의 <p/> 
n = 20(시행횟수)
p = 0.8(성공확률) <p/> 
18번 이상 성공할 확률 : P(X≥18) = 1-P(X<18) = 1-BINOM.DIST(17,20,0.8,1) <p/> 
14번 이하 성공할 확률 : P(X≤14) = BINOM.DIST(14,20,0.8,1) <p/> 
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/9242c065-016c-4c05-b9d8-493f6dc70b63"/>
<p/>

## (2) 10문항의 4지선다형 문제가 있다. 어느 학생이 10문항 전체에 대해서 임의로 답안을 적을 때 정답수를 확률변수 X라고 하자. 정답 수가 3개 이하일 확률과 정답 수가 5개 이상일 확률은 각각 얼마인가?
> X= “10문항 전체에 대해서 임의로 답안을 적을 때 정답 수” <p/>
n = 10
p = 0.25 <p/>
5개 이상 정답 확률 : P(X≥5) = 1-P(X<5) =1-BINOM.DIST(5,10,0.25,1) <p/>
3개 이하 정답 확률 : P(X≤3) = BINOM.DIST(3,10,0.25,1) <p/>
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/2e22b639-a9c3-430f-95cc-02851ca9c56a"/>
<p/>
 
# 3. 어느 은행의 콜센터로 한 시간에 평균 4.5통의 상담전화가 걸려온다고 한다. 한 시간 동안에 걸려오는 상담전화의 수는 포아송 분포를 따른다고 가정할 수 있다. 다음 물음에 답하시오.
> X = “한시간에 걸려오는 상단전화의 수” <p/> 
> 평균 = 4.5
## (1) 한 시간에 7통 이상의 상담전화가 걸려올 확률은? 
 > P(X≥7) = 1-P(X<7) = 1-POISSON.DIST(6,4.5,1) <p/> 
## (2) 한 시간에 2통 이하의 상담전화가 걸려올 확률은?
 > P(X≤2) = POISSON.DIST(2,4.5,1) <p/> 
## (3) 한 시간에 3통 이상 7통 이하의 상담전화가 걸려올 확률은?
 > P(3≤X≤7) = P(X≤7) - P(X<3) = POISSON.DIST(7,4.5,1)-POISSON.DIST(2,4.5,1)
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/e1552b64-3b52-4ff8-b274-2eadabe171c1"/>
<p/>

# 4. 어느 회사의 전체 직원을 대상으로 하는 직무관련 시험에서 시험점수는 평균 82, 표준편차 9인 정규분포를 따른다는 것을 알았다. 다음 물음에 답하시오.
※ 문제 4는 엑셀데이터 멀티미디어 7강 내용을 참고하여 해결해 보기 바랍니다. 문제 4의 (2), (3)은 NORM.INV 함수를 이용하는 문제입니다. 

## (1) 시험점수가 65점 이하이면 재교육을 받도록 하려고 한다. 재교육을 받는 직원의 비율은 얼마인가?
> X(시험 점수) : 65, μ(평균): 82, σ(표준편차) : 9 <p/> 
> Z(표준정규분포) = X -μ / σ = 1.89
> P(X≤65) = P(X≤(65-82)/9) = P(Z≥1.89) = 1 – P(Z<1.89) <p/> 
표준정규분포표에 의해 1.89에 해당하는 값은 0.9706으로 1-0.9706을 하면 <p/> 
> 0.0294로 재교육 받는 직원의 비율은 2.94%가 나옴

## (2) 만약 전체 직원의 90%만 합격을 시키고자 한다면 합격 점수는 얼마로 해야 하는가? 
> 29.53점 이상 받아야 합격한다. 100-NORM.INV(0.1,82,9) <p/> 
  
## (3) 상위 5%의 직원에게는 포상금을 주려고 한다. 포상금을 받기 위해서는 최소한 몇 점을 얻어야 하는가?
> 최소 96.80점 이상을 받아야한다. NORM.INV(0.95,82,9) <p/> 
<p>
<img src="https://github.com/yumioh/data_analysis/assets/38059057/40277cc7-5a0b-4b09-bccb-a58a6beaaeb1"/>
<p/>
