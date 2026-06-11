import uuid
import json
from datetime import datetime
from collections import Counter
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from app.core.content_filters import split_analysis_events
from app.core.gemini import gemini_client
from app.core.shorts_analysis import build_shorts_analysis
from app.core.mission_loader import mission_loader
from app.core.scoring_rule_loader import scoring_rule_loader
from app.services.dashboard_service import DashboardService
from app.repositories.detox_repository import DetoxRepository


class DetoxService:
    def __init__(
        self,
        repository: Optional[DetoxRepository] = None,
        dashboard_service: Optional[DashboardService] = None,
    ):
        self.repository = repository or DetoxRepository()
        self.dashboard_service = dashboard_service or DashboardService()

    def generate_detox_plan(self, run_id: str, user_id: str) -> Dict[str, Any]:
        runs = self.repository.fetch_score_run(run_id)
        if not runs:
            raise HTTPException(status_code=404, detail="Score run not found.")
        run = runs[0]

        axes_list = self.repository.fetch_score_axes(run_id)
        axis_scores = {axis["axis_code"]: axis["axis_value"] for axis in axes_list}

        events = self.repository.fetch_norm_events(run.get("file_id"))
        analysis_events, _excluded_ad_events = split_analysis_events(events)
        shorts_analysis = build_shorts_analysis(analysis_events)

        # Get actual dominant topics from nlp results and events
        file_id = run.get("file_id")
        sessions_list = self.repository.fetch_session_texts(file_id)
        session_ids = [s["id"] for s in sessions_list]

        local_categories = []
        keywords_list = []
        confidences = []
        results = self.repository.fetch_nlp_results_by_session_ids(session_ids)
        for r in results:
            if r.get("local_category"):
                local_categories.append(r["local_category"])
            if r.get("category_confidence") is not None:
                confidences.append(r["category_confidence"])
            kws_json = r.get("keywords_json")
            if kws_json:
                try:
                    kws = json.loads(kws_json)
                    for item in kws:
                        if isinstance(item, list) or isinstance(item, tuple):
                            keywords_list.append(item[0])
                        else:
                            keywords_list.append(str(item))
                except Exception:
                    pass

        cat_counts = Counter(local_categories)
        kw_counts = Counter(keywords_list)

        dominant_topics = []
        for cat, _ in cat_counts.most_common(2):
            if cat not in ["❓ 기타/미분류"]:
                dominant_topics.append(cat)
        for kw, _ in kw_counts.most_common(3):
            dominant_topics.append(kw)

        if not dominant_topics:
            dominant_topics = scoring_rule_loader.get("default_dominant_topics", ["관심사 다양화", "추천 피드 점검"])

        # Determine actual DSAO code
        view_events = [
            e for e in analysis_events
            if e.get("action_type") == "view" and e.get("content_format") == "standard_video"
        ]
        long_views = [e for e in view_events if e.get("time_delta_sec") is not None and e.get("time_delta_sec") >= 180]
        long_ratio = (len(long_views) / len(view_events)) * 100.0 if view_events else 100.0

        uas_score = axis_scores.get("UAS", 50.0)
        tds_score = axis_scores.get("TDS", 50.0)
        sms_score = axis_scores.get("SMS", 50.0)

        actual_d_p = "D" if uas_score >= 50.0 else "P"
        actual_w_n = "W" if tds_score >= 50.0 else "N"
        actual_s_m = "M" if sms_score >= 50.0 else "S"
        actual_f_l = "L" if long_ratio >= 50.0 else "F"

        actual_dsao_code = f"{actual_d_p}{actual_w_n}{actual_s_m}{actual_f_l}"

        # Get warning codes & data quality flags
        exception_codes = self.dashboard_service.normalize_exception_codes(run.get("exception_codes", []))
        data_quality_flags = run.get("data_quality_flags") or []

        # Get top local category & candidates
        top_local_cat = "❓ 기타/미분류"
        if cat_counts:
            top_local_cat = cat_counts.most_common(1)[0][0]
        category_candidates = [cat for cat, _ in cat_counts.most_common(4)]
        top_kws = [kw for kw, _ in kw_counts.most_common(6)]

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Run dynamic recommender
        matched_recs = mission_loader.recommend_missions(
            keywords=top_kws,
            local_category=top_local_cat,
            category_candidates=category_candidates,
            category_confidence=avg_confidence,
            actual_dsao=actual_dsao_code,
            data_quality_flags=data_quality_flags,
            warning_codes=exception_codes,
            axis_scores=axis_scores,
            bias_risk_score=run["bias_risk_score"],
            shorts_count=shorts_analysis.get("shorts_count", 0),
            shorts_stimulation_risk=shorts_analysis.get("shorts_stimulation_risk", 0)
        )

        plan_response = gemini_client.generate_detox_plan(
            risk_score=run["bias_risk_score"],
            axis_scores=axis_scores,
            mbti_type=run["mbti_type"],
            dominant_topics=dominant_topics,
            shorts_analysis=shorts_analysis,
        )

        # Override missions with our dynamically matched, scored, and localized missions
        formatted_missions = []
        for idx, rec in enumerate(matched_recs, 1):
            rec["id"] = f"m{idx}"
            formatted_missions.append(rec)
        plan_response["missions"] = formatted_missions

        plan_id = str(uuid.uuid4())
        plan_entry = {
            "plan_id": plan_id,
            "run_id": run_id,
            "user_id": user_id,
            "reverse_queries": plan_response["reverse_queries"],
            "mission_json": plan_response["missions"],
        }
        self.repository.save_detox_plan(plan_entry)

        for mission in plan_response["missions"]:
            log_entry = {
                "log_id": str(uuid.uuid4()),
                "plan_id": plan_id,
                "mission_item_id": mission["id"],
                "completed_yn": False,
                "completed_at": None,
            }
            self.repository.save_mission_log(log_entry)

        return {
            "success": True,
            "plan_id": plan_id,
            "overall_summary": plan_response["overall_summary"],
            "shorts_analysis": shorts_analysis,
            "reverse_queries": plan_response["reverse_queries"],
            "missions": plan_response["missions"],
        }

    def get_active_plan(self, plan_id: Optional[str], user_id: str) -> Dict[str, Any]:
        if plan_id:
            plans = self.repository.fetch_detox_plan_by_id(plan_id)
            if not plans:
                raise HTTPException(status_code=404, detail="Requested detox plan not found.")
            latest_plan = plans[0]
        else:
            plans = self.repository.fetch_detox_plans_by_user_id(user_id)
            if not plans:
                return {"active": False, "message": "No active detox plan found."}
            latest_plan = plans[-1]

        logs = self.repository.fetch_mission_logs_by_plan_id(latest_plan["plan_id"])

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

    def update_mission_status(self, log_id: str, completed: bool) -> Dict[str, Any]:
        logs = self.repository.fetch_mission_log_by_id(log_id)
        if not logs:
            raise HTTPException(status_code=404, detail="Mission log not found.")

        log = logs[0]
        log["completed_yn"] = completed
        log["completed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if completed else None
        self.repository.save_mission_log(log)

        return {
            "success": True,
            "log_id": log_id,
            "completed": completed,
            "completed_at": log["completed_at"],
        }
