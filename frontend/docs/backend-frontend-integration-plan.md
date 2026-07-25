# 백엔드 API 연동 계획

> 백엔드 `backend/interfaces/api/v1/routes/` 폴더의 API 엔드포인트를 기준으로 프론트엔드 연동 계획입니다.

---

## 📊 현재 상태

### 백엔드 API (구현 완료)
- ✅ 인증 (Auth): 회원가입, 로그인, 로그아웃, 비밀번호 재설정
- ✅ 트립 (Trips): 생성 (SSE 스트리밍), CRUD, 가져오기
- ✅ 아이템 (Items): CRUD, 체크/언체크, 정렬
- ✅ 메모 (Memos): CRUD (최대 2,000자)
- ✅ 수화물 체커 (Baggage): 항공사별 규정 확인

### 프론트엔드 (부분 구현)
- ✅ API 클라이언트 (`lib/api.ts`) - 인증, 트립 생성, 아이템, 수화물
- ✅ 타입 정의 (`lib/types.ts`) - 인증, 트립, 아이템, 수화물
- ✅ 인증 제공자 (`lib/auth.tsx`) - JWT 관리
- ⚠️ **누락**: 트립 CRUD API, 메모 API
- ⚠️ **타입 불일치**: Item의 quantity, baggage_flag 타입

---

## 🎯 구현 계획

### 1단계: TypeScript 타입 업데이트

**파일**: `frontend/lib/types.ts`

#### 1.1 메모 관련 인터페이스 추가

```typescript
// ============ Memo CRUD ============
export interface Memo {
  id: string;
  trip_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface AddMemoCommand {
  trip_id: string;
  content: string; // 최대 2,000자
}

export interface UpdateMemoCommand {
  content: string; // 최대 2,000자
}

export interface MemosByTripResponse {
  trip_id: string;
  memos: Memo[];
  total: number;
}
```

#### 1.2 트립 CRUD 관련 인터페이스 추가

```typescript
// ============ Trip CRUD ============
export interface TripCreateRequest {
  title: string;
  destination: string;
  purpose: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions?: string[];
  baggage_summary?: string[];
}

export interface TripUpdateRequest {
  title?: string;
  destination?: string;
  purpose?: string[];
  duration_nights?: number;
  departure_month?: number;
  companions?: string;
  cautions?: string[];
  baggage_summary?: string[];
}

export interface TripListResponse {
  trips: Trip[];
  total: number;
}
```

#### 1.3 기존 타입 불일치 수정

```typescript
// 백엔드가 string을 반환하므로 타입 수정
export interface AddItemCommand {
  trip_id: string;
  category: string;
  name: string;
  quantity?: string;  // ❌ number → ✅ string
  tip?: string;
  baggage_flag?: string;  // ❌ boolean → ✅ string
  source?: string;
}

export interface Item {
  id: string;
  trip_id: string;
  category: string;
  name: string;
  quantity: string;  // ❌ number → ✅ string
  tip?: string;
  baggage_flag: string;  // ❌ boolean → ✅ string
  source?: string;
  checked: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}
```

---

### 2단계: API 클라이언트 메서드 추가

**파일**: `frontend/lib/api.ts`

#### 2.1 트립 도메인 API 추가

```typescript
// ============ Trip Domain API ============
export const tripsDomainApi = {
  /**
   * 사용자 트립 목록 조회
   * GET /api/v1/trips
   */
  getUserTrips: (): Promise<TripListResponse> =>
    apiClient.get<TripListResponse>('/api/v1/trips'),

  /**
   * 트립 상세 조회
   * GET /api/v1/trips/{trip_id}
   */
  getTripById: (tripId: string): Promise<Trip> =>
    apiClient.get<Trip>(`/api/v1/trips/${tripId}`),

  /**
   * 새 트립 생성
   * POST /api/v1/trips
   */
  createTrip: (data: TripCreateRequest): Promise<Trip> =>
    apiClient.post<Trip>('/api/v1/trips', data),

  /**
   * 트립 수정
   * PATCH /api/v1/trips/{trip_id}
   */
  updateTrip: (tripId: string, data: TripUpdateRequest): Promise<Trip> =>
    apiClient.patch<Trip>(`/api/v1/trips/${tripId}`, data),

  /**
   * 트립 삭제
   * DELETE /api/v1/trips/{trip_id}
   */
  deleteTrip: (tripId: string): Promise<void> =>
    apiClient.delete<void>(`/api/v1/trips/${tripId}`),

  /**
   * 로컬 데이터 가져오기 (마이그레이션용)
   * POST /api/trips/import
   */
  importTrips: (trips: any[]): Promise<any> =>
    apiClient.post<any>('/api/trips/import', { trips }),
};
```

