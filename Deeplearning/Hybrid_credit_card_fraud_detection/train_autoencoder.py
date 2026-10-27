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

BATCH_SIZE = 1024 # 한번의 거래 1024건씩 보고 가중치를 고친다는 의미
MAX_EPOCHS = 100 # 문제집을 최대 100바퀴까지만 돈다는 상한선 (라벨 없는 기준은 오래 좋아져서 30이면 끝까지 감)
PATIENCE = 3  # val 정상 거래 복원 오차가 3에폭 연속 좋아지지 않으면 멈춘다는 조기 종료 기준 => 1에폭 = 가중치 340번 수정
torch.manual_seed(42) # 무작위 시작점을 42로 고정

# 1. 데이터 불러오기 (preprocessing.py의 nn 버전: 결측 채움 + 결측 표시 + 스케일링)
with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    meta = json.load(f)
target = meta["target"]
cat_cols = meta["cat_cols"]
# 복원 대상: 수치형 + 결측 표시 컬럼
# 중앙값으로 채워져 있기 때문에 해당 거래가 결측치인지 알려주기 위해 사용
recon_cols = meta["num_cols"] + meta["na_flag_cols"]

splits = {s: pd.read_parquet(DATA_DIR / "nn" / f"{s}.parquet") for s in ["train", "val", "test"]}

# pandas 표(DataFrame)를 PyTorch가 계산할 수 있는 형태(텐서)로 바꿔주는 함수
# df[cat_cols]: 범주형 컬럼
# .values: 표에서 컬럼 이름, 행 번호를 떼고 숫자만 담긴 배열
# torch.tensor(..., dtype=torch.long): PyTorch 텐서로 바꾸면서 정수형(long)으로 지정
# 이름표로만 쓰고, 각 이름표마다 고유한 벡터를 따로 학습
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

