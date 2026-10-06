// Hough 변환을 이용한 직선 검출 - 직접 구현
// 이미지 파일 입출력(stb_image)을 제외한 모든 처리(그레이스케일, 가우시안 블러,
// Sobel, Canny 에지, Hough 누적 배열, 피크 검출, 직선 그리기)를 직접 구현한다.
//
// 빌드: g++ -O2 -std=c++17 hough.cpp -o hough.exe
// 실행: hough.exe <입력 이미지> [출력 접두어] [투표 임계값] [최대 직선 수]
//   투표 임계값이 1 미만이면 누적 배열 최댓값에 대한 비율로 해석한다. (기본 0.5)

#define STB_IMAGE_IMPLEMENTATION
#include "third_party/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "third_party/stb_image_write.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

static const double PI = 3.14159265358979323846;

// 단일 채널 실수형 영상
struct Gray {
    int w = 0, h = 0;
    std::vector<float> px;
    Gray() = default;
    Gray(int w_, int h_) : w(w_), h(h_), px((size_t)w_ * h_, 0.f) {}
    float& at(int x, int y) { return px[(size_t)y * w + x]; }
    float at(int x, int y) const { return px[(size_t)y * w + x]; }
    // 경계 밖 좌표는 가장자리 픽셀로 대체 (border replicate)
    float clampAt(int x, int y) const {
        x = std::clamp(x, 0, w - 1);
        y = std::clamp(y, 0, h - 1);
        return at(x, y);
    }
};

// 3채널 8비트 컬러 영상 (결과 출력용)
struct Rgb {
    int w = 0, h = 0;
    std::vector<unsigned char> px;
    void set(int x, int y, unsigned char r, unsigned char g, unsigned char b) {
        if (x < 0 || y < 0 || x >= w || y >= h) return;
        size_t i = ((size_t)y * w + x) * 3;
        px[i] = r; px[i + 1] = g; px[i + 2] = b;
    }
};

struct Line {
    double rho, theta;
    int votes;
};

// ---------------------------------------------------------------- 전처리

// RGB -> Gray (ITU-R BT.601 가중치)
static Gray toGray(const unsigned char* data, int w, int h, int ch) {
    Gray g(w, h);
    for (int i = 0; i < w * h; ++i) {
        const unsigned char* p = data + (size_t)i * ch;
        g.px[i] = (ch >= 3) ? 0.299f * p[0] + 0.587f * p[1] + 0.114f * p[2] : p[0];
    }
    return g;
}

// 분리 가능한(separable) 가우시안 필터: 가로 1D 컨볼루션 후 세로 1D 컨볼루션
static Gray gaussianBlur(const Gray& src, double sigma) {
    int r = (int)std::ceil(3 * sigma);
    std::vector<float> k(2 * r + 1);
    float sum = 0;
    for (int i = -r; i <= r; ++i) sum += k[i + r] = (float)std::exp(-(i * i) / (2 * sigma * sigma));
    for (float& v : k) v /= sum;

    Gray tmp(src.w, src.h), dst(src.w, src.h);
    for (int y = 0; y < src.h; ++y)
        for (int x = 0; x < src.w; ++x) {
            float s = 0;
            for (int i = -r; i <= r; ++i) s += k[i + r] * src.clampAt(x + i, y);
            tmp.at(x, y) = s;
        }
    for (int y = 0; y < src.h; ++y)
        for (int x = 0; x < src.w; ++x) {
            float s = 0;
            for (int i = -r; i <= r; ++i) s += k[i + r] * tmp.clampAt(x, y + i);
            dst.at(x, y) = s;
        }
    return dst;
}

// ---------------------------------------------------------------- Canny 에지 검출

// Sobel 연산자로 그래디언트 크기(mag)와 방향(dir, 라디안)을 계산
static void sobel(const Gray& src, Gray& mag, Gray& dir) {
    mag = Gray(src.w, src.h);
    dir = Gray(src.w, src.h);
    for (int y = 0; y < src.h; ++y)
        for (int x = 0; x < src.w; ++x) {
            auto I = [&](int dx, int dy) { return src.clampAt(x + dx, y + dy); };
            float gx = -I(-1, -1) - 2 * I(-1, 0) - I(-1, 1) + I(1, -1) + 2 * I(1, 0) + I(1, 1);
            float gy = -I(-1, -1) - 2 * I(0, -1) - I(1, -1) + I(-1, 1) + 2 * I(0, 1) + I(1, 1);
            mag.at(x, y) = std::sqrt(gx * gx + gy * gy);
            dir.at(x, y) = std::atan2(gy, gx);
        }
}

