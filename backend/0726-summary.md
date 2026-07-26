# 2026-07-26 작업 요약
# 필드명 정합성 점검 · 진행률 집계 · 배포(Render + Vercel)

전날(`0725`) 고친 `cautions` 필드명 불일치와 **같은 패턴**이 다른 곳에도 남아 있는지 점검하는 것으로 시작해,
백엔드 진행률 집계 추가와 프로덕션 배포까지 진행함.

---

# 1부. 필드명 불일치 전수 점검

## 1-1. `baggage_flag` — bool ↔ string (전날 건보다 심각)

**원인**

GLM 프롬프트(`infrastructure/external/glm_client.py`)가 불리언을 요구하고 있었음.

```
"baggage_flag": true/false
```

저장 로직(`interfaces/api/v1/routes/trips.py`)이 이를 문자열로 강제 캐스팅.

```python
baggage_flag=str(item_data.get("baggage_flag", False)),   # → "True" / "False"
```

반면 도메인·스키마가 기대한 값은 `'carry_on_only' | 'checked_only' | 'restricted'`.

프론트(`app/trip/page.tsx`)는 이렇게 렌더링하고 있었음.

```tsx
{item.baggageFlag && (⚠ {item.baggageFlag === "carry_on_only" ? "기내만" : "규정"})}
```

**JS에서 문자열 `"False"` 는 truthy** 이므로, 모든 아이템에 ⚠ 배지가 뜨고 전부 "규정"으로 표시됨.
전날의 `cautions` 건은 데이터가 *안 보이는* 버그였던 반면, 이건 *잘못된 데이터가 전부 보이는* 버그.

**해결**

1. 프롬프트를 문자열 리터럴 4종으로 교체하고 각 값의 의미를 예시와 함께 명시
2. `_normalize_baggage_flag()` 추가 — `cautions` 정규화와 동일한 방어 패턴

```python
@staticmethod
def _normalize_baggage_flag(raw: Any) -> str | None:
    VALID = {"carry_on_only", "checked_only", "restricted"}
    if raw is None:
        return None
    if isinstance(raw, bool):            # 불리언 응답 방어
        return "restricted" if raw else None
    if isinstance(raw, str):
        value = raw.strip().lower()
        if value in VALID:
            return value
        if value in {"false", "none", "null", ""}:
            return None
        if value == "true":
            return "restricted"
    return None
```

3. 라우터의 `str(...)` 강제 캐스팅 제거
4. 프론트에 `normalizeBaggageFlag()` + `BAGGAGE_FLAG_LABEL` 맵 추가 (기존 DB의 `"False"` 잔재 방어)

**검증 결과**

| 입력 `baggage_flag` | 이전 저장값 | 이전 화면 | 수정 후 |
|---|---|---|---|
| `true` | `"True"` | ⚠ 규정 | ⚠ 제한 있음 |
| `false` | `"False"` | **⚠ 규정** (truthy 버그) | 배지 없음 |
| `"carry_on_only"` | 그대로 | ⚠ 기내만 | ⚠ 기내만 |

**부수 수정**
- 프롬프트의 `"quantity": 수량 (기본 1)"` — 따옴표 불일치로 JSON 예시 자체가 invalid였음. 문자열로 정정
- `baggage_summary` 폴백이 **전체 아이템**을 세고 있었음. 화면은 "확인할 수화물 규정이 N건"이라 표기하므로, `baggage_flag`가 있는 아이템만 집계하도록 수정

---

## 1-2. `verdict` enum 값 불일치 (수화물 체커)

| 위치 | 값 |
|---|---|
| 백엔드 `VerdictType` | `allowed` / `conditional` / `forbidden` |
| 프론트 `lib/api/baggage.ts` | `allowed` / `caution` / `prohibited` / `unknown` |
| `globals.css` | `.verdict.allowed` / `.conditional` / `.forbidden` |

