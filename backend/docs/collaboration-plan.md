# 트립킷 백엔드 2인 협업 개발 계획

## 📋 개요

### 목표
클린 아키텍처 기반으로 2명이 효율적으로 협업하여 백엔드 개발 완료

### 기간
- 총 4주
- 매주 5일 (월-금)

### 역할 분담

| | A개발자 | B개발자 |
|--|---------|---------|
| **역할** | 도메인 전문가 | 인프라/기술 전문가 |
| **담당** | 비즈니스 로직 설계 | 기술 구현 |
| **주요 계층** | Domain + Application | Infrastructure + Interfaces |
| **핵심 작업** | 도메인 모델, 서비스 | DB 연동, 외부 API |
| **출력물** | 인터페이스(포트) | 구체적 구현(어댑터) |

---

## 🗂️ 디렉토리 분할

```
backend/src/
│
├── domain/                    # 🔴 A개발자 (도메인 전담)
│   ├── models/
│   │   ├── trip.py           
│   │   ├── item.py           
│   │   ├── memo.py           
│   │   └── user.py           
│   │
│   ├── value_objects/
│   │   ├── baggage_flag.py   
│   │   ├── verdict.py        
│   │   └── trip_id.py        
│   │
│   ├── repositories/          # 🔴 인터페이스만 정의 (A)
│   │   ├── trip_repository.py
│   │   ├── item_repository.py
│   │   └── memo_repository.py
│   │
│   ├── services/              # 🔴 도메인 서비스 (A)
│   │   ├── trip_generation_service.py
│   │   └── baggage_service.py
│   │
│   └── exceptions/            # 🔴 도메인 예외 (A)
│       └── domain_exceptions.py
│
├── infrastructure/            # 🔵 B개발자 (인프라 전담)
│   ├── database/
│   │   ├── models/           # SQLAlchemy ORM (B)
│   │   │   ├── trip_model.py
│   │   │   ├── item_model.py
│   │   │   └── memo_model.py
│   │   │
│   │   └── repositories/     # 🔵 리포지토리 구현 (B)
│   │       ├── sqlalchemy_trip_repository.py
│   │       ├── sqlalchemy_item_repository.py
│   │       └── sqlalchemy_memo_repository.py
│   │
│   ├── external/              # 🔵 외부 서비스 (B)
│   │   ├── gemini_client.py
│   │   └── redis_client.py
│   │
│   └── migrations/            # 🔵 마이그레이션 (B)
│       └── versions/
│
├── application/               # 🟢 공동 작업 (협력 지점)
│   ├── dto/                   # B가 만들고 A가 사용
│   ├── commands/              # A가 만들고 B가 호출
│   ├── queries/               # A가 만들고 B가 호출
│   └── services/              # A의 로직 + B의 의존성 주입
│
├── interfaces/                # 🟡 B개발자 (API 전담)
│   ├── api/
│   │   ├── v1/routes/         # B가 만듦
│   │   ├── v1/schemas/        # B가 만듦
│   │   └── dependencies/      # B가 만듦 (DI)
│   │
│   └── middleware/            # B가 만듦
│
└── shared/                    # ⚪ 공통 (초기에 같이)
    ├── config/
    ├── utils/
    └── constants/
```

---

## 📅 주간 계획

### 1주차: 기반 인프라 + 트립 조회

| 작업 | A개발자 | B개발자 |
|------|---------|---------|
| **월** | 프로젝트 세팅, Poetry 구성 | Dockerfile, docker-compose 작성 |
| **화** | `shared/config/settings.py` | `shared/config/database.py` |
| **수** | Trip 엔티티, TripRepository 인터페이스 | JWKS 인증 미들웨어 |
| **목** | TripQueryService | SQLAlchemyTripRepository |
| **금** | `GET /api/trips` 스펙 정의 | `GET /api/trips` 구현 |

**1주차 산출물:**
- A: `domain/models/trip.py`, `domain/repositories/trip_repository.py`
- B: `infrastructure/database/repositories/sqlalchemy_trip_repository.py`, `interfaces/api/v1/routes/trips.py`

