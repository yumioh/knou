"""
퍼지(Fuzzy) 기반 잡음 제거 필터

[퍼지 논리를 아주 쉽게]
보통 논리는 "이 픽셀은 잡음이다 / 아니다"처럼 0 또는 1로 딱 자른다.
퍼지 논리는 "이 픽셀은 0.8만큼 믿을 만하다"처럼 0~1 사이의 '소속 정도'를 쓴다.
이 소속 정도를 계산하는 함수를 "멤버십 함수"라고 부른다.

[이 파일의 두 필터]
1) baseline_fuzzy_filter (베이스라인, 고정형)
   - 주변 픽셀이 "중앙값과 얼마나 비슷한가"를 멤버십 함수로 0~1 점수로 바꾸고
   - 그 점수를 가중치로 써서 가중 평균을 낸다. (Fuzzy Weighted Mean 계열)
   - 멤버십 함수의 폭(sigma)이 영상 전체에서 '고정'되어 있다는 게 한계다.

2) proposed_fuzzy_filter (제안, 적응형)
   - 1단계: 0/255 픽셀을 Salt & Pepper 잡음 후보로 찾아서 그 픽셀만 고친다 (스위칭).
   - 2단계: 지역 분산(local variance)을 보고 멤버십 함수의 폭(sigma)을
            픽셀마다 다르게 조절한다.
            · 평평한 곳(하늘, 벽)  → 폭을 넓게 → 많이 섞어서 잡음을 강하게 제거
            · 경계·무늬가 있는 곳  → 폭을 좁게 → 비슷한 픽셀만 섞어서 에지 보존
"""
import cv2
import numpy as np


# ---------------------------------------------------------------------------
# 공통 도구
# ---------------------------------------------------------------------------
def _window_stack(img, k):
    """
    각 픽셀의 k x k 이웃을 한꺼번에 꺼내서 (k*k, 높이, 너비) 모양으로 쌓는다.

    파이썬 for문으로 픽셀을 하나씩 돌면 512x512 영상에서도 매우 느리다.
    대신 영상을 k*k 방향으로 '한 칸씩 밀어 놓은 복사본'을 겹겹이 쌓으면,
    stack[:, y, x] 가 바로 (y, x) 픽셀의 이웃 k*k개가 된다.
    이렇게 하면 NumPy가 모든 픽셀을 한 번에 계산해서 훨씬 빠르다.
    """
    r = k // 2
    padded = np.pad(img, r, mode="reflect")  # 가장자리는 거울처럼 반사해서 채움
    h, w = img.shape
    return np.stack([padded[dy:dy + h, dx:dx + w] for dy in range(k) for dx in range(k)])


def gaussian_membership(diff, sigma):
    """
    가우시안 멤버십 함수: 차이(diff)가 0이면 1, 차이가 클수록 0에 가까워진다.

        mu = exp( -diff^2 / (2 * sigma^2) )

    sigma(폭)가 클수록 '꽤 다른 픽셀'도 높은 점수를 받는다 → 더 많이 섞임(강한 평활화).
    sigma가 작을수록 '아주 비슷한 픽셀'만 높은 점수를 받는다 → 에지 보존.
    """
    return np.exp(-(diff ** 2) / (2.0 * sigma ** 2))