`caution` / `prohibited` 는 목업 데이터에만 존재하던 값. 런타임 에러는 없었으나 타입이 거짓이었음.
→ 백엔드 enum과 1:1 대응하는 `VerdictType` 으로 교정.

---

## 1-3. 기타 타입 불일치

| 항목 | 문제 | 조치 |
|---|---|---|
| `Trip.purpose` | 프론트 `string` ↔ 백엔드 `list[str]` | `string[]` 으로 수정 |
| `TripItem.trip_id` | 필수로 선언했으나 목록 응답에 없음 | optional 로 완화, `sort_order` 추가 |
| `Caution.item` | 존재하지 않는 필드에 대한 폴백 | 제거하고 실제 필드인 `confidence` 사용 |

`confidence === "check_required"` 일 때 "확인 필요" 뱃지를 표시하도록 반영 (원래 설계 의도였으나 프론트 타입에서 누락돼 있었음).

---

# 2부. 진행률 집계 (백엔드)

`/trips` 목록의 프로그레스바를 위해 진행률이 필요했으나, `TripResponse` 에는 해당 필드가 없었음.

**설계 판단**

진행률은 **DB에 저장하지 않고 조회 시점에 계산**하기로 결정.
저장 방식은 아이템 추가/삭제/체크마다 동기화가 필요해 값이 실제와 어긋날 위험이 있음 — 1-1의 `baggage_flag` 사고와 같은 유형의 문제를 유발함.

**DB 스키마 변경 없음.** `items` 테이블에 `trip_id`, `checked` 가 이미 인덱스까지 걸린 상태라 마이그레이션 불필요.

**구현 (N+1 회피)**

```python
# ItemRepository (추상) + SQLAlchemyItemRepository (구현)
async def count_by_trip_ids(self, trip_ids: list[TripId]) -> dict[str, tuple[int, int]]
```

`COUNT(*) FILTER` 대신 `SUM(CASE ...)` 사용 — SQLite 등 FILTER 미지원 백엔드 호환.
여행이 몇 개든 `GROUP BY` 쿼리 **1번**.

`TripQueryService` 에 `item_repository` 를 **선택 인자**로 주입해, 기존 호출부 3곳은 수정 없이 동작.

**검증**

| trip | 데이터 | 결과 |
|---|---|---|
| A | 3개 중 2개 체크 | `(3, 2)` |
| B | 2개 중 0개 체크 | `(2, 0)` |
| D | 아이템 없음 | 결과 누락 → 호출측 `(0,0)` 보정 |
| E | 조회 대상 아님 | 제외됨 |

추상 메서드 11개 전부 구현 확인(미구현 시 요청 시점 `TypeError`), 순환 참조 신규 발생 없음.

**부수 수정**
- `app/domain/models/item.py` 의 미사용 `from app.domain.models.trip import Trip` 제거 (잠재적 순환 위험)

---

# 3부. `/trips` 페이지 API 연결

목업 하드코딩(`meta`, `progress`)을 제거하고 실제 `getUserTrips()` 호출로 전환.

동시에 해결한 문제들:

- **`tripkit-trip-id` 미저장** — 카드 클릭 시 `title` 만 저장해 상세 페이지가 직전 여행 데이터를 로드하던 버그
- **`meta` 조립** — 백엔드는 표시용 문자열을 주지 않으므로 `duration_nights`/`departure_month` 로 프론트에서 생성
- **0으로 나누기** — 아이템 0개인 여행에서 `percent` 가 `NaN`
- **이름 변경/삭제가 로컬 state만 변경** — 새로고침하면 되돌아갔음. 실제 API 연결 + 낙관적 업데이트/롤백

> PATCH 응답에는 진행률이 집계되지 않아 0으로 오므로, 이름 변경 후 응답 전체로 목록을 덮어쓰면 프로그레스바가 리셋됨. `title` 만 반영하도록 처리하고 타입 주석에 명시.

---

# 4부. 인증 정책 통일

## 문제