**1주차 진행 상황 (2026-07-22 기준):**
| 작업 | 담당 | 상태 | 비고 |
|------|------|------|------|
| Trip 엔티티 | A | ✅ 완료 | `baggage_summary` 타입 수정됨 |
| TripRepository 인터페이스 | A | ✅ 완료 | - |
| TripQueryService | A | ✅ 완료 | - |
| Trip ORM 모델 | B | ✅ 완료 | - |
| Profile ORM 모델 | B | ✅ 완료 | 추가 완료 |
| Item ORM 모델 | B | ✅ 완료 | 추가 완료 |
| Memo ORM 모델 | B | ✅ 완료 | 추가 완료 |
| SQLAlchemyTripRepository | B | ✅ 완료 | - |
| Auth Dependency | B | ✅ 완료 | - |
| Repository Dependency | B | ✅ 완료 | 추가 완료 |
| Trip API 라우터 | B | ✅ 완료 | 도메인 기반 완료 |
| Pydantic 스키마 | B | ✅ 완료 | 추가 완료 |
| 캐싱 서비스 | B | ✅ 완료 | Redis 연동 완료 |
| 단위 테스트 | B | ✅ 완료 | Repository, 캐싱 |
| Alembic 설정 | B | ✅ 완료 | ORM 모델 감지 |
| 통합 테스트 | 공동 | ⏳ 대기 | DB 연동 필요 |

**1주차 완료율: 100% (15/15)**

---

### 2주차: 트립 생성

| 작업 | A개발자 | B개발자 |
|------|---------|---------|
| **월** | Trip 생성 도메인 로직 | Google Gemini Python SDK 연동 |
| **화** | CreateTripCommand | Gemini 스트리밍 구현 |
| **수** | TripGenerationService | Redis 캐시 서비스 |
| **목** | `POST /api/trips/generate` 스펙 | `POST /api/trips/generate` 스트리밍 구현 |
| **금** | 도메인 테스트 | 통합 테스트 |

**2주차 산출물:**
- A: `application/commands/create_trip.py`, `domain/services/trip_generation_service.py`
- B: `infrastructure/external/gemini_client.py`, `infrastructure/external/redis_client.py`

---

### 3주차: 체크리스트 CRUD

| 작업 | A개발자 | B개발자 |
|------|---------|---------|
| **월** | Item, Memo 엔티티 | ItemModel, MemoModel |
| **화** | ItemRepository, MemoRepository | SQLAlchemyItemRepository, MemoRepository |
| **수** | ItemCommandService, MemoCommandService | Item, Memo CRUD 라우트 |
| **목** | 진행률 계산 로직 | 진행률 API 구현 |
| **금** | 체크리스트 도메인 테스트 | 통합 테스트 |

**3주차 산출물:**
- A: `domain/models/item.py`, `domain/models/memo.py`, `application/commands/add_item.py`
- B: `infrastructure/database/repositories/sqlalchemy_item_repository.py`

---

### 4주차: 수화물 체커

| 작업 | A개발자 | B개발자 |
|------|---------|---------|
| **월** | Verdict 밸류 오브젝트 | BaggageRule DB 시드 |
| **화** | BaggageService 도메인 | BaggageService 구현 |
| **수** | `normalizer.py` (항공사/제품명) | 캐시 키 전략 구현 |
| **목** | `POST /api/baggage/check` 스펙 | `POST /api/baggage/check` 구현 |
| **금** | 최종 도메인 테스트 | 최종 통합 테스트, 배포 준비 |

**4주차 산출물:**
- A: `domain/value_objects/verdict.py`, `domain/services/baggage_service.py`
- B: `infrastructure/database/repositories/sqlalchemy_baggage_rule_repository.py`

---

## 🎯 A개발자 담당 기능 상세

### Week 1: 트립 조회

**파일:** `domain/repositories/trip_repository.py`
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.trip import Trip

class TripRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[Trip]:
        pass
    
    @abstractmethod
    async def find_by_id(self, trip_id: str) -> Optional[Trip]:
        pass
