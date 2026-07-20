# 트립킷 프론트엔드 목업 프롬프트

프로젝트명: 트립킷 (TripKit)
목적: UI/UX 테스트용 프론트엔드 목업 완결
서비스 유형: AI 여행 준비물 리스트 & 수화물 규정 체크 웹서비스
MVP 범위: 여행 정보 입력 화면(목적지/목적/선택 정보), AI 리스트 결과 화면(체크리스트·주의사항·메모 탭 + 수화물 규정 요약), 수화물 체커 화면(판정 카드), 내 여행 목록 화면, 로그인/회원가입 화면

[중요 선언]
이 작업은 UI/UX 테스트용 프론트엔드 목업이다.
- 어떤 서버 로직도 새로 만들지 않는다.
- 어떤 데이터베이스도 생성하지 않는다.
- 어떤 API route도 새로 생성하지 않으며, 기존 `app/api/`가 있다면 수정하지도 호출하지도 않는다.
- 어떤 외부 요청도 하지 않는다. Anthropic API(AI 리스트 생성) 호출 금지 — AI 생성은 로딩 시뮬레이션 + 더미 JSON으로 대체한다.
- fetch/axios 같은 네트워크 코드를 만들지 않는다.
- 환경변수를 요구하지 않는다. (`ANTHROPIC_API_KEY`, `DATABASE_URL`, `JWT_SECRET` 포함 — 목업 단계에서는 전부 불필요)
- 실제 인증 시스템을 만들지 않는다. 로그인은 로컬 상태 토글로만 시뮬레이션한다.
- 새 의존성을 설치하지 않는다. (Next.js + Tailwind만 사용)

모든 데이터는 로컬 JSON 더미 파일(`data/routes/*.json`)에서만 가져온다.
모든 인터랙션(체크, 추가, 삭제, 판정, 로그인)은 로컬 상태 변화로만 시뮬레이션한다.
AI 리스트 생성은 **로딩 1.5초 시뮬레이션 → trip.json 렌더링**으로 대체한다.
수화물 판정은 **더미 판정 테이블(baggage.json)에서 품목명 매칭**으로 대체하며, 매칭 실패 시 "AI 판정" 라벨이 붙은 기본 더미 결과를 보여준다.
기존 `lib/`, `app/api/`의 실제 로직이 있다면 삭제·수정하지 않는다. 목업은 UI 레이어만 만드는 작업이다.

────────────────────────────────────────────────────────
[PRD 요약]
────────────────────────────────────────────────────────
1. What: 목적지·여행 목적을 입력하면 AI가 맞춤 준비물 체크리스트 + 여행지 주의사항 + 수화물 규정 요약을 생성해주고, 제품명·용량 입력으로 기내 반입/위탁 가능 여부를 판정하는 수화물 체커를 제공하는 여행 준비 서비스. (전체 PRD: `docs/PRD.md`)
2. Value: "검색하고 짜깁기하는 여행 준비를, 입력 한 번으로 끝내주는 서비스". 블로그 여러 개 뒤질 필요 없이 내 여행 맥락(어디로·왜·언제·며칠)에 맞는 리스트를 즉시 받는다.
3. JTBD: 여행자는 템플릿이 아니라 "이번" 여행에 맞는 준비물을 원하며, "이거 기내 반입 되나?"를 커뮤니티에 묻지 않고 즉시 확인하고 싶어 한다.
4. Primary Personas: 20~30대 해외 자유여행자(1차, LCC 수화물 규정에 민감), 출장 잦은 직장인(2차), 가족 단위 여행자(3차).
5. Non-Goals: 항공권/숙소 예약, 일정 짜기, 경비 정산, 공유/협업 편집, 소셜 기능, 실제 AI·DB·인증 연동(이번 목업 단계).
6. MVP Metrics: 모든 라우터의 더미 데이터 정상 렌더링, 체크리스트 체크/추가/삭제 로컬 상태 전이, 수화물 체커 판정 카드 전환, 로그인 상태 토글에 따른 UI 분기, 리스트 생성 로딩 시뮬레이션 정상 동작.

────────────────────────────────────────────────────────
[라우터 목록]
────────────────────────────────────────────────────────
- "/" (public, 홈 — 여행 정보 입력 + 수화물 체커 바로가기 + 최근 여행)
- "/trip" (public, 리스트 결과/여행 상세 — 체크리스트·주의사항·메모 탭 + 진행률 + 규정 요약)
- "/baggage" (public, 수화물 체커 — 품목 검색 + 판정 카드 + 자주 찾는 품목 칩)
- "/trips" (public, 내 여행 목록 — 로그인 시뮬레이션 상태에서만 카드 노출)
- "/login" (public, 로그인/회원가입 — 탭 전환, 실제 인증 없음)

