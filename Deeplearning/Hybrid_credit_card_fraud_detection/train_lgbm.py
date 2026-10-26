import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed_ieee"
MODEL_DIR = BASE_DIR / "models"
PRED_DIR = BASE_DIR / "data" / "predictions"

# 1. 데이터 불러오기 (preprocessing.py의 tree 버전: 결측치 NaN 그대로)
with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
target = meta["target"]
features = meta["cat_cols"] + meta["num_cols"]

# 범주 수가 20개 이하인 컬럼만 LightGBM 범주형으로 지정
# card1(약 1만 종), DeviceInfo(약 1,400종)처럼 범주가 너무 많은 컬럼을 범주형으로 지정하면
# 학습 데이터의 드문 값에 과적합됨
# 기준값은 tune_lgbm_categories.py 실험으로 정함 (val 기준 seed 3개 평균, test는 보지 않음)
# 전부 지정: ROC-AUC 0.9253 / PR-AUC 0.6022
# 500 이하: 0.9297 / 0.6148
# 100 이하: 0.9331 / 0.6294  ← PR-AUC 최고
# 20 이하 : 0.9334 / 0.6284  ← ROC-AUC 최고, PR-AUC는 seed별 흔들림이 더 작음(표준편차 0.0013 vs 0.0039)
# (0~200 사이는 차이가 seed에 따른 흔들림 안에 있어 사실상 같음. 500 이상에서 확실히 나빠짐)
# 대부분의 범주형은 수십 종 이하
# 나머지는 정수 코드 그대로 숫자로 사용
MAX_CATEGORIES = 20
cat_cols = [c for c in meta["cat_cols"] if meta["cat_sizes"][c] <= MAX_CATEGORIES]

train = pd.read_parquet(DATA_DIR / "tree" / "train.parquet")
val = pd.read_parquet(DATA_DIR / "tree" / "val.parquet")
test = pd.read_parquet(DATA_DIR / "tree" / "test.parquet")

# 2. LightGBM 데이터셋
# categorical_feature: 범주형 번호를 크기가 아닌 "종류"로 다루도록 지정
train_set = lgb.Dataset(train[features], train[target], categorical_feature=cat_cols)
val_set = lgb.Dataset(val[features], val[target], categorical_feature=cat_cols, reference=train_set)

# 3. 학습
# - 평가 지표: ROC-AUC+ PR-AUC(사기처럼 드문 클래스에서 더 엄격한 지표)
# - 조기 종료: 검증 점수가 200번 연속 좋아지지 않으면 멈춤 → 과적합 방지
# - 불균형 처리는 따로 하지 않음 (AUC는 순위만 보기 때문에 오버샘플링 없이도 잘 나옴)
params = {
    "objective": "binary",
    "metric": ["auc", "average_precision"],
    "learning_rate": 0.05,
    "num_leaves": 256,
    "min_child_samples": 100,
    "feature_fraction": 0.5,  # 나무마다 변수 절반만 사용 (V 컬럼처럼 비슷한 변수가 많아 효과적)
    "bagging_fraction": 0.8,  # 나무마다 행 80%만 사용
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "seed": 42,
    "deterministic": True,  # 멀티스레드 계산 순서로 생기는 미세한 차이까지 없앰 → 다시 돌려도 같은 결과
    "force_row_wise": True,  # deterministic이 제대로 동작하려면 계산 방식을 하나로 고정해야 함
    "verbose": -1,
}
model = lgb.train(
    params,
    train_set,
    num_boost_round=5000,
    valid_sets=[val_set],
    valid_names=["val"],
    callbacks=[lgb.early_stopping(200, first_metric_only=True), lgb.log_evaluation(100)],
)
print("최적 반복 횟수:", model.best_iteration)

# 4. 평가
val_pred = model.predict(val[features], num_iteration=model.best_iteration)
test_pred = model.predict(test[features], num_iteration=model.best_iteration)

for name, y, pred in [("val", val[target], val_pred), ("test", test[target], test_pred)]:
    print(f"[{name}] ROC-AUC {roc_auc_score(y, pred):.4f} | PR-AUC {average_precision_score(y, pred):.4f}")

# 사기 판정 기준(threshold): 검증 데이터에서 F1이 가장 높은 값으로 정함
# test로 정하면 test 정보를 미리 보는 셈이라 val에서 정함
precision, recall, thresholds = precision_recall_curve(val[target], val_pred)
f1 = 2 * precision * recall / (precision + recall + 1e-9)
threshold = thresholds[np.argmax(f1[:-1])]
print(f"판정 기준: {threshold:.3f} (val F1 최대)")

test_label = (test_pred >= threshold).astype(int)
print("[test] 혼동 행렬 (행: 실제 정상/사기, 열: 예측 정상/사기)")
print(confusion_matrix(test[target], test_label))
print(classification_report(test[target], test_label, target_names=["정상", "사기"], digits=4))

# 5. 변수 중요도 (gain: 그 변수로 나눴을 때 성능이 얼마나 좋아졌는지의 합)
importance = pd.Series(
    model.feature_importance(importance_type="gain"), index=features
).sort_values(ascending=False)
print("중요 변수 상위 20개:")
print((importance / importance.sum()).head(20).round(4).to_string())

# 6. 저장
# 예측값은 TransactionID와 함께 저장 → 나중에 오토인코더 점수와 행끼리 결합
MODEL_DIR.mkdir(exist_ok=True)
PRED_DIR.mkdir(parents=True, exist_ok=True)

model.save_model(MODEL_DIR / "lgbm.txt", num_iteration=model.best_iteration)

for name, part, pred in [("val", val, val_pred), ("test", test, test_pred)]:
    pd.DataFrame(
        {"TransactionID": part["TransactionID"], target: part[target], "lgbm_score": pred}
    ).to_parquet(PRED_DIR / f"lgbm_{name}.parquet", index=False)
print("저장 완료:", MODEL_DIR / "lgbm.txt", PRED_DIR)