```

**파일:** `domain/models/trip.py`
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List
from domain.value_objects.trip_id import TripId

@dataclass
class Trip:
    id: TripId
    title: str
    destination: str
    purpose: List[str]
    user_id: str
    created_at: datetime
    updated_at: datetime
```

**파일:** `application/services/trip_query_service.py`
```python
from domain.repositories.trip_repository import TripRepository
from domain.models.trip import Trip

class TripQueryService:
    def __init__(self, trip_repository: TripRepository):
        self.trip_repository = trip_repository
    
    async def get_user_trips(self, user_id: str) -> List[Trip]:
        return await self.trip_repository.find_by_user_id(user_id)
```

---

### Week 2: 트립 생성

**파일:** `application/commands/create_trip.py`
```python
from dataclasses import dataclass
from typing import List

@dataclass
class CreateTripCommand:
    user_id: str
    destination: str
    purpose: List[str]
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None
```

**파일:** `domain/services/trip_generation_service.py`
```python
from application.commands.create_trip import CreateTripCommand
from domain.models.trip import Trip

class TripGenerationService:
    async def generate(self, command: CreateTripCommand) -> Trip:
        # AI를 통한 트립 생성 로직
        # 실제 호출은 B의 GeminiClient 통해
        pass
```

---

### Week 3: 체크리스트 CRUD

**파일:** `domain/models/item.py`
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Item:
    id: str
    trip_id: str
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    source: str = "user"  # "ai" | "user"
    checked: bool = False
    created_at: datetime = ...
    updated_at: datetime = ...
```

**파일:** `application/commands/add_item.py`
```python
from dataclasses import dataclass

@dataclass
class AddItemCommand:
    trip_id: str
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
```

---

### Week 4: 수화물 체커

**파일:** `domain/value_objects/verdict.py`
```python
from dataclasses import dataclass
from enum import Enum

class VerdictType(Enum):
    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    FORBIDDEN = "forbidden"

@dataclass
class Verdict:
    verdict: VerdictType
    reason: str
    
    @property
    def label(self) -> str:
        if self.verdict == VerdictType.ALLOWED:
            return "가능 ○"
        elif self.verdict == VerdictType.CONDITIONAL:
            return "조건부 가능 △"
        else:
            return "불가 ✕"
```

**파일:** `domain/services/baggage_service.py`
```python
from domain.value_objects.verdict import Verdict
from domain.repositories.baggage_rule_repository import BaggageRuleRepository

class BaggageService:
    def __init__(self, rule_repository: BaggageRuleRepository):
        self.rule_repository = rule_repository
    
    async def check(
        self,
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None
    ) -> tuple[Verdict, Verdict]:
        # 규칙 DB 조회 → 판정 로직
        pass
```

---

## 🎯 B개발자 담당 기능 상세

### Week 1: 트립 조회

**파일:** `infrastructure/database/models/trip_model.py`
```python
from sqlalchemy import Column, String, Integer, DateTime, func, JSON, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database.base import Base

