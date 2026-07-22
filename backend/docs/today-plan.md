# 오늘 작업 계획

## 📅 날짜
2026-07-21 (월)

## 🎯 목표
Week 1 기반 인프라 사전 준비 및 B개발자 독립 작업 완료

---

## ✅ 완료된 작업 (공통 세팅)

- [x] 가상환경 생성 (`backend/venv/`)
- [x] 의존성 설치 (`pip install -r requirements.txt`)
- [x] Docker 컨테이너 실행 (PostgreSQL, Redis)
- [x] `.env` 파일 생성
- [x] Alembic 마이그레이션 준비

---

## 📋 오늘 할 작업 (B개발자)

### 1단계: 인프라 기반 (15분)

| 작업 | 파일 | 상태 | Week 1 투두 |
|------|------|------|-----------|
| DB Base Model | `infrastructure/database/base.py` | ✅ | 사전 준비 |
| Database Config | `shared/config/database.py` | ✅ | 사전 준비 |

### 2단계: 인증 구현 (30분)

| 작업 | 파일 | 상태 | Week 1 투두 |
|------|------|------|-----------|
| Auth Dependency | `interfaces/api/dependencies/auth.py` | ✅ | [x] B: `interfaces/api/dependencies/auth.py` 작성 |

### 3단계: API 스키마 (15분)

| 작업 | 파일 | 상태 | Week 1 투두 |
|------|------|------|-----------|
| Trip Schemas | `interfaces/api/v1/schemas/trip_schemas.py` | ✅ | 사전 준비 |

### 4단계: API 라우터 구조 (10분)

| 작업 | 파일 | 상태 | Week 1 투두 |
|------|------|------|-----------|
| Trip Router | `interfaces/api/v1/routes/trips.py` | ⏳ | [ ] B: `interfaces/api/v1/routes/trips.py` 작성 |
| Repository DI | `interfaces/api/dependencies/repositories.py` | ⏳ | 사전 준비 |

---

## 🔄 대기 중인 작업 (A개발자 완료 필요)

| 작업 | 파일 | 의존 | Week 1 투두 |
|------|------|------|-----------|
| Trip ORM 모델 | `infrastructure/database/models/trip_model.py` | A: `domain/models/trip.py` | [ ] B: `infrastructure/database/models/trip_model.py` 작성 |
| Repository 구현 | `infrastructure/database/repositories/sqlalchemy_trip_repository.py` | A: `domain/repositories/trip_repository.py` | [ ] B: `infrastructure/database/repositories/sqlalchemy_trip_repository.py` 작성 |
| 서비스 연결 | `interfaces/api/v1/routes/trips.py` | A: `application/services/trip_query_service.py` | (위의 Trip Router와 연동) |

---

## 📁 생성할 디렉토리 구조

```
backend/
├── infrastructure/
│   └── database/
│       ├── base.py              [생성 예정]
│       ├── models/
│       │   └── trip_model.py    [대기]
│       └── repositories/
│           └── sqlalchemy_trip_repository.py  [대기]
├── shared/
│   └── config/
│       └── database.py          [생성 예정]
├── interfaces/
│   └── api/
│       ├── dependencies/
│       │   ├── auth.py          [✅ 생성 완료]
│       │   └── repositories.py  [생성 예정]
│       └── v1/
│           ├── routes/
│           │   └── trips.py     [생성 예정]
│           └── schemas/
│               └── trip_schemas.py  [✅ 생성 완료]
```

---

## 🎯 완료 기준

- [x] DB 연결 정상 작동 확인
- [x] 인증 의존성 테스트 통과
- [x] API 스키마 검증 완료
- [ ] 라우터 구조 정의 완료

---

## 📝 비고

- A개발자가 `Trip` 모델과 `TripRepository` 인터페이스를 정의하면 즉시 연동 작업 진행
- 인증은 실제 JWT/JWKS 연동 전에 Mock으로 먼저 구현 가능
- 오늘은 기반 인프라에 집중, 비즈니스 로직은 A개발자에게 맡김

---

*마지막 업데이트: 2026-07-21*