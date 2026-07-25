# 프론트엔드-백엔드 API 연동 완료 요약

## 구현 완료 일자
2026-07-24

---

## 구현 내용

### 1. 인증 연동
- **파일**: [`app/layout.tsx`](app/layout.tsx)
  - AuthProvider 추가로 전역 인증 상태 관리
  - JWT 토큰 자동 관리

- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L41-L67)
  - `Header` 컴포넌트에서 `useAuth()` 사용
  - 로그인 상태에 따라 다른 UI 표시
  - 로그아웃 기능 연동

- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L447-L466)
  - `Login` 컴포넌트에서 실제 API 연동
  - `authApi.login()`, `authApi.signup()` 사용
  - 에러 처리 및 피드백 제공

---

### 2. 수화물 체커 연동
- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L419-L446)
  - `Baggage` 컴포넌트에서 `baggageApi.check()` 사용
  - 실제 백엔드 API 호출
  - API 실패 시 mock 데이터 fallback
  - 기내·위탁 판정 결과 표시

```typescript
const response = await baggageApi.check({
  airline: "대한항공",
  product: value,
  value: amount ? parseFloat(amount) : undefined,
  unit: amount ? unit : undefined
});
```

---

### 3. 트립 생성 SSE 스트리밍 연동
- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L143-L195)
  - `Home` 컴포넌트에서 여행 정보 수집
  - `sessionStorage`에 요청 데이터 저장

- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L207-L241)
  - `Trip` 컴포넌트에서 `tripsApi.generateTripStream()` 사용
  - 실시간 진행 상황 표시
  - 완료 시 아이템 자동 로드

```typescript
const cleanup = tripsApi.generateTripStream(
  request,
  (event: SSEEvent) => console.log(event.status),
  async (trip: Trip) => {
    setTripId(trip.id);
    setTitle(trip.title);
    // 아이템 로드
    const itemsResponse = await itemsApi.getByTripId(trip.id);
    setCategories(groupItemsByCategory(itemsResponse.items));
  }
);
```

---

### 4. 아이템 CRUD 연동
- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L243-L267)
  - 체크박스 토글: `itemsApi.check()`
  - 아이템 추가: `itemsApi.create()`
  - 아이템 삭제: `itemsApi.delete()`
  - 카테고리별 그룹화 및 표시

```typescript
// 체크 토글
const toggle = async (id: string) => {
  // UI 업데이트
  setCategories(updatedCategories);
  // API 호출
  if (tripId) await itemsApi.check(id, item.checked);
};

// 아이템 추가
const add = async (categoryName: string, name: string) => {
  if (isAuthenticated && tripId) {
    await itemsApi.create({
      trip_id: tripId,
      category: categoryName,
      name: name.trim(),
      quantity: 1,
      baggage_flag: false,
      source: "user"
    });
    // 다시 로드
    const itemsResponse = await itemsApi.getByTripId(tripId);
    setCategories(groupItemsByCategory(itemsResponse.items));
  }
};
```

---

### 5. 내 여행 페이지 연동
- **파일**: [`app/mockup.tsx`](app/mockup.tsx#L430-L456)
  - `Trips` 컴포넌트에서 `isAuthenticated` 확인
  - 인증 상태에 따라 다른 UI 표시
  - 로그인되지 않은 경우 로그인 페이지로 이동

---

## API 엔드포인트 매핑

| 기능 | 프론트엔드 | 백엔드 | 메서드 |
|------|-----------|--------|--------|
| 로그인 | `authApi.login()` | `/api/auth/login` | POST |
| 회원가입 | `authApi.signup()` | `/api/auth/signup` | POST |
| 인증 확인 | `authApi.verify()` | `/api/auth/verify` | GET |
| 수화물 체크 | `baggageApi.check()` | `/api/v1/baggage/check` | POST |
| 트립 생성 | `tripsApi.generateTripStream()` | `/api/v1/trips/generate` | POST (SSE) |
| 아이템 조회 | `itemsApi.getByTripId()` | `/api/v1/items/{trip_id}` | GET |
| 아이템 생성 | `itemsApi.create()` | `/api/v1/items` | POST |
| 아이템 체크 | `itemsApi.check()` | `/api/v1/items/{item_id}/check` | PATCH |
| 아이템 삭제 | `itemsApi.delete()` | `/api/v1/items/{item_id}` | DELETE |

---

## 환경 설정

### `.env.local`
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

### 백엔드 CORS 설정
```python
# backend/app/config.py
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:3003",  # 프론트엔드 포트
]
```

---

## 사용 흐름

### 1. 로그인
```
사용자 → 로그인 폼 입력 → authApi.login() → 백엔드 인증 → 토큰 저장 → 로그인 완료
```

### 2. 트립 생성
```
홈 화면 → 여행 정보 입력 → generateTripStream() → AI 생성 (SSE) → 아이템 로드 → 트립 상세 화면
```

### 3. 체크리스트 사용
```
트립 상세 → 아이템 체크/추가/삭제 → itemsApi 호출 → DB 업데이트 → UI 갱신
```

### 4. 수화물 체크
```
수화물 체커 → 품목 입력 → baggageApi.check() → 규정 확인 → 결과 표시
```

---

## 주요 파일

| 파일 | 역할 |
|------|------|
| [`lib/api.ts`](lib/api.ts) | API 클라이언트 구현 |
| [`lib/types.ts`](lib/types.ts) | TypeScript 타입 정의 |
| [`lib/auth.tsx`](lib/auth.tsx) | 인증 Context & Hook |
| [`app/layout.tsx`](app/layout.tsx) | AuthProvider 적용 |
| [`app/mockup.tsx`](app/mockup.tsx) | 전체 페이지 구현 및 API 연동 |
| [`docs/API_INTEGRATION.md`](docs/API_INTEGRATION.md) | 상세 API 연동 가이드 |

---

## 테스트 체크리스트

- [ ] 로그인/로그아웃 정상 작동
- [ ] 회원가입 정상 작동
- [ ] 수화물 규정 체크 정상 작동
- [ ] 트립 생성 SSE 스트리밍 정상 작동
- [ ] 아이템 CRUD 정상 작동
- [ ] 체크박스 토글 정상 작동
- [ ] 인증되지 않은 사용자 리디렉션
- [ ] 에러 상황 처리

---

## 다음 단계

1. 백엔드 트립 조회/삭제 API 구현
2. 내 여행 페이지에 실제 트립 리스트 표시
3. 에러 바운더리 추가
4. 로딩 상태 개선
5. 테스트 코드 작성