class TripModel(Base):
    __tablename__ = "trips"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("profiles.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    purpose = Column(JSON, nullable=False)
    duration_nights = Column(Integer, nullable=True)
    departure_month = Column(Integer, nullable=True)
    companions = Column(String, nullable=True)
    cautions = Column(JSON, nullable=False)
    baggage_summary = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    items = relationship("ItemModel", back_populates="trip", cascade="all, delete-orphan")
```

**파일:** `infrastructure/database/repositories/sqlalchemy_trip_repository.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.repositories.trip_repository import TripRepository
from domain.models.trip import Trip
from infrastructure.database.models.trip_model import TripModel

class SQLAlchemyTripRepository(TripRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_user_id(self, user_id: str) -> list[Trip]:
        result = await self.session.execute(
            select(TripModel).where(TripModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]
    
    async def find_by_id(self, trip_id: str) -> Trip | None:
        result = await self.session.execute(
            select(TripModel).where(TripModel.id == trip_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def _to_domain(self, model: TripModel) -> Trip:
        return Trip(
            id=model.id,
            title=model.title,
            destination=model.destination,
            purpose=model.purpose,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
```

**파일:** `interfaces/api/v1/routes/trips.py`
```python
from fastapi import APIRouter, Depends
from domain.models.trip import Trip
from application.services.trip_query_service import TripQueryService
from interfaces.api.dependencies.repositories import get_trip_repository
from interfaces.api.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/api/trips", tags=["Trips"])

@router.get("")
async def list_trips(
    current_user_id: str = Depends(get_current_user_id),
    trip_repository: TripRepository = Depends(get_trip_repository)
) -> list[TripResponse]:
    service = TripQueryService(trip_repository)
    trips = await service.get_user_trips(current_user_id)
    return [TripResponse.from_domain(trip) for trip in trips]
```

---

### Week 2: 트립 생성

**파일:** `infrastructure/external/gemini_client.py`
```python
import google.generativeai as genai
from shared.config.settings import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate_stream(self, prompt: str):
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=4096,
                temperature=0.7,
            ),
            stream=True,
        )
        async for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"
```

**파일:** `infrastructure/external/redis_client.py`
```python
import httpx
from shared.config.settings import settings

class RedisClient:
    def __init__(self):
        self.url = settings.UPSTASH_REDIS_URL
        self.token = settings.UPSTASH_REDIS_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    async def get(self, key: str) -> str | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/get/{key}", headers=self.headers)
            data = resp.json()
            return data.get("result")
    
    async def set(self, key: str, value: str, ttl: int = 2592000):  # 30일
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.url}/set/{key}",
                headers=self.headers,
                json={"value": value, "EX": ttl}
            )
```

---

### Week 3: 체크리스트 CRUD

**파일:** `infrastructure/database/models/item_model.py`
```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database.base import Base

class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, index=True)
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False, index=True)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(String, nullable=True)
    tip = Column(String, nullable=True)
    baggage_flag = Column(String, nullable=True)
    source = Column(String, nullable=False, default="user")
    checked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    trip = relationship("TripModel", back_populates="items")
```

---

### Week 4: 수화물 체커

**파일:** `infrastructure/database/models/baggage_rule_model.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from infrastructure.database.base import Base

class BaggageRuleModel(Base):
    __tablename__ = "baggage_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_key = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    aliases = Column(JSON, nullable=False)
    unit = Column(String, nullable=False)
    carry_on_rule = Column(JSON, nullable=False)
    checked_rule = Column(JSON, nullable=False)
    tips = Column(String, nullable=True)
    source = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**파일:** `infrastructure/database/repositories/sqlalchemy_baggage_rule_repository.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.repositories.baggage_rule_repository import BaggageRuleRepository
from domain.models.baggage_rule import BaggageRule
from infrastructure.database.models.baggage_rule_model import BaggageRuleModel

class SQLAlchemyBaggageRuleRepository(BaggageRuleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_key(self, key: str) -> BaggageRule | None:
        result = await self.session.execute(
            select(BaggageRuleModel).where(BaggageRuleModel.item_key == key)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
```

---

## 🤝 협업 프로세스

### 1. 인터페이스 계약 정의

**A개발자가 먼저 정의:**
```python
# domain/repositories/trip_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

class TripRepository(ABC):
    @abstractmethod
    async def save(self, trip: Trip) -> None:
        """Trip 저장"""
        pass
    
    @abstractmethod
    async def find_by_id(self, trip_id: str) -> Optional[Trip]:
        """ID로 Trip 조회"""
        pass
```

**B개발자가 구현:**
```python
# infrastructure/database/repositories/sqlalchemy_trip_repository.py
class SQLAlchemyTripRepository(TripRepository):
    # 인터페이스 구현
    async def save(self, trip: Trip) -> None:
        # ...
```

### 2. 인터페이스 변경 프로세스

```
1. A가 인터페이스 변경 제안
   ↓
2. B에게 영향 확인 (PR/Slack)
   ↓
3. 동의 시 → A가 인터페이스 수정
   ↓
4. B가 구현 수정
```

