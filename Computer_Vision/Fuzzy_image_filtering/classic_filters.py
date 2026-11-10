"""
비교군: 전통적인 공간 영역 필터 (OpenCV 함수 사용)

"공간 영역 필터"란 각 픽셀을 그 주변 이웃 픽셀들(예: 3x3 창)을 보고
새 값으로 바꾸는 방법이다. 어떤 규칙으로 바꾸느냐에 따라 이름이 달라진다.

공정한 비교를 위해 모든 필터의 파라미터는 실험 내내 고정한다.
"""
import cv2


def mean_filter(img, k=3):
    """평균 필터: 주변 k x k 픽셀의 단순 평균. 잡음은 줄지만 경계(에지)도 같이 흐려진다."""
    return cv2.blur(img, (k, k))


def gaussian_filter(img, k=5, sigma=1.0):
    """
    가우시안 필터: 가운데 픽셀에 가까울수록 더 큰 가중치를 주는 평균.
    평균 필터보다 자연스럽게 흐려지지만, 역시 에지가 흐려진다.
    """
    return cv2.GaussianBlur(img, (k, k), sigma)


def median_filter(img, k=3):
    """
    미디언 필터: 주변 k x k 픽셀을 크기순으로 줄 세워 가운데 값(중앙값)을 고른다.
    0이나 255 같은 튀는 값은 줄의 맨 끝으로 밀려나 선택되지 않으므로
    Salt & Pepper 잡음에 특히 강하다.
    """
    return cv2.medianBlur(img, k)


def bilateral_filter(img, d=5, sigma_color=40, sigma_space=5):
    """
    양방향(Bilateral) 필터: 가우시안 필터 + "밝기 차이" 조건.
    - 가까운 픽셀일수록(sigma_space) 그리고
    - 밝기가 비슷한 픽셀일수록(sigma_color) 큰 가중치를 준다.
    밝기가 확 다른 경계 건너편 픽셀은 거의 섞지 않으므로 에지가 잘 보존된다.
    """
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
