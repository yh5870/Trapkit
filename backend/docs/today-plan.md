# B개발자 작업 계획 (Week 4)

## 📅 날짜
2026-07-23 (수) ~ 2026-07-24 (목)

---

## ✅ 추가 작업 완료 (2026-07-23 19:00)

### 회원가입/로그인 DB 연동

| 작업 | 파일 | 상태 |
|------|------|------|
| Profile 모델에 nickname, password_hash 추가 | `infrastructure/database/models/profile_model.py` | ✅ 완료 |
| UserRepository 인터페이스 생성 | `app/domain/repositories/user_repository.py` | ✅ 완료 |
| SQLAlchemyProfileRepository 구현 | `infrastructure/database/repositories/sqlalchemy_profile_repository.py` | ✅ 완료 |
| Repository Dependency 업데이트 | `infrastructure/database/dependencies/repositories.py` | ✅ 완료 |
| auth.py에 DB 연동 코드 추가 | `app/api/auth.py` | ✅ 완료 |
| 마이그레이션 생성 및 적용 | `alembic/versions/20260723_1905-4687670c5452.py` | ✅ 완료 |

**🎯 목적:** 회원가입/로그인이 DB와 연동되어 계정이 저장되도록 구현

**💡 이유:** 기존 코드는 임시 응답만 반환하여 DB에 계정이 저장되지 않음

**📦 산출물:**
- UserRepository 인터페이스 (find_by_email, find_by_id, save, update_password, soft_delete)
- SQLAlchemyProfileRepository 구현
- auth.py에 실제 DB 연동 코드 (signup, login, delete_account)
- DB 테이블에 nickname, password_hash 컬럼 추가

---

## 📋 Week 4 완료 상황

### A개발자 완료 작업 (backend-dev 브랜치)

| 작업 | 파일 | 상태 |
|------|------|------|
| Verdict 값 객체 | `app/domain/value_objects/verdict.py` | ✅ 완료 |
| BaggageRuleRepository 인터페이스 | `app/domain/repositories/baggage_rule_repository.py` | ✅ 완료 |
| BaggageService 도메인 | `app/domain/services/baggage_service.py` | ✅ 완료 |
| normalizer.py | `shared/utils/normalizer.py` | ✅ 완료 |

### B개발자 완료 작업 (week4B 브랜치)

| 작업 | 상태 |
|------|------|
| BaggageRule DB 시드 데이터 (25개 규칙) | ✅ 완료 |
| 캐시 전략 구현 | ✅ 완료 |

---

## 🎯 B개발자 Week 4 작업 계획

### 1단계: 두 브랜치 병합 (10분)

**작업 내용:**

**🎯 목적:**
- A개발자와 B개발자의 Week 4 작업 병합
- 단일 브랜치에서 통합 작업 진행

**💡 이유:**
- A개발자 인터페이스와 B개발자 구현 연동 필요
- 통합 테스트 및 최종 검증을 위해 병합 필수

**📦 작업 단계:**
1. [ ] backend-dev 브랜치로 이동
2. [ ] week4B 브랜치 병합
3. [ ] 충돌 확인 및 해결
4. [ ] 병합 푸시

**📦 명령어:**
```bash
git checkout backend-dev
git merge week4B
git status  # 충돌 확인
git push origin backend-dev
```

---

### 2단계: A개발자 인터페이스 확인 (20분)

**작업 내용:**

**🎯 목적:**
- A개발자가 정의한 인터페이스 확인
- 구현 방법 이해 및 구조 설계

**💡 이유:**
- 인터페이스 계약 준수 필수
- ORM 모델 구조 결정 필요
- 의존성 역전 원칙 유지

**📦 확인 파일:**
```bash
# A개발자 인터페이스 확인
cat app/domain/repositories/baggage_rule_repository.py
cat app/domain/value_objects/verdict.py
cat app/domain/services/baggage_service.py
cat shared/utils/normalizer.py
```

**📦 주요 확인 사항:**
1. BaggageRuleRepository 메서드 시그니처
2. Verdict 값 객체 구조
3. BaggageService 사용 패턴
4. normalizer.py 함수 시그니처

---

### 3단계: BaggageRule ORM 모델 작성 (1시간)

**작업 내용:**

