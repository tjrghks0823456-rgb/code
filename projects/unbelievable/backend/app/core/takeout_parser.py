import re
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Action type patterns
RE_WATCHED_EN = re.compile(r"^Watched\s+", re.I)
RE_SEARCHED_EN = re.compile(r"^Searched for\s+", re.I)
RE_WATCHED_KO = re.compile(r"시청함|시청했습니다", re.I)
RE_SEARCHED_KO = re.compile(r"검색함|검색했습니다", re.I)

def extract_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        if "youtube.com" in parsed.netloc:
            # Check for standard watch
            query = urllib.parse.parse_qs(parsed.query)
            v = query.get("v")
            if v:
                return v[0]
            # Check for shorts or live or embed
            path_parts = parsed.path.strip("/").split("/")
            if "shorts" in path_parts and len(path_parts) > path_parts.index("shorts") + 1:
                return path_parts[path_parts.index("shorts") + 1]
            if "live" in path_parts and len(path_parts) > path_parts.index("live") + 1:
                return path_parts[path_parts.index("live") + 1]
            if "embed" in path_parts and len(path_parts) > path_parts.index("embed") + 1:
                return path_parts[path_parts.index("embed") + 1]
        elif "youtu.be" in parsed.netloc:
            parts = parsed.path.strip("/").split("/")
            if parts:
                return parts[0]
    except Exception:
        pass
    return None

def parse_takeout_timestamp(timestamp_str: str) -> Tuple[Optional[str], List[str]]:
    warnings = []
    if not timestamp_str:
        return None, ["timestamp_empty"]
    
    val = timestamp_str.strip()
    
    # 1. Try dateparser dynamically if available (supports broad multilingual formats)
    try:
        import dateparser
        parsed_dt = dateparser.parse(val)
        if parsed_dt:
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S"), []
    except ImportError:
        pass
    except Exception as e:
        warnings.append(f"dateparser_error: {str(e)}")

    # 2. Try python-dateutil standard parser (already installed)
    try:
        import dateutil.parser
        parsed_dt = dateutil.parser.parse(val)
        if parsed_dt:
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S"), []
    except Exception as e:
        warnings.append(f"dateutil_parser_error: {str(e)}")

    # 3. ISO 8601 or Standard Space-delimited Parse (e.g. 2023-10-27T20:15:30.000Z or 2023-10-27 20:15:30)
    try:
        clean_time = val.replace("Z", "")
        iso_str = clean_time.replace(" ", "T")
        if "T" in iso_str:
            if "." in iso_str:
                iso_str = iso_str.split(".")[0]
            parsed_time = datetime.fromisoformat(iso_str)
            return parsed_time.strftime("%Y-%m-%d %H:%M:%S"), []
    except Exception:
        pass

    # 4. Korean style (e.g. "2023. 10. 27. 오후 8:15:30 KST")
    if "오후" in val or "오전" in val:
        try:
            parts = [p.strip() for p in val.split() if p.strip()]
            year = parts[0].replace(".", "")
            month = parts[1].replace(".", "").zfill(2)
            day = parts[2].replace(".", "").zfill(2)
            ampm = parts[3]
            time_part = parts[4]

            hour_str, minute_str, second_str = time_part.split(":")
            hour = int(hour_str)
            if ampm == "오후" and hour < 12:
                hour += 12
            elif ampm == "오전" and hour == 12:
                hour = 0

            return f"{year}-{month}-{day} {str(hour).zfill(2)}:{minute_str.zfill(2)}:{second_str.zfill(2)}", []
        except Exception as e:
            warnings.append(f"korean_timestamp_parse_failed: {str(e)}")

    # 5. English style (e.g. "Oct 27, 2023, 8:15:30 PM UTC")
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    try:
        lower_str = val.lower()
        for m_name, m_num in months.items():
            if m_name in lower_str:
                clean_str = val.replace(",", " ")
                parts = [p.strip() for p in clean_str.split() if p.strip()]
                month_num = m_num
                day = parts[1].zfill(2)
                year = parts[2]
                time_part = parts[3]
                ampm = parts[4].upper()

                hour_str, minute_str, second_str = time_part.split(":")
                hour = int(hour_str)
                if ampm == "PM" and hour < 12:
                    hour += 12
                elif ampm == "AM" and hour == 12:
                    hour = 0

                return f"{year}-{month_num}-{day} {str(hour).zfill(2)}:{minute_str.zfill(2)}:{second_str.zfill(2)}", []
    except Exception as e:
        warnings.append(f"english_timestamp_parse_failed: {str(e)}")

    warnings.append("timestamp_format_unrecognized")
    return None, warnings

