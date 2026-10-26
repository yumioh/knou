# 미관측 패턴 사기 실험 (Leave-one-type-out)
# 질문: 학습 때 한 번도 보지 못한 유형의 사기를, 오토인코더 기반 하이브리드가 LightGBM보다 더 잘 잡는가?
#
# 설계
# - 미관측 유형: 상품 종류(ProductCD) W, C, R, H, S를 하나씩 미관측 유형으로 정함
# - LightGBM: train/val에서 미관측 유형의 "사기 거래"를 제거하고 학습 (정상 거래는 그대로)
#            → 그 유형의 사기를 한 번도 보지 못한 상태
# - 오토인코더: 정상 거래로만 학습, 에폭은 val 정상 거래의 복원 오차로 선택 (사기 라벨을 전혀 쓰지 않음)
#            → 어떤 유형의 사기 정보도 들어가지 않으므로 유형마다 다시 학습할 필요 없음
# - 하이브리드: 두 점수를 순위(0~1)로 바꿔 결합
#     tuned  : 가중치를 미관측 유형 사기를 뺀 val로 선택 (원래 설계. val에 관측 유형만 있어 LightGBM 쪽으로 치우침)
#     w=0.9 등: 고정 가중치 (오토인코더 비중 10~50%) → 관측/미관측 유형 사이의 교환 관계 확인
#     max    : 두 순위 중 큰 값 (둘 중 하나라도 이상하다고 본 거래를 높게 봄, 정할 값이 없음)
# - 참고 상한선: 모든 사기로 학습한 LightGBM (미관측 유형을 "관측했다면" 얼마나 잡았을지)
# - 평가: test에서 미관측 유형 거래만(unseen) / 나머지 유형 거래만(seen) 따로
#     ROC-AUC, PR-AUC, 상위 1·5·10% 재현율(전체 test 중 점수 상위 k%를 검토할 때 그 집단의 사기를 몇 % 잡는가)
# - 반복: 유형 5개 x seed 3개, test 차이는 부트스트랩 95% 신뢰구간으로 확인
#
# 모델 설정은 train_lgbm.py, train_autoencoder.py와 같음 (오토인코더 에폭 선택 방식만 다름)
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
from scipy.stats import rankdata
from sklearn.metrics import average_precision_score, roc_auc_score
from torch import nn

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed_ieee"
RAW_DIR = BASE_DIR / "data" / "ieee"
RESULT_DIR = BASE_DIR / "results"
PRED_DIR = BASE_DIR / "data" / "predictions" / "unseen"

TYPES = ["W", "C", "R", "H", "S"]
SEEDS = [42, 7, 2024]
MAX_CATEGORIES = 20      # train_lgbm.py와 같음
FIXED_AE_WEIGHTS = [0.1, 0.2, 0.3, 0.5]  # 하이브리드에서 오토인코더 비중
TOP_RATES = [0.01, 0.05, 0.10]  # 검토량: 전체 test 중 점수 상위 1%, 5%, 10%
AE_MAX_EPOCHS = 100     # 라벨 없는 기준(정상 복원 오차)은 오래 좋아지므로 넉넉히 (30에서는 모두 끝까지 감)
N_BOOT = 1000            # 부트스트랩 반복 수
SPLITS = ["train", "val", "test"]

RESULT_DIR.mkdir(exist_ok=True)
PRED_DIR.mkdir(parents=True, exist_ok=True)
start_all = time.time()


def log(msg):
    print(f"[{(time.time() - start_all) / 60:5.1f}분] {msg}", flush=True)


# 1. 데이터 불러오기
with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
target = meta["target"]
features = meta["cat_cols"] + meta["num_cols"]
lgb_cat_cols = [c for c in meta["cat_cols"] if meta["cat_sizes"][c] <= MAX_CATEGORIES]
ae_cat_cols = meta["cat_cols"]
recon_cols = meta["num_cols"] + meta["na_flag_cols"]

tree = {s: pd.read_parquet(DATA_DIR / "tree" / f"{s}.parquet") for s in SPLITS}
nn_data = {s: pd.read_parquet(DATA_DIR / "nn" / f"{s}.parquet") for s in SPLITS}
y = {s: tree[s][target].values for s in SPLITS}
for s in SPLITS:
    assert (tree[s]["TransactionID"].values == nn_data[s]["TransactionID"].values).all(), "tree/nn 행 순서가 다름"

