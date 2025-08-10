from fastapi import FastAPI, Query
import os, requests, datetime
from openai import OpenAI

FINNHUB = "https://finnhub.io/api/v1"
FMP = "https://financialmodelingprep.com/api/v3"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# --- 1) 지표 수집 ---
def get_per_pbr_from_finnhub(ticker: str):
    r = requests.get(f"{FINNHUB}/stock/metric",
                     params={"symbol": ticker, "metric": "valuation",
                             "token": os.getenv("FINNHUB_API_KEY")})
    data = r.json().get("metric", {}) if r.ok else {}
    per = data.get("peTTM") or data.get("peBasicExclExtraTTM") or data.get("peAnnual")
    pbr = data.get("pbRatioTTM") or data.get("pbAnnual") or data.get("priceToBookAnnual")
    return (float(per) if per else None, float(pbr) if pbr else None)

def get_roe_from_fmp(ticker: str):
    r = requests.get(f"{FMP}/ratios/{ticker}", params={"apikey": os.getenv("FMP_API_KEY")})
    if not r.ok: return None
    for row in r.json():
        v = row.get("returnOnEquity")
        if v is not None:
            return float(v)*100 if v < 1 else float(v)  # 일부 소스는 소수(0.12)로 제공
    return None

# --- 2) RPG 분류 ---
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

# --- 3) GPT 호출(Responses API + Structured Outputs) ---
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
    # Responses API call with structured outputs
    resp = client.responses.create(
        model="gpt-4o-mini",  # 성능/비용 균형. 필요 시 상위 모델로 교체
        input=[{"role":"user","content":user_prompt}],
        response_format={ "type":"json_schema", "json_schema": { "name":"RPGSummary", "schema": SUMMARY_SCHEMA } }
    )
    parsed = resp.output_parsed  # -> dict: {"summary3":[...], "insights":{"caution":"...","positive":"..."}}
    return parsed

# --- 4) 엔드포인트 ---
@app.get("/api/analyze")
def analyze(ticker: str, company: str = None):
    per, pbr = get_per_pbr_from_finnhub(ticker)
    roe = get_roe_from_fmp(ticker)
    title, job, temper, desc = classify_rpg(roe, per, pbr)

    gpt = gpt_generate(company or ticker, roe, per, pbr, title, desc)

    return {
        "company": company or ticker,
        "ticker": ticker,
        "roe": roe, "per": per, "pbr": pbr,
        "rpg": {"title": title, "job": job, "temper": temper, "description": desc},
        "summary3": gpt["summary3"],
        "insights": {
            "caution": gpt["insights"]["caution"],
            "positive": gpt["insights"]["positive"]
        },
        "source": {
            "primary": "Finnhub", "backup": ["FMP","OpenDART"],
            "as_of": datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        }
    }