def parse_single_item(raw_item: Dict[str, Any], file_kind: str = "watch", mock_estimation_enabled: bool = False) -> Tuple[Dict[str, Any], List[str]]:
    warnings = []
    
    # 1. Title and Action Type extraction
    raw_title = raw_item.get("title") or raw_item.get("title_text") or raw_item.get("text_base") or ""
    title_text = raw_title
    
    action_type = "unknown"
    if RE_WATCHED_EN.match(raw_title):
        title_text = RE_WATCHED_EN.sub("", raw_title)
        action_type = "view"
    elif RE_SEARCHED_EN.match(raw_title):
        title_text = RE_SEARCHED_EN.sub("", raw_title)
        action_type = "search"
    elif RE_WATCHED_KO.search(raw_title):
        title_text = RE_WATCHED_KO.sub("", raw_title).strip()
        action_type = "view"
    elif RE_SEARCHED_KO.search(raw_title):
        title_text = RE_SEARCHED_KO.sub("", raw_title).strip()
        action_type = "search"
    else:
        # Fallback to file_kind
        if file_kind == "search":
            action_type = "search"
        elif file_kind == "watch":
            action_type = "view"
        warnings.append("action_type_inferred_from_file_kind")

    # 2. URL and Video ID
    title_url = raw_item.get("titleUrl") or raw_item.get("title_url") or raw_item.get("url") or ""
    video_id = extract_video_id(title_url)

    # 3. Channel Name
    channel_name = None
    subtitles = raw_item.get("subtitles", [])
    if subtitles and isinstance(subtitles, list):
        channel_name = subtitles[0].get("name")
    if not channel_name:
        channel_name = raw_item.get("header") or raw_item.get("channel_name")
    if not channel_name:
        details = raw_item.get("details", [])
        if isinstance(details, list) and details:
            channel_name = details[0].get("name")
    if not channel_name:
        channel_name = "Unknown"
        warnings.append("channel_name_missing")

    # 4. Time 파싱
    raw_time = raw_item.get("time") or raw_item.get("event_time") or ""
    event_time, time_warnings = parse_takeout_timestamp(raw_time)
    warnings.extend(time_warnings)
    timestamp_parse_failed = event_time is None

    # 5. source_surface / source_confidence (strictly as instructed)
    if action_type == "search":
        source_surface = "search_history"
        source_confidence = "estimated"
    else:
        source_surface = "unknown"
        source_confidence = "unknown"
    
    # 6. duration_sec / time_delta_sec
    time_delta_sec = None
    estimated_duration_sec = None
    duration_confidence = "unknown"
    duration_source = "none"
    estimated_duration_confidence = "unknown"

    if mock_estimation_enabled and action_type == "view":
        is_short = "/shorts/" in title_url or "youtube.com/shorts" in title_url
        estimated_duration_sec = 30 if is_short else 600
        duration_confidence = "medium" if is_short else "low"
        estimated_duration_confidence = duration_confidence
        duration_source = "mock_heuristic"
    elif action_type == "view":
        # When mock is disabled, we set duration_confidence to 'unknown' and wait for YouTube API / timeline logic.
        # But we default duration_confidence to 'unknown' and keep time_delta_sec/estimated_duration_sec as None
        pass

    # Assemble parsed item
    parsed_item = {
        "text_base": title_text,
        "action_type": action_type,
        "event_time": event_time,
        "raw_time": raw_time,
        "raw_timestamp": raw_time,
        "timestamp_parse_failed": timestamp_parse_failed,
        "timestamp_parse_status": "missing" if not raw_time else ("failed" if timestamp_parse_failed else "parsed"),
        "title_url": title_url or None,
        "video_id": video_id,
        "channel_name": channel_name,
        "source_surface": source_surface,
        "source_confidence": source_confidence,
        "time_delta_sec": time_delta_sec,
        "estimated_duration_sec": estimated_duration_sec,
        "duration_confidence": duration_confidence,
        "estimated_duration_confidence": estimated_duration_confidence,
        "duration_source": duration_source,
        "mock_estimation_used": mock_estimation_enabled,
        "raw_item": raw_item
    }

    return parsed_item, warnings
