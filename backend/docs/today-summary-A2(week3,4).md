# A개자 작업 요약 (Week 2, 3, 4)

## 📅 날짜
2026-07-22 (화) ~ (Week 2, 3, 4 작업 진행)

---

## 🎯 Week 2 완료된 작업

### 1. Trip 생성 Command 구현

#### `application/commands/create_trip.py`

**🎯 목적**
- Trip 생성 유스케이스를 위한 Command 패턴 구현
- CQRS 패턴의 Command 측면 담당

**💡 이유**
- B개발자가 스트리밍 API 구현 시 사용
- 도메인 로직과 인프라 레이어 분리
- 의존성 주입으로 테스트 용이

**📦 구현 내용**
```python
@dataclass(frozen=True)
class CreateTripCommand:
    user_id: str
    title: str
    destination: str
    purpose: list[str]
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None
```

---

### 2. Trip 생성 도메인 서비스 구현

#### `domain/services/trip_generation_service.py`

**🎯 목적**
- AI를 통한 트립 생성 유스케이스를 담당
- TripRepository와 AIClient를 통합

**💡 이유**
- 비즈니스 로직 캡슐화
- AIClient 인터페이스로 B개자의 구현과 분리
- 도메인 모델 독립성 유지

**📦 구현 내용**
```python
class TripGenerationService:
    def __init__(self, trip_repository: TripRepository, ai_client: AIClient) -> None:
        ...

    async def generate(self, command: CreateTripCommand) -> Trip:
        # 1. AI로부터 트립 콘텐츠 생성
        ai_content = await self.ai_client.generate_trip_content(command)
        
        # 2. Trip 엔티티 생성
        trip = Trip.create(
            title=command.title,
            destination=command.destination,
            purpose=command.purpose,
            user_id=command.user_id,
            duration_nights=command.duration_nights,
            departure_month=command.departure_month,
            companions=command.companions,
            cautions=ai_content.get("cautions", []),
            baggage_summary=ai_content.get("baggage_summary", []),
        )
        
        # 3. Repository에 저장
        return await self.trip_repository.save(trip)

    # 캐시 무효화 (Trip 생성/수정/삭제 시 호출)
    async def invalidate_trip_cache(self, trip_id: TripId) -> None:
        if self.trip_repository.supports_caching():
            await self.trip_repository.invalidate_trip_cache(trip_id)
```

---

### 3. AIClient 인터페이스 정의

**파일**: `domain/services/ai_client.py`

**🎯 목적**
- B개자가 구현할 AI 클라이언트의 인터페이스 정의
- 표준화된 메서드 시그니처 제공

**📦 인터페이스**
```python
class AIClient(ABC):
    @abstractmethod
    async def generate_trip_content(self, command: CreateTripCommand) -> dict:
        """AI로부터 트립 콘텐츠 생성.
        
        Returns:
            {
                "cautions": list[dict],
                "baggage_summary": list[dict]
            }
        """
```

**💡 이유**
- B개자가 협업 계획의 "Google Gemini" → "Anthropic" 변경에 대응
- 명확한 메서드 시그니처로 B개자와 협업 방식 확정

---

## ✅ Week 2 진행률

| 작업 | 담당 | 상태 | 비고 |
|------|------|------|------|
| `application/commands/create_trip.py` | A | ✅ 완료 | CQRS Command 패턴 |
| `domain/services/trip_generation_service.py` | A | ✅ 완료 | 도메인 서비스 |
| `domain/services/ai_client.py` | A | ✅ 정의 | 인터페이스 정의 |
| `infrastructure/external/gemini_client.py` | B | ⏳ 미완료 | A가 정의한 인터페이스 구현 필요 |
| `infrastructure/external/redis_client.py` | B | ⏳ 미완료 | 캐시 서비스 구현 필요 |
| `POST /api/trips/generate` | B | ⏳ 미완료 | 스트리밍 API 구현 필요 |
| 도메인 테스트 | A | ⏳ 미완료 | Week 3 작업 선행 중 |
| 스트리밍 테스트 | 공동 | ⏳ 미완료 | Week 2 완료 후 |

**Week 2 완료율**: 50% (A개발자 100%, B개발자 0%)

---

## 🟡 Week 3 진행 중 (선행 작업)

### 1. Item 엔티티 구현 ✅

#### `app/domain/models/item.py`

