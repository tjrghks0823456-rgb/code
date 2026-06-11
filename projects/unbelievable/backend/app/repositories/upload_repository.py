from typing import Dict, Any, List
from app.core.database import db_client

class UploadRepository:
    """Repository layer for upload metadata and records to isolate direct DatabaseClient PostgREST calls."""
    
    def save_raw_file(self, raw_file_data: Dict[str, Any]) -> Dict[str, Any]:
        return db_client.save_data("raw_file", raw_file_data)
        
    def save_norm_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return db_client.save_many_data("norm_event", events)
        
    def save_session_texts(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return db_client.save_many_data("session_text", sessions)
        
    def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        return db_client.save_data("profiles", profile_data)
        
    def fetch_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("profiles", {"id": user_id})
        
    @property
    def is_mock(self) -> bool:
        return db_client.is_mock
