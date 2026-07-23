# A개발자 작업 요약 (Week 1~3)

## 📅 날짜
2026-07-21 (월) ~ 2026-07-22 (화)

---

## 🎯 전체 완료율

| 주차 | A개발자 | B개발자 | 전체 | 상태 |
|------|---------|---------|------|------|
| **Week 1** | ✅ 100% | ✅ 100% | **100%** | 완료 |
| **Week 2** | ✅ 100% | ✅ 100% | **100%** | 완료 |
| **Week 3** | ✅ 100% | ✅ 100% | **100%** | 완료 (버그 수정 포함) |
| **Week 4** | ⏳ 0% | ⏳ 0% | **0%** | 예정 |

---

## ✅ Week 1 완료된 작업 (기반 인프라 + 트립 조회)

### 1. Trip 엔티티 구현

#### `app/domain/models/trip.py`

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

---

### 2. TripId 값 객체 구현

#### `app/domain/value_objects/trip_id.py`

**🎯 목적**
- UUID 기반의 Trip 식별자 값 객체 정의
- 원시 타입(문자열) 대신 도메인에 의미 있는 타입 사용

**💡 이유**
- 타입 안정성 확보 (문자열 혼용 방지)
- 비즈니스 로직에서 ID 검증/변환 로직 캡슐화
- 도메인 모델의 명확성 향상

---

### 3. TripRepository 인터페이스 정의

#### `app/domain/repositories/trip_repository.py`

**🎯 목적**
- Trip 저장소의 추상 인터페이스 정의
- B개발자가 구현해야 할 명확한 계약서 제공

**💡 이유**
- 도메인 레이어가 인프라 레이어(DB)에 의존하지 않도록 분리
- 단위 테스트 시 Mock 생성 가능
- 인프라 구현 교체 용이성 확보

**📦 구현 메서드**
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

### 4. TripQueryService 구현

#### `app/application/services/trip_query_service.py`

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

---

## ✅ Week 2 완료된 작업 (트립 생성)

### 1. CreateTripCommand 구현

#### `app/application/commands/create_trip.py`

**🎯 목적**
- Trip 생성 유스케이스를 위한 Command 패턴 구현
- CQRS 패턴의 Command 측면 담당

**💡 이유**
- B개발자가 스트리밍 API 구현 시 사용
- 불변 Command 객체로 데이터 일관성 보장
- API 라우터에서 쉽게 데이터 전달 가능

---

### 2. TripGenerationService 구현

#### `app/domain/services/trip_generation_service.py`

**🎯 목적**
- AI를 통한 트립 생성 유스케이스를 담당
- TripRepository와 AIClient를 통합

**💡 이유**
- AI 의존성 인터페이스로 분리 (테스트 용이)
- 도메인 로직과 인프라 분리 유지
- B개발자가 AI 구현 완료 전에 서비스 구조 확정

**📦 생성 프로세스**
1. AI로부터 트립 콘텐츠 생성 (cautions, baggage_summary)
2. Trip 엔티티 생성 (Trip.create())
3. 저장소에 저장 (trip_repository.save())
4. 저장된 Trip 반환

---

### 3. AIClient 인터페이스 정의

**🎯 목적**
- B개발자가 구현할 AI 클라이언트의 인터페이스 정의
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

---

## ✅ Week 3 완료된 작업 (Item & Memo)

### 1. Item 엔티티 구현

#### `app/domain/models/item.py`

**🎯 목적**
- 여행에 필요한 짐 항목 엔티티 정의
- 불변 엔티티 패턴 구현으로 데이터 일관성 보장
- 체크리스트 진행 상황 추적 가능

**💡 이유**
- B개발자가 API 라우터 구현 시 참조 가능한 명확한 인터페이스 제공
- 도메인 로직(체크박스, 정렬)을 인프라 레이어와 분리

