# 7월 22일-23일 개발 진행 상황

## 📅 개요

- **날짜**: 2026-07-22 (화) ~ 2026-07-23 (수)
- **진행 단계**: Week 4 수화물 체커 - 인프라 구축
- **참여자**: A개발자 (도메인), B개발자 (인프라)
- **목표**: Week 4 인프라 기반 구축
- **상태**: B개발자 독립 작업 완료, A개발자 대기 중

---

## ✅ 완료된 작업 (7/22)

### 1. 키 발급 계획 수립

**작업 내용:**
- B개발자용 키 발급 계획 문서 작성
- Supabase, Google Gemini, Upstash 키 발급 절차 정의
- 각 서비스의 이유와 필요한 값 정리

**💡 각 서비스 사용 이유:**

| 서비스 | 이유 |
|------|------|
| **Supabase** | PostgreSQL DB, JWT 검증, 자동 profiles 생성 |
| **Google Gemini** | AI 리스트 생성, SSE 스트리밍, 무료 요금제 (1,500 req/day) |
| **Upstash Redis** | AI 응답 캐싱 (비용 절감), 수화물 체커 규칙 캐싱 |

**📋 계획된 키 발급 절차:**
- Supabase: 계정 생성 → 트리거 SQL → Pooler URL 확인
- Anthropic: 콘솔 → 키 생성 → 크레딧 확인
- Upstash: DB 생성 → REST API → 토 생성 → 테스트

---

### 2. AI API 마이그레이션: Anthropic → Google Gemini

**작업 내용:**
- Anthropic API에서 Google Gemini API로 마이그레이션 완료
- 프로젝트 내 모든 Anthropic 관련 코드를 Gemini로 변경

**💡 이유:**
- Anthropic Claude는 유료 API (초기 $5 크레딧 후 유료)
- Google Gemini는 무료 요금제 제공 (1,500 requests/day, 15 requests/min)
- 비용 절감 및 개발 효율성 향상

---

## ✅ 완료된 작업 (7/23)

### Week 3 Item/Memo CRUD 버그 수정

**작업 내용:**
- Week 3 Item/Memo CRUD 구현 후 발견된 6개 버그 수정 완료
- 불변 객체 패턴 관련 버그 수정
- 소유권 확인 로직 수정
- API 상태코드 정정

**🔧 수정된 버그:**

| # | 버그 | 원인 | 해결 방법 | 파일 |
|---|------|------|----------|------|
| 1 | sort_order 업데이트 불가 | `Item.update()`에 sort_order 파라미터 누락 | 파라미터 추가 | [app/domain/models/item.py](app/domain/models/item.py) |
| 2 | 정렬 순서 변경 미반영 | `sort_order_up()` 반환값 저장하지 않음 | `updated = item.sort_order_up(...)` | [interfaces/api/v1/routes/items.py](interfaces/api/v1/routes/items.py) |
| 3 | AttributeError 소유권 확인 | `item.trip_id.user_id` 접근 시도 | Trip 조회 후 user_id 확인 | [items.py](interfaces/api/v1/routes/items.py), [memos.py](interfaces/api/v1/routes/memos.py) |
| 4 | Memo 중복 정의 | item.py에 Memo 존재 | 중복 삭제 | [app/domain/models/item.py](app/domain/models/item.py) |
| 5 | 200 vs 204 상태코드 | None 리턴 시 FastAPI 200 반환 | `Response(204)` 명시적 반환 | [items.py](interfaces/api/v1/routes/items.py), [memos.py](interfaces/api/v1/routes/memos.py) |
| 6 | 빌드 실패 | packages 설정 누락 | packages 명시 | [pyproject.toml](pyproject.toml) |

---

## 📊 전체 진행률 (7/23 기준)

| 주차 | A개발자 | B개발자 | 전체 | 상태 |
|------|---------|---------|------|------|
| **Week 1** | ✅ 100% | ✅ 100% | **100%** | 완료 |
| **Week 2** | ✅ 100% | ✅ 100% | **100%** | 완료 |
| **Week 3** | ✅ 100% | ✅ 100% | **100%** | 완료 (버그 수정 포함) |
| **Week 4** | ⏳ 0% | ⏳ 50% | **25%** | 진행 중 (B개발자 독립 작업 완료) |
| **전체** | **75%** | **63%** | **69%** | 진행 중 |

