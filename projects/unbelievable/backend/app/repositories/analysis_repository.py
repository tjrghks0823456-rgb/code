from typing import Dict, Any, List
from app.core.database import db_client

class AnalysisRepository:
    """Repository layer isolating DB load/save operations for standard and advanced analysis runs."""
    
    def fetch_norm_events(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("norm_event", {"file_id": file_id})
        
    def fetch_raw_files(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("raw_file", {"id": file_id})
        
    def fetch_sessions(self, file_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("session_text", {"file_id": file_id})
        
    def save_nlp_result(self, nlp_data: Dict[str, Any]) -> Dict[str, Any]:
        return db_client.save_data("nlp_result", nlp_data)
        
    def save_score_run(self, score_run_data: Dict[str, Any]) -> Dict[str, Any]:
        return db_client.save_data("score_run", score_run_data)
        
    def save_score_axes(self, axis_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return db_client.save_many_data("score_axis", axis_entries)