**📦 주요 메서드**
- `create()`: 새 Item 생성 (자동 ID, 정렬 순서=0)
- `update()`: Item 업데이트 (불변 패턴)
- `check()`: 체크박스 완료 처리
- `uncheck()`: 체크박스 완료 취소
- `sort_order_up()`: 정렬 순서 변경
- `update_source()`: 소스를 AI로 변경
- `update_baggage_flag()`: 수화물 규정 플래그 변경

**주요 필드**:
```python
baggage_flag: str | None  # "carry_on_only" | "checked_only" | "restricted" | null
source: str = "user"      # "ai" | "user"
checked: bool = False     # 체크박스 완료 여부
sort_order: int = 0       # 정렬 순서 (오름차순)
```

---

### 2. ItemList 값 객체 구현

**🎯 목적**
- 항목 목록의 진행 상황을 계산하는 값 객체
- 진행률 계산 로직 캡슐화

**💡 이유**
- 진행률 계산 로직을 도메인 레이어에 위치
- 불변 객체로 일관성 보장
- 재사용 가능한 계산 로직 제공

**📦 주요 메서드**
```python
class ItemList:
    def total_items(self) -> int:
        """전체 항목 수."""

    def checked_items(self) -> int:
        """완료된 항목 수."""

    def completion_rate(self) -> float:
        """완료율 (백분율)."""

    def pending_items(self) -> list[Item]:
        """미완료 항목 리스트."""

    def checked_items_by_category(self) -> dict[str, list[Item]]:
        """카테고리별 완료 항목 그룹화."""
```

---

### 3. Memo 엔티티 구현

#### `app/domain/models/memo.py`

**🎯 목적**
- 여행에 관한 메모/기록 엔티티 정의
- 불변 엔티티 패턴 구현
- 최대 2,000자 길이 제한 검증

**💡 이유**
- 도메인 레이어에서 비즈니스 규칙(길이 제한) 검증
- 불변 패턴으로 데이터 일관성 보장

**📦 주요 메서드**
- `create()`: 새 Memo 생성 (자동 ID, 길이 검증)
- `update_content()`: 메모 내용 업데이트 (2,000자 제한)

---

### 4. ItemId, MemoId 값 객체 구현

#### `app/domain/value_objects/item_id.py`
#### `app/domain/value_objects/memo_id.py`

**🎯 목적**
- UUID 기반의 식별자 값 객체 정의
- 원시 타입(문자열) 대신 도메인에 의미 있는 타입 사용

**💡 이유**
- 타입 안정성 확보 (문자열 혼용 방지)
- 비즈니스 로직에서 ID 검증/변환 로직 캡슐화

---

### 5. ItemRepository 인터페이스 정의

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
    async def save(self, item: Item) -> Item: ...
    async def find_by_id(self, item_id: ItemId) -> Item | None: ...
    async def find_by_trip_id(self, trip_id: TripId) -> list[Item]: ...
    async def find_by_trip_id_sorted(self, trip_id: TripId) -> list[Item]: ...
    async def find_by_category(self, trip_id: TripId, category: str) -> list[Item]: ...
    async def delete(self, item_id: ItemId) -> None: ...
    async def delete_by_trip_id(self, trip_id: TripId) -> None: ...
    async def get_checked_count(self, trip_id: TripId) -> int: ...
    async def get_total_count(self, trip_id: TripId) -> int: ...
    async def update_sort_order(self, item_id: ItemId, new_order: int) -> None: ...
```

---

### 6. MemoRepository 인터페이스 정의

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
    async def save(self, memo: Memo) -> Memo: ...
    async def find_by_id(self, memo_id: MemoId) -> Memo | None: ...
    async def find_by_trip_id(self, trip_id: TripId) -> list[Memo]: ...
    async def delete(self, memo_id: MemoId) -> None: ...
    async def delete_by_trip_id(self, trip_id: TripId) -> None: ...
    async def get_count(self, trip_id: TripId) -> int: ...
```

---

### 7. Item 관련 Command 구현

#### `app/application/commands/item_commands.py`

