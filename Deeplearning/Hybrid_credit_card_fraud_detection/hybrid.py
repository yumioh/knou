from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

BASE_DIR = Path(__file__).parent
PRED_DIR = BASE_DIR / "data" / "predictions"
TARGET = "isFraud"

# 1. 두 모델의 예측 불러와서 TransactionID로 결합
# LightGBM 점수와 오토인코더 점수를 같은 거래끼리 한 표로 합치는 부분
preds = {}
for name in ["val", "test"]:
    lgbm = pd.read_parquet(PRED_DIR / f"lgbm_{name}.parquet")
    ae = pd.read_parquet(PRED_DIR / f"ae_{name}.parquet")
    preds[name] = lgbm.merge(ae.drop(columns=TARGET), on="TransactionID", how="inner")
    assert len(preds[name]) == len(lgbm) == len(ae), "두 모델의 거래 목록이 다름"
val, test = preds["val"], preds["test"]

# 모델 하나의 성적을 val과 test 모두에 대해 한 줄로 출력해주는 도우미
# 
def evaluate(label, val_score, test_score):
    print(
        f"{label:28s} val ROC-AUC {roc_auc_score(val[TARGET], val_score):.4f} " # 결과 줄에 붙일 이름
        f"PR-AUC {average_precision_score(val[TARGET], val_score):.4f} | " # 	val 거래들의 점수
        f"test ROC-AUC {roc_auc_score(test[TARGET], test_score):.4f} "  # 	test 거래들의 점수
        f"PR-AUC {average_precision_score(test[TARGET], test_score):.4f}"
    )


print("[단독 모델]")
evaluate("LightGBM", val["lgbm_score"], test["lgbm_score"])
evaluate("오토인코더", val["ae_score"], test["ae_score"])
print("두 점수의 순위 상관 (val):", round(val["lgbm_score"].corr(val["ae_score"], method="spearman"), 4))

# 2. 방법 1: 순위 가중 평균
# 두 점수는 범위가 전혀 달라서(확률 0~1 vs 복원 오차) 그대로 더할 수 없음
# → 각각 순위(0~1)로 바꾼 뒤 가중 평균. 가중치는 val에서 고르고 test로 확인
def rank(s): # 전체 중 몇 % 위치인가
    return s.rank(pct=True)

# w = 1.0 → LightGBM만 사용 / w = 0.0 → 오토인코더만 사용 / w = 0.8 → LightGBM 80%, 오토인코더 20%
weights = np.round(np.arange(0, 1.01, 0.05), 2)
val_auc = [roc_auc_score(val[TARGET], w * rank(val["lgbm_score"]) + (1 - w) * rank(val["ae_score"])) for w in weights]
# argmax는 가장 큰 값의 위치
best_w = weights[int(np.argmax(val_auc))]
print(f"\n[방법 1: 순위 가중 평균] LightGBM 가중치 {best_w} / 오토인코더 {1 - best_w:.2f} (val ROC-AUC 최대)")
evaluate(
    "순위 가중 평균",
    best_w * rank(val["lgbm_score"]) + (1 - best_w) * rank(val["ae_score"]),
    best_w * rank(test["lgbm_score"]) + (1 - best_w) * rank(test["ae_score"]),
)
# best_w가 1.0으로 나오면 → 오토인코더를 섞어도 val에서 나아지지 않았다는 뜻
# best_w가 0.7~0.9 정도면 → 오토인코더가 LightGBM이 놓친 부분을 일부 보완한다는 뜻

# 3. 방법 2: 스태킹 (두 점수를 입력으로 받는 로지스틱 회귀)
# 두 모델이 학습에 쓰지 않은 val 데이터로 결합 모델을 학습하고 test로 평가
# (train으로 학습하면 두 모델이 이미 본 데이터라 점수가 실제보다 좋게 나와 결합이 왜곡됨)
# 점수를 로그 스케일로 바꿔 넣음: LightGBM 확률 → logit, 복원 오차 → log
def stack_features(df):
    p = df["lgbm_score"].clip(1e-6, 1 - 1e-6) # LightGBM 확률 → 로짓
    lgbm_logit = np.log(p / (1 - p)) # 로짓(log-odds) 변환
    ae_log = np.log(df["ae_score"] + 1e-6) # 오른쪽으로 길게 치우친 분포예요. 로그를 씌우면 고르게 펴져서 회귀에 넣기 좋아요. +1e-6은 0일 때 로그 오류를 막는 장치
    return np.column_stack([lgbm_logit, ae_log, lgbm_logit * ae_log])

# val로 로지스틱 회귀를 학습하고 계수 3개를 출력
# max_iter=1000은 수렴할 때까지 충분히 반복하라는 설정
stacker = LogisticRegression(max_iter=1000).fit(stack_features(val), val[TARGET])
print("\n[방법 2: 스태킹] 계수 (LightGBM, 오토인코더, 상호작용):", stacker.coef_[0].round(3))
evaluate(
    "스태킹 (val로 학습 → 참고용)",
    stacker.predict_proba(stack_features(val))[:, 1],
    stacker.predict_proba(stack_features(test))[:, 1],
)

# 4. 저장: 최종 점수 (test)
out = test[["TransactionID", TARGET, "lgbm_score", "ae_score"]].copy()
out["hybrid_rank_score"] = best_w * rank(test["lgbm_score"]) + (1 - best_w) * rank(test["ae_score"])
out["hybrid_stack_score"] = stacker.predict_proba(stack_features(test))[:, 1]
out.to_parquet(PRED_DIR / "hybrid_test.parquet", index=False)
print("\n저장 완료:", PRED_DIR / "hybrid_test.parquet")