# 입력: 범주형(임베딩) + 수치형/결측 표시 → 16차원으로 압축 → 수치형/결측 표시 복원
# 범주형은 입력으로만 사용: "이 카드·기기라면 보통 이런 수치가 나온다"는 관계를 학습해
# 범주와 수치의 조합이 평소와 다르면 복원 오차가 커짐
class AutoEncoder(nn.Module):
    def __init__(self, cat_sizes, n_recon, bottleneck=16):
        super().__init__()
        # 임베딩 크기: 범주 수의 절반, 최대 16
        self.embeddings = nn.ModuleList( 
            # 범주형 컬럼마다 "번호 → 숫자 묶음" 변환표를 하나씩 만듬
            # 벡터 길이 규칙은 종류 수의 절반, 단 16을 넘지 않게 => 종류 하나를 표현하는 숫자 칸을 16칸으로 제한
            [nn.Embedding(size, min(16, (size + 1) // 2)) for size in cat_sizes]
        )
        emb_dim = sum(e.embedding_dim for e in self.embeddings) # 입력 크기 계산

        # 인코더
        self.encoder = nn.Sequential(
            nn.Linear(emb_dim + n_recon, 256), nn.ReLU(), nn.Dropout(0.1), # 435개 숫자를 섞고 조합해서 256개로 줄임
            nn.Linear(256, 64), nn.ReLU(), # 음수는 0으로, 양수는 그대로
            nn.Linear(64, bottleneck),
        )
        # 디코더: 16칸에서 원래 모습으로 복원
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck, 64), nn.ReLU(), # 16 → 64
            nn.Linear(64, 256), nn.ReLU(), # 64 → 256
            nn.Linear(256, n_recon), # 256 → 400 (복원 대상 개수)
        )

    def forward(self, x_cat, x_num): # 데이터를 넣으면 어떤 순서로 계산할지
        # x_cat: 범주형 번호 → 크기 (1024, 3) = 거래 1024건 × 범주형 3개
        # x_num: 수치형 + 결측 표시 → 크기 (1024, 400)
        emb = [e(x_cat[:, i]) for i, e in enumerate(self.embeddings)]
        z = self.encoder(torch.cat(emb + [x_num], dim=1))
        return self.decoder(z)


# dam은 **신경망의 가중치를 "어느 방향으로, 얼마나" 고칠지 정하는 방법(옵티마이저)
# 기울기를 그때그때 따르지 않고, 최근 기울기들의 평균 방향으로 움직임
# 가던 방향을 기억하고(관성), 지형이 험한 곳은 조심스럽게, 평탄한 곳은 성큼
model = AutoEncoder([meta["cat_sizes"][c] for c in cat_cols], len(recon_cols))
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# 이상 점수 = 거래별 복원 오차(평균 제곱 오차). 클수록 정상 패턴에서 벗어난 거래
@torch.no_grad() # 학습용 계산 기록을 하지 않겠다는 표시
def anomaly_score(df):
    model.eval()
    x_cat, x_num = to_tensors(df)
    scores = []
    for i in range(0, len(df), 8192): # 거래를 8192건씩 나눠서 처리 => 한 번에 수십만 건을 넣으면 메모리가 부족할 수 있어서 나눔
        recon = model(x_cat[i : i + 8192], x_num[i : i + 8192]) # 8192건을 모델에 넣어 복원 결과
        scores.append(((recon - x_num[i : i + 8192]) ** 2).mean(dim=1)) 
    return torch.cat(scores).numpy()


# 3. 학습
# 모델 선택은 사기 라벨 없이 함: val "정상 거래"의 평균 복원 오차가 가장 작은 에폭
# → 사기 라벨로 고르면(이전 방식) 어떤 사기가 있는지 간접적으로 알게 되어 "미관측 사기 탐지"라고 주장하기 어려움
#   experiment_unseen.py와 같은 방식
# val ROC-AUC는 진행 상황을 보는 참고용으로만 출력하고 선택에는 쓰지 않음
# 오토인코더 학습 → 조기 종료 → 평가 → 저장
# best_loss : 가장 작은 복원 오차 / best_state : 모델의 가중치 / bad_epochs : 최고 기록을 못 넘은 에폭이 몇 번 연속인지
val_normal = splits["val"][splits["val"][target] == 0]
best_loss, best_state, best_epoch, bad_epochs = np.inf, None, 0, 0
for epoch in range(1, MAX_EPOCHS + 1): # 최대 MAX_EPOCHS 에폭 반복
    model.train()
    perm = torch.randperm(len(x_num_train)) # 0부터 (학습 거래 수 − 1)까지의 번호를 무작위로 섞임 => 배치 전체를 하나의 숫자로 평균
    total_loss = 0.0
    for i in range(0, len(perm), BATCH_SIZE):
        idx = perm[i : i + BATCH_SIZE]
        recon = model(x_cat_train[idx], x_num_train[idx]) # 배치를 복원하고 복원 오차(MSE)를 계산
        loss = ((recon - x_num_train[idx]) ** 2).mean()
        optimizer.zero_grad() # 이전 배치의 계산 기록 지우기
        loss.backward() # 오차를 줄이려면 각 가중치를 어느 쪽으로 바꿔야 하는지 계산
        optimizer.step() # Adam이 그 방향으로 가중치 수정
        total_loss += loss.item() * len(idx)

    val_score = anomaly_score(splits["val"])
    val_loss = anomaly_score(val_normal).mean()  # 선택 기준: val 정상 거래의 평균 복원 오차
    val_auc = roc_auc_score(splits["val"][target], val_score)  # 참고용
    print(f"epoch {epoch:2d} | 학습 복원 오차 {total_loss / len(perm):.4f} | "
          f"val 정상 복원 오차 {val_loss:.4f} | (참고) val ROC-AUC {val_auc:.4f}")
    if val_loss < best_loss:
        best_loss, best_epoch, bad_epochs = val_loss, epoch, 0
        best_state = {k: v.clone() for k, v in model.state_dict().items()}
    else:
        bad_epochs += 1
        if bad_epochs >= PATIENCE:
            print("조기 종료")
            break

model.load_state_dict(best_state) # 가장 성적이 좋았던 순간의 가중치로 모델을 되돌리는 코드
print(f"선택한 에폭: {best_epoch}")

# 4. 평가
scores = {} 
for name in ["val", "test"]:
    scores[name] = anomaly_score(splits[name]) # 해당 구간의 모든 거래에 이상 점수를 매겨서 저장해요. 거래 수만큼 숫자가 담긴 배열
    y = splits[name][target]
    print(f"[{name}] ROC-AUC {roc_auc_score(y, scores[name]):.4f} | PR-AUC {average_precision_score(y, scores[name]):.4f}")
    print(f"       평균 이상 점수: 정상 {scores[name][y == 0].mean():.4f} / 사기 {scores[name][y == 1].mean():.4f}")

# ROC-AUC: 사기를 정상보다 위에 줄 세우는 비율
# PR-AUC: 위쪽에 사기가 얼마나 깔끔하게 몰려 있는지

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
