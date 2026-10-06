// third_party/ (이미지 읽기/저장)
// images/ (테스트 영상)
// 빌드 명령어 : g++ -O2 -std=c++17 my_hough.cpp -o my_hough.exe

#define STB_IMAGE_IMPLEMENTATION
#include "third_party/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "third_party/stb_image_write.h"

#include <cmath>
#include <cstdio>
#include <vector>

// 테스트 영상 만들기: 검은 배경(0)에 흰 직선(255) 3개
// 정답을 미리 알고 있는 영상으로 Hough 변환 결과를 검증하기 위함
//   가로선 y = 100  ->  theta = -90도, rho = -100  (theta 범위가 -90~89도이므로 90도 대신 -90도로 표현)
//   세로선 x = 200  ->  theta =   0도, rho = 200
//   대각선 y = x    ->  theta = -45도, rho = 0
std::vector<unsigned char> makeTestImage(int w, int h) {
    std::vector<unsigned char> img(w * h, 0);  // 전부 검정으로 초기화

    for (int x = 0; x < w; x++) img[100 * w + x] = 255;      // 가로선
    for (int y = 0; y < h; y++) img[y * w + 200] = 255;      // 세로선
    for (int i = 0; i < w && i < h; i++) img[i * w + i] = 255;  // 대각선

    return img;
}

// 이진화: 밝기가 임계값(th)보다 크면 255(에지), 아니면 0
std::vector<unsigned char> threshold(const std::vector<unsigned char>& src, int th) {
    std::vector<unsigned char> dst(src.size());
    for (size_t i = 0; i < src.size(); i++) {
        dst[i] = (src[i] > th) ? 255 : 0; 
    }
    return dst;
}

// Hough 변환: 누적 배열 만들기 + 투표
//   직선의 Hesse 표준형  rho = x*cos(theta) + y*sin(theta)
//   theta : -90 ~ 89도 (1도 간격, 180칸)     -> 인덱스 t = theta + 90
//   rho   : -D ~ +D    (1픽셀 간격, 2D+1칸)  -> 인덱스 r = rho + D   (D = 영상 대각선 길이)
//   누적 배열은 2차원 [r][t]를 1차원 acc[r * nTheta + t]로 저장
std::vector<int> houghTransform(const std::vector<unsigned char>& edges, int w, int h,
                                int& D, int& nRho, int& nTheta) {
    const double PI = 3.14159265358979;

    D = (int)std::ceil(std::sqrt((double)(w * w + h * h)));
    nTheta = 180;
    nRho = 2 * D + 1;
    std::vector<int> acc(nRho * nTheta, 0);  // 모든 칸ㄹ을 0으로 초기화

    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            if (edges[y * w + x] == 0) continue;  // 에지가 아닌 점은 투표하지 않음

            // 에지 점 (x, y)는 지나갈 수 있는 모든 직선(theta 180개)에 한 표씩 투표
            for (int t = 0; t < nTheta; t++) {
                double theta = (t - 90) * PI / 180.0;  // 도 -> 라디안
                double rho = x * std::cos(theta) + y * std::sin(theta); // 이 점을 지나는 θ 방향 직선의 ρ
                int r = (int)std::round(rho) + D;      // rho -> 배열 인덱스
                acc[r * nTheta + t]++; // 한표
            }
        }
    }
    return acc;
}

// 누적 배열을 이미지로 저장
//   가로축: theta (-90 ~ 89도), 세로축: rho (-D ~ +D)
//   득표 수를 0~255 밝기로 변환: 많이 득표한 칸일수록 밝게
//   그대로 비례시키면 1~2표인 곡선이 너무 어두워서, 제곱근을 씌워 약한 값도 보이게 함
//   theta 축이 180칸뿐이라 가로로 sx배 늘려서 저장
void saveAccumulator(const char* path, const std::vector<int>& acc, int nRho, int nTheta, int maxVote) {
    const int sx = 3;
    int imgW = nTheta * sx, imgH = nRho;
    std::vector<unsigned char> img(imgW * imgH);

    for (int r = 0; r < nRho; r++) {
        for (int x = 0; x < imgW; x++) {
            int t = x / sx;
           img[r * imgW + x] = (unsigned char)(255.0 * std::sqrt((double)acc[r * nTheta + t] / maxVote));
           //img[r * imgW + x] = (unsigned char)(255.0 * acc[r * nTheta + t] / maxVote);
        }
    }
    stbi_write_png(path, imgW, imgH, 1, img.data(), imgW);
}

