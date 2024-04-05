#scan함수로 txt파일 읽기
score <- scan("D:\\knou\\Data_Info_Processor\\Midterm_Project\\score.txt")
score

#(1) 평균, 중앙값, 표본분산, 표본표준편차, 사분위수범위, 변동계수를 구하시오 
#결측지여부 확인
sum(is.na(score))
#평균 : 47.44615
mean(score)
#중앙값 : 48
median(score)
#표본분산 : 404.3135
var(score)
#표본표준편차 : 20.10755
sd(score)
#사분위수범위 : 3사분위(57) - 1사분위(33) : 24
iqr <- quantile(score, 0.75) - quantile(score, 0.25)
iqr
#변동계수 : 표준편차 / 평균 : 0.4237972
cofficient <- sd(score)/mean(score)
cofficient

#(2)줄기-잎 그림, 히스토그램, 상자그림 그리고 설명하시오
#줄기-잎 그림
stem(score)
#히스토그램
hist(score, main = "score", xlab="점수", ylab = "빈도")
#상자그림
bp <- boxplot(score, main ="socre", ylab="점수")
print(bp$stats)
#다섯가지 통계량 : 최소, 1사분위수, 중앙값, 3사분위수, 최대값
fivenum(score)
