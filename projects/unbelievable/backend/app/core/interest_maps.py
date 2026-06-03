"""Rule-based interest maps built from ad-safe Takeout events."""

from collections import Counter, defaultdict
import re
from typing import Any, Dict, List, Optional

from app.core.content_filters import (
    clean_search_query,
    detect_ad_event_reason,
    is_shorts_video_event,
    is_standard_video_event,
    is_valid_search_event,
)


UNKNOWN_VALUES = {"", "unknown", "none", "null", "n/a"}

INTEREST_RULES = [
    {"category": "게임", "subcategory": "모바일게임", "keywords": ["fc모바일", "fc 모바일"], "entities": ["FC모바일"], "secondary_tags": ["스포츠", "축구"]},
    {"category": "스포츠", "subcategory": "야구", "keywords": ["류현진", "kbo", "야구", "mlb", "한화", "두산", "삼성 라이온즈", "기아 타이거즈"], "entities": ["류현진"]},
    {"category": "스포츠", "subcategory": "축구", "keywords": ["이강인", "손흥민", "축구", "토트넘", "k리그", "premier league"], "entities": ["이강인", "손흥민"]},
    {"category": "스포츠", "subcategory": "농구", "keywords": ["농구", "nba"]},
    {"category": "스포츠", "subcategory": "배구", "keywords": ["배구", "v리그"]},
    {"category": "스포츠", "subcategory": "e스포츠", "keywords": ["e스포츠", "esports", "lck", "롤드컵"]},
    {"category": "게임", "subcategory": "롤", "keywords": ["리그오브레전드", "league of legends", "롤토체스", "롤 ", "lol"]},
    {"category": "게임", "subcategory": "FPS", "keywords": ["발로란트", "valorant", "오버워치", "overwatch", "fps", "배틀그라운드", "pubg"]},
    {"category": "게임", "subcategory": "콘솔게임", "keywords": ["닌텐도", "플스", "playstation", "xbox", "스팀 게임"]},
    {"category": "게임", "subcategory": "유희왕/카드게임", "keywords": ["유희왕", "카드게임", "마스터듀얼"]},
    {"category": "정치/사회", "subcategory": "시사토크", "keywords": ["매불쇼", "겸손은힘들다", "김어준"], "source_group": "유튜브·팟캐스트형 시사 채널"},
    {"category": "정치/사회", "subcategory": "정치논평/유튜브 채널", "keywords": ["가로세로연구소", "가세연", "정치논평"], "source_group": "유튜브 정치/사회 채널"},
    {"category": "정치/사회", "subcategory": "방송뉴스", "keywords": ["mbc 뉴스", "mbcnews", "sbs 뉴스", "kbs 뉴스"], "source_group": "지상파 뉴스"},
    {"category": "정치/사회", "subcategory": "방송뉴스", "keywords": ["tv조선", "tv chosun", "jtbc 뉴스", "ytn", "연합뉴스"], "source_group": "방송 뉴스"},
    {"category": "정치/사회", "subcategory": "국회/정당/선거", "keywords": ["국회", "정당", "선거", "여론조사", "대통령"]},
    {"category": "정치/사회", "subcategory": "사회이슈/사건", "keywords": ["사회", "시사", "사건", "논란", "법원", "검찰", "뉴스"]},
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
    {"category": "경제/금융", "subcategory": "세금", "keywords": ["세금", "종합소득세", "연말정산"]},
    {"category": "학습/자격증", "subcategory": "정보처리", "keywords": ["정보처리기사", "정처기"]},
    {"category": "학습/자격증", "subcategory": "코딩학습", "keywords": ["코딩 강의", "프로그래밍 강의", "튜토리얼", "입문"]},
    {"category": "학습/자격증", "subcategory": "대학과제", "keywords": ["대학과제", "과제", "레포트", "보고서"]},
    {"category": "학습/자격증", "subcategory": "자격증", "keywords": ["자격증", "컴활", "한국사"]},
    {"category": "학습/자격증", "subcategory": "영어/어학", "keywords": ["영어", "토익", "토플", "일본어", "중국어", "회화"]},
    {"category": "엔터테인먼트", "subcategory": "음악/아이돌", "keywords": ["음악", "노래", "뮤직", "아이돌", "정국", "뉴진스", "아이브", "세븐틴"]},
    {"category": "엔터테인먼트", "subcategory": "영화/드라마", "keywords": ["영화", "드라마", "예고편", "넷플릭스", "ott"]},
    {"category": "엔터테인먼트", "subcategory": "예능/인물", "keywords": ["예능", "인터뷰", "박명수", "유재석", "침착맨", "라이브"]},
    {"category": "여행/맛집", "subcategory": "여행", "keywords": ["여행", "호텔", "항공", "숙소", "호캉스", "해외여행", "국내여행"]},
    {"category": "여행/맛집", "subcategory": "맛집/카페", "keywords": ["맛집", "카페", "식당", "브런치", "디저트"]},
    {"category": "건강/운동", "subcategory": "운동", "keywords": ["운동", "헬스", "근력", "스트레칭", "러닝", "요가"]},
    {"category": "건강/운동", "subcategory": "건강관리", "keywords": ["건강", "다이어트", "영양제", "피부", "수면", "병원"]},
    {"category": "라이프스타일", "subcategory": "일상", "keywords": ["브이로그", "vlog", "일상", "루틴", "하루"]},
    {"category": "라이프스타일", "subcategory": "생활", "keywords": ["요리", "레시피", "인테리어", "청소", "살림", "육아"]},
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
    query = clean_search_query(raw_text or _event_title(event))
    return query or None


def _category_distribution(
    category_counter: Counter,
    subcategory_counter: Dict[str, Counter],
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
                "value": round((sub_count / total) * 100.0, 1),
            }
            for subcategory, sub_count in subcategory_counter[category].most_common(5)
        ]
        distribution.append(
            {
                "category": category,
                "name": category,
                "count": count,
                "ratio": round(count / total, 4),
                "value": round((count / total) * 100.0, 1),
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
            }
        )
    return rows


