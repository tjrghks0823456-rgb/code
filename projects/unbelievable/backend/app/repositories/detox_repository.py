from typing import Any, Dict, List
from app.core.database import db_client


class DetoxRepository:
    def fetch_score_run(self, run_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("score_run", {"run_id": run_id})

    def fetch_score_axes(self, run_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("score_axis", {"run_id": run_id})

    def fetch_norm_events(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("norm_event", {"file_id": file_id})

    def fetch_session_texts(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("session_text", {"file_id": file_id})

    def fetch_nlp_results_by_session_ids(self, session_ids: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for sid in session_ids:
            results.extend(db_client.fetch_data("nlp_result", {"session_id": sid}))
        return results

    def save_detox_plan(self, plan_entry: Dict[str, Any]) -> None:
        db_client.save_data("detox_plan", plan_entry)

    def save_mission_log(self, log_entry: Dict[str, Any]) -> None:
        db_client.save_data("mission_log", log_entry)

    def fetch_detox_plan_by_id(self, plan_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("detox_plan", {"plan_id": plan_id})

    def fetch_detox_plans_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("detox_plan", {"user_id": user_id})

    def fetch_mission_logs_by_plan_id(self, plan_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("mission_log", {"plan_id": plan_id})

    def fetch_mission_log_by_id(self, log_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("mission_log", {"log_id": log_id})
