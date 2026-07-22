# B개발자 작업 계획 (Week 2)

## 📅 날짜
2026-07-23 (수)

---

## 🔄 A개발자 Week2 완료 내용

A개발자가 Week2에서 다음 작업을 완료했습니다:

| 작업 | 파일 | 상태 |
|------|------|------|
| CreateTripCommand | `app/application/commands/create_trip.py` | ✅ 완료 |
| TripGenerationService | `app/domain/services/trip_generation_service.py` | ✅ 완료 |
| AIClient 인터페이스 | `app/domain/services/trip_generation_service.py` | ✅ 완료 |

---

## 🎯 B개발자 Week2 작업 계획

### 1단계: Gemini Client 구현 (2시간)

**작업 내용:**

#### GeminiClient (`app/infrastructure/external/gemini_client.py`)

**🎯 목적:**
- A개발자가 정의한 AIClient 인터페이스 구현
- Google Gemini API를 통한 트립 콘텐츠 생성
- 스트리밍 지원으로 실시간 응답 제공

**💡 이유:**
- A개발자의 도메인 서비스와 AI 인프라 분리
- 테스트 용이성 확보 (인터페이스 주입)
- 비용 효율적 (무료 요금제: 15 requests/min, 1,500 requests/day)
- 한국어 이해도 우수

**📦 주요 기능:**
- `generate_trip_content()`: CreateTripCommand로부터 AI 콘텐츠 생성
- 스트리밍 응답 지원 (SSE - Server-Sent Events)
- Redis 캐싱으로 비용 절감

**📦 AIClient 인터페이스 (A개발자 정의):**
```python
class AIClient(ABC):
    @abstractmethod
    async def generate_trip_content(self, command: CreateTripCommand) -> dict:
        """AI를 통해 트립 콘텐츠 생성."""
        pass
```

**📦 AI 콘텐츠 형식:**
```json
{
    "cautions": [{"type": "weather", "message": "비 우산 챙기기"}],
    "baggage_summary": [{"category": "clothing", "count": 5}]
}
```

**📦 작업 단계:**
1. [x] Gemini SDK 설치 (`pip install google-generativeai`)
2. [x] GeminiClient 클래스 구현 (AIClient 상속)
3. [x] generate_trip_content() 메서드 구현
4. [x] 스트리밍 지원 추가
5. [x] Redis 캐싱 연동
6. [x] 단위 테스트 작성

**📦 코드 구조 예시:**
```python
from app.domain.services.trip_generation_service import AIClient, CreateTripCommand

class GeminiClient(AIClient):
    def __init__(self, api_key: str, redis_client):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.redis = redis_client

    async def generate_trip_content(self, command: CreateTripCommand) -> dict:
        # 캐시 확인
        cache_key = f"trip:{hash(command)}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # AI 생성
        prompt = self._build_prompt(command)
        response = await self.model.generate_content_async(prompt)

        # 결과 파싱
        content = self._parse_response(response)

        # 캐시 저장 (30일 TTL)
        await self.redis.set(cache_key, json.dumps(content), ex=2592000)

        return content

    def _build_prompt(self, command: CreateTripCommand) -> str:
        # 프롬프트 빌드 로직
        pass

    def _parse_response(self, response) -> dict:
        # 응답 파싱 로직
        pass
```

---

### 2단계: Redis Client 구현 (1시간) ✅

**작업 내용:**

#### RedisClient (`app/core/redis.py`)

**🎯 목적:**
- Redis 연결 및 캐싱 기능 제공
- AI 응답 캐싱으로 비용 절감

**💡 이유:**
- 기존 Redis asyncio 기반 클라이언트 구현 완료
- Upstash Redis는 Redis 프로토콜 지원 → 기존 클라이언트 그대로 사용

**📦 주요 기능:**
- `get(key)`: 캐시 조회
- `set(key, value, ttl)`: 캐시 저장
- `delete(key)`: 캐시 삭제

**📦 작업 단계:**
1. [x] Upstash Redis REST API 확인 (Redis 프로토콜 사용)
2. [x] RedisClient 클래스 확인 (기존 구현)
3. [x] 비동기 HTTP 클라이언트 (redis.asyncio) 사용
4. [x] 단위 테스트 (기존 테스트 확인)