#### BaggageRuleModel (`infrastructure/database/models/baggage_rule_model.py`)

**🎯 목적:**
- BaggageRule 데이터베이스 테이블 매핑
- SQLAlchemy ORM 모델 구현

**💡 이유:**
- A개발자의 BaggageRuleRepository 인터페이스 구현 기반
- DB 시드 데이터와 호환되도록 구조 설계
- 캐싱 전략과 연동 가능한 키 구조

**📦 테이블 구조 (시드 데이터 기반):**
```python
class BaggageRuleModel(Base):
    __tablename__ = "baggage_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_key = Column(String, unique=True, nullable=False, index=True)  # "laptop", "smartphone"
    display_name = Column(String, nullable=False)  # "노트북", "스마트폰"
    aliases = Column(JSON, nullable=False)  # ["macbook", "laptop", "mac"]
    unit = Column(String, nullable=False)  # "inch", "kg", "wh", "ml"
    carry_on_rule = Column(JSON, nullable=False)  # {"max_size": 15.6, "unit": "inch"}
    checked_rule = Column(JSON, nullable=False)  # {"max_weight": 7, "unit": "kg"}
    tips = Column(String, nullable=True)  # "배터리 분리 가능"
    source = Column(String, nullable=False)  # "iata", "airline_policy"
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**📦 작업 단계:**
1. [ ] 시드 데이터 구조 분석
2. [ ] ORM 모델 작성
3. [ ] relationships 확인 (필요 시)
4. [ ] 인덱스 설정 (item_key)
5. [ ] Alembic 마이그레이션 생성

---

### 4단계: SQLAlchemyBaggageRuleRepository 구현 (2시간)

**작업 내용:**

#### SQLAlchemyBaggageRuleRepository (`infrastructure/database/repositories/sqlalchemy_baggage_rule_repository.py`)

**🎯 목적:**
- A개발자의 BaggageRuleRepository 인터페이스 구현
- 도메인 모델 ↔ ORM 모델 변환
- 캐시 연동으로 성능 최적화

**💡 이유:**
- 의존성 역전 원칙 준수
- 비즈니스 로직(DB 쿼리) 캡슐화
- 캐싱으로 DB 쿼리 80% 절감

**📦 인터페이스 구현:**
```python
class BaggageRuleRepository(ABC):
    @abstractmethod
    async def find_by_key(self, key: str) -> BaggageRule | None:
        """키로 규칙 조회."""
        
    @abstractmethod
    async def find_by_normalized_key(self, normalized_key: str) -> BaggageRule | None:
        """정규화된 키로 규칙 조회."""
        
    @abstractmethod
    async def get_all_rules(self) -> list[BaggageRule]:
        """모든 규칙 조회."""
```

**📦 작업 단계:**
1. [ ] 인터페이스 시그니처 확인
2. [ ] find_by_key() 구현 (item_key 조회)
3. [ ] find_by_normalized_key() 구현 (aliases 매칭)
4. [ ] get_all_rules() 구현
5. [ ] _to_domain() 변환 메서드
6. [ ] 캐시 연동 (RedisBaggageClient)
7. [ ] 단위 테스트 작성

---

### 5단계: POST /api/baggage/check 구현 (2시간)

**작업 내용:**

#### Baggage Check Route (`interfaces/api/v1/routes/baggage.py`)

**🎯 목적:**
- 수화물 규정 체크 API 엔드포인트 구현
- BaggageService와 Repository 연동
- 캐싱으로 응답 시간 단축

**💡 이유:**
- 사용자가 수화물 규정 확인 가능
- A개발자의 BaggageService 도메인 로직 사용
- 캐싱으로 비용 절감 ($80+/월)

**📦 API 스펙:**
```yaml
POST /api/v1/baggage/check
Authorization: Bearer <jwt_token>

Request Body:
{
  "airline": "korean air",
  "product": "laptop",
  "value": 15.6,
  "unit": "inch"
}

