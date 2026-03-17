import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import time
from urllib.parse import urlencode

'''
문제1] 웹스크래핑을 통한 데이터 수집 
 - 수집항목 : 기사 제목, 날짜, 언론사명, 요약문(있는 경우)
 - 네이버 뉴스는 무한 스크롤(프론트)이나, SSR 페이지(where=news, start=1/11/21...)로
   자바스크립트 없이도 페이징 수집이 가능함.
'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Referer':'https://search.naver.com/'
}

# (A) 상세 기사 파서
def get_news(URL):
    res = requests.get(URL, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 1. 제목
    title_el = soup.select_one("h2#title_area span") or soup.select_one("h2.media_end_head_headline")
    title = title_el.text.strip() if title_el else "No Title Found"

    # 2. 날짜
    date_el = (soup.select_one("span.media_end_head_info_datestamp_time")
               or soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
               or soup.select_one("span#newsct_article_date"))
    date_text = date_el.text.strip() if date_el else "No Date Found"

    # 3. 언론사
    media_el = (soup.select_one("a.media_end_head_top_logo img")
                or soup.select_one("img.media_end_head_top_logo_img"))
    media = (media_el['alt'].strip() if (media_el and media_el.has_attr('alt')) else "No Media Found")

    # 4. 본문
    content_el = soup.select_one("div#newsct_article") or soup.select_one("div#dic_area")
    if content_el:
        content = re.sub(r"\s+", " ", content_el.get_text(" ", strip=True))
    else:
        content = "No Content Found"

    print(f'수집완료 : {title} ({URL})')
    print(f'언론사: {media}')
    print(f'날짜: {date_text}')
    return (title, date_text, media, content)

# (B) SSR 뉴스 리스트 페이지 URL 빌더 (자바스크립트 없이 페이징 가능)
def build_news_list_url(keyword: str, day_str: str, start: int = 1):
    """
    day_str: 'YYYY.MM.DD'
    start: 1, 11, 21 ... (10개 단위)
    """
    day_compact = re.sub(r"[^\d]", "", day_str)  # '2025.10.01' -> '20251001'
    params = {
        "where": "news",
        "sm": "tab_pge",
        "query": keyword,
        "nso": f"so:r,p:from{day_compact}to{day_compact}",
        "ds": day_str,
        "de": day_str,
        "start": start
    }
    return "https://search.naver.com/search.naver?" + urlencode(params, safe=":,")

# (C) 특정 날짜에서 최대 100건까지 카드 추출(제목/링크/언론사/날짜/요약문)
def fetch_cards_one_day(keyword: str, day_str: str, limit_per_day: int = 100, delay: float = 0.4):
    collected = []
    start = 1  # 1, 11, 21 ...
    while len(collected) < limit_per_day:
        url = build_news_list_url(keyword, day_str, start=start)
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        wraps = soup.select("div.news_wrap.api_ani_send")
        if not wraps:
            break

        for w in wraps:
            a = w.select_one("a.news_tit")
            if not a:
                continue
            title = a.get("title") or a.get_text(strip=True)
            link = a.get("href")

            # 네이버 뉴스 본문 링크만 선별 (모바일/데스크톱 모두 허용)
            if ("n.news.naver.com" not in link) and ("news.naver.com" not in link):
                continue

            press, date_text, summary = "", "", ""
            info_group = w.select_one(".info_group")
            if info_group:
                for info in info_group.select(".info, a.info"):
                    t = info.get_text(strip=True)
                    if info.name == "a" and not press:
                        press = t
                    if any(x in t for x in ["분 전","시간 전","일 전","어제","오늘",".","전"]) and not date_text:
                        date_text = t

            dsc = w.select_one(".news_dsc .dsc_txt") or w.select_one(".news_dsc")
            if dsc:
                summary = dsc.get_text(" ", strip=True)

            collected.append({
                "title": title, "url": link, "press": press,
                "date_text": date_text, "summary": summary
            })

        start += 10
        time.sleep(delay)

    # 중복 제거 + limit 자르기
    df = pd.DataFrame(collected).drop_duplicates(subset=["url"]).reset_index(drop=True)
    if len(df) > limit_per_day:
        df = df.iloc[:limit_per_day].copy()
    return df

# (D) 날짜 범위 루프 + 상세기사 파싱(제목/날짜/언론사/본문)
def get_news_list(keyword, from_date, to_date, per_day=100):
    all_rows = []
    for d in pd.date_range(start=from_date, end=to_date, freq="D"):  # 오름차순
        day = d.strftime("%Y.%m.%d")
        print(f"\n--- {day} 날짜의 뉴스 수집 시작 ---")
        df_cards = fetch_cards_one_day(keyword, day, limit_per_day=per_day)

        # 상세 기사까지 파싱(요약문 필요하면 df_cards로 함께 저장해도 됨)
        for _, row in df_cards.iterrows():
            title, date_text, media, content = get_news(row["url"])
            all_rows.append((title, date_text, media, content))

        print(f"{day} 수집 완료: {len(df_cards)}건")

    return pd.DataFrame(all_rows, columns=['title','date','media','content'])


# ---------------- 사용 예시 ----------------
if __name__ == "__main__":
    keyword   = "양자컴퓨팅"
    from_date = "2025.10.01"
    to_date   = "2025.10.08"

    rows = get_news_list(keyword, from_date, to_date, per_day=100)

    out_path = 'D:/knou/PythonDataProcessing/Midterm/webscraping_2510.csv'
    rows.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\nCSV 저장 완료 (총 {len(rows)}건)")
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import time
from urllib.parse import urlencode

'''
문제1] 웹스크래핑을 통한 데이터 수집 
 - 수집항목 : 기사 제목, 날짜, 언론사명, 요약문(있는 경우)
 - 네이버 뉴스는 무한 스크롤(프론트)이나, SSR 페이지(where=news, start=1/11/21...)로
   자바스크립트 없이도 페이징 수집이 가능함.
