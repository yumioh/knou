#작업 directory 설정 및 현재 directory
#setwd('경로')
setwd('D:\\knou\\R_Computing')
#현재 작업하는 디렉토리 확인
getwd()

#c() 함수는 가장 기본적인 데이터 입력 방법
#좌측에 벡터이름 위치 <- 나 = 연산자는 데이터 할당 의미 

#1,2,3,4,5 다섯개의 관측값을 갖는 벡터 x 생성
x <- c(1,2,3,4,5)

#10,20,30,40,50 다섯개의 관측값을 갖는 벡터 x 생성
y <- c(10,20,30,40,50)
y

#길이가 동일한 벡터를 묶는 것 cbind
dat <- cbind(x,y)
dat

#scan 함수는 바로 데이터를 입력 할 수 있음 
w1 <- scan()

#데이터프레임을 생성하기 위해 빈 객체를 데이터 프레임으로 지정해 준뒤 
#창을 열어 데이이터 입력 :edit
data5 <- data.frame()
data5 = edit(data5)
data5

#출력된 모든 결과를 파일로 저장 : 
#sink('파일명') 
#저장할 내용
#sink()
sink('print.txt')
summary(iris) #iris 데이터셋의 기술통계량을 저장
sink()

#외부 파일로 저장할 수 있음 : write.csv(넣을 데이터, 파일경로)
#다른 경로가 지정되어 있지 않다면 이 파일은 기 설정된 작업에 저장
#csv는 엑셀, 노트패드 등 다양한 프로그램에서 쉽게 저장 및 편집을 할 수 있는 데이터 포멧으로 
#비교적 적은 용량으로 데이터 저장 가능
write.csv(dat, 'dat_exam1.csv')

# 객체를 외부로 저장하는 점은 동일하지만 옵션 상 차이 
# 기본적으로 공백으로 구분, sep 옵션을 통해 변경 가능
write.table(dat, 'dat_exam2.txt')
write.table(dat, 'dat_exam2.txt', sep=',')
write.table(data5, 'dat_exam3.txt')

# csv 형식의 데이터 파일을 불려 올때 read.csv()
#변수명이 없었던 첫번째 column은 X라는 변수명이 자동 할당
data2 <- read.csv('dat_exam1.csv')
data2

us_dat <- read.csv('USArrests.csv', header = T)
head(us_dat)

#자료 구조를 확인하기 위해 str()함수 사용
#state라는 변수는 자동으로 factor라는 변수로 변환 되었는데 
#stringsAsFoctors =F라는 옵션을 추가하여 문자로 인식
#R에서 문자열을 기본적으로 팩터로 처리하는데, 
#이는 데이터 분석 작업에서 예상치 못한 결과를 초래할 수 있기 때문에 때로는 문제가 될 수 있습니다
#stringsAsFactors는 TRUE로 설정되어 있어, 문자열 벡터를 데이터 프레임의 열로 추가할 때 
#이 문자열들이 자동으로 팩터로 변환됩니다. 팩터는 범주형 데이터를 효과적으로 다루기 위한 데이터 유형
# stringsAsFactors = FALSE를 사용하면 문자열을 팩터로 변환하지 않으므로, 문자열이 그대로 문자열 벡터로 처리
str(us_dat)

#텍스트 파일은 read.csv()함수 외에서도 read.table()함수로 불려올 수 있음
#header 옵션에 따라 첫째줄 관측지를 변수명으로 인식하느냐 여부 결정
read.table('dat_exam2.txt', header=T)

#na.string 옵션을 이요한 결측치 지정
#결측치가 NA로 표시되지만, na.strings와 같은 옵션을 지정해주면 특정한 문자로 인식
#na.strings에 지정된 값과 일치하는 문자열을 NA(결측값)로 처리
nadat1 <- read.table('dat_exam3.txt', na.strings = 'aa', header = T)
nadat1

#현재까지 작업 중 만들어진 object를 모두 확인
ls()

#모든 object를 삭제 rm()
rm(list=ls())

#연습문제 
sink('printa.txt')
summary(iris)
sink()

