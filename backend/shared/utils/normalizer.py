"""항공사/제품명 정규화 유틸리티."""

import re
from typing import Optional


# 항공사 정규화 매핑
AIRLINE_ALIASES = {
    # 대한항공
    "koreanair": "대한항공",
    "korean air": "대한항공",
    "kal": "대한항공",
    "asiana": "아시아나항공",
    "jin air": "진에어",
    "t'way": "티웨이",
    "air busan": "에어부산",
    "air seoul": "에어서울",
    "eastar": "이스타",
    "jeju air": "제주항공",
    "air busan": "에어부산",

    # 해외 항공사
    "delta": "델타",
    "united": "유나이티드",
    "american": "아메리칸",
    "american airlines": "아메리칸항공",
    "continental": "콘티넨탈",
    "continental airlines": "콘티넨탈항공",
    "northwest": "노스웨스트",
    "southwest": "사우스웨스트",
    "jetblue": "제트블루",
    "alaska": "알래스카",
    "allegiant": "알레전트",
    "spirit": "스피릿",
    "frontier": "프론티어",
    "hawaiian": "하와이안",
    "southwest": "사우스웨스트",
    "allegiant air": "알레전트항공",
    "jetblue airways": "제트블루항공",
    "frontier airlines": "프론티어항공",
    "spirit airlines": "스피릿항공",
    "hawaiian airlines": "하와이안항공",

    # 일본 항공사
    "jal": "일본항공",
    "japan airlines": "일본항공",
    "ana": "전일본공",
    "all nippon": "전일본공",
    "zipair": "zipair",
    "zipair airways": "zipair",
    "starflyer": "스타플라이어",
}

# 제품 카테고리별 정규화 패턴
PRODUCT_PATTERNS = {
    "macbook": [
        r"macbook\s*pro",
        r"mac\s*pro\s*13\s*inch",
        r"mac\s*pro\s*14\s*inch",
        r"mac\s*pro\s*16\s*inch",
    ],
    "iphone": [
        r"iphone\s*\d+\s*pro",
        r"iphone\s+\d+\s*pro\s+max",
        r"iphone\s+\d+\s+mini",
        r"iphone\s+\d+\s+plus",
    ],
    "ipad": [
        r"ipad\s+pro",
        r"ipad\s+air",
        r"ipad\s+mini",
    ],
    "laptop": [
        r"laptop\s*pro",
        r"thinkpad\s*",
        r"surface\s+pro",
        r"dell\s+xps\s*",
        r"hp\s*spectre\s*x360",
    ],
}


def normalize_airline(airline: str) -> str:
    """항공사명 정규화.

    Args:
        airline: 항공사명 (예: "대한항공", "Kal", "Asiana")

    Returns:
        정규화된 항공사명 (예: "대한항공", "아시아나항공")

    Examples:
        >>> normalize_airline("Korean Air")
        '대한항공'
        >>> normalize_airline("kal")
        '대한항공'
        >>> normalize_airline("Asiana Airlines")
        '아시아나항공'
    """
    if not airline:
        return ""

    # 소문자로 변환하고 공백 제거
    normalized = airline.lower().strip()

    # 별명 매핑
    for alias, full_name in AIRLINE_ALIASES.items():
        if alias in normalized:
            return full_name

    # 알파벗순 정렬 (한국어 우선)
    # 실제 구현 시에는 퍼미코디어 정렬 사용 권장
    return airline  # 매핑 실패 시 원래 이름 반환


