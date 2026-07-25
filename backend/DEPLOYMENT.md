# 배포 준비 가이드

## 📋 현재 프로젝트 구조

```
backend/
├── app/                      # 도메인 로직
│   ├── main.py              # FastAPI 엔트리 포인트
│   ├── config.py
│   ├── dependencies.py
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── core/
│   └── utils/
├── interfaces/               # API 라우터
│   └── api/
│       ├── v1/
│       │   └── routes/
│       │       ├── baggage.py
│       │       ├── items.py
│       │       └── memos.py
│       └── dependencies/
│           └── auth.py
├── infrastructure/           # 인프라 구성
│   ├── database/
│   └── external/
├── shared/                   # 공유 유틸리티
│   ├── config/
│   └── utils/
├── alembic/                  # DB 마이그레이션
├── tests/                    # 테스트
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── railway.toml
```

## 🚀 배포 방법 추천순위

| 순위 | 서비스 | 장점 | 단점 | 월 비용 |
|------|--------|------|------|--------|
| 1 | **Railway** | 쉬움, GitHub 연동, PostgreSQL 포함 | 트래픽 제한 | $5 |
| 2 | Render | Railway 비슷, 로드밸런서 | | $7 |
| 3 | Vercel | FastAPI 지원 | Docker만 가능 | $20 |
| 4 | AWS | 완전 제어 | 설정 복잡 | 가변 |

---

## 1️⃣ Railway 배포 (권장)

### 1.1 프로젝트 생성