def _to_uint8(x):
    """계산은 실수(float)로 하고, 마지막에 0~255 정수 영상으로 되돌린다."""
    return np.clip(np.round(x), 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# 1) 베이스라인 퍼지 필터 (고정 파라미터)
# ---------------------------------------------------------------------------
def baseline_fuzzy_filter(img, k=3, sigma=30.0):
    """
    퍼지 가중 평균 필터 (멤버십 함수 폭 sigma 고정).

    각 픽셀마다:
      1) 주변 k x k 이웃의 중앙값(median)을 '기준값'으로 삼는다.
         (중앙값은 튀는 잡음에 잘 흔들리지 않아서 믿을 만한 기준이 된다)
      2) 이웃 픽셀마다 기준값과의 차이를 멤버십 함수에 넣어 0~1 가중치를 얻는다.
      3) 가중치로 가중 평균을 낸다:  결과 = sum(가중치 * 픽셀) / sum(가중치)

    한계: sigma가 영상 전체에서 하나로 고정되어 있다.
      - 잡음이 강하면 sigma가 너무 작아서 잡음이 덜 지워지고
      - 잡음이 약하면 sigma가 너무 커서 에지까지 뭉개진다.
      - Salt & Pepper 잡음이 많아지면 기준값(중앙값) 자체가 잡음이 되어 무너진다.
    """
    x = img.astype(np.float64)
    win = _window_stack(x, k)                 # (k*k, H, W)
    ref = np.median(win, axis=0)              # 픽셀마다 이웃의 중앙값
    w = gaussian_membership(win - ref, sigma) # 이웃마다 0~1 가중치
    out = (w * win).sum(axis=0) / w.sum(axis=0)
    return _to_uint8(out)


# ---------------------------------------------------------------------------
# 2) 제안 필터 (적응형)
# ---------------------------------------------------------------------------
def estimate_noise_sigma(img):
    """
    영상에 섞인 가우시안 잡음의 세기(표준편차)를 영상만 보고 추정한다.
    (Immerkaer, 1996의 빠른 잡음 추정법)

    아래 3x3 마스크는 '부드러운 밝기 변화'에는 거의 0을 내고
    '픽셀마다 들쭉날쭉한 변화(= 잡음)'에 크게 반응한다.
         1 -2  1
        -2  4 -2
         1 -2  1
    그 반응 크기의 평균에 정해진 상수를 곱하면 잡음의 표준편차 추정값이 된다.
    → 사용자가 잡음 세기를 몰라도 필터가 스스로 강도를 정할 수 있다.
    """
    x = img.astype(np.float64)
    kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float64)
    resp = cv2.filter2D(x, -1, kernel)[1:-1, 1:-1]  # 가장자리 1픽셀은 제외
    h, w = x.shape
    return float(np.sqrt(np.pi / 2) * np.abs(resp).sum() / (6.0 * (w - 2) * (h - 2)))


def remove_impulses(img, max_k=9, sigma=20.0):
    """
    [1단계] Salt & Pepper 잡음 제거 (스위칭 방식)

    - 값이 정확히 0 또는 255인 픽셀만 '잡음 후보'로 표시한다.
    - 잡음 후보가 아닌 깨끗한 픽셀은 절대 건드리지 않는다. (← 미디언 필터와의 차이,
      미디언은 깨끗한 픽셀까지 전부 바꿔서 영상이 뭉개진다)
    - 잡음 픽셀은 주변의 '깨끗한 이웃'만 가지고 퍼지 가중 평균으로 채운다.
    - 잡음이 아주 많아서 3x3 안에 깨끗한 이웃이 하나도 없으면
      창을 5x5, 7x7, 9x9로 넓혀가며 찾는다.
    """
    x = img.astype(np.float64)
    noisy = (img == 0) | (img == 255)        # 잡음 후보 위치 (True/False 지도)
    clean = np.where(noisy, np.nan, x)       # 잡음 자리는 NaN(빈칸)으로 지워둠
    out = x.copy()
    todo = noisy.copy()                      # 아직 못 고친 잡음 픽셀

    for k in range(3, max_k + 1, 2):         # 3, 5, 7, 9
        if not todo.any():
            break
        r = k // 2
        padded = np.pad(clean, r, mode="reflect")
        ys, xs = np.nonzero(todo)
        # 고쳐야 하는 픽셀들의 이웃만 꺼냄: (k*k, 잡음픽셀 수)
        win = np.stack([padded[ys + dy, xs + dx] for dy in range(k) for dx in range(k)])

        has_clean = ~np.all(np.isnan(win), axis=0)  # 깨끗한 이웃이 하나라도 있는가
        if not has_clean.any():
            continue
        win = win[:, has_clean]

        ref = np.nanmedian(win, axis=0)                     # 깨끗한 이웃들의 중앙값
        w = np.nan_to_num(gaussian_membership(win - ref, sigma))  # 빈칸(NaN)의 가중치는 0
        val = (w * np.nan_to_num(win)).sum(axis=0) / w.sum(axis=0)

        out[ys[has_clean], xs[has_clean]] = val
        todo[ys[has_clean], xs[has_clean]] = False

    # 9x9 안에도 깨끗한 픽셀이 없는 극단적인 경우는 미디언 값으로 대신한다
    if todo.any():
        out[todo] = cv2.medianBlur(img, 5)[todo]
    return out


