# Trip API 스펙 문서

## 📋 개요

Trip(여행) 관리 API 스펙입니다. 프론트엔드 개발자가 참고할 수 있습니다.

---

## 🔐 인증

### Bearer Token

모든 요청은 `Authorization` 헤더에 Bearer Token을 포함해야 합니다.

```http
Authorization: Bearer {token}
```

**참고**: 현재는 Mock 인증으로, 유효한 토큰이면 `"dev-user-id"`로 인식됩니다. (2026-07-22 기준)

---

## 🗂️ 엔드포인트

### 1. 사용자의 모든 Trip 조회

#### Request

```http
GET /api/v1/trips
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-123",
    "title": "도쿄 여행",
    "destination": "일본 도쿄",
    "purpose": ["쇼핑", "음식 탐방"],
    "duration_nights": 5,
    "departure_month": 8,
    "companions": "가족 3인",
    "cautions": [],
    "baggage_summary": [],
    "created_at": "2026-07-21T12:00:00Z",
    "updated_at": "2026-07-21T12:00:00Z"
  }
]
```

#### Response (401 Unauthorized)

```json
{
  "detail": "Authorization header missing"
}
```

---

### 2. 특정 Trip 조회

#### Request

```http
GET /api/v1/trips/{trip_id}
Authorization: Bearer {token}
```

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| trip_id | string (UUID) | Trip ID |

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "title": "도쿄 여행",
  "destination": "일본 도쿄",
  "purpose": ["쇼핑", "음식 탐방"],
  "duration_nights": 5,
  "departure_month": 8,
  "companions": "가족 3인",
  "cautions": [],
  "baggage_summary": [],
  "created_at": "2026-07-21T12:00:00Z",
  "updated_at": "2026-07-21T12:00:00Z"
}
```

#### Response (404 Not Found)

```json
{
  "detail": "Trip not found"
}
```

---

### 3. Trip 생성

#### Request

```http
POST /api/v1/trips
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "title": "도쿄 여행",
  "destination": "일본 도쿄",
  "purpose": ["쇼핑", "음식 탐방"],
  "duration_nights": 5,
  "departure_month": 8,
  "companions": "가족 3인"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | ✅ | 트립 제목 (1-200자) |
| destination | string | ✅ | 여행지 (1-100자) |
| purpose | list[string] | ✅ | 여행 목적 (최소 1개) |
| duration_nights | int | ❌ | 박수 (1 이상) |
| departure_month | int | ❌ | 출발 월 (1-12) |
| companions | string | ❌ | 동행인 (최대 100자) |

#### Response (201 Created)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "title": "도쿄 여행",
  "destination": "일본 도쿄",
  "purpose": ["쇼핑", "음식 탐방"],
  "duration_nights": 5,
  "departure_month": 8,
  "companions": "가족 3인",
  "cautions": [],
  "baggage_summary": [],
  "created_at": "2026-07-22T12:00:00Z",
  "updated_at": "2026-07-22T12:00:00Z"
}
```

---

### 4. Trip 수정

#### Request

```http
PATCH /api/v1/trips/{trip_id}
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "title": "도쿄 여행 (수정)",
  "duration_nights": 7
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | ❌ | 수정할 제목 (1-200자) |
| destination | string | ❌ | 수정할 여행지 (1-100자) |
| purpose | list[string] | ❌ | 수정할 목적 (최소 1개) |
| duration_nights | int | ❌ | 수정할 박수 (1 이상) |
| departure_month | int | ❌ | 수정할 출발 월 (1-12) |
| companions | string | ❌ | 수정할 동행인 (최대 100자) |

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "title": "도쿄 여행 (수정)",
  "destination": "일본 도쿄",
  "purpose": ["쇼핑", "음식 탐방"],
  "duration_nights": 7,
  "departure_month": 8,
  "companions": "가족 3인",
  "cautions": [],
  "baggage_summary": [],
  "created_at": "2026-07-21T12:00:00Z",
  "updated_at": "2026-07-22T13:00:00Z"
}
```

---

### 5. Trip 삭제

#### Request

```http
DELETE /api/v1/trips/{trip_id}
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "트립이 삭제되었습니다."
}
```

---

## 📊 TripResponse 스키마

```json
{
  "id": "string (UUID)",
  "user_id": "string",
  "title": "string (1-200자)",
  "destination": "string (1-100자)",
  "purpose": ["string"],
  "duration_nights": "int | null",
  "departure_month": "int (1-12) | null",
  "companions": "string | null (최대 100자)",
  "cautions": [{"key": "value"}],
  "baggage_summary": [{"key": "value"}],
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

---

## ⚠️ 에러 코드

| 코드 | 설명 |
|------|------|
| 401 | Authorization 헤더 누락 |
| 404 | Trip을 찾을 수 없음 |
| 422 | 요청 데이터 유효성 검증 실패 |

---

## 📝 비고

- `cautions`와 `baggage_summary`는 `list[dict]` 타입입니다 (2026-07-22 수정)
- 날짜 형식은 ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`)
- ID는 UUID 형식입니다

---

*문서 버전: 1.0*  
*마지막 업데이트: 2026-07-22*