// 비최대 억제: 그래디언트 방향(0/45/90/135도)의 양쪽 이웃보다 크지 않으면 제거
static Gray nonMaxSuppression(const Gray& mag, const Gray& dir) {
    Gray out(mag.w, mag.h);
    for (int y = 1; y < mag.h - 1; ++y)
        for (int x = 1; x < mag.w - 1; ++x) {
            double a = dir.at(x, y) * 180.0 / PI;
            if (a < 0) a += 180;
            int dx, dy;
            if (a < 22.5 || a >= 157.5) { dx = 1; dy = 0; }   // 수평 그래디언트
            else if (a < 67.5)          { dx = 1; dy = 1; }   // 45도
            else if (a < 112.5)         { dx = 0; dy = 1; }   // 수직 그래디언트
            else                        { dx = -1; dy = 1; }  // 135도
            float m = mag.at(x, y);
            if (m >= mag.at(x + dx, y + dy) && m >= mag.at(x - dx, y - dy)) out.at(x, y) = m;
        }
    return out;
}

// 이중 임계값 + 히스테리시스: high 이상은 강한 에지, low~high 는 강한 에지와
// 8-연결로 이어진 경우에만 에지로 인정. 결과는 0/255 이진 영상.
static Gray hysteresis(const Gray& nms, float low, float high) {
    Gray out(nms.w, nms.h);
    std::vector<int> stack;
    for (int y = 0; y < nms.h; ++y)
        for (int x = 0; x < nms.w; ++x)
            if (nms.at(x, y) >= high && out.at(x, y) == 0) {
                out.at(x, y) = 255;
                stack.push_back(y * nms.w + x);
                while (!stack.empty()) {
                    int idx = stack.back(); stack.pop_back();
                    int cx = idx % nms.w, cy = idx / nms.w;
                    for (int dy = -1; dy <= 1; ++dy)
                        for (int dx = -1; dx <= 1; ++dx) {
                            int nx = cx + dx, ny = cy + dy;
                            if (nx < 0 || ny < 0 || nx >= nms.w || ny >= nms.h) continue;
                            if (out.at(nx, ny) == 0 && nms.at(nx, ny) >= low) {
                                out.at(nx, ny) = 255;
                                stack.push_back(ny * nms.w + nx);
                            }
                        }
                }
            }
    return out;
}

static Gray canny(const Gray& gray, double sigma, float lowRatio, float highRatio) {
    Gray blurred = gaussianBlur(gray, sigma);
    Gray mag, dir;
    sobel(blurred, mag, dir);
    Gray nms = nonMaxSuppression(mag, dir);
    // 임계값은 그래디언트 최댓값에 대한 비율로 지정 (영상마다 대비가 달라도 동작하도록)
    float maxMag = *std::max_element(mag.px.begin(), mag.px.end());
    return hysteresis(nms, lowRatio * maxMag, highRatio * maxMag);
}

// ---------------------------------------------------------------- Hough 변환

// 직선의 극좌표 표현:  rho = x*cos(theta) + y*sin(theta),  theta ∈ [0, 180)
// 누적 배열 acc[rhoIdx][thetaIdx], rho ∈ [-D, D] (D = 영상 대각선 길이)
struct Accumulator {
    int nRho, nTheta;
    double rhoRes, thetaRes, diag;
    std::vector<int> v;
    int& at(int r, int t) { return v[(size_t)r * nTheta + t]; }
    int at(int r, int t) const { return v[(size_t)r * nTheta + t]; }
};