1. [Railway](https://railway.app) 접속
2. `New Project` → `Deploy from GitHub`
3. Repository: `RBX-Trapkit-fresh`
4. Root Directory: `backend`
5. 자동 감지된 Dockerfile 사용

### 1.2 데이터베이스 추가

Railway 프로젝트 내에서:
1. `+ New Service` → `Database` → `PostgreSQL`
2. 이름: `postgres`
3. 생성 후 `Variables` 탭에서 `DATABASE_URL` 자동 생성 확인

### 1.3 환경변수 설정

Railway Dashboard → `Variables` → `New Variable`:

| Key | Value | 설명 |
|-----|-------|------|
| `DATABASE_URL` | `${{postgres.DATABASE_URL}}` | PostgreSQL 연결 (자동 연동) |
| `JWT_SECRET` | `[랜덤 32+ 문자열]` | JWT 서명 키 |
| `GEMINI_API_KEY` | `[Google API Key]` | Gemini AI 서비스 |
| `REDIS_URL` | `[선택]` | Redis 캐싱 |
| `CORS_ORIGINS` | `https://trapkit.vercel.app,http://localhost:3000` | CORS 허용 |
| `ENVIRONMENT` | `production` | 배포 환경 |

**JWT_SECRET 생성 방법:**
```bash
openssl rand -hex 32
```

### 1.4 마이그레이션 실행

**방법 A: Railway Console (권장)**
```bash
# Railway Console → New Terminal
alembic upgrade head
```

**방법 B: Deployment Hook**
1. Railway Settings → `Deploy Hooks`
2. Hook Name: `db-migration`
3. Command: `alembic upgrade head`

### 1.5 배포 확인

```bash
# Health Check
curl https://[project].railway.app/health

# API 문서
https://[project].railway.app/docs
```

---

## 2️⃣ Dockerfile 개선 필요

### 현재 문제점

```dockerfile
# 현재 Dockerfile - 중요 디렉토리 누락
COPY app ./app
# interfaces/, infrastructure/, shared/ 가 누락됨!
```

### 개선된 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 코드 복사 (중요)
COPY app ./app
COPY interfaces ./interfaces
COPY infrastructure ./infrastructure
COPY shared ./shared
COPY alembic.ini .
COPY alembic ./alembic
COPY pyproject.toml .

# Python 경로 설정
ENV PYTHONPATH="/app:$PYTHONPATH"

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3️⃣ 배포 전 체크리스트

### ✅ 코드
- [x] Dockerfile 존재
- [ ] Dockerfile 최신화 (위 개선 버전 적용)
- [ ] requirements.txt 최신 확인
- [ ] alembic.ini 설정 확인
- [ ] railway.toml 설정 확인

### ✅ 환경변수
- [ ] `DATABASE_URL` 설정
- [ ] `JWT_SECRET` 설정 (32자 이상)
- [ ] `GEMINI_API_KEY` 설정
- [ ] `CORS_ORIGINS`에 프론트엔드 도메인 포함
- [ ] `ENVIRONMENT=production` 설정

### ✅ 데이터베이스
- [ ] PostgreSQL 준비 (Railway 또는 Supabase)
- [ ] 마이그레이션 파일 확인
- [ ] 초기 데이터 (baggage_rules) 준비

### ✅ 테스트
- [ ] 로컬에서 빌드 테스트: `docker build -t trapkit-backend .`
- [ ] 로컬에서 실행 테스트: `docker run -p 8000:8000 trapkit-backend`
- [ ] Health 엔드포인트 테스트

---

## 4️⃣ 배포 순서

### Step 1: Railway 프로젝트 생성
```bash
1. Railway 접속
2. New Project → Deploy from GitHub
3. Repository: RBX-Trapkit-fresh
4. Root Directory: backend
5. Deploy
```

### Step 2: PostgreSQL 추가
```bash
1. + New Service → Database → PostgreSQL
2. 생성 완료 대기
3. DATABASE_URL 자동 생성 확인
```

### Step 3: 환경변수 설정
```bash
1. Railway Variables → New Variable
2. 필수 변수들 설정
3. Redeploy 트리거
```

### Step 4: 마이그레이션 실행
```bash
# Railway Console
alembic upgrade head
```

### Step 5: 배포 확인
```bash
1. 배포 완료 대기
2. URL 확인
3. Health check: curl https://[url]/health
4. /docs 접속하여 API 확인
```

---

## 5️⃣ 프론트엔드 연동

### Vercel 배포 후

Railway → Variables 업데이트:
```bash
CORS_ORIGINS=https://[프론트엔드].vercel.app,http://localhost:3000
```

Vercel → Environment Variables:
```bash
NEXT_PUBLIC_API_BASE_URL=https://[백엔드].railway.app
```

---

## 6️⃣ 문제 해결

### 배포 실패 시

```bash
# Railway 로그 확인
railway logs

# 로컬에서 Docker 빌드 테스트
docker build -t test . && docker run test
```

### 데이터베이스 연결 실패

```bash
# Railway Console에서 확인
echo $DATABASE_URL

# 테스트 스크립트 실행
python test_db_connection.py
```

### CORS 오류

```bash
# CORS_ORIGINS에 프론트엔드 도메인 포함
CORS_ORIGINS=https://trapkit.vercel.app,http://localhost:3000
```

### 마이그레이션 실패

```bash
# Railway Console에서
alembic current      # 현재 버전 확인
alembic history      # 마이그레이션 히스토리
alembic upgrade head # 다시 시도
```

---

## 7️⃣ 비용

| 서비스 | 플랜 | 월 비용 | 무료 한도 |
|--------|------|---------|-----------|
| Railway | Starter | $5 | $5 크레딧/월 |
| PostgreSQL | Railway | 포함 | - |
| Supabase | Free | $0 | 500MB |
| **합계** | | **$5** | - |

---

## 8️⃣ 다음 단계

1. [ ] **Dockerfile 업데이트** (위 개선 버전 적용)
2. [ ] **requirements.txt 확인**
3. [ ] **Alembic 마이그레이션 파일 최신화**
4. [ ] **Railway 계정 생성**
5. [ ] **GitHub Railway 연동**
6. [ ] **배포 시작**

---

*마지막 업데이트: 2026-07-25*