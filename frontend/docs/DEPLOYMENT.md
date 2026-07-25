# 배포 가이드

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Production Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────┐          ┌─────────────────┐            │
│  │   Vercel        │          │   Railway       │            │
│  │   Frontend      │ ◄──────► │   Backend API   │            │
│  │   (Next.js)     │   HTTP   │   (FastAPI)     │            │
│  │   .vercel.app   │          │   .railway.app  │            │
│  └─────────────────┘          └─────────┬───────┘            │
│                                        │                     │
│                                        │                     │
│                              ┌─────────▼───────┐            │
│                              │   Supabase      │            │
│                              │   PostgreSQL    │            │
│                              └─────────────────┘            │
│                                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Frontend 배포 (Vercel)

### 1.1 Vercel 프로젝트 설정

```bash
# Vercel CLI 설치
npm i -g vercel

# 로그인
vercel login

# 배포
vercel
```

### 1.2 환경 변수 설정

Vercel Dashboard → Settings → Environment Variables:

| 변수명 | 값 | 환경 |
|--------|---|------|
| `NEXT_PUBLIC_API_BASE_URL` | Railway 배포 URL | Production, Preview, Development |

### 1.3 도메인 설정

1. Vercel Dashboard → Domains
2. 도메인 추가: `trapkit.vercel.app` (기본)
3. 커스텀 도메인 추가 가능

### 1.4 배포 명령어

```bash
# 로컬 테스트
vercel dev

# 프리뷰 배포
vercel --prod=false

# 프로덕션 배포
vercel --prod
```

---

## 2. Backend 배포 (Railway)

### 2.1 Railway 프로젝트 생성

1. Railway Dashboard → New Project → Deploy from GitHub
2. Repository 선택: `RBX-Trapkit-fresh/backend`
3. 빌드 설정 자동 감지 (Dockerfile 기반)

### 2.2 환경 변수 설정

Railway Dashboard → Variables:

| 변수명 | 값 | 설명 |
|--------|---|------|
| `DATABASE_URL` | Supabase Connection URL | PostgreSQL 연결 |
| `JWT_SECRET` | 자동 생성됨 | JWT 토큰 서명 |
| `GEMINI_API_KEY` | Google API Key | AI 서비스 |
| `REDIS_URL` | Railway Redis URL | 캐싱 |
| `ENVIRONMENT` | `production` | 배포 환경 |
| `CORS_ORIGINS` | `https://trapkit.vercel.app` | CORS 허용 |

### 2.3 Supabase 연결 설정

