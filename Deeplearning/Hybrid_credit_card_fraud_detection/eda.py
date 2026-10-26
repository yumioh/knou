# %% [markdown]
# # IEEE-CIS 사기 탐지 데이터 탐색 (EDA)
# 전처리 전 원본 데이터로 분포를 확인 (전처리 후에는 번호·스케일이 바뀌어 해석이 어려움)
# VS Code에서 "Run Cell"로 셀 단위 실행 가능. 그림은 figures/ 폴더에도 저장됨

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "ieee"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

# 색: 정상 = 파랑, 사기 = 주황 (색각 이상이 있어도 구분되는 조합으로 검증함)
NORMAL, FRAUD = "#2a78d6", "#eb6834"
MISSING = "#8a8984"  # 결측은 중립 회색
TEXT, TEXT_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
# 글자 뒤에 배경을 깔아 점선·막대와 겹쳐도 읽히게 함
LABEL_BOX = {"facecolor": SURFACE, "edgecolor": "none", "pad": 1}

plt.rcParams.update({
    "font.family": "Malgun Gothic",  # 한글 표시
    "axes.unicode_minus": False,     # 한글 폰트에서 마이너스 기호 깨짐 방지
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_2,
    "axes.titlecolor": TEXT,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": TEXT_2,
    "ytick.color": TEXT_2,
    "legend.frameon": False,
    "figure.dpi": 110,
})


def save(fig, name):
    fig.savefig(FIG_DIR / f"{name}.png", bbox_inches="tight", facecolor=SURFACE)
    plt.show()


# %%
transaction = pd.read_csv(RAW_DIR / "train_transaction.csv")
identity = pd.read_csv(RAW_DIR / "train_identity.csv")
df = transaction.merge(identity, on="TransactionID", how="left")
del transaction, identity

overall_rate = df["isFraud"].mean()
df["Day"] = df["TransactionDT"] // 86400
df["Hour"] = (df["TransactionDT"] // 3600) % 24
print(f"거래 {len(df):,}건, 컬럼 {df.shape[1]}개, 사기 {df['isFraud'].sum():,}건 ({overall_rate:.2%})")

# %% [markdown]
# ## 1. 시간에 따른 거래 수와 사기 비율
# 점선은 preprocessing.py의 시간순 분할 경계 (train 60% / val 20% / test 20%)

# %%
daily = df.groupby("Day").agg(count=("isFraud", "size"), fraud_rate=("isFraud", "mean"))
sorted_days = df["Day"].sort_values().values
split_days = [sorted_days[int(len(df) * 0.6)], sorted_days[int(len(df) * 0.8)]]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
ax1.plot(daily.index, daily["count"], color=NORMAL, linewidth=2)
ax1.set_title("일별 거래 수")
ax1.set_ylabel("거래 수")
ax2.plot(daily.index, daily["fraud_rate"] * 100, color=FRAUD, linewidth=2)
ax2.axhline(overall_rate * 100, color=TEXT_2, linewidth=1, linestyle=":")
ax2.text(daily.index.max(), overall_rate * 100, f" 전체 평균 {overall_rate:.1%}", va="bottom", ha="right", color=TEXT_2, fontsize=9, bbox=LABEL_BOX)
ax2.set_title("일별 사기 비율")
ax2.set_ylabel("사기 비율 (%)")
ax2.set_xlabel("기준 시점부터 경과 일수")
for ax in (ax1, ax2):
    for d in split_days:
        ax.axvline(d, color=TEXT_2, linewidth=1, linestyle="--")
for x, label in zip([0, *split_days], ["train", "val", "test"]):
    ax1.text(x + 2, ax1.get_ylim()[1] * 0.97, label, va="top", color=TEXT_2, fontsize=10)
fig.tight_layout()
save(fig, "01_daily_trend")

# %% [markdown]
# ## 2. 결제 금액 분포 (정상 vs 사기)
# 사기가 3.5%뿐이라 건수로 그리면 사기 분포가 안 보이므로, 각 그룹 안에서의 비율(밀도)로 비교

# %%
bins = np.logspace(np.log10(df["TransactionAmt"].min()), np.log10(df["TransactionAmt"].max()), 60)
fig, ax = plt.subplots(figsize=(11, 4.5))
for label, color, mask in [("정상", NORMAL, df["isFraud"] == 0), ("사기", FRAUD, df["isFraud"] == 1)]:
    ax.hist(df.loc[mask, "TransactionAmt"], bins=bins, density=True, histtype="step", linewidth=2, color=color, label=label)
ax.set_xscale("log")
ax.set_title("결제 금액 분포 (로그 축)")
ax.set_xlabel("결제 금액 ($)")
ax.set_ylabel("밀도")
ax.legend(loc="upper right")
fig.tight_layout()
save(fig, "02_amount_distribution")
print(df.groupby("isFraud")["TransactionAmt"].describe().round(2))

# %% [markdown]
# ## 3. 시간대별 사기 비율
# Hour는 기준 시점을 자정으로 가정한 상대적인 값 (실제 시각과 어긋날 수 있음)

# %%
hourly = df.groupby("Hour")["isFraud"].mean() * 100
fig, ax = plt.subplots(figsize=(11, 4))
ax.bar(hourly.index, hourly.values, color=NORMAL, width=0.8)
ax.axhline(overall_rate * 100, color=TEXT_2, linewidth=1, linestyle=":")
ax.text(23.5, overall_rate * 100, f"전체 평균 {overall_rate:.1%}", va="bottom", ha="right", color=TEXT_2, fontsize=9, bbox=LABEL_BOX)
ax.set_title("시간대별 사기 비율")
ax.set_xlabel("시간대 (Hour)")
ax.set_ylabel("사기 비율 (%)")
ax.set_xticks(range(24))
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "03_hourly_fraud_rate")

