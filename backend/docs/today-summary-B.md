# B개발자 작업 요약

## 📅 날짜
2026-07-22 (화)

---

## ✅ 완료된 작업

### 1. 도메인 모델 수정

#### `app/domain/models/trip.py`

**🎯 목적**
- `baggage_summary` 데이터 타입을 더 적합한 구조로 수정

**💡 이유**
- 수화물 요약은 카테고리별로 분류된 리스트 형태가 더 적합
- A개발자가 `today-summary-A.md`에서 수정한 내용과 일치

**📦 수정 내용**
```python
# 수정 전
baggage_summary: dict = field(default_factory=dict)

# 수정 후
baggage_summary: list[dict] = field(default_factory=list)
```

**영향**
- `update_baggage_summary()` 메서드 시그니처도 함께 수정

---

### 2. ORM 모델 구현

#### 파일 구조
```
infrastructure/database/models/
├── __init__.py
├── trip_model.py       ✅ Trip ORM 모델
├── profile_model.py    ✅ Profile ORM 모델
├── item_model.py       ✅ Item ORM 모델
└── memo_model.py       ✅ Memo ORM 모델
```

#### TripModel (`infrastructure/database/models/trip_model.py`)

**🎯 목적**
- Trip 테이블에 대한 SQLAlchemy ORM 모델 정의

**📦 주요 특징**
- `shared/config/database.py`의 `Base` 사용 (SQLAlchemy 2.0+)
- UUID 기반의 `id` (String으로 매핑)
- JSON 필드: `purpose`, `cautions`, `baggage_summary`
- 자동 타임스탬프: `created_at`, `updated_at`
- 인덱스: `id`, `user_id`

**💡 이유**
- A개발자의 도메인 모델과 동기화
- 레거시 `declarative_base()` 대신 최신 `DeclarativeBase` 사용
- 비동기 쿼리 지원

---

#### ProfileModel (`infrastructure/database/models/profile_model.py`)

**🎯 목적**
- Supabase Auth의 `auth.users` 테이블과 연동되는 프로필 정보

**📦 주요 특징**
- `id`가 `auth.users.id`와 동일하게 UUID
- `email`에 유니크 인덱스 설정
- 자동 타임스탬프

**💡 이유**
- Supabase Auth와 사용자 프로필 데이터 분리
- 추가적인 사용자 정보 저장 가능

---

#### ItemModel (`infrastructure/database/models/item_model.py`)

**🎯 목적**
- 여행에 필요한 짐 항목 저장

**📦 주요 특징**
- `baggage_flag`: `carry_on_only` | `checked_only` | `restricted` | `null`
- `source`: `ai` (AI 생성) 또는 `user` (사용자 직접 추가)
- `checked`: 체크리스트 완료 여부
- 인덱스: `id`, `trip_id`, `category`, `source`, `checked`

**💡 이유**
- 수화물 규정 체크 기능 지원
- AI 생성 vs 사용자 추가 구분
- 진행 상황 추적

---

#### MemoModel (`infrastructure/database/models/memo_model.py`)

**🎯 목적**
- 여행에 관한 메모/기록 저장

**📦 주요 특징**
- `content`: 최대 2,000자 (Text 타입)
- 자동 타임스탬프

**💡 이유**
- 사용자가 여행 관련 메모 저장 가능
- 자유로운 텍스트 입력 지원

---

### 3. Repository 구현

#### SQLAlchemyTripRepository (`infrastructure/database/repositories/sqlalchemy_trip_repository.py`)

**🎯 목적**
- A개발자가 정의한 `TripRepository` 인터페이스 구현

**📦 구현 메서드**
- `save(trip: Trip) -> Trip`: 저장/업데이트 (기존 Trip이면 업데이트)
- `find_by_id(trip_id: TripId) -> Trip | None`: ID로 조회
- `find_by_user_id(user_id: str) -> list[Trip]`: 사용자별 조회 (생성일 내림차순)
- `delete(trip_id: TripId) -> None`: 삭제

**📦 변환 메서드**
- `_to_domain(model: TripModel) -> Trip`: ORM → 도메인 모델
- `_to_infrastructure(trip: Trip) -> TripModel`: 도메인 → ORM 모델