1. Supabase Dashboard → Settings → Database
2. Connection String → URI (postgresql://...)

```
postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

3. Railway Variables에 `DATABASE_URL`로 설정

### 2.4 데이터베이스 마이그레이션

Railway Console에서:

```bash
# DB 마이그레이션 실행
alembic upgrade head

# 마이그레이션 확인
alembic current
```

### 2.5 Railway 배포 확인

- Railway Dashboard에서 배포 상태 확인
- 배포 완료 후 Railway URL 확인: `https://[project].railway.app`

---

## 3. Supabase 설정

### 3.1 프로젝트 생성

1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. 프로젝트 설정:
   - Database Name: `trapkit`
   - Region: `Singapore` (추천)
   - Database Password: 안전한 비밀번호 생성

### 3.2 테이블 구조

Alembic 마이그레이션이 자동 생성:

```sql
-- users 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nickname VARCHAR(50),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- trips 테이블
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    purpose TEXT[],
    duration_nights INTEGER,
    departure_month INTEGER,
    companions VARCHAR(100),
    cautions TEXT[],
    baggage_summary TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- items 테이블
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1,
    tip TEXT,
    baggage_flag BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'ai',
    checked BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- baggage_rules 테이블
CREATE TABLE baggage_rules (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    airline VARCHAR(100) NOT NULL,
    product VARCHAR(255) NOT NULL,
    carry_on_allowed BOOLEAN DEFAULT FALSE,
    checked_allowed BOOLEAN DEFAULT TRUE,
    conditions TEXT[],
    tips TEXT[]
);
```

### 3.3 Row Level Security (선택)

```sql
-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- 사용자 정책
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can view own trips"
ON trips FOR SELECT
USING (auth.uid() = user_id);
```

---

## 4. 배포 전 체크리스트

### Frontend
- [ ] `.env.local`에 `NEXT_PUBLIC_API_BASE_URL` 설정
- [ ] API 엔드포인트 HTTPS 확인
- [ ] CORS 헤더 확인
- [ ] Build 테스트: `npm run build`
- [ ] Lighthouse 점수 확인

### Backend
- [ ] `DATABASE_URL` 설정 (Supabase)
- [ ] `GEMINI_API_KEY` 설정
- [ ] `JWT_SECRET` 설정 (또는 자동 생성)
- [ ] `CORS_ORIGINS`에 프론트엔드 도메인 포함
- [ ] Alembic 마이그레이션 실행
- [ ] Health 엔드포인트 테스트

### Database
- [ ] Supabase 프로젝트 생성
- [ ] Connection URL 획득
- [ ] 마이그레이션 실행
- [ ] Connection Pool 설정 (필요 시)

---

## 5. 배포 순서

### 순서 1: Supabase 설정
```bash
# Supabase Dashboard에서 프로젝트 생성
# Connection URL 복사
```

### 순서 2: Railway 배포
```bash
# Railway에 GitHub 연결
# 환경 변수 설정
# 배포 시작
```

### 순서 3: 마이그레이션 실행
```bash
# Railway Console에서
alembic upgrade head
```

### 순서 4: Vercel 배포
```bash
# Vercel에 GitHub 연결
# 환경 변수 설정
# 배포 시작
```

---

## 6. 배포 후 확인

### Backend 확인
```bash
# Health Check
curl https://[your-railway-app].railway.app/health

# API Docs
curl https://[your-railway-app].railway.app/docs
```

### Frontend 확인
- [ ] https://trapkit.vercel.app 접속
- [ ] 로그인 기능 테스트
- [ ] 트립 생성 테스트
- [ ] 수화물 체크 테스트

---

## 7. 도메인 설정 (선택)

### 프론트엔드
```
도메인: trapkit.com
→ Vercel DNS 설정
→ A 레코드: 76.76.21.21
```

### 백엔드
```
도메인: api.trapkit.com
→ Railway Custom Domains
→ CNAME 레코드: [railway-app].railway.app
```

---

## 8. 모니터링

### Vercel
- Dashboard → Analytics
- Web Vitals, 사용자 추적

### Railway
- Dashboard → Metrics
- CPU, Memory, Requests 모니터링

### Supabase
- Dashboard → Database → Logs
- 쿼리 성능, 오류 추적

---

## 9. 롤백 절차

### Vercel
```bash
# 이전 배포로 롤백
vercel rollback
```

### Railway
```bash
# Railway Dashboard
# Deployments → 특정 배포 선택 → Redeploy
```

---

## 10. 비용 추정

| 서비스 | 플랜 | 월 비용 |
|--------|------|---------|
| Vercel | Pro | $20 |
| Railway | Starter | $5 |
| Supabase | Free | $0 |
| **합계** | | **~$25/월** |

---

## 문제 해결

### CORS 오류
```python
# backend/app/config.py
CORS_ORIGINS = [
    "https://trapkit.vercel.app",
    "http://localhost:3000",  # 개발용
]
```

### 데이터베이스 연결 실패
```bash
# Railway Console에서 환경 변수 확인
echo $DATABASE_URL
```

### 빌드 실패
```bash
# 로그 확인
vercel logs
# 또는
railway logs
```

---

## 연락처

배포 관련 문제는:
- 팀 채팅 또는
- GitHub Issues

---

*마지막 업데이트: 2026-07-24*