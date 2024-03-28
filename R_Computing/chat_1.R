#R에 기본적으로 설치되어 있는 패키지 외의 사용자가 직접 설치한 패키지의 경우 
#활성화 필요 

install.packages("rpart")
library(rpart)

#패키지 내에 저장되어 있는 데이터를 불려오는 것도 가능
help(package="rpart")
library(help="rpart")

#작업공간 : R콘솔창에서 작업한 모든 객체들, 즉 변수, 함수 데이터 파일 등 표시
#작업공간 탭 : 오른쪽 작업이력탭을 통해 수행했던 명령문들이 나타남
#그래프 (plots)탭, 윈도우 탑색기 (files)탭

#작업 경로 설정 가능
#setwd("D:\\knou\\R_Computing")



