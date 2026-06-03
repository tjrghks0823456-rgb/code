import math
from typing import Any, Dict, List, Optional, Tuple

from app.core.content_filters import detect_ad_event_reason
from app.core.score_config import (
    CONFIDENCE_WEIGHTS,
    DURATION_CONFIDENCE_VALUES,
    HARMFUL_KEYWORDS,
    MIN_DATA_REQUIREMENTS,
    SENTIMENT_THRESHOLDS,
    TOXIC_CATEGORY_KEYWORDS,
)
from app.core.shorts_analysis import build_shorts_analysis


UNKNOWN_VALUES = {"", "unknown", "none", "null", "n/a"}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _lower(value: Any) -> str:
    return _clean_text(value).lower()


def _as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _is_known(value: Any) -> bool:
    return _lower(value) not in UNKNOWN_VALUES


def _top_level_category(category: Any) -> str:
    if isinstance(category, dict):
        raw_name = category.get("name", "")
    else:
        raw_name = category
    name = _clean_text(raw_name)
    if not name:
        return ""
    parts = [part.strip() for part in name.split("/") if part.strip()]
    return parts[0] if parts else name


def _duration_confidence_value(label: Any) -> float:
    key = _lower(label) or "unknown"
    return DURATION_CONFIDENCE_VALUES.get(key, DURATION_CONFIDENCE_VALUES["unknown"])


