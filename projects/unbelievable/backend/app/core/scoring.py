import math
from typing import Any, Dict, List, Optional, Tuple

from app.core.features import extract_features
from app.core.score_config import (
    AXIS_CODES,
    CLASSIFICATION_THRESHOLDS,
    MIN_DATA_REQUIREMENTS,
    NEUTRAL_COMPAT_SCORE,
    SCORE_RANGE,
    SMS_WEIGHTS,
    UAS_WEIGHTS,
    VOS_WEIGHTS,
    MAX_TOPIC_CATEGORIES,
    EDUCATIONAL_CATEGORIES,
    CONCENTRATION_BETA,
)


from app.core.persona_loader import persona_loader
PERSONALITY_MAP = persona_loader.legacy_mbti_map


def calculate_shannon_entropy(probabilities: List[float]) -> float:
    if not probabilities:
        return 0.0
    entropy = 0.0
    for probability in probabilities:
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy


def calculate_hhi(shares: List[float]) -> float:
    """Compatibility helper for percentage-share HHI calculations."""
    if not shares:
        return 10000.0
    return sum(share ** 2 for share in shares)


def clamp_score(value: float) -> float:
    return max(SCORE_RANGE["min"], min(SCORE_RANGE["max"], value))


def _detail(
    score: Optional[float],
    confidence: Any,
    reason: str,
    warnings: Optional[List[str]] = None,
    available: bool = True,
) -> Dict[str, Any]:
    numeric_score = NEUTRAL_COMPAT_SCORE if score is None else score
    if isinstance(confidence, str):
        conf_val = confidence
    else:
        conf_val = round(max(0.0, min(1.0, float(confidence))), 3)
    return {
        "score": round(clamp_score(numeric_score), 1),
        "confidence": conf_val,
        "reason": reason,
        "warnings": sorted(set(warnings or [])),
        "available": available,
    }



def _weighted_ratio_score(
    metrics: Dict[str, Optional[float]],
    weights: Dict[str, float],
) -> Tuple[Optional[float], float, List[str]]:
    used_weight = 0.0
    weighted_sum = 0.0
    missing: List[str] = []

    for key, weight in weights.items():
        value = metrics.get(key)
        if value is None:
            missing.append(key)
            continue
        weighted_sum += max(0.0, min(1.0, value)) * weight
        used_weight += weight

    if used_weight <= 0:
        return None, 0.0, missing

    coverage = used_weight / max(sum(weights.values()), 1.0)
    return (weighted_sum / used_weight) * 100.0, coverage, missing


def _distribution_ratios(distribution: Dict[str, int]) -> List[float]:
    total = sum(distribution.values())
    if total <= 0:
        return []
    return [count / total for count in distribution.values() if count > 0]


def _entropy_score(distribution: Dict[str, int]) -> Optional[float]:
    ratios = _distribution_ratios(distribution)
    active_count = len(ratios)
    if active_count <= 1:
        return None
    entropy = calculate_shannon_entropy(ratios)
    max_entropy = math.log2(active_count)
    if max_entropy <= 0:
        return None
    return (entropy / max_entropy) * 100.0


def _hhi_balance_score(distribution: Dict[str, int]) -> Optional[float]:
    ratios = _distribution_ratios(distribution)
    if len(ratios) <= 1:
        return None
    hhi = sum(ratio ** 2 for ratio in ratios)
    return (1.0 - hhi) * 100.0


def _max_ratio(distribution: Dict[str, int]) -> Optional[float]:
    total = sum(distribution.values())
    if total <= 0 or not distribution:
        return None
    return max(distribution.values()) / total