// 검출된 직선 하나
struct Line {
    int rho;    // 원점에서 직선까지의 거리
    int theta;  // 법선의 각도 (도)
    int votes;  // 득표 수
};

// 직선 찾기: 누적 배열에서 득표 수가 임계값(th) 이상인 칸을 직선으로 판정 (강의 p.13)
//   win = 0 : 임계값만 검사
//   win > 0 : 지역 최대 검사 추가. 주변 (2*win+1) x (2*win+1) 칸 중 가장 큰 칸만 직선으로 인정
//             -> 한 직선의 피크 주변 칸들이 중복 검출되는 문제를 막음
std::vector<Line> findLines(const std::vector<int>& acc, int nRho, int nTheta, int D, int th, int win) {
    std::vector<Line> lines;

    for (int r = 0; r < nRho; r++) {
        for (int t = 0; t < nTheta; t++) {
            int v = acc[r * nTheta + t];
            if (v < th) continue;  // 임계값 미만이면 직선 아님

            // 지역 최대 검사
            bool isMax = true;
            for (int dr = -win; dr <= win && isMax; dr++) {
                for (int dt = -win; dt <= win; dt++) {
                    int rr = r + dr, tt = t + dt;
                    if (rr < 0 || rr >= nRho) continue;

                    // theta 축의 양 끝은 이어져 있음: (rho, -90도) == (-rho, +90도)
                    // 범위를 벗어나면 반대쪽 끝으로 넘어가면서 rho 부호를 뒤집음
                    if (tt < 0)       { tt += nTheta; rr = nRho - 1 - rr; }
                    if (tt >= nTheta) { tt -= nTheta; rr = nRho - 1 - rr; }

                    int nv = acc[rr * nTheta + tt];
                    // 이웃이 더 크면 최대 아님. 같은 값이면 앞쪽 칸 하나만 남김
                    if (nv > v || (nv == v && rr * nTheta + tt < r * nTheta + t)) {
                        isMax = false;
                        break;
                    }
                }
            }
            if (isMax) lines.push_back({r - D, t - 90, v});  // 인덱스 -> 실제 rho, theta
        }
    }
    return lines;
}

// 흑백 영상 -> 컬러(RGB) 영상: 빨간 직선을 그리기 위해 R=G=B=밝기로 복사
std::vector<unsigned char> grayToRgb(const std::vector<unsigned char>& gray) {
    std::vector<unsigned char> rgb(gray.size() * 3);
    for (size_t i = 0; i < gray.size(); i++) {
        rgb[i * 3 + 0] = rgb[i * 3 + 1] = rgb[i * 3 + 2] = gray[i];
    }
    return rgb;
}

// 빨간 점 찍기 (굵기 2픽셀). 영상 밖 좌표는 무시
void setRed(std::vector<unsigned char>& rgb, int w, int h, int x, int y) {
    for (int dy = 0; dy <= 1; dy++) {
        for (int dx = 0; dx <= 1; dx++) {
            int px = x + dx, py = y + dy;
            if (px < 0 || py < 0 || px >= w || py >= h) continue;
            int i = (py * w + px) * 3;
            rgb[i + 0] = 255; rgb[i + 1] = 0; rgb[i + 2] = 0;
        }
    }
}

// 두 점 (x1, y1) ~ (x2, y2)를 잇는 선분 그리기 (cv.line에 해당)
// Bresenham 알고리즘: 정수 덧셈만으로 직선에 가장 가까운 픽셀을 차례로 선택
void drawSegment(std::vector<unsigned char>& rgb, int w, int h, int x1, int y1, int x2, int y2) {
    int dx = std::abs(x2 - x1), dy = -std::abs(y2 - y1);
    int sx = (x1 < x2) ? 1 : -1, sy = (y1 < y2) ? 1 : -1;
    int err = dx + dy;  // 오차: 실제 직선과 현재 픽셀의 차이
    while (true) {
        setRed(rgb, w, h, x1, y1);
        if (x1 == x2 && y1 == y2) break;
        int e2 = 2 * err;
        if (e2 >= dy) { err += dy; x1 += sx; }  // x 방향으로 한 칸
        if (e2 <= dx) { err += dx; y1 += sy; }  // y 방향으로 한 칸
    }
}