#### 2.2 메모 API 추가

```typescript
// ============ Memo API ============
export const memosApi = {
  /**
   * 트립별 메모 조회
   * GET /api/v1/memos/{trip_id}
   */
  getByTripId: (tripId: string): Promise<MemosByTripResponse> =>
    apiClient.get<MemosByTripResponse>(`/api/v1/memos/${tripId}`),

  /**
   * 메모 생성
   * POST /api/v1/memos
   */
  create: (data: AddMemoCommand): Promise<Memo> =>
    apiClient.post<Memo>('/api/v1/memos', data),

  /**
   * 메모 수정
   * PATCH /api/v1/memos/{memo_id}
   */
  update: (memoId: string, data: UpdateMemoCommand): Promise<Memo> =>
    apiClient.patch<Memo>(`/api/v1/memos/${memoId}`, data),

  /**
   * 메모 삭제
   * DELETE /api/v1/memos/{memo_id}
   */
  delete: (memoId: string): Promise<void> =>
    apiClient.delete<void>(`/api/v1/memos/${memoId}`),
};
```

#### 2.3 import 업데이트

```typescript
import type {
  // 기존 import들
  LoginRequest,
  SignupRequest,
  TokenResponse,
  BaggageCheckRequest,
  BaggageCheckResponse,
  TripGenerateRequest,
  Trip,
  SSEEvent,
  AddItemCommand,
  UpdateItemCommand,
  CheckItemCommand,
  UpdateSortOrderCommand,
  Item,
  ItemsByTripResponse,
  UserResponse,
  
  // 새로 추가
  Memo,
  AddMemoCommand,
  UpdateMemoCommand,
  MemosByTripResponse,
  TripCreateRequest,
  TripUpdateRequest,
  TripListResponse,
} from './types';
```

---

### 3단계: 컴포넌트 API 연동

**파일**: `frontend/app/mockup.tsx`

#### 3.1 import 추가

```typescript
import { authApi, tripsApi, itemsApi, baggageApi, tripsDomainApi, memosApi } from "../lib/api";
```

#### 3.2 Trips 컴포넌트 수정

```typescript
function Trips() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [menu, setMenu] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [renaming, setRenaming] = useState<string | null>(null);

  // 트립 목록 로드
  useEffect(() => {
    if (isAuthenticated) {
      loadTrips();
    }
  }, [isAuthenticated]);

  const loadTrips = async () => {
    setLoading(true);
    try {
      const response = await tripsDomainApi.getUserTrips();
      setTrips(response.trips);
    } catch (err) {
      console.error('트립 목록 로드 실패:', err);
      setError('여행 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 트립 삭제
  const deleteTrip = async (tripId: string) => {
    try {
      await tripsDomainApi.deleteTrip(tripId);
      setTrips(trips.filter(t => t.id !== tripId));
      setConfirm(null);
      setToast("여행이 삭제되었습니다.");
    } catch (err) {
      console.error('여행 삭제 실패:', err);
      setToast("여행 삭제에 실패했습니다.");
    }
  };

  // 트립 이름 변경
  const updateTripTitle = async (tripId: string, newTitle: string) => {
    try {
      await tripsDomainApi.updateTrip(tripId, { title: newTitle });
      setTrips(trips.map(t => t.id === tripId ? { ...t, title: newTitle } : t));
      setRenaming(null);
      setToast("제목이 변경되었습니다.");
    } catch (err) {
      console.error('제목 변경 실패:', err);
      setToast("제목 변경에 실패했습니다.");
    }
  };
  
  // ... 나머지 컴포넌트 코드
}
```

#### 3.3 Trip 컴포넌트 메모 기능 추가

