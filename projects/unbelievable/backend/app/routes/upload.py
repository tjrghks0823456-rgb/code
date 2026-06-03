import uuid
import json
import logging
import zipfile
import urllib.parse
import csv
from io import BytesIO, StringIO
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from bs4 import BeautifulSoup
from app.core.content_filters import build_ad_skip_summary, detect_ad_event_reason, split_analysis_events
from app.core.database import db_client
from app.core.shorts_analysis import build_shorts_analysis
from app.core.upload_config import DURATION_LIMITS, PARSER_LIMITS, ZIP_LIMITS
from app.core.youtube import parse_iso8601_duration, youtube_client

logger = logging.getLogger(__name__)
router = APIRouter()

YOUTUBE_HINTS = [
    "youtube",
    "youtube and youtube music",
    "watch-history",
    "search-history",
    "history",
    "subscriptions",
    "playlists",
    "comments",
    "live_chat",
    "channels",
    "channel",
    "시청 기록",
    "검색 기록",
    "구독정보",
    "구독 정보",
    "재생목록",
    "재생 목록",
    "댓글",
    "실시간 채팅",
    "실시간채팅",
    "채널",
]

MAX_ZIP_FILE_COUNT = ZIP_LIMITS["max_file_count"]
MAX_SINGLE_FILE_SIZE = ZIP_LIMITS["max_single_file_size"]
MAX_TOTAL_EXTRACT_SIZE = ZIP_LIMITS["max_total_extract_size"]

def extract_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        if "youtube.com" in parsed.netloc:
            query = urllib.parse.parse_qs(parsed.query)
            v = query.get("v")
            if v:
                return v[0]
        elif "youtu.be" in parsed.netloc:
            parts = parsed.path.strip("/").split("/")
            if parts:
                return parts[0]
    except Exception:
        pass
    return None

def classify_content_format(item: Dict[str, Any]) -> str:
    action_type = (item.get("action_type") or "").lower()
    url = (
        item.get("title_url")
        or item.get("titleUrl")
        or item.get("url")
        or item.get("URL")
        or ""
    ).lower()
    title = (item.get("title_text") or item.get("text_base") or "").lower()

    if "/shorts/" in url or "youtube.com/shorts" in url:
        return "shorts"
    if "/live/" in url or "youtube.com/live" in url or "실시간 스트리밍" in title:
        return "live"
    if action_type == "view" and ("watch?v=" in url or item.get("video_id")):
        return "standard_video"
    return "unknown"

def infer_intent_level(item: Dict[str, Any]) -> str:
    action_type = (item.get("action_type") or "").lower()
    source_type = (item.get("source_type") or "").lower()
    if action_type == "search" or source_type == "search_history":
        return "active_search"
    return "unknown"

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

def is_shorts_item(item: Dict[str, Any]) -> bool:
    return classify_content_format(item) == "shorts"
    title = (item.get("title_text") or item.get("text_base") or "").lower()
    url = (item.get("title_url") or "").lower()
    return "shorts" in title or "#shorts" in title or "/shorts/" in url or "쇼츠" in title

def estimate_default_duration(item: Dict[str, Any]) -> tuple:
    if item.get("action_type") != "view":
        return None, "unknown", "not_applicable"

    if is_shorts_item(item):
        return DURATION_LIMITS["shorts_default_sec"], "medium", "shorts_heuristic"

    return DURATION_LIMITS["standard_default_sec"], "low", "default_heuristic"

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

def apply_youtube_duration_metadata(events: List[Dict[str, Any]]) -> Dict[str, int]:
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
    metadata_by_id: Dict[str, Dict[str, Any]] = {}
    for video_id in video_ids[:metadata_limit]:
        metadata_by_id[video_id] = youtube_client.get_video_metadata(video_id)

    for event in events:
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
            event["estimated_duration_sec"] = duration_sec
            event["duration_confidence"] = "api"
            event["duration_source"] = "youtube_api"
        elif duration_sec:
            event["mock_metadata_duration_sec"] = duration_sec

    return count_duration_sources(events)

def apply_timeline_duration_estimates(timed_events: List[tuple]) -> None:
    max_gap_sec = DURATION_LIMITS["max_timeline_gap_sec"]
    default_sec = DURATION_LIMITS["standard_default_sec"]

    timed_events.sort(key=lambda pair: pair[0])
    for idx, (event_time, event) in enumerate(timed_events[:-1]):
        if event["action_type"] != "view":
            continue

        next_event_time = timed_events[idx + 1][0]
        gap_sec = int((next_event_time - event_time).total_seconds())
        if gap_sec <= 0 or gap_sec > max_gap_sec:
            continue

        event["timeline_gap_sec"] = gap_sec
        metadata_duration = event.get("metadata_duration_sec")
        current_estimate = event.get("estimated_duration_sec") or default_sec

        if metadata_duration:
            bounded_duration = max(1, min(gap_sec, metadata_duration))
            event["time_delta_sec"] = bounded_duration
            event["estimated_duration_sec"] = metadata_duration
            if bounded_duration < metadata_duration:
                event["duration_confidence"] = "timeline_capped_api"
                event["duration_source"] = "timeline_capped_api"
            else:
                event["duration_confidence"] = "api"
                event["duration_source"] = "youtube_api"
            continue

        bounded_duration = max(1, min(gap_sec, current_estimate))
        event["time_delta_sec"] = bounded_duration
        event["estimated_duration_sec"] = bounded_duration
        event["duration_confidence"] = "timeline"
        event["duration_source"] = "timeline_gap"