---

## 🎯 다음 단계 (Week 4: 수화물 체커)

### A개발자 작업 (Day 1-2)
- [ ] Verdict 값 객체 정의
- [ ] BaggageService 도메인 구현
- [ ] normalizer.py 구현 (항공사/제품명 정규화)
- [ ] BaggageRuleRepository 인터페이스

### B개발자 작업 (Day 3-4)
- [x] BaggageRule DB 시드 데이터 ✅ 완료
- [ ] BaggageRule ORM 모델
- [ ] SQLAlchemyBaggageRuleRepository 구현
- [x] 캐시 키 전략 구현 ✅ 완료
- [ ] POST /api/baggage/check 구현

### 공통 작업 (Day 5)
- [ ] 통합 테스트
- [ ] 문서 업데이트

---

## 📝 메모

### 중요 결정사항 (7/21, 7/22, 7/23)

1. **기술 스택**: FastAPI + SQLAlchemy + Supabase + Upstash Redis + Google Gemini
2. **아키텍처**: 클린 아키텍처 (Domain/Infrastructure/Application/Interfaces)
3. **협업 방식**: 의존성 역전 (A가 인터페이스 정의, B가 구현)
4. **인증**: Supabase Auth 위임 + JWKS 검증
5. **캐싱**: Upstash Redis (무료 요금제)
6. **배포**: Vercel 멀티 플랫폼 (프론트+백엔드)

### 오늘 해결한 문제

- [x] Redis 사용 이유 논의 완료
- [x] .env 파일 위치 결정 완료
- [x] 역할 분담 전략 확정
- [x] ORM 모델 구조 설계 완료
- [x] Repository 구현 패턴 확정
- [x] 테스트 작성 방법 확정
- [x] Week 4 영역 침범 문제 해결 (normalizer.py 삭제)

---

## 🚀 다음 단계 (예정)

### 1. A개발자와 협업 (우선)

- [ ] A개발자에게 B개발자 작업 내용 공유
- [ ] A개발자에게 normalizer.py는 본인 영역임을 통보
- [ ] A개발자가 인터페이스 정의할 때까지 대기

### 2. A개발자 작업 (Week 4 Day 1-2)

**목적:** A개발자가 인터페이스 정의

**구현해야 할 것:**
- [ ] `domain/value_objects/verdict.py` (Verdict 값 객체)
- [ ] `domain/services/baggage_service.py` (BaggageService 도메인)
- [ ] `shared/utils/normalizer.py` (항공사/제품명 정규화)
- [ ] `domain/repositories/baggage_rule_repository.py` (인터페이스)

### 3. B개발자 작업 (A개발자 이후)

**목의:** A개발자의 인터페이스 구현

**구현해야 할 것:**
- [ ] `infrastructure/database/models/baggage_rule_model.py`
- [ ] `infrastructure/database/repositories/sqlalchemy_baggage_rule_repository.py`
- [ ] `interfaces/api/v1/routes/baggage.py`
- [ ] Pydantic 스키마 응답 모델 작성
- [ ] Repository 주입 후 서비스 호출
- [ ] 인증 미들웨어 적용

---

## 📞 일일 작업 시간

| 시간 | 작업 | 소요 시간 |
|------|------|----------|
| 09:00 - 11:00 | BaggageRule DB 시드 데이터 작성 | 2시간 |
| 11:00 - 13:00 | 캐시 전략 설계 및 구현 | 2시간 |
| 13:00 - 13:30 | 영역 침범 문제 해결 | 30분 |
| 13:30 - 14:00 | today-summary-B.md 작성 | 30분 |

**총 예상 시간: 5시간**

---

## 🎉 오늘 성공!

### 기본 인프라 완료

```
✅ BaggageRule DB 시드 데이터 (25개 규칙)
✅ 캐시 전략 설계 (RedisBaggageClient)
✅ 캐시 의존성 주입
✅ 영역 침범 문제 해결 (normalizer.py 삭제)
```

### 다음 할 일

1. **A개발자와 커뮤니케이션**: 작업 내용 공유, 인터페이스 정의 요청
2. **A개발자 작업**: Verdict, BaggageService, normalizer.py, BaggageRuleRepository 인터페이스
3. **B개발자 작업**: A개발자 인터페이스 이후 ORM/Repository/API 구현

---

*마지막 업데이트: 2026-07-23*