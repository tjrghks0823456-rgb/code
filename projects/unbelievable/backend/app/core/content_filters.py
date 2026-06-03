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
    "promoted",
    "shortened:",
    "cid=",
    "gclid",
    "gbraid",
    "wbraid",
    "utm_",
    "utm-source",
    "utm source",
    "adurl",
    "aclk",
    "clickserve",
    "tracking",
    "redirect",
    "official store",
    "official mall",
    "time deal",
    "hot deal",
    "special offer",
    "limited offer",
    "popular products",
    "shop now",
    "buy now",
    "sale",
    "promo",
    "광고",
    "스폰서",
    "프로모션",
    "타임딜",
    "핫딜",
    "특가",
    "공식몰",
    "인기 제품",
    "인기상품",
    "기획전",
    "할인",
    "쿠폰",
    "무료배송",
    "구매하기",
    "쇼핑",
    "쇼핑몰",
    "lge.com",
    "닥터패치",
    "the android show",
]

AD_URL_MARKERS = [
    "googleadservices",
    "doubleclick.net",
    "adservice.google",
    "googlesyndication",
    "ads.youtube.com",
    "/pagead/",
    "/aclk",
    "adclick",
    "adurl=",
    "utm_",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "gclid=",
    "gbraid=",
    "wbraid=",
    "cid=",
]

LOW_VALUE_SEARCH_MARKERS = [
    "알 수 없는 비디오",
    "unknown video",
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

    for marker in LOW_VALUE_SEARCH_MARKERS:
        if marker in flattened:
            return f"noise_marker:{marker}"

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

