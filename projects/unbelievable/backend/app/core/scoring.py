import math
import re
from collections import Counter
from typing import Dict, List, Any, Tuple

# 16-Type Personality Mapping (4-bit binary D, S, A, O)
# High = 'H', Low = 'L'
PERSONALITY_MAP = {
    # D, S, A, O
    ("H", "H", "H", "H"): ("진정한 탐험가", ["#호기심", "#도전", "#학습"]),
    ("H", "H", "H", "L"): ("자기주도적 탐구자", ["#탐구", "#목표", "#확장"]),
    ("H", "H", "L", "H"): ("지적 모험가", ["#신선함", "#공부", "#흥미"]),
    ("H", "H", "L", "L"): ("에너지 넘치는 사색가", ["#창의", "#이슈", "#소통"]),
    
    ("H", "L", "H", "H"): ("조화로운 관점 설계자", ["#공감", "#독해력", "#다양성"]),
    ("H", "L", "H", "L"): ("주도적 감성 관찰자", ["#감성분석", "#내면성찰", "#표현"]),
    ("H", "L", "L", "H"): ("친화적 소통가", ["#키워드", "#친화력", "#소통"]),
    ("H", "L", "L", "L"): ("감성 아웃사이더", ["#아웃라이어", "#독특함", "#예술"]),
    
    ("L", "H", "H", "H"): ("효율적 정보 관리자", ["#효율성", "#전문성", "#집중"]),
    ("L", "H", "H", "L"): ("주도적 분석 매니아", ["#데이터", "#실용적", "#심층분석"]),
    ("L", "H", "L", "H"): ("소통 지향 마니아", ["#트렌드", "#민감", "#교류"]),
    ("L", "H", "L", "L"): ("감성적 정보 몰입러", ["#몰입형", "#감수성", "#애청자"]),
    
    ("L", "L", "H", "H"): ("추천 흐름 점검형", ["#반복패턴", "#균형회복", "#자기조절"]),
    ("L", "L", "H", "L"): ("흥미 반응형", ["#자극", "#쇼츠", "#재미"]),
    ("L", "L", "L", "H"): ("수동적 수용자", ["#알고리즘", "#흘러가는대로", "#피동"]),
    ("L", "L", "L", "L"): ("조용한 휴식형", ["#차분함", "#휴식", "#균형회복"]),
}

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    """Calculates the Shannon entropy of a probability distribution."""
    if not probabilities:
        return 0.0
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def calculate_hhi(shares: List[float]) -> float:
    """Calculates the Herfindahl-Hirschman Index (HHI).
    shares: List of percentage shares, e.g., [50.0, 30.0, 20.0]
    """
    if not shares:
        return 10000.0
    return sum(s ** 2 for s in shares)

STIMULATION_KEYWORDS = [
    "충격", "분노", "논란", "폭로", "참교육", "소름", "역대급", "미쳤다", "최악", "경악"
]
INFORMATION_KEYWORDS = [
    "정리", "설명", "강의", "튜토리얼", "리뷰", "분석", "역사", "과학", "방법"
]
CALM_KEYWORDS = [
    "힐링", "감동", "평온", "일상", "브이로그", "자연", "음악"
]
DIRECT_SURFACES = {"search", "direct", "channel", "subscriptions", "subscription", "playlist", "library"}
UNKNOWN_SOURCE_VALUES = {"unknown", "none", "null", "n/a"}
STOPWORDS = {
    "watched", "searched", "for", "the", "and", "with", "youtube", "video",
    "에서", "으로", "에게", "하다", "하는", "그리고", "오늘", "영상"
}

def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, round(value, 1)))

def weighted_score(parts: List[Dict[str, Any]]) -> float:
    usable_parts = [
        part for part in parts
        if part.get("value") is not None and part.get("weight", 0) > 0
    ]
    if not usable_parts:
        return 50.0

    total_weight = sum(float(part["weight"]) for part in usable_parts)
    if total_weight <= 0:
        return 50.0

    score = sum(float(part["value"]) * float(part["weight"]) for part in usable_parts) / total_weight
    return clamp_score(score)

