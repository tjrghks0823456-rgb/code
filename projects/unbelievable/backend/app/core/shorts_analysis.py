import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


SHORTS_LOOP_GAP_SEC = 180
MEANINGFUL_LOOP_MIN_COUNT = 5
HIGH_LOOP_MIN_COUNT = 10

TIME_BUCKETS = {
    "dawn": range(0, 6),
    "morning": range(6, 12),
    "afternoon": range(12, 18),
    "night": range(18, 24),
}

TOKEN_RE = re.compile(r"[\uac00-\ud7a3A-Za-z0-9][\uac00-\ud7a3A-Za-z0-9._-]{1,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "video",
    "shorts",
    "youtube",
    "watched",
    "official",
    "episode",
    "shortened",
    "cid",
}


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _lower(value: Any) -> str:
    return _clean(value).lower()


def _content_format(event: Dict[str, Any]) -> str:
    explicit = _lower(event.get("content_format"))
    if explicit and explicit != "unknown":
        return explicit

    url = _lower(event.get("title_url") or event.get("titleUrl") or event.get("url") or event.get("URL"))
    if "/shorts/" in url or "youtube.com/shorts" in url:
        return "shorts"
    if "/live/" in url or "youtube.com/live" in url:
        return "live"
    if "watch?v=" in url or event.get("video_id"):
        return "standard_video"
    return "unknown"


def _is_watch_event(event: Dict[str, Any]) -> bool:
    action_type = _lower(event.get("action_type"))
    source_type = _lower(event.get("source_type"))
    return action_type == "view" or source_type == "watch_history"


def _is_active_search_event(event: Dict[str, Any]) -> bool:
    action_type = _lower(event.get("action_type"))
    source_type = _lower(event.get("source_type"))
    intent_level = _lower(event.get("intent_level"))
    return action_type == "search" or source_type == "search_history" or intent_level == "active_search"