────────────────────────────────────────────────────────
[공통 UI 규칙]
────────────────────────────────────────────────────────
- 전체 테마: 여행 감성 클린 톤 (Warm White `#fafaf7` 배경, 딥 트래블 블루(trip `#1c5d99`) 메인, 앰버(`#f59e0b`) 포인트). Tailwind 토큰으로 trip/amber/ink/line 정의해 사용한다.
- 판정 색상 규칙(고정): 가능 ○ `#16a34a`, 조건부 △ `#f59e0b`, 불가 ✕ `#dc2626`. 규정 뱃지(⚠)는 앰버 배경.
- Header: 로고(트립킷 ✈) + "리스트 만들기 / 수화물 체커 / 내 여행" 탭 + 우측 로그인 버튼(로그인 시뮬레이션 시 닉네임 표시). 모든 라우터 공통, "/"는 히어로 영역과 병행.
- Footer: 없음 (모바일 우선 꽉 찬 화면). 단, 수화물 관련 화면 하단에는 고지 문구 고정 표기("본 판정은 국토교통부 고시 및 IATA 기준 참고 정보입니다. 최종 확인은 이용 항공사 안내를 따르세요.").
- 버튼: 라운드, Hover 시 약간의 scale up. 주요 CTA(리스트 만들기, 확인)는 trip 배경 + 흰 텍스트.
- 입력창: 연한 배경 + 라운드의 깔끔한 스타일. 여행 목적은 선택형 칩(선택 시 trip 배경 반전) + 자유 입력 병행.
- 체크리스트: 카테고리 아코디언, 체크 시 취소선 + 흐림 처리, 진행률 바(예: 8/26 · 31%) 상단 고정.
- Loading UI: 비행기 이륙 애니메이션 또는 원형 스피너 + "리스트를 만들고 있어요…" (1.5초 시뮬레이션).
- Empty UI: 상황별 문구 ("아직 저장된 여행이 없어요", "검색 결과가 없어요 — AI 판정으로 확인해드릴게요").
- Error UI: "리스트 생성에 실패했어요. 잠시 후 다시 시도해주세요." + [다시 시도] 버튼.
- Modal: 항목 삭제 확인·다시 생성 옵션은 화면 하단 Bottom Sheet (모바일), 데스크톱에서는 중앙 다이얼로그.
- 모든 UI 텍스트는 한국어, PRD 문구를 우선 사용 ("어디로 떠나세요?", "이거 기내 반입 되나요?", "리스트를 저장하려면 로그인이 필요합니다.").
- 시의성 정보(`confidence: "check_required"`)에는 "출발 전 확인" 뱃지를 붙인다.
- AI 생성 항목(source: "ai")과 사용자 추가 항목(source: "user")은 아이콘 또는 라벨로 구분 표시한다.
- 로그인 시뮬레이션: 전역 로컬 상태(예: zustand 없이 React Context 또는 localStorage 플래그) 하나로 관리. 로그인하면 닉네임 "여행자"로 고정.

────────────────────────────────────────────────────────
[라우터별 JSON]
────────────────────────────────────────────────────────

1. /data/routes/home.json
{
  "__mock": { "mode": "success" },
  "page": {
    "title": "트립킷",
    "tagline": "입력 한 번으로 끝내는 여행 준비",
    "prompt": "어디로 떠나세요?"
  },
  "view": {
    "placeholders": { "destination": "예: 일본 삿포로, 다낭, 제주도" },
    "purposeChips": ["휴양", "관광", "스키", "서핑/수영", "트레킹", "출장", "배낭여행", "가족여행", "촬영"],
    "optionalFields": {
      "durationLabel": "기간 (박수)",
      "monthLabel": "출발 월",
      "companionOptions": ["혼자", "커플", "친구", "가족·유아 동반"]
    },
    "recentTrips": [
      { "id": "sapporo-ski", "title": "삿포로 스키 여행", "meta": "12월 · 진행률 8/26" },
      { "id": "danang-family", "title": "다낭 가족 휴양", "meta": "7월 · 진행률 23/23 ✓" }
    ],
    "baggageShortcut": {
      "title": "이거 기내 반입 되나요?",
      "subtitle": "수화물 체커 바로가기",
      "popularChips": ["보조배터리", "선크림", "라이터", "전자담배", "향수"]
    }
  }
}