static Accumulator houghTransform(const Gray& edges, double rhoRes, double thetaResDeg) {
    Accumulator acc;
    acc.rhoRes = rhoRes;
    acc.thetaRes = thetaResDeg * PI / 180.0;
    acc.diag = std::ceil(std::hypot(edges.w, edges.h));  // 정수로 올림: rho 인덱스가 정확히 대칭이 됨
    acc.nTheta = (int)std::round(180.0 / thetaResDeg);
    acc.nRho = (int)std::ceil(2 * acc.diag / rhoRes) + 1;
    acc.v.assign((size_t)acc.nRho * acc.nTheta, 0);

    // sin/cos 를 미리 계산해 두어 에지 픽셀마다 삼각함수를 다시 계산하지 않는다
    std::vector<double> cosT(acc.nTheta), sinT(acc.nTheta);
    for (int t = 0; t < acc.nTheta; ++t) {
        cosT[t] = std::cos(t * acc.thetaRes);
        sinT[t] = std::sin(t * acc.thetaRes);
    }

    // 각 에지 픽셀 (x, y) 에 대해 모든 theta 에서 rho 를 계산해 투표
    for (int y = 0; y < edges.h; ++y)
        for (int x = 0; x < edges.w; ++x) {
            if (edges.at(x, y) == 0) continue;
            for (int t = 0; t < acc.nTheta; ++t) {
                double rho = x * cosT[t] + y * sinT[t];
                int r = (int)std::round((rho + acc.diag) / rhoRes);
                acc.at(r, t)++;
            }
        }
    return acc;
}

// 피크 검출: 임계값 이상이면서 (2*win+1)^2 이웃 안에서 최대인 셀만 직선으로 채택
static std::vector<Line> findPeaks(const Accumulator& acc, int threshold, int win, int maxLines) {
    std::vector<Line> lines;
    for (int r = 0; r < acc.nRho; ++r)
        for (int t = 0; t < acc.nTheta; ++t) {
            int v = acc.at(r, t);
            if (v < threshold) continue;
            bool isMax = true;
            for (int dr = -win; dr <= win && isMax; ++dr)
                for (int dt = -win; dt <= win; ++dt) {
                    int rr = r + dr, tt = t + dt;
                    if (rr < 0 || rr >= acc.nRho) continue;
                    // theta 는 0 과 180 이 이어져 있다: (rho, theta+180) == (-rho, theta)
                    if (tt < 0)            { tt += acc.nTheta; rr = acc.nRho - 1 - rr; }
                    else if (tt >= acc.nTheta) { tt -= acc.nTheta; rr = acc.nRho - 1 - rr; }
                    int nv = acc.at(rr, tt);
                    // 동점일 때 하나만 남기도록 인덱스가 앞선 쪽을 우선
                    if (nv > v || (nv == v && (rr * acc.nTheta + tt) < (r * acc.nTheta + t))) {
                        isMax = false;
                        break;
                    }
                }
            if (isMax) lines.push_back({r * acc.rhoRes - acc.diag, t * acc.thetaRes, v});
        }
    std::sort(lines.begin(), lines.end(), [](const Line& a, const Line& b) { return a.votes > b.votes; });
    if ((int)lines.size() > maxLines) lines.resize(maxLines);
    return lines;
}

// ---------------------------------------------------------------- 출력