def _parse_event_time(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    raw = _clean(value)
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        if " " in normalized and "T" not in normalized:
            normalized = normalized.replace(" ", "T")
        parsed = datetime.fromisoformat(normalized)
        return parsed.replace(tzinfo=None)
    except Exception:
        return None


def _title_text(event: Dict[str, Any]) -> str:
    return _clean(event.get("text_base") or event.get("title_text") or event.get("title"))


def _extract_keywords(shorts_events: List[Dict[str, Any]]) -> Counter:
    counter: Counter = Counter()
    for event in shorts_events:
        title = _title_text(event)
        for match in TOKEN_RE.findall(title):
            token = match.strip("._-").lower()
            if len(token) < 2 or token in STOPWORDS or token.isdigit():
                continue
            counter[token] += 1
    return counter


def _time_bucket(hour: int) -> str:
    for name, hours in TIME_BUCKETS.items():
        if hour in hours:
            return name
    return "unknown"


def _build_loops(timed_shorts: List[Tuple[datetime, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not timed_shorts:
        return []

    timed_shorts = sorted(timed_shorts, key=lambda item: item[0])
    groups: List[List[Tuple[datetime, Dict[str, Any]]]] = []
    current = [timed_shorts[0]]

    for item in timed_shorts[1:]:
        previous_time = current[-1][0]
        gap_sec = (item[0] - previous_time).total_seconds()
        if gap_sec <= SHORTS_LOOP_GAP_SEC:
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    groups.append(current)

    loops: List[Dict[str, Any]] = []
    for group in groups:
        started_at = group[0][0]
        ended_at = group[-1][0]
        duration_min = max(0.0, (ended_at - started_at).total_seconds() / 60.0)
        loops.append(
            {
                "count": len(group),
                "duration_min": round(duration_min, 1),
                "started_at": started_at.isoformat(sep=" "),
                "ended_at": ended_at.isoformat(sep=" "),
            }
        )
    return loops


def _level_from_score(score: float) -> str:
    if score <= 30:
        return "low"
    if score <= 65:
        return "medium"
    return "high"


def build_shorts_analysis(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    watch_events = [event for event in events if _is_watch_event(event)]
    active_search_count = sum(1 for event in events if _is_active_search_event(event))
    shorts_events = [
        event
        for event in events
        if _content_format(event) == "shorts" and (_is_watch_event(event) or event.get("content_format") == "shorts")
    ]
    shorts_count = len(shorts_events)
    shorts_ratio = shorts_count / max(len(watch_events), 1)

    warnings = [
        "숏츠 분석은 Google Takeout의 event_time, title, URL 메타데이터를 기반으로 추정합니다.",
        "홈피드/추천/구독탭 같은 유입 경로는 Takeout만으로 확정하지 않습니다.",
        "passive_feed_score는 휴리스틱 추정치이며 숏츠 유입 경로 확정값이 아닙니다.",
    ]
    shorts_detection_status = "detected" if shorts_count > 0 else "not_detected"
    shorts_detection_note = "이번 업로드에서 /shorts/ URL로 식별된 숏츠 이벤트가 확인되었습니다."
    if shorts_count == 0:
        shorts_detection_note = (
            "이번 업로드에서 /shorts/ URL로 식별된 숏츠 이벤트가 0건입니다. "
            "실제로 숏츠를 보지 않았다는 뜻은 아니며, Takeout이 숏츠를 일반 watch URL로 저장했거나 "
            "이전 분석 run_id를 보고 있을 수 있습니다."
        )
        warnings.append(shorts_detection_note)
    elif shorts_count < MEANINGFUL_LOOP_MIN_COUNT:
        shorts_detection_status = "limited"
        shorts_detection_note = "숏츠 이벤트 수가 적어 반복 루프/시간대 집중도는 참고용입니다."
        warnings.append(shorts_detection_note)

    keyword_counter = _extract_keywords(shorts_events)
    repeated_keyword_count = sum(1 for count in keyword_counter.values() if count >= 3)
    repeated_topic_score = min(100.0, repeated_keyword_count * 12.0)

    timed_shorts: List[Tuple[datetime, Dict[str, Any]]] = []
    missing_time_count = 0
    for event in shorts_events:
        parsed_time = _parse_event_time(event.get("event_time") or event.get("time"))
        if parsed_time:
            timed_shorts.append((parsed_time, event))
        else:
            missing_time_count += 1

    if missing_time_count:
        warnings.append(f"{missing_time_count} shorts events had no valid event_time and were excluded from loop/time-bucket analysis.")

    loops = _build_loops(timed_shorts)
    loop_count = len(loops)
    meaningful_loops = [loop for loop in loops if loop["count"] >= MEANINGFUL_LOOP_MIN_COUNT]
    high_loops = [loop for loop in loops if loop["count"] >= HIGH_LOOP_MIN_COUNT]
    max_loop_length = max((loop["count"] for loop in loops), default=0)
    avg_loop_length = round(sum(loop["count"] for loop in loops) / loop_count, 1) if loop_count else 0.0
    max_loop_duration_min = max((loop["duration_min"] for loop in loops), default=0.0)
    avg_loop_duration_min = round(sum(loop["duration_min"] for loop in loops) / loop_count, 1) if loop_count else 0.0

    base = min(100.0, len(meaningful_loops) * 15.0)
    length_bonus = min(30.0, max_loop_length * 2.0)
    duration_bonus = min(20.0, max_loop_duration_min * 1.5)
    dopamine_loop_score = min(100.0, base + length_bonus + duration_bonus)

    shorts_by_time_bucket = {bucket: 0 for bucket in TIME_BUCKETS}
    for event_time, _event in timed_shorts:
        bucket = _time_bucket(event_time.hour)
        if bucket in shorts_by_time_bucket:
            shorts_by_time_bucket[bucket] += 1

    timed_count = len(timed_shorts)
    if timed_count:
        peak_shorts_time_bucket = max(shorts_by_time_bucket, key=shorts_by_time_bucket.get)
        peak_ratio = (shorts_by_time_bucket[peak_shorts_time_bucket] / timed_count) * 100.0
        late_night_shorts_ratio = ((shorts_by_time_bucket["dawn"] + shorts_by_time_bucket["night"]) / timed_count) * 100.0
        time_concentration_score = min(
            100.0,
            (peak_ratio * 1.2) + (10.0 if late_night_shorts_ratio >= 60.0 else 0.0),
        )
    else:
        peak_shorts_time_bucket = "unknown"
        late_night_shorts_ratio = 0.0
        time_concentration_score = 0.0
        if shorts_count:
            warnings.append("No valid event_time values were available for shorts time-bucket analysis.")

    active_search_ratio = active_search_count / max(shorts_count + active_search_count, 1)
    passive_feed_score = 0.0
    if shorts_count:
        passive_feed_score = min(
            100.0,
            shorts_ratio * 35.0
            + dopamine_loop_score * 0.35
            + repeated_topic_score * 0.15
            + time_concentration_score * 0.10
            + (1.0 - min(1.0, active_search_ratio)) * 15.0,
        )

    shorts_stimulation_risk = 0.0
    if shorts_count:
        shorts_stimulation_risk = min(
            100.0,
            dopamine_loop_score * 0.35
            + repeated_topic_score * 0.25
            + time_concentration_score * 0.20
            + passive_feed_score * 0.20,
        )

    return {
        "shorts_count": shorts_count,
        "total_shorts_count": shorts_count,
        "shorts_detection_status": shorts_detection_status,
        "shorts_detection_note": shorts_detection_note,
        "shorts_ratio": round(shorts_ratio, 3),
        "shorts_ratio_percent": round(shorts_ratio * 100.0, 1),
        "shorts_stimulation_risk": round(shorts_stimulation_risk, 1),
        "dopamine_loop_score": round(dopamine_loop_score, 1),
        "loop_count": loop_count,
        "meaningful_loop_count": len(meaningful_loops),
        "high_loop_count": len(high_loops),
        "max_loop_length": max_loop_length,
        "avg_loop_length": avg_loop_length,
        "max_loop_duration_min": round(max_loop_duration_min, 1),
        "avg_loop_duration_min": avg_loop_duration_min,
        "repeated_keyword_count": repeated_keyword_count,
        "repeated_topic_score": round(repeated_topic_score, 1),
        "scroll_repetition_level": _level_from_score(repeated_topic_score),
        "active_search_count": active_search_count,
        "active_search_ratio": round(active_search_ratio, 3),
        "passive_feed_score": round(passive_feed_score, 1),
        "passive_feed_level": _level_from_score(passive_feed_score),
        "top_shorts_keywords": [
            {"keyword": keyword, "count": count}
            for keyword, count in keyword_counter.most_common(8)
        ],
        "shorts_by_time_bucket": shorts_by_time_bucket,
        "peak_shorts_time_bucket": peak_shorts_time_bucket,
        "late_night_shorts_ratio": round(late_night_shorts_ratio, 1),
        "time_concentration_score": round(time_concentration_score, 1),
        "warnings": warnings,
    }


def build_overall_risk(information_bias_risk: float, shorts_analysis: Dict[str, Any]) -> Dict[str, float]:
    shorts_count = int(shorts_analysis.get("shorts_count") or 0)
    shorts_risk = float(shorts_analysis.get("shorts_stimulation_risk") or 0.0)
    info_risk = float(information_bias_risk or 0.0)

    if shorts_count <= 0:
        shorts_weight = 0.0
    elif shorts_count < 20:
        shorts_weight = 0.10
    else:
        shorts_weight = 0.30

    final_detox_risk = (info_risk * (1.0 - shorts_weight)) + (shorts_risk * shorts_weight)
    return {
        "information_bias_risk": round(info_risk, 1),
        "shorts_stimulation_risk": round(shorts_risk, 1),
        "shorts_weight": round(shorts_weight, 2),
        "final_detox_risk": round(min(100.0, max(0.0, final_detox_risk)), 1),
    }