**🎯 목적**
- 여행에 필요한 짐 항목 엔티티 정의
- 불변 엔티티 패턴 구현으로 데이터 일관성 보장
- B개발자의 ItemModel과 동기화

**💡 이유**
- B개자가 이미 ItemModel을 구현 완료 (확인됨)
- A개발자가 도메인 로직 정의할 수 있도록 구조 확정
- 체크리스트 진행 상황 추적 가능

**📦 주요 기능**
- `create()`: 새 Item 생성 (자동 ID, 정렬 순서=0)
- `check()`: 체크박스 완료
- `uncheck()`: 체크박스 취소
- `sort_order_up()`: 정렬 순서 변경
- `update_source()`: 소스를 AI로 변경
- `update_baggage_flag()`: 수화물 규정 플래그 변경
- 불변 패턴: 업데이트 시 새 인스턴스 반환

**주요 필드**:
```python
baggage_flag: str | None  # "carry_on_only" | "checked_only" | "restricted" | null
source: str = "user"  # "ai" | "user"
checked: bool = False  # 체크박스 완료 여부
sort_order: int = 0  # 정렬 순서 (오름차순)
```

---

### 2. Memo 엔티티 구현 ✅

#### `app/domain/models/memo.py`

**🎯 목적**
- 여행에 관한 메모/기록 엔티티 정의
- 불변 엔티티 패턴 구현
- 최대 2,000자 길이 제한 검증

**💡 이유**
- B개발자가 이미 MemoModel을 구현 완료 (확인됨)
- 도메인 로직 정의할 수 있도록 구조 확정

**📦 주요 기능**
- `create()`: 새 Memo 생성 (자동 ID, 길이 검증)
- `update_content()`: 메모 내용 업데이트 (2,000자 제한)
- 불변 패턴: 업데이트 시 새 인스턴스 반환

---

### 3. ItemId, MemoId 값 객체 구현 ✅

#### `app/domain/value_objects/item_id.py`
#### `app/domain/value_objects/memo_id.py`

**🎯 목적**
- UUID 기반의 식별자 값 객체 정의
- 원시 타입(문자열) 대신 도메인에 의미 있는 타입 사용

**💡 이유**
- 타입 안정성 확보 (문자열 혼용 방지)
- 비즈니스 로직에서 ID 검증/변환 로직 캡슐화

---

### 4. ItemRepository 인터페이스 구현 ✅

#### `app/domain/repositories/item_repository.py`

**🎯 목적**
- Item 저장소의 추상 인터페이스 정의
- B개발자가 구현해야 할 명확한 계약서 제공

**💡 이유**
- 도메인 레이어가 인프라 레이어(DB)에 의존하지 않도록 분리
- 단위 테스트 시 Mock 생성 가능
- 인프라 구현 교체 용이성 확보

**📦 구현 메서드**
```python
class ItemRepository(ABC):
    async def save(self, item: Item) -> Item:
        """Item 저장."""
        
    async def find_by_id(self, item_id: ItemId) -> Item | None:
        """ID로 Item 조회."""
        
    async def find_by_trip_id(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (생성일 내림차순)."""
        
    async def find_by_trip_id_sorted(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (sort_order 오름차순)."""
        
    async def find_by_category(self, trip_id: TripId, category: str) -> list[Item]:
        """Trip ID와 카테고리로 Item 조회."""
        
    async def delete(self, item_id: ItemId) -> None:
        """Item 삭제."""
        
    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Item 삭제 (Trip 삭제 시)."""
        
    async def get_checked_count(self, trip_id: TripId) -> int:
        """Trip ID로 완료된 Item 수 조회."""
        
    async def get_total_count(self, trip_id: TripId) -> int:
        """Trip ID로 전체 Item 수 조회."""
        
    async def update_sort_order(self, item_id: ItemId, new_order: int) -> None:
        """Item 정렬 순서 업데이트."""
```

**특징**
- CRUD 기본 작업
- Trip ID 기반 조회 (다중 항목)
- 카테고리 필터링
- 정렬 순서 업데이트
- 통계 기능 (완료/전체 수)

---

### 5. MemoRepository 인터페이스 구현 ✅

#### `app/domain/repositories/memo_repository.py`

**🎯 목적**
- Memo 저장소의 추상 인터페이스 정의
- B개발자가 구현해야 할 명확한 계약서 제공

**💡 이유**
- 도메인 레이어가 인프라 레이어(DB)에 의존하지 않도록 분리
- 단위 테스트 시 Mock 생성 가능
- 인프라 구현 교체 용이성 확보

