# 수화물 규정 시드 데이터

## 📋 개요

**작성일자:** 2026-07-23  
**작성자:** B개발자  
**용도:** 수화물 규정 데이터베이스 시드 데이터  
**데이터 출처:** IATA (국제항공운송협회) 규정

---

## 📊 데이터 개요

| 항목 | 수량 |
|------|------|
| 전체 규칙 수 | 25개 |
| 카테고리 수 | 6개 (전자기기, 액체, 의류품, 스포츠, 음식물, 기타) |
| 항공사 호환성 | 모든 항공사 공통 규정 (IATA 기준) |
| 캐시 TTL | 7일 (규칙은 자주 바뀌지 않음) |

---

## 📂 카테고리별 규칙

### 1. 전자기기 (4개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| laptop | 노트북 | 개 | 16x9x9인치 이내 | 전자기기 위탁 |
| tablet | 태블릿 | 개 | 16x9x9인치 이내 | 전자기기 위탁 |
| power_bank | 보조배터리 | 개 | 100Wh 이하 | 160Wh 이하 |
| smartphone | 스마트폰 | 개 | 기내 휴대 | 전원 꺼고 위탁 |

### 2. 액체 (2개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| liquid_container_100ml | 액체 용기 (100ml 이하) | 개 | 100ml/용기, 1L 비닐백 1개 | 규정 없음 |
| alcohol | 주류 | 병 | 100ml/용기, 24% 이하 | 5L 이내 |

### 3. 의류품 (4개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| medicine_liquid | 액체 의약품 | 개 | 100ml/용기, 처방전/의사 | 규정 없음 |
| insulin | 인슐린 | 개 | 기내 휴대, 처방전/의사 | 규정 없음 |
| medical_device | 의료기기 | 개 | 기내 휴대, 처방전/의사 | 규정 없음 |
| baby_formula_liquid | 유아용 조제 분유 | 개 | 100ml/용기 | 규정 없음 |

### 4. 스포츠 용품 (3개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| sports_equipment_racket | 라켓 (스포츠) | 개 | 기내 휴대 | 위탁 가능 |
| sports_equipment_golf_club | 골프채 | 개 | 위탁만 가능 | 전용 백 권장 |
| sports_equipment_skis | 스키 장비 | 세트 | 위탁만 가능 | 위탁 가능 |

### 5. 음식물 (2개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| food_solid | 고체 음식물 | 개 | 기내 휴대 | 위탁 가능 |
| food_frozen | 냉동 음식물 | 개 | 위탁만 가능 | 위탁 가능 |

### 6. 기타 (10개 규칙)

| item_key | display_name | unit | carry_on | checked |
|----------|-------------|------|-----------|---------|
| umbrella | 우산 | 개 | 기내 휴대 (날 날카로우면 위탁) | 위탁 가능 |
| walking_stick | 지팡이 | 개 | 기내 휴대 | 위탁 가능 |
| belt | 벨트 | 개 | 기내 휴대 | 위탁 가능 |
| watch | 시계 | 개 | 기내 휴대 | 위탁 가능 |
| jewelry | 귀금속 | 개 | 기내 휴대 (신고 권장) | 위탁 가능 |
| cosmetics_solid | 고체 화장품 | 개 | 기내 휴대 | 위탁 가능 |
| aerosol | 에어로졸 | 개 | 위탁만 가능 | 개인 사용량 |
| vitamin_pill | 비타민/영양제 | 개 | 기내 휴대 | 위탁 가능 |
| camera | 카메라 | 개 | 기내 휴대 | 위탁 가능 |
| headphone | 헤드폰 | 개 | 기내 휴대 | 위탁 가능 |

---

## 🔑 데이터 구조

### baggage_rules 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | 자동 증가 ID |
| item_key | VARCHAR(100) | 고유 키 (aliases에서 정규화된 결과) |
| display_name | VARCHAR(200) | 표시 이름 |
| aliases | JSON | 별칭 리스트 (예: ["laptop", "맥북"]) |
| unit | VARCHAR(50) | 단위 (개, 병, ml 등) |
| carry_on_rule | JSON | 기내 휴대 규칙 |
| checked_rule | JSON | 위탁 규칙 |
| tips | TEXT | 팁 (NULL 가능) |
| source | VARCHAR(50) | 출처 (기본값: iata) |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### carry_on_rule / checked_rule 구조