2. /data/routes/trip.json
{
  "__mock": { "mode": "success" },
  "page": {
    "tripTitle": "삿포로 스키 여행",
    "meta": "12월 · 4박 5일 · 친구 2명",
    "progress": { "checked": 8, "total": 26 }
  },
  "view": {
    "tabs": ["체크리스트", "주의사항", "메모"],
    "categories": [
      {
        "name": "필수",
        "items": [
          { "id": "c1-1", "name": "여권", "quantity": null, "tip": "유효기간 6개월 이상 확인", "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c1-2", "name": "항공권 e-티켓", "quantity": null, "tip": null, "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c1-3", "name": "여행자보험 증서", "quantity": null, "tip": null, "baggageFlag": null, "source": "ai", "checked": false },
          { "id": "c1-4", "name": "보조배터리", "quantity": "1개", "tip": "추위에 배터리가 빨리 닳으므로 필수", "baggageFlag": "carry_on_only", "source": "ai", "checked": false }
        ]
      },
      {
        "name": "의류",
        "items": [
          { "id": "c2-1", "name": "스키복 상하의", "quantity": "1벌", "tip": null, "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c2-2", "name": "히트텍 상하의", "quantity": "3벌", "tip": null, "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c2-3", "name": "두꺼운 양말", "quantity": "5켤레", "tip": null, "baggageFlag": null, "source": "ai", "checked": false },
          { "id": "c2-4", "name": "방수 장갑", "quantity": "1켤레", "tip": null, "baggageFlag": null, "source": "ai", "checked": false },
          { "id": "c2-5", "name": "비니/넥워머", "quantity": null, "tip": null, "baggageFlag": null, "source": "ai", "checked": false }
        ]
      },
      {
        "name": "세면/위생",
        "items": [
          { "id": "c3-1", "name": "여행용 세면도구 세트", "quantity": null, "tip": "기내 반입은 개당 100ml 이하", "baggageFlag": "restricted", "source": "ai", "checked": true },
          { "id": "c3-2", "name": "립밤/핸드크림", "quantity": null, "tip": "건조한 실내 대비", "baggageFlag": null, "source": "ai", "checked": false },
          { "id": "c3-3", "name": "콘택트렌즈 세척액", "quantity": "1개", "tip": null, "baggageFlag": "restricted", "source": "user", "checked": false }
        ]
      },
      {
        "name": "전자기기",
        "items": [
          { "id": "c4-1", "name": "돼지코 어댑터", "quantity": "1개", "tip": "일본 A타입, 110V", "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c4-2", "name": "충전 케이블", "quantity": null, "tip": null, "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c4-3", "name": "고글", "quantity": "1개", "tip": "설맹 방지", "baggageFlag": null, "source": "ai", "checked": false }
        ]
      },
      {
        "name": "의약품",
        "items": [
          { "id": "c5-1", "name": "상비약 (감기약·진통제)", "quantity": null, "tip": null, "baggageFlag": null, "source": "ai", "checked": true },
          { "id": "c5-2", "name": "핫팩", "quantity": "10개", "tip": "대량 반입은 제한될 수 있음", "baggageFlag": "restricted", "source": "ai", "checked": false }
        ]
      },
      {
        "name": "목적지 특화",
        "items": [
          { "id": "c6-1", "name": "방한 부츠", "quantity": null, "tip": "빙판길 미끄럼 방지", "baggageFlag": null, "source": "ai", "checked": false },
          { "id": "c6-2", "name": "현금 (엔화)", "quantity": null, "tip": "소규모 식당은 현금 필요", "baggageFlag": null, "source": "ai", "checked": false }
        ]
      }
    ],
    "cautions": [
      { "category": "기후", "text": "12월 삿포로는 평균 -4℃이며 폭설로 항공편이 지연될 수 있습니다.", "confidence": "stable" },
      { "category": "문화/관습", "text": "대부분 상점에서 카드 사용이 가능하지만 소규모 식당은 현금이 필요합니다.", "confidence": "stable" },
      { "category": "전압/통신", "text": "일본은 110V A타입 플러그를 사용합니다. 돼지코 어댑터가 필요합니다.", "confidence": "stable" },
      { "category": "위생", "text": "수돗물 음용이 가능하지만 민감한 경우 생수를 권장합니다.", "confidence": "stable" },
      { "category": "출입국", "text": "일본은 무비자 90일 체류가 가능합니다.", "confidence": "check_required" }
    ],
    "cautionNotice": "비자·출입국 규정은 수시로 변경됩니다. 출발 전 외교부 해외안전여행 및 해당국 공관 공지를 확인하세요.",
    "baggageSummary": [
      { "item": "보조배터리", "rule": "위탁 불가, 기내 반입만 가능 (100Wh 이하)", "severity": "warning" },
      { "item": "세면도구/화장품", "rule": "기내 반입은 개당 100ml 이하", "severity": "warning" },
      { "item": "스키 장비", "rule": "위탁 처리, 항공사별 스포츠 장비 요금 확인", "severity": "info" }
    ],
    "memos": [
      { "id": "m1", "content": "루스츠 리조트 리프트권 온라인 선구매 — 현장가보다 15% 저렴", "updatedAt": "1월 3일" },
      { "id": "m2", "content": "공항 → 삿포로역 JR 쾌속 에어포트, 스키 시즌엔 지정석 추천", "updatedAt": "1월 2일" }
    ]
  }
}

