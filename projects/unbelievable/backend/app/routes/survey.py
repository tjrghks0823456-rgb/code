from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.survey_service import SurveyService

router = APIRouter()
survey_service = SurveyService()


class SurveySaveRequest(BaseModel):
    user_id: str
    survey_scores: Dict[str, float]
    result_code: str
    result_name: str
    schema_version: Optional[str] = "1.0.0"


@router.post("/survey/save")
async def save_survey(req: SurveySaveRequest):
    try:
        return survey_service.save_survey(
            user_id=req.user_id,
            survey_scores=req.survey_scores,
            result_code=req.result_code,
            result_name=req.result_name,
            schema_version=req.schema_version,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save survey: {str(e)}")
