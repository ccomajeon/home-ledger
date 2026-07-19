# home-ledger 🏠📒

가족이 함께 사용하는 경량 가계부 웹 앱입니다. Windows PC에서 한 서버로 실행할 수
있으며, 필요하면 Cloudflare Tunnel을 통해 외부에서도 접속할 수 있습니다.

## 주요 기능

- Argon2 기반 로컬 관리자 로그인, Google OAuth와 HTTPOnly 서명 세션 쿠키
- OWNER 계정·허용 계정·허용 이메일 도메인 기반 접근 제어
- 수입/지출 거래 등록, 수정, 삭제 및 날짜·유형·분류·검색어 필터
- 수입·지출·잔액 요약
- 카테고리와 결제수단 관리
- OWNER 전용 계정 관리, 감사 로그, SQLite 백업·복원
- 모바일과 데스크톱을 지원하는 React 화면

## 기술 구성

- Frontend: React 19, TypeScript, Vite
- Backend: FastAPI, SQLAlchemy
- Database: SQLite
- Test: Pytest, Vitest, Testing Library

## 준비 사항

- Python 3.11 이상
- Node.js 20 이상과 npm

처음 실행하기 전에 `backend/.env.example`을 `backend/.env`로 복사하고
`SESSION_SECRET`을 설정하세요. 로컬 관리자 로그인이나 Google OAuth 중 사용할
인증 방식을 하나 이상 설정해야 합니다. Google Cloud Console의 승인된 리디렉션
URI는 기본값 기준 `http://localhost:8000/auth/callback`입니다.

## 로컬 관리자 로그인

로컬 관리자는 로그인할 때마다 `OWNER` 권한으로 보정되며 계정 관리, 백업·복원 등
모든 관리 기능을 사용할 수 있습니다. 비밀번호 원문은 소스나 환경 파일에 저장하지
않고 Argon2 해시만 저장합니다.

가상환경 설치 후 다음 명령으로 비밀번호 해시를 생성하세요.

```powershell
cd backend
.\.venv\Scripts\python.exe -c "from getpass import getpass; from app.utils.security import create_password_hash; print(create_password_hash(getpass('새 비밀번호: ')))"
```

출력된 해시를 `backend/.env`의 `LOCAL_ADMIN_PASSWORD_HASH`에 넣고 다음 항목을
설정합니다. 기본 사용자 이름은 `SYSTEM`입니다.

```dotenv
LOCAL_ADMIN_ENABLED=true
LOCAL_ADMIN_USERNAME=SYSTEM
LOCAL_ADMIN_PASSWORD_HASH=<생성된 Argon2 해시>
LOCAL_ADMIN_IDENTITY=system@local
```

`backend/.env`는 Git에서 제외됩니다.

## 한 번에 빌드하고 실행

다음 명령은 Python 가상환경과 npm 패키지를 준비하고, 전체 검사·테스트와 프런트엔드
프로덕션 빌드를 수행한 뒤 FastAPI 단일 서버를 시작합니다.

```powershell
.\scripts\server.ps1
```

PowerShell 실행 정책이 스크립트를 차단하는 PC에서는 다음 명령을 사용하세요.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\server.ps1
```

서버가 시작되면 [http://localhost:8000](http://localhost:8000)에서 접속할 수 있습니다.

빌드와 실행을 나누려면 다음과 같이 사용합니다.

```powershell
.\scripts\build.ps1
.\scripts\start.ps1
```

Linux/macOS에서는 `./scripts/server.sh` 또는 `build.sh`와 `start.sh`를 사용할 수
있습니다.

## 개발 모드

백엔드와 Vite 개발 서버를 각각 실행합니다.

```powershell
.\scripts\dev.ps1
```

- Vite로 로그인 후 돌아올 주소가 필요하면 `backend/.env`의
  `FRONTEND_BASE_URL=http://localhost:5173`으로 변경합니다.
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`

## 검증

전체 빌드 하네스는 테스트를 기본 포함합니다. 이미 빌드한 결과가 실제로 제공되는지
빠르게 확인하려면 다음 스모크 테스트를 실행하세요.

```powershell
.\scripts\smoke.ps1
```

개별 검사는 다음 명령으로 실행할 수 있습니다.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests

cd ..\frontend
npm run lint
npm run test
npm run build
```

## 환경 설정

주요 백엔드 환경 변수는 다음과 같습니다.

- `SESSION_SECRET`: 세션 서명 키. 운영에서는 충분히 긴 임의 문자열을 사용합니다.
- `OWNER_EMAIL`: 최초 OWNER 계정
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: Google OAuth 자격 증명
- `ALLOWED_EMAIL_DOMAINS`: 쉼표로 구분한 자동 허용 도메인
- `CORS_ALLOW_ORIGINS`: 개발 프런트엔드 등 허용 Origin 목록
- `DB_URL`: 기본값 `sqlite:///./data/app.db`
- `BACKUP_DIR`: 기본값 `./data/backups`
- `DEV_AUTH_BYPASS`: 개발 전용 로그인 API 활성화. 운영에서는 사용하지 않습니다.
- `LOCAL_ADMIN_ENABLED`: 로컬 관리자 로그인 활성화 여부
- `LOCAL_ADMIN_USERNAME`: 로컬 관리자 사용자 이름
- `LOCAL_ADMIN_PASSWORD_HASH`: 원문이 아닌 Argon2 비밀번호 해시
- `LOCAL_ADMIN_IDENTITY`: 앱 내부에서 사용하는 로컬 관리자 식별자

전체 예시는 `backend/.env.example`과 `frontend/.env.example`을 참고하세요.

## 보안 원칙

- 인증 토큰을 LocalStorage에 저장하지 않습니다.
- 세션 쿠키는 HTTPOnly와 SameSite 속성을 사용하며 운영 환경에서는 Secure로 전송합니다.
- 인증 실패는 401, 허용되지 않은 계정은 403으로 구분합니다.
- 외부 게이트웨이 사용 여부와 관계없이 앱 자체 허용 목록 검증을 항상 적용합니다.