```
생성: POST /api/v1/trips/generate/body/dev  → get_optional_user_id (토큰 불필요)
조회: GET  /api/v1/trips/{id}               → get_current_user_id  (토큰 필수)
```

비로그인 사용자가 여행을 **만들 수는 있는데 볼 수가 없는** 구조. `401 Authorization header missing` 발생.
로그인해도 해당 여행의 `user_id` 가 `'dev-user-id'` 로 박혀 있어 이번엔 403.

## 결정: 로그인 필수로 통일 (A안)

- 프론트 생성 엔드포인트를 `/generate/body` (인증 필수) 로 전환
- 홈에서 비로그인 시 로그인으로 유도 (입력한 목적지 보존 후 복원, CTA 문구 전환)
- `/trip` 진입 시 토큰 없으면 401 전에 로그인으로 유도
- **`/dev` 엔드포인트 2개를 프로덕션에서 차단** — `interfaces/api/dependencies/dev_only.py` 신설

403이 아닌 **404** 반환. 403은 "존재하지만 권한 없음"이라 엔드포인트 존재를 노출함.

| ENVIRONMENT | 결과 |
|---|---|
| `development` / `local` / `test` | 허용 |
| `production` / `staging` | 차단 404 |
| `""` / 미설정 | **차단 404** (안전한 쪽으로 실패) |

**부수 수정**: 홈과 로그인 페이지의 `console.log` 가 **액세스 토큰을 브라우저 콘솔에 출력**하고 있어 제거.

---

# 5부. 배포

## 5-1. 배포 전 사전 정리

**환경변수 이름 불일치 (배포했으면 100% 실패)**

```
코드가 읽는 것   : NEXT_PUBLIC_API_URL        (api-client.ts, trips.ts)
설정이 정의한 것 : NEXT_PUBLIC_API_BASE_URL   (vercel.json, .env.local)
```

값이 무시되고 `http://localhost:8000` 폴백이 적용됨 → 배포된 프론트가 사용자 PC의 localhost를 호출.
로컬에서는 폴백값이 우연히 맞아 드러나지 않았음.

**`vercel.json` 의 `@backend-url` 시크릿 참조 제거** — 존재하지 않는 시크릿이라 빌드 단계에서 실패했을 것.

**`frontend/.gitignore` 신설** — 파일 자체가 없었음.

**`Dockerfile`** — `--port 8000` → `--port ${PORT:-8000}`. Render는 `$PORT` 주입.

## 5-2. `render.yaml` (Blueprint)

```yaml
rootDir         : backend
buildCommand    : pip install -r requirements.txt && alembic upgrade head
startCommand    : uvicorn app.main:app --host 0.0.0.0 --port $PORT
healthCheckPath : /health
region          : singapore
```

시크릿 6종은 `sync: false` 로 두어 저장소에 값이 남지 않도록 함.

DB 상태 확인 결과 `alembic_version` 을 포함해 필요한 테이블이 모두 존재 → 마이그레이션은 현재 no-op이나,
향후 스키마 변경이 배포와 함께 적용되도록 `buildCommand` 에 포함.

## 5-3. 배포 중 발생한 오류 5건

### ① `ModuleNotFoundError: No module named 'app'` (alembic)

`alembic.ini` 에 `prepend_sys_path` 가 없었음.
로컬은 `.venv` 의 **editable 설치**(`_editable_impl_trapkit_backend.pth`) 덕에 동작했으나,
Render는 `requirements.txt` 만 설치하므로 `app` 이 경로에 없음.

```ini
prepend_sys_path = .
```

### ② `InvalidCatalogNameError: database "postgres\n" does not exist`

대시보드에 `DATABASE_URL` 을 붙여넣을 때 **끝에 개행이 포함**됨.

재발 방지로 `strip_whitespace` 밸리데이터 추가 (`DATABASE_URL`, `JWT_SECRET`, API 키 3종, `REDIS_URL`, `ENVIRONMENT`).
특히 `JWT_SECRET` 에 개행이 붙으면 **에러 없이 토큰 검증만 실패**해 원인 파악이 매우 어려움.

