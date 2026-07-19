# 백엔드 실행 안내

FastAPI와 SQLAlchemy로 구성된 Home Ledger API입니다.

## 설치

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 개발 서버

```powershell
uvicorn app.main:app --reload --port 8000
```

앱 시작 시 SQLite 테이블과 기본 카테고리·결제수단·OWNER 계정이 자동으로
준비됩니다. API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 로컬 관리자 인증

`LOCAL_ADMIN_ENABLED=true`와 `LOCAL_ADMIN_PASSWORD_HASH`가 설정되면
`POST /auth/local-login`을 사용할 수 있습니다. 비밀번호는
`app.utils.security.create_password_hash`로 생성한 Argon2 해시만 환경 파일에
저장합니다. 로그인에 성공한 로컬 계정은 항상 활성화된 `OWNER` 권한을 갖습니다.
반복 실패 요청에는 IP 기준 로그인 제한이 적용됩니다.

## 검사

```powershell
python -m ruff check app tests
python -m black --check app tests
python -m pytest -q
```

환경 변수는 `.env.example`을 `.env`로 복사한 뒤 수정하세요.
