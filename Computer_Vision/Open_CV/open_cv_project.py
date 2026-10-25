import cv2
import numpy as np
from pathlib import Path

"""
openCV 얼굴 탬플릿 매칭
  1. 특징 이미지 준비
 - 내 얼굴 사진(images/face_photo.jpg)을 적당한 크기로 줄여서
   특징 이미지(images/my_face.jpg)로 저장

   2. 웹캠 매칭
 - 웹캠 실시간 영상에서 특징 이미지와 가장 잘 맞는 영역 선택
 - 매칭된 영역에 빨간 색 굵은 사각형 표시

   3. 웹캠에서 한 장 읽기 (cap.read)
   → 좌우 반전 (MIRROR)
   → 흑백 사본으로 얼굴 찾기
   → 점수 0.55 이상이면 빨간 사각형 + 점수
   → 왼쪽 위에 score / width 표시
   → 화면에 띄우고 키 확인
   → q/ESC면 종료, +/-면 크기 조절
     웹캠 해제, 창 닫기

"""

DATA_DIR = Path(__file__).parent / "images"
PHOTO_PATH = DATA_DIR / "face_photo.jpg"  # 준비한 내 얼굴 사진 (원본)
TEMPLATE_PATH = DATA_DIR / "my_face.jpg"  # 크기를 맞춰 저장한 특징 이미지
TEMPLATE_WIDTH = 220            # 템플릿 가로 크기(px) - 실습하며 조절 (웹캠 화면 640px 기준)
SIZE_STEP = 20                  # +/- 한 번에 바뀌는 크기(px)
THRESHOLD = 0.55                # 이 값 이상일 때만 매칭으로 인정 (0~1)
SCALES = np.linspace(0.7, 1.3, 7)  # 거리 변화 대응용 다중 스케일
MIRROR = True                   # 웹캠 화면 좌우 반전 여부
BOX_COLOR = (0, 0, 255)         # 빨간색 (BGR)
BOX_THICKNESS = 4               # 굵은 테두리
METHOD = cv2.TM_CCOEFF_NORMED

""" cv2.imread / imwrite는 한글 경로를 못 다루므로 numpy로 읽고 씀 
    이미지 파일을 바이트데이터(메모리에 있는 압축된 데이터)를 OpenCV 이미지  배열로 바꿔주는 함수
    np.fromfile : 파일을 바이트 배열로 읽음. cv2.imdecode : 바이트를 이미지로 해석"""
def imread(path) :
    if not Path(path).exists():
        return None
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)

# 이미지 파일을 바이트로 압축
def imwrite(path, img) :
    ok, buf = cv2.imencode(Path(path).suffix, img)
    if ok:
        buf.tofile(str(path))
    return ok

""" 흑백 변환 + 히토그램 평활화로 조명 변화에 덜 민감하게
흑백으로 변환하는 이유는 속도와 조명 변화에 덜 민감하게 하기 위함
다시 컬러로 바꾸는 이유는 흑백 사진에 빨간색을 그릴 수 없기 때문에
흑백 사진은 밝기가 1개인데 빨간색을 3가지 색을 사용해야함 """
def preprocess(img_bgr) :
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)

""" 1단계 : 얼굴 사진 크기를 다시 맞춰서 특징 이미지로 저장 기본 사이즈 : 220px
    크기를 다시 맞추는 이유는 탬플릿 매칭이 사진 속 얼굴 크기 그대로 웹캠 화면을 훑기 때문
    웹캠 속 내 얼굴 크기와 비슷하게 줄여주는 게 이 코드의 역할이고, 적당한 조정 필요
"""
def make_template(photo_path, template_path, width) :
    # 원본 사진 경로
    img = imread(photo_path)
    if img is None:
        return None, None
    h,w = img.shape[:2]
    ratio = width / w
    interp = cv2.INTER_AREA if ratio < 1 else cv2.INTER_LINEAR
    img = cv2.resize(img, (width, int(h * ratio)), interpolation=interp)
    imwrite(template_path, img)
    # 크기를 맞춘 특징 이미지는 저장한 경로
    print(f"특징 이미지 저장: {template_path} ({img.shape[1]}x{img.shape[0]})")
    return img, preprocess(img)

