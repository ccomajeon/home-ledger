# 프런트엔드 실행 안내

React, TypeScript, Vite로 구성된 Home Ledger 웹 화면입니다.

## 설치와 개발 서버

```powershell
cd frontend
npm ci
npm run dev
```

개발 서버는 기본적으로 `http://localhost:5173`에서 실행됩니다.

## 검사와 빌드

```powershell
npm run lint
npm run test
npm run format
npm run build
```

개발 API 주소는 `.env.example`의 `VITE_API_BASE_URL`로 지정합니다. 프로덕션
빌드에서는 값이 없을 경우 현재 Origin의 FastAPI 서버를 사용합니다.