# %% [markdown]
# ## 4. 범주형 변수별 사기 비율
# 막대 옆 숫자는 거래 수. 거래 수가 적은 범주의 비율은 우연에 크게 흔들리므로 함께 확인할 것

# %%
cat_specs = [
    ("ProductCD", "상품 종류", None),
    ("card4", "카드 브랜드", None),
    ("card6", "카드 종류", None),
    ("DeviceType", "기기 종류", None),
    ("P_emaildomain", "구매자 이메일 도메인 (거래 수 상위 10개)", 10),
    ("id_31", "브라우저 (거래 수 상위 10개)", 10),
]
fig, axes = plt.subplots(3, 2, figsize=(12, 12))
for ax, (col, title, top) in zip(axes.flat, cat_specs):
    stats = df.groupby(df[col].fillna("(결측)"))["isFraud"].agg(["mean", "size"])
    stats = stats.sort_values("size", ascending=False)
    if top:
        stats = stats.head(top)
    stats = stats.sort_values("mean")
    ax.barh(stats.index.astype(str), stats["mean"] * 100, color=NORMAL, height=0.7)
    ax.axvline(overall_rate * 100, color=TEXT_2, linewidth=1, linestyle=":")
    for y, (rate, size) in enumerate(zip(stats["mean"] * 100, stats["size"])):
        ax.text(rate, y, f"  {rate:.1f}% (n={size:,})", va="center", color=TEXT_2, fontsize=8, bbox=LABEL_BOX)
    ax.set_title(title, loc="left")
    ax.set_xlabel("사기 비율 (%)")
    ax.set_xlim(0, stats["mean"].max() * 100 * 1.6)
    ax.grid(axis="y", visible=False)
fig.suptitle("범주형 변수별 사기 비율 (점선: 전체 평균 3.5%)", x=0.01, ha="left", fontsize=13, fontweight="bold", color=TEXT)
fig.tight_layout()
save(fig, "04_categorical_fraud_rate")

# %% [markdown]
# ## 5. 컬럼 그룹별 결측률

# %%
def group_of(col):
    for prefix in ["card", "addr", "dist", "id_", "C", "D", "M", "V"]:
        if col.startswith(prefix) and (prefix in ["card", "addr", "dist", "id_"] or col[len(prefix):].isdigit()):
            return prefix.rstrip("_")
    return None


missing = df.isna().mean()
groups = pd.Series({c: group_of(c) for c in df.columns}).dropna()
group_missing = missing[groups.index].groupby(groups).mean().sort_values() * 100
group_sizes = groups.value_counts()

fig, ax = plt.subplots(figsize=(11, 4))
ax.barh(group_missing.index, group_missing.values, color=MISSING, height=0.7)
for y, (g, rate) in enumerate(group_missing.items()):
    ax.text(rate, y, f"  {rate:.0f}% ({group_sizes[g]}개 컬럼)", va="center", color=TEXT_2, fontsize=9, bbox=LABEL_BOX)
ax.set_title("컬럼 그룹별 평균 결측률")
ax.set_xlabel("결측률 (%)")
ax.set_xlim(0, 100)
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "05_missing_by_group")

# %% [markdown]
# ## 6. 결측 여부에 따른 사기 비율
# 결측률이 높은 컬럼도 "값이 있는지 없는지"가 사기와 관련 있음 → 전처리에서 컬럼을 지우지 않은 이유

# %%
check_cols = ["D7", "dist2", "id_18", "id_07", "D1", "M4", "DeviceInfo", "R_emaildomain"]
rows = []
for col in check_cols:
    na = df[col].isna()
    rows.append((col, df.loc[~na, "isFraud"].mean() * 100, df.loc[na, "isFraud"].mean() * 100, na.mean() * 100))
na_stats = pd.DataFrame(rows, columns=["col", "present", "missing", "missing_rate"]).set_index("col")

y = np.arange(len(na_stats))
fig, ax = plt.subplots(figsize=(11, 5))
ax.barh(y + 0.2, na_stats["present"], height=0.38, color=NORMAL, label="값 있음")
ax.barh(y - 0.2, na_stats["missing"], height=0.38, color=MISSING, label="결측")
for i, row in enumerate(na_stats.itertuples()):
    ax.text(row.present, i + 0.2, f"  {row.present:.1f}%", va="center", color=TEXT_2, fontsize=8, bbox=LABEL_BOX)
    ax.text(row.missing, i - 0.2, f"  {row.missing:.1f}%", va="center", color=TEXT_2, fontsize=8, bbox=LABEL_BOX)