// 검출된 직선 (rho, theta) 그리기 (강의 p.15)
//   (x0, y0) = (rho*cos, rho*sin) : 원점에서 직선에 내린 수선의 발 (직선 위의 한 점)
//   (-sin, cos)                    : 직선의 방향 (법선 (cos, sin)에 수직)
//   직선 위의 점에서 양쪽으로 len만큼 연장한 두 점을 이음
//   강의에서는 len = 1000이지만, 영상이 커도 끝까지 그려지도록 영상 대각선 길이(D)를 사용
void drawLine(std::vector<unsigned char>& rgb, int w, int h, const Line& line, int len) {
    const double PI = 3.14159265358979;
    double theta = line.theta * PI / 180.0;
    double a = std::cos(theta), b = std::sin(theta);
    double x0 = a * line.rho, y0 = b * line.rho;
    int x1 = (int)std::round(x0 + len * (-b));
    int y1 = (int)std::round(y0 + len * a);
    int x2 = (int)std::round(x0 - len * (-b));
    int y2 = (int)std::round(y0 - len * a);
    drawSegment(rgb, w, h, x1, y1, x2, y2);
}

// Sobel 에지 검출: 밝기 변화(그래디언트)의 크기가 임계값(th)보다 크면 255(에지), 아니면 0
//   Gx = [-1 0 1]      Gy = [-1 -2 -1]
//        [-2 0 2]           [ 0  0  0]
//        [-1 0 1]           [ 1  2  1]
//   크기 = sqrt(Gx^2 + Gy^2)
std::vector<unsigned char> sobel(const std::vector<unsigned char>& gray, int w, int h, int th) {
    std::vector<unsigned char> edges(w * h, 0);
    for (int y = 1; y < h - 1; y++) {          // 3x3 마스크가 영상 밖으로 나가지 않도록 테두리 1픽셀 제외
        for (int x = 1; x < w - 1; x++) {
            auto I = [&](int dx, int dy) { return (int)gray[(y + dy) * w + (x + dx)]; };
            int gx = -I(-1, -1) - 2 * I(-1, 0) - I(-1, 1) + I(1, -1) + 2 * I(1, 0) + I(1, 1);
            int gy = -I(-1, -1) - 2 * I(0, -1) - I(1, -1) + I(-1, 1) + 2 * I(0, 1) + I(1, 1);
            double mag = std::sqrt((double)(gx * gx + gy * gy));
            edges[y * w + x] = (mag > th) ? 255 : 0;
        }
    }
    return edges;
}

// 누적 배열의 최댓값
int maxOf(const std::vector<int>& acc) {
    int m = 0;
    for (int v : acc) if (v > m) m = v;
    return m;
}