def classify_takeout_file(path: str) -> str:
    lower = path.replace("\\", "/").lower()
    filename = lower.rsplit("/", 1)[-1]

    if "search-history" in lower or "검색 기록" in filename:
        return "search_history"
    if "watch-history" in lower or "시청 기록" in filename or "/시청 기록/" in lower:
        return "watch_history"
    if "subscriptions" in lower or "subscription" in lower or "구독정보" in lower or "구독 정보" in lower:
        return "subscription"
    if "playlists" in lower or "playlist" in lower or "재생목록" in lower or "재생 목록" in lower:
        return "playlist"
    if "comments" in lower or "comment" in lower or "댓글" in lower:
        return "comment"
    if "live_chat" in lower or "live chat" in lower or "실시간 채팅" in lower or "실시간채팅" in lower:
        return "live_chat"
    if "channels" in lower or "channel" in lower or "채널" in lower:
        return "channel"
    # The parent folder is often named "YouTube and YouTube Music", so only
    # classify explicit music-only exports as music noise.
    music_markers = [
        "music (library and uploads)",
        "music-library",
        "music_library",
        "music uploads",
        "music-uploads",
        "music_uploads",
        "youtube music/",
        "youtube music\\",
    ]
    if any(marker in lower for marker in music_markers):
        return "music"
    return "unknown"

def is_supported_takeout_file(path: str) -> bool:
    lower = path.lower()
    if not (lower.endswith(".json") or lower.endswith(".html") or lower.endswith(".csv") or lower.endswith(".txt")):
        return False
    kind = classify_takeout_file(lower)
    return kind != "unknown" and kind != "music"

def scan_youtube_files_from_zip(zip_bytes: bytes):
    results = []
    ignored_sources = []
    skipped_sources_with_reason = {}
    total_size = 0

    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
            infos = zf.infolist()

            if len(infos) > MAX_ZIP_FILE_COUNT:
                raise ValueError("ZIP 내부 파일 개수가 너무 많습니다.")

            for info in infos:
                if info.is_dir():
                    continue

                # ZIP Slip 방지
                if ".." in info.filename or info.filename.startswith("/"):
                    continue

                kind = classify_takeout_file(info.filename)

                if kind == "music":
                    ignored_sources.append(info.filename)
                    skipped_sources_with_reason[info.filename] = "Excluded in MVP configuration (Music library/uploads)"
                    continue

                if not is_supported_takeout_file(info.filename):
                    continue

                if info.file_size > MAX_SINGLE_FILE_SIZE:
                    raise ValueError(f"ZIP 내 파일 '{info.filename}'의 용량이 제한(30MB)을 초과했습니다.")

                total_size += info.file_size
                if total_size > MAX_TOTAL_EXTRACT_SIZE:
                    raise ValueError(f"ZIP 내 대상 파일들의 총 용량이 제한(150MB)을 초과했습니다.")

                results.append({
                    "filename": info.filename,
                    "content": zf.read(info),
                    "kind": kind
                })
    except Exception as e:
        logger.error(f"Failed to scan ZIP file: {e}")
        raise ValueError(str(e))

    return results, ignored_sources, skipped_sources_with_reason

def parse_takeout_html_timestamp(timestamp_str: str) -> Optional[str]:
    timestamp_str = timestamp_str.strip()
    if not timestamp_str:
        return None

    # Handle Korean format: "2023. 10. 27. 오후 8:15:30 KST"
    if "오후" in timestamp_str or "오전" in timestamp_str:
        try:
            parts = [p.strip() for p in timestamp_str.split() if p.strip()]
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

            return f"{year}-{month}-{day} {str(hour).zfill(2)}:{minute_str.zfill(2)}:{second_str.zfill(2)}"
        except Exception as e:
            logger.warning(f"Failed to parse Korean timestamp '{timestamp_str}': {e}")

    # Handle English format: "Oct 27, 2023, 8:15:30 PM UTC"
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }

    try:
        lower_str = timestamp_str.lower()
        for m_name, m_num in months.items():
            if m_name in lower_str:
                clean_str = timestamp_str.replace(",", " ")
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

                return f"{year}-{month_num}-{day} {str(hour).zfill(2)}:{minute_str.zfill(2)}:{second_str.zfill(2)}"
    except Exception as e:
        logger.warning(f"Failed to parse English timestamp '{timestamp_str}': {e}")

    try:
        clean_time = timestamp_str.replace("Z", "")
        if "T" in clean_time:
            if "." in clean_time:
                clean_time = clean_time.split(".")[0]
            parsed_time = datetime.fromisoformat(clean_time)
            return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    return None

