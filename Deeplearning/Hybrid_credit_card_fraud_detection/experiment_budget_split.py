# 보완 실험: 검토량 분할 (experiment_unseen.py의 저장된 점수를 사용, 재학습 없음)
#
# 문제: 가중 평균 하이브리드는 LightGBM이 미관측 유형 거래 전체를 낮게 평가하면,
#       오토인코더 점수를 섞어도 전체 상위 k% 검토 대상에 올라오지 못함 (C·W 검출 0건)
# 방법: 점수를 섞지 않고, 검토량 B를 두 모델에 나눠 줌
#   - LightGBM 상위 (B - A) + 오토인코더 상위 A  (겹치면 오토인코더 다음 순위로 채워 총량을 B로 맞춤)
#   - 유형별 AE: 오토인코더 몫 A를 "상품 유형 안에서의 등수"로 고름
#     → 오토인코더가 특정 유형 전체를 이상하게 보는 문제(S 유형 등)를 줄이기 위해
#       (상품 유형은 운영 시 알 수 있는 정보이므로 사용 가능, 모델 입력에는 넣지 않음)
# 설정 선택: val에는 미관측 유형의 사기가 없어 오토인코더 몫이 0으로 선택되므로 val로 고르지 않음
#   주 설정은 결과를 보기 전에 정한 "검토량 10% 중 오토인코더 1%"이고,
#   다른 검토량·몫의 결과는 민감도 분석으로 모두 보고함
# 평가: 상품 유형 변수를 뺀 LightGBM (experiment_unseen.py의 주 결과와 같은 조건)
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

BASE_DIR = Path(__file__).parent
PRED_DIR = BASE_DIR / "data" / "predictions" / "unseen"
RESULT_DIR = BASE_DIR / "results"

TYPES = ["W", "C", "R", "H", "S"]
SEEDS = [42, 7, 2024]
AE_FILE = "ae_ep100_{seed}.npz"
LGBM_FILE = "lgbm_noPCD_hide{t}_{seed}.npz"
BUDGETS = [0.05, 0.10, 0.20]           # 전체 test 중 검토하는 비율
AE_SHARES = [0.05, 0.10, 0.20]         # 검토량 중 오토인코더 몫의 비율
PRIMARY = (0.10, 0.10)                 # 주 설정: 검토량 10%, 그중 10%(= 전체의 1%)를 오토인코더에
N_BOOT = 1000

test = pd.read_parquet(PRED_DIR / "test_scores.parquet")[["isFraud", "ProductCD"]]
y = test["isFraud"].values
product = test["ProductCD"].values
N = len(y)


def to_rank(score):
    return rankdata(score) / len(score)


def rank_within_type(score):
    """상품 유형 안에서의 등수 비율 (0~1)"""
    out = np.empty(len(score))
    for t in np.unique(product):
        idx = np.where(product == t)[0]
        out[idx] = rankdata(score[idx]) / len(idx)
    return out


def top_k(score, k):
    flag = np.zeros(N, dtype=bool)
    flag[np.argsort(-score, kind="stable")[:k]] = True
    return flag


def split_flags(r_lgbm, r_ae, budget, ae_share):
    """LightGBM 상위 (B-A)를 먼저 고르고, 남은 A를 오토인코더 순위로 채움 (겹침 제외)"""
    total = int(N * budget)
    flag = top_k(r_lgbm, total - int(total * ae_share))
    order = np.argsort(-r_ae, kind="stable")
    remaining = total - flag.sum()
    candidates = order[~flag[order]][:remaining]
    flag[candidates] = True
    return flag