Response:
{
  "carry_on": {
    "verdict": "allowed",
    "label": "가능 ○",
    "emoji": "✅",
    "reason": "기내 반입 가능"
  },
  "checked": {
    "verdict": "allowed",
    "label": "가능 ○",
    "emoji": "✅",
    "reason": "위탁 반입 가능"
  }
}
```

**📦 작업 단계:**
1. [ ] Pydantic 스키마 작성
2. [ ] 의존성 주입 설정
3. [ ] 엔드포인트 구현
4. [ ] 인증 미들웨어 연결
5. [ ] 에러 처리
6. [ ] 단위 테스트 작성

---

### 6단계: 통합 테스트 작성 (1시간)

**작업 내용:**

#### 통합 테스트 (`tests/interfaces/api/v1/routes/test_baggage.py`)

**🎯 목적:**
- 수화물 체크 기능 종단 간 테스트
- 캐싱 기능 검증
- 에러 시나리오 테스트

**💡 이유:**
- 실제 사용 시나리오 검증
- 캐싱 성능 확인
- 프로덕션 배포 전 품질 확보

**📦 테스트 케이스:**
1. [ ] 정상적인 수화물 체크
2. [ ] 캐시 히트 시나리오
3. [ ] 미지 항공사/제품 처리
4. [ ] 인증 실패 시나리오
5. [ ] 잘못된 요청 처리

---

## 📊 Week 4 작업 일정

| 시간 | 작업 | 상태 | 예상 소요시간 |
|------|------|------|-------------|
| 10:00 - 10:10 | 두 브랜치 병합 | ⏳ 대기 | 10분 |
| 10:10 - 10:30 | A개발자 인터페이스 확인 | ⏳ 대기 | 20분 |
| 10:30 - 11:30 | BaggageRule ORM 모델 | ⏳ 대기 | 1시간 |
| 11:30 - 13:30 | SQLAlchemyBaggageRuleRepository | ⏳ 대기 | 2시간 |
| 14:00 - 16:00 | POST /api/baggage/check | ⏳ 대기 | 2시간 |
| 16:00 - 17:00 | 통합 테스트 작성 | ⏳ 대기 | 1시간 |

**총 예상 시간: 6.5시간**

---

## 🎯 성공 기준

### 완료 체크리스트

### 병합
- [ ] 두 브랜치 병합 완료
- [ ] 충돌 해결 (없을 것으로 예상)
- [ ] 병합 푸시 완료

### ORM 모델
- [ ] BaggageRuleModel 구현 완료
- [ ] 시드 데이터와 호환
- [ ] Alembic 마이그레이션 생성

### Repository
- [ ] BaggageRuleRepository 인터페이스 구현
- [ ] find_by_key() 구현
- [ ] find_by_normalized_key() 구현
- [ ] get_all_rules() 구현
- [ ] 캐시 연동 완료
- [ ] 단위 테스트 통과

### API
- [ ] POST /api/v1/baggage/check 엔드포인트
- [ ] 정상 응답 형식 확인
- [ ] 인증 미들웨어 연동
- [ ] 에러 처리 완료
- [ ] 단위 테스트 통과

### 통합 테스트
- [ ] 정상 시나리오 통과
- [ ] 캐싱 기능 확인
- [ ] 에러 시나리오 통과

---

## 🔄 A개발자와 협업 포인트

### 의존 사항

| A개발자 | B개발자 |
|---------|---------|
| ✅ Verdict 값 객체 완료 | ⏳ ORM 모델 작성 |
| ✅ BaggageRuleRepository 인터페이스 완료 | ⏳ Repository 구현 |
| ✅ BaggageService 도메인 완료 | ⏳ API 구현 |
| ✅ normalizer.py 완료 | ⏳ 캐시 연동 |

### 협업 필요 시점

1. **인터페이스 확인 시**:
   - A개발자의 구조 이해
   - 사용 패턴 확인

2. **테스트 시**:
   - A개발자 도메인 로직 검증
   - 통합 기능 테스트

---

## ✅ 완료 시 다음 단계

### Week 4 완료 후
1. [ ] A개발자에게 Week 4 완료 알리기
2. [ ] 통합 테스트 결과 공유
3. [ ] 배포 준비 (서버리스 환경)
4. [ ] 문서 업데이트

### 전체 프로젝트 완료
1. [ ] 최종 통합 테스트
2. [ ] 배포 및 모니터링
3. [ ] 사용자 피드백 수집

---

*계획 버전: 1.0*
*마지막 업데이트: 2026-07-23*