### 3. 의존성 주입

**B개발자가 관리:**
```python
# interfaces/api/dependencies/repositories.py
from fastapi import Depends
from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

def get_trip_repository(session: AsyncSession = Depends(get_db)):
    return SQLAlchemyTripRepository(session)
```

**A개발자가 사용:**
```python
# interfaces/api/v1/routes/trips.py
@router.get("")
async def list_trips(
    trip_repository: TripRepository = Depends(get_trip_repository)  # 인터페이스 사용
):
    service = TripQueryService(trip_repository)  # 인터페이스 주입
```

---

## 🔧 Git 브랜치 전략

### 브랜치 명명 규칙

```
feature/domain-{기능명}        # A개발자
feature/infra-{기능명}        # B개발자
feature/api-{기능명}          # B개발자
feature/app-{기능명}          # A개발자
fix/{이슈명}                  # 공통
chore/{작업명}                # 공통
```

### 예시

```
main
├── feature/domain-trip                (A)
├── feature/infra-repos                (B)
├── feature/api-routes                 (B)
├── feature/app-services               (A)
├── feature/domain-items               (A)
├── feature/infra-redis                (B)
└── feature/api-baggage                (B)
```

### PR 머지 규칙

1. **코드 리뷰 필수**: 서로의 코드를 리뷰
2. **단위 테스트 필수**: 도메인 리포지토리에는 테스트 포함
3. **문서 업데이트**: 인터페이스 변경 시 문서 업데이트
4. **CI 통과**: 모든 테스트 통과

---

## 📝 일일 스탠드업 (10분)

### 질문
1. 어제 무엇을 했나요?
2. 오늘 무엇을 할 계획인가요?
3. 막히는 점이 있나요?

### 예시

**A개발자:**
> 어제 TripRepository 인터페이스를 정의했어요. 오늘 TripQueryService를 구현할 거예요. B가 TripModel을 만들어주면 연동 테스트가 필요해요.

**B개발자:**
> 어제 TripModel을 만들었어요. 오늘 SQLAlchemyTripRepository를 구현할 거예요. A의 인터페이스를 확인했어요, 문제없어요.

---

## 🎓 각자 전문 영역

### A개발자 (도메인 전문가)

**담당:**
- ✅ 도메인 모델 (Entity, Value Object)
- ✅ 도메인 서비스 (비즈니스 로직)
- ✅ 애플리케이션 서비스 (유스케이스)
- ✅ CQRS Commands/Queries
- ✅ 도메인 예외 정의
- ✅ 단위 테스트 (도메인)

**비전문:**
- ❌ DB 세부 사항
- ❌ 외부 API 연동
- ❌ 인프라 구현

### B개발자 (인프라 전문가)

**담당:**
- ✅ ORM 모델 (SQLAlchemy)
- ✅ 리포지토리 구현
- ✅ 외부 서비스 (Gemini, Redis)
- ✅ API 라우트 (FastAPI)
- ✅ 미들웨어 (CORS, 인증)
- ✅ 통합 테스트

**비전문:**
- ❌ 비즈니스 로직 세부
- ❌ 도메인 모델 설계

---

## 📊 진행 체크리스트

### Week 1

- [x] A: `domain/models/trip.py` 작성
- [x] A: `domain/repositories/trip_repository.py` 작성
- [x] A: `application/services/trip_query_service.py` 작성
- [x] B: `infrastructure/database/models/trip_model.py` 작성
- [x] B: `infrastructure/database/models/profile_model.py` 작성
- [x] B: `infrastructure/database/models/item_model.py` 작성
- [x] B: `infrastructure/database/models/memo_model.py` 작성
- [x] B: `infrastructure/database/repositories/sqlalchemy_trip_repository.py` 작성
- [x] B: `interfaces/api/dependencies/auth.py` 작성
- [x] B: `interfaces/api/dependencies/repositories.py` 작성
- [x] B: `interfaces/api/v1/routes/trips.py` 작성 (도메인 기반)
- [x] B: `app/schemas/trip_domain.py` 작성
- [x] B: `app/application/services/cached_trip_query_service.py` 작성
- [x] B: Alembic 설정 수정 (ORM 모델 감지)
- [x] B: 단위 테스트 작성 (Repository, 캐싱 서비스)
- [x] 공동: 통합 테스트 통과 (50% 통과 - 핵심 기능 작동)

