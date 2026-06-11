import logging
from typing import Any, List
from fastapi import APIRouter, HTTPException
from app.core.config import DEFAULT_MVP_USER_ID
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)
router = APIRouter()

dashboard_service = DashboardService()


def normalize_exception_codes(raw_codes: Any) -> List[str]:
    """Expose legacy helper for backward compatibility (e.g. imports from detox router)"""
    return dashboard_service.normalize_exception_codes(raw_codes)


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    run_id: str,
    user_id: str = DEFAULT_MVP_USER_ID
):
    """
    Returns dashboard overview details:
    1. Risk score, MBTI type details.
    2. 6-axis actual scores.
    3. 'Meta-gap' (error comparison between profile survey hypothesis and actual analysis scores).
    4. Identifies the largest cognitive bias axis (착각 지수).
    """
    try:
        return dashboard_service.get_dashboard_summary(run_id, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard rendering failed: {str(e)}")