3. /data/routes/baggage.json
{
  "__mock": { "mode": "success" },
  "page": {
    "title": "수화물 체커",
    "prompt": "무엇을 가져가시나요?"
  },
  "view": {
    "flightTypes": ["국제선", "국내선"],
    "units": ["ml", "g", "mAh", "Wh", "cm", "개"],
    "popularChips": ["보조배터리", "선크림", "라이터", "전자담배", "향수", "헤어스프레이", "손톱깎이", "상비약", "유아 이유식", "노트북"],
    "recentSearches": ["보조배터리 20000mAh", "선크림 150ml"],
    "notice": "본 판정은 국토교통부 고시 및 일반적인 국제 기준(IATA)을 바탕으로 한 참고 정보입니다. 항공사·출발 국가에 따라 세부 규정이 다를 수 있으니, 최종 확인은 이용 항공사 안내를 따르세요.",
    "verdicts": [
      {
        "match": ["선크림", "sunscreen"],
        "title": "선크림 150ml",
        "carryOn": { "verdict": "forbidden", "label": "불가 ✕", "reason": "액체류는 개별 용기 100ml 이하만 기내 반입할 수 있습니다. 150ml 용기는 내용물이 절반만 남았더라도 반입할 수 없습니다." },
        "checked": { "verdict": "allowed", "label": "가능 ○", "reason": "일반 액체류는 위탁 수화물 제한이 없습니다." },
        "tips": "100ml 이하 용기에 소분하면 기내 반입이 가능합니다. 소분 용기들은 1L 이하 투명 지퍼백 1개에 담아야 합니다.",
        "source": "rule_db",
        "reference": "국토교통부 항공보안 고시"
      },
      {
        "match": ["보조배터리", "배터리", "power bank"],
        "title": "보조배터리 20000mAh (약 74Wh)",
        "carryOn": { "verdict": "allowed", "label": "가능 ○", "reason": "100Wh 이하 리튬이온 배터리는 기내 반입이 가능합니다. (100~160Wh는 항공사 승인 필요, 통상 2개까지)" },
        "checked": { "verdict": "forbidden", "label": "불가 ✕", "reason": "리튬이온 배터리는 화재 위험 때문에 위탁 수화물에 넣을 수 없습니다." },
        "tips": "160Wh 초과는 운송 자체가 불가합니다.",
        "source": "rule_db",
        "reference": "국토교통부 항공보안 고시"
      },
      {
        "match": ["헤어스프레이", "스프레이"],
        "title": "헤어스프레이 300ml",
        "carryOn": { "verdict": "forbidden", "label": "불가 ✕", "reason": "액체·에어로졸 100ml 초과는 기내 반입할 수 없습니다." },
        "checked": { "verdict": "conditional", "label": "조건부 가능 △", "reason": "개당 500ml 이하, 총 2L 이하의 인화성 없는 생활용 에어로졸만 위탁 가능합니다." },
        "tips": "여행용 미니 사이즈(100ml 이하)를 구매하면 기내 반입이 가능합니다.",
        "source": "rule_db",
        "reference": "국토교통부 항공보안 고시"
      },
      {
        "match": ["라이터"],
        "title": "라이터",
        "carryOn": { "verdict": "conditional", "label": "조건부 가능 △", "reason": "일반 라이터는 1인 1개까지 몸에 소지한 경우에만 기내 반입 가능합니다." },
        "checked": { "verdict": "forbidden", "label": "불가 ✕", "reason": "인화성 물질은 위탁 수화물에 넣을 수 없습니다." },
        "tips": "터보(제트) 라이터는 기내·위탁 모두 불가합니다.",
        "source": "rule_db",
        "reference": "국토교통부 항공보안 고시"
      },
      {
        "match": ["손톱깎이"],
        "title": "손톱깎이",
        "carryOn": { "verdict": "allowed", "label": "가능 ○", "reason": "날 길이가 6cm 이하인 생활용 도구는 기내 반입이 가능합니다." },
        "checked": { "verdict": "allowed", "label": "가능 ○", "reason": "위탁 수화물 제한이 없습니다." },
        "tips": null,
        "source": "rule_db",
        "reference": "국토교통부 항공보안 고시"
      }
    ],
    "aiFallback": {
      "title": "{입력값}",
      "carryOn": { "verdict": "conditional", "label": "조건부 가능 △", "reason": "일반적인 기준으로는 조건부 반입 대상입니다. 세부 사양에 따라 달라질 수 있습니다." },
      "checked": { "verdict": "allowed", "label": "가능 ○", "reason": "일반적인 기준으로는 위탁 가능합니다." },
      "tips": "정확한 판정을 위해 용량·사양을 함께 입력해 주세요.",
      "source": "ai",
      "reference": "AI 판정"
    }
  }
}

