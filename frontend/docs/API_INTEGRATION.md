# 프론트엔드-백엔드 API 연동 가이드

## 개요

트립킷(Trapkit) 프론트엔드와 백엔드(FastAPI) 간의 API 연동 구현에 대한 문서입니다.

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                     │
├─────────────────────────────────────────────────────────────┤
│  Components                                                 │
│  ├── TripGenerator                                          │
│  ├── ItemManager                                            │
│  └── BaggageChecker                                         │
├─────────────────────────────────────────────────────────────┤
│  Hooks & Context                                            │
│  ├── useAuth()              ─── auth.tsx                    │
│  └── useTripStream()        ─── (custom hook)              │
├─────────────────────────────────────────────────────────────┤
│  API Layer                                                  │
│  ├── apiClient             ─── lib/api.ts                  │
│  ├── authApi               ─── 인증 엔드포인트              │
│  ├── tripsApi              ─── 트립 스트리밍               │
│  ├── itemsApi              ─── 아이템 CRUD                 │
│  └── baggageApi            ─── 수화물 체크                 │
├─────────────────────────────────────────────────────────────┤
│  Types                                                       │
│  └── TypeScript Interfaces  ─── lib/types.ts                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP + SSE
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  Routes                                                      │
│  ├── /api/auth/*           ─── auth.py                      │
│  ├── /api/v1/baggage/*     ─── baggage.py                   │
│  ├── /api/v1/trips/*       ─── trips.py (SSE)               │
│  └── /api/v1/items/*       ─── items.py                     │
├─────────────────────────────────────────────────────────────┤
│  Services                                                   │
│  ├── BaggageService        ─── 수화물 규정 체크             │
│  ├── TripGenerationService ─── AI 트립 생성                 │
│  └── Auth Service          ─── JWT 인증                     │
└─────────────────────────────────────────────────────────────┘
```

---

## API 엔드포인트

### 1. 인증 API (`/api/auth`)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/auth/signup` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/verify` | 인증 확인 |

**사용 예시:**

```typescript
import { authApi } from '@/lib/api';

// 로그인
try {
  const response = await authApi.login({ email, password });
  tokenStorage.set(response.access_token);
} catch (error) {
  console.error('로그인 실패', error);
}
```

---

### 2. 수화물 체커 API (`/api/v1/baggage`)

| 메서드 | 엔드포인트 | 설명 | 인증 |
|--------|-----------|------|------|
| POST | `/api/v1/baggage/check` | 수화물 규정 체크 | 선택 |

**요청 예시:**

```typescript
import { baggageApi } from '@/lib/api';

const result = await baggageApi.check({
  airline: '대한항공',
  product: '맥북',
  value: 15.6,
  unit: 'inch'
});

// 결과
// {
//   carry_on: { verdict: 'allowed', label: '가능 ○', ... },
//   checked: { verdict: 'allowed', label: '가능 ○', ... },
//   checked_at: '2026-07-23T10:30:00'
// }
```

---

### 3. 트립 생성 API (SSE 스트리밍) (`/api/v1/trips`)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/v1/trips/generate` | 트립 생성 스트리밍 (Query) |
| POST | `/api/v1/trips/generate/body` | 트립 생성 스트리밍 (Body) |

**SSE 이벤트 타입:**

| 이벤트 | 설명 |
|--------|------|
| `started` | 생성 시작 |
| `generating` | AI 콘텐츠 생성 중 |
| `content` | 생성된 콘텐츠 전달 |
| `creating` | Trip 엔티티 생성 중 |
| `saving` | DB 저장 중 |
| `completed` | 완료 (최종 Trip 포함) |
| `error` | 에러 발생 |

**사용 예시 (Query 방식):**

```typescript
import { tripsApi } from '@/lib/api';

const cleanup = tripsApi.generateTripStream(
  {
    destination: '제주도',
    purpose: ['관광', '식사'],
    duration_nights: 3,
    departure_month: 8,
    companions: '가족'
  },
  (event) => {
    console.log('이벤트:', event);
  },
  (trip) => {
    console.log('완료된 트립:', trip);
    // 트립 생성 완료 후 아이템 불러오기
    itemsApi.getByTripId(trip.id);
  },
  (error) => {
    console.error('에러:', error);
  }
);

// 연결 종료 시
cleanup();
```

**사용 예시 (Body 방식):**

```typescript
import { tripsApi } from '@/lib/api';

const cleanup = tripsApi.generateTripStreamBody(
  {
    destination: '제주도',
    purpose: ['관광', '식사']
  },
  (event) => {
    // 이벤트 처리
  }
);
```

---

### 4. 아이템 API (`/api/v1/items`)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/items/{trip_id}` | 트립별 아이템 조회 |
| POST | `/api/v1/items` | 아이템 생성 |
| PATCH | `/api/v1/items/{item_id}` | 아이템 수정 |
| DELETE | `/api/v1/items/{item_id}` | 아이템 삭제 |
| PATCH | `/api/v1/items/{item_id}/check` | 체크박스 토글 |
| PATCH | `/api/v1/items/{item_id}/sort` | 정렬 순서 변경 |

**사용 예시:**

```typescript
import { itemsApi } from '@/lib/api';

// 아이템 조회
const { items, total, checked, pending } = await itemsApi.getByTripId(tripId);

// 아이템 생성
const newItem = await itemsApi.create({
  trip_id: tripId,
  category: '의류',
  name: '여름 티셔츠',
  quantity: 3,
  tip: '가벼운 소재 선택',
  baggage_flag: true
});

// 체크박스 토글
await itemsApi.check(itemId, true);

// 정렬 순서 변경
await itemsApi.updateSortOrder(itemId, 5);

// 삭제
await itemsApi.delete(itemId);
```

---

## 인증 흐름

### JWT 인증 방식

1. **로그인** → `access_token` 수신
2. **토큰 저장** → `localStorage`에 저장
3. **요청 시** → `Authorization: Bearer {token}` 헤더 포함
4. **만료 시** → 재로그인 또는 토큰 갱신

### AuthContext 사용법

```typescript
'use client';

import { AuthProvider, useAuth } from '@/lib/auth';

// 루트 레이아웃
export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

// 컴포넌트에서 사용
function MyComponent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  if (isLoading) return <div>로딩 중...</div>;

  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />;
  }

  return (
    <div>
      <p>안녕하세요, {user?.nickname}님!</p>
      <button onClick={logout}>로그아웃</button>
    </div>
  );
}
```

---

## TypeScript 타입

### 주요 타입 정의

```typescript
// 인증
interface UserResponse {
  id: string;
  email: string;
  nickname: string;
  created_at: string;
}

// 수화물 체크
interface VerdictResponse {
  verdict: 'allowed' | 'conditional' | 'forbidden';
  label: string;
  reason: string;
  emoji: string;
  color_code: string;
  is_allowed: boolean;
  is_forbidden: boolean;
}

// 트립
interface Trip {
  id: string;
  title: string;
  destination: string;
  purpose: string[];
  user_id: string;
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions: string[];
  baggage_summary: string[];
  created_at: string;
  updated_at: string;
}

// SSE 이벤트
interface SSEEvent {
  status: 'started' | 'generating' | 'content_generated' |
          'creating' | 'saving' | 'completed' | 'error';
  message?: string;
  destination?: string;
  content?: { cautions: string[]; baggage_summary: string[] };
  trip?: Trip;
}

// 아이템
interface Item {
  id: string;
  trip_id: string;
  category: string;
  name: string;
  quantity: number;
  tip?: string;
  baggage_flag: boolean;
  source?: string;
  checked: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}
```

---

## 에러 처리

### 공통 에러 포맷

```typescript
try {
  await someApiCall();
} catch (error) {
  // 에러 처리
  if (error instanceof Error) {
    console.error(error.message);
    // 사용자에게 메시지 표시
  }
}
```

### HTTP 상태 코드

| 코드 | 설명 | 처리 방법 |
|------|------|-----------|
| 200 | 성공 | 정상 처리 |
| 401 | 인증 실패 | 로그인 페이지로 이동 |
| 403 | 권한 없음 | 권한 부족 메시지 표시 |
| 404 | 리소스 없음 | 404 페이지 표시 |
| 422 | 유효성 검사 실패 | 폼 유효성 메시지 표시 |
| 500 | 서버 오류 | 에러 페이지 표시 |

---

## 환경 설정

### `.env.local`

```env
# 백엔드 API 주소
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

## 디버깅 팁

### 브라우저 개발자 도구

1. **네트워크 탭** → API 요청/응답 확인
2. **콘솔** → 에러 로그 확인
3. **Application 탭** → localStorage 토큰 확인

### 로깅

```typescript
// API 요청 로깅
console.log('API Request:', { endpoint, data });

// SSE 이벤트 로깅
tripsApi.generateTripStream(
  data,
  (event) => {
    console.log('SSE Event:', event.status, event);
  }
);
```

---

## 테스트

### 수동 테스트 체크리스트

- [ ] 로그인/로그아웃 기능
- [ ] 토큰 저장 및 전송
- [ ] 수화물 규정 체크
- [ ] 트립 생성 스트리밍
- [ ] 아이템 CRUD
- [ ] 체크박스 토글
- [ ] 정렬 순서 변경
- [ ] 에러 상황 처리

---

## 참고 파일

- `lib/api.ts` - API 클라이언트 구현
- `lib/types.ts` - TypeScript 타입 정의
- `lib/auth.tsx` - 인증 Context & Hook

---

## 업데이트 내역

| 날짜 | 내용 |
|------|------|
| 2026-07-24 | 초기 연동 구현 완료 |