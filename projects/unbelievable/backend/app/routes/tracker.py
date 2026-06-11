from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.tracker_service import TrackerService
from app.core.config import DEFAULT_MVP_USER_ID

router = APIRouter()
tracker_service = TrackerService()


class TrackerEventRequest(BaseModel):
    user_id: Optional[str] = DEFAULT_MVP_USER_ID
    action_type: str  # "view" or "search"
    video_id: Optional[str] = None
    video_title: Optional[str] = None
    video_url: Optional[str] = None
    channel_name: Optional[str] = None
    channel_url: Optional[str] = None
    content_format: Optional[str] = "standard_video"
    view_duration_sec: Optional[int] = None
    search_query: Optional[str] = None
    watch_timestamp: Optional[str] = None


@router.post("/tracker/event")
async def collect_tracker_event(req: TrackerEventRequest):
    """
    Endpoint for Chrome Extension tracker to send real-time user viewing/searching activity.
    """
    try:
        user_id = req.user_id or DEFAULT_MVP_USER_ID
        payload = req.dict()
        return tracker_service.process_tracker_event(user_id, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tracker data collection failed: {str(e)}")
