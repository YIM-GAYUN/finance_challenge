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
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
    allow_origins=["*"],  # 모든 도메인 허용 (필요에 따라 제한 가능)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        quotes = _search_finnhub_candidates(s)
        print(f"Quotes for {s}: {quotes}")  # Finnhub API 검색 결과 출력
        ranked = _rank_kr_candidates(s, quotes)
        print(f"Ranked candidates for {s}: {ranked}")
        if not ranked:
            raise HTTPException(status_code=404, detail=f"검색 결과가 없습니다: {user_input}")

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
# 2) 지표 수집 (Finnhub /stock/metric)
#    GET /stock/metric?symbol=...&metric=all&token=...
#    주요 필드: peTTM, pbRatioTTM, roeTTM 등 (없을 경우 대체 키도 시도)
# =========================================================
def get_metrics_from_finnhub(ticker: str):
    try:
        r = requests.get(
            f"{FINNHUB}/stock/metric",
            params={"symbol": ticker, "metric": "all", "token": FINNHUB_API_KEY},
            timeout=10
        )
        if not r.ok:
            print("metric call failed:", r.status_code, r.text[:200])
            return None, None, None
        metric = (r.json() or {}).get("metric", {}) or {}
        print(f"Full metric response for {ticker}: {r.json()}")  # 전체 응답 출력

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
            _to_float(metric.get("priceToBookMRQ"))
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
# 3) RPG 분류 & GPT 요약 (기존 로직 재사용)
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
[3문장 요약]
- 회사명: {company}
- ROE(%): {roe}
- PER(x): {per}
- PBR(x): {pbr}
규칙: 정확히 3문장. 1) 현재 상태 2) 시사점 3) 주의/리스크.

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

        resp = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": user_prompt}]
        )
        return resp.output_parsed
    except Exception as e:
        print(f"Error in gpt_generate: {e}")
        return {
            "summary3": ["OpenAI API 호출 실패"],
            "insights": {"caution": "OpenAI API 호출 실패", "positive": "OpenAI API 호출 실패"}
        }

# =========================================================
# 4) 엔드포인트
#    - /api/analyze_by_name?name=삼성전자
#    - /api/analyze?ticker=005930.KS
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