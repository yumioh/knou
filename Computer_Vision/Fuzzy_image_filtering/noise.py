"""
실험용 잡음(노이즈) 만들기

깨끗한 영상에 일부러 잡음을 넣어야 "필터가 얼마나 잘 지웠는지"를
원본과 비교해서 점수(PSNR, SSIM)로 매길 수 있다.

- Salt & Pepper(소금-후추) 잡음: 픽셀 일부가 갑자기 완전 흰색(255) 또는
  완전 검은색(0)으로 바뀌는 잡음. 화면에 소금·후추를 뿌린 것처럼 보인다.
- Gaussian(가우시안) 잡음: 모든 픽셀에 조금씩 랜덤한 값이 더해지는 잡음.
  사진이 전체적으로 "자글자글"해 보인다.
"""
import numpy as np


def add_salt_pepper(img, density, seed=0):
    """
    Salt & Pepper 잡음을 넣는다.

    img     : 흑백 영상 (uint8, 0~255)
    density : 잡음 비율. 0.3이면 전체 픽셀의 30%가 0 또는 255로 바뀐다.
    seed    : 난수 시드. 같은 값이면 항상 같은 위치에 잡음이 생겨 실험을 다시 해도 결과가 같다.
    """
    rng = np.random.default_rng(seed)
    noisy = img.copy()

    # 픽셀마다 0~1 사이 난수를 하나씩 뽑는다
    r = rng.random(img.shape)

    # 난수가 density/2 보다 작으면 검은색(후추), density/2 ~ density 이면 흰색(소금)
    # → 결과적으로 density 비율만큼 잡음이 생기고, 흰/검이 반반씩 섞인다
    noisy[r < density / 2] = 0
    noisy[(r >= density / 2) & (r < density)] = 255
    return noisy


def add_gaussian(img, sigma, seed=0):
    """
    Gaussian 잡음을 넣는다.

    sigma : 잡음의 세기(표준편차). 클수록 영상이 더 지저분해진다.
            예) sigma=10 이면 픽셀값이 대략 ±10 정도 흔들린다.
    """
    rng = np.random.default_rng(seed)

    # 평균 0, 표준편차 sigma인 정규분포 난수를 픽셀마다 더한다
    noise = rng.normal(0, sigma, img.shape)
    noisy = img.astype(np.float64) + noise

    # 더한 결과가 0보다 작거나 255보다 커질 수 있으므로 0~255 범위로 잘라준다
    return np.clip(noisy, 0, 255).round().astype(np.uint8)
