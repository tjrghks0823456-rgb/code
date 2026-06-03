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

INTEREST_TAXONOMY = [
    {
        "category": "스포츠",
        "rules": [
            ("축구", ["축구", "손흥민", "이강인", "토트넘", "k리그", "premier league"]),
            ("야구", ["야구", "kbo", "mlb", "류현진", "한화", "삼성 라이온즈", "기아 타이거즈"]),
            ("농구/배구", ["농구", "nba", "배구", "v리그"]),
            ("e스포츠", ["e스포츠", "esports", "lck", "롤드컵"]),
        ],
    },
    {
        "category": "게임",
        "rules": [
            ("리그오브레전드", ["리그오브레전드", "league of legends", "롤 ", "롤토체스", "lol"]),
            ("FPS", ["발로란트", "valorant", "오버워치", "overwatch", "fps", "배틀그라운드", "pubg"]),
            ("모바일/콘솔", ["fc모바일", "모바일게임", "닌텐도", "플스", "xbox", "스팀 게임"]),
        ],
    },
    {
        "category": "정치/사회",
        "rules": [
            ("정치", ["정치", "대통령", "국회", "선거", "정당", "여론조사"]),
            ("사회/시사", ["사회", "뉴스", "시사", "사건", "논란", "법원", "검찰"]),
            ("국제", ["국제", "미국", "중국", "일본", "러시아", "전쟁"]),
        ],
    },
    {
        "category": "경제/금융",
        "rules": [
            ("투자", ["주식", "코스피", "나스닥", "투자", "배당", "etf"]),
            ("가상자산", ["코인", "비트코인", "이더리움", "crypto"]),
            ("부동산/재테크", ["부동산", "아파트", "청약", "재테크", "대출", "금리"]),
        ],
    },
    {
        "category": "IT/테크",
        "rules": [
            ("AI", ["ai", "gemini", "chatgpt", "openai", "llm", "머신러닝", "인공지능"]),
            ("개발", ["코딩", "프로그래밍", "개발자", "python", "javascript", "react", "next.js", "fastapi"]),
            ("클라우드/디바이스", ["google cloud", "aws", "클라우드", "노트북", "pc", "갤럭시", "아이폰", "android"]),
        ],
    },
    {
        "category": "학습/자격증",
        "rules": [
            ("학습", ["강의", "공부", "학습", "수업", "입문", "튜토리얼", "lecture"]),
            ("시험/자격증", ["자격증", "시험", "토익", "토플", "한국사", "컴활", "정보처리기사"]),
            ("언어", ["영어", "일본어", "중국어", "회화"]),
        ],
    },
    {
        "category": "엔터테인먼트",
        "rules": [
            ("음악/아이돌", ["음악", "노래", "뮤직", "아이돌", "정국", "뉴진스", "아이브", "세븐틴"]),
            ("영화/드라마", ["영화", "드라마", "예고편", "넷플릭스", "ott"]),
            ("예능/인물", ["예능", "인터뷰", "박명수", "유재석", "침착맨", "라이브"]),
        ],
    },
    {
        "category": "쇼핑/제품",
        "rules": [
            ("제품탐색", ["추천", "리뷰", "제품", "가격", "비교", "언박싱"]),
            ("구매/할인", ["구매", "할인", "쿠폰", "세일", "핫딜", "특가", "공식몰"]),
            ("패션/뷰티제품", ["신발", "화장품", "패션", "향수", "틴트", "패치"]),
        ],
    },
    {
        "category": "여행/맛집",
        "rules": [
            ("여행", ["여행", "호텔", "항공", "숙소", "호캉스", "해외여행", "국내여행"]),
            ("맛집/카페", ["맛집", "카페", "식당", "브런치", "디저트"]),
        ],
    },
    {
        "category": "건강/운동",
        "rules": [
            ("운동", ["운동", "헬스", "근력", "스트레칭", "러닝", "요가"]),
            ("건강관리", ["건강", "다이어트", "영양제", "피부", "수면", "병원"]),
        ],
    },
    {
        "category": "라이프스타일",
        "rules": [
            ("일상", ["브이로그", "vlog", "일상", "루틴", "하루"]),
            ("생활", ["요리", "레시피", "인테리어", "청소", "살림", "육아"]),
        ],
    },
]


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


def classify_interest_topic(text: Any) -> Dict[str, Any]:
    """Classify a title/query into a major/minor interest topic."""
    raw = _text(text)
    lowered = raw.lower()
    matched: List[str] = []

    for category_rule in INTEREST_TAXONOMY:
        for subcategory, keywords in category_rule["rules"]:
            matched = [keyword for keyword in keywords if _keyword_matches(lowered, keyword)]
            if matched:
                confidence = "high" if len(matched) >= 2 else "medium"
                return {
                    "category": category_rule["category"],
                    "subcategory": subcategory,
                    "confidence": confidence,
                    "matched_keywords": matched[:5],
                }

    return {
        "category": "기타/미분류",
        "subcategory": "미분류",
        "confidence": "low",
        "matched_keywords": [],
    }


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