def build_search_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    keyword_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
    excluded_ad_count = 0

    for event in events or []:
        if detect_ad_event_reason(event):
            excluded_ad_count += 1
            continue

        query = extract_search_query(event)
        if not query:
            continue

        keyword_counter[query] += 1
        topic = classify_interest_topic(query)
        category_counter[topic["category"]] += 1
        subcategory_counter[topic["category"]][topic["subcategory"]] += 1

    total = sum(keyword_counter.values())
    warnings = []
    if total == 0:
        warnings.append("광고/노이즈를 제외한 실제 검색어가 부족합니다.")

    top_keywords = _keyword_rows(keyword_counter)
    return {
        "total_search_count": total,
        "top_keywords": top_keywords,
        "keywords": top_keywords,
        "category_distribution": _category_distribution(category_counter, subcategory_counter, total),
        "excluded_ad_count": excluded_ad_count,
        "warnings": warnings,
    }


def build_standard_video_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    title_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
    channel_counter: Counter = Counter()

    for event in events or []:
        if not is_standard_video_event(event):
            continue

        title = _event_title(event)
        if title:
            title_counter[title] += 1
            topic = classify_interest_topic(title)
            category_counter[topic["category"]] += 1
            subcategory_counter[topic["category"]][topic["subcategory"]] += 1

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
        "category_distribution": _category_distribution(category_counter, subcategory_counter, total),
        "warnings": warnings,
    }


