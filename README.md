# home-ledger 🏠📒

가족 가계부를 위한 경량 웹 앱입니다.
집/사무실의 Windows PC에서 로컬로 실행하고, 필요 시 Cloudflare Tunnel로 외부 접속도 지원합니다.

## 한눈에 보기 ✨

- 🔐 Google 계정 기반 로그인
- ✅ 서버에서 허용 계정(allowlist)으로 접근 제어
- 🧾 수입/지출 거래 관리
- 🗂️ 카테고리·결제수단 설정
- 🔎 날짜/유형/카테고리 기반 조회 필터
- 🧑‍💼 관리자(OWNER) 기능: 허용 계정 관리, 백업/복구

## 기술 구성 🧩

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + Alembic
- DB: SQLite

## 실행 방법 🚀

### 1) 백엔드 실행

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### 2) 프론트엔드 실행

```powershell
cd frontend
npm install
npm run dev
```

### 3) 한 번에 실행 (권장)

```powershell
.\scripts\dev.ps1
```

## 환경 변수(예시) ⚙️

- `backend/.env.example`
- `frontend/.env.example`

## 보안 원칙 🛡️

- 토큰은 브라우저 LocalStorage에 저장하지 않습니다.
- 인증되지 않은 요청은 401, 허용되지 않은 사용자 접근은 403으로 처리됩니다.
- 세션 쿠키는 HTTPOnly 설정으로 운영됩니다.

## 외부 접속 안내 🌐

- 포트포워딩 없이 Cloudflare Tunnel + Cloudflare Access로 외부 접근이 가능합니다.
- 외부 게이트웨이가 있더라도 앱 자체 allowlist 검증은 항상 동작합니다.

## 시작 전 체크리스트 ✅

- Owner 계정 이메일이 환경변수에 등록돼 있는지 확인
- 첫 관리자 로그인 후 필요 시 추가 허용 계정 등록
- 로컬/클라우드 실행 시 `FRONTEND_BASE_URL`, `BACKEND_BASE_URL` 값 확인

## 문의/기여 🤝

문제가 생기면 `Issue` 또는 PR로 남겨주세요.

