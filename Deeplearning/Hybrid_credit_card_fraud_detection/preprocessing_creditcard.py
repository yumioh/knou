from pathlib import Path

import kagglehub
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RANDOM_STATE = 42

# 1. 데이터 다운로드 (mlg-ulb/creditcardfraud, 이미 받았으면 다시 받지 않음)
path = kagglehub.dataset_download("mlg-ulb/creditcardfraud", output_dir=str(DATA_DIR))
df = pd.read_csv(Path(path) / "creditcard.csv")
print("원본 크기:", df.shape)

# 2. 중복 행 제거
# 결측치는 없음, 모든 컬럼의 값이 전부 같은 행을 중복으로 봄
# 다만 time을 기준으로 넣음. time을 빼면 9144개가 중복으로 잡히지만,
# 이건 시각만 다르고 금액과 패턴이 같은 서로 다른 거래일 수 있음
# 실제 반복 결제나 사기범의 연속 시도일 수도 있으니 지우면 안됨
# 지워진 1081개 중 19개는 사기 거래임 => 같은 값으로 기록된 거래라 기록이 중복으로 봄
df = df.drop_duplicates().reset_index(drop=True)
print("중복 제거 후 크기:", df.shape)
print("클래스 분포:\n", df["Class"].value_counts())

# 3. 파생 변수
# Time: 첫 거래 이후 경과 초(이틀치) → 하루 중 시간대(0~23)
df["Hour"] = (df["Time"] // 3600) % 24
# Amount: 오른쪽으로 크게 치우쳐 있어 로그 변환
df["Amount"] = np.log1p(df["Amount"])
df = df.drop(columns=["Time"])

# 정답을 뺀 입력 변수
X = df.drop(columns=["Class"])
# 정답 => 모델이 맞춰야하는 값
y = df["Class"]

# 4. 학습/검증/테스트 분할 (60/20/20), 사기 비율 유지를 위해 stratify
# 층화추출: 지정한 컬럼의 비율이 나눈 묶음마다 똑같이 유지되는 옵션
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, stratify=y, random_state=RANDOM_STATE
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=RANDOM_STATE
)

# 5. 스케일링: 이상치에 강한 RobustScaler, 학습 데이터로만 fit (데이터 누수 방지)
# V1~V28은 이미 PCA로 변환된 값이라 Amount, Hour만 스케일링
scale_cols = ["Amount", "Hour"]
scaler = RobustScaler()
X_train[scale_cols] = scaler.fit_transform(X_train[scale_cols])
X_val[scale_cols] = scaler.transform(X_val[scale_cols])
X_test[scale_cols] = scaler.transform(X_test[scale_cols])

# 6. 저장
# 오버샘플링(SMOTE 등)은 모델 학습 단계에서 학습 데이터에만 적용할 것
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
for name, X_part, y_part in [
    ("train", X_train, y_train),
    ("val", X_val, y_val),
    ("test", X_test, y_test),
]:
    part = X_part.assign(Class=y_part)
    part.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    print(f"{name}: {part.shape}, 사기 비율 {y_part.mean():.4%}")
