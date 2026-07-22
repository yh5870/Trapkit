# A개발자 작업 요약

## 📅 날짜
2026-07-21 (월)

---

## ✅ 완료된 작업 (Week 1 - 기반 인프라 + 트립 조회)

### 1. 도메인 엔티티 구현

#### Trip 엔티티 (`app/domain/models/trip.py`)

**🎯 목적**
- 여행(Trip)의 비즈니스 도메인 모델 정의
- 불변 엔티티 패턴 구현으로 데이터 일관성 보장
- 도메인 로직 캡슐화

**💡 이유**
- B개발자가 ORM 모델을 구현할 때 참조 가능한 명확한 인터페이스 제공
- 비즈니스 규칙(도메인 로직)을 인프라 레이어와 분리
- 클린 아키텍처 원칙에 따른 도메인 모델 독립성 확보

**📦 주요 기능**
- `Trip.create()`: 새로운 Trip 생성 (id 자동 생성, 생성/수정 시간 관리)
- `Trip.update()`: 불변 객체 패턴으로 업데이트 (새 인스턴스 반환)
- `add_caution()`: 주의사항 추가
- `update_baggage_summary()`: 수화물 요약 업데이트

**📦 산출물**
```python
@dataclass(frozen=True)
class Trip:
    id: TripId
    title: str
    destination: str
    purpose: list[str]
    user_id: str
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None
    cautions: list[dict] = field(default_factory=list)
    baggage_summary: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
```

---

### 2. Value Object 구현

#### TripId (`app/domain/value_objects/trip_id.py`)

**🎯 목적**
- UUID 기반의 Trip 식별자 값 객체 정의
- 원시 타입(문자열) 대신 도메인에 의미 있는 타입 사용

**💡 이유**
- 타입 안정성 확보 (문자열 혼용 방지)
- 비즈니스 로직에서 ID 검증/변환 로직 캡슐화
- 도메인 모델의 명확성 향상

**📦 주요 기능**
- `TripId.from_string()`: 문자열로부터 TripId 생성
- `__str__()`: 문자열로 변환 (UI/API 응답용)

**📦 산출물**
```python
@dataclass(frozen=True)
class TripId:
    value: UUID
```

---

### 3. Repository 인터페이스 정의

#### TripRepository (`app/domain/repositories/trip_repository.py`)

**🎯 목적**
- Trip 저장소의 추상 인터페이스 정의
- B개발자가 구현해야 할 명확한 계약서 제공

**💡 이유**
- 도메인 레이어가 인프라 레이어(DB)에 의존하지 않도록 분리
- 단위 테스트 시 Mock 생성 가능
- 인프라 구현 교체 용이성 확보

**📦 주요 기능**
- `save()`: Trip 저장
- `find_by_id()`: ID로 Trip 조회
- `find_by_user_id()`: 사용자 ID로 모든 Trip 조회
- `delete()`: Trip 삭제

**📦 산출물**
```python
class TripRepository(ABC):
    @abstractmethod
    async def save(self, trip: Trip) -> Trip: ...

    @abstractmethod
    async def find_by_id(self, trip_id: TripId) -> Trip | None: ...

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[Trip]: ...

    @abstractmethod
    async def delete(self, trip_id: TripId) -> None: ...
```

---

### 4. Application Service 구현

#### TripQueryService (`app/application/services/trip_query_service.py`)

**🎯 목적**
- Trip 조회 유스케이스를 담당하는 애플리케이션 서비스
- B개발자의 API 라우터에서 호출 가능한 인터페이스 제공

**💡 이유**
- 도메인 모델과 외부(API) 간의 중개 계층
- 복잡한 조회 로직의 집중 관리
- CQRS 패턴의 Query 측면 구현

**📦 주요 기능**
- `get_user_trips()`: 사용자의 모든 Trip 조회
- `get_trip_by_id()`: ID로 Trip 조회 (문자열 ID 자동 변환)