'''

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Referer':'https://search.naver.com/'
}

# (A) 상세 기사 파서
def get_news(URL):
    res = requests.get(URL, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 1. 제목
    title_el = soup.select_one("h2#title_area span") or soup.select_one("h2.media_end_head_headline")
    title = title_el.text.strip() if title_el else "No Title Found"

    # 2. 날짜
    date_el = (soup.select_one("span.media_end_head_info_datestamp_time")
               or soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
               or soup.select_one("span#newsct_article_date"))
    date_text = date_el.text.strip() if date_el else "No Date Found"

    # 3. 언론사
    media_el = (soup.select_one("a.media_end_head_top_logo img")
                or soup.select_one("img.media_end_head_top_logo_img"))
    media = (media_el['alt'].strip() if (media_el and media_el.has_attr('alt')) else "No Media Found")

    # 4. 본문
    content_el = soup.select_one("div#newsct_article") or soup.select_one("div#dic_area")
    if content_el:
        content = re.sub(r"\s+", " ", content_el.get_text(" ", strip=True))
    else:
        content = "No Content Found"

    print(f'수집완료 : {title} ({URL})')
    print(f'언론사: {media}')
    print(f'날짜: {date_text}')
    return (title, date_text, media, content)

# (B) SSR 뉴스 리스트 페이지 URL 빌더 (자바스크립트 없이 페이징 가능)
def build_news_list_url(keyword: str, day_str: str, start: int = 1):
    """
    day_str: 'YYYY.MM.DD'
    start: 1, 11, 21 ... (10개 단위)
    """
    day_compact = re.sub(r"[^\d]", "", day_str)  # '2025.10.01' -> '20251001'
    params = {
        "where": "news",
        "sm": "tab_pge",
        "query": keyword,
        "nso": f"so:r,p:from{day_compact}to{day_compact}",
        "ds": day_str,
        "de": day_str,
        "start": start
    }
    return "https://search.naver.com/search.naver?" + urlencode(params, safe=":,")

# (C) 특정 날짜에서 최대 100건까지 카드 추출(제목/링크/언론사/날짜/요약문)
def fetch_cards_one_day(keyword: str, day_str: str, limit_per_day: int = 100, delay: float = 0.4):
    collected = []
    start = 1  # 1, 11, 21 ...
    while len(collected) < limit_per_day:
        url = build_news_list_url(keyword, day_str, start=start)
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        wraps = soup.select("div.news_wrap.api_ani_send")
        if not wraps:
            break

        for w in wraps:
            a = w.select_one("a.news_tit")
            if not a:
                continue
            title = a.get("title") or a.get_text(strip=True)
            link = a.get("href")

            # 네이버 뉴스 본문 링크만 선별 (모바일/데스크톱 모두 허용)
            if ("n.news.naver.com" not in link) and ("news.naver.com" not in link):
                continue

            press, date_text, summary = "", "", ""
            info_group = w.select_one(".info_group")
            if info_group:
                for info in info_group.select(".info, a.info"):
                    t = info.get_text(strip=True)
                    if info.name == "a" and not press:
                        press = t
                    if any(x in t for x in ["분 전","시간 전","일 전","어제","오늘",".","전"]) and not date_text:
                        date_text = t

            dsc = w.select_one(".news_dsc .dsc_txt") or w.select_one(".news_dsc")
            if dsc:
                summary = dsc.get_text(" ", strip=True)

            collected.append({
                "title": title, "url": link, "press": press,
                "date_text": date_text, "summary": summary
            })

        start += 10
        time.sleep(delay)

    # 중복 제거 + limit 자르기
    df = pd.DataFrame(collected).drop_duplicates(subset=["url"]).reset_index(drop=True)
    if len(df) > limit_per_day:
        df = df.iloc[:limit_per_day].copy()
    return df

# (D) 날짜 범위 루프 + 상세기사 파싱(제목/날짜/언론사/본문)
def get_news_list(keyword, from_date, to_date, per_day=100):
    all_rows = []
    for d in pd.date_range(start=from_date, end=to_date, freq="D"):  # 오름차순
        day = d.strftime("%Y.%m.%d")
        print(f"\n--- {day} 날짜의 뉴스 수집 시작 ---")
        df_cards = fetch_cards_one_day(keyword, day, limit_per_day=per_day)

        # 상세 기사까지 파싱(요약문 필요하면 df_cards로 함께 저장해도 됨)
        for _, row in df_cards.iterrows():
            title, date_text, media, content = get_news(row["url"])
            all_rows.append((title, date_text, media, content))

        print(f"{day} 수집 완료: {len(df_cards)}건")

    return pd.DataFrame(all_rows, columns=['title','date','media','content'])


# ---------------- 사용 예시 ----------------
if __name__ == "__main__":
    keyword   = "양자컴퓨팅"
    from_date = "2025.10.01"
    to_date   = "2025.10.08"

    rows = get_news_list(keyword, from_date, to_date, per_day=100)

    out_path = 'D:/knou/PythonDataProcessing/Midterm/webscraping_25101.csv'
    rows.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"\nCSV 저장 완료 (총 {len(rows)}건)")
