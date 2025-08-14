import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

from fastapi import FastAPI, HTTPException, Query
import os, datetime, math, re, requests, time
from typing import Optional, List, Dict, Any
from functools import lru_cache
from cachetools import TTLCache, cached
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import numpy as np
import json
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from bs4 import BeautifulSoup

# -----------------------------
# 환경변수
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise RuntimeError("FINNHUB_API_KEY 가 .env 에 설정되어야 합니다.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# -----------------------------
# 상수
# -----------------------------
FINNHUB = "https://finnhub.io/api/v1"

app = FastAPI(title="KR Stock Analyzer with Finnhub")
print(f"Loaded OpenAI API Key: {bool(OPENAI_API_KEY)}")
print(f"Loaded Finnhub API Key: {bool(FINNHUB_API_KEY)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",  # 로컬 개발 환경
        "http://localhost:5173",  # 로컬 개발 환경
        "https://finance-challenge-two.vercel.app",  # Vercel 배포 URL
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================================================
# 0) 공통 유틸
# =========================================================
def _to_float(x):
    try:
        if x is None: return None
        if isinstance(x, float) and math.isnan(x): return None
        return float(x)
    except Exception:
        return None

def _looks_like_kr_code(s: str) -> bool:
    """6자리 한국 종목코드 형태인지"""
    return bool(re.fullmatch(r"\d{6}", s.strip()))

# =========================================================
# 1) 이름 → 티커 변환 (Finnhub 검색 API)
#    GET /search?q=...&token=...
# =========================================================
cache = TTLCache(maxsize=128, ttl=3600)  # 1시간 캐시

@cached(cache)
def _search_finnhub_candidates(query: str) -> List[Dict[str, Any]]:
    try:
        query = query.strip()  # 앞뒤 공백 제거
        query = re.sub(r'[^\w\s]', '', query)  # 특수 문자 제거
        query = ' '.join(query.split())  # 중복 공백 제거

        r = requests.get(
            f"{FINNHUB}/search",
            params={"q": query, "token": FINNHUB_API_KEY},
            timeout=10
        )
        r.raise_for_status()
        data = r.json() or {}
        print(f"Search results for query '{query}': {data}")  # 검색 결과 출력
        return data.get("result", []) or []
    except Exception as e:
        print(f"Error in _search_finnhub_candidates: {e}")
        return []

def _rank_kr_candidates(q: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """KRX(.KS/.KQ) 또는 글로벌 종목을 포함하여 간단 점수로 정렬"""
    try:
        q_norm = q.strip().lower()
        # 모든 종목 포함
        candidates = [
            x for x in items if isinstance(x.get("symbol", ""), str)
        ]

        def score(x):
            sym = x.get("symbol", "")
            desc = (x.get("description") or "").lower()
            # 이름 매칭 점수
            name_hit = 0
            if q_norm in desc: name_hit += 2
            if q_norm == desc: name_hit += 2
            # 거래소 우선순위 (KRX > NASDAQ/NYSE > 기타)
            exch_boost = 0.3 if sym.endswith(".KS") or sym.endswith(".KQ") else (
                0.2 if sym in ["TSLA", "AAPL", "GOOGL"] else 0.0
            )
            # 기본 점수
            base = 1.0
            return base + name_hit + exch_boost

        return sorted(candidates, key=score, reverse=True)
    except Exception as e:
        print(f"Error in _rank_kr_candidates: {e}")
        return []

def resolve_kr_ticker(user_input: str) -> Dict[str, str]:
    try:
        s = user_input.strip()

        # 한국어 종목명일 경우 GPT를 사용하여 영어로 변환
        if re.search(r"[가-힣]", s):  # 한국어 문자가 포함된 경우
            print(f"Detected Korean name: {s}. Translating to English using GPT.")
            s = translate_kor_to_eng_with_gpt(s)

        print(f"Final query for Finnhub API: '{s}'")  # Finnhub API에 전달될 쿼리 출력
        quotes = _search_finnhub_candidates(s)
        print(f"Quotes for {s}: {quotes}")  # Finnhub API 검색 결과 출력
        ranked = _rank_kr_candidates(s, quotes)
        print(f"Ranked candidates for {s}: {ranked}")
        if not ranked:
            raise HTTPException(status_code=404, detail=f"검색 결과가 없습니다: {user_input}. 더 자세한 종목명을 입력해주세요.")

        top = ranked[0]
        return {
            "symbol": top["symbol"],
            "name": top.get("description") or top["symbol"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in resolve_kr_ticker: {e}")
        raise HTTPException(status_code=500, detail="티커 변환 중 오류가 발생했습니다.")

# =========================================================
# 2) 지표 수집 (Finnhub /stock/metric + 네이버 금융 크롤링)
# =========================================================
def get_metrics_from_finnhub(ticker: str):
    try:
        # 티커가 .KS 또는 .KQ로 끝날 경우 Finnhub를 건너뛰고 네이버 금융 크롤링 시도
        if ticker.endswith(".KS") or ticker.endswith(".KQ"):
            kr_ticker = ticker.split(".")[0]  # 접미사 제거 (숫자 6자리만 남김)
            print(f"Ticker '{ticker}' detected as KR code. Using Naver Finance directly with ticker: {kr_ticker}")
            return get_metrics_from_naver_finance(kr_ticker)

        # Finnhub API 호출
        r = requests.get(
            f"{FINNHUB}/stock/metric",
            params={"symbol": ticker, "metric": "all", "token": FINNHUB_API_KEY},
            timeout=10
        )
        if not r.ok:
            print("Finnhub metric call failed:", r.status_code, r.text[:200])
            return None, None, None
        metric = (r.json() or {}).get("metric", {}) or {}

        # PER
        per = (
            _to_float(metric.get("peTTM")) or
            _to_float(metric.get("peBasicExclExtraTTM")) or
            _to_float(metric.get("peAnnual")) or
            _to_float(metric.get("priceToEarningsTTM"))
        )

        # PBR
        pbr = (
            _to_float(metric.get("pbRatioTTM")) or
            _to_float(metric.get("priceToBookAnnual")) or
            _to_float(metric.get("priceToBookMRQ")) or
            _to_float(metric.get("pbTTM")) or
            _to_float(metric.get("pbAnnual"))
        )
        # PBR 계산 추가
        if pbr is None:
            price = _to_float(metric.get("currentPrice"))
            bvps = _to_float(metric.get("bookValuePerShare"))
            if price is not None and bvps is not None:
                pbr = price / bvps
                print(f"Calculated PBR for {ticker}: {pbr}")
            else:
                print(f"PBR data is missing and cannot be calculated for {ticker}")

        # ROE(%)
        roe = (
            _to_float(metric.get("roeTTM")) or
            _to_float(metric.get("returnOnEquityTTM")) or
            _to_float(metric.get("roeAnnual"))
        )
        # roe가 소수(0.12)로 올 수도 있어 보정
        if roe is not None and roe < 1.0:
            roe = roe * 100.0

        return per, pbr, roe
    except Exception as e:
        print(f"Error in get_metrics_from_finnhub: {e}")
        return None, None, None

# =========================================================
# 네이버 금융 크롤링
# =========================================================
import re, time, json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

NAVER_JSON_URL = "https://api.finance.naver.com/service/itemSummary.nhn"
NAVER_HTML_URL = "https://finance.naver.com/item/main.naver?code={itemcode}"

def _extract_itemcode(ticker_or_code: str | None) -> str | None:
    if not ticker_or_code:
        return None
    m = re.search(r'(\d{6})', str(ticker_or_code))
    return m.group(1) if m else None

def _to_float_safe(s):
    """쉼표·단위(원, 배 등) 포함 문자열에서도 숫자만 추출하여 float 변환"""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        try:
            import math
            if isinstance(s, float) and math.isnan(s):
                return None
        except Exception:
            pass
        return float(s)

    s = str(s).strip()
    if s in {"", "-", "N/A", "NaN"}:
        return None

    # 일반적인 제거 후에도 남는 단위가 있을 수 있으므로 최종적으로 숫자 패턴을 추출
    s = s.replace(",", "").replace("%", "")
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    return float(m.group(0)) if m else None

def _session_with_retries():
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,  # 0.5s, 1s, 2s ...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

def get_metrics_from_naver_finance(ticker_or_code: str):
    itemcode = _extract_itemcode(ticker_or_code)
    if not itemcode:
        return None, None, None

    sess = _session_with_retries()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": NAVER_HTML_URL.format(itemcode=itemcode),
        "Connection": "keep-alive",
    }

    per = pbr = roe = eps = bps = None

    # 1) JSON 엔드포인트 시도
    try:
        r = sess.get(NAVER_JSON_URL, headers=headers, params={"itemcode": itemcode}, timeout=5)
        if not r.content:
            time.sleep(0.4)
            r = sess.get(NAVER_JSON_URL, headers=headers, params={"itemcode": itemcode}, timeout=5)

        if not r.content:
            raise ValueError("Empty body from Naver JSON")

        js = r.json()
        per = _to_float_safe(js.get("per"))
        pbr = _to_float_safe(js.get("pbr"))
        roe = _to_float_safe(js.get("roe"))
        eps = _to_float_safe(js.get("eps"))
        bps = _to_float_safe(js.get("bps"))  # JSON에 bps가 있으면 1순위로 사용
        print(f"JSON Response: {js}")
    except Exception as e:
        print(f"[naver itemSummary error] {e} (itemcode={itemcode})")

    # 2) HTML 폴백 (부족한 값만 채움)
    if per is None or pbr is None or roe is None or eps is None or bps is None:
        try:
            html_headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            url = NAVER_HTML_URL.format(itemcode=itemcode)
            res = sess.get(url, headers=html_headers, timeout=6)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            # id 기반(있으면 가장 신뢰)
            if per is None:
                node = soup.select_one("#_per")
                per = _to_float_safe(node.get_text(strip=True)) if node else per
            if pbr is None:
                node = soup.select_one("#_pbr") or soup.select_one("#pbr")  # 언더스코어/무언더스코어 둘 다 대응
                pbr = _to_float_safe(node.get_text(strip=True)) if node else pbr
            if roe is None:
                node = soup.select_one("#_roe")
                roe = _to_float_safe(node.get_text(strip=True)) if node else roe
            if eps is None:
                node = soup.select_one("#_eps")
                eps = _to_float_safe(node.get_text(strip=True)) if node else eps

            # BPS: 너가 확인한 구조 - <em id="pbr">PBR</em> 바로 다음 <em>이 BPS(원 단위)
            if bps is None:
                em_pbr = soup.select_one("em#_pbr") or soup.select_one("em#pbr")
                if em_pbr:
                    # 같은 <td> 안의 두 번째 em을 우선 시도
                    td = em_pbr.find_parent("td")
                    ems = td.find_all("em") if td else []
                    if len(ems) >= 2:
                        bps = _to_float_safe(ems[1].get_text(strip=True))
                    # 보조: 문서 순서상 다음 em 하나만 집는다
                    if bps is None:
                        nxt = em_pbr.find_next("em")
                        if nxt and nxt is not em_pbr:
                            bps = _to_float_safe(nxt.get_text(strip=True))

            # 최후 보강: 표 헤더가 'BPS'인 셀을 찾아 오른쪽(td) 값
            if bps is None:
                th_bps = soup.find(["th", "dt"], string=re.compile(r"\bBPS\b", re.I))
                if th_bps:
                    td_bps = th_bps.find_next("td") or (th_bps.parent.find_next("td") if th_bps.parent else None)
                    if td_bps:
                        bps = _to_float_safe(td_bps.get_text(" ", strip=True))

            # 마지막 보조: '원'이 포함된 em 주변에서 숫자만 추출
            if bps is None:
                em_with_won = soup.find("em", string=re.compile(r"원"))
                if em_with_won:
                    candidate = em_with_won.get_text(" ", strip=True)
                    if _to_float_safe(candidate) is None:
                        candidate = (em_with_won.previous_sibling or "") or em_with_won.parent.get_text(" ", strip=True)
                    bps = _to_float_safe(candidate)

        except Exception as e:
            print(f"[naver HTML fallback error] {e} (itemcode={itemcode})")

    # 3) ROE 직접 계산 (eps/bps 모두 있고 bps != 0일 때)
    if roe is None and eps is not None and bps is not None and bps != 0:
        roe = round((eps / bps) * 100, 2)

    print(f"Debug - PER: {per}, PBR: {pbr}, ROE: {roe}, EPS: {eps}, BPS: {bps}")
    return per, pbr, roe

# =========================================================
# 3) RPG 분류 & GPT 요약
# =========================================================
def classify_rpg(roe, per, pbr):
    roe_tag = "High" if (roe is not None and roe >= 10) else "Low"
    per_tag = "Low" if (per is not None and per <= 12) else "High"
    pbr_tag = "Low" if (pbr is not None and pbr <= 1.0) else "High"

    if roe_tag=="High" and pbr_tag=="Low": job = "전사"
    elif roe_tag=="High" and per_tag=="High": job = "마법사"
    else: job = "도적"

    temper = "모험" if (per_tag=="High" and roe_tag=="High") else "수호"
    title = f"{temper} {job}"

    descriptions = {
        "수호 전사": "안정적 수익성과 저평가 매력을 바탕으로 자산을 지키는 타입",
        "모험 전사": "수익성을 무기로 새로운 기회를 추적하는 도전형",
        "수호 마법사": "검증된 기반 위에 분석과 혁신을 결합한 전략가",
        "모험 마법사": "성장성과 기술 혁신을 앞세우는 개척자",
        "수호 도적": "저평가 구간에서 반등을 노리는 잠행형",
        "모험 도적": "높은 변동성을 기회로 삼는 추격형"
    }
    return title, job, temper, descriptions.get(title, "")

SUMMARY_SCHEMA = {
  "type": "object",
  "properties": {
    "summary3": { "type": "array", "items": {"type": "string"}, "minItems":3, "maxItems":3 },
    "insights": {
      "type":"object",
      "properties": { "caution":{"type":"string"}, "positive":{"type":"string"} },
      "required":["caution","positive"]
    }
  },
  "required": ["summary3","insights"],
  "additionalProperties": False
}

def gpt_generate(company, roe, per, pbr, rpg_title, rpg_desc):
    try:
        user_prompt = f"""
[요약]
- 회사명: {company}
- ROE(%): {roe}
- PER(x): {per}
- PBR(x): {pbr}
규칙: 1. 회사명을 기반으로, ROE, PER, PBR을 분석하여 앞으로 이 회사에 어떻게 투자해야할지 조언하는 문장 2~3문장 필수로 출력하기 (investment_advice)
     2. 회사명을 기반으로 해당 회사의 최근 뉴스나 이벤트를 반영하여 투자 전략을 2~3문장으로 필수로 제시하기 (recent_news_strategy)
     3. rpg_title과 rpg_desc를 반영하여 이 회사가 rpg_title로서 어떻게 활동하고있는지 rpg_desc를 풀어서 1~2문장으로 필수로 설명하기 (rpg_title_desc)

[캐릭터 코멘트]
- RPG: {rpg_title}
- 설명: {rpg_desc}
- 위 수치를 반영하여 '주의 1~2문장 / 장점 1~2문장'을 한 줄씩 작성.
출력은 JSON만.
"""
        if client is None:
            return {
                "summary3": [
                    f"{company}의 핵심 지표를 요약했다.",
                    "지표 조합을 통해 투자 시사점을 도출할 수 있다.",
                    "데이터의 공시 지연·결측에 유의해야 한다."
                ],
                "insights": {
                    "caution": "지표는 참고용이며, 공시 지연/결측 가능성이 있다.",
                    "positive": "Finnhub 무료 API로도 빠른 프로토타입이 가능하다."
                }
            }

        # OpenAI API 호출
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.2
        )

        print(f"OpenAI API response: {resp}")

        content = resp.choices[0].message.content  # 문자열(JSON)
        raw_data = json.loads(content)  # dict로 파싱

        # OpenAI 응답 데이터를 summary3와 insights로 매핑
        summary3 = [
            raw_data.get("investment_advice", ""),
            raw_data.get("recent_news_strategy", ""),
            raw_data.get("rpg_title_desc", "")
        ]
        insights = {
            "caution": raw_data.get("caution", ""),
            "positive": raw_data.get("advantage", "")
        }

        return {"summary3": summary3, "insights": insights}

    except Exception as e:
        print(f"Error in gpt_generate: {e}")
        return {
            "summary3": ["OpenAI API 호출 실패"],
            "insights": {
                "caution": "OpenAI API 호출 실패",
                "positive": "오프라인 모드로 계속 진행"
            }
        }

# =========================================================
# 4) 엔드포인트
# =========================================================
@app.get("/api/analyze_by_name")
def analyze_by_name(name: str = Query(..., description="회사명(한글/영문) 또는 6자리 코드")):
    try:
        print(f"Received request for name: {name}")
        resolved = resolve_kr_ticker(name)
        print(f"Resolved ticker: {resolved}")
        symbol = resolved["symbol"]
        display_name = resolved["name"]

        per, pbr, roe = get_metrics_from_finnhub(symbol)
        print(f"Metrics - PER: {per}, PBR: {pbr}, ROE: {roe}")
        title, job, temper, desc = classify_rpg(roe, per, pbr)
        gpt = gpt_generate(display_name, roe, per, pbr, title, desc)

        if all(v is None for v in [roe, per, pbr]):
            raise HTTPException(status_code=502, detail="지표 조회에 실패했습니다. 티커는 확인되었으나 지표 데이터가 부족합니다.")

        response_data = {
            "company": display_name,
            "ticker": symbol,
            "roe": roe, "per": per, "pbr": pbr,
            "rpg": {"title": title, "job": job, "temper": temper, "description": desc},
            "summary3": gpt["summary3"],
            "insights": gpt["insights"],
            "source": {
                "primary": "Finnhub (/search, /stock/metric)",
                "as_of": datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            }
        }
        print(f"Response data: {response_data}")
        return response_data
    except HTTPException as e:
        print(f"HTTPException in analyze_by_name: {e.detail}")
        raise
    except Exception as e:
        print(f"Unhandled exception in analyze_by_name: {e}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다.")

@app.get("/api/analyze")
def analyze(ticker: str, company: Optional[str] = None):
    try:
        per, pbr, roe = get_metrics_from_finnhub(ticker)
        title, job, temper, desc = classify_rpg(roe, per, pbr)
        gpt = gpt_generate(company or ticker, roe, per, pbr, title, desc)

        return {
            "company": company or ticker,
            "ticker": ticker,
            "roe": roe, "per": per, "pbr": pbr,
            "rpg": {"title": title, "job": job, "temper": temper, "description": desc},
            "summary3": gpt["summary3"],
            "insights": gpt["insights"],
            "source": {
                "primary": "Finnhub (/stock/metric)",
                "as_of": datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            }
        }
    except Exception as e:
        print(f"Error in analyze: {e}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the KR Stock Analyzer API. Use /docs for API documentation."}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "Favicon is available at /static/favicon.ico"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    print(f"Unhandled exception: {exc}")
    print("".join(traceback.format_exception(None, exc, exc.__traceback__)))  # 전체 스택 트레이스 출력
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

def translate_kor_to_eng_with_gpt(kor_name: str) -> str:
    """
    GPT를 사용하여 한국어 종목명을 영어 종목명으로 변환 (JSON 형식 강제)
    """
    try:
        if client is None:
            raise RuntimeError("OpenAI API Key가 설정되지 않았습니다.")

        # 프롬프트 수정: JSON 형식 강제
        prompt = f"""
        아래의 한국어 종목명을 영어 종목명으로 변환하세요.
        - 한국어 종목명: "{kor_name}"
        - 영어 종목명만 JSON 형식으로 반환하세요. 최대한 한 단어로만 반환하세요. 여러 단어로만 해야할 경우에는 꼭 띄어쓰기를 지키세요. 다른 설명은 포함하지 마세요.
        - JSON 형식 예시: {{ "english_name": "Samsung" }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        # GPT 응답에서 JSON 파싱
        content = response.choices[0].message.content.strip()
        print(f"GPT raw response: {content}")
        eng_name_json = json.loads(content)  # JSON 파싱
        eng_name = eng_name_json.get("english_name", "").strip()
        if not eng_name:
            raise ValueError("영어 종목명을 찾을 수 없습니다.")
        
        # 특수 문자 제거 및 공백 정리
        eng_name = re.sub(r'[^\w\s]', '', eng_name)  # 특수 문자 제거
        eng_name = ' '.join(eng_name.split())  # 중복 공백 제거
        print(f"Translated '{kor_name}' to '{eng_name}' using GPT.")
        return eng_name
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        raise HTTPException(status_code=500, detail="GPT 응답에서 JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"Error in translate_kor_to_eng_with_gpt: {e}")
        raise HTTPException(status_code=500, detail="종목명 변환 중 오류가 발생했습니다.")