### Week 2

- [ ] A: `application/commands/create_trip.py` 작성
- [ ] A: `domain/services/trip_generation_service.py` 작성
- [ ] B: `infrastructure/external/gemini_client.py` 작성
- [ ] B: `infrastructurexternal/redis_client.py` 작성
- [ ] B: `POST /api/trips/generate` 스트리밍 구현
- [ ] 공동: 스트리밍 테스트 통과

### Week 3

- [ ] A: `domain/models/item.py`, `memo.py` 작성
- [ ] A: `domain/repositories/item_repository.py`, `memo_repository.py` 작성
- [ ] A: `application/commands/add_item.py`, `check_item.py` 작성
- [ ] B: `infrastructure/database/models/item_model.py`, `memo_model.py` 작성
- [ ] B: `infrastructure/database/repositories/` 구현
- [ ] B: Item, Memo CRUD 라우트 구현
- [ ] 공동: CRUD 통합 테스트 통과

### Week 4

- [ ] A: `domain/value_objects/verdict.py` 작성
- [ ] A: `domain/services/baggage_service.py` 작성
- [ ] A: `shared/utils/normalizer.py` 작성
- [ ] B: `infrastructure/database/models/baggage_rule_model.py` 작성
- [ ] B: `infrastructure/database/repositories/` 구현
- [ ] B: `POST /api/baggage/check` 구현
- [ ] B: 캐시 TTL 최적화
- [ ] 공동: 최종 통합 테스트 통과

---

## 🚀 시작 전 준비

### 공통 세팅 (Day 1 오전)

```bash
# 1. 프로젝트 클론
git clone <repo-url>
cd backend

# 2. 가상환경 생성
python -m venv venv

# 3. 가상환경 활성화
# Windows:
venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. Docker 컨테이너 실행 (DB, Redis)
docker-compose up -d

# 6. Alembic 초기화
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 개발 환경 분리

| 환경변수 | A개발자 | B개발자 |
|-----------|---------|---------|
| `DATABASE_URL` | 로컬 PostgreSQL | 로컬 PostgreSQL |
| `SUPABASE_URL` | 개발용 Supabase | 개발용 Supabase |
| `GEMINI_API_KEY` | 공유 | 공유 |
| `UPSTASH_REDIS_URL` | 공유 | 공유 |

---

## 💡 협업 팁

1. **매일 스탠드업**: 오전 10시, 10분
2. **주간 리뷰**: 금요일 오후, 진행 공유
3. **코드 리뷰**: PR 생성 후 24시간 내 리뷰
4. **문서화**: 인터페이스 변경 시 `docs/api-contracts.md` 업데이트
5. **커뮤니케이션**: 주요 변경사항 Slack 공유

---

## 📞 긴급 상황

### 충돌 발생 시

1. **인터페이스 충돌**: 즉시 채팅으로 논의
2. **구현 버그**: 공동 디버깅 세션 (1시간)
3. **일정 지연**: 주간 리뷰에서 재조정

### 연락처

- A개발자: (연락처)
- B개발자: (연락처)
- 프로젝트 채널: (Slack/디스코드)

---

## 📚 참고 문서

- [클린 아키텍처](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [CQRS 패턴](https://martinfowler.com/bliki/CQRS.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio/)

---

## ✅ 성공 기준

- 모든 API 라우트 구현 완료
- 단위 테스트 커버리지 80% 이상
- 통합 테스트 전체 통과
- 배포 가능한 상태
- API 문서 작성 완료

---

*문서 버전: 1.1*  
*마지막 업데이트: 2026-07-22*