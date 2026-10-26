import json
from pathlib import Path

import kagglehub
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DIR = DATA_DIR / "processed_ieee"
TARGET = "isFraud"

# 출력은 두 버전으로 나눔 (분할과 범주형 코드는 동일 → 두 모델의 예측을 행끼리 결합 가능)
# - tree: LightGBM, XGBoost 등 결측치(NaN)를 스스로 처리하는 모델용 → NaN 그대로, 스케일링 없음
# - nn  : 신경망, 오토인코더 등 NaN을 처리하지 못하는 모델용 → 결측 표시 + 중앙값 채움 + 스케일링

# 1. 데이터 다운로드
# 대회 데이터라 competition_download 사용
# 폴더가 비어 있지 않으면 오류가 나므로, 이미 받았으면 다운로드 생략
path = DATA_DIR / "ieee"
if not (path / "train_transaction.csv").exists():
    kagglehub.competition_download("ieee-fraud-detection", output_dir=str(path))
print("파일 목록:", [p.name for p in path.iterdir()])

# 거래 정보(transaction)와 기기/신원 정보(identity)를 TransactionID로 병합
# identity는 일부 거래에만 있으므로 left join
transaction = pd.read_csv(path / "train_transaction.csv")
identity = pd.read_csv(path / "train_identity.csv")
df = transaction.merge(identity, on="TransactionID", how="left")
del transaction, identity
print("원본 크기:", df.shape)
print("사기 비율:", df[TARGET].mean())

# 메모리 절약: float64 → float32 (약 2GB → 1GB)
float_cols = df.select_dtypes("float64").columns
df[float_cols] = df[float_cols].astype(np.float32)
df = df.copy()  # 컬럼별 형변환으로 쪼개진 메모리 정리

# 2. 결측 컬럼은 제거하지 않음
# 결측률 90%가 넘는 컬럼(D7, dist2, id_07 등)도 값이 있을 때 사기 비율이 2~4배 높아
# "값이 있는지 없는지" 자체가 중요한 정보이기 때문
# TransactionID는 거래마다 달라 중복 행은 없음

