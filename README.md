# Finance Challenge Project

## 프로젝트 개요
이 프로젝트는 React 기반의 프론트엔드와 Python FastAPI 기반의 백엔드로 구성된 금융 데이터 분석 및 시각화 도구입니다. 사용자는 검색 바를 통해 데이터를 검색하고, RPG 분류 및 AI 기반 투자 전략 생성 기능을 활용할 수 있습니다. OpenAI GPT-4와 Finnhub API를 활용하여 실시간 데이터를 분석하고, 투자 전략 및 요약 정보를 제공합니다.

## 프로젝트 결과물
https://youtu.be/n8fnSXLbsSY
<iframe width="560" height="315" src="https://www.youtube.com/embed/n8fnSXLbsSY" frameborder="0" allowfullscreen></iframe>

---

## 프로젝트 구조
```
finance_challenge/
├── backend/                # 백엔드 디렉토리
│   └── app.py             # FastAPI 애플리케이션
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
### 1. 레이아웃 및 스타일링
- **검색 페이지**: 로딩 인디케이터와 검색 결과를 추가하여 사용자 경험 개선.
- **소개 페이지**: 텍스트와 이미지를 적절히 배치하여 가독성 향상.
- **캐릭터 소개 페이지**: 2행 3열 레이아웃으로 캐릭터 정보를 정렬하고, 이름과 설명을 이미지 오른쪽에 배치.

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

