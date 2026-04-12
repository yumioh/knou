install.packages("tseries")
library(tseries)

## 1. 원계열과 계절조정계열의 시계열도표를 같이 그리고, 특징을 변동요인 중심으로 기술

## 통계청에서 다운로드 받은 파일 읽기
# 원지수 : 계절적 요인, 설추석 등 모두 포함된 통계 수치
iaip_orign = read.csv("D:/knou/Prediction_Methodology/data/전산업생산지수_원지수.csv",
                  fileEncoding = "EUC-KR",check.names = FALSE)
# 계정조정지수 : 정기적인 변동요인을 추세를 명확히 보여주는 지수
iaip_season = read.csv("D:/knou/Prediction_Methodology/data/전산업생산지수_계절조정지수.csv",
                     fileEncoding = "EUC-KR",check.names = FALSE)

# 전산업생산지수 행만 추출
orign <- as.numeric(iaip_orign[,-1])
season <- as.numeric(iaip_season[,-1])

## 시계열 객체 생성
ts_orign <- ts(orign, start=c(2000,1), frequency = 12)
ts_season <- ts(season, start=c(2000,1), frequency = 12)


# 시계열 도표
plot(ts_orign, 
     col  = "blue", lwd = 1.5, 
     main = "전산업생산지수: 원계열", 
     ylab = "지수", xlab = "연도")

plot(ts_season, 
     col  = "red", lwd = 1.5, lty = 1,
     main = "전산업생산지수: 계절조정계열", 
     ylab = "지수", xlab = "연도")


## 2. 원계열과 계절조정계열에 대한 스펙트럼을 같이 그래프로 표현하고, 그 특징을 시계열의 변동요인과 연계해서 설명

spectrum(ts_orign,
         main = "원계열 스펙트럼",
         col  = "blue", lwd = 1.5,
         xlab = "Frequency (cycles/year)",
         ylab = "Spectrum")


spectrum(ts_season,
         main = "계절조정계열 스펙트럼",
         col  = "red", lwd = 1.5,
         xlab = "Frequency (cycles/year)",
         ylab = "Spectrum")

## 3.두 시계열(로그변환 계절조정계열과 로그차분 계절조정계열)에 대해 
## ADF(Augmented Dickey-Fuller) 검정을 각각 실시하고 검정결과를 표로 비교하여 정리

# 데이터 로그 변환
log_season <- log(ts_season)

# 로그 차분 : 1기간 차분하는 것으로 전월 대비 성장률 의미
diff_season <- diff(log_season)

plot(diff_season,
     main = "로그차분 계절조정계열",
     ylab = "차분", col = "red", lwd = 1.5)
par(mfrow = c(1, 1))

# adf 검정
adf_log  <- adf.test(log_season)
adf_diff <- adf.test(diff_season)

# 결과 출력 차분
print(adf_log)
print(adf_diff)

# 로그 변환 데이터
acf(log_season,
    main = "로그변환 계절조정계열 ACF",
    lag.max = 36)
pacf(log_season,
     main = "로그변환 계절조정계열 PACF",
     lag.max = 36)


# 로그 차분 데이터
acf(diff_season,
    main = "로그차분 계절조정계열 ACF",
    lag.max = 36)
pacf(diff_season,
     main = "로그차분 계절조정계열 PACF",
     lag.max = 36)