def normalize_source(value: Any) -> str:
    if value is None:
        return "Unknown"
    source = str(value).strip()
    return source if source else "Unknown"

def is_known_source(value: str) -> bool:
    return value.strip().lower() not in UNKNOWN_SOURCE_VALUES

def extract_keywords_from_text(text: Any) -> List[str]:
    if not text:
        return []

    normalized = str(text).lower()
    normalized = normalized.replace("watched", " ").replace("searched for", " ")
    tokens = re.findall(r"[0-9a-zA-Z가-힣]{2,}", normalized)
    return [token for token in tokens if token not in STOPWORDS]

def extract_topic_counts(results: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in results:
        cats = r.get("categories_json", [])
        if not isinstance(cats, list):
            continue

        for c in cats:
            if isinstance(c, dict):
                path = str(c.get("name", "")).strip()
            else:
                path = str(c).strip()

            if not path:
                continue

            parts = [part.strip() for part in path.split("/") if part.strip()]
            top_level = parts[0] if parts else path
            if top_level:
                counts[top_level] = counts.get(top_level, 0) + 1

    return counts

def classify_text_tone(text: Any) -> str:
    lowered = str(text or "").lower()
    if any(keyword in lowered for keyword in STIMULATION_KEYWORDS):
        return "stimulating"
    if any(keyword in lowered for keyword in CALM_KEYWORDS):
        return "positive"
    if any(keyword in lowered for keyword in INFORMATION_KEYWORDS):
        return "neutral"
    return "unknown"

def score_entropy(counts: List[int], max_classes: int) -> float:
    total = sum(counts)
    if total <= 0:
        return 50.0

    probs = [count / total for count in counts if count > 0]
    entropy = calculate_shannon_entropy(probs)
    max_entropy = math.log2(max_classes) if max_classes > 1 else 1.0
    return clamp_score((entropy / max_entropy) * 100.0)

def compute_6axis_scores(
    events: List[Dict[str, Any]], 
    nlp_results: List[Dict[str, Any]]
) -> Tuple[Dict[str, float], List[str], Dict[str, List[Dict[str, Any]]]]:
    """
    Computes 6-axis scores based on normalized watch history events and NLP results.
    Returns:
        axis_scores: Dict of axis code to score (0-100)
        exception_codes: List of triggered exceptions (P01, P04, etc.)
        score_components: Per-axis sub-scores used for the weighted score
    """
    scores = {
        "TDS": 50.0, # 주제다양성
        "SBS": 50.0, # 출처균형
        "EBS": 50.0, # 감정균형
        "VOS": 50.0, # 관점개방성
        "SMS": 50.0, # 유해안전
        "UAS": 50.0  # 사용자주도성
    }
    exception_codes = []
    score_components: Dict[str, List[Dict[str, Any]]] = {}

    def add_warning(code: str) -> None:
        if code not in exception_codes:
            exception_codes.append(code)

    def component(name: str, label: str, value: Any, weight: float) -> Dict[str, Any]:
        normalized_value = None if value is None else clamp_score(float(value))
        return {
            "name": name,
            "label": label,
            "value": normalized_value,
            "weight": weight,
            "status": "limited" if normalized_value is None else "used"
        }

    def component_score(parts: List[Dict[str, Any]]) -> float:
        return weighted_score(parts)

    def build_event_stats() -> Dict[str, Any]:
        total_events = len(events)
        view_items = [e for e in events if e.get("action_type") == "view"]
        search_items = [e for e in events if e.get("action_type") == "search"]
        action_total = len(view_items) + len(search_items)

        sources = [normalize_source(e.get("author_id") or e.get("source_surface")) for e in events]
        valid_sources = [source for source in sources if is_known_source(source)]
        source_counts = Counter(valid_sources)
        unknown_source_ratio = None
        if total_events > 0:
            unknown_source_ratio = (total_events - len(valid_sources)) / total_events

        top_source_ratio = None
        if valid_sources:
            top_source_ratio = max(source_counts.values()) / len(valid_sources)

        comparable_source_pairs = 0
        same_source_pairs = 0
        previous_source = None
        for source in sources:
            if not is_known_source(source):
                previous_source = None
                continue
            if previous_source is not None:
                comparable_source_pairs += 1
                if previous_source == source:
                    same_source_pairs += 1
            previous_source = source

        consecutive_same_source_ratio = None
        if comparable_source_pairs > 0:
            consecutive_same_source_ratio = same_source_pairs / comparable_source_pairs

        direct_surface_count = 0
        known_surface_count = 0
        for e in events:
            surface = str(e.get("source_surface") or "").strip().lower()
            if not surface or surface in UNKNOWN_SOURCE_VALUES:
                continue
            known_surface_count += 1
            if surface in DIRECT_SURFACES:
                direct_surface_count += 1

        direct_surface_ratio = None
        if known_surface_count > 0:
            direct_surface_ratio = direct_surface_count / known_surface_count

        keywords_by_event = []
        all_keywords = []
        search_keywords = []
        tone_labels = []
        stimulation_keyword_events = 0
        information_keyword_events = 0
        calm_keyword_events = 0

        for e in events:
            text = e.get("text_base") or e.get("title") or e.get("query") or ""
            keywords = extract_keywords_from_text(text)
            keywords_by_event.append(keywords)
            all_keywords.extend(keywords)
            if e.get("action_type") == "search":
                search_keywords.extend(keywords)

            text_lower = str(text).lower()
            has_stimulation = any(keyword in text_lower for keyword in STIMULATION_KEYWORDS)
            has_information = any(keyword in text_lower for keyword in INFORMATION_KEYWORDS)
            has_calm = any(keyword in text_lower for keyword in CALM_KEYWORDS)
            if has_stimulation:
                stimulation_keyword_events += 1
            if has_information:
                information_keyword_events += 1
            if has_calm:
                calm_keyword_events += 1
            tone_labels.append(classify_text_tone(text))

        keyword_counts = Counter(all_keywords)
        repeated_keyword_ratio = None
        if all_keywords:
            repeated_keyword_ratio = 1.0 - (len(keyword_counts) / len(all_keywords))

        search_keyword_counts = Counter(search_keywords)
        search_keyword_diversity_ratio = None
        if search_keywords:
            search_keyword_diversity_ratio = len(search_keyword_counts) / len(search_keywords)

        event_topic_labels = [keywords[0] if keywords else None for keywords in keywords_by_event]
        comparable_topic_pairs = 0
        same_topic_pairs = 0
        topic_switch_count = 0
        previous_topic = None
        for topic in event_topic_labels:
            if topic is None:
                previous_topic = None
                continue
            if previous_topic is not None:
                comparable_topic_pairs += 1
                if previous_topic == topic:
                    same_topic_pairs += 1
                else:
                    topic_switch_count += 1
            previous_topic = topic

        topic_switch_ratio = None
        consecutive_same_topic_ratio = None
        if comparable_topic_pairs > 0:
            topic_switch_ratio = topic_switch_count / comparable_topic_pairs
            consecutive_same_topic_ratio = same_topic_pairs / comparable_topic_pairs

        view_durations = [
            e.get("time_delta_sec") for e in view_items
            if isinstance(e.get("time_delta_sec"), (int, float)) and e.get("time_delta_sec") >= 0
        ]
        estimated_long_ratio = None
        short_view_ratio = None
        if view_durations:
            estimated_long_ratio = sum(1 for duration in view_durations if duration >= 180) / len(view_durations)
            short_view_ratio = sum(1 for duration in view_durations if duration <= 60) / len(view_durations)

        comparable_tone_pairs = 0
        same_tone_pairs = 0
        previous_tone = None
        for tone in tone_labels:
            if tone == "unknown":
                previous_tone = None
                continue
            if previous_tone is not None:
                comparable_tone_pairs += 1
                if previous_tone == tone:
                    same_tone_pairs += 1
            previous_tone = tone

        consecutive_same_tone_ratio = None
        if comparable_tone_pairs > 0:
            consecutive_same_tone_ratio = same_tone_pairs / comparable_tone_pairs

        return {
            "total_events": total_events,
            "view_events": len(view_items),
            "search_events": len(search_items),
            "search_ratio": (len(search_items) / action_total) if action_total else None,
            "unique_sources": len(source_counts),
            "source_counts": source_counts,
            "valid_sources": valid_sources,
            "unknown_source_ratio": unknown_source_ratio,
            "top_source_ratio": top_source_ratio,
            "unique_keywords": len(keyword_counts),
            "total_keywords": len(all_keywords),
            "repeated_keyword_ratio": repeated_keyword_ratio,
            "search_unique_keywords": len(search_keyword_counts),
            "search_total_keywords": len(search_keywords),
            "search_keyword_diversity_ratio": search_keyword_diversity_ratio,
            "topic_switch_count": topic_switch_count,
            "topic_switch_ratio": topic_switch_ratio,
            "estimated_long_ratio": estimated_long_ratio,
            "short_view_ratio": short_view_ratio,
            "consecutive_same_source_ratio": consecutive_same_source_ratio,
            "consecutive_same_topic_ratio": consecutive_same_topic_ratio,
            "direct_surface_ratio": direct_surface_ratio,
            "stimulation_keyword_events": stimulation_keyword_events,
            "information_keyword_events": information_keyword_events,
            "calm_keyword_events": calm_keyword_events,
            "tone_counts": Counter(tone for tone in tone_labels if tone != "unknown"),
            "consecutive_same_tone_ratio": consecutive_same_tone_ratio
        }
    
    # Check minimum events constraint (FEAT_07: P01_DATA_SHORT)
    if len(events) < 10:
        add_warning("P01_DATA_SHORT")
        for axis in scores:
            score_components[axis] = [
                component("data_volume", "분석 이벤트 수", None, 1.0)
            ]
        return scores, exception_codes, score_components

    stats = build_event_stats()
    topic_counts = extract_topic_counts(nlp_results)
    valid_topic_count = len(topic_counts)
    total_topics = sum(topic_counts.values())

    # --- 1. 사용자주도성 (User Agency - UAS) ---
    search_ratio_score = None
    if stats["search_events"] == 0 or stats["search_ratio"] is None:
        add_warning("P04_NO_SEARCH")
    else:
        search_ratio_score = min(100.0, stats["search_ratio"] * 400.0)

    uas_topic_switch_score = None
    if stats["topic_switch_ratio"] is None:
        add_warning("P09_KEYWORD_SAMPLE_LIMITED")
    else:
        uas_topic_switch_score = stats["topic_switch_ratio"] * 100.0

    repetition_inputs = [
        ratio for ratio in [
            stats["consecutive_same_source_ratio"],
            stats["consecutive_same_topic_ratio"]
        ]
        if ratio is not None
    ]
    repetition_penalty_score = None
    if not repetition_inputs:
        add_warning("P09_REPETITION_SAMPLE_LIMITED")
    else:
        repetition_penalty_score = (1.0 - (sum(repetition_inputs) / len(repetition_inputs))) * 100.0

    directness_proxy_score = None
    if stats["direct_surface_ratio"] is None:
        add_warning("P08_DIRECTNESS_METADATA_LIMITED")
    else:
        directness_proxy_score = stats["direct_surface_ratio"] * 100.0

    score_components["UAS"] = [
        component("search_ratio_score", "검색 비율", search_ratio_score, 0.4),
        component("topic_switch_score", "주제 전환", uas_topic_switch_score, 0.25),
        component("repetition_penalty_score", "반복 시청 패턴", repetition_penalty_score, 0.2),
        component("directness_proxy_score", "직접 선택 추정", directness_proxy_score, 0.15)
    ]
    scores["UAS"] = component_score(score_components["UAS"])

    # --- 2. 주제다양성 (Topic Diversity - TDS) ---
    nlp_category_entropy_score = None
    if len(nlp_results) < 2 or valid_topic_count < 2:
        add_warning("P02_TOPIC_SAMPLE_LIMITED")
    else:
        probs = [count / total_topics for count in topic_counts.values()]
        entropy = calculate_shannon_entropy(probs)
        nlp_category_entropy_score = min(100.0, (entropy / 3.5) * 100.0)

    title_keyword_diversity_score = None
    if stats["repeated_keyword_ratio"] is None:
        add_warning("P09_KEYWORD_SAMPLE_LIMITED")
    else:
        title_keyword_diversity_score = (1.0 - stats["repeated_keyword_ratio"]) * 100.0

    top_topic_concentration_reverse_score = None
    if valid_topic_count < 2:
        add_warning("P06_VIEWPOINT_SAMPLE_LIMITED")
    else:
        top_topic_concentration_reverse_score = (1.0 - (max(topic_counts.values()) / total_topics)) * 100.0

    score_components["TDS"] = [
        component("nlp_category_entropy_score", "NLP 카테고리 다양성", nlp_category_entropy_score, 0.4),
        component("title_keyword_diversity_score", "제목 키워드 다양성", title_keyword_diversity_score, 0.25),
        component("topic_switch_score", "주제 전환 빈도", uas_topic_switch_score, 0.2),
        component("top_topic_concentration_reverse_score", "상위 주제 집중도 완화", top_topic_concentration_reverse_score, 0.15)
    ]
    scores["TDS"] = component_score(score_components["TDS"])

    # --- 3. 출처균형 (Source Balance - SBS) ---
    valid_sources = list(stats["source_counts"].keys())
    source_hhi_reverse_score = None
    unique_source_score = None
    top_source_concentration_reverse_score = None
    consecutive_same_source_reverse_score = None

    if len(valid_sources) < 2:
        add_warning("P05_SOURCE_SAMPLE_LIMITED")
    else:
        valid_total = sum(stats["source_counts"].values())
        shares = [(count / valid_total) * 100 for count in stats["source_counts"].values()]
        hhi = calculate_hhi(shares)
        source_hhi_reverse_score = max(0.0, 100.0 - (hhi / 100.0))
        unique_source_score = min(100.0, (stats["unique_sources"] / 10.0) * 100.0)
        top_source_concentration_reverse_score = (1.0 - stats["top_source_ratio"]) * 100.0

    if stats["consecutive_same_source_ratio"] is None:
        add_warning("P05_SOURCE_SAMPLE_LIMITED")
    else:
        consecutive_same_source_reverse_score = (1.0 - stats["consecutive_same_source_ratio"]) * 100.0

    source_metadata_quality_score = None
    if stats["unknown_source_ratio"] is None:
        add_warning("P05_SOURCE_MISSING")
    elif len(valid_sources) < 2:
        add_warning("P05_SOURCE_SAMPLE_LIMITED")
    else:
        source_metadata_quality_score = (1.0 - stats["unknown_source_ratio"]) * 100.0
        if source_metadata_quality_score == 0:
            add_warning("P05_SOURCE_MISSING")

    score_components["SBS"] = [
        component("source_hhi_reverse_score", "출처 HHI 역점수", source_hhi_reverse_score, 0.35),
        component("unique_source_score", "고유 출처 수", unique_source_score, 0.2),
        component("top_source_concentration_reverse_score", "상위 출처 집중도 완화", top_source_concentration_reverse_score, 0.2),
        component("consecutive_same_source_reverse_score", "동일 출처 연속 완화", consecutive_same_source_reverse_score, 0.15),
        component("source_metadata_quality_score", "출처 메타데이터 품질", source_metadata_quality_score, 0.1)
    ]
    scores["SBS"] = component_score(score_components["SBS"])

    # --- 4. 감정균형 (Emotion Balance - EBS) ---
    sentiments = [r.get("sentiment_score", 0.0) for r in nlp_results if "sentiment_score" in r]
    sentiment_entropy_score = None
    if len(sentiments) < 2:
        add_warning("P03_SENTIMENT_SAMPLE_LIMITED")
    else:
        pos = sum(1 for s in sentiments if s > 0.25)
        neg = sum(1 for s in sentiments if s < -0.25)
        neu = len(sentiments) - (pos + neg)
        sentiment_entropy_score = score_entropy([pos, neg, neu], 3)

    tone_counts = stats["tone_counts"]
    tone_total = sum(tone_counts.values())
    emotional_keyword_balance_score = None
    neutral_content_ratio_score = None
    repeated_emotional_tone_reverse_score = None
    if tone_total == 0:
        add_warning("P11_EMOTION_KEYWORD_LIMITED")
    else:
        emotional_keyword_balance_score = score_entropy([
            tone_counts.get("stimulating", 0),
            tone_counts.get("neutral", 0),
            tone_counts.get("positive", 0)
        ], 3)
        neutral_content_ratio_score = (tone_counts.get("neutral", 0) / tone_total) * 100.0

    if stats["consecutive_same_tone_ratio"] is None:
        add_warning("P11_EMOTION_KEYWORD_LIMITED")
    else:
        repeated_emotional_tone_reverse_score = (1.0 - stats["consecutive_same_tone_ratio"]) * 100.0

    score_components["EBS"] = [
        component("sentiment_entropy_score", "NLP 감정 분포", sentiment_entropy_score, 0.4),
        component("emotional_keyword_balance_score", "감정 키워드 균형", emotional_keyword_balance_score, 0.25),
        component("neutral_content_ratio_score", "중립 정보 키워드 비율", neutral_content_ratio_score, 0.2),
        component("repeated_emotional_tone_reverse_score", "반복 감정 톤 완화", repeated_emotional_tone_reverse_score, 0.15)
    ]
    scores["EBS"] = component_score(score_components["EBS"])

    # --- 5. 자극성 안전 (Stimulation Safety - SMS) ---
    toxic_hits = 0
    total_items = len(nlp_results)
    for r in nlp_results:
        for cat in r.get("categories_json", []):
            if isinstance(cat, dict):
                name = str(cat.get("name", "")).lower()
            else:
                name = str(cat).lower()
            if any(toxic_word in name for toxic_word in ["adult", "violence", "drugs", "weapons", "gore", "hate"]):
                toxic_hits += 1

    toxic_category_safety_score = None
    if total_items < 2:
        add_warning("P07_SAFETY_SAMPLE_LIMITED")
    else:
        toxic_ratio = toxic_hits / total_items
        toxic_category_safety_score = max(0.0, 100.0 - (toxic_ratio * 300.0))

    stimulation_keyword_safety_score = None
    emotional_extreme_safety_score = None
    if stats["total_events"] > 0:
        stimulation_event_ratio = stats["stimulation_keyword_events"] / stats["total_events"]
        stimulation_keyword_safety_score = max(0.0, 100.0 - (stimulation_event_ratio * 100.0))

        extreme_event_ratio = (stats["stimulation_keyword_events"] + stats["calm_keyword_events"]) / stats["total_events"]
        emotional_extreme_safety_score = max(0.0, 100.0 - (extreme_event_ratio * 100.0))
    else:
        add_warning("P09_KEYWORD_SAMPLE_LIMITED")

    short_repetition_safety_score = None
    short_repetition_inputs = [
        ratio for ratio in [
            stats["short_view_ratio"],
            stats["consecutive_same_topic_ratio"],
            stats["repeated_keyword_ratio"]
        ]
        if ratio is not None
    ]
    if not short_repetition_inputs:
        add_warning("P10_DURATION_SAMPLE_LIMITED")
    else:
        short_repetition_safety_score = (1.0 - (sum(short_repetition_inputs) / len(short_repetition_inputs))) * 100.0

    repeated_stimulus_topic_safety_score = None
    repeated_stimulus_inputs = [
        ratio for ratio in [
            stats["consecutive_same_topic_ratio"],
            (stats["stimulation_keyword_events"] / stats["total_events"]) if stats["total_events"] else None
        ]
        if ratio is not None
    ]
    if not repeated_stimulus_inputs:
        add_warning("P09_REPETITION_SAMPLE_LIMITED")
    else:
        repeated_stimulus_topic_safety_score = (1.0 - (sum(repeated_stimulus_inputs) / len(repeated_stimulus_inputs))) * 100.0

    score_components["SMS"] = [
        component("toxic_category_safety_score", "자극성 카테고리 안전", toxic_category_safety_score, 0.25),
        component("stimulation_keyword_safety_score", "자극 키워드 안전", stimulation_keyword_safety_score, 0.3),
        component("short_repetition_safety_score", "짧은 반복 시청 안전", short_repetition_safety_score, 0.2),
        component("emotional_extreme_safety_score", "감정 극단 키워드 안전", emotional_extreme_safety_score, 0.15),
        component("repeated_stimulus_topic_safety_score", "반복 자극 주제 안전", repeated_stimulus_topic_safety_score, 0.1)
    ]
    scores["SMS"] = component_score(score_components["SMS"])

    # --- 6. 관점개방성 (Perspective Openness - VOS) ---
    topic_concentration_reverse_score = top_topic_concentration_reverse_score
    if valid_topic_count < 2:
        add_warning("P06_VIEWPOINT_SAMPLE_LIMITED")

    source_diversity_support_score = None
    if len(valid_sources) < 2:
        add_warning("P05_SOURCE_SAMPLE_LIMITED")
    else:
        source_diversity_support_score = (source_hhi_reverse_score + top_source_concentration_reverse_score) / 2

    keyword_repetition_reverse_score = None
    if stats["repeated_keyword_ratio"] is None:
        add_warning("P09_KEYWORD_SAMPLE_LIMITED")
    else:
        keyword_repetition_reverse_score = (1.0 - stats["repeated_keyword_ratio"]) * 100.0

    cross_category_transition_score = uas_topic_switch_score
    if cross_category_transition_score is None:
        add_warning("P06_VIEWPOINT_SAMPLE_LIMITED")

    search_keyword_diversity_score = None
    if stats["search_events"] == 0:
        add_warning("P04_NO_SEARCH")
    elif stats["search_keyword_diversity_ratio"] is None:
        add_warning("P12_SEARCH_KEYWORD_SAMPLE_LIMITED")
    else:
        search_keyword_diversity_score = stats["search_keyword_diversity_ratio"] * 100.0

    score_components["VOS"] = [
        component("topic_concentration_reverse_score", "주제 집중도 완화", topic_concentration_reverse_score, 0.3),
        component("source_diversity_support_score", "출처 다양성 보조", source_diversity_support_score, 0.2),
        component("keyword_repetition_reverse_score", "키워드 반복 완화", keyword_repetition_reverse_score, 0.2),
        component("cross_category_transition_score", "교차 주제 전환", cross_category_transition_score, 0.2),
        component("search_keyword_diversity_score", "검색어 다양성", search_keyword_diversity_score, 0.1)
    ]
    scores["VOS"] = component_score(score_components["VOS"])
        
    return scores, exception_codes, score_components

def classify_16_type(scores: Dict[str, float]) -> Tuple[str, str, List[str]]:
    """
    Classifies the user into one of 16 media consumption personality types.
    Dimensions:
        D (Diversity) = (TDS + SBS) / 2 >= 50 ? H : L
        S (Stability) = (EBS + SMS) / 2 >= 60 ? H : L
        A (Agency)    = UAS >= 40 ? H : L
        O (Openness)  = VOS >= 50 ? H : L
    Returns:
        type_code: String code like "INTP" style representing D,S,A,O High/Low bits
        type_name: String title of the personality type
        tags: List of hash tags
    """
    # 1. Diversity
    div_avg = (scores["TDS"] + scores["SBS"]) / 2
    d_bit = "H" if div_avg >= 50.0 else "L"
    
    # 2. Stability
    sta_avg = (scores["EBS"] + scores["SMS"]) / 2
    s_bit = "H" if sta_avg >= 60.0 else "L"
    
    # 3. Agency
    a_bit = "H" if scores["UAS"] >= 40.0 else "L"
    
    # 4. Openness
    o_bit = "H" if scores["VOS"] >= 50.0 else "L"
    
    key = (d_bit, s_bit, a_bit, o_bit)
    type_name, tags = PERSONALITY_MAP.get(key, ("미지의 미디어 관찰자", ["#분석대기", "#신규성향"]))
    
    # Formulate a code name like "H-H-H-H" or "H-H-L-L"
    type_code = f"{d_bit}{s_bit}{a_bit}{o_bit}"
    
    return type_code, type_name, tags
