from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.core.database import db_client
from app.core.survey_scoring import convert_8axis_to_6axis

router = APIRouter()

class SurveySaveRequest(BaseModel):
    user_id: str
    survey_scores: Dict[str, float]
    result_code: str
    result_name: str
    schema_version: Optional[str] = "1.0.0"

@router.post("/survey/save")
async def save_survey(req: SurveySaveRequest):
    try:
        user_id = req.user_id
        # 1. Fetch existing profile to preserve nickname, email etc.
        profiles = db_client.fetch_data("profiles", {"id": user_id})
        
        if profiles:
            profile = profiles[0]
        else:
            profile = {
                "id": user_id,
                "email": "user@example.com",
                "nickname": "사용자"
            }
        
        # 2. Convert 8-axis to 6-axis
        six_axis_scores = convert_8axis_to_6axis(req.survey_scores)
        
        # 3. Update profile data
        # Store only valid float values. EBS/SBS will be excluded (not mapped to 50)
        profile["survey_scores"] = {k: v for k, v in six_axis_scores.items() if v is not None}
        profile["raw_survey"] = {
            "survey_scores": req.survey_scores,
            "result_code": req.result_code,
            "result_name": req.result_name,
            "schema_version": req.schema_version
        }
        
        # 4. Save profile
        db_client.save_data("profiles", profile)
        
        return {
            "success": True,
            "message": "Survey result saved successfully.",
            "converted_scores": six_axis_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save survey: {str(e)}")
