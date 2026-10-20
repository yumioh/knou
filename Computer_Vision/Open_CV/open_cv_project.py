import cv2
import numpy as np

""""
1. openCV 얼굴 탬플릿 매칭 
 - 얼굴 사진을 특징 이미지로 사용
 - 웹캠 실시간 영상에서 탬플릿과 가장 잘 맞는 영역 선택
 - 매칭된 영역에 빨간 색 굵은 사격형 표시
 
2. 웹캠을 통한 얼굴 인식
"""

DATA_DIR = Path(__file__).parent / "images" # 내 얼굴 사진 경로
TEMPLATE_WIDTH = 140            # 템플릿 가로 크기(px) - 실습하며 조절
THRESHOLD = 0.55                # 이 값 이상일 때만 매칭으로 인정 (0~1)
SCALES = np.linspace(0.7, 1.3, 7)  # 거리 변화 대응용 다중 스케일
MIRROR = True                   # 웹캠 화면 좌우 반전 여부
BOX_COLOR = (0, 0, 255)         # 빨간색 (BGR)
BOX_THICKNESS = 4               # 굵은 테두리
METHOD = cv2.TM_CCOEFF_NORMED

""" 흑백 변환 + 히토그램 평활화로 조명 변화에 덜 민감하게 """
def preprocess(img_bgr) :
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)

""" 사진 크기를 다시 맞춤 기본 사이즈 : 140px 
    크기를 다시 맞추는 이유는 탬플릿 매칭이 사진 속 얼굴 크기 그대로 웹캠 화면을 훑기 때문
    웹캠 속 내 얼굴 크기와 비슷하게 줄여주는 게 이 코드의 역할이고, 적당한 조정 필요  
"""
def load_template(path, width) :
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return None, None
    h,w = img.shape[:2]
    ratio = width / w
    img = cv2.resize(img, (width, int(h * ratio)), interpolation=cv2.INTER_AREA)
    return img, preprocess(img)

""" 여러 크기로 탬플릿 매칭 후 최고 점수 위치 반환"""
def match_multiscale(gray_frame, templ_gray, scale) :
    # 최고 점수, 그 위치, 그 크기를 담을 변수
    # TM_CCOEFF_NORMED 점수는 -1 ~ 1 범위
    best_val, best_loc, best_size = -0.1, None, None
    # 웹캠 화면 크기
    fh, fw = gray_frame.shape
    for s in scales:
        # 줄일땐 평균 INTER_AREA, 키울땐 INTER_LINEAR
        # fx=s, fy=s는 가로 세로를 같은 배율로 바꿈
        interp = cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR
        t = cv2.resize(tmpl_gray, None, fx=s, fy=s, interpolation=interp)
        # 탬플릿이 화면보다 크면 건너뛰기 = > 탬픔릿이 화면보다 크면 비교를 할 수 없음 => 그 크기는 패스
        th, tw = t.shape
        if th >= fh or tw >= fw:
            continue
        # 탬플릿을 화면 왼쪽 위부터 한칸씩 밀면서, 모든 위치에서 얼마나 비슷한지 점수를 계산
        # res 위치별 점수가 담긴 2차원 배열
        res = cv2.matchTemplate(gray_frame, t, METHOD)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val, best_loc, best_size = max_val, max_loc, (tw, th)
    return best_val, best_loc, best_size




