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
    "googleads",
    "doubleclick.net",
    "adservice.google",
    "googlesyndication",
    "ads.youtube.com",
    "pagead/",
    "/aclk",
    "adclick",
    "adurl=",
    "utm_campaign",
    "utm_medium=cpc",
    "utm_medium=paid",
    "gclid=",
    "dclid=",
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
    "\uccab\uad6c\ub9e4",
    "\uc138\uc77c",
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
    "you searched for ",
    "search: ",
    "query: ",
    "\uac80\uc0c9\uc5b4: ",
    "\uac80\uc0c9: ",
]

SEARCH_FIELD_NAMES = [
    "query",
    "searchQuery",
    "searchTerm",
    "searchedText",
    "keyword",
]

SEARCH_TEXT_PATTERNS = [
    re.compile(r"^\s*searched for\s+(.+?)\s*$", re.IGNORECASE | re.DOTALL),
    re.compile(r"^\s*you searched for\s+(.+?)\s*$", re.IGNORECASE | re.DOTALL),
    re.compile(r"(?:검색어|검색)\s*[:：]\s*(.+?)(?:\n|$)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^\s*(?:검색함|검색)\s+(.+?)\s*$", re.IGNORECASE | re.DOTALL),
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
    query = re.sub(r"https?://\S+", " ", query)
    query = re.sub(r"\b(?:gclid|dclid|gbraid|wbraid|utm_[a-z_]+|cid)=[^\s&]+", " ", query, flags=re.IGNORECASE)
    query = re.sub(r"\s+", " ", query)
    return query.strip(" \t\r\n\"'")


def _first_string_field(record: Dict[str, Any], names: List[str]) -> str:
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _search_candidate_from_text(value: Any) -> Optional[str]:
    text = _clean_text(value)
    if not text:
        return None

    first_line = text.splitlines()[0].strip() if "\n" in text else text
    for pattern in SEARCH_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).splitlines()[0].strip()

    lower_first = first_line.lower()
    for prefix in SEARCH_PREFIXES:
        if lower_first.startswith(prefix):
            return first_line[len(prefix):].strip()

    return None


def _looks_like_search_context(record: Dict[str, Any]) -> bool:
    return (
        _lower(record.get("action_type")) == "search"
        or _lower(record.get("source_type")) == "search_history"
        or _lower(record.get("intent_level")) == "active_search"
    )


def _looks_like_watch_context(record: Dict[str, Any]) -> bool:
    raw_title = _lower(record.get("title") or record.get("title_text") or record.get("text_base"))
    return (
        raw_title.startswith("watched ")
        or _lower(record.get("action_type")) == "view"
        or _lower(record.get("source_type")) == "watch_history"
    )


def _has_video_link_evidence(record: Dict[str, Any]) -> bool:
    url_text = " ".join(
        _flatten_strings({
            "title_url": record.get("title_url"),
            "titleUrl": record.get("titleUrl"),
            "url": record.get("url"),
            "URL": record.get("URL"),
        })
    ).lower()
    return bool(record.get("video_id")) or "watch?v=" in url_text or "/shorts/" in url_text


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


def _valid_search_query(candidate: Any) -> Optional[str]:
    query = clean_search_query(candidate)
    query_lower = query.lower()

    if not query:
        return None
    if len(query) < 2:
        return None
    if len(query) > 120:
        return None
    if query_lower.startswith(("watched ", "visited ")):
        return None
    if re.fullmatch(r"(?:https?://|www\.)\S+", query_lower):
        return None
    if re.search(r"\.(?:html?|json|csv|txt|mp4|mov|avi|webm)$", query_lower):
        return None
    if is_promotional_search_text(query):
        return None
    return query


def extract_search_query(item: Dict[str, Any], raw_text: str = "") -> Optional[str]:
    """Return a clear user-entered YouTube search query, or None if ambiguous."""
    if not isinstance(item, dict):
        return None

    record = dict(item)
    if raw_text:
        record["raw_text"] = raw_text

    if detect_ad_event_reason(record):
        return None
    if _looks_like_watch_context(record) and not _looks_like_search_context(record):
        return None

    for field_name in SEARCH_FIELD_NAMES:
        query = _valid_search_query(record.get(field_name))
        if query:
            return query

    for source in [
        record.get("title"),
        raw_text,
        record.get("raw_takeout_text"),
        record.get("text_base"),
        record.get("title_text"),
    ]:
        candidate = _search_candidate_from_text(source)
        query = _valid_search_query(candidate)
        if query:
            return query

    if _looks_like_search_context(record) and not _looks_like_watch_context(record):
        if _has_video_link_evidence(record):
            return None
        normalized_candidate = _first_string_field(record, ["search_query", "text_base", "title_text", "title"])
        return _valid_search_query(normalized_candidate)

    return None


def is_google_ad_event(raw_item: Dict[str, Any], file_path: str = "", raw_text: str = "") -> Tuple[bool, str]:
    record = dict(raw_item or {})
    if file_path:
        record["file_path"] = file_path
    if raw_text:
        record["raw_text"] = raw_text
    reason = detect_ad_event_reason(record)
    return bool(reason), reason or ""


def detect_content_format(url: str = "", title: str = "", raw_item: Optional[Dict[str, Any]] = None) -> str:
    item = raw_item or {}
    url_text = " ".join(
        _flatten_strings({
            "url": url,
            "title_url": item.get("title_url"),
            "titleUrl": item.get("titleUrl"),
            "URL": item.get("URL"),
        })
    ).lower()
    title_text = " ".join(
        _flatten_strings({
            "title": title,
            "title_text": item.get("title_text"),
            "text_base": item.get("text_base"),
        })
    ).lower()
    detail_text = " ".join(_flatten_strings(item.get("details") or item.get("detail") or [])).lower()

    if "/shorts/" in url_text or "youtube.com/shorts" in url_text:
        return "shorts"
    if (
        "/live/" in url_text
        or "youtube.com/live" in url_text
        or "실시간 스트리밍" in title_text
        or "live stream" in title_text
        or "live" in detail_text
        or _is_true_flag(item.get("isLive"))
        or _is_true_flag(item.get("is_live"))
    ):
        return "live"
    if "youtube.com/watch" in url_text or "watch?v=" in url_text:
        return "standard_video"
    if _lower(item.get("action_type")) == "view" and item.get("video_id"):
        return "standard_video"
    return "unknown"


def detect_ad_event_reason(record: Dict[str, Any]) -> Optional[str]:
    if not isinstance(record, dict):
        return None

    if _is_true_flag(record.get("is_ad_event")) or _is_true_flag(record.get("is_ad")):
        return str(record.get("ad_filter_reason") or "explicit_ad_flag")

    details = {
        "details": record.get("details"),
        "detail": record.get("detail"),
        "source": record.get("source"),
        "activityControls": record.get("activityControls"),
        "activity_controls": record.get("activity_controls"),
    }
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

    return extract_search_query(event) is not None


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
