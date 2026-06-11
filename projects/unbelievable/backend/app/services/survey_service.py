from typing import Any, Dict, Optional
from app.core.survey_scoring import convert_8axis_to_6axis
from app.repositories.survey_repository import SurveyRepository


class SurveyService:
    def __init__(self, repository: Optional[SurveyRepository] = None):
        self.repository = repository or SurveyRepository()

    def save_survey(
        self,
        user_id: str,
        survey_scores: Dict[str, float],
        result_code: str,
        result_name: str,
        schema_version: Optional[str] = "1.0.0",
    ) -> Dict[str, Any]:
        # 1. Fetch existing profile to preserve nickname, email etc.
        profiles = self.repository.fetch_profile(user_id)

        if profiles:
            profile = profiles[0]
        else:
            profile = {
                "id": user_id,
                "email": "user@example.com",
                "nickname": "사용자"
            }

        # 2. Convert 8-axis to 6-axis
        six_axis_scores = convert_8axis_to_6axis(survey_scores)

        # 3. Update profile data
        profile["survey_scores"] = {k: v for k, v in six_axis_scores.items() if v is not None}
        profile["raw_survey"] = {
            "survey_scores": survey_scores,
            "result_code": result_code,
            "result_name": result_name,
            "schema_version": schema_version
        }

        # 4. Save profile
        self.repository.save_profile(profile)

        return {
            "success": True,
            "message": "Survey result saved successfully.",
            "converted_scores": six_axis_scores
        }
