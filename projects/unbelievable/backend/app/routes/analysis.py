import uuid
import logging
from typing import List
from fastapi import APIRouter, HTTPException
from app.core.content_filters import split_analysis_events
from app.core.database import db_client
from app.core.nlp import nlp_client
from app.core.scoring import compute_6axis_score_details, classify_16_type
from app.core.shorts_analysis import build_overall_risk

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
        # 1. Fetch normalized events first so shorts-only uploads can still be scored.
        events = db_client.fetch_data("norm_event", {"file_id": file_id})
        analysis_events, excluded_ad_events = split_analysis_events(events)

        # 2. Fetch sessions for NLP. Shorts are intentionally excluded from
        # session_text, so an event-only analysis path is valid.
        sessions = db_client.fetch_data("session_text", {"file_id": file_id})
        if not sessions and not analysis_events:
            raise HTTPException(status_code=404, detail="No analyzable history found for this file. Please upload a valid history file.")

        # Chronologically sort the sessions by start_time
        sessions_sorted = sorted(sessions, key=lambda s: s.get("start_time", ""))

        # Chronological even-spacing representative sampling (max 5 sessions)
        if len(sessions_sorted) > 5:
            # Evenly space selection of 5 indices from the total sessions list
            indices = [int(i * (len(sessions_sorted) - 1) / 4) for i in range(5)]
            selected_sessions = [sessions_sorted[idx] for idx in indices]
        else:
            selected_sessions = sessions_sorted

        analysis_warnings = []
        if not sessions:
            analysis_warnings.append("No standard-video/search session text found; scoring will use event features only.")

        nlp_results = []

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
                    "language_code": nlp_response.get("language_code", "ko"),
                    "mock_used": bool(nlp_response.get("mock_used", False)),
                    "fallback_used": bool(nlp_response.get("fallback_used", False))
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
            analysis_warnings.append("All NLP sessions failed; scoring will use low-confidence feature warnings instead of fake default NLP data.")

        # 4. Score all normalized non-ad events
        if excluded_ad_events:
            analysis_warnings.append(f"Excluded {len(excluded_ad_events)} ad-origin events before scoring.")

        # 5. Compute 6-axis scores using deterministic python scoring engine (FEAT_06)
        score_details, exception_codes, feature_summary = compute_6axis_score_details(analysis_events, nlp_results)
        feature_summary["excluded_ad_count"] = len(excluded_ad_events)
        axis_scores = {
            code: detail["score"]
            for code, detail in score_details.items()
        }
        score_quality_warnings = sorted({
            warning
            for detail in score_details.values()
            for warning in detail.get("warnings", [])
        })

        # 6. Classify into one of 16 types (FEAT_08)
        type_code, type_name, tags = classify_16_type(axis_scores)

        # Calculate confidence-weighted health while preserving a numeric fallback.
        confidence_total = sum(detail.get("confidence", 0.0) for detail in score_details.values())
        if confidence_total > 0:
            weighted_health = sum(
                detail["score"] * detail.get("confidence", 0.0)
                for detail in score_details.values()
            ) / confidence_total
        else:
            weighted_health = sum(axis_scores.values()) / len(axis_scores)
        bias_risk_score = round(100.0 - weighted_health, 1)
        weighted_health = round(weighted_health, 1)
        risk_overall = build_overall_risk(
            information_bias_risk=bias_risk_score,
            shorts_analysis=feature_summary.get("shorts_analysis", {})
        )
        shorts_warnings = feature_summary.get("shorts_analysis", {}).get("warnings", [])
        if isinstance(shorts_warnings, list):
            analysis_warnings.extend(shorts_warnings)

        # 7. Save score run summary
        run_id = str(uuid.uuid4())
        score_run_entry = {
            "run_id": run_id,
            "user_id": user_id,
            "file_id": file_id,
            "bias_risk_score": bias_risk_score,
            "weighted_health": weighted_health,
            "information_bias_risk": risk_overall["information_bias_risk"],
            "shorts_stimulation_risk": risk_overall["shorts_stimulation_risk"],
            "final_detox_risk": risk_overall["final_detox_risk"],
            "shorts_analysis": feature_summary.get("shorts_analysis", {}),
            "mbti_type": type_code, # e.g. "HHHH"
            "exception_codes": exception_codes,
            "score_warnings": analysis_warnings + score_quality_warnings # Saved in warnings JSONB
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
            "information_bias_risk": risk_overall["information_bias_risk"],
            "shorts_stimulation_risk": risk_overall["shorts_stimulation_risk"],
            "final_detox_risk": risk_overall["final_detox_risk"],
            "shorts_weight": risk_overall["shorts_weight"],
            "mbti_type": type_code,
            "mbti_name": type_name,
            "mbti_tags": tags,
            "axis_scores": axis_scores,
            "score_details": score_details,
            "feature_summary": {
                key: feature_summary.get(key)
                for key in [
                    "watch_count",
                    "search_count",
                    "standard_video_count",
                    "shorts_count",
                    "live_count",
                    "unknown_format_count",
                    "shorts_analysis",
                    "comment_count",
                    "playlist_count",
                    "subscription_count",
                    "channel_count",
                    "live_chat_count",
                    "duration_confidence",
                    "data_confidence",
                    "mock_used",
                    "fallback_used",
                    "excluded_ad_count",
                    "data_quality_warnings"
                ]
            },
            "excluded_ad_count": len(excluded_ad_events),
            "exception_codes": exception_codes,
            "analysis_warnings": analysis_warnings + score_quality_warnings
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis calculation failed: {str(e)}")
