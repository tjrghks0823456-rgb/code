import uuid
import logging
import time
import json
from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException

from app.core.content_filters import build_ad_skip_summary, split_analysis_events
from app.core.nlp_enhanced import analyze_session_text_advanced
from app.core.scoring import compute_6axis_score_details, classify_16_type
from app.core.shorts_analysis import build_overall_risk
from app.core.local_category_screening import estimate_local_category
from app.repositories.analysis_repository import AnalysisRepository

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service layer coordinating sampling, NLP screening, 6-axis calculation, and results storage."""
    
    def __init__(self):
        self.repository = AnalysisRepository()

    def run_scoring_pipeline(self, file_id: str, user_id: str) -> Dict[str, Any]:
        logger.info(f"[AnalysisService] started scoring run for file_id={file_id}")
        
        # 1. Fetch raw and normalized events
        events = self.repository.fetch_norm_events(file_id)
        analysis_events, excluded_ad_events = split_analysis_events(events)
        raw_files = self.repository.fetch_raw_files(file_id)
        raw_file = raw_files[0] if raw_files else {}
        upload_excluded_ad_count = int(raw_file.get("excluded_ad_count") or 0)
        excluded_ad_count = upload_excluded_ad_count + len(excluded_ad_events)
        ad_skip_summary = raw_file.get("ad_skip_summary") or build_ad_skip_summary(excluded_ad_events)

        # 2. Fetch sessions for NLP
        sessions = self.repository.fetch_sessions(file_id)
        if not sessions and not analysis_events:
            raise HTTPException(status_code=404, detail="No analyzable history found for this file. Please upload a valid history file.")

        # Blended representative sampling (max 20 sessions)
        target_count = 20
        strategy_name = "all_sessions"
        
        if len(sessions) <= target_count:
            selected_sessions = sessions
        else:
            strategy_name = "blended_oldest_newest_middle_longest_search"
            sessions_sorted = sorted(sessions, key=lambda s: s.get("start_time", ""))
            total = len(sessions_sorted)
            
            selected_indices = set()
            
            # 1) Oldest 4
            for i in range(min(4, total)):
                selected_indices.add(i)
            # 2) Newest 4
            for i in range(max(0, total - 4), total):
                selected_indices.add(i)
            # 3) Middle 4
            mid_start, mid_end = 4, total - 4
            if mid_end > mid_start:
                mid_indices = [int(mid_start + i * (mid_end - mid_start - 1) / 3) for i in range(4) if mid_start + i * (mid_end - mid_start - 1) / 3 < mid_end]
                for idx in mid_indices:
                    if 0 <= idx < total:
                        selected_indices.add(idx)

            selected_ids = {sessions_sorted[idx]["id"] for idx in selected_indices if idx < len(sessions_sorted)}
            
            # 4) Longest 4
            remaining = [s for s in sessions_sorted if s["id"] not in selected_ids]
            longest_sorted = sorted(remaining, key=lambda s: s.get("token_count", 0), reverse=True)
            for s in longest_sorted[:4]:
                selected_ids.add(s["id"])
                
            # 5) Search-heavy 4
            remaining = [s for s in sessions_sorted if s["id"] not in selected_ids]
            def has_search(s):
                txt = s.get("aggregated_text", "").lower()
                return "searched for" in txt or "검색했습니다" in txt or "검색" in txt
            search_sess = [s for s in remaining if has_search(s)]
            search_sorted = sorted(search_sess, key=lambda s: s.get("token_count", 0), reverse=True)
            for s in search_sorted[:4]:
                selected_ids.add(s["id"])
                
            # Fill up to 20
            if len(selected_ids) < target_count:
                remaining = [s for s in sessions_sorted if s["id"] not in selected_ids]
                fill_sorted = sorted(remaining, key=lambda s: s.get("token_count", 0), reverse=True)
                for s in fill_sorted[:target_count - len(selected_ids)]:
                    selected_ids.add(s["id"])
                    
            selected_sessions = [s for s in sessions_sorted if s["id"] in selected_ids]

        analysis_warnings = []
        if not sessions:
            analysis_warnings.append("No standard-video/search session text found; scoring will use event features only.")

        # 3. Category screening
        local_category_counts = {}
        for s in selected_sessions:
            txt = s.get("aggregated_text", "")
            items = [item.strip() for item in txt.split('|') if item.strip()]
            for item in items:
                cat = estimate_local_category(item)
                local_category_counts[cat] = local_category_counts.get(cat, 0) + 1

        nlp_results = []
        max_char_limit = 10000

        for idx, session in enumerate(selected_sessions):
            text = session.get("aggregated_text", "")
            truncated_text = text[:max_char_limit]

            sess_start = session.get("start_time")
            sess_end = session.get("end_time")
            session_events = [
                e for e in analysis_events
                if e.get("event_time") and sess_start <= e["event_time"] <= sess_end
            ]

            session_payload = {
                "session_text": truncated_text,
                "events": session_events
            }

            try:
                keywords, classifier_res, stability_factor, safety_factor, gcp_res = analyze_session_text_advanced(session_payload)
                nlp_result_id = str(uuid.uuid4())
                
                sentiment_score = 0.0
                sentiment_magnitude = 0.0
                language_code = "ko"
                mock_used = False
                fallback_used = True
                
                if gcp_res:
                    sentiment_score = gcp_res.get("documentSentiment", {}).get("score", 0.0)
                    sentiment_magnitude = gcp_res.get("documentSentiment", {}).get("magnitude", 0.0)
                    language_code = gcp_res.get("language_code", "ko")
                    fallback_used = False
                else:
                    sentiment_score = (1.0 - stability_factor) / 0.8 * -1.0
                    mock_used = True

                categories_json = []
                if gcp_res and gcp_res.get("categories"):
                    categories_json = gcp_res["categories"]
                else:
                    categories_json = [{"name": classifier_res.get("category"), "confidence": classifier_res.get("category_confidence")}]

                nlp_entry = {
                    "id": nlp_result_id,
                    "session_id": session["id"],
                    "categories_json": categories_json,
                    "sentiment_score": sentiment_score,
                    "sentiment_magnitude": sentiment_magnitude,
                    "language_code": language_code,
                    "mock_used": mock_used,
                    "fallback_used": fallback_used,
                    "nlp_input_token_count": session.get("token_count", 0),
                    "keywords_json": json.dumps(keywords, ensure_ascii=False),
                    "local_category": classifier_res.get("category"),
                    "category_confidence": classifier_res.get("category_confidence"),
                    "category_source": classifier_res.get("category_source"),
                    "category_candidates": classifier_res.get("category_candidates"),
                    "stability_factor": stability_factor,
                    "safety_factor": safety_factor,
                    "nlp_provider": "gcp" if gcp_res else "rule_based_fallback",
                    "category_version": "2.0"
                }
                self.repository.save_nlp_result(nlp_entry)
                nlp_results.append(nlp_entry)
            except Exception as e:
                warning_msg = f"세션 {idx+1} ({session.get('start_time')}) 분석 실패: {str(e)}"
                logger.error(warning_msg, exc_info=True)
                analysis_warnings.append(warning_msg)

        if not nlp_results:
            analysis_warnings.append("All NLP sessions failed; scoring will use low-confidence feature warnings instead of fake default NLP data.")

        if excluded_ad_count:
            analysis_warnings.append(f"Excluded {excluded_ad_count} ad-origin events before scoring.")

        # 4. Scoring Engine Call
        score_details, exception_codes, feature_summary = compute_6axis_score_details(analysis_events, nlp_results)
        feature_summary["excluded_ad_count"] = excluded_ad_count
        feature_summary["local_category_counts"] = local_category_counts
        feature_summary["data_quality_flags"] = {"sampling_strategy": strategy_name}
        axis_scores = {
            code: detail["score"]
            for code, detail in score_details.items()
        }
        score_quality_warnings = sorted({
            warning
            for detail in score_details.values()
            for warning in detail.get("warnings", [])
        })

        # 5. Classify 16 Types
        type_code, type_name, tags = classify_16_type(axis_scores)

        available_axes = [
            detail for detail in score_details.values()
            if detail.get("available", True) is True
        ]
        excluded_axes = [code for code, detail in score_details.items() if not detail.get("available", True)]
        
        if available_axes:
            weighted_health = sum(float(axis["score"]) for axis in available_axes) / len(available_axes)
        else:
            weighted_health = 50.0
            
        bias_risk_score = round(100.0 - weighted_health, 1)
        weighted_health = round(weighted_health, 1)
        
        if len(excluded_axes) >= 2 or not available_axes:
            overall_confidence = "low"
        elif len(excluded_axes) == 1:
            overall_confidence = "medium"
        else:
            overall_confidence = "high"
            
        risk_overall = build_overall_risk(
            information_bias_risk=bias_risk_score,
            shorts_analysis=feature_summary.get("shorts_analysis", {})
        )
        shorts_warnings = feature_summary.get("shorts_analysis", {}).get("warnings", [])
        if isinstance(shorts_warnings, list):
            analysis_warnings.extend(shorts_warnings)

        # 6. Save score run summary
        run_id = str(uuid.uuid4())
        data_coverage = {
            "excluded_ad_count": excluded_ad_count,
            "skipped_sources_with_reason": raw_file.get("skipped_sources_with_reason", {}),
            "ad_skip_summary": ad_skip_summary,
            "parsed_source_counts": raw_file.get("parsed_source_counts", {}),
            "analysis_source_counts": raw_file.get("analysis_source_counts", {}),
            "content_format_counts": raw_file.get("content_format_counts", {}),
            "duration_source_counts": raw_file.get("duration_source_counts", {}),
        }
        
        total_session_count = len(sessions)
        sampled_session_count = len(selected_sessions)
        sampling_strategy = strategy_name
        nlp_input_token_count = sum(s.get("token_count", 0) for s in selected_sessions)
        
        upload_flags = raw_file.get("data_quality_flags") or raw_file.get("data_coverage", {}).get("data_quality_flags") or []
        data_quality_flags = list(upload_flags)
        if len(nlp_results) < sampled_session_count:
            if len(nlp_results) == 0:
                data_quality_flags.append("nlp_api_all_failed")
            else:
                data_quality_flags.append("nlp_api_partial_failure")

        sampling_metadata = {
            "total_session_count": total_session_count,
            "sampled_session_count": sampled_session_count,
            "sampling_strategy": sampling_strategy,
            "nlp_input_token_count": nlp_input_token_count,
            "excluded_axes": excluded_axes,
            "overall_confidence": overall_confidence,
            "score_details": score_details
        }

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
            "data_coverage": data_coverage,
            "mbti_type": type_code,
            "exception_codes": exception_codes,
            "score_warnings": analysis_warnings + score_quality_warnings,
            "sampling_metadata": sampling_metadata,
            "data_quality_flags": data_quality_flags
        }
        
        logger.info(f"[analysis/run] score_run_save_started")
        t_run_start = time.perf_counter()
        self.repository.save_score_run(score_run_entry)
        t_run_elapsed = int((time.perf_counter() - t_run_start) * 1000)
        storage_type = "MockDB" if score_run_entry.get("__storage") == "MockDB" else "Supabase"
        logger.info(f"[analysis/run] score_run_save_done elapsed_ms={t_run_elapsed} storage={storage_type}")

        # 7. Save each axis score
        axis_entries = []
        for code, value in axis_scores.items():
            grade = "High" if value >= 60 else ("Medium" if value >= 40 else "Low")
            axis_entries.append({
                "axis_id": str(uuid.uuid4()),
                "run_id": run_id,
                "axis_code": code,
                "axis_value": value,
                "axis_grade": grade
            })
        logger.info(f"[analysis/run] score_axis_save_started count={len(axis_entries)}")
        t_axis_start = time.perf_counter()
        self.repository.save_score_axes(axis_entries)
        t_axis_elapsed = int((time.perf_counter() - t_axis_start) * 1000)
        logger.info(f"[analysis/run] score_axis_save_done elapsed_ms={t_axis_elapsed} storage={storage_type}")

        logger.info(f"[analysis/run] completed")
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
            "excluded_ad_count": excluded_ad_count,
            "data_coverage": data_coverage,
            "exception_codes": exception_codes,
            "analysis_warnings": analysis_warnings + score_quality_warnings,
            "total_session_count": total_session_count,
            "sampled_session_count": sampled_session_count,
            "sampling_strategy": sampling_strategy,
            "nlp_input_token_count": nlp_input_token_count,
            "data_quality_flags": data_quality_flags,
            "excluded_axes": excluded_axes,
            "overall_confidence": overall_confidence
        }
