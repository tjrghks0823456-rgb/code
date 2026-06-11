from typing import Optional
from fastapi import APIRouter, Body, HTTPException
from app.core.config import DEFAULT_MVP_USER_ID
from app.services.detox_service import DetoxService

router = APIRouter()
detox_service = DetoxService()


@router.post("/detox/generate")
async def generate_detox_plan(
    run_id: str,
    user_id: str = DEFAULT_MVP_USER_ID,
):
    """Generate reverse queries and missions for the completed score run."""
    try:
        return detox_service.generate_detox_plan(run_id, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate detox plan: {str(e)}")


@router.get("/detox/plan")
async def get_active_plan(
    plan_id: Optional[str] = None,
    user_id: str = DEFAULT_MVP_USER_ID,
):
    """Fetch a detox plan and merge each mission's completion log."""
    try:
        return detox_service.get_active_plan(plan_id, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve detox plan: {str(e)}")


@router.patch("/detox/mission/{log_id}")
async def update_mission_status(
    log_id: str,
    completed: bool = Body(..., embed=True),
):
    """Update the completion status for one mission log."""
    try:
        return detox_service.update_mission_status(log_id, completed)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update mission status: {str(e)}")
