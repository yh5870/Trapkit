# Trapkit Backend - Claude 가이드

## 📋 작업 흐름 (B개발자)

각 단계는 다음 순서로 진행:

1. **[today-plan.md] 확인** → 다음 작업 확인
2. **작업 소개** → 🎯 목적 / 💡 이유 / 📦 산출물
3. **사용자 "ok"** → 구현 시작
4. **파일 생성** → 실제 코드 작성
5. **[today-plan.md] 업데이트** → 상태 체크 ✅
6. **[today-summary.md] 업데이트** → 목적/이유/산출물 정리

---

## 🎯 B개발자 역할

- ✅ ORM 모델 (SQLAlchemy)
- ✅ 리포지토리 구현
- ✅ 외부 서비스 (Anthropic, Redis)
- ✅ API 라우트 (FastAPI)
- ✅ 미들웨어 (CORS, 인증)
- ✅ 통합 테스트

---

## 📂 디렉토리 구조

```
backend/
├── infrastructure/        # 🔵 B개발자 전담
│   ├── database/
│   │   ├── base.py       # SQLAlchemy Base
│   │   └── models/       # ORM 모델
│   ├── external/         # 외부 서비스
│   └── migrations/       # Alembic 마이그레이션
├── interfaces/           # 🟡 B개발자 전담
│   └── api/
│       ├── v1/routes/    # API 라우트
│       ├── v1/schemas/   # Pydantic 스키마
│       └── dependencies/ # 의존성 주입
├── shared/               # ⚪ 공통
│   └── config/
│       └── database.py   # DB 설정
└── docs/                 # 📝 문서
    ├── CLAUDE.md         # 이 파일
    ├── collaboration-plan.md
    ├── today-plan.md     # 오늘 계획
    └── today-summary.md  # 오늘 요약
```

---

## 🔑 환경변수

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
ANTHROPIC_API_KEY=your-api-key
```

---

## 🚀 개발 시작 전

```bash
cd backend
.\venv\Scripts\activate
docker-compose up -d
```

---

*마지막 업데이트: 2026-07-21*