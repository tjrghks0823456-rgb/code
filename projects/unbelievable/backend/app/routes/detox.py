import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from app.core.content_filters import split_analysis_events
from app.core.database import db_client
from app.core.gemini import gemini_client
from app.core.shorts_analysis import build_shorts_analysis


router = APIRouter()


@router.post("/detox/generate")
async def generate_detox_plan(
    run_id: str,
    user_id: str = "00000000-0000-0000-0000-000000000001",
):
    """Generate reverse queries and missions for the completed score run."""
    try:
        runs = db_client.fetch_data("score_run", {"run_id": run_id})
        if not runs:
            raise HTTPException(status_code=404, detail="Score run not found.")
        run = runs[0]

        axes_list = db_client.fetch_data("score_axis", {"run_id": run_id})
        axis_scores = {axis["axis_code"]: axis["axis_value"] for axis in axes_list}

        events = db_client.fetch_data("norm_event", {"file_id": run.get("file_id")})
        analysis_events, _excluded_ad_events = split_analysis_events(events)
        shorts_analysis = build_shorts_analysis(analysis_events)

        plan_response = gemini_client.generate_detox_plan(
            risk_score=run["bias_risk_score"],
            axis_scores=axis_scores,
            mbti_type=run["mbti_type"],
            dominant_topics=["IT/Tech", "Shorts"],
            shorts_analysis=shorts_analysis,
        )

        plan_id = str(uuid.uuid4())
        plan_entry = {
            "plan_id": plan_id,
            "run_id": run_id,
            "user_id": user_id,
            "reverse_queries": plan_response["reverse_queries"],
            "mission_json": plan_response["missions"],
        }
        db_client.save_data("detox_plan", plan_entry)

        for mission in plan_response["missions"]:
            log_entry = {
                "log_id": str(uuid.uuid4()),
                "plan_id": plan_id,
                "mission_item_id": mission["id"],
                "completed_yn": False,
                "completed_at": None,
            }
            db_client.save_data("mission_log", log_entry)

        return {
            "success": True,
            "plan_id": plan_id,
            "overall_summary": plan_response["overall_summary"],
            "shorts_analysis": shorts_analysis,
            "reverse_queries": plan_response["reverse_queries"],
            "missions": plan_response["missions"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate detox plan: {str(e)}")


@router.get("/detox/plan")
async def get_active_plan(
    plan_id: Optional[str] = None,
    user_id: str = "00000000-0000-0000-0000-000000000001",
):
    """Fetch a detox plan and merge each mission's completion log."""
    try:
        if plan_id:
            plans = db_client.fetch_data("detox_plan", {"plan_id": plan_id})
            if not plans:
                raise HTTPException(status_code=404, detail="Requested detox plan not found.")
            latest_plan = plans[0]
        else:
            plans = db_client.fetch_data("detox_plan", {"user_id": user_id})
            if not plans:
                return {"active": False, "message": "No active detox plan found."}
            latest_plan = plans[-1]

        logs = db_client.fetch_data("mission_log", {"plan_id": latest_plan["plan_id"]})

        missions = []
        for mission in latest_plan["mission_json"]:
            log = next((item for item in logs if item["mission_item_id"] == mission["id"]), None)
            missions.append(
                {
                    **mission,
                    "completed": log["completed_yn"] if log else False,
                    "completed_at": log["completed_at"] if log else None,
                    "log_id": log["log_id"] if log else None,
                }
            )

        return {
            "active": True,
            "plan_id": latest_plan["plan_id"],
            "reverse_queries": latest_plan["reverse_queries"],
            "missions": missions,
        }
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
        logs = db_client.fetch_data("mission_log", {"log_id": log_id})
        if not logs:
            raise HTTPException(status_code=404, detail="Mission log not found.")

        log = logs[0]
        log["completed_yn"] = completed
        log["completed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if completed else None
        db_client.save_data("mission_log", log)

        return {
            "success": True,
            "log_id": log_id,
            "completed": completed,
            "completed_at": log["completed_at"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update mission status: {str(e)}")
