import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def insert_data():
    database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(database_url)

    # 25개 규칙 데이터
    rules = [
        # 전자기기
        ('laptop', '노트북', json.dumps(['laptop', '맥북', 'notebook', '노트북 컴퓨터', 'macbook']), '개',
         json.dumps({'max_size': '16x9x9', 'max_wh': None, 'max_ml': None, 'condition': '기내용 16x9x9인치 이내 가능', 'note': '보안 검색 시 노트북 꺼내야 함'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '전자기기로 위탁 가능', 'note': '파손 방지를 위해 케이스에 담아 권장'}),
         '보안 검색 대기 시간 단축을 위해 파워 코드를 분리해서 제출', 'iata'),

        ('tablet', '태블릿', json.dumps(['tablet', '아이패드', '갤럭시탭', 'ipad', '갤럭시']), '개',
         json.dumps({'max_size': '16x9x9', 'max_wh': None, 'max_ml': None, 'condition': '기내용 16x9x9인치 이내 가능', 'note': '보안 검색 시 태블릿 꺼내야 함'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '전자기기로 위탁 가능', 'note': '파손 방지를 위해 케이스에 담아 권장'}),
         '보안 검색 대기 시간 단축을 위해 파워 코드를 분리해서 제출', 'iata'),

        ('power_bank', '보조배터리', json.dumps(['power bank', '배터리', '충전기', '보조배터리', 'portable charger', 'powerbank']), '개',
         json.dumps({'max_size': None, 'max_wh': 100, 'max_ml': None, 'condition': '100Wh 이하만 기내 휴대 가능', 'note': '100Wh~160Wh는 기내 휴대 2개로 제한'}),
         json.dumps({'max_size': None, 'max_wh': 160, 'max_ml': None, 'condition': '160Wh 이하만 위탁 가능', 'note': '160Wh 초과는 위탁 불가'}),
         '배터리 용량은 제품 라벨에 표시된 Wh(와트시)를 확인 (mAh ÷ 전압 × 3.7 = Wh)', 'iata'),

        ('smartphone', '스마트폰', json.dumps(['smartphone', '스마트폰', '핸드폰', '폰', '아이폰', '갤럭시', 'phone']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '전원 꺼고 위탁 가능'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '전원 꺼고 위탁 가능', 'note': '배터리 포함 위탁 가능'}),
         '기내 사용은 비행 모드로 설정', 'iata'),

        # 액체
        ('liquid_container_100ml', '액체 용기 (100ml 이하)', json.dumps(['liquid', '액체', '물', '음료', 'beverage', 'drink']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': 100, 'condition': '100ml/용기, 1L 비닐백 1개 가능', 'note': '100ml 초과 용기는 반려'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '규정 없음', 'note': '규정 없음'}),
         '비닐백은 반투명 재질이어야 하며, 지퍼로 밀봉 가능해야 함', 'iata'),

        ('alcohol', '주류', json.dumps(['alcohol', '술', '주류', 'liquor', 'wine', 'beer']), '병',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': 100, 'condition': '100ml/용기, 24% 이하 가능', 'note': '100ml 초과 또는 24% 초과는 반려'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': 5000, 'condition': '5L 이내 가능', 'note': '포장되어 있어야 함'}),
         '규정 준수 확인 후 기내 반입 가능 (일부 항공사는 엄격 적용)', 'iata'),

        # 의료품
        ('medicine_liquid', '액체 의약품', json.dumps(['medicine', '의약품', '약', 'medicine liquid', 'liquid medicine']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': 100, 'condition': '100ml/용기, 처방전/의사 진단서 필요', 'note': '여행 기간 필요량 한도'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '규정 없음', 'note': '규정 없음'}),
         '의약품은 개인용으로만 허용', 'iata'),

        ('insulin', '인슐린', json.dumps(['insulin', '인슐린', '주사제']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대, 처방전/의사 진단서 필요', 'note': '냉장 보관 필요 (쿨러 사용 권장)'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '규정 없음', 'note': '규정 없음'}),
         '냉장 보관 필요하므로 쿨러 사용 권장', 'iata'),

        ('medical_device', '의료기기', json.dumps(['medical device', '의료기기', 'CPAP', '산소발생기']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대, 처방전/의사 진단서 필요', 'note': '배터리 포함 시 보조배터리 규정 확인'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '규정 없음', 'note': '규정 없음'}),
         '의료기기는 여행 필수 물품으로 간주', 'iata'),

        ('baby_formula_liquid', '유아용 조제 분유', json.dumps(['baby formula', '유아용 조제 분유', '분유', 'formula', 'baby milk']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': 100, 'condition': '100ml/용기, 유아 동반 필요', 'note': '여행 기간 필요량 한도'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '규정 없음', 'note': '규정 없음'}),
         '유아용 조제 분유는 기내 반입 케이스 완화', 'iata'),

        # 스포츠 용품
        ('sports_equipment_racket', '라켓 (스포츠)', json.dumps(['racket', '라켓', '테니스 라켓', 'badminton racket']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '날카로운 부분 케이스로 보호'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '파손 방지 조치 필요'}),
         '날카로운 부분 케이스로 보호하면 기내 반입 가능', 'iata'),

        ('sports_equipment_golf_club', '골프채', json.dumps(['golf club', '골프채', 'golf equipment']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁만 가능', 'note': '기내 휴대 불가'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '전용 백 권장'}),
         '기내 휴대 불가, 위탁만 가능', 'iata'),

        ('sports_equipment_skis', '스키 장비', json.dumps(['ski', '스키', 'snowboard', 'snow board']), '세트',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁만 가능', 'note': '기내 휴대 불가'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '전용 백 권장'}),
         '기내 휴대 불가, 위탁만 가능', 'iata'),

        # 음식물
        ('food_solid', '고체 음식물', json.dumps(['solid food', '고체 음식물', 'food', '음식', 'snack', '과자']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '개인 소비용량으로 제한'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '파손 방지 조치 필요'}),
         '고체 음식물은 기내 휴대 가능', 'iata'),

        ('food_frozen', '냉동 음식물', json.dumps(['frozen food', '냉동 음식물', 'frozen']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁만 가능', 'note': '냉동 보관 불가'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '냉동 보호 조치 필요'}),
         '냉동 음식물은 위탁만 가능 (기내 냉동 불가)', 'iata'),

        # 기타
        ('umbrella', '우산', json.dumps(['umbrella', '우산', 'parasol']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능 (날 날카로우면 위탁)', 'note': '날 접힌 우산은 기내 휴대 가능'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '규정 없음'}),
         '날 접힌 우산은 기내 휴대 가능', 'iata'),

        ('walking_stick', '지팡이', json.dumps(['walking stick', '지팡이', 'cane']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '보안 검색 시 제출 필요'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '규정 없음'}),
         '지팡이는 기내 휴대 가능', 'iata'),

        ('belt', '벨트', json.dumps(['belt', '벨트', '허리띠']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '규정 없음'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '규정 없음'}),
         '벨트는 기내 휴대 가능', 'iata'),

        ('watch', '시계', json.dumps(['watch', '시계', 'watch timepiece']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '규정 없음'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '규정 없음'}),
         '시계는 기내 휴대 가능', 'iata'),

        ('jewelry', '귀금속', json.dumps(['jewelry', '귀금속', 'necklace', 'ring']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능 (신고 권장)', 'note': '고가 귀금속 신고 권장'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '고가 귀금속 신고 권장'}),
         '고가 귀금속 신고 권장', 'iata'),

        ('cosmetics_solid', '고체 화장품', json.dumps(['cosmetics solid', '고체 화장품', 'solid cosmetics']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '기내 휴대 가능', 'note': '규정 완화'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능', 'note': '규정 없음'}),
         '고체 화장품은 기내 휴대 가능', 'iata'),

        ('aerosol', '에어로졸', json.dumps(['aerosol', '에어로졸', 'spray']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁만 가능', 'note': '개인 사용량으로 제한'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '위탁 가능 (개인 사용량)', 'note': '과다한 양은 반려될 수 있음'}),
         '에어로졸은 위탁 가능 (개인 사용량만 허용)', 'iata'),

        ('vitamin_pill', '비타민/영양제', json.dumps(['vitamin', '비타민', '영양제', 'supplement']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '비타민/영양제는 기내 휴대 가능', 'note': '의약품 규정 적용 안 함'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '비타민/영양제는 위탁 가능', 'note': '파손 방지 조치 필요'}),
         '비타민/영양제는 의약품 규정에서 제외', 'iata'),

        ('camera', '카메라', json.dumps(['camera', '카메라', 'DSLR', '미러리스', '캠논']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '카메라는 기내 휴대 가능', 'note': '배터리 포함 시 보조배터리 규정 확인'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '카메라는 위탁 가능', 'note': '파손 방지 조치 필요'}),
         '카메라 배터리는 보조배터리 규정 확인', 'iata'),

        ('headphone', '헤드폰', json.dumps(['headphone', '헤드폰', '이어폰', '이어버드', 'earphone', 'earbud']), '개',
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '헤드폰은 기내 휴대 가능', 'note': '전자기기로 분류되나 규정은 완화'}),
         json.dumps({'max_size': None, 'max_wh': None, 'max_ml': None, 'condition': '헤드폰은 위탁 가능', 'note': '파손 방지 조치 필요'}),
         '헤드폰은 전자기기지만 규정 완화', 'iata'),
    ]

    # 데이터 삽입
    for rule in rules:
        await conn.execute('''
            INSERT INTO baggage_rules (
                item_key, display_name, aliases, unit, carry_on_rule, checked_rule, tips, source
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ''', *rule)

    await conn.close()
    print(f'{len(rules)} rules inserted successfully!')

asyncio.run(insert_data())