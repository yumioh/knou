# LightGBM 범주형 지정 기준(MAX_CATEGORIES) 실험
# 범주 수가 기준값 이하인 컬럼만 범주형으로 지정하고, 기준값별로 학습해 val 점수로 비교
# test는 이 실험에서 보지 않음 → 기준값을 정한 뒤 train_lgbm.py에서 한 번만 확인
import json
import time
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed_ieee"

# 0: 범주형 지정 안 함 / None: 전부 지정
CANDIDATES = [0, 20, 50, 100, 200, 500, None]
# seed를 바꿔 여러 번 학습해 평균으로 비교
# 기준값 사이 차이가 작아서(0.001 이하), seed 하나의 결과만으로는 우연인지 구분할 수 없음
SEEDS = [42, 7, 2024]

with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
target = meta["target"]
features = meta["cat_cols"] + meta["num_cols"]

train = pd.read_parquet(DATA_DIR / "tree" / "train.parquet")
val = pd.read_parquet(DATA_DIR / "tree" / "val.parquet")

# train_lgbm.py와 같은 설정 (기준값만 바꿔서 비교하기 위해)
params = {
    "objective": "binary", # 이진분류
    "metric": "auc", # 검증시 ROC-AUC로 사용
    "learning_rate": 0.05, #트리 하나의 의견을 5%만 반영. 작을수록 천천히, 안정적으로 배우지만 트리가 더 많이 필요함
    "num_leaves": 256, # 트리 하나의 잎(최종 칸) 최대 256개. 클수록 복잡한 패턴을 잡지만 과적합 위험
    "min_child_samples": 100, # 잎 하나에 거래가 최소 100건은 있어야 함. 몇 건짜리 우연한 규칙을 못 만들게 막음
    "feature_fraction": 0.5, # 트리마다 컬럼을 무작위로 50%만 골라서 사용
    "bagging_fraction": 0.8, # 트리마다 거래를 무작위로 80%만 골라서 사용
    "bagging_freq": 1, # 거래 샘플링을 매 트리마다 새로 함
    "lambda_l2": 1.0, # 잎 값이 너무 커지지 않게 벌점(L2 규제)
    "seed": 42, # 무작위 샘플링의 시작값 고정 (아래 반복문에서 SEEDS 값으로 바꿔 가며 사용)
    "deterministic": True, # 멀티스레드 계산 순서 때문에 생기는 미세한 차이까지 없앰 → 같은 seed면 항상 같은 결과
    "force_row_wise": True, # deterministic이 제대로 동작하려면 계산 방식을 하나로 고정해야 함
    "verbose": -1, # 경고 숨기기
}

results = []
for max_cat in CANDIDATES: # 비교할 기준값 목록
    if max_cat is None:
        cat_cols = meta["cat_cols"]
    else:
        cat_cols = [c for c in meta["cat_cols"] if meta["cat_sizes"][c] <= max_cat]
    label = "전부" if max_cat is None else str(max_cat)

    # 히스토그램 구간 => 범주형으로 처리
    train_set = lgb.Dataset(train[features], train[target], categorical_feature=cat_cols)
    val_set = lgb.Dataset(val[features], val[target], categorical_feature=cat_cols, reference=train_set)
    for seed in SEEDS:
        start = time.time()
        model = lgb.train(
            {**params, "seed": seed}, train_set, num_boost_round=5000, valid_sets=[val_set],
            callbacks=[lgb.early_stopping(200, verbose=False)], ## VAL점수가 200번 연속 안좋아지면 멈춤
        )
        # 결과기록
        # best_iteration: val 점수가 가장 좋았던 시점의 트리 개수예요. 
        # 조기 종료로 멈춘 시점(최고점 + 200개)이 아니라 최고점까지만 써서 예측
        val_pred = model.predict(val[features], num_iteration=model.best_iteration)
        results.append({
            "기준값": label,
            "seed": seed,
            "범주형 수": len(cat_cols),
            "반복 횟수": model.best_iteration,
            "val ROC-AUC": roc_auc_score(val[target], val_pred),
            "val PR-AUC": average_precision_score(val[target], val_pred),
            "시간(초)": round(time.time() - start),
        })
        print(f"기준값 {label:>4s} / seed {seed:>4d} 완료: "
              f"val ROC-AUC {results[-1]['val ROC-AUC']:.4f} | PR-AUC {results[-1]['val PR-AUC']:.4f}")

results = pd.DataFrame(results)
# 기준값별 평균과 표준편차 (표준편차 = seed에 따라 흔들리는 정도)
summary = results.groupby("기준값", sort=False).agg(
    범주형_수=("범주형 수", "first"),
    ROC_평균=("val ROC-AUC", "mean"),
    ROC_표준편차=("val ROC-AUC", "std"),
    PR_평균=("val PR-AUC", "mean"),
    PR_표준편차=("val PR-AUC", "std"),
)
print("\n[seed별 결과]\n", results.round(4).to_string(index=False))
print(f"\n[기준값별 평균 (seed {len(SEEDS)}개)]\n", summary.round(4).to_string())
for col in ["ROC_평균", "PR_평균"]:
    best = summary[col].idxmax()
    print(f"{col} 최고: 기준값 {best} ({summary.loc[best, col]:.4f})")