int main() {
    // 0. 테스트 영상 만들기
    int tw = 300, th = 300;
    std::vector<unsigned char> test = makeTestImage(tw, th);
    stbi_write_png("results/test_lines.png", tw, th, 1, test.data(), tw);
    printf("저장 완료: results/test_lines.png\n");

    // 0-1. 테스트 영상 이진화
    std::vector<unsigned char> testBin = threshold(test, 100);
    stbi_write_png("results/test_binary.png", tw, th, 1, testBin.data(), tw);
    printf("저장 완료: results/test_binary.png\n");

    // 0-2. Hough 변환 (누적 배열 + 투표)
    int D, nRho, nTheta;
    std::vector<int> acc = houghTransform(testBin, tw, th, D, nRho, nTheta);
    printf("누적 배열 크기: %d(rho) x %d(theta), D = %d\n", nRho, nTheta, D);

    // 확인: 최대 득표 칸 찾기
    int maxVote = 0, maxR = 0, maxT = 0;
    for (int r = 0; r < nRho; r++) {
        for (int t = 0; t < nTheta; t++) {
            if (acc[r * nTheta + t] > maxVote) {
                maxVote = acc[r * nTheta + t];
                maxR = r;
                maxT = t;
            }
        }
    }
    printf("최대 득표: %d표, theta = %d도, rho = %d\n", maxVote, maxT - 90, maxR - D);

    // 0-3. 누적 배열 이미지 저장
    saveAccumulator("results/test_accumulator1.png", acc, nRho, nTheta, maxVote);
    printf("저장 완료: results/test_accumulator1.png\n");

    // 0-4. 직선 찾기
    int voteTh = 100;  // 득표 임계값

    // (1) 임계값만 적용 -> 피크 주변 칸까지 중복 검출됨
    std::vector<Line> raw = findLines(acc, nRho, nTheta, D, voteTh, 0);
    printf("\n[임계값만 적용] 임계값 %d표 이상: %zu개\n", voteTh, raw.size());

    // (2) 임계값 + 지역 최대 검사 -> 직선마다 하나씩만 검출
    std::vector<Line> lines = findLines(acc, nRho, nTheta, D, voteTh, 5);
    printf("[지역 최대 검사 추가] 검출된 직선: %zu개\n", lines.size());
    for (size_t i = 0; i < lines.size(); i++) {
        printf("  직선 %zu: theta = %4d도, rho = %4d, 득표 = %d\n",
               i + 1, lines[i].theta, lines[i].rho, lines[i].votes);
    }
    printf("\n");

    // 0-5. 직선 그리기
    std::vector<unsigned char> testRgb = grayToRgb(test);
    for (const Line& l : lines) drawLine(testRgb, tw, th, l, D);
    stbi_write_png("results/test_result.png", tw, th, 3, testRgb.data(), tw * 3);
    printf("저장 완료: results/test_result.png\n\n");

    // 1. 이미지 읽기
    int w, h, ch;
    unsigned char* img = stbi_load("images/building_1.jpg", &w, &h, &ch, 3);  // 마지막 3: 항상 RGB 3채널로 읽기
    if (img == nullptr) {
        printf("이미지를 읽을 수 없습니다.\n");
        return 1;
    }
    printf("크기: %d x %d\n", w, h);

    // 2. 그레이스케일 변환
    std::vector<unsigned char> gray(w * h);
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            int i = y * w + x;                   // (x, y) 픽셀의 위치
            unsigned char r = img[i * 3 + 0];
            unsigned char g = img[i * 3 + 1];
            unsigned char b = img[i * 3 + 2];
            gray[i] = (unsigned char)(0.299 * r + 0.587 * g + 0.114 * b);
        }
    }

    // 3. 저장
    stbi_write_png("results/building1_gray.png", w, h, 1, gray.data(), w);
    printf("저장 완료: results/building1_gray.png\n");

    // 4. 건물 사진 이진화 (비교용: 실제 사진에는 이진화만으로 선이 남지 않음을 확인)
    std::vector<unsigned char> grayBin = threshold(gray, 100);
    stbi_write_png("results/building1_binary.png", w, h, 1, grayBin.data(), w);
    printf("저장 완료: results/building1_binary.png\n");

    // 5. Sobel 에지 검출
    int edgeTh = 150;  // 그래디언트 크기 임계값
    std::vector<unsigned char> edges = sobel(gray, w, h, edgeTh);
    stbi_write_png("results/building1_edges.png", w, h, 1, edges.data(), w);
    printf("저장 완료: results/building1_edges.png\n");

    // 6. Hough 변환
    int bD, bRho, bTheta;
    std::vector<int> bAcc = houghTransform(edges, w, h, bD, bRho, bTheta);
    int bMax = maxOf(bAcc);
    printf("누적 배열 크기: %d(rho) x %d(theta), D = %d, 최대 득표 = %d\n", bRho, bTheta, bD, bMax);
    saveAccumulator("results/building1_accumulator.png", bAcc, bRho, bTheta, bMax);
    printf("저장 완료: results/building1_accumulator.png\n");

    // 7. 직선 찾기 + 그리기: 임계값을 바꿔 가며 결과 비교
    int voteThs[] = {500, 400, 250};
    for (int vt : voteThs) {
        std::vector<Line> bLines = findLines(bAcc, bRho, bTheta, bD, vt, 5);
        printf("\n[임계값 %d표] 검출된 직선: %zu개\n", vt, bLines.size());
        for (size_t i = 0; i < bLines.size(); i++) {
            printf("  직선 %2zu: theta = %4d도, rho = %5d, 득표 = %d\n",
                   i + 1, bLines[i].theta, bLines[i].rho, bLines[i].votes);
        }

        std::vector<unsigned char> result(img, img + w * h * 3);  // 원본 컬러 사진 복사
        for (const Line& l : bLines) drawLine(result, w, h, l, bD);
        char path[100];
        snprintf(path, sizeof(path), "results/building1_result_%d.png", vt);
        stbi_write_png(path, w, h, 3, result.data(), w * 3);
        printf("저장 완료: %s\n", path);
    }

    stbi_image_free(img);
    return 0;
}