def _content_format(event: Dict[str, Any], action_type: str) -> str:
    explicit = _lower(event.get("content_format"))
    if explicit and explicit != "unknown":
        return explicit

    title_url = _lower(
        event.get("title_url")
        or event.get("titleUrl")
        or event.get("url")
        or event.get("URL")
    )
    text_base = _lower(event.get("text_base") or event.get("title_text") or event.get("title"))
    video_id = _clean_text(event.get("video_id"))

    if "/shorts/" in title_url or "youtube.com/shorts" in title_url:
        return "shorts"
    if "/live/" in title_url or "youtube.com/live" in title_url or "실시간 스트리밍" in text_base:
        return "live"
    if action_type == "view" and ("watch?v=" in title_url or video_id):
        return "standard_video"
    return "unknown"


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def normalize_event(event: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Normalize the current norm_event dict without inventing new raw fields."""
    warnings: List[str] = []
    if not isinstance(event, dict):
        return {}, ["event row was not a dict"]

    action_type = _lower(event.get("action_type"))
    source_type = _lower(event.get("source_type"))

    if not action_type:
        if source_type == "watch_history":
            action_type = "view"
            warnings.append("action_type missing; inferred view from source_type")
        elif source_type == "search_history":
            action_type = "search"
            warnings.append("action_type missing; inferred search from source_type")
        elif source_type in {"subscription", "playlist", "comment", "live_chat", "channel"}:
            action_type = source_type
            warnings.append("action_type missing; inferred from source_type")
        else:
            warnings.append("action_type missing")

    if not source_type:
        if action_type == "view":
            source_type = "watch_history"
            warnings.append("source_type missing; inferred watch_history from action_type")
        elif action_type == "search":
            source_type = "search_history"
            warnings.append("source_type missing; inferred search_history from action_type")
        elif action_type:
            source_type = action_type
            warnings.append("source_type missing; inferred from action_type")
        else:
            warnings.append("source_type missing")

    text_base = _clean_text(event.get("text_base") or event.get("title_text") or event.get("title"))
    if not text_base:
        warnings.append("text_base missing")

    channel_key = _clean_text(
        event.get("channel_name")
        or event.get("channel_url")
        or event.get("author_id")
        or event.get("source_surface")
    )
    if not _is_known(channel_key):
        channel_key = ""

    actual_duration = _as_float(event.get("time_delta_sec"))
    estimated_duration = _as_float(event.get("estimated_duration_sec"))
    duration_sec = actual_duration if actual_duration is not None else estimated_duration

    duration_label = event.get("duration_confidence")
    if actual_duration is not None and not duration_label:
        duration_label = "timeline"
    elif estimated_duration is not None and not duration_label:
        duration_label = "estimated"

    title_url = _clean_text(event.get("title_url"))
    content_format = _content_format(event, action_type)
    intent_level = _lower(event.get("intent_level"))
    if not intent_level:
        intent_level = "active_search" if action_type == "search" or source_type == "search_history" else "unknown"
    is_short = content_format == "shorts"

    return {
        "id": event.get("id"),
        "event_time": event.get("event_time"),
        "action_type": action_type,
        "source_type": source_type,
        "text_base": text_base,
        "channel_key": channel_key,
        "source_surface": _lower(event.get("source_surface")),
        "content_format": content_format,
        "intent_level": intent_level,
        "duration_sec": duration_sec,
        "duration_confidence": _duration_confidence_value(duration_label),
        "duration_confidence_label": _lower(duration_label) or "unknown",
        "is_estimated_duration": actual_duration is None and estimated_duration is not None,
        "is_short": is_short,
        "storage": _clean_text(event.get("__storage")),
    }, warnings


def extract_features(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized_events: List[Dict[str, Any]] = []
    warnings: List[str] = []
    excluded_ad_count = 0

    for event in events or []:
        if detect_ad_event_reason(event):
            excluded_ad_count += 1
            continue
        normalized, event_warnings = normalize_event(event)
        if normalized:
            normalized_events.append(normalized)
        warnings.extend(event_warnings)

    action_counts: Dict[str, int] = {}
    source_type_counts: Dict[str, int] = {}
    channel_distribution: Dict[str, int] = {}
    search_keyword_distribution: Dict[str, int] = {}
    durations: List[float] = []
    duration_confidences: List[float] = []
    harmful_keyword_hits = 0

    watch_count = 0
    search_count = 0
    shorts_count = 0
    standard_video_count = 0
    live_count = 0
    unknown_format_count = 0
    estimated_duration_count = 0

    for event in normalized_events:
        action = event["action_type"]
        source_type = event["source_type"]
        content_format = event.get("content_format", "unknown")
        intent_level = event.get("intent_level", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

        is_watch = action == "view" or source_type == "watch_history"
        is_search = action == "search" or source_type == "search_history" or intent_level == "active_search"

        if is_watch:
            watch_count += 1
            if content_format == "standard_video":
                standard_video_count += 1
            elif content_format == "live":
                live_count += 1
            elif content_format == "unknown":
                unknown_format_count += 1
            duration = event.get("duration_sec")
            if duration is not None:
                durations.append(duration)
                duration_confidences.append(event.get("duration_confidence", 0.0))
            if event.get("is_estimated_duration"):
                estimated_duration_count += 1
            if event.get("is_short"):
                shorts_count += 1

        if is_search:
            search_count += 1
            keyword = _lower(event.get("text_base"))
            if keyword:
                search_keyword_distribution[keyword] = search_keyword_distribution.get(keyword, 0) + 1

        channel_key = event.get("channel_key")
        if channel_key and not is_search and content_format != "shorts":
            channel_distribution[channel_key] = channel_distribution.get(channel_key, 0) + 1

        text_lower = _lower(event.get("text_base"))
        if any(keyword in text_lower for keyword in HARMFUL_KEYWORDS):
            harmful_keyword_hits += 1

    topic_distribution: Dict[str, int] = {}
    sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
    toxic_hits = 0
    nlp_count = 0
    mock_used = False
    fallback_used = False

    for result in nlp_results or []:
        if not isinstance(result, dict):
            continue
        nlp_count += 1
        mock_used = mock_used or bool(result.get("mock_used"))
        fallback_used = fallback_used or bool(result.get("fallback_used"))
        storage = _lower(result.get("__storage"))
        fallback_used = fallback_used or "fallback" in storage

        categories = result.get("categories_json", [])
        if isinstance(categories, list):
            for category in categories:
                topic = _top_level_category(category)
                if topic:
                    topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
                name = _lower(category.get("name", "") if isinstance(category, dict) else category)
                if any(keyword in name for keyword in TOXIC_CATEGORY_KEYWORDS):
                    toxic_hits += 1

        sentiment = _as_float(result.get("sentiment_score"))
        if sentiment is None:
            continue
        if sentiment > SENTIMENT_THRESHOLDS["positive"]:
            sentiment_distribution["positive"] += 1
        elif sentiment < SENTIMENT_THRESHOLDS["negative"]:
            sentiment_distribution["negative"] += 1
        else:
            sentiment_distribution["neutral"] += 1

    storage_labels = {_lower(event.get("storage")) for event in normalized_events if event.get("storage")}
    fallback_used = fallback_used or any("fallback" in label for label in storage_labels)

    if not normalized_events:
        warnings.append("no normalized events available")
    if watch_count < MIN_DATA_REQUIREMENTS["watch_count"]:
        warnings.append("watch event sample is below minimum requirement")
    if search_count == 0:
        warnings.append("search events are missing or not included in the Takeout upload")
    if not channel_distribution:
        warnings.append("channel/source information is missing")
    if len(topic_distribution) < 2:
        warnings.append("topic distribution is too small for diversity scoring")
    if nlp_count == 0:
        warnings.append("nlp results are missing")
    if mock_used:
        warnings.append("mock data used")
    if fallback_used:
        warnings.append("fallback data used")
    if estimated_duration_count > 0:
        warnings.append("some watch durations are estimated")
    if excluded_ad_count > 0:
        warnings.append("ad events excluded from scoring")

    total_events = len(normalized_events)
    total_actions = max(total_events, 1)
    curation_count = sum(
        max(action_counts.get(kind, 0), source_type_counts.get(kind, 0))
        for kind in ["subscription", "playlist", "channel"]
    )
    participation_count = sum(
        max(action_counts.get(kind, 0), source_type_counts.get(kind, 0))
        for kind in ["comment", "live_chat"]
    )

    search_ratio = search_count / max(watch_count + search_count, 1)
    curation_ratio = min(1.0, curation_count / total_actions)
    participation_ratio = min(1.0, participation_count / total_actions)
    shorts_ratio = shorts_count / max(watch_count, 1)
    harmful_keyword_ratio = harmful_keyword_hits / max(total_events, 1)
    toxic_ratio = toxic_hits / max(nlp_count, 1) if nlp_count else None

    repeated_short_count = 0
    previous_short = False
    for event in normalized_events:
        is_watch = event["action_type"] == "view" or event["source_type"] == "watch_history"
        current_short = bool(is_watch and event.get("content_format") == "shorts")
        if current_short and previous_short:
            repeated_short_count += 1
        previous_short = current_short
    repeated_short_exposure_ratio = repeated_short_count / max(watch_count, 1)

    sample_confidence = min(1.0, total_events / MIN_DATA_REQUIREMENTS["event_count"])
    source_confidence = min(1.0, len(channel_distribution) / MIN_DATA_REQUIREMENTS["channel_count"])
    topic_confidence = min(1.0, len(topic_distribution) / MIN_DATA_REQUIREMENTS["topic_count"])
    duration_confidence = (
        sum(duration_confidences) / len(duration_confidences)
        if duration_confidences
        else CONFIDENCE_WEIGHTS["missing"]
    )
    data_confidence = (
        sample_confidence * 0.45
        + source_confidence * 0.20
        + topic_confidence * 0.20
        + duration_confidence * 0.15
    )
    # Mock/fallback penalties are applied per axis in scoring.py. At the
    # feature layer we keep only data-shape confidence plus explicit warnings.

    shorts_analysis = build_shorts_analysis(normalized_events)

    return {
        "watch_count": watch_count,
        "search_count": search_count,
        "comment_count": max(action_counts.get("comment", 0), source_type_counts.get("comment", 0)),
        "playlist_count": max(action_counts.get("playlist", 0), source_type_counts.get("playlist", 0)),
        "subscription_count": max(action_counts.get("subscription", 0), source_type_counts.get("subscription", 0)),
        "channel_count": max(action_counts.get("channel", 0), source_type_counts.get("channel", 0)),
        "live_chat_count": max(action_counts.get("live_chat", 0), source_type_counts.get("live_chat", 0)),
        "topic_distribution": topic_distribution,
        "channel_distribution": channel_distribution,
        "search_keyword_distribution": search_keyword_distribution,
        "shorts_count": shorts_count,
        "standard_video_count": standard_video_count,
        "live_count": live_count,
        "unknown_format_count": unknown_format_count,
        "shorts_analysis": shorts_analysis,
        "total_duration_sec": sum(durations) if durations else None,
        "duration_confidence": round(duration_confidence, 3),
        "data_confidence": round(max(0.0, min(1.0, data_confidence)), 3),
        "data_quality_warnings": _dedupe(warnings),
        "mock_used": mock_used,
        "fallback_used": fallback_used,
        "action_counts": action_counts,
        "source_type_counts": source_type_counts,
        "nlp_count": nlp_count,
        "sentiment_distribution": sentiment_distribution,
        "search_ratio": search_ratio,
        "direct_selection_ratio": None,
        "curation_ratio": curation_ratio,
        "participation_ratio": participation_ratio,
        "shorts_ratio": shorts_ratio,
        "toxic_ratio": toxic_ratio,
        "harmful_keyword_ratio": harmful_keyword_ratio,
        "repeated_short_exposure_ratio": repeated_short_exposure_ratio,
        "estimated_duration_count": estimated_duration_count,
        "excluded_ad_count": excluded_ad_count,
    }