// Bresenham 알고리즘으로 선분을 그림 (영상 밖 픽셀은 Rgb::set 에서 무시)
static void drawSegment(Rgb& img, int x0, int y0, int x1, int y1, int thick) {
    int dx = std::abs(x1 - x0), dy = -std::abs(y1 - y0);
    int sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
    int err = dx + dy;
    while (true) {
        for (int ty = -thick / 2; ty <= thick / 2; ++ty)
            for (int tx = -thick / 2; tx <= thick / 2; ++tx) img.set(x0 + tx, y0 + ty, 255, 0, 0);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}

// (rho, theta) 직선을 영상 전체에 걸쳐 그림.
// 직선 위의 기준점 (rho*cos, rho*sin) 에서 방향벡터 (-sin, cos) 로 ±대각선 길이만큼 연장
static void drawLine(Rgb& img, const Line& l, double diag) {
    double c = std::cos(l.theta), s = std::sin(l.theta);
    double x0 = l.rho * c, y0 = l.rho * s;
    drawSegment(img,
                (int)std::lround(x0 - diag * s), (int)std::lround(y0 + diag * c),
                (int)std::lround(x0 + diag * s), (int)std::lround(y0 - diag * c), 2);
}

static void saveGray(const std::string& path, const Gray& g) {
    std::vector<unsigned char> buf(g.px.size());
    for (size_t i = 0; i < buf.size(); ++i) buf[i] = (unsigned char)std::clamp(g.px[i], 0.f, 255.f);
    stbi_write_png(path.c_str(), g.w, g.h, 1, buf.data(), g.w);
}

// 누적 배열 시각화: 가로축 theta(0~180도), 세로축 rho(-D~D).
// 약한 투표도 보이도록 제곱근 스케일로 정규화한다.
static void saveAccumulator(const std::string& path, const Accumulator& acc, const std::vector<Line>& lines) {
    const int sx = 3;  // theta 축이 180칸뿐이라 가로로 3배 확대
    int w = acc.nTheta * sx, h = acc.nRho;
    int maxV = *std::max_element(acc.v.begin(), acc.v.end());
    Rgb img{w, h, std::vector<unsigned char>((size_t)w * h * 3)};
    for (int r = 0; r < h; ++r)
        for (int x = 0; x < w; ++x) {
            auto v = (unsigned char)(255.0 * std::sqrt((double)acc.at(r, x / sx) / maxV));
            img.set(x, r, v, v, v);
        }
    // 검출된 피크 위치를 빨간 사각형으로 표시
    for (const Line& l : lines) {
        int cx = (int)std::lround(l.theta / acc.thetaRes) * sx + sx / 2;
        int cy = (int)std::lround((l.rho + acc.diag) / acc.rhoRes);
        for (int d = -8; d <= 8; ++d)
            for (int k = 6; k <= 8; ++k) {
                img.set(cx + d, cy - k, 255, 0, 0); img.set(cx + d, cy + k, 255, 0, 0);
                img.set(cx - k, cy + d, 255, 0, 0); img.set(cx + k, cy + d, 255, 0, 0);
            }
    }
    stbi_write_png(path.c_str(), w, h, 3, img.px.data(), w * 3);
}

// ---------------------------------------------------------------- main

int main(int argc, char** argv) {
    if (argc < 2) {
        std::printf("usage: %s <image> [out_prefix] [vote_threshold] [max_lines]\n", argv[0]);
        return 1;
    }
    std::string inPath = argv[1];
    std::string prefix = argc > 2 ? argv[2] : "out";
    double thArg = argc > 3 ? std::atof(argv[3]) : 0.5;
    int maxLines = argc > 4 ? std::atoi(argv[4]) : 30;

    int w, h, ch;
    unsigned char* data = stbi_load(inPath.c_str(), &w, &h, &ch, 3);
    if (!data) {
        std::printf("failed to load %s\n", inPath.c_str());
        return 1;
    }
    std::printf("input: %s (%dx%d)\n", inPath.c_str(), w, h);

    // 1) 그레이스케일 변환
    Gray gray = toGray(data, w, h, 3);

    // 2) Canny 에지 검출 (sigma=1.4, low=0.1*max, high=0.25*max)
    Gray edges = canny(gray, 1.4, 0.10f, 0.25f);
    long edgeCount = std::count(edges.px.begin(), edges.px.end(), 255.f);
    std::printf("edge pixels: %ld\n", edgeCount);

    // 3) Hough 변환 (rho 해상도 1px, theta 해상도 1도)
    Accumulator acc = houghTransform(edges, 1.0, 1.0);
    int maxVote = *std::max_element(acc.v.begin(), acc.v.end());
    int threshold = thArg < 1.0 ? (int)(thArg * maxVote) : (int)thArg;
    std::printf("accumulator: %d(rho) x %d(theta), max vote = %d, threshold = %d\n",
                acc.nRho, acc.nTheta, maxVote, threshold);

    // 4) 피크 검출 -> 직선
    std::vector<Line> lines = findPeaks(acc, threshold, 10, maxLines);
    std::printf("detected lines: %zu\n", lines.size());
    for (size_t i = 0; i < lines.size(); ++i)
        std::printf("  #%2zu rho=%7.1f theta=%6.1f deg votes=%d\n",
                    i + 1, lines[i].rho, lines[i].theta * 180 / PI, lines[i].votes);

    // 5) 결과 저장
    Rgb result{w, h, std::vector<unsigned char>(data, data + (size_t)w * h * 3)};
    for (const Line& l : lines) drawLine(result, l, acc.diag);
    stbi_image_free(data);

    saveGray(prefix + "_1_gray.png", gray);
    saveGray(prefix + "_2_edges.png", edges);
    saveAccumulator(prefix + "_3_accumulator.png", acc, lines);
    stbi_write_png((prefix + "_4_lines.png").c_str(), w, h, 3, result.px.data(), w * 3);
    std::printf("saved: %s_{1_gray,2_edges,3_accumulator,4_lines}.png\n", prefix.c_str());
    return 0;
}
