import uuid
import logging
from typing import List
from fastapi import APIRouter, HTTPException
from app.core.database import db_client
from app.core.nlp import nlp_client
from app.core.scoring import compute_6axis_scores, classify_16_type

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analysis/run")
async def run_analysis(
    file_id: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
):
    """
    Triggers the quantitative and qualitative analysis pipelines.
    Supports chronological even-spacing multi-session sampling, GCP Natural Language API limits,
    and resilience against individual session failures.
    """
    try:
        # 1. Fetch sessions for the file
        sessions = db_client.fetch_data("session_text", {"file_id": file_id})
        if not sessions:
            raise HTTPException(status_code=404, detail="No session text found for this file. Please upload a valid history file.")

        # Chronologically sort the sessions by start_time
        sessions_sorted = sorted(sessions, key=lambda s: s.get("start_time", ""))

        # Chronological even-spacing representative sampling (max 5 sessions)
        if len(sessions_sorted) > 5:
            # Evenly space selection of 5 indices from the total sessions list
            indices = [int(i * (len(sessions_sorted) - 1) / 4) for i in range(5)]
            selected_sessions = [sessions_sorted[idx] for idx in indices]
        else:
            selected_sessions = sessions_sorted

        nlp_results = []
        analysis_warnings = []

        # NLP text word count capping (MVP Limits)
        max_char_limit = 10000

        for idx, session in enumerate(selected_sessions):
            text = session.get("aggregated_text", "")
            # Truncate text to avoid NLP API cost explosion
            truncated_text = text[:max_char_limit]

            try:
                # Call NLP annotation client
                nlp_response = nlp_client.analyze_text(truncated_text)

                nlp_result_id = str(uuid.uuid4())
                nlp_entry = {
                    "id": nlp_result_id,
                    "session_id": session["id"],
                    "categories_json": nlp_response.get("categories_json", []),
                    "sentiment_score": nlp_response.get("documentSentiment", {}).get("score", 0.0),
                    "sentiment_magnitude": nlp_response.get("documentSentiment", {}).get("magnitude", 0.0),
                    "language_code": nlp_response.get("language_code", "ko")
                }
                db_client.save_data("nlp_result", nlp_entry)
                nlp_results.append(nlp_entry)
            except Exception as e:
                # Dynamic error resilience: record warning, proceed with remaining sessions
                warning_msg = f"세션 {idx+1} ({session.get('start_time')}) 분석 실패: {str(e)}"
                logger.error(warning_msg)
                analysis_warnings.append(warning_msg)

        # Handle case where all sessions fail
        if not nlp_results:
            default_nlp = {
                "id": str(uuid.uuid4()),
                "session_id": selected_sessions[0]["id"],
                "categories_json": [{"name": "/Computers & Electronics/Software", "confidence": 0.95}],
                "sentiment_score": 0.1,
                "sentiment_magnitude": 0.15,
                "language_code": "ko"
            }
            nlp_results.append(default_nlp)
            analysis_warnings.append("모든 세션 분석 실패로 인해 기본 NLP 분석 설정으로 폴백 적용되었습니다.")

        # 4. Fetch all normalized events for scoring
        events = db_client.fetch_data("norm_event", {"file_id": file_id})

        # 5. Compute 6-axis scores using deterministic python scoring engine (FEAT_06)
        axis_scores, exception_codes = compute_6axis_scores(events, nlp_results)

        # 6. Classify into one of 16 types (FEAT_08)
        type_code, type_name, tags = classify_16_type(axis_scores)

        # Calculate Weighted Health & Bias Risk Score (FEAT_06)
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
            "exception_codes": exception_codes,
            "score_warnings": analysis_warnings # Saved in warnings JSONB
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
            "exception_codes": exception_codes,
            "analysis_warnings": analysis_warnings
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis calculation failed: {str(e)}")
