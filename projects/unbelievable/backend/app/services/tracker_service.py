import uuid
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.repositories.tracker_repository import TrackerRepository

logger = logging.getLogger(__name__)


class TrackerService:
    def __init__(self, repository: Optional[TrackerRepository] = None):
        self.repository = repository or TrackerRepository()

    def process_tracker_event(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes real-time view/search event from Chrome Extension.
        Saves normalized event and consolidates text sessions (5-minute inactivity threshold).
        """
        # 1. Resolve or create active file_id for real-time tracking
        latest_run = self.repository.fetch_latest_score_run(user_id)
        if latest_run and latest_run.get("file_id"):
            file_id = latest_run["file_id"]
        else:
            # Generate a stable virtual file_id for tracking if no run exists
            file_id = f"rt-{user_id[:8]}"

        action_type = payload.get("action_type", "view")
        event_time_str = payload.get("watch_timestamp")
        if not event_time_str:
            event_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Normalize event object mapping to DB norm_event schema
        event_id = str(uuid.uuid4())
        text_base = ""
        channel_name = payload.get("channel_name", "")
        content_format = "standard_video"
        time_delta_sec = payload.get("view_duration_sec")

        if action_type == "search":
            search_query = payload.get("search_query", "").strip()
            text_base = f"Searched for: {search_query}" if search_query else "empty search"
        else:
            video_title = payload.get("video_title", "").strip()
            text_base = video_title
            # Simple heuristic for Shorts detection in real-time tracker
            if payload.get("content_format") == "shorts" or "youtube.com/shorts" in payload.get("video_url", ""):
                content_format = "shorts"

        norm_event = {
            "id": event_id,
            "file_id": file_id,
            "action_type": action_type,
            "content_format": content_format,
            "text_base": text_base,
            "channel_name": channel_name,
            "channel_url": payload.get("channel_url", ""),
            "event_time": event_time_str,
            "time_delta_sec": time_delta_sec,
            "source_surface": "chrome_extension_tracker",
            "author_id": channel_name,
        }

        # Save to DB
        self.repository.save_norm_event(norm_event)
        logger.info(f"[TrackerService] saved norm_event id={event_id} type={action_type}")

        # 3. Real-time Session Consolidation (5-min sliding window)
        new_session_segment = f"{action_type.upper()}: {text_base}"
        if channel_name:
            new_session_segment += f" (Channel: {channel_name})"

        latest_session = self.repository.fetch_latest_session(user_id, file_id)
        consolidated = False

        if latest_session:
            # Check duration gap between latest session end_time and current event_time
            try:
                latest_end = datetime.strptime(latest_session["end_time"], "%Y-%m-%d %H:%M:%S")
                current_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M:%S")
                time_gap = (current_time - latest_end).total_seconds()
            except Exception:
                time_gap = 999.0  # Force new session on timestamp parsing error

            # If gap is under 5 minutes, append to the existing session
            if 0 <= time_gap <= 300.0:
                old_text = latest_session.get("aggregated_text", "")
                # Avoid duplicates if extension sends multiple pings for same video
                if new_session_segment not in old_text:
                    new_text = f"{old_text} | {new_session_segment}"
                    token_estimate = len(new_text) // 2
                    self.repository.update_session_text(
                        session_id=latest_session["id"],
                        aggregated_text=new_text,
                        token_count=token_estimate,
                        end_time=event_time_str
                    )
                    logger.info(f"[TrackerService] updated existing session {latest_session['id']}")
                consolidated = True

        if not consolidated:
            # Create a brand new session
            session_id = str(uuid.uuid4())
            new_session = {
                "id": session_id,
                "file_id": file_id,
                "start_time": event_time_str,
                "end_time": event_time_str,
                "aggregated_text": new_session_segment,
                "token_count": len(new_session_segment) // 2
            }
            self.repository.save_session_text(new_session)
            logger.info(f"[TrackerService] created new session {session_id}")

        return {
            "success": True,
            "event_id": event_id,
            "file_id": file_id,
            "action_type": action_type,
            "session_consolidated": consolidated
        }