**📦 산출물**
```python
class TripQueryService:
    def __init__(self, trip_repository: TripRepository): ...

    async def get_user_trips(self, user_id: str) -> list[Trip]: ...

    async def get_trip_by_id(self, trip_id: str) -> Trip | None: ...
```

---

## 📊 Week 1 진행률

| 작업 | 상태 | Week 1 투두 |
|------|------|-----------|
| `domain/models/trip.py` 작성 | ✅ | [x] A: `domain/models/trip.py` 작성 |
| `domain/repositories/trip_repository.py` 작성 | ✅ | [x] A: `domain/repositories/trip_repository.py` 작성 |
| `application/services/trip_query_service.py` 작성 | ✅ | [x] A: `application/services/trip_query_service.py` 작성 |
| `GET /api/trips` 스펙 정의 | ⏳ | [ ] A: `GET /api/trips` 스펙 정의 |

---

## 🔄 B개발자 의존 사항

### B개발자가 구현해야 할 작업

| 작업 | 파일 | 의존 | 현재 상태 |
|------|------|------|----------|
| Trip ORM 모델 | `infrastructure/database/models/trip_model.py` | `domain/models/trip.py` | ⏳ |
| Repository 구현 | `infrastructure/database/repositories/sqlalchemy_trip_repository.py` | `domain/repositories/trip_repository.py` | ⏳ |
| Repository DI | `interfaces/api/dependencies/repositories.py` | 위 2개 파일 | ⏳ |
| Trip 라우터 | `interfaces/api/v1/routes/trips.py` | `application/services/trip_query_service.py` | ⏳ |

---

### ⚠️ B개발자 주의사항 (2026-07-22)

#### Base 클래스 import 방법

ORM 모델 생성 시 `shared/config/database.py`에서 `Base`를 import하세요:

```python
# ✅ 올바른 사용
from shared.config.database import Base

class TripModel(Base):
    __tablename__ = "trips"
    ...

# ❌ 사용 금지 (파일 삭제됨)
from infrastructure.database.base import Base  # ❌
```

**이유**: `declarative_base()` 방식이 아닌 최신 `DeclarativeBase` 사용, 공용 설정(`shared/config/`) 통일

---

## 📝 비고

- B개발자가 ORM 모델과 Repository를 구현하면 통합 테스트 가능
- `Trip` 엔티티의 `frozen=True` 속성으로 불변성 보장 (이는 디자인 의도)
- `TripId`는 UUID 사용으로 추론 불가능한 ID 생성 (보안)
- `TripQueryService`는 추후 캐싱 로직 추가 가능 (성능 최적화)

---

## 🔄 2026-07-22 수정 사항

### 1. 데이터 타입 일치 (`baggage_summary`)

**문제**: 도메인 모델과 API 스키마 간 데이터 타입 불일치

**수정 전**:
```python
baggage_summary: dict = field(default_factory=dict)
```

**수정 후**:
```python
baggage_summary: list[dict] = field(default_factory=list)
```

**이유**: B개발자가 작성한 `TripResponse` 스키마(`list[dict]`)와 일치시키기 위해 수정

**영향**:
- `update_baggage_summary()` 메서드 시그니처도 함께 수정 (`summary: dict` → `summary: list[dict]`)

---

### 2. Base 클래스 중복 해결

**문제**: 두 곳에서 서로 다른 방식으로 `Base` 클래스 정의

| 파일 | 방식 | 상태 |
|------|------|------|
| `infrastructure/database/base.py` | `declarative_base()` (레거시) | ❌ 삭제됨 |
| `shared/config/database.py` | `DeclarativeBase` (최신) | ✅ 유지 |

**조치**: `infrastructure/database/base.py` 파일 삭제

**이유**:
- `DeclarativeBase`는 SQLAlchemy 2.0+의 최신 방식
- `shared/config/`는 공용 설정으로 적합한 위치
- 이미 세션 팩토리/엔진과 같은 파일에 있어 통일성 확보

**B개발자 영향**: ORM 모델 생성 시 `from shared.config.database import Base` 사용 필요

---

*마지막 업데이트: 2026-07-22*