# Finance Challenge Project

## 프로젝트 개요
이 프로젝트는 React 기반의 프론트엔드와 Python Flask 기반의 백엔드로 구성된 금융 데이터 시각화 및 분석 도구입니다. 사용자는 검색 바를 통해 데이터를 검색하고, RPG 분류 및 데이터 시각화 기능을 활용할 수 있습니다.

---

## 프로젝트 구조
```
finance_challenge/
├── backend/                # 백엔드 디렉토리
│   └── app.py             # Flask 애플리케이션
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
4. Flask 서버를 실행합니다:
   ```bash
   python app.py
   ```
5. 서버가 `http://127.0.0.1:5000`에서 실행됩니다.

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
- **검색 바**: 사용자가 데이터를 검색할 수 있는 기능.
- **RPG 분류**: 데이터를 RPG 기준으로 분류.
- **데이터 시각화**: 차트 및 그래프를 통해 데이터를 시각적으로 표현.

---

## 기술 스택
- **프론트엔드**: React, Vite, Tailwind CSS
- **백엔드**: Python Flask
- **빌드 도구**: Vite

---

## 문제 해결
### 1. React 앱이 렌더링되지 않는 문제
- `index.html` 파일에 다음 스크립트를 추가하여 해결:
  ```html
  <script type="module" src="/src/main.jsx"></script>
  ```

### 2. Vite 설정 문제
- `vite.config.js` 파일에서 `root`와 `build` 설정을 추가하여 해결:
  ```javascript
  export default {
    root: './frontend',
    build: {
      outDir: 'dist',
    },
  };
  ```

---

## 향후 작업
- **RPG 분류 기능 구현**
- **데이터 시각화 기능 추가**
- **백엔드 API 통합**

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

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.