""" 2단계 : 웹캡 화면서 내얼굴이 어디에 있는지 찾는 함수
웹캠의 거리에 따라 얼굴 크기가 달라지니 특징 이미지를 여러 크기로 바꿔가며 가장 잘 맞는 결과를 고름"""
def match_multiscale(gray_frame, tmpl_gray, scales) :
    # 최고 점수, 그 위치, 그 크기를 담을 변수
    # TM_CCOEFF_NORMED 점수는 -1 ~ 1 범위
    best_val, best_loc, best_size = -1.0, None, None
    # 웹캠 화면 크기 : 흑백으로 바꾼 웹캠 화면
    fh, fw = gray_frame.shape
    for s in scales:
        # 줄일땐 평균 INTER_AREA, 키울땐 INTER_LINEAR
        # fx=s, fy=s는 가로 세로를 같은 배율로 바꿈
        interp = cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR
        t = cv2.resize(tmpl_gray, None, fx=s, fy=s, interpolation=interp)
        # 탬플릿이 화면보다 크면 건너뛰기 = > 탬플릿이 화면보다 크면 비교를 할 수 없음 => 그 크기는 패스
        th, tw = t.shape
        if th >= fh or tw >= fw:
            continue
        # 탬플릿을 화면 왼쪽 위부터 한칸씩 밀면서, 모든 위치에서 얼마나 비슷한지 점수를 계산
        # res 위치별 점수가 담긴 2차원 배열
        res = cv2.matchTemplate(gray_frame, t, METHOD)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        # 가장 높은 점수(1에 가까울수록 똑같음)
        # best_loc : 그때 위치 = 사각형의 왼쪽 위 좌표
        # best_size : 그때 특징 이미지 크기 (가로, 세로) = 사각형 크기
        if max_val > best_val:
            best_val, best_loc, best_size = max_val, max_loc, (tw, th)
    return best_val, best_loc, best_size

def main() :
    width = TEMPLATE_WIDTH
    templ, templ_gray = make_template(PHOTO_PATH, TEMPLATE_PATH, width)
    if templ is None:
        print(f"얼굴 사진이 없습니다: {PHOTO_PATH}")
        print("얼굴 부분만 잘라낸 내 사진을 위 경로에 넣고 다시 실행하세요.")
        return

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("웹캠 영상을 읽을 수 없습니다.")
            break
        if MIRROR:
            frame = cv2.flip(frame, 1)

        gray = preprocess(frame)
        score, loc, size = match_multiscale(gray, templ_gray, SCALES)
        # 점수가 0.55일때만 얼굴로 인정 :
        if loc is not None and score >= THRESHOLD:
            x, y = loc
            tw, th = size
            cv2.rectangle(frame, (x, y), (x + tw, y + th), BOX_COLOR, BOX_THICKNESS)
            # 빨간 사각형 바로 위에 매칭 점수를 글자로 써 주는 코드
            # 사각형 윗변y 보다 10px
            cv2.putText(frame, f"{score:.2f}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, BOX_COLOR, 2)
        # 현재 점수와 탬플릿 크기 표시 
        # 글꼴 : cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"score {score:.2f}  width {width}px", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("face template matching", frame)
        # & 0xFF : 키 코드(마지막 8비트)만 남김
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key in (ord('+'), ord('=')):
            width += SIZE_STEP
            templ, templ_gray = make_template(PHOTO_PATH, TEMPLATE_PATH, width)
        elif key == ord('-') and width > 40:
            width -= SIZE_STEP
            templ, templ_gray = make_template(PHOTO_PATH, TEMPLATE_PATH, width)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