**📦 코드 구조 예시:**
```python
import httpx
from app.shared.config.settings import settings

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

    async def set(self, key: str, value: str, ttl: int = 2592000) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.url}/set/{key}",
                headers=self.headers,
                json={"value": value, "EX": ttl}
            )

    async def delete(self, key: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(f"{self.url}/del/{key}", headers=self.headers)
```

---

### 3단계: POST 스트리밍 구현 (2시간) ✅

**작업 내용:**

#### Trip Generate Route (`interfaces/api/v1/routes/trips.py`)

**🎯 목적:**
- `POST /api/v1/trips/generate` 엔드포인트 구현
- Server-Sent Events (SSE)로 실시간 스트리밍 응답 제공
- A개발자의 TripGenerationService 연동

**💡 이유:**
- 사용자에게 AI 생성 진행 상황 실시간 피드백
- 대기 시간 단축 및 사용자 경험 향상
- FastAPI StreamingResponse 활용

**📦 주요 기능:**
- `POST /api/v1/trips/generate`: 트립 생성 요청 (쿼리 파라미터)
- `POST /api/v1/trips/generate/body`: 트립 생성 요청 (Request Body)
- SSE 스트리밍 응답
- 인증 (user_id 파라미터)
- 요청 유효성 검사

**📦 API 스펙:**
```yaml
POST /api/v1/trips/generate
Authorization: Bearer <jwt_token>

Request (Query Params):
user_id=test-user
destination=제주도
purpose=관광
duration_nights=3
departure_month=8
companions=가족

Response (SSE):
event: started
data: {"status": "started", "message": "트립 생성을 시작합니다...", "destination": "제주도"}

event: generating
data: {"status": "generating", "message": "AI로부터 콘텐츠를 생성 중입니다..."}

event: content
data: {"status": "content_generated", "content": {"cautions": [...], "baggage_summary": [...]}}

event: creating
data: {"status": "creating_entity", "message": "Trip 엔티티를 생성 중입니다..."}

event: saving
data: {"status": "saving", "message": "데이터베이스에 저장 중입니다..."}

event: completed
data: {"status": "completed", "trip": {...}}
```

**📦 작업 단계:**
1. [x] FastAPI StreamingResponse 설정
2. [x] TripGenerationService 의존성 주입
3. [x] 스트리밍 핸들러 구현
4. [x] 인증 미들웨어 연결 (user_id)
5. [x] 요청 유효성 검사
6. [x] 에러 처리

**📦 코드 구조 예시:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.application.commands.create_trip import CreateTripCommand
from app.domain.services.trip_generation_service import TripGenerationService
from app.infrastructure.external.gemini_client import GeminiClient
from app.infrastructure.external.redis_client import RedisClient
from app.interfaces.api.dependencies.auth import get_current_user_id
from app.interfaces.api.dependencies.repositories import get_trip_repository

router = APIRouter(prefix="/api/v1/trips", tags=["Trip Generation"])

@router.post("/generate")
async def generate_trip_stream(
    request: GenerateTripRequest,
    current_user_id: str = Depends(get_current_user_id),
    trip_repository = Depends(get_trip_repository),
):
    # 의존성 주입
    redis_client = RedisClient()
    gemini_client = GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        redis_client=redis_client
    )
    service = TripGenerationService(trip_repository, gemini_client)

    # Command 생성
    command = CreateTripCommand(
        user_id=current_user_id,
        destination=request.destination,
        purpose=request.purpose,
        duration_nights=request.duration_nights,
        departure_month=request.departure_month,
        companions=request.companions
    )

    async def generate():
        try:
            # 스트리밍 진행 상황 전송
            yield "data: {\"type\": \"thinking\", \"message\": \"분석 중...\"}\n\n"

            # 트립 생성
            trip = await service.generate(command)

            # 성공 응답
            response = {
                "type": "success",
                "trip": {
                    "id": str(trip.id),
                    "title": trip.title,
                    "destination": trip.destination,
                    "purpose": trip.purpose,
                    "cautions": trip.cautions,
                    "baggage_summary": trip.baggage_summary
                }
            }
            yield f"data: {json.dumps(response)}\n\n"

        except Exception as e:
            error_response = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

---

### 4단계: 테스트 및 검증 (1시간) ✅

**작업 내용:**

#### 테스트 리스트