4. /data/routes/trips.json
{
  "__mock": { "mode": "success" },
  "page": { "title": "내 여행" },
  "view": {
    "trips": [
      { "id": "sapporo-ski", "title": "삿포로 스키 여행", "meta": "12월 · 4박 5일", "progress": { "checked": 8, "total": 26 }, "status": "ongoing" },
      { "id": "danang-family", "title": "다낭 가족 휴양", "meta": "7월 · 3박 4일", "progress": { "checked": 23, "total": 23 }, "status": "done" },
      { "id": "osaka-biz", "title": "오사카 출장", "meta": "완료", "progress": { "checked": 12, "total": 12 }, "status": "done" }
    ],
    "emptyMessage": "아직 저장된 여행이 없어요. 첫 리스트를 만들어보세요!",
    "loginRequired": "리스트를 저장하려면 로그인이 필요합니다. 지금 만든 리스트는 로그인 후 그대로 저장됩니다."
  }
}

5. /data/routes/auth.json
{
  "__mock": { "mode": "success" },
  "page": { "title": "로그인" },
  "view": {
    "tabs": ["로그인", "회원가입"],
    "fields": {
      "login": ["이메일", "비밀번호"],
      "signup": ["이메일", "비밀번호", "비밀번호 확인", "닉네임"]
    },
    "passwordRule": "8자 이상, 영문+숫자 조합",
    "mockNickname": "여행자",
    "errors": {
      "duplicateEmail": "이미 가입된 이메일입니다. 로그인하거나 비밀번호를 재설정하세요.",
      "tooManyAttempts": "비밀번호가 5회 이상 틀렸습니다. 잠시 후 다시 시도하세요."
    }
  }
}

────────────────────────────────────────────────────────
[라우터별 상세]
────────────────────────────────────────────────────────

[Route: "/"]
- 목적: 목적지/여행 목적(+선택 정보) 입력 → 리스트 생성 시뮬레이션 진입점
- 레이아웃: Header -> 히어로(로고+태그라인+"어디로 떠나세요?") -> 목적지 입력창 -> 목적 칩 그리드(+자유 입력) -> 접힘 섹션(기간·출발 월·동행) -> [리스트 만들기] CTA -> 최근 여행 카드(로그인 시뮬레이션 시) -> 수화물 체커 바로가기 카드
- 데이터: home.json 의 page/view 매핑
- 이벤트명: SELECT_PURPOSE_CHIP, TOGGLE_OPTIONAL_FIELDS, SUBMIT_GENERATE, CLICK_RECENT_TRIP, CLICK_BAGGAGE_SHORTCUT
- 클릭 시 변화:
  - 목적 칩 클릭 → 선택 토글 (복수 선택 가능, trip 배경 반전)
  - "▸ 기간·출발 시기·동행 입력 (선택)" 클릭 → 접힘 섹션 펼침
  - [리스트 만들기] 클릭 → 로딩 1.5초 ("리스트를 만들고 있어요…") → "/trip"으로 라우팅
  - 목적지 미입력 시 인라인 에러 "목적지를 입력해 주세요." / 목적 미선택은 통과 (일반 관광 기준 안내 문구)
  - 목적지가 모호한 값(예: "바다")이어도 통과하되 결과 화면 상단에 안내 "목적지를 구체적으로 입력하면 (예: '베트남 다낭') 더 정확한 리스트를 받을 수 있어요."
  - 최근 여행 카드 클릭 → "/trip" 라우팅 (trip.json 그대로 사용)
  - 수화물 체커 카드/칩 클릭 → "/baggage" 라우팅 (칩 클릭 시 해당 품목 판정 결과 프리필)
