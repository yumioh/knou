library(vcd) # 관절염 데이터
#호흡곡선

#age 변수의 quantile의 값에 따라 4등분
#x축 연속형 변수
#y가 범주형 변수
with(Arthritis, spine(Improved ~ Age, breaks=quantile(Age)))

#자료가 적은 경우 5세 구간으로 사용하고 많은경우 10세 구간으로 자동적으로 설정
spine(Improved ~ Age, data=Arthritis, breaks='Scott')

#조건부 밀도 함수
#Conditional Density Plot
cdplot(Improved ~ Age, data=Arthritis)

#rug 함수를 이용하여 연속형 변수의 값이 특정 구간에 얼마나 많은 분포하는지 표현
#with 같이 사용 
#age의 실제 데이터값을 하단에 하얀색으로 표시하라
cdplot(Improved ~ Age, data=Arthritis)
with(Arthritis, rug(jitter(Age),col="white",quiet = TRUE))