**📦 작업 단계:**
1. [x] GeminiClient 단위 테스트 (Mock 사용)
2. [x] RedisClient 단위 테스트 (기존 구현 확인)
3. [x] 스트리밍 엔드포인트 통합 테스트
4. [x] 캐시 기능 테스트
5. [x] 에러 처리 테스트

**📦 테스트 파일:**
```
tests/infrastructure/
└── external/
    └── test_gemini_client.py (11개 테스트)
tests/interfaces/
└── api/
    └── v1/
        └── routes/
            └── test_trips.py (6개 테스트)
```

**📦 테스트 파일:**
```
tests/infrastructure/
├── external/
│   ├── test_gemini_client.py
│   └── test_redis_client.py
tests/interfaces/
└── api/
    └── v1/
        └── test_trip_generate.py
```

---

## 📊 Week2 작업 일정

| 시간 | 작업 | 상태 | 예상 소요시간 |
|------|------|------|-------------|
| 09:00 - 11:00 | Gemini Client 구현 | ✅ 완료 | 2시간 |
| 11:00 - 12:00 | Redis Client 구현 | ✅ 완료 | 1시간 |
| 13:00 - 15:00 | POST 스트리밍 구현 | ✅ 완료 | 2시간 |
| 15:00 - 16:00 | 테스트 및 검증 | ✅ 완료 | 1시간 |

**총 예상 시간: 6시간**
**실제 완료: 100%**

---

## 🎯 성공 기준

### 완료 체크리스트

### Gemini Client
- [x] AIClient 인터페이스 구현 완료
- [x] generate_trip_content() 메서드 구현
- [x] 스트리밍 지원 (SSE)
- [x] Redis 캐싱 연동
- [x] 단위 테스트 통과 (11개 테스트)

### Redis Client
- [x] REST API 연동 (redis.asyncio)
- [x] get/set/delete 메서드 구현
- [x] TTL 설정 지원
- [x] 단위 테스트 통과 (기존 구현 확인)

### 스트리밍 API
- [x] POST /api/v1/trips/generate 엔드포인트
- [x] SSE 스트리밍 응답
- [x] 인증 미들웨어 연동 (user_id)
- [x] 에러 처리
- [x] 통합 테스트 통과 (6개 테스트)

---

## 🔄 A개발자와 협업 포인트

### 의존 사항

| A개발자 | B개발자 |
|---------|---------|
| ✅ CreateTripCommand 완료 | ✅ GeminiClient 구현 |
| ✅ TripGenerationService 완료 | ✅ 스트리밍 엔드포인트 |
| ✅ AIClient 인터페이스 정의 | ✅ AIClient 구현 |

### 협업 필요 시점

1. **테스트 시**:
   - A개발자의 도메인 로직 검증
   - 스트리밍 테스트

2. **Week 3 시작 시**:
   - 체크리스트 CRUD 스펙 협의
   - Item, Memo 엔티티 구조 확인

---

## 📝 메모

### 주의사항

1. **Gemini Client 구현 시**:
   - A개발자의 AIClient 인터페이스 준수 필수
   - 반환 형식 (`dict` with `cautions`, `baggage_summary`) 일치
   - 스트리밍 지원으로 사용자 경험 향상

2. **Redis Client 구현 시**:
   - Upstash REST API 사용 (서버리스 적합)
   - TTL 설정으로 자동 만료
   - 비동기 HTTP 클라이언트 (httpx) 사용

3. **스트리밍 API 구현 시**:
   - SSE (Server-Sent Events) 사용
   - 적절한 헤더 설정 (`Cache-Control`, `Connection`)
   - 에러 처리로 안정성 확보

### A개발자에게 전달할 질문

1. 스트리밍 응답 포맷이 맞는가요? (`type`, `message`, `trip`)
2. 캐시 TTL은 30일이 적절한가요?
3. 에러 응답 형식이 맞는가요?

---

## ✅ 완료 시 다음 단계

### Week 2 완료 후
1. [x] A개발자에게 Week2 완료 알리기
2. [x] 스트리밍 테스트 결과 공유
3. [x] Week 3 준비 (선택 사항)

### Week 3 준비 (A개발자 협업 필요)
1. [ ] Item, Memo 엔티티 구조 확인
2. [ ] ItemRepository, MemoRepository 인터페이스 확인
3. [ ] CRUD 엔드포인트 스펙 정의

---

*계획 버전: 2.0*
*마지막 업데이트: 2026-07-23*