- 상태 머신: initial -> (submit) loading(1.5초) -> success(라우팅)
- ASCII:
  [ ✈ 트립킷 ]  리스트 만들기 | 수화물 체커 | 내 여행   (로그인)
  어디로 떠나세요?
  목적지 ( 예: 일본 삿포로, 다낭, 제주도 )
  목적  (휴양) (관광) (스키) (출장) (배낭여행) + 직접 입력
  ▸ 기간·출발 시기·동행 입력 (선택)
  [ 리 스 트  만 들 기 ]
  ────────────────
  ✈ 이거 기내 반입 되나요?
    수화물 체커 바로가기 →
    (보조배터리) (선크림) (라이터)

[Route: "/trip"]
- 목적: AI 생성 리스트 결과 확인 + 체크리스트 편집 + 주의사항/메모 열람
- 레이아웃: Header -> 여행 제목(인라인 수정 가능) + 메타 + 진행률 바 -> 탭(체크리스트/주의사항/메모) -> 탭별 콘텐츠 -> 하단 액션 바([다시 생성] / [저장])
  - 체크리스트 탭: 수화물 규정 요약 배너(⚠ 3건) -> 카테고리 아코디언 -> 항목(체크박스+이름+수량+팁+⚠뱃지) -> 카테고리 말미 "+ 항목 추가" 인라인 입력
  - 주의사항 탭: 카테고리 라벨 + 1~2문장 카드 리스트, check_required 항목에 "출발 전 확인" 뱃지, 하단 고지 문구
  - 메모 탭: 메모 카드 리스트(최신순, 수정 시각) + 새 메모 입력창 (자동 저장 시뮬레이션: 입력 멈춤 1초 후 "저장됨" 토스트)
- 데이터: trip.json 의 page/view 매핑. 체크/추가/수정/삭제는 전부 로컬 상태
- 이벤트명: TOGGLE_CHECK, ADD_ITEM, EDIT_ITEM, DELETE_ITEM, SWITCH_TAB, REGENERATE, SAVE_TRIP, ADD_MEMO, DELETE_MEMO, CLICK_BAGGAGE_BADGE
- 클릭 시 변화:
  - 체크박스 클릭 → 체크 토글 + 진행률 바 즉시 갱신 + 취소선 처리
  - "+ 항목 추가" → 인라인 입력창 → 확정 시 항목 추가 (source: "user" 라벨)
  - 항목 길게 누름/휴지통 버튼 → 삭제 + "실행 취소" 토스트 5초 노출 (클릭 시 복원)
  - ⚠ 뱃지 클릭 → "/baggage" 라우팅 (해당 품목 판정 프리필)
  - [다시 생성] 클릭 → Bottom Sheet: "( ) 내가 추가·수정한 항목은 유지하고 나머지만 새로 받기 / ( ) 전체 새로 받기" → 선택 시 로딩 1.5초 → trip.json 다시 렌더 (user 항목 유지 옵션이면 c3-3 유지)
  - [저장] 클릭 → 로그인 시뮬레이션 상태면 "저장됨" 토스트, 비로그인이면 로그인 유도 Bottom Sheet ("리스트를 저장하려면 로그인이 필요합니다.") → [로그인하기] → "/login"
  - 여행 제목 클릭 → 인라인 편집
- 상태 머신: loading(1.5초, 홈에서 진입 시) -> success | error(재시도 버튼) / 탭 전환은 로컬 상태
- ASCII:
  삿포로 스키 여행 ✎          8/26 ▓▓▓░░░░░ 31%
  [체크리스트] [주의사항] [메모]
  ⚠ 이 여행에서 확인할 수화물 규정 3건 ▾
  필수 (2/4) ▾
  ☑ 여권 — 유효기간 6개월 이상 확인
  ☑ 항공권 e-티켓
  ☐ 여행자보험 증서
  ☐ 보조배터리 1개 ⚠기내만
  의류 (2/5) ▸
  + 항목 추가
  [ 다시 생성 ]        [ 저장 ]

