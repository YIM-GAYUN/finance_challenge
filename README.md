# K-STOCK INSIGHTS: Finance Challenge Project

## 프로젝트 개요
이 프로젝트는 React 기반의 프론트엔드와 Python FastAPI 기반의 백엔드로 구성된 금융 데이터 분석 및 시각화 도구입니다. 사용자는 검색 바를 통해 데이터를 검색하고, RPG 분류 및 AI 기반 투자 전략 생성 기능을 활용할 수 있습니다. OpenAI GPT-4와 Finnhub API 및 네이버 금융 크롤링을 활용하여 실시간 데이터를 분석하고, 투자 전략 및 요약 정보를 제공합니다.

## 프로젝트 결과물
[영상] https://youtu.be/n8fnSXLbsSY<br>
[웹페이지 링크] https://finance-challenge-two.vercel.app/<br><br>

<img width="1919" height="1079" alt="스크린샷 2025-08-13 232059" src="https://github.com/user-attachments/assets/d31fe79e-e54b-49bb-b3b4-109850d8568c" />
<img width="1919" height="1077" alt="스크린샷 2025-08-13 231628" src="https://github.com/user-attachments/assets/7e3fe2c8-19ea-46f7-a7f3-1b0f3c386600" />
<img width="1919" height="1079" alt="스크린샷 2025-08-13 232040" src="https://github.com/user-attachments/assets/e57126a8-f5bc-447a-9dec-789af53f695b" />
<img width="1919" height="1079" alt="스크린샷 2025-08-13 230926" src="https://github.com/user-attachments/assets/bfd688cf-598b-41f4-b3c3-baa4187c9c37" />

---

## 프로젝트 구조
```
finance_challenge/
├── backend/                # 백엔드 디렉토리
│   ├── app.py             # FastAPI 애플리케이션
│   ├── requirements.txt   # Python 의존성 관리 파일
├── frontend/               # 프론트엔드 디렉토리
│   ├── index.html         # HTML 진입점
│   ├── package.json       # Node.js 의존성 관리 파일
│   ├── postcss.config.js  # PostCSS 설정 파일
│   ├── tailwind.config.js # Tailwind CSS 설정 파일
│   ├── vite.config.js     # Vite 설정 파일
│   └── src/               # React 소스 코드
│       ├── App.jsx        # React 메인 컴포넌트
│       ├── index.css      # CSS 파일
│       ├── main.jsx       # React 진입점
│       ├── Search.jsx     # 검색 페이지 컴포넌트
│       ├── Intro.jsx      # 소개 페이지 컴포넌트
│       ├── Character.jsx  # 캐릭터 소개 페이지 컴포넌트
│       └── ...            # 기타 소스 파일
```

---

## 설치 및 실행 방법

### 1. 백엔드 설정
1. Python이 설치되어 있는지 확인합니다.
2. `backend` 디렉토리로 이동합니다:
   ```bash
   cd backend
   ```
3. 필요한 Python 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```
4. FastAPI 서버를 실행합니다:
   ```bash
   uvicorn app:app --reload
   ```
5. 서버가 `http://127.0.0.1:8000`에서 실행됩니다.

### 2. 프론트엔드 설정
1. Node.js가 설치되어 있는지 확인합니다.
2. `frontend` 디렉토리로 이동합니다:
   ```bash
   cd frontend
   ```
3. 필요한 Node.js 패키지를 설치합니다:
   ```bash
   npm install
   ```
4. 개발 서버를 실행합니다:
   ```bash
   npm run dev
   ```
5. 브라우저에서 `http://localhost:5173`에 접속하여 애플리케이션을 확인합니다.

---

## 배포 방식
### 1. 프론트엔드 배포 (Vercel)
- Vercel을 사용하여 프론트엔드를 배포하였습니다.
- 환경 변수(`VITE_API_URL`)를 Vercel 대시보드에서 설정해야 합니다.

### 2. 백엔드 배포 (Render)
- Render를 사용하여 FastAPI 백엔드를 배포하였습니다.
- Render 대시보드에서 환경 변수(`OPENAI_API_KEY`, `FINNHUB_API_KEY`)를 설정해야 합니다.

---

## 환경 변수 관리
### `.env` 파일
- 로컬 개발 환경에서 `.env` 파일을 사용하여 환경 변수를 관리합니다.
  ```properties
  OPENAI_API_KEY=your-openai-api-key
  FINNHUB_API_KEY=your-finnhub-api-key
  VITE_API_URL=http://127.0.0.1:8000  # 로컬 개발용
  ```

### Render 환경 변수
- Render 대시보드에서 다음 환경 변수를 설정합니다:
  - `OPENAI_API_KEY`
  - `FINNHUB_API_KEY`

### Vercel 환경 변수
- Vercel 대시보드에서 다음 환경 변수를 설정합니다:
  - `VITE_API_URL` (Render 백엔드 URL)

---

## 주요 기능
- **검색 페이지**: 사용자가 종목명을 검색하고 관련 데이터를 확인할 수 있는 기능.
- **소개 페이지**: 프로젝트의 개요와 RPG 캐릭터 기반 투자 설명 제공.
- **캐릭터 소개 페이지**: RPG 캐릭터별 이미지와 설명을 제공.
- **RPG 분류**: 데이터를 RPG 기준으로 분류.
- **AI 기반 투자 전략 생성**: OpenAI GPT-4를 활용하여 투자 전략 및 요약 정보를 생성.

---

## 기술 스택
- **프론트엔드**: React, Vite, Tailwind CSS
- **백엔드**: Python FastAPI
- **AI**: OpenAI GPT-4
- **데이터 API**: Finnhub API
- **빌드 도구**: Vite

---

## 문제 해결
### 1. CORS 설정
- FastAPI의 `CORSMiddleware`를 사용하여 로컬 및 배포 환경에서의 CORS 문제를 해결.
- `allow_origins`에 로컬(`http://127.0.0.1:5173`)과 배포된 Vercel URL을 모두 포함.

### 2. API 호출 문제
- `.env` 파일에 API 키를 올바르게 설정하여 OpenAI 및 Finnhub API 호출 문제 해결.

---

## 향후 작업
- **RPG 분류 기능 개선**
- **데이터 시각화 기능 추가**
- **백엔드 API 최적화**
- **프론트엔드와 백엔드 간 데이터 전달 최적화**

---

## 기여 방법
1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다:
   ```bash
   git checkout -b feature/새로운-기능
   ```
3. 변경 사항을 커밋합니다:
   ```bash
   git commit -m "새로운 기능 추가"
   ```
4. 브랜치에 푸시합니다:
   ```bash
   git push origin feature/새로운-기능
   ```
5. Pull Request를 생성합니다.

---