# 3. 파생 변수
# TransactionDT: 기준 시점 이후 경과 초. 실제 날짜는 공개되지 않음
# 한시간의 초 : 86400, 하루의 초 : 86400
# 시간과 몇번째 요일인지 구분
df["Hour"] = (df["TransactionDT"] // 3600) % 24
df["Weekday"] = (df["TransactionDT"] // 86400) % 7

# TransactionAmt: 오른쪽으로 크게 치우쳐 있어 로그 변환
df["TransactionAmt"] = np.log1p(df["TransactionAmt"])

# 4. 시간 순서 기준 분할 (60/20/20)
# 실제로는 과거 거래로 학습해 미래 거래를 예측하므로 무작위로 섞지 않음
# 무작위로 나누면 미래 정보가 학습에 섞여 점수가 실제보다 좋게 나옴
df = df.sort_values("TransactionDT").reset_index(drop=True)
n = len(df)
train = df.iloc[: int(n * 0.6)].copy() # 0~ 354, 323번
val = df.iloc[int(n * 0.6) : int(n * 0.8)].copy() # 354, 324번 ~ 472번, 431번 
test = df.iloc[int(n * 0.8) :].copy()  # 472,432번 ~ 끝
del df

# 5. 범주형 처리 (두 버전 공통)
# 범주형: 문자열 컬럼 + 숫자로 되어 있지만 실제로는 코드값인 컬럼
# 카드·주소 코드
# id_12 ~ id_38: 주최사(Vesta)가 범주형으로 분류한 컬럼 (id_13, id_17 등은 숫자로 저장돼 있음)

# 숫자로 저장된 범주형은 사람이 직접 목록을 적어 추가
code_cols = ["card1", "card2", "card3", "card5", "addr1", "addr2"]
code_cols += [c for c in train.columns if c.startswith("id_") and int(c[3:]) >= 12]
# 범주형 컬럼만 추출 
cat_cols = train.select_dtypes(exclude="number").columns.tolist()
cat_cols += [c for c in code_cols if c not in cat_cols]
# 수치형 컬럼만 추출
num_cols = [
    c for c in train.columns
    if c not in cat_cols + ["TransactionID", "TransactionDT", TARGET]
]

# 학습 데이터에 나온 값에 1부터 번호를 붙이고, 결측·처음 보는 값은 0
# 학습 데이터 기준으로만 번호를 정함 → val/test 정보가 섞이지 않게 (데이터 누수 방지)
# 정수 코드라 트리 모델에도, 딥러닝 임베딩 층에도 그대로 쓸 수 있음
# 범주형 컬럼의 값을 정수 번호로 바꾸는 코드
# 번호는 train에서 처음 등장한 순서로 붙임 (train은 시간순 정렬 상태)
# → 번호가 작을수록 일찍부터 쓰이던 값, 클수록 늦게 처음 나타난(새로운) 값
# LightGBM이 범주형으로 지정하지 않은 컬럼(card1 등)은 번호를 크기로 보므로
# "번호 > 8000" 같은 분할이 "최근에 처음 나타난 카드인가"라는 의미를 가짐
#
# 다른 방식도 실험했으나 이 방식이 가장 단순하면서 val 점수가 가장 좋았음 (LightGBM, seed 42)
#   처음 등장 순서 (현재)          : ROC-AUC 0.9333 / PR-AUC 0.6294
#   많이 나온 순서                  : 0.9315 / 0.6205
#   많이 나온 순서 + 빈도 변수 49개 : 0.9334 / 0.6294 (변수만 늘고 이득 없음)
cat_sizes = {}
for col in cat_cols:
    categories = train[col].dropna().unique()  # 처음 나온 순서대로, 결측 제외
    mapping = {v: i + 1 for i, v in enumerate(categories)}
    for part in (train, val, test):
        part[col] = part[col].map(mapping).fillna(0).astype(np.int32)
    cat_sizes[col] = len(categories) + 1  # 0번(결측·미등록) 포함

splits = {"train": train, "val": val, "test": test}

def save(version, parts):
    out_dir = PROCESSED_DIR / version
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, part in parts.items():
        part.to_parquet(out_dir / f"{name}.parquet", index=False)
        print(f"[{version}] {name}: {part.shape}, 사기 비율 {part[TARGET].mean():.4%}")


# 6-1. tree 버전: 수치형 결측치를 NaN 그대로 저장
# 트리 모델은 NaN을 별도 갈래로 보내 "비어 있음" 자체를 학습함
save("tree", splits)

# 6-2. nn 버전 : null 값이 없는 데이터 
# (1) 결측 표시 컬럼:  결측 위치가 똑같은 수치형 컬럼들을 찾아 한 그룹으로 묶는 부분
#     예) D11, V1~V11은 항상 같은 행에서 함께 비어 있음 → 12개 대신 na_D11 하나
na_groups = {}
for col in num_cols:
    is_na = train[col].isna()
    if is_na.any():
        na_groups.setdefault(is_na.values.tobytes(), []).append(col)
na_groups = {f"na_{cols[0]}": cols for cols in na_groups.values()}
print(f"결측이 있는 수치형 {sum(map(len, na_groups.values()))}개 → 결측 표시 {len(na_groups)}개")

# (2) 결측치는 학습 데이터 중앙값으로 채우고 RobustScaler 적용
#  중앙값 채우기와 결측 표시는 한 세트
medians = train[num_cols].median().fillna(0)
scaler = RobustScaler().fit(train[num_cols].fillna(medians))

nn_splits = {}
for name, part in splits.items():
    # 그룹 안에서 하나라도 비어 있으면 1  =>  결측 표시 컬럼 만들기
    # 그룹에 속한 컬럼들의 결측 여부를 확인
    # 행마다 그중에 하나라도 비어 있으면 True => 가로 방향이라는 뜻
    # astype : 0 or 1로 바뀜
    na_flags = pd.DataFrame(
        {flag: part[cols].isna().any(axis=1).astype(np.int8) for flag, cols in na_groups.items()},
        index=part.index,
    )
    # 결측 채우기 -> 스케일링 -> 로그변환
    # 그냥 log를 쓰지 않는 이유는 스케일링하면 음수가 생기기 때문
    # np.log1p(...): log(1 + 크기)로 큰 값을 줄입니다
    # scaler.transform은 컬럼 이름이 없는 숫자 배열을 돌려줍니다. 
    scaled_values = scaler.transform(part[num_cols].fillna(medians))    # 중앙값으로 채움
    scaled_values = np.sign(scaled_values) * np.log1p(np.abs(scaled_values)) # 남은 극단값 줄임
    scaled = pd.DataFrame(
        scaled_values.astype(np.float32),
        columns=num_cols,
        index=part.index,
    )
    nn_splits[name] = pd.concat(
        [part[["TransactionID", "TransactionDT", TARGET] + cat_cols], scaled, na_flags], axis=1
    )
save("nn", nn_splits)

# 7. 모델 학습 때 필요한 컬럼 정보 (임베딩 층 크기 등)
# 오버샘플링(SMOTE 등)은 모델 학습 단계에서 학습 데이터에만 적용할 것
# 오토인코더는 학습 단계에서 정상 거래(isFraud == 0)만 골라 학습시킬 것
# 정상거래만 학습하는 이유는 사기 거래인 경우 처음 보는 패턴이라 복원이 잘 되지 않음
meta = {
    "target": TARGET,
    "cat_cols": cat_cols,
    "num_cols": num_cols,
    "cat_sizes": cat_sizes,
    "na_flag_cols": list(na_groups),  # nn 버전에만 있음
    "na_groups": na_groups,
}
with open(PROCESSED_DIR / "meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print(f"범주형 {len(cat_cols)}개, 수치형 {len(num_cols)}개, 결측 표시 {len(na_groups)}개")