```typescript
function Trip() {
  // ... 기존 상태들
  
  // 메모 관련 상태 추가
  const [memos, setMemos] = useState<Memo[]>([]);

  // 트립 로드 시 메모도 함께 로드
  useEffect(() => {
    if (tripId) {
      loadMemos();
    }
  }, [tripId]);

  const loadMemos = async () => {
    if (!tripId) return;
    try {
      const response = await memosApi.getByTripId(tripId);
      setMemos(response.memos);
    } catch (err) {
      console.error('메모 로드 실패:', err);
    }
  };

  // 메모 추가
  const addMemo = async () => {
    if (!memo.trim() || !tripId) return;
    
    try {
      const newMemo = await memosApi.create({
        trip_id: tripId,
        content: memo.trim()
      });
      setMemos([newMemo, ...memos]);
      setMemo("");
      setToast("저장됨");
    } catch (err) {
      console.error('메모 추가 실패:', err);
      setToast("메모 추가에 실패했습니다.");
    }
  };

  // 메모 삭제
  const deleteMemo = async (memoId: string) => {
    try {
      await memosApi.delete(memoId);
      setMemos(memos.filter(m => m.id !== memoId));
      setToast("메모가 삭제되었습니다.");
    } catch (err) {
      console.error('메모 삭제 실패:', err);
      setToast("메모 삭제에 실패했습니다.");
    }
  };

  // 메모 탭의 메모 목록 업데이트
  {tab === "메모" && <section className="memo-layout">
    <form onSubmit={(e) => { e.preventDefault(); addMemo(); }}>
      <label htmlFor="memo">여행 전에 기억할 것</label>
      <textarea 
        id="memo" 
        value={memo} 
        onChange={(e) => setMemo(e.target.value)} 
        placeholder="예약 번호, 이동 방법, 꼭 가볼 곳을 적어두세요." 
      />
      <button className="primary" disabled={!memo.trim()}>메모 추가</button>
    </form>
    <div className="memo-list">
      {memos.map((value) => (
        <article key={value.id}>
          <p>{value.content}</p>
          <small>{new Date(value.updated_at).toLocaleString('ko-KR')}</small>
          <button onClick={() => deleteMemo(value.id)}>삭제</button>
        </article>
      ))}
      {memos.length === 0 && <p className="empty-memo">메모가 없습니다.</p>}
    </div>
  </section>}
}
```

---

## 📋 백엔드 API 레퍼런스

### 인증 (Authentication)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| `/api/auth/signup` | POST | 회원가입 | ❌ |
| `/api/auth/login` | POST | 로그인 | ❌ |
| `/api/auth/logout` | POST | 로그아웃 | ❌ |
| `/api/auth/verify` | GET | 토큰 검증 | ✅ |
| `/api/auth/reset-request` | POST | 비밀번호 재설정 요청 | ❌ |
| `/api/auth/reset` | POST | 비밀번호 재설정 | ❌ |

**요청 예시:**
```json
// POST /api/auth/login
{
  "email": "user@example.com",
  "password": "Password123"
}
```

**응답 예시:**
```json
{
  "access_token": "jwt-token-here",
  "token_type": "Bearer",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "nickname": "nickname",
    "created_at": "2026-07-23T00:00:00Z"
  }
}
```

---

### 트립 (Trips)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| `/api/v1/trips` | GET | 사용자 트립 목록 | ✅ |
| `/api/v1/trips/{trip_id}` | GET | 트립 상세 | ✅ |
| `/api/v1/trips` | POST | 트립 생성 | ✅ |
| `/api/v1/trips/{trip_id}` | PATCH | 트립 수정 | ✅ |
| `/api/v1/trips/{trip_id}` | DELETE | 트립 삭제 | ✅ |
| `/api/v1/trips/generate` | GET | 트립 생성 (SSE) | ✅ |
| `/api/v1/trips/generate/body` | POST | 트립 생성 (SSE) | ✅ |
| `/api/trips/import` | POST | 트립 가져오기 | ✅ |

**SSE 이벤트 타입:**
- `started`: 생성 시작
- `generating`: AI 콘텐츠 생성 중
- `content`: AI 콘텐츠
- `creating`: 엔티티 생성 중
- `saving`: DB 저장 중
- `completed`: 완료 (trip 객체 포함)
- `error`: 오류 발생

---

### 아이템 (Items)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| `/api/v1/items/{trip_id}` | GET | 트립별 아이템 목록 | ✅ |
| `/api/v1/items` | POST | 아이템 생성 | ✅ |
| `/api/v1/items/{item_id}` | PATCH | 아이템 수정 | ✅ |
| `/api/v1/items/{item_id}` | DELETE | 아이템 삭제 | ✅ |
| `/api/v1/items/{item_id}/check` | PATCH | 체크/언체크 | ✅ |
| `/api/v1/items/{item_id}/sort` | PATCH | 정렬 순서 변경 | ✅ |

**응답 예시:**
```json
{
  "trip_id": "trip-id",
  "items": [
    {
      "id": "item-id",
      "category": "필수",
      "name": "여권",
      "quantity": "1개",
      "tip": "유효기간 6개월 이상 확인",
      "baggage_flag": "carry_on_only",
      "source": "ai",
      "checked": false,
      "sort_order": 0,
      "created_at": "2026-07-23T00:00:00Z",
      "updated_at": "2026-07-23T00:00:00Z"
    }
  ],
  "total": 1,
  "checked": 0,
  "pending": 1
}
```

---

### 메모 (Memos)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| `/api/v1/memos/{trip_id}` | GET | 트립별 메모 목록 | ✅ |
| `/api/v1/memos` | POST | 메모 생성 | ✅ |
| `/api/v1/memos/{memo_id}` | PATCH | 메모 수정 | ✅ |
| `/api/v1/memos/{memo_id}` | DELETE | 메모 삭제 | ✅ |

