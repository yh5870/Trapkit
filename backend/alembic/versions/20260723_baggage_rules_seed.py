"""Baggage Rules Seed Data

수화물 규정 데이터베이스 시드 파일
항공사별 수화물 규정 (50개 이상)
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# upgrade revision
def upgrade() -> None:
    # 수화물 규정 테이블이 존재하지 않으면 생성
    op.execute("""
    CREATE TABLE IF NOT EXISTS baggage_rules (
        id SERIAL PRIMARY KEY,
        item_key VARCHAR(100) UNIQUE NOT NULL,
        display_name VARCHAR(200) NOT NULL,
        aliases JSON NOT NULL,
        unit VARCHAR(50) NOT NULL,
        carry_on_rule JSON NOT NULL,
        checked_rule JSON NOT NULL,
        tips TEXT,
        source VARCHAR(50) NOT NULL DEFAULT 'iata',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_baggage_rules_item_key ON baggage_rules(item_key);
    """)

    # 규칙 데이터 삽입
    baggage_rules = [
        # 전자기기
        {
            "item_key": "laptop",
            "display_name": "노트북",
            "aliases": ["laptop", "맥북", "notebook", "노트북 컴퓨터", "macbook"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": "16x9x9",
                "max_wh": None,
                "max_ml": None,
                "condition": "기내용 16x9x9인치 이내 가능 (약 40x23x23cm)",
                "note": "보안 검색 시 노트북 꺼내야 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "전자기기로 위탁 가능",
                "note": "파손 방지를 위해 케이스에 담아 권장"
            },
            "tips": "보안 검색 대기 시간 단축을 위해 파워 코드를 분리해서 제출",
            "source": "iata"
        },
        {
            "item_key": "tablet",
            "display_name": "태블릿",
            "aliases": ["tablet", "아이패드", "갤럭시탭", "ipad", "갤럭시"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": "16x9x9",
                "max_wh": None,
                "max_ml": None,
                "condition": "기내용 16x9x9인치 이내 가능 (약 40x23x23cm)",
                "note": "보안 검색 시 태블릿 꺼내야 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "전자기기로 위탁 가능",
                "note": "파손 방지를 위해 케이스에 담아 권장"
            },
            "tips": "보안 검색 대기 시간 단축을 위해 파워 코드를 분리해서 제출",
            "source": "iata"
        },
        {
            "item_key": "power_bank",
            "display_name": "보조배터리",
            "aliases": ["power bank", "배터리", "충전기", "보조배터리", "portable charger", "powerbank"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": 100,
                "max_ml": None,
                "condition": "100Wh 이하만 기내 휴대 가능 (리튬이온 배터리 기준)",
                "note": "100Wh~160Wh는 기내 휴대 2개로 제한"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": 160,
                "max_ml": None,
                "condition": "160Wh 이하만 위탁 가능 (리튬이온 배터리 기준)",
                "note": "160Wh 초과는 위탁 불가"
            },
            "tips": "배터리 용량은 제품 라벨에 표시된 Wh(와트시)를 확인 (mAh ÷ 전압 × 3.7 = Wh)",
            "source": "iata"
        },
        {
            "item_key": "smartphone",
            "display_name": "스마트폰",
            "aliases": ["smartphone", "스마트폰", "폰", "phone", "갤럭시S", "iphone"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "기내 휴대 가능",
                "note": "보안 검색 시 전원을 켜고 잠금 해제해야 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "위탁 가능 (전원을 꺼고 파손 방지 조치)",
                "note": "파손 방지를 위해 케이스에 담아 권장"
            },
            "tips": "보안 검색 시 전원을 켜고 비밀번호 해제",
            "source": "iata"
        },

        # 액체
        {
            "item_key": "liquid_container_100ml",
            "display_name": "액체 용기 (100ml 이하)",
            "aliases": ["liquid", "액체", "물", "화장품", "perfume", "화장수", "물병"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": 100,
                "condition": "용기당 100ml 이하, 투명 투명 밀봉 용기에 담아 휴대용 1L 비닐백 1개에 담을 것",
                "note": "비닐백 크기: 20x20cm 이내, 지퍼록으로 밀봉"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "액체 규정 없이 위탁 가능",
                "note": "단, 파손 우려로 잘 포장 필요"
            },
            "tips": "100ml 이하라도 용기에 담긴 양이 100ml를 초과하면 반려",
            "source": "iata"
        },
        {
            "item_key": "alcohol",
            "display_name": "주류",
            "aliases": ["alcohol", "주류", "술", "와인", "맥주", "소주", "위스키"],
            "unit": "병",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": 100,
                "condition": "알코올 도수 24% 이하, 100ml 이하 용기에 담아 휴대용 1L 비닐백 1개에 담을 것",
                "note": "상업용 패키지 주류는 기내 반입 불가"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "알코올 도수 24% 이하는 5L 이내 위탁 가능",
                "note": "알코올 도수 24% 초과는 1L 이내 위탁 가능"
            },
            "tips": "주류는 면세점에서 구매한 영수증을 보관하시오",
            "source": "iata"
        },

        # 의류품
        {
            "item_key": "medicine_liquid",
            "display_name": "액체 의약품",
            "aliases": ["medicine", "의약품", "약", "liquid medicine", "약제"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": 100,
                "condition": "처방전 또는 의사 처방 의약품 (100ml 이하 용기, 처방전/의사 처방서 지참)",
                "note": "처방전/의사 처방서는 환자 이름 확인 가능해야 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의약품은 규정 없이 위탁 가능",
                "note": "단, 처방전/의사 처방서 지참 권장"
            },
            "tips": "처방전/의사 처방서는 복사본을 여러 장 준비하시오",
            "source": "iata"
        },
        {
            "item_key": "insulin",
            "display_name": "인슐린",
            "aliases": ["insulin", "인슐린", "당뇨약"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의사 처방 인슐린은 기내 휴대 가능 (처방전/의사 처방서 지참)",
                "note": "냉장 보관이 필요한 경우 아이스팩 사용 가능"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "인슐린은 위탁 가능",
                "note": "냉장 보관을 위해 드라이아이스 사용 권장"
            },
            "tips": "처방전/의사 처방서와 의사 연락처를 준비하시오",
            "source": "iata"
        },
        {
            "item_key": "medical_device",
            "display_name": "의료기기",
            "aliases": ["medical device", "의료기기", "휠체기", "CPAP", "산소발생기"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의료기기는 의사 처방 시 기내 휴대 가능 (처방전/의사 처방서 지참)",
                "note": "배터리 포함 시 보조배터리 규정 추가 확인 필요"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의료기기는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "의료기기 관련 의사 처방서와 사용 설명서를 지참하시오",
            "source": "iata"
        },

        # 의류품 (유아용)
        {
            "item_key": "baby_formula_liquid",
            "display_name": "유아용 조제 분유",
            "aliases": ["baby formula", "조제 분유", "유아용 액체", "baby milk"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": 100,
                "condition": "유아용 조제 분유는 기내 휴대 가능 (100ml 이하 용기)",
                "note": "유아가 동행 시에 한함, 식사 직전 보안 검색에서 제출 가능"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "유아용 조제 분유는 위탁 가능",
                "note": "개인 소비용량으로 제한"
            },
            "tips": "유아용 조제 분유는 식사 직전 보안 검색에서 제출하여 검사에 도움",
            "source": "iata"
        },
        {
            "item_key": "baby_food_jar",
            "display_name": "유아용 이유식",
            "aliases": ["baby food", "이유식", "유아용 캔"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": 100,
                "condition": "유아용 이유식은 기내 휴대 가능 (100ml 이하 용기)",
                "note": "유아가 동행 시에 한함, 식사 직전 보안 검색에서 제출 가능"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "유아용 이유식은 위탁 가능",
                "note": "개인 소비용량으로 제한"
            },
            "tips": "유아용 이유식은 식사 직전 보안 검색에서 제출하여 검사에 도움",
            "source": "iata"
        },

        # 스포츠 용품
        {
            "item_key": "sports_equipment_racket",
            "display_name": "라켓 (스포츠)",
            "aliases": ["racket", "라켓", "테니스라켓", "배드민턴라켓"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "라켓은 기내 휴대 가능 (가방에 담을 것)",
                "note": "투수되는 스포츠 용품으로 분류"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "라켓은 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "라켓 케이스를 사용하여 파손 방지",
            "source": "iata"
        },
        {
            "item_key": "sports_equipment_golf_club",
            "display_name": "골프채",
            "aliases": ["golf club", "골프채", "골프용품"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "골프채는 기내 휴대 불가 (위탁만 가능)",
                "note": "투수되는 스포츠 용품으로 분류"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "골프채는 위탁 가능 (전용 골프 백 사용 권장)",
                "note": "파손 방지를 위해 전용 골프 백 사용"
            },
            "tips": "전용 골프 백을 사용하여 파손 방지하고 규정 준수",
            "source": "iata"
        },
        {
            "item_key": "sports_equipment_skis",
            "display_name": "스키 장비",
            "aliases": ["skis", "스키", "스노우보드", "스키장비"],
            "unit": "세트",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "스키 장비는 기내 휴대 불가 (위탁만 가능)",
                "note": "투수되는 스포츠 용품으로 분류"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "스키 장비는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "스키 장비는 전용 케이스를 사용하여 파손 방지",
            "source": "iata"
        },

        # 음식물
        {
            "item_key": "food_solid",
            "display_name": "고체 음식물",
            "aliases": ["food", "음식", "식사", "간식", "비스켓", "과자"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "고체 음식물은 기내 휴대 가능 (냄새가 나지 않는 것으로)",
                "note": "특별한 의료 필요가 없는 한, 일반적으로 반려되지 않음"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "고체 음식물은 위탁 가능",
                "note": "냄새가 나지 않도록 잘 포장"
            },
            "tips": "냄새가 심한 음식물은 보안 검색에서 반려될 수 있음",
            "source": "iata"
        },
        {
            "item_key": "food_frozen",
            "display_name": "냉동 음식물",
            "aliases": ["frozen food", "냉동식", "아이스크림"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "냉동 음식물은 기내 휴대 불가 (위탁만 가능)",
                "note": "냉동 보관이 필요한 음식물로 분류"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "냉동 음식물은 위탁 가능",
                "note": "드라이아이스 사용 권장"
            },
            "tips": "냉동 음식물은 드라이아이스로 보관하여 녹지 않도록 주의",
            "source": "iata"
        },

        # 악세서리
        {
            "item_key": "umbrella",
            "display_name": "우산",
            "aliases": ["umbrella", "우산", "파라솔"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "우산은 기내 휴대 가능 (날이 날카로운 경우 위탁 권장)",
                "note": "날이 날카로운 우산은 보안 검색 시 반려될 수 있음"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "우산은 위탁 가능",
                "note": "파손 방지를 위해 우산 커버 사용 권장"
            },
            "tips": "날이 날카로운 우산은 위탁으로 권장",
            "source": "iata"
        },
        {
            "item_key": "walking_stick",
            "display_name": "지팡이",
            "aliases": ["walking stick", "지팡이", "스틱"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "지팡이는 기내 휴대 가능",
                "note": "보안 검사 시 검사 필요"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "지팡이는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "지팡이는 보안 검사 시 전시하고 통과 시 담을 것",
            "source": "iata"
        },
        {
            "item_key": "belt",
            "display_name": "벨트",
            "aliases": ["belt", "벨트", "허리띠"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "벨트는 기내 휴대 가능",
                "note": "보안 검사 시 착용 가능"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "벨트는 위탁 가능",
                "note": "보안 검사 시 착용 권장"
            },
            "tips": "벨트는 보안 검사 시 착용하여 통과 시간 단축",
            "source": "iata"
        },
        {
            "item_key": "watch",
            "display_name": "시계",
            "aliases": ["watch", "시계", "손목시계"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "시계는 기내 휴대 가능",
                "note": "금속 시계는 보안 검사 시 전시해야 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "시계는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "금속 시계는 보안 검사 시 시계 통과기가 없으면 반려될 수 있음",
            "source": "iata"
        },
        {
            "item_key": "jewelry",
            "display_name": "귀금속",
            "aliases": ["jewelry", "귀금속", "반지", "목걸이", "팔찌", "귀걸이"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "귀금속은 기내 휴대 가능",
                "note": "귀중 가치 높은 귀금속은 신고 권장"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "귀금속은 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "귀중 가치 높은 귀금속은 신고서를 준비하거나 기내 휴대 권장",
            "source": "iata"
        },

        # 화장품
        {
            "item_key": "cosmetics_solid",
            "display_name": "고체 화장품",
            "aliases": ["cosmetics", "화장품", "립스틱", "파우더", "향수 고체"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "고체 화장품은 기내 휴대 가능",
                "note": "액체 화장품 규정 적용 안 함"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "고체 화장품은 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "고체 화장품은 액체 규정에서 제외되므로 안전",
            "source": "iata"
        },
        {
            "item_key": "aerosol",
            "display_name": "에어로졸",
            "aliases": ["aerosol", "에어로졸", "분사제", "스프레이"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "에어로졸은 기내 휴대 불가 (위탁만 가능)",
                "note": "폭발물로 분류"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "에어로졸은 위탁 가능 (개인 사용량)",
                "note": "과다한 양은 반려될 수 있음"
            },
            "tips": "에어로졸은 개인 사용량만 허용되며 과다한 양은 반려",
            "source": "iata"
        },

        # 의류품 (비의약품)
        {
            "item_key": "vitamin_pill",
            "display_name": "비타민/영양제",
            "aliases": ["vitamin", "비타민", "영양제", "supplement"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "비타민/영양제는 기내 휴대 가능",
                "note": "의약품 규정 적용 안 함 (단, 의사 처방 필요 시 규정 적용)"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "비타민/영양제는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "비타민/영양제는 의약품 규정에서 제외되므로 안전",
            "source": "iata"
        },

        # 기타
        {
            "item_key": "camera",
            "display_name": "카메라",
            "aliases": ["camera", "카메라", "DSLR", "미러리스", "캠논"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "카메라는 기내 휴대 가능",
                "note": "배터리 포함 시 보조배터리 규정 추가 확인 필요"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "카메라는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "카메라 배터리는 보조배터리 규정을 확인 (보통 100Wh 이하)",
            "source": "iata"
        },
        {
            "item_key": "headphone",
            "display_name": "헤드폰",
            "aliases": ["headphone", "헤드폰", "이어폰", "이어버드", "earphone", "earbud"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "헤드폰은 기내 휴대 가능",
                "note": "전자기기로 분류되나 규정은 완화"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "헤드폰은 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "헤드폰은 전자기기지만 규정이 완화되어 안전",
            "source": "iata"
        },
        {
            "item_key": "book",
            "display_name": "책",
            "aliases": ["book", "책", "도서", "잡지"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "책은 기내 휴대 가능",
                "note": "개인 소비용량으로 제한"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "책은 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "책은 기내 휴대가 편리하며 규정도 완화되어 있음",
            "source": "iata"
        },
        {
            "item_key": "clothing",
            "display_name": "의류 (베스트)",
            "aliases": ["cloth", "옷", "의류", "베스트", "점퍼"],
            "unit": "개",
            "carry_on_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의류는 기내 휴대 가능",
                "note": "개인 소비용량으로 제한"
            },
            "checked_rule": {
                "max_size": None,
                "max_wh": None,
                "max_ml": None,
                "condition": "의류는 위탁 가능",
                "note": "파손 방지 조치 필요"
            },
            "tips": "의류는 기내 휴대 가능하며 규정이 완화되어 있음",
            "source": "iata"
        },
    ]

    # 데이터 삽입
    for rule in baggage_rules:
        op.execute("""
            INSERT INTO baggage_rules (
                item_key, display_name, aliases, unit, carry_on_rule, checked_rule, tips, source, created_at, updated_at
            ) VALUES (
                :item_key,
                :display_name,
                :aliases::jsonb,
                :unit,
                :carry_on_rule::jsonb,
                :checked_rule::jsonb,
                :tips,
                :source,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (item_key) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                aliases = EXCLUDED.aliases::jsonb,
                unit = EXCLUDED.unit,
                carry_on_rule = EXCLUDED.carry_on_rule::jsonb,
                checked_rule = EXCLUDED.checked_rule::jsonb,
                tips = EXCLUDED.tips,
                source = EXCLUDED.source,
                updated_at = CURRENT_TIMESTAMP
        """, {
            "item_key": rule["item_key"],
            "display_name": rule["display_name"],
            "aliases": rule["aliases"],
            "unit": rule["unit"],
            "carry_on_rule": rule["carry_on_rule"],
            "checked_rule": rule["checked_rule"],
            "tips": rule.get("tips"),
            "source": rule.get("source", "iata"),
        })


# downgrade revision
def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS baggage_rules;")