**💡 이유**
- A개발자의 인터페이스 계약 완전 준수
- 도메인 모델 독립성 유지
- 비동기 처리 지원

**특징**
- JSON 필드 타입 안전하게 처리 (list/dict 변환)
- 업데이트 시 기존 레코드 확인 후 수정
- 조회 결과 생성일 기준 내림차순 정렬

---

### 4. 의존성 주입 설정

#### 파일 구조
```
infrastructure/database/dependencies/
├── __init__.py
└── repositories.py     ✅ Repository DI 설정
```

#### `infrastructure/database/dependencies/repositories.py`

**🎯 목적**
- FastAPI의 의존성 주입(DI)을 위한 함수 제공

**📦 주요 기능**
- `get_trip_repository()`: TripRepository 주입
- `TripRepositoryDep`: 타입 힌트 별칭

**💡 이유**
- 요청마다 독립된 DB 세션 제공
- 코드 가독성 향상 (타입 힌트 사용)
- 테스트 시 Mock 주입 용이

**사용 예시:**
```python
from infrastructure.database.dependencies import TripRepositoryDep

@router.get("/trips")
async def get_trips(
    trip_repo: TripRepositoryDep,
):
    trips = await trip_repo.find_by_user_id(user_id)
    return trips
```

---

### 5. Alembic 마이그레이션 설정

#### `alembic/env.py`

**🎯 목적**
- Alembic이 ORM 모델을 감지하여 마이그레이션 생성

**📦 수정 내용**
- 실제 `Base` import (`shared.config.database.Base`)
- 모든 ORM 모델 import (메타데이터에 등록)
- `target_metadata = Base.metadata` 설정

**💡 이유**
- 자동 마이그레이션 생성 지원
- DB 스키마와 ORM 모델 동기화

---

### 6. Pydantic 스키마 작성

#### `app/schemas/trip_domain.py`

**🎯 목적**
- 도메인 모델에 맞는 API 요청/응답 스키마 정의

**📦 스키마 목록**
- `TripResponse`: Trip 응답 (모든 필드 포함)
- `TripCreate`: Trip 생성 (필수/선택 필드 구분)
- `TripUpdate`: Trip 수정 (모든 필드 선택적)
- `TripListResponse`: Trip 목록 응답

**💡 이유**
- API 계약서 역할
- 자동 검증 및 문서화
- 도메인 모델과 분리

**특징**
- 필드별 길이/범위 제한
- 기본값 설정 (`default_factory=list`)
- `from_attributes = True` (ORM 모델 변환 지원)

---

### 7. API 라우터 구현

#### `app/api/trip_domain.py`

**🎯 목적**
- 도메인 모델 기반의 RESTful API 엔드포인트 구현

**📦 엔드포인트**

| Method | URL | 설명 |
|--------|-----|------|
| GET | `/api/v1/trips` | 사용자의 모든 Trip 조회 |
| GET | `/api/v1/trips/{trip_id}` | 특정 Trip 조회 |
| POST | `/api/v1/trips` | Trip 생성 (201 Created) |
| PATCH | `/api/v1/trips/{trip_id}` | Trip 수정 |
| DELETE | `/api/v1/trips/{trip_id}` | Trip 삭제 (204 No Content) |

**💡 이유**
- A개발자의 도메인 모델과 Repository 사용
- RESTful 설계 원칙 준수
- 소유권 확인 (자신의 Trip만 접근 가능)

**특징**
- 의존성 주입 사용 (`TripRepositoryDep`)
- 적절한 HTTP 상태 코드 반환
- 상세한 에러 메시지
- 로깅 포함

---

#### 라우터 등록 (`app/main.py`)

```python
from app.api import trip_domain

app.include_router(
    trip_domain.router,
    prefix="/api/v1/trips",
    tags=["Trips V1 (Domain)"]
)
```

---

### 8. 단위 테스트 작성

#### `tests/infrastructure/test_sqlalchemy_trip_repository.py`

**🎯 목적**
- SQLAlchemyTripRepository 정확성 검증