**제한사항:**
- 메모 내용 최대 2,000자

**요청 예시:**
```json
// POST /api/v1/memos
{
  "trip_id": "trip-id",
  "content": "여행 전에 기억할 메모 내용"
}
```

---

### 수화물 (Baggage)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|----------|--------|------|------|
| `/api/v1/baggage/check` | POST | 수화물 규정 확인 | ⚠️ |

**요청 예시:**
```json
{
  "airline": "대한항공",
  "product": "맥북",
  "value": 15.6,
  "unit": "inch"
}
```

**응답 예시:**
```json
{
  "carry_on": {
    "verdict": "allowed",
    "label": "가능 ○",
    "reason": "기내 반입 가능: 15.6inch",
    "emoji": "✅",
    "color_code": "#10b981",
    "is_allowed": true,
    "is_forbidden": false
  },
  "checked": {
    "verdict": "allowed",
    "label": "가능 ○",
    "reason": "위탁 반입 가능: 15.6inch",
    "emoji": "✅",
    "color_code": "#10b981",
    "is_allowed": true,
    "is_forbidden": false
  },
  "checked_at": "2026-07-23T10:30:00Z"
}
```

---

## 🔧 기술 참고

### 인증 방식
- **타입**: JWT Bearer Token
- **헤더**: `Authorization: Bearer {access_token}`
- **저장소**: `localStorage.getItem('access_token')`

### 에러 코드
- `401`: 인증 실패 (토큰 만료, 유효하지 않음)
- `403`: 권한 없음 (다른 사용자의 리소스 접근)
- `404`: 리소스 없음
- `422`: 유효성 검사 실패
- `500`: 서버 오류

### 백엔드 파일 구조
```
backend/
├── interfaces/api/v1/routes/
│   ├── trips.py          # 트립 스트리밍 API
│   ├── items.py          # 아이템 CRUD API
│   ├── baggage.py        # 수화물 체크 API
│   └── memos.py          # 메모 CRUD API
├── app/api/
│   ├── auth.py           # 인증 API
│   └── trip_domain.py    # 트립 CRUD API
```

---

## ✅ 검증 체크리스트

### 1단계: 타입 업데이트
- [ ] `Memo`, `AddMemoCommand`, `UpdateMemoCommand` 인터페이스 추가
- [ ] `TripCreateRequest`, `TripUpdateRequest`, `TripListResponse` 인터페이스 추가
- [ ] `Item.quantity` 타입: `number` → `string` 수정
- [ ] `Item.baggage_flag` 타입: `boolean` → `string` 수정

### 2단계: API 클라이언트
- [ ] `tripsDomainApi` 객체 추가
- [ ] `getUserTrips()`, `getTripById()`, `createTrip()`, `updateTrip()`, `deleteTrip()`, `importTrips()` 메서드 추가
- [ ] `memosApi` 객체 추가
- [ ] `getByTripId()`, `create()`, `update()`, `delete()` 메서드 추가
- [ ] import 문에 새 타입 추가

### 3단계: 컴포넌트 연동
- [ ] Trips 컴포넌트: API로 트립 목록 로드
- [ ] Trips 컴포넌트: API로 트립 삭제
- [ ] Trips 컴포넌트: API로 트립 제목 변경
- [ ] Trip 컴포넌트: 메모 상태 추가
- [ ] Trip 컴포넌트: API로 메모 로드
- [ ] Trip 컴포넌트: API로 메모 생성
- [ ] Trip 컴포넌트: API로 메모 삭제

### 테스트
- [ ] 회원가입/로그인 작동 확인
- [ ] 트립 생성 (SSE) 작동 확인
- [ ] 트립 목록 조회 작동 확인
- [ ] 메모 추가/삭제 작동 확인
- [ ] 트립 삭제 작동 확인
- [ ] 에러 핸들링 확인

---

## ⏱️ 예상 소요 시간

| 단계 | 작업 | 시간 |
|------|------|------|
| 1 | TypeScript 타입 업데이트 | 10분 |
| 2 | API 클라이언트 메서드 추가 | 15분 |
| 3 | 컴포넌트 API 연동 | 30분 |
| 4 | 테스트 및 디버깅 | 30분 |
| **합계** | | **85분** |

---

## 📚 참고 링크

- 백엔드 API 라우트: `backend/interfaces/api/v1/routes/`
- 프론트엔드 API 클라이언트: `frontend/lib/api.ts`
- 프론트엔드 타입 정의: `frontend/lib/types.ts`
- 프론트엔드 메인 컴포넌트: `frontend/app/mockup.tsx`