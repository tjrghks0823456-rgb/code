import logging
from fastapi import APIRouter, HTTPException
from app.core.database import db_client
from app.core.scoring import PERSONALITY_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    run_id: str,
    user_id: str = "test-user-id"
):
    """
    Returns dashboard overview details:
    1. Risk score, MBTI type details.
    2. 6-axis actual scores.
    3. 'Meta-gap' (error comparison between profile survey hypothesis and actual analysis scores).
    4. Identifies the largest cognitive bias axis (착각 지수).
    """
    try:
        # 1. Fetch score run
        runs = db_client.fetch_data("score_run", {"run_id": run_id})
        if not runs:
            raise HTTPException(status_code=404, detail="Analysis result not found.")
        run = runs[0]
        
        # 2. Fetch axes scores
        axes = db_client.fetch_data("score_axis", {"run_id": run_id})
        axis_scores = {a["axis_code"]: a["axis_value"] for a in axes}
        
        # 3. Fetch user profile survey scores (for meta-gap calculation)
        profiles = db_client.fetch_data("profiles", {"id": user_id})
        if not profiles:
            raise HTTPException(status_code=404, detail="User profile not found.")
        profile = profiles[0]
        survey_scores = profile.get("survey_scores", {})
        
        # 4. Calculate Meta-gap (FEAT_16)
        # Gap = Survey Score (subjective) - Actual Score (objective)
        meta_gap = {}
        max_gap_axis = "TDS"
        max_gap_value = -1.0
        
        # Axis name mapping
        axis_names = {
            "TDS": "주제 다양성",
            "SBS": "출처 균형",
            "EBS": "감정 균형",
            "VOS": "관점 개방성",
            "SMS": "유해/자극 안전",
            "UAS": "사용자 주도성"
        }
        
        for code, name in axis_names.items():
            s_val = float(survey_scores.get(code, 50.0))
            a_val = float(axis_scores.get(code, 50.0))
            gap = abs(s_val - a_val)
            meta_gap[code] = {
                "name": name,
                "survey": s_val,
                "actual": a_val,
                "gap": round(s_val - a_val, 1) # Positive means overestimated, Negative means underestimated
            }
            if gap > max_gap_value:
                max_gap_value = gap
                max_gap_axis = code
                
        # Calculate overall "Misconception Index" (착각 지수)
        # Average of absolute gaps across all 6 axes
        avg_gap = sum(abs(item["gap"]) for item in meta_gap.values()) / len(meta_gap)
        misconception_index = round(avg_gap * 1.5, 1) # scale slightly for visual impact
        misconception_index = min(100.0, misconception_index)
        
        # Find MBTI descriptions
        # MBTI type code is stored as 4 characters, e.g., "HHHH"
        mbti_code = run["mbti_type"]
        key = tuple(mbti_code[i] for i in range(4)) if len(mbti_code) == 4 else ("H", "H", "H", "H")
        mbti_details = PERSONALITY_MAP.get(key, ("미지의 미디어 관찰자", ["#분석대기", "#신규성향"]))
        
        return {
            "run_id": run_id,
            "user": {
                "nickname": profile["nickname"],
                "email": profile["email"]
            },
            "bias_risk_score": run["bias_risk_score"],
            "weighted_health": run["weighted_health"],
            "mbti": {
                "code": mbti_code,
                "name": mbti_details[0],
                "tags": mbti_details[1]
            },
            "exception_codes": run.get("exception_codes", []),
            "meta_gap": meta_gap,
            "misconception": {
                "index": misconception_index,
                "worst_axis_code": max_gap_axis,
                "worst_axis_name": axis_names[max_gap_axis],
                "worst_gap_value": round(meta_gap[max_gap_axis]["gap"], 1),
                "message": f"주관적으로 인지하는 것보다 실제 데이터상으로 '{axis_names[max_gap_axis]}' 영역의 편향이 가장 큽니다. 거울 치료와 의도적 디톡스가 절실히 요구됩니다."
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard rendering failed: {str(e)}")