def adaptive_fuzzy_smooth(x, noise_sigma, k=5, a_min=1.5, a_max=3.5):
    """
    [2단계] 지역 분산에 따라 멤버십 함수 폭을 바꾸는 퍼지 평활화

    1) 픽셀마다 주변 k x k 창의 분산(local variance)을 구한다.
       분산 = 그 동네 픽셀값이 얼마나 들쭉날쭉한가.
    2) 측정된 분산 = (원래 영상의 무늬/에지 분산) + (잡음 분산) 이므로
       잡음 분산을 빼서 '진짜 무늬의 세기'(signal_var)를 얻는다.
    3) ratio = 잡음분산 / (잡음분산 + 무늬분산)
         · 평평한 곳  : 무늬분산 ≈ 0  → ratio ≈ 1
         · 에지/무늬  : 무늬분산 큼   → ratio ≈ 0
    4) 멤버십 폭 sigma = 잡음세기 * (a_min ~ a_max 사이를 ratio로 섞은 값)
         · 평평한 곳  → 폭 넓게 (잡음세기의 3.5배) → 강하게 평활화
         · 에지/무늬  → 폭 좁게 (잡음세기의 1.5배) → 에지 보존
    5) 가중치는 "가운데 픽셀 자신과 얼마나 비슷한가"로 매긴다.
       (처음엔 베이스라인처럼 중앙값을 기준으로 했는데, 그러면 폭이 좁은 에지에서
        결과가 5x5 미디언처럼 변해 디테일이 뭉개졌다. 가운데 픽셀을 기준으로 하면
        폭이 좁을 때 원래 값이 유지되어 에지가 보존된다.)
    * k, a_min, a_max 값은 가우시안 잡음 σ=10~40 실험에서 정했다.
    """
    if noise_sigma < 1.0:  # 잡음이 거의 없으면 건드리지 않는다
        return x

    noise_var = noise_sigma ** 2
    mean = cv2.blur(x, (k, k))
    mean_sq = cv2.blur(x * x, (k, k))
    local_var = np.maximum(mean_sq - mean ** 2, 0)       # 분산 = E[x^2] - (E[x])^2
    signal_var = np.maximum(local_var - noise_var, 0)    # 잡음 몫을 빼고 남은 무늬의 세기
    ratio = noise_var / (noise_var + signal_var)         # 평평 1 ↔ 에지 0
    sigma_map = noise_sigma * (a_min + (a_max - a_min) * ratio)  # 픽셀마다 다른 폭

    win = _window_stack(x, k)
    w = gaussian_membership(win - x, sigma_map)  # 기준 = 가운데 픽셀, 폭은 픽셀마다 다름
    return (w * win).sum(axis=0) / w.sum(axis=0)


def proposed_fuzzy_filter(img, return_info=False):
    """
    제안하는 적응형 퍼지 필터 = [1단계 스위칭] + [잡음 세기 추정] + [2단계 적응형 평활화]

    잡음 종류를 미리 알려주지 않아도 된다.
      - Salt & Pepper 영상 : 1단계에서 거의 다 지워지고, 남은 잡음 추정값이 작아서
                              2단계는 아주 약하게만 동작한다.
      - Gaussian 영상      : 1단계에서는 고칠 게 거의 없고(0/255로 잘린 픽셀만),
                              2단계가 추정된 잡음 세기에 맞춰 평활화한다.
    """
    step1 = remove_impulses(img)
    sigma_n = estimate_noise_sigma(step1)
    out = _to_uint8(adaptive_fuzzy_smooth(step1, sigma_n))
    if return_info:
        return out, {"impulse_ratio": float(((img == 0) | (img == 255)).mean()),
                     "estimated_sigma": sigma_n}
    return out
