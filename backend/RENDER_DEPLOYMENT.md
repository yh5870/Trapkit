# Render 배포 가이드

## 🎯 Render 선택 이유

| 장점 | 설명 |
|------|------|
| **CLI 지원** | `render-cli`로 로컬에서 배포 관리 가능 |
| **무료 티어** | 웹 서비스 + PostgreSQL 무료 |
| **GitHub 통합** | 자동 배포 |
| **SSL 자동** | HTTPS 자동 적용 |
| **로드밸런서** | 여러 인스턴스 자동 관리 |

---

## 1️⃣ 설치 및 설정

### 1.1 Render CLI 설치

```bash
# macOS
brew install render

# Windows
winget install render.cli

# npm (크로스 플랫폼)
npm install -g render-cli
```

### 1.2 로그인

```bash
render login
```

브라우저가 열리고 Render 계정에 연동됩니다.

---

## 2️⃣ PostgreSQL 생성

### 2.1 CLI로 데이터베이스 생성

```bash
render create-db trapkit-db \
  --database-postgres \
  --region=oregon \
  --plan=free
```

### 2.2 데이터베이스 연결 정보 확인

```bash
render ps trapkit-db
```

출력에서 `Connection String` 복사:
```
postgresql://postgres:[password]@[host]:[port]/[database]
```

---

## 3️⃣ Web Service 배포

### 3.1 배포 명령어

```bash
render create-service trapkit-backend \
  --env=docker \
  --region=oregon \
  --plan=free \
  --branch=main \
  --repo=RBX-Trapkit-fresh \
  --docker-context=backend \
  --docker-dockerfile=Dockerfile
```

### 3.2 또는 render.yaml 사용 (권장)

프로젝트 루트에 `render.yaml` 생성:

```yaml
services:
  - type: web
    name: trapkit-backend
    env: docker
    region: oregon
    plan: free
    branch: main
    dockerContext: backend
    dockerfilePath: backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: trapkit-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: https://trapkit.onrender.com
      - key: GEMINI_API_KEY
        value: ""  # 선택사항
      - key: GLM_API_KEY
        value: ""  # 선택사항
      - key: REDIS_URL
        value: ""  # 선택사항
    healthCheckPath: /health
    domains:
      - trapkit.onrender.com

databases:
  - name: trapkit-db
    databaseName: trapkit
    user: trapkit_user
    plan: free
```

배포:
```bash
render push
```

---

## 4️⃣ 환경변수 설정

### 4.1 CLI로 환경변수 추가

```bash
# 필수
render env set DATABASE_URL "postgresql://[USER]:[PASS]@[HOST]:[PORT]/[DB]" --service trapkit-backend
render env set JWT_SECRET "[랜덤 32+ 문자열]" --service trapkit-backend
render env set ENVIRONMENT production --service trapkit-backend
render env set CORS_ORIGINS "https://trapkit.onrender.com,http://localhost:3000" --service trapkit-backend

# 선택사항 (AI 서비스)
render env set GEMINI_API_KEY "[Google API Key]" --service trapkit-backend
render env set GLM_API_KEY "[智谱AI API Key]" --service trapkit-backend

# Redis (선택)
render env set REDIS_URL "redis://[HOST]:[PORT]/[DB]" --service trapkit-backend
```

### 4.2 환경변수 확인

```bash
render env list --service trapkit-backend
```

---

## 5️⃣ 마이그레이션 실행

### 5.1 Render Console 접속

```bash
render ssh trapkit-backend
```

### 5.2 마이그레이션 실행

```bash
alembic upgrade head
```

### 5.3 초기 데이터 로드 (baggage_rules)

```bash
# Railway Console에서
python insert_baggage_rules.py
```

---

## 6️⃣ 배포 확인

### 6.1 배포 상태 확인

```bash
render logs trapkit-backend
```

### 6.2 헬스 체크

```bash
curl https://trapkit.onrender.com/health
```

### 6.3 API 문서 접속

```
https://trapkit.onrender.com/docs
```

---

## 7️⃣ 로컬 개발과 배포

### 7.1 로컬에서 배포 테스트

```bash
# 로컬 Docker 빌드 테스트
cd backend
docker build -t trapkit-backend .
docker run -p 8000:8000 trapkit-backend
```

### 7.2 로컬에서 환경변수 테스트

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://[USER]:[PASS]@[HOST]:[PORT]/[DB]" \
  -e JWT_SECRET="test-secret-key-for-development-only" \
  -e ENVIRONMENT=development \
  trapkit-backend
```

---

## 8️⃣ 자동 배포 (GitHub 통합)

### 8.1 GitHub Webhook 설정

Render Dashboard → Settings → Connect GitHub

### 8.2 자동 배포 트리거

```bash
git push origin main
```

GitHub push 시 자동 배포됩니다.

---

## 9️⃣ 모니터링

### 9.1 로그 확인

```bash
# 실시간 로그
render logs -f trapkit-backend

# 마지막 100줄
render logs --lines 100 trapkit-backend
```

### 9.2 메트릭 확인

```bash
render metrics trapkit-backend
```

---

## 🔟 롤백

### 10.1 이전 배포로 롤백

```bash
render rollback trapkit-backend
```

### 10.2 특정 커밋으로 롤백

```bash
render rollback trapkit-backend --commit=[commit-hash]
```

---

## 📊 비용

| 서비스 | 플랜 | 월 비용 | 무료 한도 |
|--------|------|---------|-----------|
| Web Service | Free | $0 | 750시간/월 |
| PostgreSQL | Free | $0 | 90일 후 슬립 |
| **합계** | | **$0** | |

**유료 플랜:**
- Web Service Starter: $7/월
- PostgreSQL: $7/월

---

## 🐛 문제 해결

### 배포 실패

```bash
# 로그 확인
render logs trapkit-backend

# 상태 확인
render status trapkit-backend
```

### 데이터베이스 연결 실패

```bash
# Render Console에서 환경변수 확인
render ssh trapkit-backend
echo $DATABASE_URL
```

### CORS 오류

```bash
# 프론트엔드 도메인 추가
render env set CORS_ORIGINS "https://trapkit.onrender.com,http://localhost:3000" --service trapkit-backend
```

### 마이그레이션 실패

```bash
# 현재 버전 확인
render ssh trapkit-backend
alembic current

# 강제 업데이트
alembic upgrade head
```

---

## 📝 전체 배포 스크립트

```bash
#!/bin/bash

# Render 배포 스크립트

# 1. 로그인
render login

# 2. 데이터베이스 생성
render create-db trapkit-db \
  --database-postgres \
  --region=oregon \
  --plan=free

# 3. 환경변수 설정
DB_URL=$(render ps trapkit-db | grep "Connection String" | awk '{print $3}')

render create-service trapkit-backend \
  --env=docker \
  --region=oregon \
  --plan=free \
  --branch=main \
  --repo=RBX-Trapkit-fresh

# 4. 환경변수 설정
render env set DATABASE_URL "$DB_URL" --service trapkit-backend
render env set JWT_SECRET "$(openssl rand -hex 32)" --service trapkit-backend
render env set ENVIRONMENT production --service trapkit-backend
render env set CORS_ORIGINS "https://trapkit.onrender.com,http://localhost:3000" --service trapkit-backend

# 5. 배포 대기
sleep 60

# 6. 마이그레이션 실행
render ssh trapkit-backend -c "alembic upgrade head"

# 7. 배포 확인
curl https://trapkit.onrender.com/health
```

---

*마지막 업데이트: 2026-07-25*