# 전처리에서 ProductCD가 번호로 바뀌었으므로 원본에서 상품 종류 글자를 가져옴
raw_product = pd.read_csv(RAW_DIR / "train_transaction.csv", usecols=["TransactionID", "ProductCD"])
raw_product = raw_product.set_index("TransactionID")["ProductCD"]
product = {s: tree[s]["TransactionID"].map(raw_product).values for s in SPLITS}
log("데이터 준비 완료")
for t in TYPES:
    counts = {s: int(((product[s] == t) & (y[s] == 1)).sum()) for s in SPLITS}
    log(f"  유형 {t} 사기 건수: {counts}")


# 2. LightGBM (train_lgbm.py와 같은 설정)
LGB_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "learning_rate": 0.05,
    "num_leaves": 256,
    "min_child_samples": 100,
    "feature_fraction": 0.5,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "deterministic": True,
    "force_row_wise": True,
    "verbose": -1,
}


def train_lgbm(seed, hidden_type=None, drop_cols=()):
    """hidden_type의 사기 거래를 train/val에서 빼고 학습. None이면 모든 사기로 학습(참고 상한선).
    drop_cols: 입력에서 뺄 컬럼 (지름길 점검용)"""
    feats = [c for c in features if c not in drop_cols]
    cats = [c for c in lgb_cat_cols if c not in drop_cols]
    keep = {}
    for s in ["train", "val"]:
        keep[s] = np.ones(len(y[s]), dtype=bool)
        if hidden_type is not None:
            keep[s] = ~((product[s] == hidden_type) & (y[s] == 1))
    train_set = lgb.Dataset(tree["train"].loc[keep["train"], feats], y["train"][keep["train"]],
                            categorical_feature=cats)
    val_set = lgb.Dataset(tree["val"].loc[keep["val"], feats], y["val"][keep["val"]],
                          categorical_feature=cats, reference=train_set)
    model = lgb.train({**LGB_PARAMS, "seed": seed}, train_set, num_boost_round=5000, valid_sets=[val_set],
                      callbacks=[lgb.early_stopping(200, verbose=False)])
    return {s: model.predict(tree[s][feats], num_iteration=model.best_iteration) for s in ["val", "test"]}