[Route: "/baggage"]
- 목적: 제품명(+용량/수치) 입력 → 기내/위탁 판정 카드 표시
- 레이아웃: Header(탭 활성화) -> 국제선/국내선 토글 -> 검색 입력(제품명 + 수치 + 단위 셀렉트 + [확인]) -> 자주 찾는 품목 칩 -> 판정 결과 카드(기내/위탁 2열 + 이유 + 팁 + 출처) -> 최근 검색 이력 -> 하단 고정 고지 문구
- 데이터: baggage.json 의 verdicts 배열에서 입력 품목명 부분 매칭(match 배열). 매칭 실패 시 aiFallback 결과 + "AI 판정" 라벨
- 이벤트명: SUBMIT_CHECK, CLICK_POPULAR_CHIP, TOGGLE_FLIGHT_TYPE, CLICK_RECENT_SEARCH, REPORT_ERROR
- 클릭 시 변화:
  - [확인] 클릭 → 로딩 0.5초 → 판정 카드 표시 (verdict별 색상: ○ 초록 / △ 앰버 / ✕ 빨강)
  - 자주 찾는 품목 칩 클릭 → 입력창 프리필 + 즉시 판정 표시
  - 국제선/국내선 토글 → 토글 상태만 전환 (목업: 판정 결과 동일, 라벨만 변경)
  - 빈 입력으로 [확인] → 인라인 에러 "수화물 품목을 입력해주세요."
  - 규정과 무관한 입력(매칭 실패) → aiFallback 카드 + "AI 판정" 라벨
  - 판정 카드 하단 [오류 신고] 클릭 → 토스트 "목업: 오류 신고는 다음 단계에서 붙어요"
  - 최근 검색 클릭 → 해당 판정 카드 재표시
- 상태 머신: initial(입력 대기 + 칩) -> loading(0.5초) -> success(판정 카드) / 매칭 실패도 success(aiFallback)
- ASCII:
  ✈ 수화물 체커                    [국제선 ▾]
  무엇을 가져가시나요?
  [ 선크림          ] [ 150 ] [ml ▾]  [확인]
  (보조배터리) (라이터) (전자담배) (향수) (상비약)
  ──────────────────
  선크림 150ml                      규칙 DB 판정
  기내 반입          위탁 수화물
    ✕ 불가             ○ 가능
  액체류는 개별 용기 100ml 이하만 기내 반입할 수 있습니다.
  💡 100ml 이하 용기에 소분하면 기내 반입이 가능합니다.
  [오류 신고]
  ──────────────────
  본 판정은 국토교통부 고시 및 IATA 기준 참고 정보입니다.

[Route: "/trips"]
- 목적: 저장된 여행 목록 관리 (로그인 시뮬레이션 상태 분기 확인용)
- 레이아웃: Header(탭 활성화) -> 여행 카드 리스트(제목, 시기, 진행률 바, ⋯ 메뉴) -> [+ 새 여행 만들기] 버튼
- 데이터: trips.json 의 trips 배열. 비로그인 시뮬레이션 상태면 카드 대신 로그인 유도 화면
- 이벤트명: CLICK_TRIP_CARD, OPEN_TRIP_MENU, DELETE_TRIP, RENAME_TRIP, CLICK_NEW_TRIP
- 클릭 시 변화:
  - 여행 카드 클릭 → "/trip" 라우팅 (목업: trip.json 그대로 사용, 제목만 카드 값 반영)
  - ⋯ 메뉴 → 이름 변경(인라인) / 삭제 (확인 다이얼로그 "이 여행을 삭제할까요? 체크리스트와 메모가 함께 삭제됩니다.") → 로컬 상태에서 제거
  - [+ 새 여행 만들기] → "/" 라우팅
  - 비로그인 상태 → "리스트를 저장하려면 로그인이 필요합니다." + [로그인하기] 버튼 → "/login"
- 상태 머신: initial -> success | empty("아직 저장된 여행이 없어요") | loggedOut(로그인 유도)
- ASCII:
  내 여행                          [+ 새 여행]
  ┌──────────────────────┐
  │ 삿포로 스키 여행    12월  ⋯  │
  │ 8/26 ▓▓▓░░░░░           │
  └──────────────────────┘
  ┌──────────────────────┐
  │ 다낭 가족 휴양      7월  ⋯  │
  │ 23/23 ▓▓▓▓▓▓▓▓ ✓        │
  └──────────────────────┘

[Route: "/login"]
- 목적: 로그인/회원가입 UI + 로그인 상태 시뮬레이션 토글
- 레이아웃: 로고 -> 탭(로그인/회원가입) -> 폼 필드 -> CTA 버튼 -> 보조 링크(비밀번호 재설정 — 토스트 처리)
- 데이터: auth.json 의 view 매핑
- 이벤트명: SWITCH_AUTH_TAB, SUBMIT_LOGIN, SUBMIT_SIGNUP, CLICK_RESET_PASSWORD
- 클릭 시 변화:
  - 로그인 제출 → 입력값 검증 없이 로딩 0.5초 → 전역 로그인 상태 true (닉네임 "여행자") → 직전 페이지 또는 "/"로 복귀 + 토스트 "환영해요, 여행자님!"
  - 회원가입 제출 → 비밀번호 8자 미만 시 인라인 에러 (passwordRule 문구) → 통과 시 로그인과 동일 처리 + "임시 리스트를 계정으로 옮겼어요" 토스트 (비로그인 이관 시뮬레이션)
  - 비밀번호 재설정 클릭 → 토스트 "목업: 재설정 메일은 다음 단계에서 붙어요"
  - Header 로그인 상태에서 닉네임 클릭 → 드롭다운 [로그아웃] → 전역 상태 false
