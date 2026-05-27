import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.core.database import db_client
from app.core.nlp import nlp_client
from app.core.scoring import compute_6axis_scores, classify_16_type

router = APIRouter()

@router.post("/analysis/run")
async def run_analysis(
    file_id: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
):
    """
    Triggers the quantitative and qualitative analysis pipelines.
    1. Annotates merged session texts with Google Cloud Natural Language API.
    2. Stores NLP JSONB results in database.
    3. Calculates 6-axis scores and 16-type media personality.
    4. Saves final analysis in score_run and score_axis.
    """
    try:
        # 1. Fetch sessions for the file
        sessions = db_client.fetch_data("session_text", {"file_id": file_id})
        if not sessions:
            raise HTTPException(status_code=404, detail="No session text found for this file. Please upload a valid history file.")
            
        session = sessions[0] # Analyze the primary session for the prototype
        
        # 2. Annotate text with NLP client
        nlp_response = nlp_client.analyze_text(session["aggregated_text"])
        
        # 3. Save NLP results to public.nlp_result
        nlp_result_id = str(uuid.uuid4())
        nlp_entry = {
            "id": nlp_result_id,
            "session_id": session["id"],
            "categories_json": nlp_response["categories_json"],
            "sentiment_score": nlp_response["documentSentiment"]["score"],
            "sentiment_magnitude": nlp_response["documentSentiment"]["magnitude"],
            "language_code": nlp_response["language_code"]
        }
        db_client.save_data("nlp_result", nlp_entry)
        
        # 4. Fetch all normalized events for scoring
        events = db_client.fetch_data("norm_event", {"file_id": file_id})
        
        # 5. Compute 6-axis scores using deterministic python scoring engine (FEAT_06)
        # We pass the events and the newly saved nlp_entry
        axis_scores, exception_codes = compute_6axis_scores(events, [nlp_entry])
        
        # 6. Classify into one of 16 types (FEAT_08)
        type_code, type_name, tags = classify_16_type(axis_scores)
        
        # Calculate Weighted Health & Bias Risk Score (FEAT_06)
        # weighted_health = average of all 6 axes for simplicity in prototype
        weighted_health = sum(axis_scores.values()) / len(axis_scores)
        bias_risk_score = round(100.0 - weighted_health, 1)
        weighted_health = round(weighted_health, 1)
        
        # 7. Save score run summary
        run_id = str(uuid.uuid4())
        score_run_entry = {
            "run_id": run_id,
            "user_id": user_id,
            "file_id": file_id,
            "bias_risk_score": bias_risk_score,
            "weighted_health": weighted_health,
            "mbti_type": type_code, # e.g. "HHHH"
            "exception_codes": exception_codes
        }
        db_client.save_data("score_run", score_run_entry)
        
        # 8. Save each axis score
        for code, value in axis_scores.items():
            grade = "High" if value >= 60 else ("Medium" if value >= 40 else "Low")
            axis_entry = {
                "axis_id": str(uuid.uuid4()),
                "run_id": run_id,
                "axis_code": code,
                "axis_value": value,
                "axis_grade": grade
            }
            db_client.save_data("score_axis", axis_entry)
            
        return {
            "success": True,
            "run_id": run_id,
            "bias_risk_score": bias_risk_score,
            "mbti_type": type_code,
            "mbti_name": type_name,
            "mbti_tags": tags,
            "axis_scores": axis_scores,
            "exception_codes": exception_codes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis calculation failed: {str(e)}")
