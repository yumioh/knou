"""
영상 품질 평가 지표: PSNR, SSIM

"원본 영상"과 "필터로 복원한 영상"이 얼마나 비슷한지 숫자로 나타낸다.
두 지표 모두 값이 클수록 복원이 잘 된 것이다.
"""
import cv2
import numpy as np


def psnr(original, restored):
    """
    PSNR (Peak Signal-to-Noise Ratio, 최대 신호 대 잡음비), 단위 dB

    1) 두 영상의 픽셀값 차이를 제곱해서 평균을 낸다 → MSE (평균 제곱 오차)
    2) 픽셀이 가질 수 있는 최댓값(255)과 비교해서 로그 스케일로 바꾼다

    보통 30dB 이상이면 눈으로 보기에 꽤 괜찮고, 40dB 이상이면 거의 구분이 안 된다.
    """
    a = original.astype(np.float64)
    b = restored.astype(np.float64)
    mse = np.mean((a - b) ** 2)
    if mse == 0:  # 완전히 똑같으면 무한대
        return float("inf")
    return 10 * np.log10(255.0 ** 2 / mse)


def ssim(original, restored):
    """
    SSIM (Structural Similarity, 구조적 유사도), 범위 0~1 (1이면 완전히 같음)

    PSNR은 픽셀값 차이만 보지만, 사람 눈은 "밝기·대비·구조(무늬)"가
    비슷한지를 더 중요하게 본다. SSIM은 영상을 작은 창(11x11)으로 훑으면서
    창마다 아래 세 가지를 비교한다.
      - 밝기 : 두 창의 평균(mu)이 비슷한가
      - 대비 : 두 창의 분산(sigma^2)이 비슷한가
      - 구조 : 두 창이 같이 밝아지고 같이 어두워지는가 (공분산)
    그리고 모든 창의 점수를 평균낸다.
    (Wang et al., 2004 논문의 표준 식과 표준 상수를 그대로 사용)
    """
    a = original.astype(np.float64)
    b = restored.astype(np.float64)

    # 분모가 0이 되는 것을 막는 작은 상수 (논문에서 정한 값)
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    # 11x11 가우시안 창 안에서의 "가중 평균"을 구하는 함수
    def local_mean(x):
        return cv2.GaussianBlur(x, (11, 11), 1.5)

    mu_a, mu_b = local_mean(a), local_mean(b)
    var_a = local_mean(a * a) - mu_a ** 2      # 창 안의 분산 = E[x^2] - (E[x])^2
    var_b = local_mean(b * b) - mu_b ** 2
    cov_ab = local_mean(a * b) - mu_a * mu_b   # 창 안의 공분산

    ssim_map = ((2 * mu_a * mu_b + C1) * (2 * cov_ab + C2)) / (
        (mu_a ** 2 + mu_b ** 2 + C1) * (var_a + var_b + C2)
    )
    return float(ssim_map.mean())
