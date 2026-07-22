# 오늘 작업 요약

## 📅 날짜
2026-07-21 (월)

---

## ✅ 완료된 작업

### 1단계: 인프라 기반

#### DB Base Model (`infrastructure/database/base.py`)

**🎯 목적**
- 모든 SQLAlchemy ORM 모델이 상속받을 공통 기반 클래스 제공
- Alembic 마이그레이션에서 테이블을 자동 감지하여 스키마 생성

**💡 이유**
- 단일 Base 클래스로 모든 모델의 메타데이터 중앙 관리
- Alembic이 `Base.metadata`를 통해 변경 사항을 감지
- 일관된 모델 구조 유지

**📦 산출물**
```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

---

#### Database Config (`shared/config/database.py`)

**🎯 목적**
- PostgreSQL 비동기 연결 엔진 생성 및 관리
- FastAPI의 의존성 주입(DI)을 통해 요청마다 독립된 DB 세션 제공
- 트랜잭션 관리 (자동 커밋/롤백)

**💡 이유**
- 비동기 처리로 높은 동시성 지원
- 요청별 세션 격리로 데이터 일관성 보장
- 커넥션 풀로 DB 연결 효율화

**📦 주요 기능**
- `create_async_engine()`: 비동기 엔진 생성 (echo=True로 쿼리 로그)
- `AsyncSessionLocal`: 세션 팩토리 (expire_on_commit=False로 객체 접근 유지)
- `get_db()`: 의존성 주입 함수 (자동 트랜잭션 관리)
- `init_db()`: 개발용 테이블 초기화 (실제 배포에서는 Alembic 사용)

**⚙️ 설정**
- `pool_size=10`: 기본 커넥션 풀 크기
- `max_overflow=20`: 초과 커넥션 최대 개수
- `pool_pre_ping=True`: 연결 유효성 자동 검사

**📦 산출물**
```python
# 비동기 엔진
engine = create_async_engine(settings.DATABASE_URL, echo=True, ...)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(engine, ...)

# 의존성 주입
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## ⏸️ 진행 중인 작업

### 2단계: 인증 구현 (완료)

#### Auth Dependency (`interfaces/api/dependencies/auth.py`)

---

### 3단계: API 스키마 (완료)

#### Trip Schemas (`interfaces/api/v1/schemas/trip_schemas.py`)

**🎯 목적**
- API 요청/응답 데이터 구조 정의
- Pydantic으로 자동 검증 및 직렬화
- FastAPI의 OpenAPI 문서 자동 생성

**💡 이유**
- A개발자와 독립적으로 스키마 정의 가능
- API 계약서 역할 (협업 기준)
- 자동 유효성 검사로 버그 방지
- Type Hints로 IDE 자동 완성 지원

**📦 주요 스키마**
- `TripResponse`: 트립 조회 응답
- `TripCreateRequest`: 트립 생성 요청
- `TripUpdateRequest`: 트립 수정 요청
- `TripDeleteResponse`: 트립 삭제 응답

**🔄 Note**
- A의 `Trip` 모델과 독립적
- 나중에 `_from_domain()` 메서드로 연동

**📦 산출물**
```python
class TripResponse(BaseModel):
    id: str
    user_id: str
    title: str
    destination: str
    purpose: list[str]
    # ...

class TripCreateRequest(BaseModel):
    title: str
    destination: str
    purpose: list[str]
    # ...
```

**🎯 목적**
- JWT 토큰 검증 및 사용자 식별
- 보호된 API 엔드포인트 접근 제어
- Authorization 헤더에서 토큰 추출 및 검증

**💡 이유**
- 모든 보호된 라우트에서 사용자 ID 필요
- 인증 실패 시 자동 401 응답
- A개발자와 독립적으로 구현 가능 (Mock 우선)

**📦 주요 기능**
- `get_current_user_id()`: 필수 인증 (헤더 없으면 401)
- `get_optional_user_id()`: 선택적 인증 (헤더 없으면 None)
- Mock 구현: 항상 "dev-user-id" 반환 (개발용)

**🔄 TODO: 프로덕션에서 JWKS 연동**
- JWKS 키 서버에서 공개 키 조회
- JWT 서명 검증
- 토큰 만료 확인
- 실제 user_id 추출

**📦 산출물**
```python
async def get_current_user_id(
    authorization: str | None = Header(None)
) -> str:
    if not authorization:
        raise HTTPException(status_code=401, ...)
    return "dev-user-id"  # Mock
```

---

## ⏸️ 대기 중인 작업 (A개발자 완료 필요)

- Trip ORM 모델
- Repository 구현
- 서비스 연결

---

## 📊 진행률

| 단계 | 상태 | 완료율 |
|------|------|--------|
| 1단계: 인프라 기반 | ✅ 완료 | 100% |
| 2단계: 인증 구현 | ✅ 완료 | 100% |
| 3단계: API 스키마 | ✅ 완료 | 100% |
| 4단계: API 라우터 | ⏳ 대기 | 0% |
| **전체** | - | **75%** |

---

*마지막 업데이트: 2026-07-21*