from typing import Any, Dict, List, Optional
from app.core.database import db_client


class TrackerRepository:
    def save_norm_event(self, event_data: Dict[str, Any]) -> None:
        db_client.save_data("norm_event", event_data)

    def fetch_latest_session(self, user_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        # Fetch sessions for the specific file_id, sorted to find the latest
        sessions = db_client.fetch_data("session_text", {"file_id": file_id})
        if not sessions:
            return None
        # Sort by end_time or start_time descending
        sessions_sorted = sorted(sessions, key=lambda s: s.get("end_time", ""), reverse=True)
        return sessions_sorted[0]

    def save_session_text(self, session_data: Dict[str, Any]) -> None:
        db_client.save_data("session_text", session_data)

    def update_session_text(self, session_id: str, aggregated_text: str, token_count: int, end_time: str) -> None:
        # Fetch the session, modify, and save
        sessions = db_client.fetch_data("session_text", {"id": session_id})
        if sessions:
            session = sessions[0]
            session["aggregated_text"] = aggregated_text
            session["token_count"] = token_count
            session["end_time"] = end_time
            db_client.save_data("session_text", session)

    def fetch_latest_score_run(self, user_id: str) -> Optional[Dict[str, Any]]:
        runs = db_client.fetch_data("score_run", {"user_id": user_id})
        if not runs:
            return None
        runs_sorted = sorted(runs, key=lambda r: r.get("created_at", ""), reverse=True)
        return runs_sorted[0]
