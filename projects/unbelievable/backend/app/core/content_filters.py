"""Shared content filters for analysis hygiene."""

from typing import Any, Dict, List, Optional, Tuple


AD_TEXT_MARKERS = [
    "from google ads",
    "from youtube ads",
    "google ads",
    "youtube ads",
    "video ads",
    "advertisement",
    "advertiser",
    "paid promotion",
    "sponsored",
    "google 광고",
    "youtube 광고",
    "유튜브 광고",
    "광고에서",
    "광고를 시청",
    "광고 동영상",
    "스폰서 광고",
    "광고주",
]

AD_URL_MARKERS = [
    "googleadservices",
    "doubleclick.net",
    "adservice.google",
    "googlesyndication",
    "ads.youtube.com",
    "/pagead/",
]


def _flatten_strings(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        result: List[str] = []
        for item in value.values():
            result.extend(_flatten_strings(item))
        return result
    if isinstance(value, (list, tuple, set)):
        result = []
        for item in value:
            result.extend(_flatten_strings(item))
        return result
    return [str(value)]


def _is_true_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return False


def detect_ad_event_reason(record: Dict[str, Any]) -> Optional[str]:
    if not isinstance(record, dict):
        return None

    if _is_true_flag(record.get("is_ad_event")) or _is_true_flag(record.get("is_ad")):
        return str(record.get("ad_filter_reason") or "explicit_ad_flag")

    flattened = " ".join(_flatten_strings(record)).lower()
    for marker in AD_URL_MARKERS:
        if marker in flattened:
            return f"url_marker:{marker}"

    for marker in AD_TEXT_MARKERS:
        if marker in flattened:
            return f"text_marker:{marker}"

    return None


def split_analysis_events(events: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    analysis_events: List[Dict[str, Any]] = []
    ad_events: List[Dict[str, Any]] = []

    for event in events or []:
        reason = detect_ad_event_reason(event)
        if reason:
            event["is_ad_event"] = True
            event["ad_filter_reason"] = reason
            ad_events.append(event)
            continue
        analysis_events.append(event)

    return analysis_events, ad_events


def filter_analysis_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    analysis_events, _ = split_analysis_events(events)
    return analysis_events

