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
)


# 16-type personality mapping kept for the existing dashboard/API contract.
PERSONALITY_MAP = {
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
    confidence: float,
    reason: str,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    numeric_score = NEUTRAL_COMPAT_SCORE if score is None else score
    return {
        "score": round(clamp_score(numeric_score), 1),
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "reason": reason,
        "warnings": sorted(set(warnings or [])),
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

    uas_metrics = {
        "search_ratio": features.get("search_ratio"),
        "direct_selection_ratio": features.get("direct_selection_ratio"),
        "curation_ratio": features.get("curation_ratio"),
        "participation_ratio": features.get("participation_ratio"),
    }
    uas_score, uas_coverage, uas_missing = _weighted_ratio_score(uas_metrics, UAS_WEIGHTS)
    uas_warnings = []
    if features.get("search_count", 0) == 0:
        uas_warnings.append("search events missing")
    if "direct_selection_ratio" in uas_missing:
        uas_warnings.append("direct selection ratio unavailable in current norm_event schema")
    details["UAS"] = _detail(
        uas_score,
        base_confidence * uas_coverage,
        "weighted agency ratio from search, curation, and participation signals",
        uas_warnings,
    )

    channel_distribution = features.get("channel_distribution", {})
    sbs_score = _hhi_balance_score(channel_distribution)
    sbs_confidence = base_confidence * min(
        1.0,
        len(channel_distribution) / MIN_DATA_REQUIREMENTS["channel_count"],
    )
    sbs_warnings = []
    if not channel_distribution:
        sbs_warnings.append("channel distribution missing")
    elif len(channel_distribution) < 2:
        sbs_warnings.append("channel sample limited")
    details["SBS"] = _detail(
        sbs_score,
        sbs_confidence,
        "HHI balance score from channel/source distribution",
        sbs_warnings,
    )

    topic_distribution = features.get("topic_distribution", {})
    tds_score = _entropy_score(topic_distribution)
    topic_total = sum(topic_distribution.values())
    tds_confidence = base_confidence * min(
        1.0,
        topic_total / MIN_DATA_REQUIREMENTS["topic_count"],
    )
    tds_warnings = []
    if len(topic_distribution) <= 1:
        tds_warnings.append("topic sample limited")
    details["TDS"] = _detail(
        tds_score,
        tds_confidence,
        "Shannon entropy normalized by active topic count",
        tds_warnings,
    )

    sentiment_distribution = features.get("sentiment_distribution", {})
    sentiment_total = sum(sentiment_distribution.values())
    ebs_score = (
        _entropy_score(sentiment_distribution)
        if sentiment_total >= MIN_DATA_REQUIREMENTS["sentiment_count"]
        else None
    )
    ebs_confidence = base_confidence * min(
        1.0,
        sentiment_total / MIN_DATA_REQUIREMENTS["sentiment_count"],
    )
    ebs_warnings = []
    if sentiment_total < MIN_DATA_REQUIREMENTS["sentiment_count"]:
        ebs_warnings.append("sentiment sample limited")
    details["EBS"] = _detail(
        ebs_score,
        ebs_confidence,
        "emotion distribution entropy across positive, neutral, and negative buckets",
        ebs_warnings,
    )

    sms_metrics = {
        "toxic_ratio": features.get("toxic_ratio"),
        "harmful_keyword_ratio": features.get("harmful_keyword_ratio"),
        "shorts_ratio": features.get("shorts_ratio"),
        "repeated_short_exposure_ratio": features.get("repeated_short_exposure_ratio"),
    }
    sms_penalty, sms_coverage, sms_missing = _weighted_ratio_score(sms_metrics, SMS_WEIGHTS)
    sms_score = None if sms_penalty is None else 100.0 - sms_penalty
    sms_warnings = []
    if features.get("nlp_count", 0) < MIN_DATA_REQUIREMENTS["safety_count"]:
        sms_warnings.append("safety NLP sample limited")
    if sms_missing:
        sms_warnings.append("some safety penalty terms unavailable")
    details["SMS"] = _detail(
        sms_score,
        base_confidence * sms_coverage,
        "100 minus weighted safety/stimulus penalty ratios",
        sms_warnings,
    )

    vos_metrics = {
        "topic_concentration": _max_ratio(topic_distribution),
        "channel_concentration": _max_ratio(channel_distribution),
        "search_repetition": _max_ratio(features.get("search_keyword_distribution", {})),
    }
    concentration, vos_coverage, vos_missing = _weighted_ratio_score(vos_metrics, VOS_WEIGHTS)
    vos_score = None if concentration is None else 100.0 - concentration
    vos_warnings = []
    if "topic_concentration" in vos_missing:
        vos_warnings.append("topic concentration unavailable")
    if "channel_concentration" in vos_missing:
        vos_warnings.append("channel concentration unavailable")
    if "search_repetition" in vos_missing:
        vos_warnings.append("search repetition unavailable")
    # TODO: Add explicit opposing-viewpoint query detection in the next scoring phase.
    details["VOS"] = _detail(
        vos_score,
        base_confidence * vos_coverage,
        "openness estimated from topic, channel, and search-keyword concentration",
        vos_warnings,
    )

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

    return codes


def compute_6axis_score_details(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[str], Dict[str, Any]]:
    features = extract_features(events, nlp_results)
    details = calculate_scores_v2(events, nlp_results)
    exception_codes = _exception_codes_from_details(features, details)
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
