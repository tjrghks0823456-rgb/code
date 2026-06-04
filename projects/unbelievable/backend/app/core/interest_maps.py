"""Rule-based interest maps built from ad-safe Takeout events."""

from collections import Counter, defaultdict
import re
from typing import Any, Dict, List, Optional

from app.core.content_filters import (
    clean_search_query,
    detect_ad_event_reason,
    extract_search_query as extract_event_search_query,
    is_shorts_video_event,
    is_standard_video_event,
    is_valid_search_event,
)


UNKNOWN_VALUES = {"", "unknown", "none", "null", "n/a"}

INTEREST_RULES = [
    {"category": "게임", "subcategory": "모바일게임", "keywords": ["fc모바일", "fc 모바일"], "entities": ["FC모바일"], "secondary_tags": ["스포츠", "축구"]},
    {"category": "스포츠", "subcategory": "야구", "keywords": ["류현진", "kbo", "야구", "mlb", "한화", "한화 이글스", "한화이글스", "이글스", "김서현", "노시환", "김경문", "최재훈", "문동주", "홍창화", "불꽃야구", "두산", "삼성 라이온즈", "기아 타이거즈", "kia"], "entities": ["류현진", "김서현", "노시환", "김경문", "최재훈"]},
    {"category": "스포츠", "subcategory": "축구", "keywords": ["이강인", "손흥민", "축구", "토트넘", "k리그", "premier league"], "entities": ["이강인", "손흥민"]},
    {"category": "스포츠", "subcategory": "농구", "keywords": ["농구", "nba"]},
    {"category": "스포츠", "subcategory": "배구", "keywords": ["배구", "v리그"]},
    {"category": "스포츠", "subcategory": "e스포츠", "keywords": ["e스포츠", "esports", "lck", "롤드컵", "t1", "faker", "페이커", "젠지", "geng", "담원", "디플러스", "dk"], "entities": ["T1", "페이커"]},
    {"category": "게임", "subcategory": "롤", "keywords": ["리그오브레전드", "league of legends", "롤토체스", "롤체", "tft", "teamfighttactics", "전략적팀전투", "롤 ", "lol", "제라스", "사일러스", "바드", "룰루"]},
    {"category": "게임", "subcategory": "FPS", "keywords": ["콜오브듀티", "call of duty", "발로란트", "valorant", "오버워치", "overwatch", "fps", "배틀그라운드", "pubg"]},
    {"category": "게임", "subcategory": "콘솔게임", "keywords": ["닌텐도", "플스", "playstation", "xbox", "스팀 게임"]},
    {"category": "게임", "subcategory": "유희왕/카드게임", "keywords": ["유희왕", "카드게임", "마스터듀얼"]},
    {"category": "정치/사회", "subcategory": "시사토크", "keywords": ["매불쇼", "겸손은힘들다", "김어준"], "source_group": "유튜브·팟캐스트형 시사 채널"},
    {"category": "정치/사회", "subcategory": "정치논평/유튜브 채널", "keywords": ["가로세로연구소", "가세연", "정치논평"], "source_group": "유튜브 정치/사회 채널"},
    {"category": "정치/사회", "subcategory": "방송뉴스", "keywords": ["mbc", "mbc 뉴스", "mbcnews", "sbs 뉴스", "kbs 뉴스"], "source_group": "지상파 뉴스"},
    {"category": "정치/사회", "subcategory": "방송뉴스", "keywords": ["tv조선", "tv chosun", "jtbc 뉴스", "ytn", "연합뉴스"], "source_group": "방송 뉴스"},
    {"category": "정치/사회", "subcategory": "국회/정당/선거", "keywords": ["국회", "정당", "선거", "여론조사", "대통령", "서울시장", "시장 후보"]},
    {"category": "정치/사회", "subcategory": "사회이슈/사건", "keywords": ["사회", "시사", "사건", "논란", "법원", "검찰", "뉴스", "국토부", "국토부장관", "철근 누락", "부실시공"]},
    {"category": "정치/사회", "subcategory": "국제정치", "keywords": ["국제정치", "미국", "중국", "일본", "러시아", "전쟁"]},
    {"category": "IT/테크", "subcategory": "AI", "keywords": ["ai", "gemini", "chatgpt", "openai", "llm", "머신러닝", "인공지능"]},
    {"category": "IT/테크", "subcategory": "클라우드", "keywords": ["google cloud", "gcp", "aws", "azure", "클라우드"]},
    {"category": "IT/테크", "subcategory": "프로그래밍", "keywords": ["코딩", "프로그래밍", "개발자", "python", "javascript", "react", "next.js", "fastapi"]},
    {"category": "IT/테크", "subcategory": "노트북/PC", "keywords": ["노트북", "pc", "컴퓨터", "맥북", "그래픽카드"]},
    {"category": "IT/테크", "subcategory": "모바일/기기", "keywords": ["갤럭시", "아이폰", "android", "스마트폰", "태블릿"]},
    {"category": "쇼핑/제품", "subcategory": "제품탐색", "keywords": ["추천", "리뷰", "제품", "가격", "비교", "언박싱"]},
    {"category": "쇼핑/제품", "subcategory": "구매/할인", "keywords": ["구매", "할인", "쿠폰", "세일", "핫딜", "특가", "공식몰"]},
    {"category": "쇼핑/제품", "subcategory": "패션/뷰티제품", "keywords": ["신발", "화장품", "패션", "향수", "틴트", "패치"]},
    {"category": "경제/금융", "subcategory": "주식", "keywords": ["주식", "코스피", "나스닥", "배당", "etf"]},
    {"category": "경제/금융", "subcategory": "코인", "keywords": ["코인", "비트코인", "이더리움", "crypto"]},
    {"category": "경제/금융", "subcategory": "부동산", "keywords": ["부동산", "아파트", "청약"]},
    {"category": "경제/금융", "subcategory": "재테크", "keywords": ["재테크", "투자", "대출", "금리"]},
    {"category": "경제/금융", "subcategory": "기타 경제", "keywords": ["장사의신", "자영업", "창업", "사업", "매출", "장사"]},
    {"category": "경제/금융", "subcategory": "세금", "keywords": ["세금", "종합소득세", "연말정산", "간편장부", "간편장부대상자", "소득세", "사업자 세금"]},
    {"category": "학습/자격증", "subcategory": "정보처리", "keywords": ["정보처리기사", "정처기"]},
    {"category": "학습/자격증", "subcategory": "코딩학습", "keywords": ["코딩 강의", "프로그래밍 강의", "튜토리얼", "입문"]},
    {"category": "학습/자격증", "subcategory": "대학과제", "keywords": ["대학과제", "과제", "레포트", "보고서"]},
    {"category": "학습/자격증", "subcategory": "자격증", "keywords": ["자격증", "컴활", "한국사"]},
    {"category": "학습/자격증", "subcategory": "영어/어학", "keywords": ["영어", "토익", "토플", "일본어", "중국어", "회화"]},
    {"category": "엔터테인먼트", "subcategory": "음악/아이돌", "keywords": ["음악", "노래", "뮤직", "아이돌", "밴드", "힙합", "락힙합", "록", "rock", "ost", "딘딘", "리센느", "지누션", "여돌", "스텔라이브", "정국", "뉴진스", "아이브", "세븐틴", "my whole world", "사랑이라 했던 말"]},
    {"category": "엔터테인먼트", "subcategory": "영화/드라마", "keywords": ["영화", "드라마", "예고편", "넷플릭스", "ott"]},
    {"category": "엔터테인먼트", "subcategory": "예능/인물", "keywords": ["예능", "인터뷰", "김호영", "박명수", "유재석", "유병재", "강동원", "정지훈", "이민우", "복냥즈", "배우", "천만 배우", "수상소감", "웃긴", "침착맨", "라이브"]},
    {"category": "여행/맛집", "subcategory": "여행", "keywords": ["여행", "호텔", "항공", "숙소", "호캉스", "해외여행", "국내여행"]},
    {"category": "여행/맛집", "subcategory": "맛집/카페", "keywords": ["맛집", "카페", "식당", "브런치", "디저트"]},
    {"category": "건강/운동", "subcategory": "운동", "keywords": ["운동", "헬스", "근력", "스트레칭", "러닝", "요가"]},
    {"category": "건강/운동", "subcategory": "건강관리", "keywords": ["건강", "다이어트", "영양제", "피부", "수면", "병원"]},
    {"category": "라이프스타일", "subcategory": "일상", "keywords": ["브이로그", "vlog", "일상", "루틴", "하루"]},
    {"category": "라이프스타일", "subcategory": "생활", "keywords": ["요리", "레시피", "인테리어", "청소", "살림", "육아", "이사", "해외이사", "주재원이사", "세차", "주방"]},
]

