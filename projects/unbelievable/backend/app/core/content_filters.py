"""Shared content filters for analysis hygiene."""

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


AD_DETAIL_MARKERS = [
    "from google ads",
    "from youtube ads",
    "google ads",
    "youtube ads",
    "video ads",
    "ad served by",
    "advertisement",
    "advertiser",
    "\uad11\uace0",
    "\uad6c\uae00 \uad11\uace0",
]

AD_URL_MARKERS = [
    "googleadservices",
    "doubleclick.net",
    "adservice.google",
    "googlesyndication",
    "ads.youtube.com",
    "pagead/",
    "/aclk",
    "adclick",
    "adurl=",
    "utm_",
    "utm-source",
    "utm source",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "gclid=",
    "gbraid=",
    "wbraid=",
    "cid=",
]

AD_TEXT_MARKERS = [
    "paid promotion",
    "sponsored",
    "promoted",
    "promotion",
    "promo",
    "shortened:",
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
    "campaign",
    "get started on google cloud",
    "try cursor today",
    "cursor agent",
    "google cloud_kr",
    "hotels.com (kr)",
    "lge.com",
    "the android show",
    "sony audio",
    "yebisu beer",
    "coca-cola",
    "coca cola",
    "google play",
    "turn off the light",
    "high miles",
    "lab series video",
    "cjh x lab series",
    "\uad11\uace0",
    "\uc2a4\ud3f0\uc11c",
    "\ud504\ub85c\ubaa8\uc158",
    "\ud0c0\uc784\ub51c",
    "\ud56b\ub51c",
    "\uacf5\uc2dd\ubab0",
    "\uc778\uae30 \uc0c1\ud488",
    "\uc778\uae30\uc0c1\ud488",
    "\uae30\ud68d\uc804",
    "\ud560\uc778",
    "\ucfe0\ud3f0",
    "\ubb34\ub8cc\ubc30\uc1a1",
    "\uad6c\ub9e4\ud558\uae30",
    "\uc62c\uc778\ud574\ubd04",
    "\ub2e5\ud130\ud328\uce58",
    "\ub2e5\ud130 \ud328\uce58",
    "\ub2e5\ud130\ube7c",
    "\uceec\ub7ec\uadf8\ub7a8",
    "\ud2f4\ud2b8 \ucd94\ucc9c",
    "\uccab\uad6c\ub9e4",
    "\uc2a4\ud0dc\ud2f1",
    "\uc2a4\ub9c8\uc77c\ubcf4\uc774",
    "\ucf5c\uc624\ube0c\ubdf0\ud2f0",
    "\ucf5c\uc624\ube0c\ub4c0\ud2f0",
    "\uc138\uc77c",
    "\ub9e5\uc2a4\ucef7",
    "\ucd94\uc131\ud6c8",
    "\ud56b\ud55c \uc571",
    "\ubc00\ub808 2026",
    "\ud30c\uc774\ub85c\uc6b8\ud2b8\ub77c",
    "\uc62c\ub274 \uc9c4\ub85c",
    "\ub2e4\ube44\ub108\uc2a4",
    "\uc544\ub514\ub2e4\uc2a4",
    "\uc694\uace0\uc778\ud130\ub137",
    "\uc544\ud0a4\ud074\ub798\uc2dd",
    "\ud2f0\uc2a4\ud14c\uc774\uc158",
    "\ud0c0\uc774\uc5b4\uc11c\ube44\uc2a4",
    "\uc219\ucde8\ud574\uc18c\uc81c",
    "\uae68\ub178\ub2c8",
    "\ub300\ud559\uc0dd\ud3b8",
    "\ub77c\ub85c\uc288\ud3ec\uc81c",
    "\uc5d0\ube60\ub04c\ub77c",
    "\ud2b8\ub7ec\ube14*\uc5d0\uc13c\uc2a4",
    "\ud56b\uce58\uc988\ubc24",
    "\ucd9c\uc2dc",
]

LOW_VALUE_SEARCH_EXACT = {
    "",
    "unknown video",
    "\uc54c \uc218 \uc5c6\ub294 \ube44\ub514\uc624",
    "\uc5ec\uae30",
}

PROMO_QUERY_PATTERNS = [
    re.compile(r"\b\d{5,6}\b.*(horizontal|vertical|square|banner|creative|asset|campaign)", re.IGNORECASE),
    re.compile("\\b\\d{5,6}\\b.*(\uac00\ub85c\ud615|\uc138\ub85c\ud615|\ud0c0\uc774\ud3ec\ud615|\ubc30\ub108|\uc18c\uc7ac|\ucea0\ud398\uc778)"),
    re.compile(r"(?<![A-Za-z0-9])(6s|15s|30s|60s)(?![A-Za-z0-9])", re.IGNORECASE),
    re.compile(r"\bver\.?\s*\d+\b", re.IGNORECASE),
    re.compile(r"\b\d{3,4}x\d{3,4}\b", re.IGNORECASE),
    re.compile(r"_kr(_|$)", re.IGNORECASE),
    re.compile(r"^\[[^\]]+\]"),
    re.compile("[_][A-Za-z0-9\uac00-\ud7a3-]+[_]", re.IGNORECASE),
    re.compile(r"\btry .+ today\b", re.IGNORECASE),
    re.compile(r"#\S+"),
    re.compile("(?<!\\d)(6|15|30|60)\\s*[\\\"\u201d\u2033\ucd08](?!\\d)"),
    re.compile("\ucd94\ucc9c!"),
    re.compile("\uac00 \ucd94\ucc9c\ud558\ub294"),
    re.compile("\\b[A-Za-z0-9\uac00-\ud7a3]+ x [A-Za-z0-9\uac00-\ud7a3]+.*video\\b", re.IGNORECASE),
    re.compile(r"\.(mp4|mov|avi|webm)\b", re.IGNORECASE),
    re.compile(r"\[[^\]]+\].*#"),
    re.compile(r"\bwh-\d{3,}[a-z0-9-]*\b", re.IGNORECASE),
]

