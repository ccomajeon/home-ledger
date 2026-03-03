# 백엔드 실행 안내 (FastAPI)

## 설치

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

Windows에서 `python` 명령이 동작하지 않으면 다음과 같이 실행하세요.

```powershell
& "$env:LocalAppData\Programs\Python\Python312\python.exe" -m venv .venv
```

## 실행

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

## 테스트

```powershell
cd backend
pytest -q
```

## 참고

- `/api/me`는 현재 기본 동작이 `401`로 닫힘 상태입니다.
- Alembic 마이그레이션 골격은 준비돼 있으며, 초기 스키마 생성은 단계적으로 반영됩니다.
