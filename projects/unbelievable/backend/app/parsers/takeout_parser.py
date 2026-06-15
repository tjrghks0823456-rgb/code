import uuid
import json
import logging
import re
import zipfile
import urllib.parse
import csv
from io import BytesIO, StringIO
from datetime import datetime
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

from app.core.content_filters import (
    build_ad_skip_summary,
    detect_ad_event_reason,
    detect_content_format,
    extract_search_query,
    is_google_ad_event,
)
from app.core.youtube import parse_iso8601_duration, youtube_client
from app.core.upload_config import DURATION_LIMITS, PARSER_LIMITS, ZIP_LIMITS
from app.core.config import settings

logger = logging.getLogger(__name__)

SEARCH_DONE_MARKERS = (
    "searched for",
    "you searched for",
    "\uac80\uc0c9\ud588\uc2b5\ub2c8\ub2e4",
)

YOUTUBE_SEARCH_LINK_RE = re.compile(
    r"<a\s+[^>]*href=[\"']([^\"']*youtube\.com/results\?[^\"']*)[\"'][^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)

MAX_ZIP_FILE_COUNT = ZIP_LIMITS["max_file_count"]
MAX_SINGLE_FILE_SIZE = ZIP_LIMITS["max_single_file_size"]
MAX_TOTAL_EXTRACT_SIZE = ZIP_LIMITS["max_total_extract_size"]


def extract_video_id(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        if "/shorts/" in parsed.path:
            parts = [p for p in parsed.path.split("/") if p]
            if "shorts" in parts:
                idx = parts.index("shorts")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
                    
        if "youtube.com" in parsed.netloc or "music.youtube" in parsed.netloc:
            query = urllib.parse.parse_qs(parsed.query)
            v = query.get("v")
            if v:
                return v[0]
            parts = [p for p in parsed.path.split("/") if p]
            if "watch" in parts:
                idx = parts.index("watch")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        elif "youtu.be" in parsed.netloc:
            parts = [p for p in parsed.path.split("/") if p]
            if parts:
                return parts[0]
    except Exception:
        pass
    return None


def classify_content_format(item: Dict[str, Any]) -> str:
    url = (
        item.get("title_url")
        or item.get("titleUrl")
        or item.get("url")
        or item.get("URL")
    )
    title = item.get("title_text") or item.get("text_base") or item.get("title") or ""
    return detect_content_format(url=url or "", title=title, raw_item=item)


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

    # 1. Try dateparser dynamically if available (supports multilingual formats)
    try:
        import dateparser
        parsed_dt = dateparser.parse(timestamp_str)
        if parsed_dt:
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ImportError:
        pass
    except Exception:
        pass

    # 2. Try python-dateutil standard parser (already installed)
    try:
        import dateutil.parser
        parsed_dt = dateutil.parser.parse(timestamp_str)
        if parsed_dt:
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

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


def extract_search_query_from_href(href: str, fallback_text: str = "") -> Optional[str]:
    normalized_href = (href or "").replace("&amp;", "&")
    if not normalized_href:
        return None

    try:
        parsed = urllib.parse.urlparse(normalized_href)
        params = urllib.parse.parse_qs(parsed.query)
        query_value = (params.get("search_query") or [""])[0]
        if not query_value and "youtube.com" in parsed.netloc and parsed.path.rstrip("/") == "/results":
            query_value = (params.get("q") or [""])[0]
        query_text = urllib.parse.unquote_plus(query_value) or fallback_text
        return extract_search_query(
            {
                "query": query_text,
                "action_type": "search",
                "source_type": "search_history",
                "intent_level": "active_search",
            }
        )
    except Exception:
        return None


def extract_html_search_query(cell, raw_text: str) -> Optional[str]:
    lines = [line.strip() for line in cell.stripped_strings if line.strip()]
    for idx, line in enumerate(lines):
        lower_line = line.lower()
        if lower_line.startswith(("searched for ", "you searched for ", "\uac80\uc0c9\uc5b4:", "\uac80\uc0c9:")):
            query = extract_search_query(
                {
                    "title": line,
                    "action_type": "search",
                    "source_type": "search_history",
                    "intent_level": "active_search",
                }
            )
            if query:
                return query
        if lower_line in {"searched for", "you searched for", "\uac80\uc0c9", "\uac80\uc0c9\ud568"} and idx + 1 < len(lines):
            query = extract_search_query(
                {
                    "title": f"Searched for {lines[idx + 1]}",
                    "action_type": "search",
                    "source_type": "search_history",
                    "intent_level": "active_search",
                }
            )
            if query:
                return query
 
    for link in cell.find_all("a"):
        query = extract_search_query_from_href(link.get("href", ""), link.get_text().strip())
        if query:
            return query

    return None


def extract_timestamp_from_html_fragment(fragment: str) -> Optional[str]:
    text = BeautifulSoup(fragment, "html.parser").get_text("\n")
    for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
        parsed_time = parse_takeout_html_timestamp(line)
        if parsed_time:
            return line
    return None


def parse_youtube_search_html(html_content: str) -> List[dict]:
    parsed_items = []

    for match in YOUTUBE_SEARCH_LINK_RE.finditer(html_content):
        if len(parsed_items) >= PARSER_LIMITS["max_html_links"]:
            break

        tail_text = BeautifulSoup(html_content[match.end():match.end() + 220], "html.parser").get_text(" ")
        if not any(marker in tail_text.lower() for marker in SEARCH_DONE_MARKERS):
            continue

        link_text = BeautifulSoup(match.group(2), "html.parser").get_text(" ").strip()
        search_query = extract_search_query_from_href(match.group(1), link_text)
        if not search_query:
            continue

        fragment_start = html_content.rfind('<div class="outer-cell', 0, match.start())
        if fragment_start == -1:
            fragment_start = max(0, match.start() - 500)
        fragment_end = html_content.find('<div class="outer-cell', match.end())
        if fragment_end == -1 or fragment_end - fragment_start > 5000:
            fragment_end = min(len(html_content), match.end() + 1200)
        fragment = html_content[fragment_start:fragment_end]
        
        raw_ts = extract_timestamp_from_html_fragment(fragment)
        parsed_time_str = parse_takeout_html_timestamp(raw_ts) if raw_ts else None
        timestamp_parse_failed = parsed_time_str is None

        parsed_item = {
            "title_text": search_query,
            "action_type": "search",
            "event_time": parsed_time_str,
            "raw_time": raw_ts,
            "raw_timestamp": raw_ts,
            "timestamp_parse_failed": timestamp_parse_failed,
            "timestamp_parse_status": "failed" if timestamp_parse_failed else "parsed",
            "video_id": None,
            "title_url": None,
            "channel_name": None,
            "channel_url": None,
            "content_format": "unknown",
            "intent_level": "active_search",
            "search_query": search_query,
            "time": raw_ts
        }
        is_ad, ad_reason = is_google_ad_event(parsed_item, raw_text=fragment)
        if ad_reason:
            parsed_item["is_ad_event"] = True
            parsed_item["ad_filter_reason"] = ad_reason
        parsed_items.append(parsed_item)

    return parsed_items


def parse_youtube_html(html_content: str, file_kind: str) -> List[dict]:
    if file_kind == "search":
        search_items = parse_youtube_search_html(html_content)
        if search_items or "youtube.com/results?search_query=" in html_content:
            return search_items

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
        html_search_query = None

        a_tags = cell.find_all("a")

        if file_kind == "search":
            action_type = "search"
            html_search_query = extract_html_search_query(cell, text)
            if html_search_query:
                title_text = html_search_query
                video_id = None
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
            html_search_query = extract_html_search_query(cell, text)
            if html_search_query:
                title_text = html_search_query
                video_id = None

        if not title_text:
            if text.startswith("Watched "):
                title_text = text[len("Watched "):].split("\n")[0].strip()
                action_type = "view"
            elif text.startswith("Searched for "):
                html_search_query = extract_html_search_query(cell, text)
                title_text = html_search_query or ""
                action_type = "search"

        lines = [line.strip() for line in cell.stripped_strings if line.strip()]
        timestamp_str = ""
        if len(lines) >= 3:
            timestamp_str = lines[-1]
        elif len(lines) == 2:
            timestamp_str = lines[-1]

        parsed_time_str = parse_takeout_html_timestamp(timestamp_str) if timestamp_str else None
        timestamp_parse_failed = parsed_time_str is None

        parsed_item = {
            "title_text": title_text or "알 수 없는 비디오",
            "action_type": action_type,
            "event_time": parsed_time_str,
            "raw_time": timestamp_str,
            "raw_timestamp": timestamp_str,
            "timestamp_parse_failed": timestamp_parse_failed,
            "timestamp_parse_status": "failed" if timestamp_parse_failed else "parsed",
            "video_id": video_id,
            "title_url": None if action_type == "search" else (a_tags[0].get("href", "") if len(a_tags) >= 1 else None),
            "channel_name": channel_name,
            "channel_url": channel_url,
            "time": timestamp_str
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = "active_search" if action_type == "search" else "unknown"
        is_ad, ad_reason = is_google_ad_event(parsed_item, raw_text=text)
        search_query = html_search_query if action_type == "search" else None
        if action_type == "search" and search_query:
            parsed_item["search_query"] = search_query
            parsed_item["title_text"] = search_query
            parsed_item["video_id"] = None
            parsed_item["content_format"] = "unknown"
        elif action_type == "search" and not is_ad:
            continue

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

        title_url = item.get("titleUrl", "")
        video_id = extract_video_id(title_url)

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

        timestamp_parse_failed = parsed_time_str is None

        parsed_item = {
            "title_text": title_text,
            "action_type": action_type,
            "event_time": parsed_time_str,
            "raw_time": item_time,
            "raw_timestamp": item_time,
            "timestamp_parse_failed": timestamp_parse_failed,
            "timestamp_parse_status": "failed" if timestamp_parse_failed else "parsed",
            "video_id": video_id,
            "title_url": title_url,
            "channel_name": channel_name,
            "channel_url": channel_url,
            "time": item_time
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = "active_search" if action_type == "search" else "unknown"
        is_ad, ad_reason = is_google_ad_event({**item, **parsed_item})
        search_query = extract_search_query({**item, **parsed_item}) if action_type == "search" else None
        if action_type == "search" and search_query:
            parsed_item["search_query"] = search_query
            parsed_item["title_text"] = search_query
            parsed_item["video_id"] = None
            parsed_item["content_format"] = "unknown"
        elif action_type == "search" and not is_ad:
            continue

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
                    "event_time": None,
                    "raw_time": "",
                    "raw_timestamp": "",
                    "timestamp_parse_failed": True,
                    "timestamp_parse_status": "missing",
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

    def append_item(
        title: str,
        url: Optional[str] = None,
        channel_name: Optional[str] = None,
        event_time: Optional[str] = None,
        raw_time: Optional[str] = None,
    ):
        clean_title = (title or "").strip()
        clean_url = (url or "").strip()
        clean_raw_time = (raw_time or "").strip()
        if not clean_title and clean_url:
            clean_title = clean_url
        if not clean_title:
            return
        timestamp_parse_failed = event_time is None
        parsed_item = {
            "title_text": clean_title[:500],
            "action_type": action_type,
            "event_time": event_time,
            "raw_time": clean_raw_time,
            "raw_timestamp": clean_raw_time,
            "timestamp_parse_failed": timestamp_parse_failed,
            "timestamp_parse_status": "missing" if not clean_raw_time else ("failed" if timestamp_parse_failed else "parsed"),
            "title_url": clean_url or None,
            "video_id": extract_video_id(clean_url),
            "channel_name": channel_name or clean_title,
            "channel_url": clean_url or None
        }
        parsed_item["content_format"] = classify_content_format(parsed_item)
        parsed_item["intent_level"] = "active_search" if action_type == "search" else "unknown"
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
                event_time = parse_takeout_html_timestamp(raw_time)
            append_item(title, url, channel_name, event_time, raw_time)
    except Exception:
        pass

    if parsed_items:
        return parsed_items

    try:
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a")[:PARSER_LIMITS["max_html_links"]]:
            append_item(link.get_text().strip(), link.get("href", ""), raw_time="")
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
                event_time = parse_takeout_html_timestamp(raw_time) if raw_time else None
                append_item(title, url, channel_name, event_time, raw_time)
        else:
            csv_text.seek(0)
            for row in list(csv.reader(csv_text))[:PARSER_LIMITS["max_csv_rows"]]:
                values = [cell.strip() for cell in row if cell.strip()]
                if values:
                    append_item(" | ".join(values[:3]))
    except Exception:
        pass

    return parsed_items


class TakeoutParser:
    """Object-oriented parser class for handling refined Google Takeout structure and format identification."""
    
    @staticmethod
    def identify_and_parse(file_info: Dict[str, Any]) -> List[dict]:
        name = file_info["name"]
        content = file_info["content"]
        kind = file_info["kind"]
        
        is_json = name.lower().endswith(".json")
        items = []
        
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
            
        return items
