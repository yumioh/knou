"""
전체 실험 실행 스크립트

실행 방법 (이 폴더에서):  python run_experiment.py

하는 일
  1) images/ 폴더의 테스트 영상 4장을 흑백으로 읽는다.
  2) 잡음 2종류 x 강도 4단계로 잡음 영상을 만든다.
       - Salt & Pepper 밀도 : 10%, 30%, 50%, 70%
       - Gaussian 표준편차  : 10, 20, 30, 40
  3) 필터 6개(평균, 가우시안, 미디언, 양방향, 베이스라인 퍼지, 제안 퍼지)를 똑같이 적용한다.
  4) 원본과 비교해 PSNR, SSIM, 처리 시간을 기록한다.
  5) 결과를 표(results/*.csv)와 그림(figures/*.png)으로 저장한다.
"""
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from classic_filters import bilateral_filter, gaussian_filter, mean_filter, median_filter
from fuzzy_filters import baseline_fuzzy_filter, proposed_fuzzy_filter
from metrics import psnr, ssim
from noise import add_gaussian, add_salt_pepper

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
RESULT_DIR = BASE_DIR / "results"
FIG_DIR = BASE_DIR / "figures"
RESULT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

# 테스트 영상 (scikit-image 표준 테스트 영상, 흑백으로 변환해서 사용)
IMAGES = {
    "hanok": "hanok.jpg",            # 사진사: 하늘(평탄) + 사람·카메라(에지)
    "frame": "frame.jpg",              # 동전: 둥근 경계가 많음
    "woman": "woman.jpg",                # 달 표면: 부드러운 질감
    "mountain": "mountain.jpg",  # 우주인: 밝게 포화된(255) 영역이 많음
}

# 잡음 종류와 강도
NOISES = {
    "Salt&Pepper": (add_salt_pepper, [0.1, 0.3, 0.5, 0.7]),
    "Gaussian": (add_gaussian, [10, 20, 30, 40]),
}

# 비교할 필터 (이름: 함수). 순서가 곧 그래프의 색 순서다.
FILTERS = {
    "Mean": mean_filter,
    "Gaussian": gaussian_filter,
    "Median": median_filter,
    "Bilateral": bilateral_filter,
    "Baseline Fuzzy": baseline_fuzzy_filter,
    "Proposed Fuzzy": proposed_fuzzy_filter,
}

# 그래프 색: 색각 이상이 있어도 구분되도록 검증된 팔레트 (다른 과제 코드와 동일 계열)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
MARKERS = ["o", "s", "^", "D", "v", "*"]  # 색만으로 구분하지 않도록 마커 모양도 다르게
TEXT, TEXT_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "font.family": "Malgun Gothic",  # 한글 표시
    "axes.unicode_minus": False,     # 마이너스 기호 깨짐 방지
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2,
    "ytick.color": TEXT_2,
    "text.color": TEXT,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def load_images():
    """영상을 흑백(그레이스케일)으로 읽어 {이름: 배열} 형태로 돌려준다."""
    return {name: cv2.imread(str(IMG_DIR / f), cv2.IMREAD_GRAYSCALE) for name, f in IMAGES.items()}


def run():
    images = load_images()
    rows = []

    for img_name, img in images.items():
        for noise_name, (add_noise, levels) in NOISES.items():
            for level in levels:
                noisy = add_noise(img, level, seed=0)

                # 필터를 적용하기 전 잡음 영상 자체의 점수도 기록 (기준선)
                rows.append(dict(image=img_name, noise=noise_name, level=level, filter="Noisy (no filter)",
                                 psnr=psnr(img, noisy), ssim=ssim(img, noisy), time_ms=0.0))

                for filt_name, filt in FILTERS.items():
                    start = time.perf_counter()
                    restored = filt(noisy)
                    elapsed = (time.perf_counter() - start) * 1000

                    rows.append(dict(image=img_name, noise=noise_name, level=level, filter=filt_name,
                                     psnr=psnr(img, restored), ssim=ssim(img, restored), time_ms=elapsed))
                print(f"완료: {img_name:10s} {noise_name:12s} {level}")

    df = pd.DataFrame(rows)
    df.to_csv(RESULT_DIR / "results_all.csv", index=False, encoding="utf-8-sig")  # 엑셀에서 한글 안 깨지게
    return df, images