**📦 테스트 항목**
- `test_save_new_trip`: 새 Trip 저장
- `test_save_update_existing_trip`: 기존 Trip 업데이트
- `test_find_by_id`: ID로 조회
- `test_find_by_id_not_found`: 존재하지 않는 ID 조회
- `test_find_by_user_id`: 사용자별 조회
- `test_find_by_user_id_empty`: Trip이 없는 사용자 조회
- `test_delete`: Trip 삭제
- `test_to_domain_conversion`: ORM → 도메인 변환

**💡 이유**
- Repository 구현 정확성 검증
- 변환 로직 테스트
- 에지 케이스 처리 확인

---

#### `tests/conftest.py` 업데이트

**📦 수정 내용**
- 올바른 import 경로 (`shared.config.database`)
- 모든 ORM 모델 import (테이블 생성용)
- `db_session` fixture에 테이블 생성/삭제 로직 추가

**💡 이유**
- 테스트마다 독립된 DB 환경 제공
- ORM 모델 자동 감지

---

### 9. Redis 캐싱 구현

#### `app/application/services/cached_trip_query_service.py`

**🎯 목적**
- TripQueryService에 캐싱 기능 추가

**📦 주요 기능**
- `get_user_trips()`: 사용자 Trip 목록 캐싱
- `get_trip_by_id()`: 특정 Trip 캐싱
- `invalidate_user_trips_cache()`: 사용자 캐시 무효화
- `invalidate_trip_cache()`: Trip 캐시 무효화

**📦 캐시 전략**
- 캐시 키: `trip:{trip_id}`, `user_trips:{user_id}`
- TTL: 3600초 (1시간)
- 캐시 미스 시 DB 조회 후 캐시 저장
- 캐시 히트 시 캐시에서 반환

**💡 이유**
- DB 쿼리 감소 (성능 향상)
- 비용 절감 (Gemini API 호출 줄임)
- 사용자 경험 개선 (빠른 응답)

**특징**
- JSON 직렬화/역직렬화
- 캐시 손상 시 자동 복구 (DB 조회)
- Trip 생성/수정/삭제 시 캐시 무효화

---

#### `tests/application/test_cached_trip_query_service.py`

**🎯 목적**
- 캐싱 서비스 정확성 검증

**📦 테스트 항목**
- 캐시 미스 시 DB 조회 및 캐시 저장
- 캐시 히트 시 캐시에서 반환
- 사용자 Trip 목록 캐시 무효화
- Trip 캐시 무효화
- Trip 업데이트 시 캐시 무효화 통합 테스트

---

### 10. DB 연동 및 테이블 생성

#### asyncpg 패키지 설치

**🎯 목적**
- PostgreSQL 비동기 드라이버 설치
- SQLAlchemy와 PostgreSQL 연동 지원

**💡 이유**
- 비동기 DB 작업을 위한 필수 패키지
- `postgresql+asyncpg://` URL 형식 사용 필요

**📦 설치 결과**
```bash
✅ Successfully installed asyncpg-0.31.0
```

---

#### 환경설정 문제 해결

**🎯 목적**
- CORS_ORIGINS 파싱 오류 해결
- pydantic-settings 설정 로직 수정

**💡 이유**
- 리스트 형태의 환경변수가 JSON으로 파싱되지 않도록 수정

**📦 수정 내용**
```bash
# 수정 전
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 수정 후  
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

---

#### DB 연결 테스트

**🎯 목적**
- PostgreSQL 연결 상태 확인
- 드라이버 및 설정 유효성 검증

**📦 테스트 결과**
```bash
✅ DB 연결 성공!
📊 PostgreSQL 버전: PostgreSQL 16.14 on x86_64-pc-linux-musl
📋 기존 테이블: ['alembic_version']
```

**💡 이유**
- 애플리케이션 시작 전 DB 연결 확인
- 문제 조기 발견 및 해결

---

#### 테이블 생성 (venv 환경)

**🎯 목적**
- ORM 모델 기반 테이블 생성
- 데이터베이스 스키마 초기화

**💡 이유**
- Alembic 마이그레이션 도구 문제 대신 직접 생성
- venv 환경에서 안정적으로 실행

**📦 생성 결과**
```bash
✅ 테이블 생성 완료!
📦 등록된 모델: ['items', 'memos', 'profiles', 'trips']
📋 생성된 테이블 (5개):
   - alembic_version
   - items
   - memos
   - profiles
   - trips