**🎯 목적**
- Item CRUD 작업을 위한 Command 패턴 구현
- B개발자가 API 라우터에서 사용

**💡 이유**
- 불변 Command 객체로 데이터 일관성 보장
- 의존성 주입으로 테스트 용이

**📦 구현된 Commands**
```python
@dataclass(frozen=True)
class AddItemCommand:
    trip_id: str
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    source: str = "user"

@dataclass(frozen=True)
class CheckItemCommand:
    item_id: str
    checked: bool

@dataclass(frozen=True)
class UpdateItemCommand:
    item_id: str
    name: str | None = None
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    checked: bool | None = None

@dataclass(frozen=True)
class DeleteItemCommand:
    item_id: str

@dataclass(frozen=True)
class UpdateSortOrderCommand:
    item_id: str
    new_order: int
```

---

### 8. Memo 관련 Command 구현

#### `app/application/commands/memo_commands.py`

**🎯 목적**
- Memo CRUD 작업을 위한 Command 패턴 구현
- B개발자가 API 라우터에서 사용

**💡 이유**
- 불변 Command 객체로 데이터 일관성 보장
- 도메인 로직(2,000자 제한)에서 Command 구분

**📦 구현된 Commands**
```python
@dataclass(frozen=True)
class AddMemoCommand:
    trip_id: str
    content: str  # 최대 2,000자

@dataclass(frozen=True)
class UpdateMemoCommand:
    memo_id: str
    content: str  # 최대 2,000자

@dataclass(frozen=True)
class DeleteMemoCommand:
    memo_id: str
```

---

## ✅ B개발자 완료된 작업 (Week 3)

### 1. Repository 구현

**`infrastructure/database/repositories/sqlalchemy_item_repository.py`**
- ItemRepository 인터페이스 완전 구현
- ORM 모델 ↔ 도메인 모델 변환
- 정렬, 필터링, 통계 기능 구현

**`infrastructure/database/repositories/sqlalchemy_memo_repository.py`**
- MemoRepository 인터페이스 완전 구현
- Trip ID 기반 삭제 연동

---

### 2. CRUD 라우터 구현

