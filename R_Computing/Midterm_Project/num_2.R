#1) 데이터셋이 Temp 속성이 화씨 온도로 되어 있으며, 
#섭씨 온도로 변환하여 TempC로 저장하라. 섭씨 온도 = (화씨 온도-32)*5/9

#데이터셋 구조 확인: 6개의 열과 행 153개로 구성
#열: Ozone Solar.R Wind Temp Month Day
str(airquality)

#섭씨 온도로 변환 후 TempC열에 저장
airquality["TempC"] <- (airquality["Temp"]-32)*5/9

#10개의 행만 출력하여 값 확인
head(airquality,10)

#TempC열에해당하는 10개의 행만 출력하여 값 확인
head(airquality["TempC"], 10)

#2)각 변수에 결측치가 몇개씩 존재하는지 확인

#데이터 프레임에 결측값의 총 개수: 44
sum(is.na(airquality))

#방법1 : 각 변수별 결측치 개수
#Ozone의 결측개수 :37
sum(is.na(airquality$Ozone))
#Solar.R의 결측개수 : 7
sum(is.na(airquality$Solar.R))
#Wind의 결측개수 : 0
sum(is.na(airquality$Wind))
#Temp의 결측개수 :0
sum(is.na(airquality$Temp))
#Month의 결측개수 :0
sum(is.na(airquality$Month))
#Day의 결측개수 : 0
sum(is.na(airquality$Day))

#방법2 : colSums함수를 이용한 결측값 개수 합계
colSums(is.na(airquality))


#3) Ozone이 40 이상인 날들에 대해서만 평균 Solar.R 평균
#Ozone이 40 이상인 행만 추출
fliteringAir <- airquality[airquality["Ozone"] >= 40, ]
#10개의 행만 추출
head(fliteringAir,10)
#데이터 프레임 구조 확인
str(fliteringAir)
#결측값 개수 확인
colSums(is.na(fliteringAir))
#열의 값 출력
fliteringAir$Solar.R

#추출된 데이터에서 결측지를 제외한 Solar.R의 평균을 구함 : 218.2045
mean(fliteringAir$Solar.R, na.rm = TRUE)