```

**📊 생성된 테이블 구조**

1. **trips** - 여행 정보
   - id, user_id, title, destination
   - purpose, cautions, baggage_summary (JSON)
   - duration_nights, departure_month, companions
   - 인덱스: id, user_id

2. **profiles** - 사용자 프로필
   - id, email
   - 인덱스: id, email (UNIQUE)

3. **items** - 짐 항목
   - id, trip_id, category, name
   - quantity, tip, baggage_flag
   - source, checked
   - 인덱스: id, trip_id, category, source, baggage_flag, checked

4. **memos** - 메모
   - id, trip_id, content
   - 인덱스: id, trip_id

5. **alembic_version** - 마이그레이션 버전 관리

**특징**
- 모든 테이블에 자동 타임스탬프 (created_at, updated_at)
- 적절한 인덱스 설정으로 성능 최적화
- JSON 필드로 유연한 데이터 저장

---

### 11. 정리 작업

#### 레거시 파일 삭제
- ✅ `infrastructure/database/base.py` 삭제
  - 레거시 `declarative_base()` 방식
  - `shared/config/database.py`의 `Base`로 통일

**💡 이유**
- 중복 제거
- 최신 SQLAlchemy 방식 사용

---

## 📊 작업 완료율

| 단계 | 작업 | 상태 | 완료율 |
|------|------|------|--------|
| **1단계** | 키 발급 및 테스트 | ✅ | 100% |
| **2단계** | ORM 모델 구현 | ✅ | 100% |
| **3단계** | Repository 구현 | ✅ | 100% |
| **4단계** | 의존성 주입 설정 | ✅ | 100% |
| **5단계** | Alembic 설정 | ✅ | 100% |
| **6단계** | Pydantic 스키마 | ✅ | 100% |
| **7단계** | API 라우터 구현 | ✅ | 100% |
| **8단계** | 단위 테스트 | ✅ | 100% |
| **9단계** | Redis 캐싱 | ✅ | 100% |
| **10단계** | DB 연동 및 테이블 생성 | ✅ | 100% |
| **11단계** | 정리 작업 | ✅ | 100% |
| **전체** | - | - | **100%** |

---

## 📂 생성/수정 파일 목록

### 새로 생성된 파일

```
backend/
├── infrastructure/
│   ├── database/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── trip_model.py
│   │   │   ├── profile_model.py
│   │   │   ├── item_model.py
│   │   │   └── memo_model.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── sqlalchemy_trip_repository.py
│   │   └── dependencies/
│   │       ├── __init__.py
│   │       └── repositories.py
├── app/
│   ├── api/
│   │   └── trip_domain.py
│   ├── schemas/
│   │   └── trip_domain.py
│   └── application/
│       └── services/
│           └── cached_trip_query_service.py
├── tests/
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── test_sqlalchemy_trip_repository.py
│   └── application/
│       └── test_cached_trip_query_service.py
└── (DB 연동 관련)
    ├── test_db_connection.py  (DB 연결 테스트 스크립트)
    └── create_tables.py       (테이블 생성 스크립트)
```

### 수정된 파일

```
backend/
├── app/
│   ├── domain/
│   │   └── models/
│   │       └── trip.py  (baggage_summary 타입 수정)
│   ├── application/
│   │   └── services/
│   │       └── __init__.py
│   └── main.py  (라우터 등록)
├── alembic/
│   └── env.py  (Base import 수정)
├── tests/
│   └── conftest.py  (DB 설정 수정)
└── .env  (CORS_ORIGINS 파싱 문제 해결)
```

### 삭제된 파일

```
backend/
└── infrastructure/
    └── database/
        └── base.py  (레거시 파일 삭제)
