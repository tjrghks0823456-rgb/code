import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Body
from app.core.database import db_client
from app.core.gemini import gemini_client

router = APIRouter()

@router.post("/detox/generate")
async def generate_detox_plan(
    run_id: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
):
    """
    Triggers Gemini 2.5 Flash to generate custom Reverse Queries and Detox Missions.
    Presents them as checklist items in mission_log.
    """
    try:
        # 1. Fetch score runs and axes
        runs = db_client.fetch_data("score_run", {"run_id": run_id})
        if not runs:
            raise HTTPException(status_code=404, detail="Score run not found.")
        run = runs[0]
        
        axes_list = db_client.fetch_data("score_axis", {"run_id": run_id})
        axis_scores = {a["axis_code"]: a["axis_value"] for a in axes_list}
        
        # 2. Call Gemini client to generate plan
        # We pass dominant topics: let's mock dominant topics as ['IT/Tech', 'Shorts/Humor']
        plan_response = gemini_client.generate_detox_plan(
            risk_score=run["bias_risk_score"],
            axis_scores=axis_scores,
            mbti_type=run["mbti_type"],
            dominant_topics=["IT/기술", "유머/쇼츠"]
        )
        
        # 3. Save to public.detox_plan
        plan_id = str(uuid.uuid4())
        plan_entry = {
            "plan_id": plan_id,
            "run_id": run_id,
            "user_id": user_id,
            "reverse_queries": plan_response["reverse_queries"],
            "mission_json": plan_response["missions"]
        }
        db_client.save_data("detox_plan", plan_entry)
        
        # 4. Populate public.mission_log for each mission
        for m in plan_response["missions"]:
            log_id = str(uuid.uuid4())
            log_entry = {
                "log_id": log_id,
                "plan_id": plan_id,
                "mission_item_id": m["id"],
                "completed_yn": False,
                "completed_at": None
            }
            db_client.save_data("mission_log", log_entry)
            
        return {
            "success": True,
            "plan_id": plan_id,
            "overall_summary": plan_response["overall_summary"],
            "reverse_queries": plan_response["reverse_queries"],
            "missions": plan_response["missions"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate detox plan: {str(e)}")

@router.get("/detox/plan")
async def get_active_plan(
    plan_id: Optional[str] = None,
    user_id: str = "00000000-0000-0000-0000-000000000001"
):
    """Fetches the detox plan and its logs by plan_id or gets the latest for a user."""
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
            latest_plan = plans[-1] # Primary active plan
            
        logs = db_client.fetch_data("mission_log", {"plan_id": latest_plan["plan_id"]})
        
        # Merge completed status into missions
        missions = []
        for m in latest_plan["mission_json"]:
            log = next((l for l in logs if l["mission_item_id"] == m["id"]), None)
            missions.append({
                **m,
                "completed": log["completed_yn"] if log else False,
                "completed_at": log["completed_at"] if log else None,
                "log_id": log["log_id"] if log else None
            })
            
        return {
            "active": True,
            "plan_id": latest_plan["plan_id"],
            "reverse_queries": latest_plan["reverse_queries"],
            "missions": missions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve detox plan: {str(e)}")

@router.patch("/detox/mission/{log_id}")
async def update_mission_status(
    log_id: str,
    completed: bool = Body(..., embed=True)
):
    """Updates the completion status of a specific mission log."""
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
            "completed_at": log["completed_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update mission status: {str(e)}")