# 1. 방식별 검토 대상 계산 (유형 x seed x 검토량 x 몫)
rows, flags_store = [], {}
for seed in SEEDS:
    ae = np.load(PRED_DIR / AE_FILE.format(seed=seed))["test"]
    r_ae, r_ae_type = to_rank(ae), rank_within_type(ae)
    for t in TYPES:
        r_lgbm = to_rank(np.load(PRED_DIR / LGBM_FILE.format(t=t, seed=seed))["test"])
        hidden = (product == t) & (y == 1)
        seen = (product != t) & (y == 1)
        for budget in BUDGETS:
            methods = {
                ("LightGBM", 0.0): top_k(r_lgbm, int(N * budget)),
                ("가중평균 AE 20%", 0.0): top_k(0.8 * r_lgbm + 0.2 * r_ae, int(N * budget)),
            }
            for share in AE_SHARES:
                methods[("분할 AE", share)] = split_flags(r_lgbm, r_ae, budget, share)
                methods[("분할 유형별 AE", share)] = split_flags(r_lgbm, r_ae_type, budget, share)
            for (name, share), flag in methods.items():
                flags_store[(seed, t, budget, name, share)] = flag
                rows.append({
                    "seed": seed, "미관측 유형": t, "검토량": budget, "방식": name, "AE 몫": share,
                    "미관측 재현율": flag[hidden].mean(), "관측 재현율": flag[seen].mean(),
                    "정밀도": y[flag].mean(), "검토 건수": int(flag.sum()),
                })
results = pd.DataFrame(rows)
RESULT_DIR.mkdir(exist_ok=True)
results.to_csv(RESULT_DIR / "budget_split_results.csv", index=False, encoding="utf-8-sig")

# 2. 부트스트랩: 주 설정에서 "방식 - LightGBM"의 미관측 재현율 차이 95% 신뢰구간
# seed 3개의 검토 여부를 평균(0, 1/3, 2/3, 1)한 뒤, 미관측 유형의 사기 거래를 복원 추출
rng = np.random.default_rng(0)
budget, share = PRIMARY
boot_rows = []
for t in TYPES:
    hidden_idx = np.where((product == t) & (y == 1))[0]
    seen_idx = np.where((product != t) & (y == 1))[0]

    def seed_avg(name, s):
        return np.mean([flags_store[(seed, t, budget, name, s)] for seed in SEEDS], axis=0)

    base = seed_avg("LightGBM", 0.0)
    for name, s in [("가중평균 AE 20%", 0.0), ("분할 AE", share), ("분할 유형별 AE", share)]:
        method = seed_avg(name, s)
        for group, idx in [("미관측", hidden_idx), ("관측", seen_idx)]:
            diff = method[idx] - base[idx]
            point = diff.mean()
            boots = [diff[rng.integers(0, len(idx), len(idx))].mean() for _ in range(N_BOOT)]
            low, high = np.percentile(boots, [2.5, 97.5])
            boot_rows.append({
                "미관측 유형": t, "방식": name, "평가 집단": group,
                "재현율 차이(방식-LightGBM)": point, "95% CI 하한": low, "95% CI 상한": high,
                "유의(0 미포함)": bool(low > 0 or high < 0),
            })
boot = pd.DataFrame(boot_rows)
boot.to_csv(RESULT_DIR / "budget_split_bootstrap.csv", index=False, encoding="utf-8-sig")

# 3. 요약 출력
pd.set_option("display.width", 220)
primary = results[(results["검토량"] == budget) & (results["AE 몫"].isin([0.0, share]))]
print(f"[주 설정: 검토량 {budget:.0%}, 오토인코더 몫 {share:.0%} (전체의 {budget * share:.0%}), 유형 5개 x seed 3개 평균]")
print(primary.groupby("방식", sort=False)[["미관측 재현율", "관측 재현율", "정밀도"]].mean().round(3).to_string())
print("\n[미관측 유형별 재현율]")
print(primary.pivot_table(index="방식", columns="미관측 유형", values="미관측 재현율", aggfunc="mean", sort=False)[TYPES].round(3).to_string())
print("\n[민감도: 검토량 x 오토인코더 몫별 평균 (분할 유형별 AE)]")
sens = results[results["방식"].isin(["LightGBM", "분할 유형별 AE"])]
print(sens.groupby(["검토량", "방식", "AE 몫"], sort=False)[["미관측 재현율", "관측 재현율", "정밀도"]].mean().round(3).to_string())
print("\n[부트스트랩: 주 설정의 재현율 차이]")
print(boot.round(3).to_string(index=False))
