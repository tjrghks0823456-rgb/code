import logging
from fastapi import APIRouter, HTTPException
from app.core.config import DEFAULT_MVP_USER_ID
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)
router = APIRouter()
analysis_service = AnalysisService()


@router.post("/analysis/run")
async def run_analysis(
    file_id: str,
    user_id: str = DEFAULT_MVP_USER_ID
):
    """
    Triggers the quantitative and qualitative analysis pipelines.
    Delegates all scoring calculations to AnalysisService.
    """
    try:
        logger.info(f"[analysis/run] started file_id={file_id}")
        res = analysis_service.run_scoring_pipeline(file_id=file_id, user_id=user_id)
        return res
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis calculation failed: {str(e)}")