**Items CRUD Routes** (`interfaces/api/v1/routes/items.py`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/items/{trip_id}` | Trip ID로 모든 Item 조회 (완료/미완료 구분) |
| POST | `/api/v1/items` | Item 생성 (체크박스, 탭, 팁, 정렬 순서) |
| PATCH | `/api/v1/items/{item_id}` | Item 수정 (이름, 수량, 팁, 체크박스) |
| DELETE | `/api/v1/items/{item_id}` | Item 삭제 |
| PATCH | `/api/v1/items/{item_id}/check` | 체크박스 완료/취소 |
| PATCH | `/api/v1/items/{item_id}/sort` | 정렬 순서 변경 |

**Memos CRUD Routes** (`interfaces/api/v1/routes/memos.py`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/memos/{trip_id}` | Trip ID로 모든 Memo 조회 |
| POST | `/api/v1/memos` | Memo 생성 (최대 2,000자) |
| PATCH | `/api/v1/memos/{memo_id}` | Memo 수정 |
| DELETE | `/api/v1/memos/{memo_id}` | Memo 삭제 |

---

## 📋 Week 3 파일 생성/수정 현황

```
backend/
├── app/
│   ├── domain/
│   │   ├── models/
│   │   │   ├── item.py ✅
│   │   │   └── memo.py ✅
│   │   ├── repositories/
│   │   │   ├── item_repository.py ✅
│   │   │   └── memo_repository.py ✅
│   │   └── value_objects/
│   │       ├── item_id.py ✅
│   │       └── memo_id.py ✅
│   └── application/
│       └── commands/
│           ├── item_commands.py ✅
│           └── memo_commands.py ✅
├── infrastructure/
│   └── database/
│       └── repositories/
│           ├── sqlalchemy_item_repository.py ✅
│           └── sqlalchemy_memo_repository.py ✅
└── interfaces/
    └── api/
        └── v1/
            └── routes/
                ├── items.py ✅
                └── memos.py ✅
```

---

## 🔄 의존성 관계 확인

### A개발자 → B개발자 흐름 ✅

1. **도메인 인터페이스 정의** (A) → **구현** (B)
2. **도메인 엔티티** (Item, ItemList, Memo) → **ORM 모델 활용** (B)
3. **Command 패턴** (A) → **라우터 사용** (B)

---

## 🎉 다음 단계 (선택 사항)

| 작업 | 담당 | 상태 | 비고 |
|------|------|------|------|
| 단위 테스트 작성 (도메인) | A | ⏳ | test_item.py, test_memo.py |
| 단위 테스트 작성 (Repository) | B | ⏳ | test_sqlalchemy_item_repository.py |
| 통합 테스트 작성 | 공동 | ⏳ | API 엔드포인트 테스트 |
| 문서 업데이트 (CLAUDE.md) | A | ⏳ | Week 3 기능 반영 |

---

## ✅ Week 4 완료된 작업 (버그 수정)

### 1. Item 엔티티 sort_order 업데이트 버그 수정

#### `app/domain/models/item.py`

**🎯 목적**
- `Item.update()` 메서드에서 `sort_order` 파라미터 누락 문제 해결
- `sort_order_up()` 메서드가 정상 동작하도록 수정

**💡 이유**
- `Item.sort_order_up(new_order: int)`는 내부적으로 `self.update(sort_order=new_order)`를 호출
- `update()` 메서드에 `sort_order` 파라미터가 없어 정렬 순서 변경이 불가능
- 테스트에서 정렬 순서 변경이 실패하는 원인

**📦 수정 내용**
```python
def update(
    self,
    name: str | None = None,
    quantity: str | None = None,
    tip: str | None = None,
    baggage_flag: str | None = None,
    checked: bool | None = None,
    sort_order: int | None = None,  # ✅ 추가
) -> Self:
    """Item 업데이트."""
    return Item(
        # ... 기존 필드 ...
        sort_order=sort_order if sort_order is not None else self.sort_order,
        # ...
    )
```

---

### 2. 라우터 정렬 순서 변경 버그 수정

#### `interfaces/api/v1/routes/items.py`

**🎯 목적**
- `update_sort_order()` 라우터에서 반환값을 저장하지 않는 문제 해결
- 불변 객체 패턴에 맞게 업데이트된 객체를 저장

**💡 이유**
- `item.sort_order_up(command.new_order)` 호출 후 반환값을 무시
- 원래 `item` 객체를 저장하여 DB에 변경사항 반영되지 않음
- 불변 객체 패턴에서는 새로운 인스턴스를 저장해야 함

**📦 수정 내용**
```python
# 정렬 순서 변경
updated = item.sort_order_up(command.new_order)  # ✅ 반환값 저장

# 저장
saved = await item_repo.save(updated)  # ✅ 업데이트된 객체 저장
```

---

### 3. 소유권 확인 로직 수정 (Item & Memo)

#### `interfaces/api/v1/routes/items.py`
#### `interfaces/api/v1/routes/memos.py`

**🎯 목적**
- `item.trip_id.user_id` AttributeError 해결
- 올바른 소유권 확인 로직 구현

**💡 이유**
- `item.trip_id`는 `TripId` 값 객체 (user_id 속성 없음)
- 테스트에서 mock을 `trip_id=mock_trip`으로 설정하여 의도치 않게 동작
- 실제 코드에서는 `Trip` 객체를 조회하여 `user_id` 확인 필요

**📦 수정 내용**
```python
# 이전 (오류)
if item.trip_id.user_id != user_id:  # ❌ AttributeError

# 수정 후
trip = await trip_repo.find_by_id(item.trip_id)  # ✅ Trip 조회
if trip is None or trip.user_id != user_id:  # ✅ 올바른 확인
```

**적용 범위**:
- `items.py`: update_item, delete_item, check_item, update_sort_order
- `memos.py`: update_memo, delete_memo

---

### 4. Memo 중복 정의 삭제

#### `app/domain/models/item.py`

**🎯 목적**
- `item.py`에 중복 정의된 `Memo` 클래스 제거
- 코드 중복 제거 및 유지보수성 향상

**💡 이유**
- `Memo`는 `app/domain/models/memo.py`에 이미 정의
- 중복 정의로 인한 혼란 방지
- import 오류 가능성 제거

**📦 수정 내용**
- `item.py`에서 `MemoId` import 제거
- `Memo` 클래스 전체 삭제 (라인 141-172)

---

### 5. 삭제 엔드포인트 204 상태코드 반환

#### `interfaces/api/v1/routes/items.py`
#### `interfaces/api/v1/routes/memos.py`

**🎯 목적**
- DELETE 요청 시 204 No Content 명시적 반환
- RESTful API 표준 준수

**💡 이유**
- 함수 리턴 타입이 `None`이어도 FastAPI가 200 반환
- 테스트에서 204를 기대하는데 200이 반환되어 실패
- `Response(status_code=204)`로 명시적 반환 필요

**📦 수정 내용**
```python
from fastapi import Response  # ✅ import 추가

@router.delete("/{item_id}")
async def delete_item(...) -> None:
    # ... 삭제 로직 ...
    await item_repo.delete(item_id_obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # ✅ 명시적 반환
```

---

### 6. pyproject.toml packages 설정 추가

#### `pyproject.toml`

**🎯 목적**
- hatchling build가 패키지를 올바르게 식별
- editable 설치 가능

**💡 이유**
- hatchling이 기본적으로 프로젝트 이름과 일치하는 디렉토리를 찾음
- `trapkit_backend` 디렉토리가 없어 빌드 실패
- packages 설정으로 포함할 디렉토리 명시

**📦 수정 내용**
```toml
[tool.hatch.build.targets.wheel]
packages = ["app", "infrastructure", "interfaces", "shared"]
```

---

## ✅ Week 3 버그 수정 (2026-07-23)

### 1. Item 엔티티 sort_order 업데이트 버그 수정

#### `app/domain/models/item.py`

**🎯 목적**
- `Item.update()` 메서드에서 `sort_order` 파라미터 누락 문제 해결
- `sort_order_up()` 메서드가 정상 동작하도록 수정

**💡 이유**
- `Item.sort_order_up(new_order: int)`는 내부적으로 `self.update(sort_order=new_order)`를 호출
- `update()` 메서드에 `sort_order` 파라미터가 없어 정렬 순서 변경이 불가능

**📦 수정 내용**
```python
def update(
    self,
    name: str | None = None,
    quantity: str | None = None,
    tip: str | None = None,
    baggage_flag: str | None = None,
    checked: bool | None = None,
    sort_order: int | None = None,  # ✅ 추가
) -> Self:
```

---

### 2. 라우터 정렬 순서 변경 버그 수정

#### `interfaces/api/v1/routes/items.py`

**🎯 목적**
- `update_sort_order()` 라우터에서 반환값을 저장하지 않는 문제 해결
- 불변 객체 패턴에 맞게 업데이트된 객체를 저장

**💡 이유**
- `item.sort_order_up(command.new_order)` 호출 후 반환값을 무시
- 원래 `item` 객체를 저장하여 DB에 변경사항 반영되지 않음

**📦 수정 내용**
```python
updated = item.sort_order_up(command.new_order)  # ✅ 반환값 저장
saved = await item_repo.save(updated)  # ✅ 업데이트된 객체 저장
```

---

### 3. 소유권 확인 로직 수정 (Item & Memo)

#### `interfaces/api/v1/routes/items.py`, `interfaces/api/v1/routes/memos.py`

**🎯 목적**
- `item.trip_id.user_id` AttributeError 해결
- 올바른 소유권 확인 로직 구현

**💡 이유**
- `item.trip_id`는 `TripId` 값 객체 (user_id 속성 없음)
- 실제 코드에서는 `Trip` 객체를 조회하여 `user_id` 확인 필요

**📦 수정 내용**
```python
# 수정 후
trip = await trip_repo.find_by_id(item.trip_id)
if trip is None or trip.user_id != user_id:
```

---

### 4. Memo 중복 정의 삭제

#### `app/domain/models/item.py`

**🎯 목적**
- `item.py`에 중복 정의된 `Memo` 클래스 제거

**💡 이유**
- `Memo`는 `app/domain/models/memo.py`에 이미 정의

---

### 5. 삭제 엔드포인트 204 상태코드 반환

#### `interfaces/api/v1/routes/items.py`, `interfaces/api/v1/routes/memos.py`

**🎯 목적**
- DELETE 요청 시 204 No Content 명시적 반환

**💡 이유**
- 함수 리턴 타입이 `None`이어도 FastAPI가 200 반환
- `Response(status_code=204)`로 명시적 반환 필요

---

### 6. pyproject.toml packages 설정 추가

#### `pyproject.toml`

**🎯 목적**
- hatchling build가 패키지를 올바르게 식별

**💡 이유**
- `trapkit_backend` 디렉토리가 없어 빌드 실패
- packages 설정으로 포함할 디렉토리 명시

---

## 📋 Week 3 최종 파일 수정 현황

```
backend/
├── app/
│   └── domain/
│       └── models/
│           └── item.py ✅ 수정 (sort_order 추가, Memo 중복 삭제)
├── interfaces/
│   └── api/
│       └── v1/
│           └── routes/
│               ├── items.py ✅ 수정 (sort_order, 소유권 확인, 204)
│               └── memos.py ✅ 수정 (소유권 확인, 204)
└── pyproject.toml ✅ 수정 (packages 설정)
```

---

## 🔄 Week 3 버그 수정 요약

| 버그 | 원인 | 해결 방법 |
|------|------|-----------|
| sort_order 업데이트 불가 | `update()`에 sort_order 파라미터 누락 | 파라미터 추가 |
| 정렬 순서 변경 미반영 | 반환값 저장하지 않음 | `updated = item.sort_order_up(...)` |
| AttributeError 소유권 확인 | `item.trip_id.user_id` 접근 시도 | Trip 조회 후 user_id 확인 |
| Memo 중복 정의 | item.py에 Memo 존재 | 중복 제거 |
| 200 vs 204 상태코드 | None 리턴 시 FastAPI 200 반환 | `Response(204)` 명시적 반환 |
| 빌드 실패 | packages 설정 누락 | packages 명시 |

---

## 📝 비고

- **불변 엔티티 패턴**: 모든 도메인 엔티티는 `frozen=True`로 데이터 일관성 보장
- **진행률 계산 로직**: A개발자가 ItemList에 이미 구현 완료 ✅
- **의존성 주입**: Repository, Service 모두 의존성 주입 패턴 사용
- **권한 확인**: 모든 API 라우터에서 소유권 확인 (Trip 조회 후 user_id 비교) ✅ Week 3 버그 수정 완료
- **값 객체 사용**: TripId, ItemId, MemoId 값 객체로 타입 안정성 확보 ✅

---

## ⏳ Week 4 예정 작업 (수화물 체커)

| 작업 | 담당 | 상태 | 비고 |
|------|------|------|------|
| Verdict 값 객체 정의 | A | ⏳ | 수화물 규정 검증 결과 |
| BaggageService 도메인 구현 | A | ⏳ | 수화물 규정 체크 로직 |
| normalizer.py 구현 | A | ⏳ | 항공사 데이터 정규화 |
| BaggageRuleRepository 인터페이스 | A | ⏳ | 수화물 규정 저장소 |
| POST /api/baggage/check | B | ⏳ | 수화물 규정 체크 API |
| 캐시 TTL 최적화 | B | ⏳ | 캐싱 서비스 완료 후 |

---

*마지막 업데이트: 2026-07-23*