**📦 구현 메서드**
```python
class MemoRepository(ABC):
    async def save(self, memo: Memo) -> Memo:
        """Memo 저장."""
        
    async def find_by_id(self, memo_id: MemoId) -> Memo | None:
        """ID로 Memo 조회."""
        
    async def find_by_trip_id(self, trip_id: TripId) -> list[Memo]:
        """Trip ID로 모든 Memo 조회 (생성일 내림차순)."""
        
    async def delete(self, memo_id: MemoId) -> None:
        """Memo 삭제."""
        
    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Memo 삭제 (Trip 삭제 시)."""
        
    async def get_count(self, trip_id: TripId) -> int:
        """Trip ID로 Memo 수 조회."""
```

**특징**
- CRUD 기본 작업
- Trip ID 기반 조회 (다중 메모)
- Trip 삭제 시 자동 정리

---

---

## ⏳ Week 3 대기 작업

| 작업 | 담당 | 상태 | 의존 |
|------|------|------|------|
| ItemRepository 인터페이스 정의 | A | ✅ 완료 | 도메인 모델 완료 |
| MemoRepository 인터페이스 정의 | A | ✅ 완료 | 도메인 모델 완료 |
| AddItemCommand 구현 | A | ✅ 완료 | 도메인 모델 참조 |
| CheckItemCommand 구현 | A | ✅ 완료 | 도메인 모델 참조 |
| ItemCommandService 구현 | A | ⏳ | Repository 필요 |
| MemoCommandService 구현 | A | ⏳ | Repository 필요 |
| 진행률 계산 로직 | A | ⏳ | 도메인 로직 |
| Item CRUD 라우트 구현 | B | ⏳ | A의 인터페이스 필요 |
| 통합 테스트 | 공동 | ⏳ | 완료 필요 |

---

### 6. Item 관련 Command 구현 ✅

#### `app/application/commands/item_commands.py`

**🎯 목적**
- Item CRUD 작업을 위한 Command 패턴 구현
- CQRS 패턴의 Command 측면 담당
- B개발자가 API 라우트에서 사용

**💡 이유**
- B개발자가 Item CRUD 라우트 구현 시 사용
- 불변 Command 객체로 데이터 일관성 보장
- 의존성 주입으로 테스트 용이

**📦 구현된 Commands**
```python
@dataclass(frozen=True)
class AddItemCommand:
    """Item 추가 Command."""
    trip_id: str
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    source: str = "user"  # "ai" | "user"


@dataclass(frozen=True)
class CheckItemCommand:
    """Item 체크/언체크 Command."""
    item_id: str
    checked: bool


@dataclass(frozen=True)
class UpdateItemCommand:
    """Item 수정 Command."""
    item_id: str
    name: str | None = None
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    checked: bool | None = None


@dataclass(frozen=True)
class DeleteItemCommand:
    """Item 삭제 Command."""
    item_id: str


@dataclass(frozen=True)
class UpdateSortOrderCommand:
    """Item 정렬 순서 변경 Command."""
    item_id: str
    new_order: int
```

**특징**
- 불변 Command 객체 (`frozen=True`)
- 선택적 필드 지원 (`str | None`)
- 모든 CRUD 작업에 해당 Command 제공
- 정렬 순서 변경 Command 별도 정의

---

### 7. Memo 관련 Command 구현 ✅

#### `app/application/commands/memo_commands.py`

**🎯 목적**
- Memo CRUD 작업을 위한 Command 패턴 구현
- B개발자가 API 라우트에서 사용

**💡 이유**
- B개발자가 Memo CRUD 라우트 구현 시 사용
- 불변 Command 객체로 데이터 일관성 보장
- 도메인 로직(2,000자 제한)에서 Command 구분

**📦 구현된 Commands**
```python
@dataclass(frozen=True)
class AddMemoCommand:
    """Memo 추가 Command."""
    trip_id: str
    content: str  # 최대 2,000자


@dataclass(frozen=True)
class UpdateMemoCommand:
    """Memo 수정 Command."""
    memo_id: str
    content: str  # 최대 2,000자


@dataclass(frozen=True)
class DeleteMemoCommand:
    """Memo 삭제 Command."""
    memo_id: str
```

**특징**
- 불변 Command 객체
- 최소한의 CRUD 작업 Command
- 도메인 엔티티에서 길이 검증 수행