def save_summary(df):
    """영상 4장의 평균 점수를 (잡음, 강도) x 필터 표로 정리해서 저장하고 화면에 출력한다."""
    order = ["Noisy (no filter)"] + list(FILTERS)
    for metric, fmt in [("psnr", "%.2f"), ("ssim", "%.3f")]:
        table = (df.pivot_table(index=["noise", "level"], columns="filter", values=metric, aggfunc="mean")
                   [order])
        table.to_csv(RESULT_DIR / f"summary_{metric}.csv", float_format=fmt, encoding="utf-8-sig")
        print(f"\n===== 평균 {metric.upper()} (영상 4장 평균) =====")
        print(table.to_string(float_format=lambda v: fmt % v))

    t = df[df["filter"] != "Noisy (no filter)"].groupby("filter")["time_ms"].mean()[list(FILTERS)]
    t.to_csv(RESULT_DIR / "summary_time_ms.csv", float_format="%.1f", encoding="utf-8-sig")
    print("\n===== 평균 처리 시간 (ms/영상) =====")
    print(t.to_string(float_format=lambda v: "%.1f" % v))


def plot_curves(df):
    """잡음 강도가 세질수록 필터별 PSNR/SSIM이 어떻게 떨어지는지 꺾은선 그래프로 그린다."""
    avg = df.groupby(["noise", "level", "filter"])[["psnr", "ssim"]].mean().reset_index()
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    xlabels = {"Salt&Pepper": "잡음 밀도", "Gaussian": "잡음 표준편차 σ"}

    for row, noise_name in enumerate(NOISES):
        for col, (metric, label) in enumerate([("psnr", "PSNR (dB)"), ("ssim", "SSIM")]):
            ax = axes[row, col]
            for i, filt_name in enumerate(FILTERS):
                d = avg[(avg["noise"] == noise_name) & (avg["filter"] == filt_name)]
                ax.plot(d["level"], d[metric], color=COLORS[i], marker=MARKERS[i], markersize=8,
                        linewidth=2, label=filt_name)
            ax.set_title(f"{noise_name} 잡음 — {label}", loc="left", fontsize=12, color=TEXT)
            ax.set_xlabel(xlabels[noise_name])
            ax.set_ylabel(label)
            ax.set_xticks(NOISES[noise_name][1])

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("잡음 강도별 필터 성능 (테스트 영상 4장 평균)", y=1.04, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "performance_curves.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_examples(images, img_name="hanok"):
    """같은 잡음 영상에 각 필터를 적용한 결과를 나란히 보여준다 (눈으로 비교)."""
    img = images[img_name]
    cases = [("Salt&Pepper", 0.5), ("Gaussian", 30)]
    fig, axes = plt.subplots(len(cases), len(FILTERS) + 2, figsize=(22, 7.5))

    for row, (noise_name, level) in enumerate(cases):
        noisy = NOISES[noise_name][0](img, level, seed=0)
        panels = [("원본", img), (f"잡음 ({noise_name} {level})", noisy)]
        panels += [(name, f(noisy)) for name, f in FILTERS.items()]
        for col, (title, im) in enumerate(panels):
            ax = axes[row, col]
            ax.imshow(im, cmap="gray", vmin=0, vmax=255)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            sub = "" if col == 0 else f"\n{psnr(img, im):.2f} dB / {ssim(img, im):.3f}"
            ax.set_title(title + sub, fontsize=10)

    fig.suptitle(f"필터별 복원 결과 비교 ({img_name}, 제목 아래 숫자 = PSNR / SSIM)", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"examples_{img_name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    df, images = run()
    save_summary(df)
    plot_curves(df)
    plot_examples(images, "hanok")
    print(f"\n결과 표: {RESULT_DIR}\n그림: {FIG_DIR}")
