#install.packages("magrittr")
#install.packages("ggplot")
#install.packages("Rcpp")
library(magrittr)
library(ggplot2)

# 1~6번까지 주사위를 무작워로 번더 nn번 추출
# table(): 각 숫자의 발생 횟수를 세어서 테이블로 반환
# / nn으로 나눠 상대 빈도를 계산 
RDice=function(nn){
  sample(1:6, nn, replace=TRUE) %>% table()/nn
}

set.seed(7763)

#난수 생성 
dice_1 = RDice(12)  #12번
dice_2 = RDice(120) #120번
dice_3 = RDice(1200) #1200번
dice_4 = RDice(120000) #120000번

# data transformation
dice = c(as.numeric(dice_1), as.numeric(dice_2), as.numeric(dice_3), 
         as.numeric(dice_4))
nn   = c(rep("(a) n=12",6),rep("(b) n=120",6), rep("(c) n=1,200",6), 
         rep("(d) n=12,000",6)) 
num = c(rep(1:6,4))
dice_result = data.frame(nn, num, dice)
dice_result


# ggplot2
ggplot(data = dice_result, aes(x = num, y = dice)) +
  geom_bar(stat = "identity", alpha = 0.8) +
  xlab("\n Result on Die") + ylab("Relative Frequency\n") +
  geom_hline(yintercept = 1/6, colour=2, lty=2) +
  ylim(0,0.3) + facet_wrap(~nn, ncol = 2)