### ③ `ModuleNotFoundError: No module named 'sniffio'`

`zhipuai` 의 **미선언 의존성**. 라이브러리가 `import sniffio` 를 하면서 의존성으로 선언하지 않음.

과거에는 `httpx → anyio → sniffio` 로 전이 설치됐으나, **`anyio 4.14` 부터 `sniffio` 가 의존성에서 제외**되어
깨끗한 환경에서 설치 시 누락됨. 로컬 `.venv` 는 이전에 생성되어 `sniffio` 가 남아 있었음.

```
requirements.txt: sniffio>=1.3.0
```

### ④ `SettingsError: error parsing value for field "CORS_ORIGINS"`

pydantic-settings 는 `list[str]` 같은 복합 타입을 환경변수에서 읽을 때 **밸리데이터보다 먼저 `json.loads`** 를 시도함.
`parse_cors_origins` 가 콤마 문자열을 처리하도록 작성돼 있었으나 **도달 불가능한 코드**였음.

로컬 `.env` 는 JSON 배열 형식이라 동작했고, 정작 `.env.example` 은 콤마 형식을 안내하고 있어 문서와 실제가 어긋나 있었음.

```python
CORS_ORIGINS: Annotated[list[str], NoDecode] = [...]
```

`NoDecode` 로 자동 디코딩을 끄고 밸리데이터가 JSON/콤마 두 형식을 모두 처리하도록 수정.

### ⑤ `/health` 307 Temporary Redirect

`@router.get("/")` + `prefix="/health"` 조합이라 정규 경로가 `/health/` 가 되어,
Render 헬스체크(`/health`)가 매번 리다이렉트를 거치고 있었음. `@router.get("")` 을 함께 등록해 해소.

## 5-4. 배포 결과

| | URL |
|---|---|
| 백엔드 (Render) | `https://trapkit-backend.onrender.com` |
| 프론트 (Vercel) | `https://frontend-one-tan-87.vercel.app` |

`CORS_ORIGINS` 에 Vercel 별칭 도메인 등록.
배포별 URL(`frontend-738tcm7l0-...`)은 매 배포마다 변경되므로 **고정 별칭**을 사용해야 함.

---

# 6부. 회원가입 422 오류

배포 후 `POST /api/auth/signup` 이 422 반환. 1부와 **동일한 필드명 불일치 패턴**.

```
프론트가 보냄 : { name, email, password }
백엔드가 요구 : { email, password, nickname }
```

수정 과정에서 3건을 추가 발견:

**① 회원가입 응답에 토큰이 없음**

```python
@router.post("/signup", response_model=UserResponse, ...)   # TokenResponse 아님
```

프론트는 `response.access_token` / `response.user.id` 를 읽으므로, 422를 고쳐도
`response.user` 가 `undefined` 라 `TypeError` 발생 예정이었음.
→ `signupAndLogin()` 추가 (가입 후 자동 로그인해 토큰 확보).

**② 비밀번호 규칙 불일치**

| | 규칙 |
|---|---|
| 백엔드 | 8자 이상 + 영문 포함 + 숫자 포함 |
| 프론트 (기존) | 8자 이상만 |

숫자 없는 비밀번호가 프론트를 통과해 서버에서 422 발생. 동일 규칙으로 사전 검증하도록 수정.

**③ `UserProfile.name`** → `/api/auth/me` 도 `nickname` 을 반환. `UserResponse` 타입으로 통일.

---

# 회고: 반복된 근본 원인

## 1. 로컬 환경이 문제를 가림

오늘 발생한 배포 오류 상당수가 **로컬에서는 재현되지 않는** 유형이었음.