---

## ⏳ Week 3 대기 작업 (업데이트)

| 작업 | 담당 | 상태 | 의존 |
|------|------|------|------|
| ItemRepository 인터페이스 정의 | A | ✅ 완료 | 도메인 모델 완료 |
| MemoRepository 인터페이스 정의 | A | ✅ 완료 | 도메인 모델 완료 |
| AddItemCommand 구현 | A | ⏳ | 도메인 모델 참조 |
| CheckItemCommand 구현 | A | ⏳ | 도메인 모델 참조 |
| ItemCommandService 구현 | A | ⏳ | Repository 필요 |
| MemoCommandService 구현 | A | ⏳ | Repository 필요 |
| 진행률 계산 로직 | A | ⏳ | 도메인 로직 |
| Item CRUD 라우트 구현 | B | ⏳ | A의 인터페이스 필요 |
| 통합 테스트 | 공동 | ⏳ | 완료 필요 |

---

## ⏳ Week 4 대기 작업 (미시작)

| 작업 | 담당 | 상태 | 비고 |
|------|------|------|------|
| Verdict 값 객체 정의 | A | ⏳ | Week 3 진행 후 |
| BaggageService 도메인 구현 | A | ⏳ | Week 3 진행 후 |
| normalizer.py 구현 | A | ⏳ | Week 3 진행 후 |
| BaggageRuleRepository 인터페이스 정의 | A | ⏳ | Week 3 진행 후 |
| POST /api/baggage/check 구현 | B | ⏳ | A의 인터페이스 필요 |
| 캐시 TTL 최적화 | B | ⏳ | 캐싱 서비스 완료 |

---

## 🔄 B개발자 의존 사항

### Week 2 작업 (미시작)

| 작업 | 파일 | 의존 | 현재 상태 |
|------|------|------|----------|
| Gemini Client | `infrastructure/external/gemini_client.py` | `AIClient` 인터페이스 | ⏳ 대기 |
| Redis Client | `infrastructure/external/redis_client.py` | 캐싱 서비스 연동 | ⏳ 대기 |
| 스트리밍 API | `POST /api/trips/generate` | TripGenerationService 사용 | ⏳ 대기 |
| AI 콘텐츠 생성 로직 | A가 정의한 인터페이스 | ✅ 정의 |

---

### Week 3 작업 (미시작)

| 작업 | 파일 | 의존 | 현재 상태 |
|------|------|------|----------|
| Item Repository 구현 | `infrastructure/database/repositories/sqlalchemy_item_repository.py` | ItemRepository 인터페이스 | ⏳ 대기 |
| Item CRUD 라우트 구현 | `interfaces/api/v1/routes/items.py` | 도메인 모델/Repository 필요 | ⏳ 대기 |
| Memo Repository 구현 | `infrastructure/database/repositories/sqlalchemy_memo_repository.py` | MemoRepository 인터페이스 | ⏳ 대기 |
| Memo CRUD 라우트 구현 | `interfaces/api/v1/routes/memos.py` | 도메인 모델/Repository 필요 | ⏳ 대기 |

---

## 💡 A개발자를 위한 권장 작업

### 🔴 현재 작업 (당장 가능)

1. **통합 테스트 실행**
   - Repository 기능 검증
   - 도메인 모델 검증
   - Service 연동 검증

2. **API 스펙 문서 생성**
   - `/api/items` 엔드포인트 스펙
   - `/api/memos` 엔드포인트 스펙
   - Request/Response 예시

3. **단위 테스트 작성**
   - 도메인 엔티티 테스트
   - Command/Service 테스트
   - Repository Mock 사용

---

## 📊 전체 진행률

| 주차 | A개발자 | B개발자 | 전체 |
|------|-----------|----------|------|
| **Week 1** | ✅ 100% | ✅ 100% | **100%** |
| **Week 2** | ✅ 100% | ⏳ 0% | **50%** |
| **Week 3** | 🟡 25% | ✅ 100% | **62.5%** |
| **Week 4** | ⏳ 0% | ⏳ 0% | **12.5%** |

---

## 🎉 Week 3 작업 가이드

B개자가 이미 구현한 ORM 모델(ItemModel, MemoModel)이 있으므로, A개자가 도메인 로직과 인터페이스만 집중하면 유기하게 Week 3 작업을 완료할 수 있습니다.

---

*마지막 업데이트: 2026-07-22*