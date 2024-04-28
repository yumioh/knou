#install.packages("magrittr")
#install.packages("ggplot")
#install.packages("Rcpp")
library(magrittr)
library(ggplot2)

# nn으로 주사위를 던지는 횟수를 받아 
# 1~6까지의 숫자 중 하나를 nn번 무작위 선택
# sample(....) => 1~6 사이의 숫자를 nn번 무작원 추출
# factor(...) => 선택된 숫자를 팩터로 변환. 모든 레벨(1~6)이 포함
# 각 숫자의 상대 빈도를 계산할 때 1에서 6까지의 모든 숫자에 대한 테이블이 만들어지고, 
# 실제 데이터에서 빠진 숫자는 빈도가 0으로 처리
# table(): 각 숫자가 선택된 횟수를 세고, 이를 nn으로 나누어 상대 빈도를 계산

RDice = function(nn)  { 
  return (table(factor(sample(1:6, nn, replace=TRUE), levels = 1:6)) / nn) }

#난수 생성기 시드 설정 : 학번 뒤번호
set.seed(7763)

#난수 생성 
dice_1 = RDice(16) #16번
dice_2 = RDice(160) #160번
dice_3 = RDice(1600) #1600번
dice_4 = RDice(160000) #160000번
dice_1

# data transformation
dice = c(as.numeric(dice_1), as.numeric(dice_2), 
         as.numeric(dice_3), as.numeric(dice_4))
nn   = c(rep("(a) n=16",6),rep("(b) n=160",6), 
         rep("(c) n=1,600",6),rep("(d) n=16,000",6)) 
num = c(rep(1:6,4))
dice_result = data.frame(nn, num, dice)
dice_result
# ggplot2
#geom_bar : 상대 빈도를 기반으로 바 차트
#geom_hline : 이상적인 상대 빈도인 1/6을 붉은 점선으로 표시
#facet_wrap(~nn, ncol = 2) :2열의 패널로 구분하여 표시
ggplot(data = dice_result, aes(x = num, y = dice)) +
  geom_bar(stat = "identity", alpha = 0.8) +
  xlab("\n Result on Die") + ylab("Relative Frequency\n") +
  geom_hline(yintercept = 1/6, colour=2, lty=2) +
  ylim(0,0.3) + facet_wrap(~nn, ncol = 2)


#결과 해석
#이 결과는 표본 크기가 증가함에 따라 막대 그래프가 어떻게 변화하는지 보여줍니다 
# 막대는 각 주사위 면이 나올 상대 빈도를 나타내며, 
# 수평선은 이론적으로 각 면이 나올 확률인 1/6을 의미합니다. 
# 현재 그래프를 보면 주사위를 16회 던졌을 때 2, 3, 5번 면이 각각 2회, 3번 면이 4회, 1번 면이 5회 나왔습니다. 이는 이론적 확률과 다릅니다. 
# 하지만 시행 횟수가 증가함에 따라 각 면이 나올 확률이 이론적 확률 1/6에 점점 더 가까워지는 것을 관찰할 수 있습니다. 
# 주사위를 던질 때 어떤 숫자가 일시적으로 빈번하게 나올 수 있지만, 시행 횟수를 높이면 결과가 균등 분포에 가까워집니다. 이는 대수의 법칙에 따라, 더 많은 시행에서 실험 결과가 기대치에 접근하기 때문