SEARCH_PREFIXES = [
    "searched for ",
    "search: ",
    "query: ",
    "\uac80\uc0c9\uc5b4: ",
    "\uac80\uc0c9: ",
]


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _lower(value: Any) -> str:
    return _clean_text(value).lower()


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


def clean_search_query(value: Any) -> str:
    query = _clean_text(value)
    for prefix in SEARCH_PREFIXES:
        if query.lower().startswith(prefix):
            query = query[len(prefix):].strip()
            break
    query = re.sub(r"\s+", " ", query)
    return query.strip(" \t\r\n\"'")


def is_promotional_search_text(value: Any) -> Optional[str]:
    query = clean_search_query(value)
    query_lower = query.lower()

    if query_lower in LOW_VALUE_SEARCH_EXACT:
        return "low_value_search"
    if len(query) < 2:
        return "short_search_noise"
    if query_lower.startswith(("http://", "https://")):
        return "url_only_search"
    if re.match(r"^[a-z][a-z0-9+.-]*://", query_lower):
        return "url_only_search"
    if re.match("^[\u3131-\u318e\\s]+$", query):
        return "jamo_noise"

    for marker in AD_TEXT_MARKERS:
        if marker in query_lower:
            return f"text_marker:{marker}"

    for pattern in PROMO_QUERY_PATTERNS:
        if pattern.search(query):
            return f"promo_pattern:{pattern.pattern}"

    return None


def detect_ad_event_reason(record: Dict[str, Any]) -> Optional[str]:
    if not isinstance(record, dict):
        return None

    if _is_true_flag(record.get("is_ad_event")) or _is_true_flag(record.get("is_ad")):
        return str(record.get("ad_filter_reason") or "explicit_ad_flag")

    details = record.get("details") or record.get("detail") or []
    detail_text = " ".join(_flatten_strings(details)).lower()
    for marker in AD_DETAIL_MARKERS:
        if marker in detail_text:
            return f"detail_marker:{marker}"

    url_text = " ".join(
        _flatten_strings({
            "title_url": record.get("title_url"),
            "titleUrl": record.get("titleUrl"),
            "url": record.get("url"),
            "URL": record.get("URL"),
            "channel_url": record.get("channel_url"),
            "channelUrl": record.get("channelUrl"),
        })
    ).lower()
    for marker in AD_URL_MARKERS:
        if marker in url_text:
            return f"url_marker:{marker}"

    flattened = " ".join(_flatten_strings(record)).lower()
    for marker in AD_URL_MARKERS:
        if marker in flattened:
            return f"url_marker:{marker}"
    for marker in AD_DETAIL_MARKERS:
        if marker in flattened:
            return f"detail_marker:{marker}"
    for marker in AD_TEXT_MARKERS:
        if marker in flattened:
            return f"text_marker:{marker}"

    action_type = _lower(record.get("action_type"))
    source_type = _lower(record.get("source_type"))
    if action_type == "search" or source_type == "search_history":
        return is_promotional_search_text(record.get("text_base") or record.get("title_text") or record.get("title"))

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


def is_valid_search_event(event: Dict[str, Any]) -> bool:
    if not isinstance(event, dict):
        return False

    if detect_ad_event_reason(event):
        return False

    action_type = _lower(event.get("action_type"))
    source_type = _lower(event.get("source_type"))
    intent_level = _lower(event.get("intent_level"))
    content_format = _lower(event.get("content_format"))

    if content_format == "shorts" or action_type == "view" or source_type == "watch_history":
        return False

    is_search = action_type == "search" or source_type == "search_history" or intent_level == "active_search"
    if not is_search:
        return False

    query = clean_search_query(event.get("text_base") or event.get("title_text") or event.get("title"))
    if not query:
        return False

    return is_promotional_search_text(query) is None


def is_standard_video_event(event: Dict[str, Any]) -> bool:
    return (
        _lower(event.get("action_type")) == "view"
        and _lower(event.get("source_type")) == "watch_history"
        and _lower(event.get("content_format")) == "standard_video"
        and not detect_ad_event_reason(event)
    )


def is_shorts_video_event(event: Dict[str, Any]) -> bool:
    return (
        _lower(event.get("action_type")) == "view"
        and _lower(event.get("source_type")) == "watch_history"
        and _lower(event.get("content_format")) == "shorts"
        and not detect_ad_event_reason(event)
    )


def build_ad_skip_summary(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    reason_counts = Counter()
    samples: Dict[str, str] = {}

    for event in events or []:
        reason = event.get("ad_filter_reason") or detect_ad_event_reason(event) or "ad_event"
        reason_counts[reason] += 1
        samples.setdefault(reason, _clean_text(event.get("text_base") or event.get("title_text") or event.get("title"))[:120])

    return [
        {
            "source": "google_ads",
            "reason": reason,
            "sample_title": samples.get(reason, ""),
            "count": count,
        }
        for reason, count in reason_counts.most_common()
    ]
