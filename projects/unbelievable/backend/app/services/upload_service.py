import uuid
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.core.content_filters import (
    build_ad_skip_summary,
    detect_ad_event_reason,
    split_analysis_events,
)
from app.core.youtube import parse_iso8601_duration, youtube_client
from app.core.shorts_analysis import build_shorts_analysis
from app.core.upload_config import DURATION_LIMITS, PARSER_LIMITS
from app.core.config import settings
from app.core.takeout_parser import parse_single_item

from app.parsers.takeout_parser import (
    TakeoutParser,
    scan_youtube_files_from_zip,
    classify_takeout_file,
    is_supported_takeout_file,
    classify_content_format,
)
from app.repositories.upload_repository import UploadRepository

logger = logging.getLogger(__name__)


def build_sessions_from_events(events: List[Dict[str, Any]], gap_minutes: int = 30) -> List[List[Dict[str, Any]]]:
    relevant_events = [
        e for e in events
        if e.get("action_type") in ["search", "view"]
    ]
    try:
        relevant_events_sorted = sorted(relevant_events, key=lambda x: x.get("event_time") or "")
    except Exception:
        relevant_events_sorted = relevant_events

    sessions = []
    current_session = []

    for e in relevant_events_sorted:
        if not e.get("event_time"):
            continue
        if not current_session:
            current_session.append(e)
            continue

        try:
            t1 = datetime.strptime(current_session[-1]["event_time"], "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(e["event_time"], "%Y-%m-%d %H:%M:%S")
            gap_sec = abs((t2 - t1).total_seconds())
        except Exception:
            gap_sec = 0.0

        if gap_sec > gap_minutes * 60:
            sessions.append(current_session)
            current_session = [e]
        else:
            current_session.append(e)

    if current_session:
        sessions.append(current_session)

    return sessions


def infer_source_type(item: Dict[str, Any]) -> str:
    source_type = (item.get("source_type") or "").lower()
    if source_type:
        return source_type
    action_type = (item.get("action_type") or "").lower()
    if action_type == "search":
        return "search_history"
    if action_type == "view":
        return "watch_history"
    return "unknown"


def count_duration_sources(events: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for event in events:
        source = event.get("duration_source") or event.get("duration_confidence") or "unknown"
        counts[source] = counts.get(source, 0) + 1
    return counts


def count_source_types(events: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {
        "watch_history": 0,
        "search_history": 0,
        "subscription": 0,
        "playlist": 0,
        "comment": 0,
        "live_chat": 0,
        "channel": 0
    }
    for event in events:
        source_type = event.get("source_type")
        if source_type:
            counts[source_type] = counts.get(source_type, 0) + 1
    return counts


def count_content_formats(events: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {
        "shorts": 0,
        "standard_video": 0,
        "live": 0,
        "unknown": 0
    }
    for event in events:
        action_type = (event.get("action_type") or "").lower()
        source_type = (event.get("source_type") or "").lower()
        if action_type != "view" and source_type != "watch_history":
            continue
        content_format = event.get("content_format") or classify_content_format(event)
        counts[content_format] = counts.get(content_format, 0) + 1
    return counts


def apply_youtube_duration_metadata(events: List[Dict[str, Any]], mock_estimation_enabled: bool = False) -> Dict[str, int]:
    seen = set()
    video_ids = []
    for event in events:
        if event.get("action_type") != "view":
            continue
        video_id = event.get("video_id")
        if not video_id or video_id in seen:
            continue
        seen.add(video_id)
        video_ids.append(video_id)

    metadata_limit = DURATION_LIMITS["metadata_video_limit"]
    metadata_by_id = youtube_client.get_videos_metadata_batch(video_ids[:metadata_limit])

    for event in events:
        event["mock_estimation_used"] = mock_estimation_enabled
        video_id = event.get("video_id")
        metadata = metadata_by_id.get(video_id)
        if not metadata:
            if video_id and len(video_ids) > metadata_limit:
                event["duration_metadata_status"] = "metadata_limit_exceeded"
            continue

        event["youtube_metadata_api_success"] = bool(metadata.get("api_success"))
        event["youtube_metadata_mock_used"] = bool(metadata.get("mock_used"))
        event["youtube_metadata_fallback_used"] = bool(metadata.get("fallback_used"))

        duration_sec = metadata.get("duration_sec")
        if metadata.get("api_success") and duration_sec:
            event["metadata_duration_sec"] = duration_sec
            event["video_duration_sec"] = duration_sec
            if mock_estimation_enabled:
                event["estimated_duration_sec"] = duration_sec
                event["duration_confidence"] = "api"
                event["duration_source"] = "youtube_api"
            else:
                event["estimated_duration_sec"] = None
                event["duration_confidence"] = "unknown"
                event["duration_source"] = "none"
        elif duration_sec:
            event["video_duration_sec"] = duration_sec
            event["mock_metadata_duration_sec"] = duration_sec

    return count_duration_sources(events)


def apply_timeline_duration_estimates(timed_events: List[tuple], mock_estimation_enabled: bool = False) -> None:
    if not mock_estimation_enabled:
        for _, event in timed_events:
            event["timeline_gap_sec"] = None
            event["estimated_duration_sec"] = None
            event["duration_confidence"] = "unknown"
            event["duration_source"] = "none"
            event["duration_estimation_method"] = "unknown"
            if "raw_item" in event and isinstance(event["raw_item"], dict):
                event["raw_item"]["duration_estimation_method"] = "unknown"
        return

    max_gap_sec = DURATION_LIMITS["max_timeline_gap_sec"]
    default_sec = DURATION_LIMITS["standard_default_sec"]

    timed_events.sort(key=lambda pair: pair[0])
    
    # Initialize all events with unknown method
    for _, event in timed_events:
        event["duration_estimation_method"] = "unknown"
        if "raw_item" in event and isinstance(event["raw_item"], dict):
            event["raw_item"]["duration_estimation_method"] = "unknown"

    for idx, (event_time, event) in enumerate(timed_events):
        if event["action_type"] != "view":
            continue

        metadata_duration = event.get("metadata_duration_sec")
        
        # Calculate gap with next event
        gap_sec = None
        if idx < len(timed_events) - 1:
            next_event_time = timed_events[idx + 1][0]
            gap_sec = int((next_event_time - event_time).total_seconds())

        if gap_sec is not None and (gap_sec <= 0 or gap_sec > max_gap_sec):
            gap_sec = None

        if metadata_duration:
            method = "metadata"
            event["duration_estimation_method"] = method
            if "raw_item" in event and isinstance(event["raw_item"], dict):
                event["raw_item"]["duration_estimation_method"] = method

            if gap_sec is not None:
                event["timeline_gap_sec"] = gap_sec
                bounded_duration = max(1, min(gap_sec, metadata_duration))
                event["estimated_duration_sec"] = bounded_duration
                if bounded_duration < metadata_duration:
                    event["duration_confidence"] = "timeline_capped_api"
                    event["duration_source"] = "timeline_capped_api"
                else:
                    event["duration_confidence"] = "api"
                    event["duration_source"] = "youtube_api"
            else:
                event["estimated_duration_sec"] = metadata_duration
                event["duration_confidence"] = "api"
                event["duration_source"] = "youtube_api"
            continue

        # No metadata duration, perform timeline estimation
        if gap_sec is not None:
            event["timeline_gap_sec"] = gap_sec
            if gap_sec > 1800:
                # 30 minutes exceed -> idle capped
                event["estimated_duration_sec"] = 600  # DEFAULT_ESTIMATED_WATCH_SEC = 600
                event["duration_confidence"] = "estimated"
                event["duration_source"] = "idle_capped"
                method = "idle_capped"
            else:
                # Under 30 minutes -> gap based (up to 1800 capped)
                event["estimated_duration_sec"] = max(1, min(gap_sec, 1800))
                event["duration_confidence"] = "estimated"
                event["duration_source"] = "timeline_gap"
                method = "timeline_gap"
        else:
            event["estimated_duration_sec"] = default_sec
            event["duration_confidence"] = "estimated"
            event["duration_source"] = "default_estimate"
            method = "default_estimate"

        event["duration_estimation_method"] = method
        if "raw_item" in event and isinstance(event["raw_item"], dict):
            event["raw_item"]["duration_estimation_method"] = method


def _apply_mvp_limits(analysis_events: List[Dict[str, Any]]) -> tuple:
    max_watch = settings.MAX_WATCH_EVENTS
    max_search = settings.MAX_SEARCH_EVENTS

    watch_events = []
    search_events = []
    other_events = []

    for e in analysis_events:
        st = e.get("source_type") or ("search_history" if e.get("action_type") == "search" else "watch_history")
        if st == "watch_history":
            watch_events.append(e)
        elif st == "search_history":
            search_events.append(e)
        else:
            other_events.append(e)

    original_watch_count = len(watch_events)
    original_search_count = len(search_events)

    def get_time_key(event):
        t_str = event.get("event_time")
        if not t_str:
            return datetime.min
        try:
            return datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.min

    watch_events_sorted = sorted(watch_events, key=get_time_key, reverse=True)
    search_events_sorted = sorted(search_events, key=get_time_key, reverse=True)

    limited_watch_events = watch_events_sorted[:max_watch]
    limited_search_events = search_events_sorted[:max_search]

    limited_analysis_events = limited_watch_events + limited_search_events + other_events
    limited_analysis_events_sorted = sorted(limited_analysis_events, key=get_time_key)

    event_limit_applied = (original_watch_count > max_watch) or (original_search_count > max_search)
    sampling_metadata = {
        "original_watch_count": original_watch_count,
        "original_search_count": original_search_count,
        "processed_watch_count": len(limited_watch_events),
        "processed_search_count": len(limited_search_events),
        "event_limit_applied": event_limit_applied,
        "limit_per_source": max(max_watch, max_search),
        "limit_reason": "free_mvp_fast_analysis"
    }

    return limited_analysis_events_sorted, event_limit_applied, sampling_metadata, limited_watch_events, limited_search_events


class UploadService:
    """Service layer coordinating file uploading logic, validation, early parsing, and bulk database insert."""
    
    def __init__(self):
        self.repository = UploadRepository()

    def process_survey_scores(self, user_id: str, survey_scores: Optional[str]):
        if not survey_scores:
            return
        try:
            survey_data = json.loads(survey_scores)
            existing_profiles = self.repository.fetch_profiles(user_id)
            existing_scores = {}
            if existing_profiles:
                existing_scores = existing_profiles[0].get("survey_scores", {})
                if not isinstance(existing_scores, dict):
                    existing_scores = {}

            merged_scores = {**existing_scores, **survey_data}
            profile_entry = {
                "id": user_id,
                "survey_scores": merged_scores
            }
            if existing_profiles:
                profile_entry["email"] = existing_profiles[0].get("email", "seokhwan.son@gmail.com")
                profile_entry["nickname"] = existing_profiles[0].get("nickname", "손석환")
                profile_entry["birth_year"] = existing_profiles[0].get("birth_year", 1999)
            else:
                profile_entry["email"] = "seokhwan.son@gmail.com"
                profile_entry["nickname"] = "손석환"
                profile_entry["birth_year"] = 1999

            self.repository.save_profile(profile_entry)
            logger.info(f"Successfully merge-updated survey scores for user {user_id} in UploadService")
        except Exception as e:
            logger.error(f"Failed to merge-update survey scores in UploadService: {e}", exc_info=True)

    def upload_single_file(self, user_id: str, platform: str, action_type: str, filename: str, text_content: str, mock_estimation: bool) -> Dict[str, Any]:
        file_id = str(uuid.uuid4())
        raw_file_entry = {
            "id": file_id,
            "user_id": user_id,
            "storage_path": f"uploads/{file_id}_{filename}",
            "upload_status": "PROCESSING"
        }
        self.repository.save_raw_file(raw_file_entry)

        parsed_events = []
        file_extension = filename.split(".")[-1].lower() if filename else ""

        is_json = False
        raw_items = []

        if file_extension == "json":
            try:
                raw_items = json.loads(text_content)
                is_json = True
            except Exception as e:
                logger.warning(f"Failed to parse JSON file {filename}: {e}. Falling back to line-by-line.")
                is_json = False

        items = []
        if is_json and isinstance(raw_items, list):
            items = raw_items
        else:
            lines = text_content.split("\n")
            for line in lines:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                items.append({
                    "title": cleaned_line,
                    "time": None
                })

        base_time = datetime.utcnow()
        limit_count = PARSER_LIMITS["legacy_upload_json_items"] if is_json else PARSER_LIMITS["legacy_upload_text_lines"]
        fallback_used = False
        
        for i, item in enumerate(items[:limit_count]):
            parsed_res, parser_warnings = parse_single_item(item, file_kind=action_type, mock_estimation_enabled=mock_estimation)
            ad_reason = detect_ad_event_reason(parsed_res)
            
            event_time = parsed_res.get("event_time")
            timestamp_parse_failed = parsed_res.get("timestamp_parse_failed", False)
            if not event_time:
                timestamp_parse_failed = True
                
            if timestamp_parse_failed:
                fallback_used = True
                
            is_view = parsed_res["action_type"] == "view"
            
            url_for_class = parsed_res["title_url"] or item.get("title_url") or item.get("url") or item.get("titleUrl") or ""
            title_for_class = parsed_res["text_base"]
            duration_for_class = parsed_res.get("time_delta_sec") or parsed_res.get("estimated_duration_sec")
            
            from app.core.content_filters import check_shorts_candidate, check_general_watch_candidate
            is_shorts_cand, shorts_reason, shorts_conf = check_shorts_candidate(
                url=url_for_class,
                title=title_for_class,
                duration_seconds=duration_for_class,
                raw_item=item
            )
            is_general_cand, general_conf = check_general_watch_candidate(
                url=url_for_class,
                is_shorts_candidate=is_shorts_cand,
                raw_item=item
            )
            
            takeout_based_estimation = False
            if is_general_cand and parsed_res.get("time_delta_sec") is None:
                takeout_based_estimation = True

            parsed_events.append({
                "id": str(uuid.uuid4()),
                "file_id": file_id,
                "event_time": event_time,
                "time_delta_sec": parsed_res["time_delta_sec"],
                "video_duration_sec": parsed_res.get("video_duration_sec"),
                "text_base": parsed_res["text_base"] or "알 수 없는 비디오",
                "platform": platform,
                "action_type": parsed_res["action_type"],
                "source_surface": parsed_res["source_surface"],
                "source_confidence": parsed_res["source_confidence"],
                "source_type": infer_source_type({"action_type": parsed_res["action_type"]}),
                "channel_name": parsed_res["channel_name"],
                "channel_url": parsed_res.get("channel_url") or item.get("channel_url"),
                "title_url": parsed_res["title_url"],
                "video_id": parsed_res["video_id"],
                "content_format": parsed_res.get("content_format") or classify_content_format(parsed_res),
                "intent_level": parsed_res.get("intent_level") or ("active_search" if parsed_res["action_type"] == "search" else "unknown"),
                "search_query": parsed_res.get("search_query") or item.get("search_query"),
                "estimated_duration_sec": parsed_res["estimated_duration_sec"],
                "duration_confidence": parsed_res["duration_confidence"],
                "duration_source": "simulated" if is_view else parsed_res["duration_source"],
                "is_duration_estimated": True if is_view else False,
                "video_url": parsed_res["title_url"] or item.get("title_url") or item.get("url") or item.get("titleUrl"),
                "tags": item.get("tags") or [],
                "topicCategories": item.get("topicCategories") or [],
                "categoryId": item.get("categoryId") or "",
                "is_ad_event": bool(ad_reason),
                "ad_filter_reason": ad_reason,
                "raw_time": parsed_res.get("raw_time") or item.get("time") or "",
                "is_shorts_candidate": is_shorts_cand,
                "shorts_detection_reason": shorts_reason,
                "classification_confidence": shorts_conf if is_shorts_cand else general_conf,
                "is_general_watch_candidate": is_general_cand,
                "takeout_based_estimation": takeout_based_estimation,
                "timestamp_parse_failed": timestamp_parse_failed,
                "raw_item": item
            })

        analysis_events, excluded_ad_events = split_analysis_events(parsed_events)
        analysis_events, event_limit_applied, sampling_metadata, limited_watch_events, limited_search_events = _apply_mvp_limits(analysis_events)

        ad_skip_summary = build_ad_skip_summary(excluded_ad_events)
        content_format_counts = count_content_formats(analysis_events)
        shorts_analysis = build_shorts_analysis(analysis_events)
        
        apply_youtube_duration_metadata(analysis_events, mock_estimation_enabled=mock_estimation)
        
        timed_events = []
        for event in analysis_events:
            try:
                timed_events.append((datetime.strptime(event["event_time"], "%Y-%m-%d %H:%M:%S"), event))
            except Exception:
                continue
        apply_timeline_duration_estimates(timed_events, mock_estimation_enabled=mock_estimation)
        duration_source_counts = count_duration_sources(analysis_events)

        filtered_events = []
        skipped_count = 0

        for event in analysis_events:
            duration_for_filter = event.get("time_delta_sec")
            if duration_for_filter is None and mock_estimation:
                duration_for_filter = event.get("estimated_duration_sec")

            if event["action_type"] == "view" and duration_for_filter is not None:
                if duration_for_filter < DURATION_LIMITS["min_watch_sec"]:
                    skipped_count += 1
                    continue
            filtered_events.append(event)

        self.repository.save_norm_events(filtered_events)

        duration_unknown_used = any(e.get("time_delta_sec") is None and e.get("action_type") == "view" for e in filtered_events)
        data_quality_flags = []
        if fallback_used:
            data_quality_flags.append("timestamp_fallback_used")
        if duration_unknown_used:
            data_quality_flags.append("duration_unknown")
        if event_limit_applied:
            data_quality_flags.append("event_limit_applied")

        raw_file_entry["upload_status"] = "SUCCESS"
        raw_file_entry["excluded_ad_count"] = len(excluded_ad_events)
        raw_file_entry["ad_skip_summary"] = ad_skip_summary
        raw_file_entry["content_format_counts"] = content_format_counts
        raw_file_entry["duration_source_counts"] = duration_source_counts
        raw_file_entry["data_quality_flags"] = data_quality_flags
        raw_file_entry["sampling_metadata"] = sampling_metadata
        raw_file_entry["data_coverage"] = {
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "duration_source_counts": duration_source_counts,
            "data_quality_flags": data_quality_flags,
            "event_limit_applied": event_limit_applied,
            "sampling_metadata": sampling_metadata
        }
        self.repository.save_raw_file(raw_file_entry)

        sessions_list = build_sessions_from_events(filtered_events, gap_minutes=30)
        
        session_text_entries = []
        for idx, sess in enumerate(sessions_list[:100]):
            session_id = str(uuid.uuid4())
            aggregated_titles = " | ".join([e["text_base"] for e in sess if e.get("text_base")])
            session_text_entry = {
                "id": session_id,
                "file_id": file_id,
                "aggregated_text": aggregated_titles,
                "token_count": len(aggregated_titles.split()),
                "event_count": len(sess),
                "start_time": sess[0]["event_time"],
                "end_time": sess[-1]["event_time"]
            }
            session_text_entries.append(session_text_entry)
        self.repository.save_session_texts(session_text_entries)

        return {
            "success": True,
            "file_id": file_id,
            "session_count": len(sessions_list),
            "total_parsed": len(parsed_events),
            "total_saved": len(filtered_events),
            "skipped_fake_dopamine": skipped_count,
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "shorts_analysis": shorts_analysis,
            "duration_source_counts": duration_source_counts,
            "data_quality": {
                "duration": "estimated"
            },
            "warning_codes": ["P10_DURATION_ESTIMATED"],
            "original_total_count": len(parsed_events),
            "event_limit_applied": event_limit_applied,
            "limit_per_source": max(settings.MAX_WATCH_EVENTS, settings.MAX_SEARCH_EVENTS),
            "processed_watch_count": len(limited_watch_events),
            "processed_search_count": len(limited_search_events),
            "sampling_metadata": sampling_metadata,
            "message": "무료 MVP에서는 최근 시청/검색 기록 각 100건 기준으로 빠르게 분석합니다." if event_limit_applied else f"Successfully parsed {len(parsed_events)} events. 시청 지속 시간은 Google Takeout 한계로 인해 MVP용 추정값입니다."
        }

    def upload_takeout_flow(self, user_id: str, files_to_parse: List[dict], ignored_sources: List[str], skipped_sources_with_reason: Dict[str, str], mock_estimation: bool) -> Dict[str, Any]:
        total_start_time = time.perf_counter()
        
        parsed_events = []
        file_id = str(uuid.uuid4())
        raw_file_entry = {
            "id": file_id,
            "user_id": user_id,
            "storage_path": f"uploads/{file_id}_takeout_upload",
            "upload_status": "PROCESSING"
        }
        
        parsed_source_counts = {
            "watch_history": 0,
            "search_history": 0,
            "subscription": 0,
            "playlist": 0,
            "comment": 0,
            "live_chat": 0,
            "channel": 0
        }
        
        raw_watch_items = []
        raw_search_items = []
        raw_other_items = []

        # Parse and divide raw candidate items
        for file_info in files_to_parse:
            kind = file_info["kind"]
            items = TakeoutParser.identify_and_parse(file_info)
            parsed_source_counts[kind] = parsed_source_counts.get(kind, 0) + len(items)

            for item in items:
                item["_file_kind"] = kind
                if kind == "watch_history":
                    raw_watch_items.append(item)
                elif kind == "search_history":
                    raw_search_items.append(item)
                else:
                    raw_other_items.append(item)

        logger.info(f"[upload/takeout] parse_done raw_watch_count={len(raw_watch_items)} raw_search_count={len(raw_search_items)} raw_other_count={len(raw_other_items)}")

        # Limit applying early stage
        watch_before = len(raw_watch_items)
        search_before = len(raw_search_items)

        def get_raw_time_key(item):
            t_str = item.get("event_time")
            if not t_str:
                return datetime.min
            try:
                return datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return datetime.min

        raw_watch_items_sorted = sorted(raw_watch_items, key=get_raw_time_key, reverse=True)
        raw_search_items_sorted = sorted(raw_search_items, key=get_raw_time_key, reverse=True)

        max_watch = settings.MAX_WATCH_EVENTS
        max_search = settings.MAX_SEARCH_EVENTS

        limited_raw_watch_items = raw_watch_items_sorted[:max_watch]
        limited_raw_search_items = raw_search_items_sorted[:max_search]

        watch_after = len(limited_raw_watch_items)
        search_after = len(limited_raw_search_items)

        logger.info(f"[upload/takeout] limit_applied watch_before={watch_before} watch_after={watch_after} search_before={search_before} search_after={search_after}")

        limited_raw_items = limited_raw_watch_items + limited_raw_search_items + raw_other_items

        fallback_used = False
        base_time = datetime.utcnow()

        for idx, item in enumerate(limited_raw_items):
            kind = item["_file_kind"]
            parsed_res, parser_warnings = parse_single_item(
                item, 
                file_kind="search" if kind == "search_history" else "watch", 
                mock_estimation_enabled=mock_estimation
            )
            ad_reason = detect_ad_event_reason(parsed_res)

            event_time = parsed_res.get("event_time")
            timestamp_parse_failed = parsed_res.get("timestamp_parse_failed", False)
            if not event_time:
                timestamp_parse_failed = True

            if timestamp_parse_failed:
                fallback_used = True

            is_view = parsed_res["action_type"] == "view"
            
            url_for_class = parsed_res["title_url"] or item.get("title_url") or item.get("url") or item.get("titleUrl") or ""
            title_for_class = parsed_res["text_base"]
            duration_for_class = parsed_res.get("time_delta_sec") or parsed_res.get("estimated_duration_sec")
            
            from app.core.content_filters import check_shorts_candidate, check_general_watch_candidate
            is_shorts_cand, shorts_reason, shorts_conf = check_shorts_candidate(
                url=url_for_class,
                title=title_for_class,
                duration_seconds=duration_for_class,
                raw_item=item
            )
            is_general_cand, general_conf = check_general_watch_candidate(
                url=url_for_class,
                is_shorts_candidate=is_shorts_cand,
                raw_item=item
            )
            
            takeout_based_estimation = False
            if is_general_cand and parsed_res.get("time_delta_sec") is None:
                takeout_based_estimation = True

            parsed_events.append({
                "id": str(uuid.uuid4()),
                "file_id": file_id,
                "event_time": event_time,
                "time_delta_sec": parsed_res["time_delta_sec"],
                "video_duration_sec": parsed_res.get("video_duration_sec"),
                "text_base": parsed_res["text_base"] or "알 수 없는 비디오",
                "platform": "youtube",
                "action_type": parsed_res["action_type"],
                "source_surface": parsed_res["source_surface"],
                "source_confidence": parsed_res["source_confidence"],
                "source_type": kind,
                "channel_name": parsed_res["channel_name"],
                "channel_url": parsed_res.get("channel_url") or item.get("channel_url"),
                "title_url": parsed_res["title_url"],
                "video_id": parsed_res["video_id"],
                "content_format": parsed_res.get("content_format") or classify_content_format(parsed_res),
                "intent_level": item.get("intent_level") or ("active_search" if parsed_res["action_type"] == "search" else "unknown"),
                "search_query": parsed_res.get("search_query") or item.get("search_query"),
                "estimated_duration_sec": parsed_res["estimated_duration_sec"],
                "duration_confidence": parsed_res["duration_confidence"],
                "duration_source": "simulated" if is_view else parsed_res["duration_source"],
                "is_duration_estimated": True if is_view else False,
                "video_url": parsed_res["title_url"] or item.get("title_url") or item.get("url") or item.get("titleUrl"),
                "tags": item.get("tags") or [],
                "topicCategories": item.get("topicCategories") or [],
                "categoryId": item.get("categoryId") or "",
                "is_ad_event": bool(ad_reason),
                "ad_filter_reason": ad_reason,
                "raw_time": parsed_res.get("raw_time") or item.get("time") or "",
                "is_shorts_candidate": is_shorts_cand,
                "shorts_detection_reason": shorts_reason,
                "classification_confidence": shorts_conf if is_shorts_cand else general_conf,
                "is_general_watch_candidate": is_general_cand,
                "takeout_based_estimation": takeout_based_estimation,
                "timestamp_parse_failed": timestamp_parse_failed,
                "raw_item": item
            })

        analysis_events, excluded_ad_events = split_analysis_events(parsed_events)
        
        event_limit_applied = (watch_before > max_watch) or (search_before > max_search)
        sampling_metadata = {
            "original_watch_count": watch_before,
            "original_search_count": search_before,
            "processed_watch_count": len(limited_raw_watch_items),
            "processed_search_count": len(limited_raw_search_items),
            "event_limit_applied": event_limit_applied,
            "limit_per_source": max(max_watch, max_search),
            "limit_reason": "free_mvp_fast_analysis"
        }

        ad_skip_summary = build_ad_skip_summary(excluded_ad_events)
        response_skipped_sources = dict(skipped_sources_with_reason)
        if ad_skip_summary:
            response_skipped_sources["google_ads"] = f"Excluded {len(excluded_ad_events)} Google Ads/promotional Takeout events"

        analysis_source_counts = count_source_types(analysis_events)
        content_format_counts = count_content_formats(analysis_events)
        shorts_analysis = build_shorts_analysis(analysis_events)
        duration_source_counts = apply_youtube_duration_metadata(analysis_events, mock_estimation_enabled=mock_estimation)

        watch_search_events = [e for e in analysis_events if e["source_type"] in ["watch_history", "search_history"]]

        timed_events = []
        for event in watch_search_events:
            try:
                timed_events.append((datetime.strptime(event["event_time"], "%Y-%m-%d %H:%M:%S"), event))
            except Exception:
                continue

        apply_timeline_duration_estimates(timed_events, mock_estimation_enabled=mock_estimation)
        duration_source_counts = count_duration_sources(analysis_events)

        filtered_events = []
        skipped_count = 0

        for event in watch_search_events:
            duration_for_filter = event.get("time_delta_sec")
            if duration_for_filter is None and mock_estimation:
                duration_for_filter = event.get("estimated_duration_sec")

            if event["action_type"] == "view" and duration_for_filter is not None:
                if duration_for_filter < DURATION_LIMITS["min_watch_sec"]:
                    skipped_count += 1
                    continue
            filtered_events.append(event)

        aux_events = [e for e in analysis_events if e["source_type"] not in ["watch_history", "search_history"]]
        final_events = filtered_events + aux_events

        logger.info(f"[upload/takeout] filtering_done valid_count={len(final_events)} excluded_ad_count={len(excluded_ad_events)}")

        if not final_events:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="파싱된 이벤트가 없거나 모든 시청 기록이 생략되었습니다."
            )

        duration_unknown_used = any(e.get("time_delta_sec") is None and e.get("action_type") == "view" for e in final_events)
        data_quality_flags = []
        if fallback_used:
            data_quality_flags.append("timestamp_fallback_used")
        if duration_unknown_used:
            data_quality_flags.append("duration_unknown")
        if event_limit_applied:
            data_quality_flags.append("event_limit_applied")

        raw_file_entry["upload_status"] = "SUCCESS"
        raw_file_entry["excluded_ad_count"] = len(excluded_ad_events)
        raw_file_entry["skipped_sources_with_reason"] = response_skipped_sources
        raw_file_entry["ad_skip_summary"] = ad_skip_summary
        raw_file_entry["parsed_source_counts"] = parsed_source_counts
        raw_file_entry["analysis_source_counts"] = analysis_source_counts
        raw_file_entry["content_format_counts"] = content_format_counts
        raw_file_entry["duration_source_counts"] = duration_source_counts
        raw_file_entry["data_quality_flags"] = data_quality_flags
        raw_file_entry["sampling_metadata"] = sampling_metadata
        raw_file_entry["data_coverage"] = {
            "parsed_source_counts": parsed_source_counts,
            "analysis_source_counts": analysis_source_counts,
            "skipped_sources_with_reason": response_skipped_sources,
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "duration_source_counts": duration_source_counts,
            "data_quality_flags": data_quality_flags,
            "event_limit_applied": event_limit_applied,
            "sampling_metadata": sampling_metadata,
        }

        logger.info("[upload/takeout] raw_file_save_started")
        t_raw_start = time.perf_counter()
        self.repository.save_raw_file(raw_file_entry)
        elapsed_raw = int((time.perf_counter() - t_raw_start) * 1000)
        storage_type = "MockDB" if self.repository.is_mock else "Supabase"
        logger.info(f"[upload/takeout] raw_file_save_done elapsed_ms={elapsed_raw} storage={storage_type}")

        logger.info(f"[upload/takeout] norm_event_save_started count={len(final_events)}")
        t_norm_start = time.perf_counter()
        self.repository.save_norm_events(final_events)
        elapsed_norm = int((time.perf_counter() - t_norm_start) * 1000)
        logger.info(f"[upload/takeout] norm_event_save_done elapsed_ms={elapsed_norm} storage={storage_type}")

        sessions_list = build_sessions_from_events(filtered_events, gap_minutes=30)
        
        session_text_entries = []
        for idx, sess in enumerate(sessions_list[:100]):
            session_id = str(uuid.uuid4())
            aggregated_titles = " | ".join([e["text_base"] for e in sess if e.get("text_base")])
            session_text_entry = {
                "id": session_id,
                "file_id": file_id,
                "aggregated_text": aggregated_titles,
                "token_count": len(aggregated_titles.split()),
                "event_count": len(sess),
                "start_time": sess[0]["event_time"],
                "end_time": sess[-1]["event_time"]
            }
            session_text_entries.append(session_text_entry)

        aux_text_events = [e for e in aux_events if e.get("text_base")]
        aux_session_count = 0
        if aux_text_events:
            aux_session_id = str(uuid.uuid4())
            aux_titles = " | ".join([e["text_base"] for e in aux_text_events[:40]])
            aux_session_entry = {
                "id": aux_session_id,
                "file_id": file_id,
                "aggregated_text": aux_titles,
                "token_count": len(aux_titles.split()),
                "event_count": len(aux_text_events),
                "start_time": aux_text_events[0]["event_time"],
                "end_time": aux_text_events[-1]["event_time"]
            }
            session_text_entries.append(aux_session_entry)
            aux_session_count = 1

        logger.info(f"[upload/takeout] session_text_save_started count={len(session_text_entries)}")
        t_sess_start = time.perf_counter()
        self.repository.save_session_texts(session_text_entries)
        elapsed_sess = int((time.perf_counter() - t_sess_start) * 1000)
        logger.info(f"[upload/takeout] session_text_save_done elapsed_ms={elapsed_sess} storage={storage_type}")

        storage_status = raw_file_entry.get("__storage", "Unknown")
        if "Fallback" in storage_status or storage_status == "MockDB":
            logger.warning(f"[storage status] Supabase write failed or disabled. Local MockDB fallback activated for raw_file {file_id}. Storage backend: {storage_status}")
        else:
            logger.info(f"[storage status] Storage backend: {storage_status}")

        total_elapsed = int((time.perf_counter() - total_start_time) * 1000)
        logger.info(f"[upload/takeout] completed total_elapsed_ms={total_elapsed} file_id={file_id}")

        return {
            "success": True,
            "file_id": file_id,
            "parsed_source_counts": parsed_source_counts,
            "analysis_source_counts": analysis_source_counts,
            "ignored_sources": ignored_sources[:50], 
            "skipped_sources_with_reason": response_skipped_sources,
            "ad_skip_summary": ad_skip_summary,
            "session_count": len(sessions_list) + aux_session_count,
            "aux_session_count": aux_session_count,
            "total_parsed": len(parsed_events),
            "total_saved": len(final_events),
            "skipped_fake_dopamine": skipped_count,
            "excluded_ad_count": len(excluded_ad_events),
            "content_format_counts": content_format_counts,
            "shorts_analysis": shorts_analysis,
            "duration_source_counts": duration_source_counts,
            "data_quality": {
                "duration": "estimated"
            },
            "warning_codes": ["P10_DURATION_ESTIMATED"],
            "original_total_count": len(parsed_events),
            "event_limit_applied": event_limit_applied,
            "limit_per_source": max(settings.MAX_WATCH_EVENTS, settings.MAX_SEARCH_EVENTS),
            "processed_watch_count": len(limited_raw_watch_items),
            "processed_search_count": len(limited_raw_search_items),
            "sampling_metadata": sampling_metadata,
            "message": "무료 MVP에서는 최근 시청/검색 기록 각 100건 기준으로 빠르게 분석합니다." if event_limit_applied else "Successfully parsed Takeout events. 시청 지속 시간은 Google Takeout 한계로 인해 MVP용 추정값입니다."
        }