# 3. 오토인코더 (train_autoencoder.py와 같은 구조, 에폭 선택만 라벨 없이)
class AutoEncoder(nn.Module):
    def __init__(self, cat_sizes, n_recon, bottleneck=16):
        super().__init__()
        self.embeddings = nn.ModuleList(
            [nn.Embedding(size, min(16, (size + 1) // 2)) for size in cat_sizes]
        )
        emb_dim = sum(e.embedding_dim for e in self.embeddings)
        self.encoder = nn.Sequential(
            nn.Linear(emb_dim + n_recon, 256), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(256, 64), nn.ReLU(),
            nn.Linear(64, bottleneck),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck, 64), nn.ReLU(),
            nn.Linear(64, 256), nn.ReLU(),
            nn.Linear(256, n_recon),
        )

    def forward(self, x_cat, x_num):
        emb = [e(x_cat[:, i]) for i, e in enumerate(self.embeddings)]
        return self.decoder(self.encoder(torch.cat(emb + [x_num], dim=1)))


def to_tensors(df):
    return (torch.tensor(df[ae_cat_cols].values, dtype=torch.long),
            torch.tensor(df[recon_cols].values, dtype=torch.float32))


ae_tensors = {s: to_tensors(nn_data[s]) for s in SPLITS}


@torch.no_grad()
def anomaly_score(model, split):
    model.eval()
    x_cat, x_num = ae_tensors[split]
    scores = []
    for i in range(0, len(x_num), 8192):
        recon = model(x_cat[i:i + 8192], x_num[i:i + 8192])
        scores.append(((recon - x_num[i:i + 8192]) ** 2).mean(dim=1))
    return torch.cat(scores).numpy()


def train_autoencoder(seed, max_epochs=AE_MAX_EPOCHS, patience=3, batch_size=1024):
    torch.manual_seed(seed)
    normal = y["train"] == 0
    x_cat, x_num = (t[torch.from_numpy(normal)] for t in ae_tensors["train"])
    model = AutoEncoder([meta["cat_sizes"][c] for c in ae_cat_cols], len(recon_cols))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    val_normal = y["val"] == 0

    best_loss, best_state, best_epoch, bad = np.inf, None, 0, 0
    for epoch in range(1, max_epochs + 1):
        model.train()
        perm = torch.randperm(len(x_num))
        for i in range(0, len(perm), batch_size):
            idx = perm[i:i + batch_size]
            loss = ((model(x_cat[idx], x_num[idx]) - x_num[idx]) ** 2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        # 라벨 없는 선택: val 정상 거래의 평균 복원 오차 (사기 거래는 보지 않음)
        val_loss = anomaly_score(model, "val")[val_normal].mean()
        if val_loss < best_loss:
            best_loss, best_epoch, bad = val_loss, epoch, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    return {s: anomaly_score(model, s) for s in ["val", "test"]}, best_epoch


# 4. 학습
# 점수를 파일로 저장해 두고, 이미 있으면 다시 학습하지 않고 불러옴
# (평가 방법만 바꿔 다시 실행할 때 학습을 건너뛰기 위해. 모델 설정을 바꿨다면 해당 파일을 지울 것)
def cached(name, train_fn):
    path = PRED_DIR / f"{name}.npz"
    if path.exists():
        data = np.load(path)
        log(f"{name}: 저장된 점수 사용")
        return {"val": data["val"], "test": data["test"]}
    result = train_fn()
    np.savez(path, **result)
    log(f"{name}: 학습 완료")
    return result


preds = {}  # (모델 이름, 미관측 유형 또는 None, seed) → {"val": 점수, "test": 점수}
ae_epochs = {}
for seed in SEEDS:
    def train_ae(seed=seed):
        scores, epoch = train_autoencoder(seed)
        ae_epochs[seed] = epoch
        log(f"오토인코더 seed {seed}: 에폭 {epoch}에서 선택")
        return scores
    preds[("ae", None, seed)] = cached(f"ae_ep{AE_MAX_EPOCHS}_{seed}", train_ae)
    preds[("lgbm_oracle", None, seed)] = cached(f"lgbm_oracle_{seed}", lambda seed=seed: train_lgbm(seed))
    for t in TYPES:
        preds[("lgbm", t, seed)] = cached(f"lgbm_hide{t}_{seed}", lambda seed=seed, t=t: train_lgbm(seed, hidden_type=t))
        # 지름길 점검: ProductCD를 입력에서 뺀 LightGBM
        # 미관측 유형 T는 train에 정상 거래만 있어 "ProductCD = T이면 정상"이라는 지름길을 배울 수 있음
        preds[("lgbm_noPCD", t, seed)] = cached(
            f"lgbm_noPCD_hide{t}_{seed}", lambda seed=seed, t=t: train_lgbm(seed, hidden_type=t, drop_cols=("ProductCD",)))

# 다시 학습하지 않고 분석할 수 있도록 test 점수 저장
pd.DataFrame(
    {f"{m}_{t or 'all'}_{seed}": p["test"] for (m, t, seed), p in preds.items()}
    | {"TransactionID": tree["test"]["TransactionID"].values, target: y["test"], "ProductCD": product["test"]}
).to_parquet(PRED_DIR / "test_scores.parquet", index=False)


# 5. 결합과 평가
def to_rank(score):
    return rankdata(score) / len(score)


def recall_at_top(full_score, mask, rate):
    """전체 test에서 점수 상위 rate를 검토할 때, mask 집단의 사기 중 몇 %를 잡는가"""
    threshold = np.quantile(full_score, 1 - rate)
    fraud = mask & (y["test"] == 1)
    return (full_score[fraud] >= threshold).mean()


def evaluate(full_score, mask):
    ys, ss = y["test"][mask], full_score[mask]
    return {
        "ROC-AUC": roc_auc_score(ys, ss),
        "PR-AUC": average_precision_score(ys, ss),
        **{f"상위{int(r * 100)}%재현율": recall_at_top(full_score, mask, r) for r in TOP_RATES},
    }


# LightGBM 입력 구성: 기본(모든 변수) / ProductCD 제외(지름길 점검)
VARIANTS = {"": "lgbm", " (ProductCD 제외)": "lgbm_noPCD"}
# 논문 표의 주 하이브리드 설정 (전체 가중치 결과는 unseen_results.csv에 모두 있음)
PRIMARY_AE_WEIGHT = 0.2


def hybrid_scores(lgbm_pred, ae_pred, hidden_type, suffix=""):
    """결합 방식별 test 점수 (순위 기반). suffix는 LightGBM 입력 구성 이름"""
    r_lgbm, r_ae = to_rank(lgbm_pred["test"]), to_rank(ae_pred["test"])
    out = {f"LightGBM{suffix}": r_lgbm}
    # tuned: 미관측 유형 사기를 뺀 val에서 ROC-AUC가 가장 높은 가중치 (hybrid.py와 같은 방식)
    val_keep = ~((product["val"] == hidden_type) & (y["val"] == 1))
    r_lgbm_val, r_ae_val = to_rank(lgbm_pred["val"]), to_rank(ae_pred["val"])
    grid = np.round(np.arange(0, 1.01, 0.05), 2)
    val_auc = [roc_auc_score(y["val"][val_keep], ((1 - w) * r_lgbm_val + w * r_ae_val)[val_keep]) for w in grid]
    w_tuned = grid[int(np.argmax(val_auc))]
    out[f"하이브리드 tuned{suffix}"] = (1 - w_tuned) * r_lgbm + w_tuned * r_ae
    for w in FIXED_AE_WEIGHTS:
        out[f"하이브리드 AE {int(w * 100)}%{suffix}"] = (1 - w) * r_lgbm + w * r_ae
    out[f"하이브리드 max{suffix}"] = np.maximum(r_lgbm, r_ae)
    return out, w_tuned


def all_scores(t, seed):
    """미관측 유형 t, seed 하나에 대한 모든 모델의 test 순위 점수"""
    scores = {"오토인코더": to_rank(preds[("ae", None, seed)]["test"]),
              "상한선(모든 사기 학습)": to_rank(preds[("lgbm_oracle", None, seed)]["test"])}
    weights = {}
    for suffix, key in VARIANTS.items():
        s, w = hybrid_scores(preds[(key, t, seed)], preds[("ae", None, seed)], t, suffix)
        scores.update(s)
        weights[suffix] = w
    return scores, weights


rows, tuned_weights = [], []
avg_scores = {}  # 유형별 seed 평균 점수 (부트스트랩과 논문 표에 사용)
for t in TYPES:
    masks = {"미관측 유형": product["test"] == t, "관측 유형": product["test"] != t}
    avg_scores[t] = {}
    for seed in SEEDS:
        scores, weights = all_scores(t, seed)
        tuned_weights.append({"미관측 유형": t, "seed": seed, "tuned AE 가중치": weights[""],
                              "tuned AE 가중치 (ProductCD 제외)": weights[" (ProductCD 제외)"]})
        for model_name, score in scores.items():
            avg_scores[t][model_name] = avg_scores[t].get(model_name, 0) + score / len(SEEDS)
            for subset, mask in masks.items():
                rows.append({"미관측 유형": t, "seed": seed, "모델": model_name, "평가 집단": subset,
                             **evaluate(score, mask)})
results = pd.DataFrame(rows)
results.to_csv(RESULT_DIR / "unseen_results.csv", index=False, encoding="utf-8-sig")
log("평가 완료")

# 6. 부트스트랩: seed 3개 점수를 평균한 뒤, 미관측 유형 test 거래를 복원 추출해 두 모델의 차이 계산
# 비교 쌍: 하이브리드 - 같은 입력 구성의 LightGBM / 지름길 점검: LightGBM(ProductCD 제외) - LightGBM
comparisons = []
for suffix in VARIANTS:
    base = f"LightGBM{suffix}"
    comparisons += [(name, base) for name in avg_scores[TYPES[0]]
                    if name.startswith("하이브리드") and name.endswith(suffix) and (suffix or "(" not in name)]
comparisons.append(("LightGBM (ProductCD 제외)", "LightGBM"))

rng = np.random.default_rng(0)
boot_rows = []
for t in TYPES:
    avg = avg_scores[t]
    idx_all = np.where(product["test"] == t)[0]
    # 상위 k% 기준선은 전체 test 점수로 한 번만 정함 (복원 추출과 무관)
    thresholds = {(k, r): np.quantile(v, 1 - r) for k, v in avg.items() for r in TOP_RATES}

    def metric_value(model_name, idx, metric):
        if metric == "PR-AUC":
            return average_precision_score(y["test"][idx], avg[model_name][idx])
        # 복원 추출로 같은 거래가 여러 번 뽑히면 그만큼 여러 번 셈
        fraud_idx = idx[y["test"][idx] == 1]
        return (avg[model_name][fraud_idx] >= thresholds[(model_name, metric)]).mean()

    boot_idx = [rng.choice(idx_all, len(idx_all), replace=True) for _ in range(N_BOOT)]
    for model_name, base in comparisons:
        for metric in ["PR-AUC"] + TOP_RATES:
            def stat(idx):
                return metric_value(model_name, idx, metric) - metric_value(base, idx, metric)
            point = stat(idx_all)
            low, high = np.percentile([stat(idx) for idx in boot_idx], [2.5, 97.5])
            metric_name = metric if metric == "PR-AUC" else f"상위{int(metric * 100)}%재현율"
            boot_rows.append({"미관측 유형": t, "비교 모델": model_name, "기준 모델": base, "지표": metric_name,
                              "차이(비교-기준)": point, "95% CI 하한": low, "95% CI 상한": high,
                              "유의(0 미포함)": bool(low > 0 or high < 0)})
boot = pd.DataFrame(boot_rows)
boot.to_csv(RESULT_DIR / "unseen_bootstrap.csv", index=False, encoding="utf-8-sig")
log("부트스트랩 완료")

# 7. 논문용 표: 유형별 건수, PR-AUC와 무작위 기준선 대비 배수, 차이의 95% 신뢰구간
# PR-AUC는 seed 3개 점수를 평균한 점수로 계산 (신뢰구간과 같은 기준)
# 무작위 기준선 = 그 집단의 사기율 (아무렇게나 순위를 매기면 PR-AUC가 사기율과 같아짐)
primary = f"하이브리드 AE {int(PRIMARY_AE_WEIGHT * 100)}%"
paper_rows = []
for t in TYPES:
    mask = product["test"] == t
    base_rate = y["test"][mask].mean()

    def pr(name):
        return average_precision_score(y["test"][mask], avg_scores[t][name][mask])

    def ci(model_name, base):
        r = boot[(boot["미관측 유형"] == t) & (boot["비교 모델"] == model_name)
                 & (boot["기준 모델"] == base) & (boot["지표"] == "PR-AUC")].iloc[0]
        return f"{r['차이(비교-기준)']:+.3f} [{r['95% CI 하한']:+.3f}, {r['95% CI 상한']:+.3f}]"

    row = {"미관측 유형": t, "test 거래 수": int(mask.sum()), "test 사기 수": int(y["test"][mask].sum()),
           "사기율(무작위 기준선)": round(base_rate, 4)}
    for name in ["상한선(모든 사기 학습)", "오토인코더"]:
        row[f"{name} PR-AUC (배수)"] = f"{pr(name):.3f} ({pr(name) / base_rate:.1f}x)"
    for suffix in VARIANTS:
        lg, hy = f"LightGBM{suffix}", f"{primary}{suffix}"
        row[f"{lg} PR-AUC (배수)"] = f"{pr(lg):.3f} ({pr(lg) / base_rate:.1f}x)"
        row[f"{hy} PR-AUC (배수)"] = f"{pr(hy):.3f} ({pr(hy) / base_rate:.1f}x)"
        row[f"차이{suffix} [95% CI]"] = ci(hy, lg)
    row["지름길 점검: ProductCD 제외 - 포함 [95% CI]"] = ci("LightGBM (ProductCD 제외)", "LightGBM")
    paper_rows.append(row)
paper = pd.DataFrame(paper_rows).set_index("미관측 유형")
paper.to_csv(RESULT_DIR / "unseen_paper_table.csv", encoding="utf-8-sig")

# 8. 요약 출력
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
metric_cols = ["ROC-AUC", "PR-AUC"] + [f"상위{int(r * 100)}%재현율" for r in TOP_RATES]
summary = results.groupby(["평가 집단", "모델"], sort=False)[metric_cols].mean()
print("\n[유형 5개 x seed 3개 평균]\n", summary.round(4).to_string())
by_type = results[results["평가 집단"] == "미관측 유형"].pivot_table(
    index="모델", columns="미관측 유형", values="PR-AUC", aggfunc="mean", sort=False)[TYPES]
print("\n[미관측 유형별 PR-AUC (seed 평균)]\n", by_type.round(4).to_string())
print("\n[val로 고른 오토인코더 가중치]\n", pd.DataFrame(tuned_weights).to_string(index=False))
print(f"\n[논문용 표 (주 설정: {primary})]\n", paper.T.to_string())
print("\n[부트스트랩: 유의한 차이만]\n",
      boot[boot["유의(0 미포함)"]].round(4).to_string(index=False))
if ae_epochs:
    print("\n[오토인코더 선택 에폭]", ae_epochs)
log("전체 완료")