def build_shorts_interest_map(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    title_counter: Counter = Counter()
    category_counter: Counter = Counter()
    subcategory_counter: Dict[str, Counter] = defaultdict(Counter)
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
            topic = classify_interest_topic(title)
            category_counter[topic["category"]] += 1
            subcategory_counter[topic["category"]][topic["subcategory"]] += 1

    total = sum(title_counter.values())
    denominator = total + standard_count
    warnings = []
    if total == 0:
        warnings.append("숏츠 시청 기록이 부족합니다.")

    return {
        "total_shorts_count": total,
        "shorts_count": total,
        "shorts_ratio": round(total / denominator, 4) if denominator else 0.0,
        "shorts_ratio_percent": round((total / denominator) * 100.0, 1) if denominator else 0.0,
        "top_shorts_keywords": _keyword_rows(title_counter),
        "category_distribution": _category_distribution(category_counter, subcategory_counter, total),
        "warnings": warnings,
    }


def _ratio_map(interest_map: Dict[str, Any]) -> Dict[str, float]:
    ratios: Dict[str, float] = {}
    for item in interest_map.get("category_distribution") or []:
        category = item.get("category") or item.get("name")
        if category:
            ratios[category] = float(item.get("ratio") or 0.0)
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
        rows.append(
            {
                "category": category,
                "search_ratio": round(search_ratio * 100.0, 1),
                f"{target_label}_ratio": round(target_ratio * 100.0, 1),
                "gap": round(abs(delta) * 100.0, 1),
                "direction": "over_exposed" if delta > 0 else ("under_exposed" if delta < 0 else "matched"),
            }
        )
    return sorted(rows, key=lambda item: item["gap"], reverse=True)


def _mean_gap(search_ratios: Dict[str, float], target_ratios: Dict[str, float]) -> float:
    categories = set(search_ratios) | set(target_ratios)
    if not categories:
        return 0.0
    return sum(abs(target_ratios.get(category, 0.0) - search_ratios.get(category, 0.0)) for category in categories) / len(categories)


def build_interest_gap_report(
    search_interest_map: Dict[str, Any],
    standard_video_interest_map: Dict[str, Any],
    shorts_interest_map: Dict[str, Any],
) -> Dict[str, Any]:
    search_ratios = _ratio_map(search_interest_map)
    standard_ratios = _ratio_map(standard_video_interest_map)
    shorts_ratios = _ratio_map(shorts_interest_map)

    search_vs_standard = _gap_rows(search_ratios, standard_ratios, "standard_video")
    search_vs_shorts = _gap_rows(search_ratios, shorts_ratios, "shorts")

    drift_categories: List[Dict[str, Any]] = []
    for row in search_vs_standard:
        if row["direction"] == "over_exposed" and row["gap"] >= 10.0:
            drift_categories.append({**row, "surface": "standard_video"})
    for row in search_vs_shorts:
        if row["direction"] == "over_exposed" and row["gap"] >= 10.0:
            drift_categories.append({**row, "surface": "shorts"})

    matched_categories = [
        {
            "category": category,
            "search_ratio": round(search_ratios[category] * 100.0, 1),
            "standard_video_ratio": round(standard_ratios[category] * 100.0, 1),
        }
        for category in sorted(set(search_ratios) & set(standard_ratios))
        if search_ratios[category] >= 0.1 and standard_ratios[category] >= 0.1
    ]

    mismatch = (_mean_gap(search_ratios, standard_ratios) * 0.7) + (_mean_gap(search_ratios, shorts_ratios) * 0.3)
    warnings = []
    if search_interest_map.get("total_search_count", 0) < 3:
        warnings.append("검색어 표본이 적어 관심사 격차는 참고용입니다.")
    if standard_video_interest_map.get("total_video_count", 0) < 3:
        warnings.append("일반 영상 표본이 적어 알고리즘 노출 비교는 참고용입니다.")

    return {
        "interest_mismatch_score": round(min(100.0, mismatch * 100.0), 1),
        "search_vs_standard_video_gap": search_vs_standard[:8],
        "search_vs_shorts_gap": search_vs_shorts[:8],
        "algorithm_drift_categories": sorted(drift_categories, key=lambda item: item["gap"], reverse=True)[:8],
        "intent_matched_categories": matched_categories[:8],
        "warnings": warnings,
    }