RAW_CATEGORY_MAP = {
    "computers & electronics": ("IT/테크", "기타 IT"),
    "arts & entertainment": ("엔터테인먼트", "기타 엔터테인먼트"),
    "news": ("정치/사회", "방송뉴스"),
    "finance": ("경제/금융", "기타 경제"),
    "sports": ("스포츠", "기타 스포츠"),
    "games": ("게임", "기타 게임"),
    "travel": ("여행/맛집", "여행"),
    "health": ("건강/운동", "건강관리"),
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _lower(value: Any) -> str:
    return _text(value).lower()


def _known(value: Any) -> bool:
    return _lower(value) not in UNKNOWN_VALUES


def _event_title(event: Dict[str, Any]) -> str:
    return _text(event.get("text_base") or event.get("title_text") or event.get("title"))


def _channel_key(event: Dict[str, Any]) -> str:
    # Prefer stable source identity over display names for source-balance scoring.
    for key in ("channel_url", "channel_name", "author_id", "source_surface"):
        value = _text(event.get(key))
        if _known(value):
            return value
    return ""


def _keyword_matches(text: str, keyword: str) -> bool:
    lowered_keyword = keyword.lower()
    if re.match(r"^[a-z0-9.+#-]+$", lowered_keyword):
        pattern = rf"(?<![a-z0-9]){re.escape(lowered_keyword)}(?![a-z0-9])"
        return re.search(pattern, text) is not None
    return lowered_keyword in text


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = _text(item)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def _base_topic(
    category: str,
    subcategory: str,
    confidence: str,
    raw_text: str,
    raw_category: str,
    matched_keywords: List[str] = None,
    entities: List[str] = None,
    source_group: str = "",
    secondary_tags: List[str] = None,
) -> Dict[str, Any]:
    return {
        "category": category,
        "subcategory": subcategory,
        "confidence": confidence,
        "entities": _dedupe(entities or []),
        "matched_keywords": _dedupe(matched_keywords or []),
        "source_group": source_group,
        "secondary_tags": _dedupe(secondary_tags or []),
        "raw_text": raw_text,
        "raw_category": raw_category,
    }


def _topic_from_raw_category(raw_category: str, evidence_text: str, raw_text: str) -> Optional[Dict[str, Any]]:
    raw_lower = _lower(raw_category)
    if not raw_lower:
        return None

    if raw_lower == "people & society":
        political_markers = ["뉴스", "정치", "시사", "국회", "정당", "선거", "사회", "mbc", "tv조선", "ytn"]
        lifestyle_markers = ["일상", "브이로그", "vlog", "루틴", "생활", "요리", "육아"]
        if any(marker in evidence_text for marker in political_markers):
            return _base_topic("정치/사회", "기타 정치사회", "medium", raw_text, raw_category, [raw_category])
        if any(marker in evidence_text for marker in lifestyle_markers):
            return _base_topic("라이프스타일", "일상", "medium", raw_text, raw_category, [raw_category])
        return _base_topic("기타/미분류", "미분류", "low", raw_text, raw_category, [raw_category])

    mapped = RAW_CATEGORY_MAP.get(raw_lower)
    if not mapped:
        return None

    category, subcategory = mapped
    return _base_topic(
        category,
        subcategory,
        "medium",
        raw_text,
        raw_category,
        [raw_category],
    )


def classify_interest_topic(text: Any, raw_category: str = "", channel_name: str = "") -> Dict[str, Any]:
    """Classify a title/query into a service-friendly major/minor interest topic."""
    raw = _text(text)
    raw_cat = _text(raw_category)
    channel = _text(channel_name)
    evidence_text = " ".join(part for part in [raw, channel, raw_cat] if part).lower()

    for rule in INTEREST_RULES:
        keywords = rule.get("keywords", [])
        matched = [keyword for keyword in keywords if _keyword_matches(evidence_text, keyword)]
        if not matched:
            continue

        entities = [
            entity
            for entity in rule.get("entities", [])
            if _keyword_matches(evidence_text, entity)
        ]
        matched_keywords = matched[:]
        subcategory = rule["subcategory"]
        if entities and subcategory not in matched_keywords:
            matched_keywords.append(subcategory)

        confidence = "high" if entities or len(matched) >= 2 else "medium"
        return _base_topic(
            rule["category"],
            subcategory,
            confidence,
            raw,
            raw_cat,
            matched_keywords=matched_keywords[:6],
            entities=entities,
            source_group=rule.get("source_group", ""),
            secondary_tags=rule.get("secondary_tags", []),
        )

    raw_topic = _topic_from_raw_category(raw_cat, evidence_text, raw)
    if raw_topic:
        return raw_topic

    return _base_topic("기타/미분류", "미분류", "low", raw, raw_cat)


def extract_search_query(event: Dict[str, Any], raw_text: str = "") -> Optional[str]:
    """Return only a real user search query; ads, watches, and noise return None."""
    if not is_valid_search_event(event):
        return None
    return extract_event_search_query(event, raw_text=raw_text) or clean_search_query(raw_text or _event_title(event)) or None


def _event_raw_category(event: Dict[str, Any]) -> str:
    return _text(
        event.get("raw_category")
        or event.get("category")
        or event.get("nlp_category")
        or event.get("topic_category")
    )


def _confidence_score(value: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(_lower(value), 0)


def _best_confidence(values: List[str]) -> str:
    if not values:
        return "low"
    return max(values, key=_confidence_score)


def _ensure_subcategory_detail(
    details: Dict[str, Dict[str, Dict[str, Any]]],
    category: str,
    subcategory: str,
) -> Dict[str, Any]:
    if category not in details:
        details[category] = {}
    if subcategory not in details[category]:
        details[category][subcategory] = {
            "entities": [],
            "raw_items": [],
            "confidence_values": [],
            "matched_keywords": [],
            "source_groups": [],
            "secondary_tags": [],
        }
    return details[category][subcategory]


def _record_topic(
    topic: Dict[str, Any],
    raw_item: str,
    category_counter: Counter,
    subcategory_counter: Dict[str, Counter],
    subcategory_details: Dict[str, Dict[str, Dict[str, Any]]],
) -> None:
    category = topic.get("category") or "기타/미분류"
    subcategory = topic.get("subcategory") or "미분류"

    category_counter[category] += 1
    subcategory_counter[category][subcategory] += 1

    detail = _ensure_subcategory_detail(subcategory_details, category, subcategory)
    detail["entities"].extend(topic.get("entities") or [])
    detail["raw_items"].append(raw_item)
    detail["confidence_values"].append(topic.get("confidence") or "low")
    detail["matched_keywords"].extend(topic.get("matched_keywords") or [])
    if topic.get("source_group"):
        detail["source_groups"].append(topic["source_group"])
    detail["secondary_tags"].extend(topic.get("secondary_tags") or [])


def _category_distribution(
    category_counter: Counter,
    subcategory_counter: Dict[str, Counter],
    subcategory_details: Dict[str, Dict[str, Dict[str, Any]]],
    total: int,
) -> List[Dict[str, Any]]:
    if total <= 0:
        return []

    distribution: List[Dict[str, Any]] = []
    for category, count in category_counter.most_common():
        subcategories = [
            {
                "name": subcategory,
                "count": sub_count,
                "ratio": round((sub_count / max(1, count)) * 100.0, 1),
                "value": round((sub_count / max(1, count)) * 100.0, 1),
                "entities": _dedupe(subcategory_details.get(category, {}).get(subcategory, {}).get("entities", []))[:8],
                "raw_items": _dedupe(subcategory_details.get(category, {}).get(subcategory, {}).get("raw_items", []))[:8],
                "confidence": _best_confidence(subcategory_details.get(category, {}).get(subcategory, {}).get("confidence_values", [])),
                "matched_keywords": _dedupe(subcategory_details.get(category, {}).get(subcategory, {}).get("matched_keywords", []))[:8],
                "source_groups": _dedupe(subcategory_details.get(category, {}).get(subcategory, {}).get("source_groups", []))[:5],
                "secondary_tags": _dedupe(subcategory_details.get(category, {}).get(subcategory, {}).get("secondary_tags", []))[:8],
            }
            for subcategory, sub_count in subcategory_counter[category].most_common(5)
        ]
        ratio_percent = round((count / total) * 100.0, 1)
        distribution.append(
            {
                "category": category,
                "name": category,
                "count": count,
                "ratio": ratio_percent,
                "ratio_fraction": round(count / total, 4),
                "value": ratio_percent,
                "subcategories": subcategories,
            }
        )
    return distribution


def _keyword_rows(counter: Counter, top_limit: int = 8) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for keyword, count in counter.most_common(top_limit):
        topic = classify_interest_topic(keyword)
        rows.append(
            {
                "keyword": keyword,
                "count": count,
                "category": topic["category"],
                "subcategory": topic["subcategory"],
                "confidence": topic["confidence"],
                "entities": topic.get("entities", []),
                "source_group": topic.get("source_group", ""),
                "secondary_tags": topic.get("secondary_tags", []),
                "raw_category": topic.get("raw_category", ""),
            }
        )
    return rows


def build_search_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    keyword_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
    subcategory_details: Dict[str, Dict[str, Dict[str, Any]]] = {}
    excluded_ad_count = 0

    for event in events or []:
        if detect_ad_event_reason(event):
            excluded_ad_count += 1
            continue

        query = extract_search_query(event)
        if not query:
            continue

        keyword_counter[query] += 1
        topic = classify_interest_topic(
            query,
            raw_category=_event_raw_category(event),
            channel_name=event.get("channel_name", ""),
        )
        _record_topic(topic, query, category_counter, subcategory_counter, subcategory_details)

    total = sum(keyword_counter.values())
    warnings = []
    if total == 0:
        warnings.append("광고/노이즈를 제외한 실제 검색어가 부족합니다.")

    top_keywords = _keyword_rows(keyword_counter)
    return {
        "total_search_count": total,
        "top_keywords": top_keywords,
        "keywords": top_keywords,
        "category_distribution": _category_distribution(category_counter, subcategory_counter, subcategory_details, total),
        "excluded_ad_count": excluded_ad_count,
        "warnings": warnings,
    }


def build_standard_video_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    title_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
    subcategory_details: Dict[str, Dict[str, Dict[str, Any]]] = {}
    channel_counter: Counter = Counter()

    for event in events or []:
        if not is_standard_video_event(event):
            continue

        title = _event_title(event)
        if title:
            title_counter[title] += 1
            topic = classify_interest_topic(
                title,
                raw_category=_event_raw_category(event),
                channel_name=event.get("channel_name", ""),
            )
            _record_topic(topic, title, category_counter, subcategory_counter, subcategory_details)

        channel = _channel_key(event)
        if channel:
            channel_counter[channel] += 1

    total = sum(title_counter.values())
    warnings = []
    if total == 0:
        warnings.append("일반 영상 시청 기록이 부족합니다.")

    return {
        "total_video_count": total,
        "top_keywords": _keyword_rows(title_counter),
        "top_channels": [
            {"name": name, "count": count, "value": round((count / max(1, total)) * 100.0, 1)}
            for name, count in channel_counter.most_common(8)
        ],
        "category_distribution": _category_distribution(category_counter, subcategory_counter, subcategory_details, total),
        "warnings": warnings,
    }


def build_shorts_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    title_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
    subcategory_details: Dict[str, Dict[str, Dict[str, Any]]] = {}
    standard_count = 0

    for event in events or []:
        if is_standard_video_event(event):
            standard_count += 1
            continue

        if not is_shorts_video_event(event):
            continue

        title = _event_title(event)
        if title:
            title_counter[title] += 1
            topic = classify_interest_topic(
                title,
                raw_category=_event_raw_category(event),
                channel_name=event.get("channel_name", ""),
            )
            _record_topic(topic, title, category_counter, subcategory_counter, subcategory_details)

    total = sum(title_counter.values())
    denominator = total + standard_count
    warnings = [
        "숏츠 관심사 맵은 직접 검색 의도가 아니라 짧은 영상 반복 노출 패턴을 기반으로 계산됩니다."
    ]
    if total == 0:
        warnings.append("이번 업로드에서 /shorts/ URL로 식별된 숏츠 이벤트가 0건입니다. Takeout 저장 방식 또는 이전 run_id 여부를 확인해야 합니다.")

    return {
        "total_shorts_count": total,
        "shorts_count": total,
        "shorts_detection_status": "detected" if total else "not_detected",
        "shorts_detection_note": (
            "이번 업로드에서 /shorts/ URL 기반 숏츠 이벤트가 확인되었습니다."
            if total
            else "이번 업로드에서 /shorts/ URL로 식별된 숏츠 이벤트가 0건입니다. 실제 소비가 없다는 확정은 아닙니다."
        ),
        "shorts_ratio": round(total / denominator, 4) if denominator else 0.0,
        "shorts_ratio_percent": round((total / denominator) * 100.0, 1) if denominator else 0.0,
        "top_shorts_keywords": _keyword_rows(title_counter),
        "category_distribution": _category_distribution(category_counter, subcategory_counter, subcategory_details, total),
        "repeat_topic_score": round((title_counter.most_common(1)[0][1] / total) * 100.0, 1) if total else 0.0,
        "warnings": warnings,
    }


def _ratio_map(interest_map: Dict[str, Any]) -> Dict[str, float]:
    ratios: Dict[str, float] = {}
    for item in interest_map.get("category_distribution") or []:
        category = item.get("category") or item.get("name")
        if category:
            ratio = item.get("ratio_fraction")
            if ratio is None:
                ratio = float(item.get("ratio") or 0.0)
                if ratio > 1.0:
                    ratio = ratio / 100.0
            ratios[category] = float(ratio or 0.0)
    return ratios


def _gap_rows(
    search_ratios: Dict[str, float],
    target_ratios: Dict[str, float],
    target_label: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for category in sorted(set(search_ratios) | set(target_ratios)):
        search_ratio = search_ratios.get(category, 0.0)
        target_ratio = target_ratios.get(category, 0.0)
        delta = target_ratio - search_ratio
        if delta > 0:
            interpretation = "검색 대비 실제 소비 비중이 높음"
            direction = "watch_higher"
        elif delta < 0:
            interpretation = "검색은 많지만 실제 소비 비중은 낮음"
            direction = "search_higher"
        else:
            interpretation = "검색과 실제 소비 비중이 유사함"
            direction = "matched"
        rows.append(
            {
                "category": category,
                "search_ratio": round(search_ratio * 100.0, 1),
                f"{target_label}_ratio": round(target_ratio * 100.0, 1),
                "gap": round(delta * 100.0, 1),
                "abs_gap": round(abs(delta) * 100.0, 1),
                "direction": direction,
                "interpretation": interpretation,
            }
        )
    return sorted(rows, key=lambda item: item["abs_gap"], reverse=True)


def _l1_gap(search_ratios: Dict[str, float], target_ratios: Dict[str, float]) -> float:
    categories = set(search_ratios) | set(target_ratios)
    if not categories:
        return 0.0
    return sum(abs(target_ratios.get(category, 0.0) - search_ratios.get(category, 0.0)) for category in categories) / 2.0


def _category_samples(interest_map: Dict[str, Any], category: str, limit: int = 5) -> List[str]:
    samples: List[str] = []
    for item in interest_map.get("category_distribution") or []:
        if (item.get("category") or item.get("name")) != category:
            continue
        for subcategory in item.get("subcategories") or []:
            samples.extend(subcategory.get("raw_items") or [])
    return _dedupe(samples)[:limit]


def build_interest_gap_report(
    search_interest_map: Dict[str, Any],
    standard_video_interest_map: Dict[str, Any],
    shorts_interest_map: Dict[str, Any],
    explicit_map: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    search_ratios = _ratio_map(search_interest_map)
    standard_ratios = _ratio_map(standard_video_interest_map)
    shorts_ratios = _ratio_map(shorts_interest_map)

    search_vs_standard = _gap_rows(search_ratios, standard_ratios, "standard_video")
    search_vs_shorts = _gap_rows(search_ratios, shorts_ratios, "shorts")

    recommendation_candidates: List[Dict[str, Any]] = []
    for category in sorted(set(search_ratios) | set(standard_ratios) | set(shorts_ratios)):
        search_ratio = search_ratios.get(category, 0.0)
        watch_ratio = standard_ratios.get(category, 0.0)
        shorts_ratio = shorts_ratios.get(category, 0.0)
        watch_lift = max(0.0, watch_ratio - search_ratio)
        shorts_lift = max(0.0, shorts_ratio - search_ratio)
        candidate_score = ((watch_lift * 0.7) + (shorts_lift * 0.3)) * 100.0
        if candidate_score < 8.0:
            continue

        evidence = []
        if watch_lift > 0:
            evidence.append(
                f"검색 비중 {round(search_ratio * 100.0, 1)}% 대비 일반 시청 비중 {round(watch_ratio * 100.0, 1)}%"
            )
        if shorts_lift > 0:
            evidence.append(
                f"검색 비중 {round(search_ratio * 100.0, 1)}% 대비 숏츠 비중 {round(shorts_ratio * 100.0, 1)}%"
            )

        recommendation_candidates.append({
            "category": category,
            "search_ratio": round(search_ratio * 100.0, 1),
            "watch_ratio": round(watch_ratio * 100.0, 1),
            "standard_video_ratio": round(watch_ratio * 100.0, 1),
            "shorts_ratio": round(shorts_ratio * 100.0, 1),
            "candidate_score": round(candidate_score, 1),
            "interpretation": "검색 기록에서는 낮았지만 비검색 시청 기록에서 상대적으로 많이 나타난 주제입니다.",
            "evidence": evidence,
            "sample_items": _category_samples(standard_video_interest_map, category) or _category_samples(shorts_interest_map, category),
        })

    matched_categories = [
        {
            "category": category,
            "search_ratio": round(search_ratios[category] * 100.0, 1),
            "standard_video_ratio": round(standard_ratios[category] * 100.0, 1),
            "interpretation": "검색과 일반 시청에서 모두 반복된 관심사입니다.",
        }
        for category in sorted(set(search_ratios) & set(standard_ratios))
        if search_ratios[category] >= 0.1 and standard_ratios[category] >= 0.1
    ]

    standard_gap = _l1_gap(search_ratios, standard_ratios)
    shorts_gap = _l1_gap(search_ratios, shorts_ratios) if shorts_interest_map.get("total_shorts_count", 0) else 0.0
    mismatch = (standard_gap * 0.7) + (shorts_gap * 0.3)
    warnings = []
    if search_interest_map.get("total_search_count", 0) < 3:
        warnings.append("검색어 표본이 적어 관심사 격차는 참고용입니다.")
    if standard_video_interest_map.get("total_video_count", 0) < 3:
        warnings.append("일반 영상 표본이 적어 추천 흐름 영향 후보는 참고용입니다.")
    if explicit_map is None:
        warnings.append("명시적 반응 데이터가 없어 추천 흐름 영향 후보는 검색 대비 소비 비중 차이만으로 계산했습니다.")

    recommendation_candidates = sorted(
        recommendation_candidates,
        key=lambda item: item["candidate_score"],
        reverse=True,
    )[:8]

    return {
        "interest_mismatch_score": round(min(100.0, mismatch * 100.0), 1),
        "summary": "직접 검색한 관심사와 실제 시청한 관심사 사이의 차이를 비교했습니다.",
        "search_vs_watch_gap": search_vs_standard[:8],
        "search_vs_standard_video_gap": search_vs_standard[:8],
        "search_vs_shorts_gap": search_vs_shorts[:8],
        "recommendation_flow_candidate_categories": recommendation_candidates,
        "algorithm_drift_categories": recommendation_candidates,
        "intent_matched_categories": matched_categories[:8],
        "warnings": warnings,
    }
