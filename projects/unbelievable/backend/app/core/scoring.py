import math
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

def compute_6axis_scores(
    events: List[Dict[str, Any]], 
    nlp_results: List[Dict[str, Any]]
) -> Tuple[Dict[str, float], List[str]]:
    """
    Computes 6-axis scores based on normalized watch history events and NLP results.
    Returns:
        axis_scores: Dict of axis code to score (0-100)
        exception_codes: List of triggered exceptions (P01, P04, etc.)
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

    def add_exception(code: str) -> None:
        if code not in exception_codes:
            exception_codes.append(code)

    def normalize_source(value: Any) -> str:
        if value is None:
            return "Unknown"
        source = str(value).strip()
        return source if source else "Unknown"

    def is_known_source(value: str) -> bool:
        return value.strip().lower() not in {"unknown", "none", "null", "n/a"}

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
    
    # Check minimum events constraint (FEAT_07: P01_DATA_SHORT)
    if len(events) < 10:
        add_exception("P01_DATA_SHORT")
        return scores, exception_codes
        
    # --- 1. 사용자주도성 (User Agency - UAS) ---
    # Formula: 100 * (search_events) / (search_events + watch_events)
    # If no searches exist, the Takeout export may not include search history.
    # Treat this as an interpretation limit, not as evidence of low agency.
    search_events = sum(1 for e in events if e.get("action_type") == "search")
    watch_events = sum(1 for e in events if e.get("action_type") == "view")
    total_actions = search_events + watch_events
    
    if search_events == 0:
        add_exception("P04_NO_SEARCH")
        scores["UAS"] = 50.0
    elif total_actions > 0:
        # Scale to 0-100. Searches usually are fewer, so apply log-scaling or multipliers.
        search_ratio = search_events / total_actions
        # Apply a scaling factor to make it practical (e.g. 5% ratio mapped to 50 score)
        scores["UAS"] = min(100.0, search_ratio * 400.0)
        
    # --- 2. 출처균형 (Source Balance - SBS) ---
    # Group by author_id / channel_name
    channel_counts = {}
    for e in events:
        ch = normalize_source(e.get("author_id") or e.get("source_surface"))
        channel_counts[ch] = channel_counts.get(ch, 0) + 1
        
    valid_sources = [source for source in channel_counts.keys() if is_known_source(source)]
    if not valid_sources:
        scores["SBS"] = 50.0
        add_exception("P05_SOURCE_MISSING")
    elif len(valid_sources) < 2:
        scores["SBS"] = 50.0
        add_exception("P05_SOURCE_SAMPLE_LIMITED")
    else:
        valid_total = sum(channel_counts[source] for source in valid_sources)
        shares = [(channel_counts[source] / valid_total) * 100 for source in valid_sources]
        hhi = calculate_hhi(shares)
        # HHI ranges from 0 to 10000. 10000 is single monopoly.
        # SBS = 100 - HHI_normalized (scaled to 100)
        scores["SBS"] = max(0.0, 100.0 - (hhi / 100.0))
        
    # --- 3. 주제다양성 (Topic Diversity - TDS) ---
    # Extract categories from nlp_results
    topic_counts = extract_topic_counts(nlp_results)
    valid_topic_count = len(topic_counts)
    total_topics = sum(topic_counts.values())

    if len(nlp_results) < 2 or valid_topic_count < 2:
        scores["TDS"] = 50.0
        add_exception("P02_TOPIC_SAMPLE_LIMITED")
    else:
        probs = [count / total_topics for count in topic_counts.values()]
        entropy = calculate_shannon_entropy(probs)
        # Max entropy for 10 categories is ~3.32 bits. Normalize against 3.5 bits max.
        scores["TDS"] = min(100.0, (entropy / 3.5) * 100.0)
        
    # --- 4. 감정균형 (Emotion Balance - EBS) ---
    # Distribute sentiment_scores (-1.0 to 1.0) into Positive/Neutral/Negative
    sentiments = [r.get("sentiment_score", 0.0) for r in nlp_results if "sentiment_score" in r]
    if len(sentiments) < 2:
        scores["EBS"] = 50.0
        add_exception("P03_SENTIMENT_SAMPLE_LIMITED")
    else:
        pos = sum(1 for s in sentiments if s > 0.25)
        neg = sum(1 for s in sentiments if s < -0.25)
        neu = len(sentiments) - (pos + neg)
        
        # Calculate entropy of 3 emotional states
        probs = [pos / len(sentiments), neg / len(sentiments), neu / len(sentiments)]
        entropy = calculate_shannon_entropy(probs)
        # Max entropy of 3 classes is log2(3) = 1.58. Scale to 100.
        scores["EBS"] = min(100.0, (entropy / 1.58) * 100.0)
        
    # --- 5. 유해/자극 안전 (Toxic Safety - SMS) ---
    # Count occurrences in moderation categories (VOS, Adult, Gore, etc.)
    # In full Cloud NL, we receive category names. Let's mock or check if there is content.
    toxic_hits = 0
    total_items = len(nlp_results)
    for r in nlp_results:
        # Check toxic moderation in categories
        for cat in r.get("categories_json", []):
            name = cat.get("name", "").lower()
            if any(toxic_word in name for toxic_word in ["adult", "violence", "drugs", "weapons", "gore", "hate"]):
                toxic_hits += 1
                
    if total_items < 2:
        scores["SMS"] = 50.0
        add_exception("P07_SAFETY_SAMPLE_LIMITED")
    else:
        toxic_ratio = toxic_hits / total_items
        scores["SMS"] = max(0.0, 100.0 - (toxic_ratio * 300.0))
        
    # --- 6. 관점개방성 (Perspective Openness - VOS) ---
    # Formula fallback: 100 * (1 - Dominant Topic Concentration Ratio)
    if valid_topic_count < 2:
        scores["VOS"] = 50.0
        add_exception("P06_VIEWPOINT_SAMPLE_LIMITED")
    else:
        max_topic_count = max(topic_counts.values())
        dom_ratio = max_topic_count / total_topics
        scores["VOS"] = max(0.0, (1.0 - dom_ratio) * 100.0)
        
    # Make sure all scores are clamped and rounded cleanly.
    for k in scores:
        scores[k] = round(max(0.0, min(100.0, scores[k])), 1)
        
    return scores, exception_codes

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