```json
{
  "max_size": "16x9x9",  // 최대 크기 (NULL 가능)
  "max_wh": 100,        // 최대 와트시 (NULL 가능)
  "max_ml": 100,        // 최대 용량 (NULL 가능)
  "condition": "조건 설명",
  "note": "추가 노트"
}
```

---

## 📝 규칙 작성 원칙

### 1. IATA 규정 기반

- 모든 규칙은 IATA (국제항공운송협회) 규정을 기준
- 항공사별 차이는 최소화 (국제선 공통)
- 국내선 항공사도 IATA 규정을 따르는 경향

### 2. 명확한 조건 기술

- "조건부" 대신 구체적인 수치로 표현
- "가능" 대신 "조건: ~ 이내 가능" 형식
- 예외 상황을 note로 명시

### 3. 실용성 고려

- 여행자가 자주 묻는 항목 위주
- 자주 반려되는 항목 우선
- 위탁 권장 사유 명확히 설명

### 4. 확장 가능성

- aliases로 다양한 검색어 지원
- source 필드로 추후 데이터 출처 추적 가능
- tips로 실질적인 팁 제공

---

## 🔍 데이터 검증 방법

### 단위 테스트

```sql
-- 총 규칙 수 확인
SELECT COUNT(*) FROM baggage_rules;
-- 예상: 25

-- 카테고리별 개수 확인
SELECT 
    CASE 
        WHEN item_key LIKE '%laptop%' OR item_key LIKE '%tablet%' OR item_key LIKE '%power_bank%' OR item_key LIKE '%smartphone%' THEN '전자기기'
        WHEN item_key LIKE '%liquid%' OR item_key LIKE '%alcohol%' THEN '액체'
        WHEN item_key LIKE '%medicine%' OR item_key LIKE '%insulin%' OR item_key LIKE '%medical%' OR item_key LIKE '%baby%' THEN '의류품'
        WHEN item_key LIKE '%sports%' THEN '스포츠'
        WHEN item_key LIKE '%food%' THEN '음식물'
        ELSE '기타'
    END as category,
    COUNT(*)
FROM baggage_rules
GROUP BY category
ORDER BY category;
```

### 중복 검증

```sql
-- item_key 중복 확인
SELECT item_key, COUNT(*) as count
FROM baggage_rules
GROUP BY item_key
HAVING COUNT(*) > 1;
-- 예상: 0 (item_key는 UNIQUE)
```

### 유효성 검증

```sql
-- JSON 필드 유효성 확인
SELECT item_key, display_name
FROM baggage_rules
WHERE carry_on_rule IS NULL 
   OR checked_rule IS NULL;
-- 예상: 0 (모든 규칙이 JSON 필드를 가짐)
```

---

## 📚 참고 문헌

1. **IATA (국제항공운송협회)**
   - Dangerous Goods Regulations (DGR)
   - Passenger Facilitation Guidelines

2. **각 항공사 규정**
   - 대한항공: [https://www.koreanair.com/k/kr/airport-service/airport/baggage/](https://www.koreanair.com/k/kr/airport-service/airport/baggage/)
   - 아시아나항공: [https://flyasiana.com/C/kr/Contents/Airport-Service/Baggage-Policy](https://flyasiana.com/C/kr/Contents/Airport-Service/Baggage-Policy)
   - 에어서울: [https://www.airseoul.com/web/booking/baggageInfo](https://www.airseoul.com/web/booking/baggageInfo)

3. **수화물 규정 검사 가이드**
   - [공항공사 사이트](https://www.airport.or.kr/www/cus/cus/cus0301/)

---

## ✅ 완료 체크리스트

- [x] 25개 규칙 데이터 작성 ✅
- [x] 6개 카테고리 분류 ✅
- [x] IATA 규정 기반 ✅
- [x] JSON 구조 설계 ✅
- [x] Alembic 마이그레이션 파일 작성 ✅
- [x] 참고 문헌 작성 ✅
- [x] DB 마이그레이션 실행 ✅ (PR #21에서 실행 완료)
- [x] 데이터 검증 ✅ (test_baggage_rule_repository.py 작성 완료)

---

*마지막 업데이트: 2026-07-23 (모든 대기 작업 완료 ✅)*