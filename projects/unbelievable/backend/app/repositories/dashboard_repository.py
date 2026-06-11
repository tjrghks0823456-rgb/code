from typing import Any, Dict, List
from app.core.database import db_client


class DashboardRepository:
    def fetch_score_run(self, run_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("score_run", {"run_id": run_id})

    def fetch_score_axes(self, run_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("score_axis", {"run_id": run_id})

    def fetch_user_profile(self, user_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("profiles", {"id": user_id})

    def fetch_raw_file(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("raw_file", {"id": file_id})

    def fetch_norm_events(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("norm_event", {"file_id": file_id})

    def fetch_nlp_results_for_file(self, file_id: str) -> List[Dict[str, Any]]:
        sessions = db_client.fetch_data("session_text", {"file_id": file_id})
        results: List[Dict[str, Any]] = []
        for session in sessions:
            session_id = session.get("id")
            if not session_id:
                continue
            results.extend(db_client.fetch_data("nlp_result", {"session_id": session_id}))
        return results