- 상태 머신: initial -> submitting(0.5초) -> success(라우팅 복귀)
- ASCII:
  ✈ 트립킷
  [로그인] [회원가입]
  이메일    (            )
  비밀번호  (            )
  [ 로 그 인 ]
  비밀번호를 잊으셨나요?

────────────────────────────────────────────────────────
[사용자 플로우]
────────────────────────────────────────────────────────
1. 리스트 생성
   "/"
   → 목적지 "일본 삿포로" 입력 + SELECT_PURPOSE_CHIP (스키)
   → TOGGLE_OPTIONAL_FIELDS (4박 5일, 12월, 친구)
   → SUBMIT_GENERATE
   → loading(1.5초)
   → "/trip" (체크리스트 + 주의사항 + 규정 요약 렌더)

2. 체크리스트 편집
   "/trip"
   → TOGGLE_CHECK (진행률 바 갱신)
   → ADD_ITEM ("콘택트렌즈 세척액" — user 라벨)
   → DELETE_ITEM (+ 실행 취소 토스트)
   → CLICK_BAGGAGE_BADGE (보조배터리 ⚠)
   → "/baggage" (보조배터리 판정 프리필)

3. 수화물 체커 단독 사용
   "/" 또는 Header 탭
   → "/baggage"
   → CLICK_POPULAR_CHIP (선크림) 또는 직접 입력
   → loading(0.5초)
   → 판정 카드 (기내 ✕ / 위탁 ○ + 이유 + 팁)
   → 매칭 안 되는 품목 입력 → aiFallback + "AI 판정" 라벨 확인

4. 저장 → 로그인 유도 → 내 여행
   "/trip"
   → SAVE_TRIP (비로그인 상태)
   → 로그인 유도 Bottom Sheet → [로그인하기]
   → "/login" → SUBMIT_LOGIN (로컬 상태 토글)
   → "/trip" 복귀 + "저장됨" 토스트
   → Header "내 여행" 탭 → "/trips" (카드 3장 노출)
   → DELETE_TRIP (확인 다이얼로그 → 로컬 제거)

────────────────────────────────────────────────────────
[QA 체크리스트]
────────────────────────────────────────────────────────
□ 라우터 단위 진입 가능 ("/", "/trip", "/baggage", "/trips", "/login")
□ JSON 기반 렌더링 (각 라우터가 `data/routes/*.json` 더미를 화면에 매핑)
□ 네트워크 요청 0건 (개발자 도구 Network 탭에서 API/외부 호출 없음 확인 — AI 호출 없음)
□ 체크리스트 상태 전이 (체크 토글 → 진행률 바 갱신, 항목 추가 → user 라벨, 삭제 → 실행 취소 토스트)
□ 리스트 생성 로딩 시뮬레이션 ("/" 제출 → 1.5초 로딩 → "/trip" 렌더)
□ 다시 생성 옵션 분기 (user 항목 유지 vs 전체 교체 — Bottom Sheet 선택 반영)
□ 수화물 체커 판정 분기 (규칙 매칭 → rule_db 카드 / 매칭 실패 → aiFallback + "AI 판정" 라벨)
□ 판정 색상 규칙 (○ 초록 / △ 앰버 / ✕ 빨강 고정)
□ 로그인 시뮬레이션 분기 (비로그인 저장 → 로그인 유도, 로그인 후 "/trips" 카드 노출, 로그아웃 → loggedOut 화면)
□ 탭 전환 정상 (체크리스트/주의사항/메모 — 로컬 상태 유지)
□ "출발 전 확인" 뱃지 (confidence: "check_required" 항목에만 표시)
□ 고지 문구 고정 노출 (수화물 체커 하단 + 주의사항 탭 하단)
□ Empty/Error 상태 확인 (`__mock.mode`를 "empty"/"error"로 바꿔 UI 분기 렌더링 확인)
□ 네비게이션 정상 (Header 탭 3종 + ⚠ 뱃지 → 체커 프리필 + 최근 여행 → "/trip")
□ 각 라우터 독립 수정 가능 (페이지별 격리된 더미 JSON 사용)
□ 반응형 확인 (모바일: Bottom Sheet + 세로 카드 / 데스크톱: 다이얼로그 + 그리드)
□ 기존 `app/api/`, `lib/` 로직 무변경 (git diff로 확인)