ax.set_yticks(y, [f"{c} (결측 {r:.0f}%)" for c, r in na_stats["missing_rate"].items()])
ax.axvline(overall_rate * 100, color=TEXT_2, linewidth=1, linestyle=":")
ax.set_title("값이 있을 때 vs 결측일 때의 사기 비율")
ax.set_xlabel("사기 비율 (%)")
ax.set_xlim(0, na_stats[["present", "missing"]].max().max() * 1.2)
ax.legend(loc="lower right")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "06_fraud_rate_by_missing")

# %% [markdown]
# ## 7. 주요 수치형 변수 분포 (정상 vs 사기)
# LightGBM 중요도 상위 변수. 값이 한쪽으로 크게 치우쳐 있어 log(1 + x) 축으로 표시, 결측은 제외

# %%
num_specs = [
    ("C1", "C1 (횟수)"), ("C13", "C13 (횟수)"), ("C14", "C14 (횟수)"),
    ("D1", "D1 (경과 일수)"), ("D2", "D2 (경과 일수)"), ("D15", "D15 (경과 일수)"),
]
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for ax, (col, title) in zip(axes.flat, num_specs):
    values = np.log1p(df[col].clip(lower=0))
    bins = np.linspace(values.min(), values.quantile(0.999), 40)
    for label, color, mask in [("정상", NORMAL, df["isFraud"] == 0), ("사기", FRAUD, df["isFraud"] == 1)]:
        ax.hist(values[mask].dropna(), bins=bins, density=True, histtype="step", linewidth=2, color=color, label=label)
    ax.set_title(title, loc="left")
    ax.set_xlabel(f"log(1 + {col})")
axes.flat[0].legend(loc="upper right")
fig.suptitle("주요 수치형 변수 분포 (각 그룹 내 밀도)", x=0.01, ha="left", fontsize=13, fontweight="bold", color=TEXT)
fig.tight_layout()
save(fig, "07_numeric_distributions")

# %% [markdown]
# ## 8. 일별 거래 수 vs 사기 비율 (산점도)
# 점 하나 = 하루. 상관계수(r)는 피어슨: 두 값이 직선 관계에 얼마나 가까운지 (-1 ~ 1)
# 처음 25일은 거래가 많고 사기 비율이 낮은 특이한 시기라 따로 표시
# → 전체로는 음의 상관처럼 보이지만, 이 기간을 빼면 거의 0

# %%
EARLY_COLOR = "#1baf7a"  # 처음 25일 (정상·사기 색과 겹치지 않는 청록)
EARLY_DAYS = 25

early = daily.index <= EARLY_DAYS
r_all = daily["count"].corr(daily["fraud_rate"])
r_rest = daily.loc[~early, "count"].corr(daily.loc[~early, "fraud_rate"])

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(daily.loc[~early, "count"], daily.loc[~early, "fraud_rate"] * 100, s=40, color=NORMAL,
           edgecolors=SURFACE, linewidths=1.2, label=f"{EARLY_DAYS + 1}일째 이후 ({(~early).sum()}일)")
ax.scatter(daily.loc[early, "count"], daily.loc[early, "fraud_rate"] * 100, s=40, color=EARLY_COLOR,
           edgecolors=SURFACE, linewidths=1.2, label=f"처음 {EARLY_DAYS}일 ({early.sum()}일)")

# 추세선 (최소제곱 직선): 전체 vs 26일째 이후
x_line = np.linspace(daily["count"].min(), daily["count"].max(), 50)
for mask, style, label in [(slice(None), "--", f"전체 추세 (r = {r_all:.2f})"),
                           (~early, "-", f"{EARLY_DAYS + 1}일째 이후 추세 (r = {r_rest:.2f})")]:
    slope, intercept = np.polyfit(daily.loc[mask, "count"], daily.loc[mask, "fraud_rate"] * 100, 1)
    ax.plot(x_line, slope * x_line + intercept, color=TEXT_2, linewidth=2, linestyle=style, label=label)

# 그룹 이름을 그림 안에도 직접 표시 (청록색은 배경 대비가 낮아 색만으로 구분하지 않음)
# 위치는 이 데이터에서 점이 없는 빈 공간 (데이터 좌표: 거래 수, 사기 비율 %)
ax.text(5300, 1.45, f"처음 {EARLY_DAYS}일", ha="center", va="center", color=TEXT, fontsize=10, bbox=LABEL_BOX)
ax.text(2050, 6.45, f"{EARLY_DAYS + 1}일째 이후", ha="left", va="center", color=TEXT, fontsize=10, bbox=LABEL_BOX)

ax.set_title("일별 거래 수와 사기 비율")
ax.set_xlabel("하루 거래 수")
ax.set_ylabel("사기 비율 (%)")
ax.legend(loc="upper right")
fig.tight_layout()
save(fig, "08_daily_count_vs_fraud_rate")
print(f"피어슨 상관계수: 전체 {r_all:.3f} / {EARLY_DAYS + 1}일째 이후 {r_rest:.3f}")