| 오류 | 로컬에서 통과한 이유 |
|---|---|
| `No module named 'app'` | `.venv` 의 editable 설치 |
| `.env` 로딩 실패 | 상대경로 `.env` 가 CWD 기준으로 우연히 맞음 |
| `No module named 'sniffio'` | 오래된 `.venv` 에 잔존 |
| `CORS_ORIGINS` 파싱 | 로컬 `.env` 만 JSON 형식이었음 |
| `NEXT_PUBLIC_API_URL` | 폴백값이 로컬 주소와 일치 |

→ 깨끗한 환경에서의 검증이 필요.

## 2. 설정 파일과 실제 코드의 불일치

`.env.example`(콤마) ↔ 로컬 `.env`(JSON), `vercel.json`(`API_BASE_URL`) ↔ 코드(`API_URL`),
`RENDER_DEPLOYMENT.md`(존재하지 않는 CLI 명령) 등 **문서가 실제와 다른** 사례가 반복됨.

## 3. 스키마 3벌 공존 (미해결)

| 파일 | 기준 | 마운트 | 상태 |
|---|---|---|---|
| `app/schemas/trip.py` | 화면/뷰모델 (`meta`, `progress`) | `/api/trips` | 목업 껍데기 (TODO 11개) |
| `app/schemas/trip_domain.py` | 도메인 리소스 | `/api/v1/trips` | **정본** |
| `interfaces/.../trip_schemas.py` | 도메인 리소스 (중복) | 없음 | 死코드 (import 0곳) |

Swagger에 `/api/trips`(가짜)와 `/api/v1/trips`(진짜)가 나란히 노출되어 혼동을 유발함.
프론트 목업이 `meta`/`progress` 형태였던 것도 초기에 `/api/trips` 기준으로 작성됐기 때문.

---

# 남은 작업

## 우선순위 높음

- [ ] **GLM API 잔액 소진** — `error 1113: 余额不足`
  - rate limit이 아니라 **잔액 부족**이므로 시간이 지나도 자동 복구되지 않음
  - 현재 코드는 "잠시 후 다시 시도해주세요"로 안내하고 있어 **사용자를 오도**함 (수정 필요)
  - 콘솔에서 잔액이 실제로 0인지 확인 필요. Coding Plan 요금제는 지정 도구 외 API 직접 호출 시 한도가 적용되지 않아 잔액이 있어도 1113이 발생할 수 있음
  - `GEMINI_API_KEY` 가 이미 설정돼 있고 `GeminiClient` 도 구현돼 있어, **폴백 연결 시 충전 없이 복구 가능**

- [ ] **SSE 에러 처리 시 `raise` 제거** (`interfaces/api/v1/routes/trips.py`)
  - 에러 이벤트를 클라이언트에 보낸 뒤 다시 `raise` 하여 ASGI 예외로 스트림이 중단됨
  - 정상 처리된 에러인데 로그에 전체 트레이스백이 남아 실제 장애와 구분이 어려움

## 우선순위 중간

- [ ] 스키마 3벌 정리 — `trip_domain.py` 를 정본으로 하고 `interfaces/.../trip_schemas.py` 삭제, `/api/trips`(목업) 처리 방침 결정
- [ ] `interfaces/api/v1/routes/items.py:33` 의 죽은 함수 삭제
  - `__import__('json').json.dumps(...)` → `AttributeError` (호출처 0곳이라 현재는 무해)
- [ ] `RENDER_DEPLOYMENT.md` 갱신 — `render create-db`, `render ps`, `render blueprint launch` 등 실제 CLI에 없는 명령이 기재돼 있음
  - 실제: `render blueprints validate`, `render services create`, `render deploys create`
  - 설치도 npm이 아닌 GitHub 릴리스 바이너리

## 선택

- [ ] Vercel ↔ GitHub 연동 (현재는 `vercel --prod` 수동 배포만 가능. Render만 자동 배포됨)
  - 연동 시 Root Directory를 `frontend` 로 지정 필요
- [ ] Render 무료 플랜 콜드스타트(15분 무활동 시 슬립, 재기동 30~60초) 대응
