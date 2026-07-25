# 2025-07-25 작업 요약
# Trapkit 오류 수정 정리

## 1. 주의사항(`cautions`) 카드 "내용이 없습니다" 표시 오류

**원인**
GLM AI 클라이언트(`infrastructure/external/glm_client.py`)의 `_build_prompt()`가 AI에게 아래와 같은 필드명으로 응답하도록 지시하고 있었음.

```json
{"type": "weather|health|safety|other", "message": "주의사항 내용"}
```

반면 API 스키마(`app/schemas/ai.py`의 `AICautions`)와 프론트엔드가 기대하는 필드명은 다음과 같았음.

```json
{"category": "...", "text": "...", "confidence": "stable|check_required"}
```

`_parse_response()`가 AI 응답을 검증 없이 그대로 DB에 저장하다 보니, 프론트엔드가 `caution.text`를 찾지 못해 fallback 문구("내용이 없습니다")를 표시함. DB에는 실제 데이터가 정상적으로 들어 있었음(빈 값 아님).

**해결**
1. `_build_prompt()`의 JSON 응답 형식 지시를 `category` / `text` / `confidence`로 수정
2. `_parse_response()`에 필드 정규화 로직을 추가하여, AI가 구형 필드명(`type`/`message`)으로 응답하더라도 자동 변환되도록 안전장치 마련

```python
normalized_cautions = []
for c in content["cautions"]:
    normalized_cautions.append({
        "category": c.get("category", c.get("type", "other")),
        "text": c.get("text", c.get("message", "")),
        "confidence": c.get("confidence", "stable"),
    })
content["cautions"] = normalized_cautions
```

**참고 / 남은 작업**
- 이 수정은 **새로 생성되는 트립**부터 적용됨
- 기존에 이미 저장된 트립들은 여전히 `{type, message}` 형태로 DB에 남아 있어, 필요 시 별도 마이그레이션 스크립트로 일괄 변환 필요

---

## 2. 백엔드 `ResponseValidationError` (500 에러)

**원인**
FastAPI 라우터의 반환 타입 힌트(`dict[str, list[dict]]`)가 지나치게 엄격하게 지정되어, 문자열이나 정수형 데이터가 섞인 응답을 보낼 때 타입 검증 에러 발생.

**해결**
`lib/api/memos.py` 및 관련 백엔드 라우터(예: `get_memos_by_trip_id`)의 반환 타입을 유연한 `dict` 형태로 수정.

---

## 3. 프론트엔드 API 호출 주소 및 경로 불일치 (`/body`)

**원인**
AI 여행 리스트 생성 엔드포인트는 Request Body를 받기 위해 `/api/v1/trips/generate/body` (또는 개발용 `/body/dev`) 경로를 사용해야 하는데, 프론트엔드에서 경로가 잘못 지정되어 422 또는 404 에러 발생.

**해결**
API 명세서에 맞추어 `generateTripWithStream` 함수의 요청 URL을 정확한 경로로 수정.

---

## 4. API 응답 객체 매핑 오류 (`getTripById`)

**원인**
백엔드는 상세 조회 시 `Trip` 객체 자체를 단일로 반환하는데, 프론트엔드는 `{ trip: Trip }` 형태로 감싸져 올 것으로 예상하여 `response.trip`을 참조 → `undefined` 오류 발생.

**해결**
`getTripById` 함수에서 `response` 객체 자체를 그대로 반환하도록 수정.

---

## 5. React 리스트 렌더링 키(`key`) 중복 및 `undefined-undefined` 경고

**원인**
`cautions`, `baggage_summary` 항목을 `.map()`으로 렌더링할 때 존재하지 않는 속성을 조합해 `key`로 지정하거나 텍스트를 출력하려고 하여 경고 발생.

**해결**
- 배열의 `index`를 결합하여 고유한 `key`(`key={`caution-${index}`}`) 생성하도록 수정
- 백엔드 API 명세에 명시된 정확한 필드명(`category`, `text`, `item`, `rule`)을 사용하도록 프론트엔드 컴포넌트 정돈
- `Caution` 타입에 `item?: string` 등을 추가하여 TypeScript 빌드 에러 방지

---

## 전체 요약

| # | 이슈 | 계층 | 상태 |
|---|---|---|---|
| 1 | 주의사항 카드 필드명 불일치 (`type/message` vs `category/text/confidence`) | 백엔드 (GLM 프롬프트) | 수정안 확정, 파일 반영 필요 |
| 2 | `ResponseValidationError` (500) | 백엔드 (라우터 반환 타입) | 해결 완료 |
| 3 | `/generate/body` 경로 불일치 | 프론트엔드 (API 호출 경로) | 해결 완료 |
| 4 | `getTripById` 응답 매핑 오류 | 프론트엔드 (API 응답 파싱) | 해결 완료 |
| 5 | React key 중복 / `undefined-undefined` 경고 | 프론트엔드 (리스트 렌더링) | 해결 완료 |