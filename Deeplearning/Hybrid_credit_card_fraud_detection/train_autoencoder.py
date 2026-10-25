import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from torch import nn

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed_ieee"
MODEL_DIR = BASE_DIR / "models"
PRED_DIR = BASE_DIR / "data" / "predictions"

BATCH_SIZE = 1024
MAX_EPOCHS = 30
PATIENCE = 3  # 검증 점수가 3 에폭 연속 좋아지지 않으면 멈춤
torch.manual_seed(42)

# 1. 데이터 불러오기 (preprocessing.py의 nn 버전: 결측 채움 + 결측 표시 + 스케일링)
with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
target = meta["target"]
cat_cols = meta["cat_cols"]
# 복원 대상: 수치형 + 결측 표시 컬럼
recon_cols = meta["num_cols"] + meta["na_flag_cols"]

splits = {s: pd.read_parquet(DATA_DIR / "nn" / f"{s}.parquet") for s in ["train", "val", "test"]}


def to_tensors(df):
    return (
        torch.tensor(df[cat_cols].values, dtype=torch.long),
        torch.tensor(df[recon_cols].values, dtype=torch.float32),
    )


# 오토인코더는 정상 거래(isFraud == 0)로만 학습
# → 정상 패턴만 복원하도록 익혀서, 사기 거래는 복원 오차가 커지게 함
train_normal = splits["train"][splits["train"][target] == 0]
x_cat_train, x_num_train = to_tensors(train_normal)
print(f"학습: 정상 거래 {len(train_normal):,}건 (사기 {int(splits['train'][target].sum()):,}건 제외)")


# 2. 모델
# 입력: 범주형(임베딩) + 수치형/결측 표시 → 16차원으로 압축 → 수치형/결측 표시 복원
# 범주형은 입력으로만 사용: "이 카드·기기라면 보통 이런 수치가 나온다"는 관계를 학습해
# 범주와 수치의 조합이 평소와 다르면 복원 오차가 커짐
class AutoEncoder(nn.Module):
    def __init__(self, cat_sizes, n_recon, bottleneck=16):
        super().__init__()
        # 임베딩 크기: 범주 수의 절반, 최대 16
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
        z = self.encoder(torch.cat(emb + [x_num], dim=1))
        return self.decoder(z)


model = AutoEncoder([meta["cat_sizes"][c] for c in cat_cols], len(recon_cols))
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)


# 이상 점수 = 거래별 복원 오차(평균 제곱 오차). 클수록 정상 패턴에서 벗어난 거래
@torch.no_grad()
def anomaly_score(df):
    model.eval()
    x_cat, x_num = to_tensors(df)
    scores = []
    for i in range(0, len(df), 8192):
        recon = model(x_cat[i : i + 8192], x_num[i : i + 8192])
        scores.append(((recon - x_num[i : i + 8192]) ** 2).mean(dim=1))
    return torch.cat(scores).numpy()


# 3. 학습
# 모델 선택은 검증 데이터(사기 포함)의 ROC-AUC로 함
# → 복원을 잘하는 모델이 아니라 "사기와 정상을 잘 구분하는" 모델을 고르기 위해
best_auc, best_state, bad_epochs = 0.0, None, 0
for epoch in range(1, MAX_EPOCHS + 1):
    model.train()
    perm = torch.randperm(len(x_num_train))
    total_loss = 0.0
    for i in range(0, len(perm), BATCH_SIZE):
        idx = perm[i : i + BATCH_SIZE]
        recon = model(x_cat_train[idx], x_num_train[idx])
        loss = ((recon - x_num_train[idx]) ** 2).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(idx)

    val_score = anomaly_score(splits["val"])
    val_auc = roc_auc_score(splits["val"][target], val_score)
    print(f"epoch {epoch:2d} | 학습 복원 오차 {total_loss / len(perm):.4f} | val ROC-AUC {val_auc:.4f}")
    if val_auc > best_auc:
        best_auc, bad_epochs = val_auc, 0
        best_state = {k: v.clone() for k, v in model.state_dict().items()}
    else:
        bad_epochs += 1
        if bad_epochs >= PATIENCE:
            print("조기 종료")
            break

model.load_state_dict(best_state)

# 4. 평가
scores = {}
for name in ["val", "test"]:
    scores[name] = anomaly_score(splits[name])
    y = splits[name][target]
    print(f"[{name}] ROC-AUC {roc_auc_score(y, scores[name]):.4f} | PR-AUC {average_precision_score(y, scores[name]):.4f}")
    print(f"       평균 이상 점수: 정상 {scores[name][y == 0].mean():.4f} / 사기 {scores[name][y == 1].mean():.4f}")

# 5. 저장
# 예측값은 TransactionID와 함께 저장 → LightGBM 점수와 행끼리 결합
MODEL_DIR.mkdir(exist_ok=True)
PRED_DIR.mkdir(parents=True, exist_ok=True)
torch.save(model.state_dict(), MODEL_DIR / "autoencoder.pt")
for name in ["val", "test"]:
    part = splits[name]
    pd.DataFrame(
        {"TransactionID": part["TransactionID"], target: part[target], "ae_score": scores[name]}
    ).to_parquet(PRED_DIR / f"ae_{name}.parquet", index=False)
print("저장 완료:", MODEL_DIR / "autoencoder.pt", PRED_DIR)
