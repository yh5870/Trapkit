# Trapkit Backend

FastAPI 기반 Tripkit 백엔드 API

## 기술 스택

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL (Async SQLAlchemy)
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (python-jose)
- **AI**: Google Gemini API
- **Testing**: pytest, pytest-asyncio

## 프로젝트 구조

```
trapkit-backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 (환경변수, DB 연결)
│   ├── dependencies.py         # 의존성 주입 (DB 세션, 인증)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py             # 인증 API (회원가입, 로그인, 로그아웃)
│   │   ├── trips.py            # 트립/체크리스트/메모 API
│   │   ├── baggage.py          # 수화물 체커 API
│   │   └── health.py           # 헬스체크
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User 모델
│   │   ├── trip.py             # Trip 모델
│   │   ├── checklist_item.py   # ChecklistItem 모델
│   │   ├── memo.py             # Memo 모델
│   │   └── baggage_rule.py     # BaggageRule 모델
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # 인증 스키마 (요청/응답)
│   │   ├── trip.py             # 트립 스키마
│   │   ├── baggage.py          # 수화물 체커 스키마
│   │   └── ai.py               # AI 응답 스키마
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI 호출 서비스 (Google Gemini)
│   │   ├── baggage_checker.py  # 수화물 판정 엔진
│   │   ├── cache.py            # 캐시 서비스 (Redis)
│   │   └── rate_limit.py       # 레이트 리밋 서비스
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT 토큰 생성/검증, 비밀번호 해싱
│   │   ├── database.py         # DB 세션 관리
│   │   └── redis.py            # Redis 연결
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # 로거 설정
│       └── exceptions.py       # 커스텀 예외
├── tests/
│   ├── conftest.py             # pytest 설정
│   ├── test_auth.py
│   ├── test_trips.py
│   └── test_baggage.py
├── alembic/                    # DB 마이그레이션
│   ├── env.py
│   └── versions/
├── .env.example                # 환경변수 예시
├── requirements.txt            # pip 의존성
├── docker-compose.yml          # 로컬 개발 환경
├── Dockerfile                  # 배포용 Dockerfile
└── README.md                   # 이 파일
```

## 환경변수

```bash
cp .env.example .env
```

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 연결 URL | - |
| `JWT_SECRET` | JWT 시크릿 키 | - |
| `GEMINI_API_KEY` | Google Gemini API 키 | - |
| `GEMINI_MODEL` | Gemini 모델 | `gemini-1.5-flash` |
| `REDIS_URL` | Redis 연결 URL | - |
| `CORS_ORIGINS` | 허용된 CORS 오리진 | `http://localhost:3000` |

## 설치

```bash
# venv 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -e .

# DB 마이그레이션
alembic upgrade head
```

## 실행

```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

```bash
# 전체 테스트
pytest

# 커버리지 리포트
pytest --cov=app --cov-report=html

# 특정 테스트
pytest tests/test_auth.py
```

## Docker

```bash
# 로컬 개발 (PostgreSQL + Redis + FastAPI)
docker-compose up --build

# DB만 실행
docker-compose up -d postgres redis
```

## API 목록

### 인증 (`/api/auth`)
- `POST /api/auth/signup` - 회원가입
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/reset-request` - 비밀번호 재설정 요청
- `POST /api/auth/reset` - 비밀번호 재설정
- `DELETE /api/auth/me` - 회원 탈퇴

### 트립 (`/api/trips`)
- `GET /api/trips` - 내 여행 목록
- `GET /api/trips/{tripId}` - 여행 상세
- `POST /api/trips/generate` - AI 리스트 생성
- `PATCH /api/trips/{tripId}` - 여행 제목 수정
- `DELETE /api/trips/{tripId}` - 여행 삭제
- `POST /api/trips/{tripId}/items` - 항목 추가
- `PATCH /api/trips/{tripId}/items/{itemId}` - 항목 수정/체크 토글
- `DELETE /api/trips/{tripId}/items/{itemId}` - 항목 삭제
- `POST /api/trips/{tripId}/memos` - 메모 추가
- `PATCH /api/trips/{tripId}/memos/{memoId}` - 메모 수정
- `DELETE /api/trips/{tripId}/memos/{memoId}` - 메모 삭제
- `POST /api/trips/import` - 비로그인 로컬 트립 이관

### 수화물 체커 (`/api/baggage`)
- `POST /api/baggage/check` - 수화물 판정

### 헬스체크
- `GET /health` - 서버 상태 확인

## 개발 가이드

### DB 마이그레이션 생성

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 실행
alembic upgrade head

# 롤백
alembic downgrade -1
```

### 새 API 엔드포인트 추가

1. `app/api/`에 파일 생성
2. `app/main.py`에 라우터 등록
3. `app/schemas/`에 스키마 추가
4. `tests/`에 테스트 추가

### AI 호출

`app/services/ai_service.py`의 `generate_trip_list()` 함수를 참고하세요.

## 라이선스

MIT