def normalize_product(product: str, category: str | None = None) -> str:
    """제품명 정규화.

    Args:
        product: 제품명 (예: "MacBook Pro 13", "iPhone 14 Pro", "Laptop Pro")
        category: 제품 카테고리 (선택사항)

    Returns:
        정규화된 제품명

    Examples:
        >>> normalize_product("macbook pro 13 inch")
        'MacBook Pro 13 inch'
        >>> normalize_product("iPhone 14 Pro Max")
        'iPhone 14 Pro Max'
        >>> normalize_product("Dell XPS 15", "laptop")
        'Dell XPS 15'
    """
    if not product:
        return ""

    # 소문자로 변환하고 공백 제거
    normalized = product.lower().strip()

    # 카테고리별 패턴 매칭
    if category:
        category_lower = category.lower()
        if category_lower in PRODUCT_PATTERNS:
            for pattern in PRODUCT_PATTERNS[category_lower]:
                if re.search(pattern, normalized, re.IGNORECASE):
                    # 캡피터와 스페이스 정규화
                    normalized = re.sub(r"\s+", " ", normalized)
                    # 첫 글자 대문자화
                    normalized = normalized[:1].upper() + normalized[1:]
                    return normalized

    # 제품명 공통 정규화
    # 맥큐 공백 제거
    normalized = re.sub(r"\s+", " ", normalized)

    # 맨 앞 글자 대문자화 (Macbook → MacBook)
    normalized = normalized[:1].upper() + normalized[1:]

    return normalized


def extract_airline_from_text(text: str) -> Optional[str]:
    """텍스트에서 항공사명 추출.

    Args:
        text: 검색할 텍스트

    Returns:
        추출된 항공사명 또는 None
    """
    if not text:
        return None

    # 정규화된 항공사 리스트에서 매칭
    airlines = set(AIRLINE_ALIASES.values())

    for airline in sorted(airlines, key=len, reverse=True):
        if airline.lower() in text.lower():
            return airline

    return None


def extract_product_from_text(text: str) -> Optional[str]:
    """텍스트에서 제품명 추출.

    Args:
        text: 검색할 텍스트

    Returns:
        추출된 제품명 또는 None
    """
    if not text:
        return None

    # 알려진 제품명 패턴 매칭
    known_products = [
        "macbook", "macbook pro", "macbook air",
        "iphone", "ipad", "apple watch",
        "galaxy", "galaxy s", "galaxy note",
        "thinkpad", "surface", "dell", "hp",
        "asus", "acer", "lg", "msi",
    ]

    text_lower = text.lower()
    for product in sorted(known_products, key=len, reverse=True):
        if product in text_lower:
            # 원래 텍스트에서 실제 제품명 추출
            match = re.search(rf"{product}[^\\s]*(?:{product}\\s+\\w+)", text, re.IGNORECASE)
            if match:
                return match.group(0)

    return None


def get_airline_display_name(airline: str) -> str:
    """항공사 출력용 이름 (공백 제거)."""
    if not airline:
        return ""
    return airline.strip()


def get_product_display_name(product: str) -> str:
    """제품명 출력용 이름 (공백 제거, 첫 글자 대문자)."""
    if not product:
        return ""
    return product.strip()


def format_airline_for_search(airline: str) -> str:
    """검색용 항공사명 포맷.

    Args:
        airline: 원본 항공사명

    Returns:
        검색용 포맷 (소문자, 공백 제거)
    """
    if not airline:
        return ""
    return airline.lower().strip().replace(" ", "_")


def format_product_for_search(product: str) -> str:
    """검색용 제품명 포맷.

    Args:
        product: 원본 제품명

    Returns:
        검색용 포맷 (소문자, 공백 제거)
    """
    if not product:
        return ""
    return product.lower().strip().replace(" ", "_")


def generate_baggage_cache_key(airline: str, product: str, value: float, unit: str) -> str:
    """수화물 캐시 키 생성.

    Args:
        airline: 항공사명
        product: 제품명
        value: 수치
        unit: 단위

    Returns:
        캐시 키 포맷: "airline:product:value:unit"

    Examples:
        >>> generate_baggage_cache_key("대한항공", "MacBook", 15.6, "inch")
        '대한항공:macbook:15.6:inch'
    """
    normalized_airline = format_airline_for_search(airline)
    normalized_product = format_product_for_search(product)
    return f"{normalized_airline}:{normalized_product}:{value}:{unit}"