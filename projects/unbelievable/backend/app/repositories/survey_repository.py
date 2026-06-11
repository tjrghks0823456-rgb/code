from typing import Any, Dict, List
from app.core.database import db_client


class SurveyRepository:
    def fetch_profile(self, user_id: str) -> List[Dict[str, Any]]:
        return db_client.fetch_data("profiles", {"id": user_id})

    def save_profile(self, profile_data: Dict[str, Any]) -> None:
        db_client.save_data("profiles", profile_data)