def parse_youtube_html(html_content: str, file_kind: str) -> List[dict]:
    # Fast extraction of bounded cells to prevent BeautifulSoup hanging on huge Takeout files.
    cells_html = []
    start_pos = 0
    for _ in range(PARSER_LIMITS["max_html_content_cells"]):
        pos = html_content.find('class="content-cell', start_pos)
        if pos == -1:
            break
        div_start = html_content.rfind('<div', 0, pos)
        if div_start == -1:
            break
        div_end = html_content.find('</div>', pos)
        if div_end == -1:
            break
        cells_html.append(html_content[div_start:div_end+6])
        start_pos = div_end + 6

    tiny_html = "<html><body>" + "".join(cells_html) + "</body></html>"

    soup = BeautifulSoup(tiny_html, "html.parser")
    cells = soup.find_all(class_="content-cell")
    parsed_items = []

    for cell in cells:
        text = cell.get_text()
        title_text = ""
        action_type = "search" if file_kind == "search" else "view"
        video_id = None
        channel_name = None
        channel_url = None

        a_tags = cell.find_all("a")

        if file_kind == "search":
            action_type = "search"
            if len(a_tags) >= 1:
                title_text = a_tags[0].get_text().strip()
                video_id = extract_video_id(a_tags[0].get("href", ""))
        elif len(a_tags) >= 1:
            title_text = a_tags[0].get_text().strip()
            video_id = extract_video_id(a_tags[0].get("href", ""))
            if len(a_tags) >= 2:
                channel_name = a_tags[1].get_text().strip()
                channel_url = a_tags[1].get("href", "")

        if "Watched " in text:
            action_type = "view"
            if len(a_tags) >= 1:
                title_text = a_tags[0].get_text().strip()
                video_id = extract_video_id(a_tags[0].get("href", ""))
            if len(a_tags) >= 2:
                channel_name = a_tags[1].get_text().strip()
                channel_url = a_tags[1].get("href", "")
        elif "Searched for " in text:
            action_type = "search"
            if len(a_tags) >= 1:
                title_text = a_tags[0].get_text().strip()
                video_id = extract_video_id(a_tags[0].get("href", ""))

        if not title_text:
            if text.startswith("Watched "):
                title_text = text[len("Watched "):].split("\n")[0].strip()
                action_type = "view"
            elif text.startswith("Searched for "):
                title_text = text[len("Searched for "):].split("\n")[0].strip()
                action_type = "search"

        lines = [line.strip() for line in cell.stripped_strings if line.strip()]
        timestamp_str = ""
        if len(lines) >= 3:
            timestamp_str = lines[-1]
        elif len(lines) == 2:
            timestamp_str = lines[-1]

        parsed_time_str = parse_takeout_html_timestamp(timestamp_str) if timestamp_str else None
        if not parsed_time_str:
            parsed_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        parsed_item = {
            "title_text": title_text or "알 수 없는 비디오",
            "action_type": action_type,
            "event_time": parsed_time_str,
            "video_id": video_id,
            "title_url": a_tags[0].get("href", "") if len(a_tags) >= 1 else None,
            "channel_name": channel_name,
            "channel_url": channel_url
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = infer_intent_level(parsed_item)
        ad_reason = detect_ad_event_reason({**parsed_item, "raw_takeout_text": text})
        if ad_reason:
            parsed_item["is_ad_event"] = True
            parsed_item["ad_filter_reason"] = ad_reason
        parsed_items.append(parsed_item)

    return parsed_items

def parse_youtube_json(json_content: str, file_kind: str) -> List[dict]:
    raw_items = json.loads(json_content)
    parsed_items = []

    if not isinstance(raw_items, list):
        return []

    for item in raw_items[:PARSER_LIMITS["max_json_history_items"]]:
        if not isinstance(item, dict):
            continue

        raw_title = item.get("title", "")
        if not raw_title:
            continue

        title_text = raw_title
        action_type = "search" if file_kind == "search" else "view"
        if raw_title.startswith("Watched "):
            title_text = raw_title[len("Watched "):]
            if file_kind != "search":
                action_type = "view"
        elif raw_title.startswith("Searched for "):
            title_text = raw_title[len("Searched for "):]
            action_type = "search"

        # Extract video_id from titleUrl
        title_url = item.get("titleUrl", "")
        video_id = extract_video_id(title_url)

        # Channel metadata
        subtitles = item.get("subtitles", [])
        channel_name = None
        channel_url = None
        if subtitles and isinstance(subtitles, list):
            channel_name = subtitles[0].get("name", "")
            channel_url = subtitles[0].get("url", "")

        item_time = item.get("time", "")
        parsed_time_str = None
        if item_time:
            try:
                clean_time = item_time.replace("Z", "")
                if "." in clean_time:
                    clean_time = clean_time.split(".")[0]
                parsed_time = datetime.fromisoformat(clean_time)
                parsed_time_str = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        if not parsed_time_str:
            parsed_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        parsed_item = {
            "title_text": title_text,
            "action_type": action_type,
            "event_time": parsed_time_str,
            "video_id": video_id,
            "title_url": title_url,
            "channel_name": channel_name,
            "channel_url": channel_url
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = infer_intent_level(parsed_item)
        ad_reason = detect_ad_event_reason({**item, **parsed_item})
        if ad_reason:
            parsed_item["is_ad_event"] = True
            parsed_item["ad_filter_reason"] = ad_reason
        parsed_items.append(parsed_item)

    return parsed_items

def parse_youtube_subscription(content: str, is_json: bool) -> List[dict]:
    parsed_items = []
    if is_json:
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    snippet = item.get("snippet", {})
                    title = snippet.get("title", "")
                    resource = snippet.get("resourceId", {})
                    channel_id = resource.get("channelId", "")
                    channel_url = f"https://www.youtube.com/channel/{channel_id}" if channel_id else ""
                    published_at = snippet.get("publishedAt", "")
                    parsed_items.append({
                        "title_text": title,
                        "action_type": "subscription",
                        "event_time": published_at.replace("Z", "").replace("T", " ").split(".")[0] if published_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "channel_name": title,
                        "channel_url": channel_url
                    })
        except Exception:
            pass
    else:
        try:
            soup = BeautifulSoup(content, "html.parser")
            links = soup.find_all("a")
            for link in links[:PARSER_LIMITS["max_html_links"]]:
                name = link.get_text().strip()
                url = link.get("href", "")
                parsed_items.append({
                    "title_text": name,
                    "action_type": "subscription",
                    "event_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "channel_name": name,
                    "channel_url": url
                })
        except Exception:
            pass
        if not parsed_items:
            parsed_items = parse_youtube_auxiliary(content, "subscription")
    return parsed_items

def parse_youtube_playlist(content: str, is_json: bool) -> List[dict]:
    parsed_items = []
    if is_json:
        try:
            data = json.loads(content)
            playlist_title = data.get("title", "재생목록")
            items = data.get("items", [])
            if isinstance(items, list):
                for item in items:
                    title = item.get("title", "")
                    url = item.get("videoUrl", "")
                    added_date = item.get("addedDate", "")
                    video_id = extract_video_id(url)
                    parsed_items.append({
                        "title_text": title,
                        "action_type": "playlist",
                        "event_time": added_date.replace("Z", "").replace("T", " ").split(".")[0] if added_date else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "title_url": url,
                        "video_id": video_id,
                        "channel_name": playlist_title
                    })
        except Exception:
            pass
    else:
        try:
            soup = BeautifulSoup(content, "html.parser")
            links = soup.find_all("a")
            for link in links[:PARSER_LIMITS["max_html_links"]]:
                title = link.get_text().strip()
                url = link.get("href", "")
                video_id = extract_video_id(url)
                parsed_items.append({
                    "title_text": title,
                    "action_type": "playlist",
                    "event_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "title_url": url,
                    "video_id": video_id
                })
        except Exception:
            pass
        if not parsed_items:
            parsed_items = parse_youtube_auxiliary(content, "playlist")
    return parsed_items

def parse_youtube_auxiliary(content: str, action_type: str) -> List[dict]:
    parsed_items = []
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def append_item(title: str, url: Optional[str] = None, channel_name: Optional[str] = None, event_time: Optional[str] = None):
        clean_title = (title or "").strip()
        clean_url = (url or "").strip()
        if not clean_title and clean_url:
            clean_title = clean_url
        if not clean_title:
            return
        parsed_item = {
            "title_text": clean_title[:500],
            "action_type": action_type,
            "event_time": event_time or now_str,
            "title_url": clean_url or None,
            "video_id": extract_video_id(clean_url),
            "channel_name": channel_name or clean_title,
            "channel_url": clean_url or None
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = infer_intent_level(parsed_item)
        parsed_items.append(parsed_item)

    def pick_first(data: Dict[str, Any], keys: List[str]) -> str:
        for key in keys:
            value = data.get(key)
            if value:
                return str(value)
        return ""

    try:
        data = json.loads(content)
        if isinstance(data, dict):
            records = data.get("items") or data.get("comments") or data.get("messages") or data.get("channels") or [data]
        elif isinstance(data, list):
            records = data
        else:
            records = []

        for item in records[:PARSER_LIMITS["max_auxiliary_records"]]:
            if not isinstance(item, dict):
                continue
            snippet = item.get("snippet", {}) if isinstance(item.get("snippet", {}), dict) else {}
            title = (
                pick_first(item, [
                    "title", "name", "channelTitle", "text", "comment", "message", "content",
                    "채널 제목", "채널 제목(원본)", "댓글 텍스트", "실시간 채팅 텍스트",
                    "재생목록 제목(원본)", "재생목록 ID", "동영상 ID", "댓글 ID", "실시간 채팅 ID"
                ])
                or pick_first(snippet, ["title", "channelTitle", "textDisplay", "textOriginal", "description"])
            )
            url = pick_first(item, ["url", "URL", "channelUrl", "videoUrl", "titleUrl", "채널 URL"])
            channel_name = (
                pick_first(item, ["channelName", "channelTitle", "author", "authorName", "채널 제목", "채널 제목(원본)", "채널 ID"])
                or pick_first(snippet, ["channelTitle", "authorDisplayName"])
            )
            raw_time = (
                pick_first(item, [
                    "time", "publishedAt", "createdAt", "timestamp",
                    "댓글 생성 타임스탬프", "실시간 채팅 생성 타임스탬프",
                    "재생목록 생성 타임스탬프", "재생목록 업데이트 타임스탬프", "재생목록 동영상 생성 타임스탬프"
                ])
                or pick_first(snippet, ["publishedAt"])
            )
            event_time = None
            if raw_time:
                event_time = raw_time.replace("Z", "").replace("T", " ").split(".")[0]
            append_item(title, url, channel_name, event_time)
    except Exception:
        pass

    if parsed_items:
        return parsed_items

    try:
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a")[:PARSER_LIMITS["max_html_links"]]:
            append_item(link.get_text().strip(), link.get("href", ""))
    except Exception:
        pass

    if parsed_items:
        return parsed_items

    try:
        csv_text = StringIO(content)
        reader = csv.DictReader(csv_text)
        if reader.fieldnames:
            for row in list(reader)[:PARSER_LIMITS["max_csv_rows"]]:
                title = pick_first(row, [
                    "title", "Title", "name", "Name", "channel", "Channel", "comment", "Comment", "message", "Message",
                    "채널 제목", "채널 제목(원본)", "댓글 텍스트", "실시간 채팅 텍스트",
                    "재생목록 제목(원본)", "재생목록 ID", "동영상 ID", "댓글 ID", "실시간 채팅 ID"
                ])
                url = pick_first(row, ["url", "URL", "channel_url", "Channel URL", "video_url", "Video URL", "채널 URL"])
                channel_name = pick_first(row, ["channelName", "Channel Name", "채널 제목", "채널 제목(원본)", "채널 ID"])
                raw_time = pick_first(row, [
                    "time", "Time", "publishedAt", "createdAt", "timestamp",
                    "댓글 생성 타임스탬프", "실시간 채팅 생성 타임스탬프",
                    "재생목록 생성 타임스탬프", "재생목록 업데이트 타임스탬프", "재생목록 동영상 생성 타임스탬프"
                ])
                event_time = raw_time.replace("Z", "").replace("T", " ").split(".")[0] if raw_time else None
                append_item(title, url, channel_name, event_time)
        else:
            csv_text.seek(0)
            for row in list(csv.reader(csv_text))[:PARSER_LIMITS["max_csv_rows"]]:
                values = [cell.strip() for cell in row if cell.strip()]
                if values:
                    append_item(" | ".join(values[:3]))
    except Exception:
        pass

    return parsed_items

@router.post("/upload")
async def upload_file(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    platform: str = "youtube",
    action_type: str = "view",
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        file_id = str(uuid.uuid4())
        raw_file_entry = {
            "id": file_id,
            "user_id": user_id,
            "storage_path": f"uploads/{file_id}_{file.filename}",
            "upload_status": "PROCESSING"
        }
        db_client.save_data("raw_file", raw_file_entry)

        parsed_events = []
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""

        is_json = False
        raw_items = []

        if file_extension == "json":
            try:
                raw_items = json.loads(text_content)
                is_json = True
            except Exception as e:
                logger.warning(f"Failed to parse JSON file {file.filename}: {e}. Falling back to line-by-line.")
                is_json = False

        if is_json and isinstance(raw_items, list):
            for i, item in enumerate(raw_items[:PARSER_LIMITS["legacy_upload_json_items"]]):
                if not isinstance(item, dict):
                    continue

                raw_title = item.get("title", "")
                if not raw_title:
                    continue

                title_text = raw_title
                current_action_type = action_type
                if raw_title.startswith("Watched "):
                    title_text = raw_title[len("Watched "):]
                    current_action_type = "view"
                elif raw_title.startswith("Searched for "):
                    title_text = raw_title[len("Searched for "):]
                    current_action_type = "search"

                title_url = item.get("titleUrl", "")
                video_id = extract_video_id(title_url)
                current_source_type = infer_source_type({"action_type": current_action_type})
                duration_item = {
                    "title_text": title_text,
                    "title_url": title_url,
                    "action_type": current_action_type,
                    "source_type": current_source_type,
                }
                estimated_duration_sec, duration_confidence, duration_source = estimate_default_duration(duration_item)
                ad_reason = detect_ad_event_reason({**item, **duration_item})

                item_time = item.get("time", "")
                parsed_time_str = None
                if item_time:
                    try:
                        clean_time = item_time.replace("Z", "")
                        if "." in clean_time:
                            clean_time = clean_time.split(".")[0]
                        parsed_time = datetime.fromisoformat(clean_time)
                        parsed_time_str = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as time_err:
                        logger.warning(f"Could not parse timestamp {item_time}: {time_err}")

                if not parsed_time_str:
                    parsed_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                parsed_events.append({
                    "id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "event_time": parsed_time_str,
                    "time_delta_sec": None,
                    "text_base": title_text,
                    "platform": platform,
                    "action_type": current_action_type,
                    "source_type": current_source_type,
                    "source_surface": "unknown",
                    "title_url": title_url,
                    "video_id": video_id,
                    "content_format": classify_content_format(duration_item),
                    "intent_level": infer_intent_level(duration_item),
                    "estimated_duration_sec": estimated_duration_sec,
                    "duration_confidence": duration_confidence,
                    "duration_source": duration_source,
                    "is_ad_event": bool(ad_reason),
                    "ad_filter_reason": ad_reason
                })
        else:
            lines = text_content.split("\n")
            base_time = datetime.utcnow()
            for i, line in enumerate(lines[:PARSER_LIMITS["legacy_upload_text_lines"]]):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue

                title_text = cleaned_line
                if "," in cleaned_line:
                    parts = cleaned_line.split(",")
                    if len(parts) > 1:
                        title_text = parts[0].strip("\" ")

                current_source_type = infer_source_type({"action_type": action_type})
                duration_item = {
                    "title_text": title_text,
                    "action_type": action_type,
                    "source_type": current_source_type,
                }
                estimated_duration_sec, duration_confidence, duration_source = estimate_default_duration(duration_item)
                ad_reason = detect_ad_event_reason({**duration_item, "raw_line": cleaned_line})

                parsed_events.append({
                    "id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "event_time": datetime.fromtimestamp(base_time.timestamp() - (i * 600)).strftime("%Y-%m-%d %H:%M:%S"),
                    "time_delta_sec": None,
                    "text_base": title_text,
                    "platform": platform,
                    "action_type": action_type,
                    "source_type": current_source_type,
                    "source_surface": "unknown",
                    "content_format": classify_content_format(duration_item),
                    "intent_level": infer_intent_level(duration_item),
                    "estimated_duration_sec": estimated_duration_sec,
                    "duration_confidence": duration_confidence,
                    "duration_source": duration_source,
                    "is_ad_event": bool(ad_reason),
                    "ad_filter_reason": ad_reason
                })

        analysis_events, excluded_ad_events = split_analysis_events(parsed_events)
        ad_skip_summary = build_ad_skip_summary(excluded_ad_events)
        content_format_counts = count_content_formats(analysis_events)
        shorts_analysis = build_shorts_analysis(analysis_events)
        apply_youtube_duration_metadata(analysis_events)
        timed_events = []
        for event in analysis_events:
            try:
                timed_events.append((datetime.strptime(event["event_time"], "%Y-%m-%d %H:%M:%S"), event))
            except Exception:
                continue
        apply_timeline_duration_estimates(timed_events)
        duration_source_counts = count_duration_sources(analysis_events)

        filtered_events = []
        skipped_count = 0

        for event in analysis_events:
            duration_for_filter = event.get("time_delta_sec")
            if duration_for_filter is None:
                duration_for_filter = event.get("estimated_duration_sec")

            if event["action_type"] == "view" and duration_for_filter is not None and duration_for_filter < DURATION_LIMITS["min_watch_sec"]:
                skipped_count += 1
                continue
            filtered_events.append(event)

        for event in filtered_events:
            db_client.save_data("norm_event", event)

        raw_file_entry["upload_status"] = "SUCCESS"
        raw_file_entry["excluded_ad_count"] = len(excluded_ad_events)
        raw_file_entry["ad_skip_summary"] = ad_skip_summary
        raw_file_entry["content_format_counts"] = content_format_counts
        raw_file_entry["duration_source_counts"] = duration_source_counts
        raw_file_entry["data_coverage"] = {
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "duration_source_counts": duration_source_counts,
        }
        db_client.save_data("raw_file", raw_file_entry)

        session_id = str(uuid.uuid4())
        standard_text_events = [
            event for event in filtered_events
            if event.get("action_type") == "search"
            or (event.get("action_type") == "view" and event.get("content_format") == "standard_video")
        ]
        aggregated_titles = " | ".join([e["text_base"] for e in standard_text_events[:15]])
        session_text_entry = {
            "id": session_id,
            "file_id": file_id,
            "aggregated_text": aggregated_titles,
            "token_count": len(aggregated_titles.split()),
            "start_time": standard_text_events[-1]["event_time"] if standard_text_events else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": standard_text_events[0]["event_time"] if standard_text_events else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        if aggregated_titles:
            db_client.save_data("session_text", session_text_entry)

        return {
            "success": True,
            "file_id": file_id,
            "session_id": session_id if aggregated_titles else None,
            "total_parsed": len(parsed_events),
            "total_saved": len(filtered_events),
            "skipped_fake_dopamine": skipped_count,
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "shorts_analysis": shorts_analysis,
            "duration_source_counts": duration_source_counts,
            "message": f"Successfully parsed {len(parsed_events)} events. Filtered out {skipped_count} short-form dopamine loops (< {DURATION_LIMITS['min_watch_sec']}s)."
        }
    except Exception as e:
        logger.error(f"Upload processing crash: {e}")
        raise HTTPException(status_code=500, detail=f"File upload and parsing failed: {str(e)}")

@router.post("/upload/takeout")
async def upload_takeout(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    files: List[UploadFile] = File(default=None),
    paths: List[str] = Form(default=None),
    zip_file: UploadFile = File(default=None),
    survey_scores: Optional[str] = Form(default=None)
):
    """
    Handles refined multi-file folder and ZIP Google Takeout uploads.
    Integrates surveys, ignores music paths, extracts channel info, and divides chronological sessions.
    """
    try:
        # 1. Merge-update survey scores
        if survey_scores:
            try:
                survey_data = json.loads(survey_scores)
                existing_profiles = db_client.fetch_data("profiles", {"id": user_id})
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

                db_client.save_data("profiles", profile_entry)
                logger.info(f"Successfully merge-updated survey scores for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to merge-update survey scores: {e}", exc_info=True)

        files_to_parse = []
        ignored_sources = []
        skipped_sources_with_reason = {}

        # 2. Gather candidates
        if zip_file:
            zip_content = await zip_file.read()
            zip_files, ignored_sources, skipped_sources_with_reason = scan_youtube_files_from_zip(zip_content)
            for zf in zip_files:
                files_to_parse.append({
                    "name": zf["filename"],
                    "content": zf["content"].decode("utf-8", errors="ignore"),
                    "kind": zf["kind"]
                })
        elif files:
            for idx, file in enumerate(files):
                rel_path = paths[idx] if (paths and idx < len(paths)) else file.filename
                kind = classify_takeout_file(rel_path)

                if kind == "music":
                    ignored_sources.append(rel_path)
                    skipped_sources_with_reason[rel_path] = "Excluded in MVP configuration (Music library/uploads)"
                    continue

                if not is_supported_takeout_file(rel_path):
                    continue

                content = await file.read()
                files_to_parse.append({
                    "name": rel_path,
                    "content": content.decode("utf-8", errors="ignore"),
                    "kind": kind
                })

        if not files_to_parse:
            raise HTTPException(
                status_code=400,
                detail="YouTube 시청/검색 기록 파일(watch-history.json/html, search-history.json/html)을 발견하지 못했습니다."
            )

        # 3. Parse all files and normalize
        parsed_events = []
        file_id = str(uuid.uuid4())
        raw_file_entry = {
            "id": file_id,
            "user_id": user_id,
            "storage_path": f"uploads/{file_id}_takeout_upload",
            "upload_status": "PROCESSING"
        }
        db_client.save_data("raw_file", raw_file_entry)

        parsed_source_counts = {
            "watch_history": 0,
            "search_history": 0,
            "subscription": 0,
            "playlist": 0,
            "comment": 0,
            "live_chat": 0,
            "channel": 0
        }

        for file_info in files_to_parse:
            name = file_info["name"]
            content = file_info["content"]
            kind = file_info["kind"]

            items = []
            is_json = name.lower().endswith(".json")

            if kind in ["watch_history", "search_history"]:
                file_kind = "search" if kind == "search_history" else "watch"
                if is_json:
                    items = parse_youtube_json(content, file_kind)
                else:
                    items = parse_youtube_html(content, file_kind)
            elif kind == "subscription":
                items = parse_youtube_subscription(content, is_json)
            elif kind == "playlist":
                items = parse_youtube_playlist(content, is_json)
            elif kind in ["comment", "live_chat", "channel"]:
                items = parse_youtube_auxiliary(content, kind)

            parsed_source_counts[kind] = parsed_source_counts.get(kind, 0) + len(items)

            for idx, item in enumerate(items):
                estimated_duration_sec, duration_confidence, duration_source = estimate_default_duration(item)
                ad_reason = detect_ad_event_reason(item)

                parsed_events.append({
                    "id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "event_time": item["event_time"],
                    "time_delta_sec": None, # Removed simulated mock values
                    "text_base": item["title_text"],
                    "platform": "youtube",
                    "action_type": item["action_type"],
                    "source_surface": "unknown",
                    "source_type": kind,
                    "channel_name": item.get("channel_name"),
                    "channel_url": item.get("channel_url"),
                    "title_url": item.get("title_url"),
                    "video_id": item.get("video_id"),
                    "content_format": item.get("content_format") or classify_content_format(item),
                    "intent_level": item.get("intent_level") or infer_intent_level({**item, "source_type": kind}),
                    "estimated_duration_sec": estimated_duration_sec,
                    "duration_confidence": duration_confidence,
                    "duration_source": duration_source,
                    "is_ad_event": bool(ad_reason),
                    "ad_filter_reason": ad_reason
                })

        analysis_events, excluded_ad_events = split_analysis_events(parsed_events)
        ad_skip_summary = build_ad_skip_summary(excluded_ad_events)
        response_skipped_sources = dict(skipped_sources_with_reason)
        if ad_skip_summary:
            response_skipped_sources["google_ads"] = f"Excluded {len(excluded_ad_events)} Google Ads/promotional Takeout events"
        analysis_source_counts = count_source_types(analysis_events)
        content_format_counts = count_content_formats(analysis_events)
        shorts_analysis = build_shorts_analysis(analysis_events)
        duration_source_counts = apply_youtube_duration_metadata(analysis_events)

        # 4. Filter watch history views for dopamine filter & sessions
        # (Exclude playlist/subscription from standard watch filters)
        watch_search_events = [e for e in analysis_events if e["source_type"] in ["watch_history", "search_history"]]

        timed_events = []
        for event in watch_search_events:
            try:
                timed_events.append((datetime.strptime(event["event_time"], "%Y-%m-%d %H:%M:%S"), event))
            except Exception:
                continue

        apply_timeline_duration_estimates(timed_events)
        duration_source_counts = count_duration_sources(analysis_events)

        filtered_events = []
        skipped_count = 0

        for event in watch_search_events:
            # Fake dopamine filter only checks watch/view events
            duration_for_filter = event.get("time_delta_sec")
            if duration_for_filter is None:
                duration_for_filter = event.get("estimated_duration_sec")

            if event["action_type"] == "view" and duration_for_filter is not None and duration_for_filter < DURATION_LIMITS["min_watch_sec"]:
                skipped_count += 1
                continue
            filtered_events.append(event)

        # Add playlist/subscription events to final events directly (Auxiliary features)
        aux_events = [e for e in analysis_events if e["source_type"] not in ["watch_history", "search_history"]]
        final_events = filtered_events + aux_events

        if not final_events:
            raise HTTPException(
                status_code=400,
                detail="파싱된 이벤트가 없거나 모든 시청 기록이 생략되었습니다."
            )

        # 5. Save normalized events
        for event in final_events:
            db_client.save_data("norm_event", event)

        # 6. Update raw file status to SUCCESS
        raw_file_entry["upload_status"] = "SUCCESS"
        raw_file_entry["excluded_ad_count"] = len(excluded_ad_events)
        raw_file_entry["skipped_sources_with_reason"] = response_skipped_sources
        raw_file_entry["ad_skip_summary"] = ad_skip_summary
        raw_file_entry["parsed_source_counts"] = parsed_source_counts
        raw_file_entry["analysis_source_counts"] = analysis_source_counts
        raw_file_entry["content_format_counts"] = content_format_counts
        raw_file_entry["duration_source_counts"] = duration_source_counts
        raw_file_entry["data_coverage"] = {
            "parsed_source_counts": parsed_source_counts,
            "analysis_source_counts": analysis_source_counts,
            "skipped_sources_with_reason": response_skipped_sources,
            "excluded_ad_count": len(excluded_ad_events),
            "ad_skip_summary": ad_skip_summary,
            "content_format_counts": content_format_counts,
            "duration_source_counts": duration_source_counts,
        }
        db_client.save_data("raw_file", raw_file_entry)

        # 7. Chronological Time-based and Count-based Multi-session Generator
        session_events = [
            e for e in filtered_events
            if e["action_type"] == "search"
            or (e["action_type"] == "view" and e.get("content_format") == "standard_video")
        ]
        session_events_sorted = sorted(session_events, key=lambda x: x["event_time"])

        sessions_list = []
        current_session = []

        for e in session_events_sorted:
            if not current_session:
                current_session.append(e)
                continue

            try:
                t1 = datetime.strptime(current_session[-1]["event_time"], "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(e["event_time"], "%Y-%m-%d %H:%M:%S")
                gap_hours = abs((t2 - t1).total_seconds()) / 3600.0
            except Exception:
                gap_hours = 0.0

            if gap_hours > 6.0 or len(current_session) >= 100:
                sessions_list.append(current_session)
                current_session = [e]
            else:
                current_session.append(e)

        if current_session:
            sessions_list.append(current_session)

        # Limit the number of generated session entries to 10 for prototype performance
        for idx, sess in enumerate(sessions_list[:10]):
            session_id = str(uuid.uuid4())
            aggregated_titles = " | ".join([e["text_base"] for e in sess[:15]])
            session_text_entry = {
                "id": session_id,
                "file_id": file_id,
                "aggregated_text": aggregated_titles,
                "token_count": len(aggregated_titles.split()),
                "start_time": sess[0]["event_time"],
                "end_time": sess[-1]["event_time"]
            }
            db_client.save_data("session_text", session_text_entry)

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
                "start_time": aux_text_events[0]["event_time"],
                "end_time": aux_text_events[-1]["event_time"]
            }
            db_client.save_data("session_text", aux_session_entry)
            aux_session_count = 1

        return {
            "success": True,
            "file_id": file_id,
            "parsed_source_counts": parsed_source_counts,
            "analysis_source_counts": analysis_source_counts,
            "ignored_sources": ignored_sources[:50], # Limit response size
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
            "duration_source_counts": duration_source_counts
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Takeout upload processing crash: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File upload and parsing failed: {str(e)}")

@router.post("/upload/youtube-takeout")
async def upload_youtube_takeout(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    files: List[UploadFile] = File(default=None),
    paths: List[str] = Form(default=None),
    zip_file: UploadFile = File(default=None)
):
    # Forward deprecated endpoint to new /upload/takeout for backward compatibility
    res = await upload_takeout(user_id=user_id, files=files, paths=paths, zip_file=zip_file)
    return res

@router.get("/youtube-test")
async def test_youtube_api(video_id: str = "dQw4w9WgXcQ"):
    """
    Tests the YouTube Data API connection by fetching metadata for a video.
    """
    from app.core.config import settings
    import httpx

    api_key = settings.YOUTUBE_API_KEY
    if not api_key or api_key == "mock-youtube-api-key":
        logger.error("YouTube API key is missing or not configured.")
        raise HTTPException(
            status_code=400,
            detail="YouTube API Key가 설정되지 않았거나 유효하지 않습니다."
        )

    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails",
            "id": video_id,
            "key": api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)

        if response.status_code != 200:
            logger.error(f"YouTube Data API test failed with HTTP {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YouTube API 호출 실패 (HTTP {response.status_code})"
            )

        data = response.json()
        items = data.get("items", [])
        if not items:
            logger.warning(f"YouTube video {video_id} not found in test API call.")
            return {
                "success": False,
                "message": f"YouTube video ID '{video_id}' not found",
                "data": None
            }

        snippet = items[0].get("snippet", {})
        content_details = items[0].get("contentDetails", {})
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = thumbnails.get("high", {}).get("url", "") or thumbnails.get("default", {}).get("url", "")

        return {
            "success": True,
            "message": "YouTube API connection successful",
            "data": {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "category_id": snippet.get("categoryId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": thumbnail_url,
                "duration_iso8601": content_details.get("duration", ""),
                "duration_sec": parse_iso8601_duration(content_details.get("duration", ""))
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"YouTube Data API connection test crashed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="YouTube API 연결 테스트 중 서버 내부 에러가 발생했습니다."
        )
