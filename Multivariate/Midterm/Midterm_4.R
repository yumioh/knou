# 300명의 대학생에게 6과목에 대해 선호도를 조사한 결과 이다 
# 인자분석을 실행하고 물어 답하라 

# 데이터 불려오기
subjects <-read.csv("D:/knou/Multivariate/data/favoritesujects.csv")
head(subjects)
summary(subjects)

# 라이브러리 설치
install.packages('GPArotation')
library(psych)
library(GPArotation)

# 4-1) 유의한 인자 수와 그 인자들이 확보하는 정보의 양은 얼마인가?
sub_factor = principal(subjects, rotate='none')

# 유의한 인자수 고윳값이 1 이상인 인자수
sum(sub_factor$values >= 1)

# 각 주성분의 고윳값(정보량)
sub_factor$values

# 설명력 (정보 비율)
explained_var <- sub_factor$values / sum(sub_factor$values)
explained_var

# 누적 설명력
cumulative_var <- cumsum(explained_var)
cumulative_var

# 4-2) 인자부하행렬을 구하고 varimax와 promax 방법을 이용하여 인자회전을 실시 하고 결과를 비교하시오

# 주성분 분석 (Varimax 회전)
sub_varimax <- principal(subjects, nfactors = 2, rotate = "varimax", score = TRUE, method = "regression")
sub_varimax

#promax
sub_varimax
principal(subjects, nfactor=2, rotate='promax', score=T, method="regression")


# 4-3) 인자들에 적절한 이름?

# 4-4) 인자분석 결과를 종합적으로 정리하시오