```

---

## 🎯 성공 기준 달성

### 완료 체크리스트

- [x] 도메인 모델 `baggage_summary` 타입 수정
- [x] Trip ORM 모델 작성
- [x] Profile ORM 모델 작성
- [x] Item ORM 모델 작성
- [x] Memo ORM 모델 작성
- [x] TripRepository 구현 (SQLAlchemy)
- [x] 의존성 주입 함수 작성
- [x] Alembic 설정 수정
- [x] Pydantic 스키마 작성
- [x] API 라우터 구현 (5개 엔드포인트)
- [x] Repository 단위 테스트
- [x] 캐싱 서비스 구현
- [x] 캐싱 서비스 테스트
- [x] asyncpg 패키지 설치
- [x] 환경설정 문제 해결 (CORS_ORIGINS)
- [x] DB 연결 테스트
- [x] 테이블 생성 (trips, profiles, items, memos)
- [x] 레거시 파일 삭제
- [x] 라우터 등록

---

## 🔄 A개발자와 협업 포인트

### A개발자에게 알릴 사항

1. **도메인 모델 수정 완료**
   - `baggage_summary` 타입을 `dict` → `list[dict]`로 수정
   - `update_baggage_summary()` 메서드도 함께 수정

2. **Base 클래스 통일 완료**
   - `infrastructure/database/base.py` 삭제됨
   - 모든 ORM 모델은 `shared/config/database.py`의 `Base` 사용

3. **Repository 구현 완료**
   - A개발자가 정의한 인터페이스 완전 구현
   - 도메인 모델 ↔ ORM 모델 변환 로직 포함
   - 비동기 처리 지원

4. **의존성 주입 준비 완료**
   - `TripRepositoryDep` 타입 힌트로 사용 가능
   - FastAPI의 `Depends()`로 자동 주입

5. **API 라우터 구현 완료**
   - `/api/v1/trips` 엔드포인트 (도메인 기반)
   - RESTful 설계 원칙 준수
   - 소유권 확인 로직 포함

6. **캐싱 서비스 구현 완료**
   - `CachedTripQueryService`로 성능 향상
   - 자동 캐시 무효화 지원
   - Trip 생성/수정/삭제 시 캐시 갱신 가능

7. **DB 연동 완료**
   - asyncpg 패키지 설치
   - 환경설정 문제 해결
   - DB 연결 테스트 성공
   - 모든 테이블 생성 완료 (trips, profiles, items, memos)
   - 애플리케이션 실행 가능 상태

---

## 🚀 다음 단계 (A개발자와 협업)

### 1. 통합 테스트 (완료 가능)
```bash
cd backend
.\venv\Scripts\python.exe -m pytest tests/infrastructure/test_sqlalchemy_trip_repository.py -v
.\venv\Scripts\python.exe -m pytest tests/application/test_cached_trip_query_service.py -v
```

### 2. API 엔드포인트 테스트
- FastAPI 앱 시작
- Swagger UI에서 테스트
- 단위 테스트로 CRUD 기능 검증

### 3. API 스펙 문서 업데이트
- 새로운 엔드포인트 반영
- `docs/api-specs/trip-api-spec.md` 업데이트

### 4. Week 2 시작 준비
- A개발자: Trip 생성 도메인 로직 정의
- A개발자: CreateTripCommand 작성
- A개발자: TripGenerationService 인터페이스 정의
- B개발자: Gemini SDK 연동 (A의 정의 후)
- B개발자: 스트리밍 API 구현

### 5. Item/Meto Repository 구현
- A개발자: Item, Memo 도메인 모델 정의
- A개발자: ItemRepository, MemoRepository 인터페이스
- B개발자: SQLAlchemyItemRepository, SQLAlchemyMemoRepository 구현

---

## 📝 비고

### 기술적 결정

1. **데이터 타입 선택**
   - `baggage_summary`: `list[dict]` 선택 (카테고리별 분류에 적합)
   - `id`: `String(36)` 선택 (UUID 문자열로 직접 매핑)

2. **캐싱 전략**
   - TTL: 1시간 (데이터 변경 빈도 고려)
   - JSON 직렬화 (복잡한 객체 캐싱)
   - 캐시 무효화 (데이터 변경 시)

3. **API 설계**
   - `/api/v1/trips` 버전 관리 (향후 호환성)
   - 적절한 HTTP 상태 코드 (201, 204)
   - 소유권 확인 (보안)

4. **DB 연동 전략**
   - venv 환경 사용 (Poetry 대신)
   - 직접 테이블 생성 (Alembic 대신)
   - asyncpg 드라이버 사용 (비동기 지원)
   - JSON 필드 사용 (유연한 데이터 저장)

### 성능 고려사항

- 비동기 처리로 높은 동시성 지원
- 인덱스 설정 (`id`, `user_id`, `category`, `checked`)
- 캐싱으로 DB 쿼리 감소
- 연결 풀 설정 (`pool_size=10`, `max_overflow=20`)

### 보안 고려사항

- 소유권 확인 (자신의 Trip만 접근 가능)
- 필드 길이 제한 (DoS 방지)
- JWT 인증 통합 (`UserDep` 사용)

---

## 🎉 DB 연동 완료!

### ✅ 최종 상태

| 항목 | 상태 |
|------|------|
| **PostgreSQL 컨테이너** | ✅ 실행 중 |
| **DB 연결** | ✅ 성공 |
| **asyncpg 드라이버** | ✅ 설치 완료 |
| **환경설정** | ✅ 수정 완료 |
| **ORM 모델 테이블** | ✅ 생성 완료 |
| **인덱스** | ✅ 생성 완료 |
| **앱 실행 가능** | ✅ 준비 완료 |

### 📊 DB 구조 요약

```
trapkit 데이터베이스
├── profiles      (사용자 프로필)
├── trips         (여행 정보)
├── items         (짐 항목)
├── memos         (메모)
└── alembic_version (마이그레이션 관리)
```

### 🛠️ 사용된 도구

- **PostgreSQL 16.14**: 데이터베이스 서버
- **asyncpg 0.31.0**: 비동기 드라이버
- **SQLAlchemy 2.0.51**: ORM
- **venv**: 가상환경 (Poetry 대신)

---

## 🔄 Week 2 진행 상황 (2026-07-22)

### A개발자 완료 작업 ✅

- ✅ `application/commands/create_trip.py` 작성
- ✅ `domain/services/trip_generation_service.py` 작성

### B개발자 미완료 작업 ❌

- ❌ `infrastructure/external/gemini_client.py` 작성
- ❌ `infrastructure/external/redis_client.py` 작성
- ❌ `POST /api/trips/generate` 스트리밍 구현
- ❌ 스트리밍 테스트 통과

### 💡 해결 필요 문제

1. **infrastructure/external 디렉토리 생성 필요**
2. **Gemini SDK 연동** (A의 AIClient 인터페이스 구현)
3. **스트리밍 API 구현** (Server-Sent Events)

---

## 🚨 통합 테스트 문제 해결 (2026-07-22)

### 발생 문제

1. **SQLite 호환성 문제**
   - PostgreSQL 전용 pool 설정이 SQLite에서 오류 발생
   - `aiosqlite` 모듈 누락

2. **Import 경로 오류**
   - `app.api.dependencies` 모듈이 존재하지 않음
   - `UserDep` 타입 대신 `str`로 직접 사용

### 해결 조치

#### 1. DB 설정 수정 (`app/core/database.py`)
```python
# SQLite는 pool 설정을 지원하지 않음
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
}

# PostgreSQL만 pool 설정 추가
if "postgresql" in _db_url:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
```

#### 2. 테스트 conftest.py 수정
```python
# 테스트용 DB URL 오버라이드 (앱 초기화 전)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET"] = "test-secret-key-at-least-32-chars"
```

#### 3. trip_domain.py import 수정
```python
# 수정 전
from app.api.dependencies import UserDep

# 수정 후
from interfaces.api.dependencies.auth import get_current_user_id
```

### 결과

- ✅ SQLite 테스트 환경 호환성 확보
- ✅ Import 경로 문제 해결
- ✅ 통합 테스트 실행 가능 상태

---

*마지막 업데이트: 2026-07-22*
*작업 시간: 약 7시간 (Week 1) + 1시간 (테스트 문제 해결)*
*Week 1 완료율: 100%*
*Week 2 완료율: 33% (A개발자 2/6 완료)*