def calculate_scores_v2(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Return detailed explainable scores without changing the legacy API."""
    features = extract_features(events, nlp_results)
    base_confidence = float(features.get("data_confidence", 0.0))
    common_warnings = list(features.get("data_quality_warnings", []))
    details: Dict[str, Dict[str, Any]] = {}

    has_estimated_duration = any(e.get("is_duration_estimated") for e in events)
    has_duration = any(e.get("time_delta_sec") is not None or e.get("estimated_duration_sec") is not None for e in events if e.get("action_type") == "view")

    # Determine status of duration-related metrics
    duration_status = "used"
    if not has_duration:
        duration_status = "missing"
    elif has_estimated_duration:
        duration_status = "estimated"

    # 1. UAS (User Agency Score)
    search_ratio = features.get("search_ratio")
    direct_selection_ratio = features.get("direct_selection_ratio")
    
    uas_metrics = {
        "search_ratio": search_ratio,
        "direct_selection_ratio": direct_selection_ratio,
        "curation_ratio": features.get("curation_ratio"),
        "participation_ratio": features.get("participation_ratio"),
    }
    
    uas_warnings = []
    uas_available = True
    if search_ratio is None and direct_selection_ratio is None:
        uas_available = False
        uas_score = None
        uas_confidence = "low"
        uas_warnings.append("검색 기록 또는 직접 선택 경로 데이터가 부족하여 사용자 주도성 지표는 참고용으로만 표시됩니다.")
    else:
        uas_score, uas_coverage, uas_missing = _weighted_ratio_score(uas_metrics, UAS_WEIGHTS)
        uas_confidence = base_confidence * uas_coverage
        if search_ratio is None:
            uas_warnings.append("search events missing")
        if direct_selection_ratio is None:
            uas_warnings.append("direct selection ratio unavailable in current norm_event schema")
            
    uas_status = {
        "search_ratio": "used" if search_ratio is not None else "missing",
        "direct_selection_ratio": "missing",
        "curation_ratio": "used" if features.get("curation_ratio") is not None else "missing",
        "participation_ratio": "used" if features.get("participation_ratio") is not None else "missing"
    }
    uas_components = {
        "search_ratio": round(features.get("search_ratio", 0.0) * 100, 1) if search_ratio is not None else None,
        "direct_selection_ratio": round(features.get("direct_selection_ratio", 0.0) * 100, 1) if direct_selection_ratio is not None else None,
        "curation_ratio": round(features.get("curation_ratio", 0.0) * 100, 1) if features.get("curation_ratio") is not None else 0.0,
        "participation_ratio": round(features.get("participation_ratio", 0.0) * 100, 1) if features.get("participation_ratio") is not None else 0.0,
        "status": uas_status
    }
    details["UAS"] = _detail(
        uas_score,
        uas_confidence,
        "weighted agency ratio from search, curation, and participation signals",
        uas_warnings,
        available=uas_available
    )
    details["UAS"]["score_components"] = uas_components

    # 2. SBS (Source Balance Score)
    channel_distribution = features.get("channel_distribution", {})
    ratios = _distribution_ratios(channel_distribution)
    n_sources = len(ratios)
    hhi = sum(ratio ** 2 for ratio in ratios) if ratios else 1.0
    legacy_hhi_inverse = (1.0 - hhi) * 100.0
    
    sbs_warnings = []
    sbs_available = True
    if n_sources == 0:
        sbs_available = False
        sbs_score = None
        sbs_confidence = "low"
        sbs_warnings.append("채널 정보가 부족하여 출처 균형은 참고용으로만 표시됩니다.")
    else:
        if n_sources <= 1:
            sbs_score = 0.0
        else:
            relative_balance = ((1.0 - hhi) / (1.0 - 1.0 / n_sources)) * 100.0
            source_count_factor = 0.65 + 0.35 * (1.0 - math.exp(-n_sources / 3.0))
            sbs_score = relative_balance * source_count_factor
        sbs_confidence = base_confidence * min(
            1.0,
            n_sources / MIN_DATA_REQUIREMENTS["channel_count"],
        )
        if n_sources < 2:
            sbs_warnings.append("channel sample limited")
            
    sbs_status = {
        "channel_distribution": "used" if n_sources > 0 else "missing",
        "relative_hhi": "used" if n_sources > 1 else "limited"
    }
    sbs_components = {
        "legacy_hhi_inverse_score": round(legacy_hhi_inverse, 1) if n_sources > 0 else None,
        "relative_hhi_balance_score": round(sbs_score, 1) if sbs_score is not None else None,
        "unique_source_count_adjustment": round(sbs_score - legacy_hhi_inverse, 1) if (sbs_score is not None and n_sources > 1) else 0.0,
        "source_confidence": sbs_confidence if isinstance(sbs_confidence, str) else round(sbs_confidence, 3),
        "is_actual_channel_based": bool(n_sources > 0),
        "status": sbs_status
    }
    details["SBS"] = _detail(
        sbs_score,
        sbs_confidence,
        "HHI balance score from channel/source distribution",
        sbs_warnings,
        available=sbs_available
    )
    details["SBS"]["score_components"] = sbs_components

    # 3. TDS (Topic Diversity Score)
    topic_distribution = features.get("topic_distribution", {})
    local_category_distribution = features.get("local_category_distribution", {})
    
    nlp_ratios = _distribution_ratios(topic_distribution)
    nlp_entropy = calculate_shannon_entropy(nlp_ratios)
    nlp_score = (nlp_entropy / math.log2(MAX_TOPIC_CATEGORIES)) * 100.0 if nlp_ratios else 0.0
    
    local_ratios = _distribution_ratios(local_category_distribution)
    local_entropy = calculate_shannon_entropy(local_ratios)
    local_score = (local_entropy / math.log2(MAX_TOPIC_CATEGORIES)) * 100.0 if local_ratios else 0.0
    
    nlp_count = features.get("nlp_count", 0)
    use_local_fallback = nlp_count < 2 or sum(topic_distribution.values()) < 3
    
    tds_score = local_score if use_local_fallback else nlp_score
    
    if use_local_fallback:
        tds_confidence = base_confidence * 0.5
    else:
        tds_confidence = base_confidence * min(
            1.0,
            sum(topic_distribution.values()) / MIN_DATA_REQUIREMENTS["topic_count"],
        )

    # Check etc/uncategorized ratio for penalty
    uncategorized_ratio = 0.0
    if use_local_fallback:
        local_total = sum(local_category_distribution.values())
        if local_total > 0:
            etc_count = sum(local_category_distribution.get(k, 0) for k in ["기타", "기타/미분류", "미분류"])
            uncategorized_ratio = etc_count / local_total
    else:
        nlp_total = sum(topic_distribution.values())
        if nlp_total > 0:
            etc_count = sum(topic_distribution.get(k, 0) for k in ["기타", "기타/미분류", "미분류"])
            uncategorized_ratio = etc_count / nlp_total

    tds_warnings = []
    if use_local_fallback:
        tds_warnings.append("NLP sample limited; using local keyword topic diversity fallback")
    elif len(topic_distribution) <= 1:
        tds_warnings.append("topic sample limited")

    if uncategorized_ratio >= 0.7:
        tds_warnings.append("기타/미분류 카테고리 비중이 높아 주제 다양성 점수는 참고용으로 해석해야 합니다.")
    if uncategorized_ratio >= 0.8:
        tds_confidence = 0.0
        tds_warnings.append("기타/미분류 카테고리 비율이 극도로 높아 분석 신뢰도가 저하되었습니다.")
        
    tds_status = {
        "nlp_category_entropy": "limited" if use_local_fallback else "used",
        "local_keyword_category_entropy": "used"
    }
    tds_components = {
        "nlp_category_entropy": round(nlp_score, 1),
        "local_keyword_category_entropy": round(local_score, 1),
        "max_topic_categories_applied": True,
        "nlp_sample_insufficient_confidence_reduced": bool(use_local_fallback),
        "tds_confidence": tds_confidence,
        "topic_diversity_confidence": tds_confidence,
        "uncategorized_ratio": round(uncategorized_ratio, 3),
        "status": tds_status
    }
    details["TDS"] = _detail(
        tds_score,
        tds_confidence,
        "Shannon entropy normalized by K=15 possible topic categories",
        tds_warnings,
    )
    details["TDS"]["tds_confidence"] = tds_confidence
    details["TDS"]["topic_diversity_confidence"] = tds_confidence
    details["TDS"]["score_components"] = tds_components

    # 4. EBS (Emotion Balance Score)
    sentiment_distribution = features.get("sentiment_distribution", {})
    sentiment_total = sum(sentiment_distribution.values())
    
    neg_ratio = sentiment_distribution.get("negative", 0) / max(1, sentiment_total)
    neg_penalty = neg_ratio * 40.0 if sentiment_total > 0 else 0.0
    
    # Stimulus Keyword Penalty
    stimulus_keywords = ["충격", "폭로", "분노", "속보", "논란", "레전드", "경악", "극혐", "shocking", "expose", "scandal"]
    calm_keywords = ["asmr", "명상", "힐링", "차분", "calm", "수면", "relax", "healing", "peaceful", "classic", "클래식"]
    
    stimulus_event_count = 0
    calm_event_count = 0
    for e in events:
        txt = (e.get("text_base") or "").lower()
        has_calm = any(ck in txt for ck in calm_keywords)
        if has_calm:
            calm_event_count += 1
            continue
        
        has_stimulus = any(sk in txt for sk in stimulus_keywords)
        if has_stimulus:
            stimulus_event_count += 1
            
    stim_ratio = stimulus_event_count / max(1, len(events))
    stim_penalty = stim_ratio * 30.0
    
    # Neutral / Info / Calm Stability signals
    stable_count = sentiment_distribution.get("neutral", 0)
    stable_local_count = sum(local_category_distribution.get(cat, 0) for cat in ["코딩/기술", "금융/투자", "교육/강의", "건강/운동"])
    stability_ratio = (stable_count + stable_local_count + calm_event_count) / max(1, len(events) + nlp_count)
    stability_boost = stability_ratio * 20.0
    
    ebs_score = 100.0 - neg_penalty - stim_penalty + stability_boost
    
    # Blend with Sejong's stability_factor if available
    stability_factors = [r.get("stability_factor") for r in nlp_results if r.get("stability_factor") is not None]
    if stability_factors:
        avg_stability = sum(stability_factors) / len(stability_factors)
        ebs_score = (ebs_score * 0.7) + (avg_stability * 100.0 * 0.3)

    ebs_confidence = base_confidence * min(
        1.0,
        sentiment_total / MIN_DATA_REQUIREMENTS["sentiment_count"],
    )
    ebs_warnings = []
    if sentiment_total < MIN_DATA_REQUIREMENTS["sentiment_count"]:
        ebs_warnings.append("sentiment sample limited")
        
    legacy_ebs = _entropy_score(sentiment_distribution)
    ebs_status = {
        "sentiment_entropy": "used" if sentiment_total > 0 else "missing",
        "stability_factors": "used" if stability_factors else "missing"
    }
    ebs_components = {
        "legacy_sentiment_entropy_score": round(legacy_ebs, 1) if legacy_ebs is not None else 50.0,
        "negative_sentiment_penalty": round(neg_penalty, 1),
        "stimulus_keyword_penalty": round(stim_penalty, 1),
        "neutral_info_calm_stability_signal_ratio": round(stability_ratio, 3),
        "calm_keyword_protection_applied": True,
        "status": ebs_status
    }
    details["EBS"] = _detail(
        ebs_score,
        ebs_confidence,
        "stability-based emotion index tracking negative penalties and neutral/calm boosters",
        ebs_warnings,
    )
    details["EBS"]["score_components"] = ebs_components

    # 5. SMS (Safety and Stimulus Score)
    toxic_ratio = features.get("toxic_ratio")
    if nlp_count < 2:
        toxic_ratio = None
        
    has_actual_duration = any(e.get("time_delta_sec") is not None for e in events if e.get("action_type") == "view")
    repeated_short_exposure_ratio = features.get("repeated_short_exposure_ratio", 0.0)
    adjusted_repeated_short_ratio = repeated_short_exposure_ratio * (1.0 if has_actual_duration else 0.2)
    
    sms_metrics = {
        "toxic_ratio": toxic_ratio,
        "harmful_keyword_ratio": features.get("harmful_keyword_ratio"),
        "shorts_ratio": features.get("shorts_ratio"),
        "repeated_short_exposure_ratio": adjusted_repeated_short_ratio,
    }
    sms_penalty, sms_coverage, sms_missing = _weighted_ratio_score(sms_metrics, SMS_WEIGHTS)
    sms_score = None if sms_penalty is None else 100.0 - sms_penalty
    
    # Apply Sejong's safety_factor if available
    safety_factors = [r.get("safety_factor") for r in nlp_results if r.get("safety_factor") is not None]
    if safety_factors and sms_score is not None:
        avg_safety = sum(safety_factors) / len(safety_factors)
        sms_score = (sms_score * 0.8) + (avg_safety * 100.0 * 0.2)

    sms_warnings = []
    if nlp_count < MIN_DATA_REQUIREMENTS["safety_count"]:
        sms_warnings.append("safety NLP sample limited; toxic category ratio excluded from safety score")
    if sms_missing:
        sms_warnings.append("some safety penalty terms unavailable")
        
    sms_status = {
        "toxic_ratio": "used" if toxic_ratio is not None else "missing",
        "harmful_keyword_ratio": "used",
        "shorts_ratio": "used",
        "repeated_short_exposure_ratio": duration_status,
        "safety_factors": "used" if safety_factors else "missing"
    }
    sms_components = {
        "toxic_ratio_penalty": round(toxic_ratio * SMS_WEIGHTS["toxic_ratio"] * 100, 1) if toxic_ratio is not None else 0.0,
        "harmful_keyword_penalty": round(features.get("harmful_keyword_ratio", 0.0) * SMS_WEIGHTS["harmful_keyword_ratio"] * 100, 1),
        "shorts_ratio_penalty": round(features.get("shorts_ratio", 0.0) * SMS_WEIGHTS["shorts_ratio"] * 100, 1),
        "repeated_shorts_penalty": round(adjusted_repeated_short_ratio * SMS_WEIGHTS["repeated_short_exposure_ratio"] * 100, 1),
        "is_repeated_shorts_calibrated_by_duration": not has_actual_duration,
        "status": sms_status
    }
    details["SMS"] = _detail(
        sms_score,
        base_confidence * sms_coverage,
        "100 minus weighted safety/stimulus penalty ratios",
        sms_warnings,
    )
    details["SMS"]["score_components"] = sms_components

    # 6. VOS (Viewpoint Openness Score)
    top_topic = None
    if topic_distribution:
        top_topic = max(topic_distribution, key=topic_distribution.get)
        
    top_local = None
    if local_category_distribution:
        top_local = max(local_category_distribution, key=local_category_distribution.get)
        
    raw_topic_concentration = _max_ratio(topic_distribution)
    raw_channel_concentration = _max_ratio(channel_distribution)
    raw_search_repetition = _max_ratio(features.get("search_keyword_distribution", {}))
    
    adjusted_items = []
    
    # Topic relaxation
    adjusted_topic_concentration = raw_topic_concentration
    if raw_topic_concentration is not None and top_topic in EDUCATIONAL_CATEGORIES:
        adjusted_topic_concentration = raw_topic_concentration * CONCENTRATION_BETA
        adjusted_items.append("topic_concentration")
        
    # Channel relaxation
    adjusted_channel_concentration = raw_channel_concentration
    if raw_channel_concentration is not None and top_local in EDUCATIONAL_CATEGORIES:
        adjusted_channel_concentration = raw_channel_concentration * CONCENTRATION_BETA
        adjusted_items.append("channel_concentration")
        
    adjusted_vos_metrics = {
        "topic_concentration": adjusted_topic_concentration,
        "channel_concentration": adjusted_channel_concentration,
        "search_repetition": raw_search_repetition,
    }
    concentration, vos_coverage, vos_missing = _weighted_ratio_score(adjusted_vos_metrics, VOS_WEIGHTS)
    vos_score = None if concentration is None else 100.0 - concentration
    
    raw_vos_metrics = {
        "topic_concentration": raw_topic_concentration,
        "channel_concentration": raw_channel_concentration,
        "search_repetition": raw_search_repetition,
    }
    raw_concentration, _, _ = _weighted_ratio_score(raw_vos_metrics, VOS_WEIGHTS)
    raw_vos_score = None if raw_concentration is None else 100.0 - raw_concentration
    
    vos_warnings = []
    if "topic_concentration" in vos_missing:
        vos_warnings.append("topic concentration unavailable")
    if "channel_concentration" in vos_missing:
        vos_warnings.append("channel concentration unavailable")
    if "search_repetition" in vos_missing:
        vos_warnings.append("search repetition unavailable")
        
    vos_status = {
        "topic_concentration": "used" if raw_topic_concentration is not None else "missing",
        "channel_concentration": "used" if raw_channel_concentration is not None else "missing",
        "search_repetition": "used" if raw_search_repetition is not None else "missing"
    }
    vos_components = {
        "raw_concentration_score": round(raw_vos_score, 1) if raw_vos_score is not None else 50.0,
        "adjusted_concentration_score": round(vos_score, 1) if vos_score is not None else 50.0,
        "beta_applied": len(adjusted_items) > 0,
        "beta_value": CONCENTRATION_BETA,
        "productive_immersion_adjusted_fields": adjusted_items,
        "status": vos_status
    }
    details["VOS"] = _detail(
        vos_score,
        base_confidence * vos_coverage,
        "openness estimated from topic, channel, and search-keyword concentration with educational beta adjustment",
        vos_warnings,
    )
    details["VOS"]["score_components"] = vos_components

    # Post processing for mock/fallback labels
    mock_sensitive_axes = {"TDS", "EBS", "SMS", "VOS"}
    for axis in AXIS_CODES:
        axis_warnings = details[axis]["warnings"] + common_warnings
        if features.get("mock_used") and axis in mock_sensitive_axes:
            axis_warnings.append("mock data used")
            details[axis]["confidence"] = 0.0
        elif features.get("fallback_used") and axis in mock_sensitive_axes:
            axis_warnings.append("fallback data used")
            details[axis]["confidence"] = round(details[axis]["confidence"] * 0.2, 3)
        details[axis]["warnings"] = sorted(set(axis_warnings))

    return details


def _exception_codes_from_details(
    features: Dict[str, Any],
    details: Dict[str, Dict[str, Any]],
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]]
) -> List[str]:
    codes: List[str] = []

    def add(code: str) -> None:
        if code not in codes:
            codes.append(code)

    primary_event_count = features.get("watch_count", 0) + features.get("search_count", 0)
    if primary_event_count < MIN_DATA_REQUIREMENTS["event_count"]:
        add("P01_DATA_SHORT")
    if features.get("search_count", 0) == 0:
        add("P04_NO_SEARCH")
    if len(features.get("topic_distribution", {})) < 2:
        add("P02_TOPIC_SAMPLE_LIMITED")
    if sum(features.get("sentiment_distribution", {}).values()) < MIN_DATA_REQUIREMENTS["sentiment_count"]:
        add("P03_SENTIMENT_SAMPLE_LIMITED")

    channel_count = len(features.get("channel_distribution", {}))
    if channel_count == 0:
        add("P05_SOURCE_MISSING")
    elif channel_count < 2:
        add("P05_SOURCE_SAMPLE_LIMITED")
    if len(features.get("topic_distribution", {})) < 2 or channel_count < 2:
        add("P06_VIEWPOINT_SAMPLE_LIMITED")

    if features.get("nlp_count", 0) < MIN_DATA_REQUIREMENTS["safety_count"]:
        add("P07_SAFETY_SAMPLE_LIMITED")
    if features.get("mock_used"):
        add("P08_MOCK_DATA_USED")
    if features.get("fallback_used"):
        add("P09_FALLBACK_DATA_USED")
    if any("direct selection" in warning for warning in details["UAS"].get("warnings", [])):
        add("P10_DIRECT_SELECTION_UNAVAILABLE")

    # Duration Checks
    has_estimated_duration = any(e.get("is_duration_estimated") for e in events)
    has_duration = any(e.get("time_delta_sec") is not None or e.get("estimated_duration_sec") is not None for e in events if e.get("action_type") == "view")
    
    if has_estimated_duration:
        add("P10_DURATION_ESTIMATED")
    elif not has_duration:
        add("P10_DURATION_MISSING")

    # NLP Fallback Checks
    nlp_providers = [r.get("nlp_provider") for r in nlp_results if r.get("nlp_provider") is not None]
    if "rule_based_fallback" in nlp_providers:
        add("P15_NLP_FALLBACK_USED")

    # Category Confidence checks
    confidences = [r.get("category_confidence") for r in nlp_results if r.get("category_confidence") is not None]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        if avg_confidence < 0.5:
            add("P16_CATEGORY_CONFIDENCE_LOW")

    return codes


def compute_6axis_score_details(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[str], Dict[str, Any]]:
    features = extract_features(events, nlp_results)
    details = calculate_scores_v2(events, nlp_results)
    exception_codes = _exception_codes_from_details(features, details, events, nlp_results)
    return details, exception_codes, features


def compute_6axis_scores(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
) -> Tuple[Dict[str, float], List[str]]:
    detailed, exception_codes, _features = compute_6axis_score_details(events, nlp_results)
    axis_scores = {
        axis: detailed.get(axis, {}).get("score", NEUTRAL_COMPAT_SCORE)
        for axis in AXIS_CODES
    }
    return axis_scores, exception_codes


def classify_16_type(scores: Dict[str, float]) -> Tuple[str, str, List[str]]:
    div_avg = (scores["TDS"] + scores["SBS"]) / 2
    d_bit = "H" if div_avg >= CLASSIFICATION_THRESHOLDS["diversity"] else "L"

    sta_avg = (scores["EBS"] + scores["SMS"]) / 2
    s_bit = "H" if sta_avg >= CLASSIFICATION_THRESHOLDS["stability"] else "L"

    a_bit = "H" if scores["UAS"] >= CLASSIFICATION_THRESHOLDS["agency"] else "L"
    o_bit = "H" if scores["VOS"] >= CLASSIFICATION_THRESHOLDS["openness"] else "L"

    key = (d_bit, s_bit, a_bit, o_bit)
    type_name, tags = PERSONALITY_MAP.get(
        key,
        ("미지의 미디어 관찰자", ["#분석대기", "#신규성향"]),
    )
    return f"{d_bit}{s_bit}{a_bit}{o_bit}", type_name, tags
