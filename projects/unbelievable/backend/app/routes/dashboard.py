import logging
from collections import Counter
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from app.core.content_filters import (
    clean_search_query,
    is_shorts_video_event,
    is_standard_video_event,
    is_valid_search_event,
    split_analysis_events,
)
from app.core.database import db_client
from app.core.interest_maps import (
    build_interest_gap_report,
    build_search_interest_map,
    build_shorts_interest_map,
    build_standard_video_interest_map,
)
from app.core.gemini import gemini_client
from app.core.scoring import PERSONALITY_MAP
from app.core.shorts_analysis import build_overall_risk, build_shorts_analysis
from app.core.config import DEFAULT_MVP_USER_ID

logger = logging.getLogger(__name__)
router = APIRouter()

from app.core.message_loader import message_loader
from app.core.persona_loader import persona_loader

AXIS_NAMES = {
    "TDS": "주제 다양성",
    "SBS": "출처 균형",
    "EBS": "감정 균형",
    "VOS": "관점 개방성",
    "SMS": "유해/자극 안전",
    "UAS": "사용자 주도성",
    "ALL": "전체 지표"
}

# Dynamically loaded warnings mapping from message_loader config asset
SCORE_WARNING_MAP = message_loader.get_all_warnings()

def normalize_exception_codes(raw_codes: Any) -> List[str]:
    if not raw_codes:
        return []
    if isinstance(raw_codes, list):
        return [str(code) for code in raw_codes if code]
    if isinstance(raw_codes, tuple):
        return [str(code) for code in raw_codes if code]
    if isinstance(raw_codes, str):
        cleaned = raw_codes.strip("{}")
        return [code.strip().strip('"') for code in cleaned.split(",") if code.strip()]
    return []

def build_score_warnings(exception_codes: List[str]) -> List[Dict[str, str]]:
    warnings = []
    seen_codes = set()

    for code in exception_codes:
        if code in seen_codes:
            continue
        seen_codes.add(code)

        warning = SCORE_WARNING_MAP.get(code)
        if not warning:
            continue

        axis = warning["axis"]
        warnings.append({
            "axis": axis,
            "axis_name": AXIS_NAMES.get(axis, axis),
            "code": code,
            "message": warning["message"]
        })

    return warnings

INSIGHT_TONES = [
    "bg-rose-500",
    "bg-emerald-500",
    "bg-sky-500",
    "bg-amber-500",
    "bg-indigo-500",
    "bg-teal-500",
]

UNKNOWN_SOURCE_VALUES = {"", "unknown", "none", "null", "n/a"}

def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

def is_known_value(value: Any) -> bool:
    return clean_text(value).lower() not in UNKNOWN_SOURCE_VALUES

def top_level_category(category: Any) -> str:
    if isinstance(category, dict):
        raw_name = category.get("name", "")
    else:
        raw_name = category
    name = clean_text(raw_name)
    if not name:
        return ""
    parts = [part.strip() for part in name.split("/") if part.strip()]
    return parts[0] if parts else name

def fetch_nlp_results_for_file(file_id: str) -> List[Dict[str, Any]]:
    sessions = db_client.fetch_data("session_text", {"file_id": file_id})
    results: List[Dict[str, Any]] = []
    for session in sessions:
        session_id = session.get("id")
        if not session_id:
            continue
        results.extend(db_client.fetch_data("nlp_result", {"session_id": session_id}))
    return results

def build_distribution_shares(counter: Counter, top_limit: int = 6) -> List[Dict[str, Any]]:
    total = sum(counter.values())
    if total <= 0:
        return []
    shares = []
    for index, (name, count) in enumerate(counter.most_common(top_limit)):
        value = round((count / total) * 100.0, 1)
        shares.append({
            "name": name,
            "value": value,
            "count": count,
            "tone": INSIGHT_TONES[index % len(INSIGHT_TONES)]
        })
    return shares

def build_dashboard_insights(
    events: List[Dict[str, Any]],
    nlp_results: List[Dict[str, Any]],
    axis_scores: Dict[str, float],
    score_warnings: List[Dict[str, str]]
) -> Dict[str, Any]:
    search_counter: Counter = Counter()
    standard_video_counter: Counter = Counter()
    shorts_counter: Counter = Counter()
    topic_counter: Counter = Counter()
    channel_counter: Counter = Counter()
    analysis_events, excluded_ad_events = split_analysis_events(events)

    for event in analysis_events:
        title = clean_text(event.get("text_base"))

        if is_valid_search_event(event):
            query = clean_search_query(title)
            if query:
                search_counter[query] += 1

        if is_standard_video_event(event) and title:
            standard_video_counter[title] += 1

        if is_shorts_video_event(event) and title:
            shorts_counter[title] += 1

        channel = clean_text(event.get("channel_url") or event.get("channel_name") or event.get("author_id") or event.get("source_surface"))
        if is_standard_video_event(event) and is_known_value(channel):
            channel_counter[channel] += 1

    for result in nlp_results:
        categories = result.get("categories_json", [])
        if not isinstance(categories, list):
            continue
        for category in categories:
            topic = top_level_category(category)
            if topic:
                topic_counter[topic] += 1

    topic_shares = build_distribution_shares(topic_counter)
    channel_shares = build_distribution_shares(channel_counter, top_limit=5)
    search_keywords = [
        {
            "keyword": keyword,
            "count": count,
            "category": topic_shares[0]["name"] if topic_shares else "검색"
        }
        for keyword, count in search_counter.most_common(8)
    ]
    standard_video_keywords = [
        {"keyword": keyword, "count": count}
        for keyword, count in standard_video_counter.most_common(8)
    ]
    shorts_keywords = [
        {"keyword": keyword, "count": count}
        for keyword, count in shorts_counter.most_common(8)
    ]
    shorts_analysis = build_shorts_analysis(analysis_events)
    search_interest_map = build_search_interest_map(events)
    standard_video_interest_map = build_standard_video_interest_map(events)
    shorts_interest_map = build_shorts_interest_map(events)
    interest_gap_report = build_interest_gap_report(
        search_interest_map,
        standard_video_interest_map,
        shorts_interest_map,
    )
    interest_ai_summary = gemini_client.enrich_interest_report(
        search_interest_map,
        standard_video_interest_map,
        shorts_interest_map,
        interest_gap_report,
    )

    search_keywords = search_interest_map.get("top_keywords", [])[:8] or search_keywords
    standard_video_keywords = standard_video_interest_map.get("top_keywords", [])[:8] or standard_video_keywords
    shorts_keywords = shorts_interest_map.get("top_shorts_keywords", [])[:8] or shorts_keywords

    rule_topic_shares = []
    for index, item in enumerate(standard_video_interest_map.get("category_distribution", [])[:6]):
        rule_topic_shares.append({
            "name": item.get("category") or item.get("name"),
            "value": item.get("value", 0),
            "count": item.get("count", 0),
            "tone": INSIGHT_TONES[index % len(INSIGHT_TONES)]
        })
    if rule_topic_shares:
        topic_shares = rule_topic_shares

    report_insights: List[str] = []
    if search_keywords:
        top_search = search_keywords[0]
        report_insights.append(f"가장 많이 반복된 검색어는 '{top_search['keyword']}'이며 {top_search['count']}회 감지되었습니다.")
    else:
        report_insights.append("검색 기록이 없거나 부족해 직접 탐색 관심사는 낮은 신뢰도로 해석됩니다.")

    if topic_shares:
        top_topic = topic_shares[0]
        report_insights.append(f"NLP 기준 최상위 관심 주제는 '{top_topic['name']}'로 전체 주제 신호의 {top_topic['value']}%를 차지합니다.")
    else:
        report_insights.append("NLP 주제 분류 결과가 부족해 카테고리 비중은 아직 계산되지 않았습니다.")

    if channel_shares:
        top_channel = channel_shares[0]
        report_insights.append(f"가장 많이 노출된 출처는 '{top_channel['name']}'이며 출처 균형 점수는 {round(float(axis_scores.get('SBS', 0.0)), 1)}점입니다.")

    if excluded_ad_events:
        report_insights.append(f"광고 출처로 감지된 {len(excluded_ad_events)}건은 관심사/점수 분석에서 제외했습니다.")

    if score_warnings:
        report_insights.append(f"{len(score_warnings)}개의 신뢰도 경고가 있어 일부 지표는 참고용으로 봐야 합니다.")

    direct_interest_summary = " · ".join(item["keyword"] for item in search_keywords[:3]) if search_keywords else "검색 기록 부족"
    flow_summary_categories = interest_gap_report.get("recommendation_flow_candidate_categories", []) or []
    recommendation_flow_summary = (
        " · ".join(item.get("category", "") for item in flow_summary_categories[:3] if item.get("category"))
        if flow_summary_categories
        else (
            " · ".join(item["name"] for item in topic_shares[:3])
            if topic_shares
            else (" · ".join(item["name"] for item in channel_shares[:3]) if channel_shares else "분류 데이터 부족")
        )
    )

    return {
        "search_keywords": search_keywords,
        "search_interest_map": search_interest_map,
        "standard_video_interest_map": standard_video_interest_map,
        "shorts_interest_map": shorts_interest_map,
        "interest_gap_report": interest_gap_report,
        "interest_ai_summary": interest_ai_summary,
        "category_shares": topic_shares,
        "channel_shares": channel_shares,
        "excluded_ad_count": len(excluded_ad_events),
        "shorts_analysis": shorts_analysis,
        "report_insights": report_insights,
        "direct_interest_summary": direct_interest_summary,
        "recommendation_flow_summary": recommendation_flow_summary,
        "algorithm_interest_summary": recommendation_flow_summary
    }

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    run_id: str,
    user_id: str = DEFAULT_MVP_USER_ID
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
        
        sampling_metadata = run.get("sampling_metadata") or {}
        excluded_axes = sampling_metadata.get("excluded_axes") or []
        overall_confidence = sampling_metadata.get("overall_confidence") or "medium"
        score_details = sampling_metadata.get("score_details") or {}
        data_quality_flags = run.get("data_quality_flags") or []
        
        # 2. Fetch axes scores
        axes = db_client.fetch_data("score_axis", {"run_id": run_id})
        axis_scores = {a["axis_code"]: a["axis_value"] for a in axes}
        
        # 3. Fetch user profile survey scores (for meta-gap calculation)
        profiles = db_client.fetch_data("profiles", {"id": user_id})
        profile = profiles[0] if profiles else {}
        
        raw_survey_data = None
        survey_scores = {}
        source = "none"
        
        if profile.get("raw_survey"):
            raw_survey_data = profile.get("raw_survey")
            survey_scores = raw_survey_data.get("survey_scores") or profile.get("survey_scores") or {}
            source = "raw_survey"
        elif profile.get("survey_result"):
            raw_survey_data = profile.get("survey_result")
            survey_scores = raw_survey_data.get("survey_scores") or profile.get("survey_scores") or {}
            source = "survey_result"
        elif profile.get("survey_scores"):
            survey_scores = profile.get("survey_scores") or {}
            source = "survey_scores"
            
        survey_fallback = {
            "source": source,
            "raw_survey": raw_survey_data,
            "survey_scores": survey_scores
        }
        
        # Determine if survey data is available (needs at least one valid axis score)
        valid_survey_axes = [k for k in ["TDS", "SBS", "EBS", "VOS", "SMS", "UAS"] if k in survey_scores]
        meta_gap_available = len(valid_survey_axes) > 0
        
        meta_gap = {}
        max_gap_axis = "TDS"
        max_gap_value = -1.0
        
        exception_codes = normalize_exception_codes(run.get("exception_codes", []))
        score_warnings = build_score_warnings(exception_codes)

        for code, name in AXIS_NAMES.items():
            if code == "ALL":
                continue

            is_available = code not in excluded_axes
            
            if is_available:
                a_val = float(axis_scores.get(code, 50.0))
                if meta_gap_available and code in survey_scores:
                    s_val = float(survey_scores[code])
                    gap = s_val - a_val
                    meta_gap[code] = {
                        "name": name,
                        "survey": s_val,
                        "actual": a_val,
                        "gap": round(gap, 1),
                        "available": True
                    }
                    abs_gap = abs(gap)
                    if abs_gap > max_gap_value:
                        max_gap_value = abs_gap
                        max_gap_axis = code
                else:
                    meta_gap[code] = {
                        "name": name,
                        "survey": None,
                        "actual": a_val,
                        "gap": None,
                        "available": True
                    }
            else:
                if code == "SBS":
                    reason = "채널 정보 없음"
                elif code == "UAS":
                    reason = "검색 기록 또는 직접 선택 경로 부족"
                else:
                    reason = "데이터 부족"
                meta_gap[code] = {
                    "name": name,
                    "survey": None,
                    "actual": None,
                    "gap": None,
                    "available": False,
                    "reason": reason
                }
                
        if meta_gap_available:
            valid_gaps = [
                abs(item["gap"]) for item in meta_gap.values()
                if item["gap"] is not None and item.get("available", True) is not False
            ]
            if valid_gaps:
                avg_gap = sum(valid_gaps) / len(valid_gaps)
                misconception_index = round(avg_gap * 1.5, 1)
                misconception_index = min(100.0, misconception_index)
            else:
                misconception_index = None
            
            worst_gap_code = max_gap_axis
            worst_gap_name = AXIS_NAMES[max_gap_axis]
            worst_gap_val = round(meta_gap[max_gap_axis]["gap"], 1) if meta_gap[max_gap_axis]["gap"] is not None else None
            if worst_gap_val is not None:
                misconception_message = f"스스로 사전 인지했던 점수 대비 실제 YouTube 소비 데이터상으로 '{worst_gap_name}' 영역의 차이가 가장 크게 집계되었습니다. 가벼운 일상 추천 루틴 수정을 통해 성향의 균형을 복원하시는 것을 추천합니다."
            else:
                misconception_message = "자가진단 데이터와 비교 가능한 실제 분석 지표 격차가 모두 확보되지 않았습니다."
        else:
            misconception_index = None
            worst_gap_code = None
            worst_gap_name = None
            worst_gap_val = None
            misconception_message = "자가진단 데이터가 없어 메타인지 격차 분석은 참고용으로 비활성화되었습니다."
        
        # Find MBTI descriptions
        # MBTI type code is stored as 4 characters, e.g., "HHHH"
        mbti_code = run["mbti_type"]
        key = tuple(mbti_code[i] for i in range(4)) if len(mbti_code) == 4 else ("H", "H", "H", "H")
        mbti_details = PERSONALITY_MAP.get(key, ("미지의 미디어 관찰자", ["#분석대기", "#신규성향"]))
        
        # --- [NEW] Calculate Actual DSAO based on actual watch data ---
        file_id = run["file_id"]
        raw_files = db_client.fetch_data("raw_file", {"id": file_id})
        raw_file = raw_files[0] if raw_files else {}
        events = db_client.fetch_data("norm_event", {"file_id": file_id})
        analysis_events, excluded_ad_events = split_analysis_events(events)
        nlp_results = fetch_nlp_results_for_file(file_id)
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
        
        actual_dsao_name = persona_loader.get_dsao_name(actual_dsao_code)
        insights = build_dashboard_insights(events, nlp_results, axis_scores, score_warnings)
        upload_excluded_ad_count = int(raw_file.get("excluded_ad_count") or 0)
        total_excluded_ad_count = upload_excluded_ad_count + len(excluded_ad_events)
        insights["excluded_ad_count"] = max(insights.get("excluded_ad_count", 0), total_excluded_ad_count)
        if insights.get("search_interest_map"):
            insights["search_interest_map"]["excluded_ad_count"] = insights["excluded_ad_count"]
        data_coverage = run.get("data_coverage") or {
            "excluded_ad_count": total_excluded_ad_count,
            "skipped_sources_with_reason": raw_file.get("skipped_sources_with_reason", {}),
            "ad_skip_summary": raw_file.get("ad_skip_summary", []),
        }
        raw_data_coverage = raw_file.get("data_coverage") or {}
        for key in [
            "parsed_source_counts",
            "analysis_source_counts",
            "content_format_counts",
            "duration_source_counts",
            "skipped_sources_with_reason",
            "ad_skip_summary",
        ]:
            value = data_coverage.get(key) or raw_data_coverage.get(key) or raw_file.get(key)
            if value is not None:
                data_coverage[key] = value
        data_coverage["excluded_ad_count"] = max(
            int(data_coverage.get("excluded_ad_count") or 0),
            total_excluded_ad_count,
        )
        content_counts = data_coverage.get("content_format_counts") or {}
        parsed_source_counts = dict(data_coverage.get("parsed_source_counts") or {})
        parsed_source_counts.setdefault("search_history", parsed_source_counts.get("search_history", 0))
        parsed_source_counts.setdefault("standard_video", content_counts.get("standard_video", 0))
        parsed_source_counts.setdefault("shorts", content_counts.get("shorts", 0))
        parsed_source_counts.setdefault("live", content_counts.get("live", 0))
        parsed_source_counts.setdefault("unknown", content_counts.get("unknown", 0))
        data_coverage["parsed_source_counts"] = parsed_source_counts
        data_coverage.setdefault("analysis_source_counts", {})
        data_coverage.setdefault("content_format_counts", content_counts)
        data_coverage.setdefault("duration_source_counts", {})
        data_coverage.setdefault("skipped_sources_with_reason", {})
        data_coverage.setdefault("ad_skip_summary", [])
        data_coverage.setdefault("warnings", [])
        risk_overall = build_overall_risk(run["bias_risk_score"], insights.get("shorts_analysis", {}))

        # --- Sejong & Data Quality Enhancements ---
        has_estimated_duration = any(e.get("is_duration_estimated") for e in events)
        has_duration = any(e.get("time_delta_sec") is not None or e.get("estimated_duration_sec") is not None for e in events if e.get("action_type") == "view")
        
        # Determine nlp_provider
        nlp_providers = [r.get("nlp_provider") for r in nlp_results if r.get("nlp_provider") is not None]
        nlp_provider = "gcp" if "gcp" in nlp_providers else "rule_based_fallback"
        
        avg_category_confidence = 0.0
        category_confidences = [r.get("category_confidence") for r in nlp_results if r.get("category_confidence") is not None]
        if category_confidences:
            avg_category_confidence = sum(category_confidences) / len(category_confidences)

        # Dynamic main category and candidates
        main_category = "❓ 기타/미분류"
        category_source = "fallback_failed"
        category_candidates = []
        if nlp_results:
            cat_counter = Counter([r.get("local_category") for r in nlp_results if r.get("local_category")])
            if cat_counter:
                main_category = cat_counter.most_common(1)[0][0]
            cand_scores = {}
            for r in nlp_results:
                cands = r.get("category_candidates") or []
                for c in cands:
                    c_name = c.get("name")
                    c_score = c.get("score")
                    if c_name and c_score:
                        cand_scores[c_name] = cand_scores.get(c_name, 0.0) + c_score
            if cand_scores:
                sorted_cands = sorted(cand_scores.items(), key=lambda x: x[1], reverse=True)
                category_candidates = [{"name": name, "score": round(score, 2)} for name, score in sorted_cands[:3]]
                category_source = nlp_results[0].get("category_source", "rule_based_metadata")

        top_keywords = []
        for r in nlp_results:
            kw_json = r.get("keywords_json")
            if kw_json:
                try:
                    import json
                    kws = json.loads(kw_json)
                    for item in kws:
                        if isinstance(item, list) or isinstance(item, tuple):
                            top_keywords.append(item[0])
                        else:
                            top_keywords.append(str(item))
                except Exception:
                    pass
        top_keywords = [kw for kw, _ in Counter(top_keywords).most_common(5)]

        duration_q = "actual"
        if not has_duration:
            duration_q = "missing"
        elif has_estimated_duration:
            duration_q = "estimated"
            
        search_count = sum(1 for e in events if e.get("action_type") == "search")
        search_q = "present" if search_count > 0 else "missing_or_limited"
        
        data_quality = {
            "duration": duration_q,
            "source": "full" if len(events) >= 10 else "partial",
            "search_history": search_q,
            "nlp_provider": nlp_provider,
            "category_confidence": round(avg_category_confidence, 2)
        }

        estimated_fields = []
        if has_estimated_duration:
            estimated_fields.append("time_delta_sec")
            estimated_fields.append("shorts_analysis.dopamine_loop_score")

        score_basis = {
            "duration_source": "simulated_takeout_intervals" if has_estimated_duration else "youtube_api_metadata",
            "nlp_source": "google_cloud_nlp_v2" if nlp_provider == "gcp" else "local_keyword_fallback_v2"
        }

        nlp_summary = {
            "main_category": main_category,
            "category_source": category_source,
            "category_confidence": round(avg_category_confidence, 2),
            "top_keywords": top_keywords,
            "category_candidates": category_candidates
        }

        # Inject legacy mapping warning if balance_type is different from dsao_type code
        if mbti_code != actual_dsao_code:
            if "P14_DSAO_LEGACY_MAPPING" not in exception_codes:
                exception_codes.append("P14_DSAO_LEGACY_MAPPING")
                score_warnings = build_score_warnings(exception_codes)

        # DSAO confidence runtime assessment
        dsao_confidence_val = "높음"
        if len(events) < 15:
            dsao_confidence_val = "낮음 (분석 대상 기록 수량 부족)"
        elif has_estimated_duration or nlp_provider == "rule_based_fallback" or avg_category_confidence < 0.5:
            dsao_confidence_val = "보통 (추정 체류 시간 및 로컬 형태소 엔진 기반)"

        # Construct dynamic based_on patterns explaining the typing
        behavioral_patterns = []
        behavioral_patterns.append(f"주도성 지표(UAS) {round(uas_score, 1)}%로 {'스스로 직접 검색하고 클릭하는 D(주도) 성향이' if uas_score >= 50.0 else '알고리즘 추천 피드를 수용하는 P(추천) 성향이'} 강함")
        behavioral_patterns.append(f"주제 다양성 지표(TDS) {round(tds_score, 1)}%로 {'다양한 분야를 고르게 넘나드는 W(넓은 관심) 성향' if tds_score >= 50.0 else '특정 카테고리에 집중하는 N(집중 관심) 성향'} 매칭")
        behavioral_patterns.append(f"안전성 지표(SMS) {round(100.0 - sms_score, 1)}% 자극성 비중으로 {'안정적이고 학습적인 소비를 보여주는 M(안정) 성향' if sms_score >= 50.0 else '자극적이거나 숏폼 중심의 S(자극) 성향'} 매칭")
        behavioral_patterns.append(f"시청 롱폼(180초 이상) 비중 {round(long_ratio, 1)}%로 {'호흡이 긴 롱폼에 몰입하는 L(롱폼) 성향' if long_ratio >= 50.0 else '빠른 템포의 숏폼에 최적화된 F(숏폼) 성향'} 매칭")
        
        matched_kws_str = ", ".join(top_keywords[:3]) if top_keywords else "감지된 주요 키워드 부족"
        dsao_based_on = (
            f"유형 결정 요소: {', '.join(behavioral_patterns)}. "
            f"근거 키워드: [{matched_kws_str}]. "
            f"주요 관심 분야: '{main_category}'"
        )

        actual_dsao_details = persona_loader.get_dsao_detail(actual_dsao_code)
        
        actual_dsao_response = {
            "code": actual_dsao_code,
            "name": actual_dsao_name,
            "short_summary": actual_dsao_details.get("short_summary", "호기심 스낵 러너"),
            "detailed_description": actual_dsao_details.get("detailed_description", actual_dsao_details.get("description", "")),
            "strengths": actual_dsao_details.get("strengths", []),
            "risks": actual_dsao_details.get("risks", []),
            "recommended_detox_direction": actual_dsao_details.get("recommended_detox_direction", ""),
            "similar_types": actual_dsao_details.get("similar_types", []),
            "opposite_type": actual_dsao_details.get("opposite_type", ""),
            "confidence": dsao_confidence_val,
            "based_on": dsao_based_on,
            "scores": {
                "D": round(uas_score, 1),
                "P": round(100.0 - uas_score, 1),
                "W": round(tds_score, 1),
                "N": round(100.0 - tds_score, 1),
                "S": round(100.0 - sms_score, 1),
                "M": round(sms_score, 1),
                "F": round(100.0 - long_ratio, 1),
                "L": round(long_ratio, 1)
            }
        }

        # --- [NEW] Calculate Explanations for key scores ---
        health_confidence_desc = "낮은 신뢰도" if overall_confidence == "low" else ("보통 신뢰도" if overall_confidence == "medium" else "높은 신뢰도")
        health_caution = "시청 기록에 시청 지속 시간 정보가 없으므로 기록 간 간격 및 비디오 길이를 바탕으로 '추정 체류 시간'을 시뮬레이션하여 계산했습니다. 일부 장기 방치 세션 등 현실 왜곡 가능성이 존재합니다. (기록 기반 추정값)" if has_estimated_duration else "사용자 YouTube Takeout 파일에 기록된 데이터 범위 내에서 계산된 지표입니다."
        
        health_explanation = {
            "label": "종합 미디어 건강 점수",
            "value": f"{round(run['weighted_health'], 1)}점",
            "reason": f"6개 핵심 미디어 소비 지표의 가중 평균값으로, 전반적인 미디어 소비의 건강함을 나타냅니다. 현재 {health_confidence_desc} 상태입니다.",
            "evidence": f"사용자 주도성({round(uas_score, 1)}점), 주제 다양성({round(tds_score, 1)}점), 자극성 안전({round(sms_score, 1)}점) 등 6대 축 점수 조합",
            "caution": health_caution,
            "improvement_hint": "가장 점수가 낮은 영역의 미션(예: 직접 검색어 지정하기, 낯선 카테고리 클릭 등)을 실행하여 전반적인 밸런스를 높이세요."
        }

        if misconception_index is not None:
            misconception_val = f"{misconception_index}점"
            misconception_reason = f"자가진단 설문에서 본인이 응답한 수치와 실제 YouTube 시청 데이터에서 추출된 수치 간의 평균 격차율입니다. {worst_gap_name} 영역에서 가장 큰 불일치가 관찰되었습니다."
            misconception_evidence = f"가장 불일치가 큰 지표: {worst_gap_name} (격차 {worst_gap_val}점)"
            misconception_hint = f"자가진단 시점의 기억과 실제 시청 패턴이 다르므로, 특히 {worst_gap_name} 영역에 대해 의도적인 디지털 디독스 가이드를 실행해 보는 것을 추천합니다."
        else:
            misconception_val = "확인 불가"
            misconception_reason = "사전 자가진단 프로필 설문 응답 결과가 없어 메타인지 격차 점수가 활성화되지 않았습니다."
            misconception_evidence = "자가진단 데이터 부재"
            misconception_hint = "프로필 설문을 진행하시면 자가 인식 점수와 실제 시청 통계의 격차를 실시간으로 분석해 드립니다."

        misconception_explanation = {
            "label": "메타인지 착각 지수",
            "value": misconception_val,
            "reason": misconception_reason,
            "evidence": misconception_evidence,
            "caution": "본 자가인식 격차는 사용자의 주관적 설문 응답과 구글 테이크아웃 데이터에만 의존하며, 데이터 규모가 작을 경우 분석 신뢰도가 낮아질 수 있습니다.",
            "improvement_hint": misconception_hint
        }

        dsao_explanation = {
            "label": "실제 시청 기반 미디어 유형 (Actual DSAO)",
            "value": f"{actual_dsao_code} ({actual_dsao_name})",
            "reason": f"사용자의 행동 패턴(주도성, 다양성, 안전성, 시청 길이)을 조합하여 분류한 최종 미디어 성향 유형입니다. (4-letter type code representing 16 possible types)",
            "evidence": dsao_based_on,
            "caution": "시청 기록에 체류 시간 정보가 확인 불가하여 인접 이벤트 간 간격을 바탕으로 '추정 체류 시간'을 적용하였으므로 롱폼/숏폼 구분은 참고용으로 신뢰성이 제한될 수 있습니다. (기록 기반 추정값)",
            "improvement_hint": f"현재 '{actual_dsao_name}' 성향의 단점을 보완하기 위해 '{actual_dsao_details.get('recommended_detox_direction', '디톡스 가이드 참고')}'을 실천해 보세요."
        }

        category_shares = insights.get("category_shares", [])
        shorts_count_val = insights.get("shorts_analysis", {}).get("shorts_count", 0)
        shorts_risk_val = risk_overall.get("shorts_stimulation_risk", 0)

        bias_explanation = {
            "label": "관심사 편중도",
            "value": f"{round(run['bias_risk_score'], 1)}점",
            "reason": "특정 주제 카테고리에 편향되거나 특정 정보원의 영상에 반복적으로 지나치게 과다 노출되는 정도를 의미합니다.",
            "evidence": f"최상위 카테고리 '{main_category}' 비중 {category_shares[0]['value'] if category_shares else 0}% 점유 및 주요 검색 키워드 반복량",
            "caution": "Google Takeout 파일 내 정보 부족 시 로컬 규칙 및 형태소 분석 기반으로 계산되므로 카테고리 세분성에 한계가 발생할 수 있습니다. (낮은 신뢰도)",
            "improvement_hint": "반대 관심사의 공영 방송 뉴스를 시청하거나, 검색창에 평소 치지 않던 주제어를 직접 쳐서 인지 균형을 도모하세요."
        }

        ebs_score = axis_scores.get("EBS", 50.0)
        stim_explanation = {
            "label": "자극성 및 불안정성 관련 지표",
            "value": f"자극 위험 {shorts_risk_val}점 · 정서 안정 {round(ebs_score, 1)}점",
            "reason": "시청 텍스트의 부정적/자극적 톤앤매너 노출 빈도와 숏츠 반복 소비 패턴으로 인한 도파민 루프 위험도를 종합한 지표입니다.",
            "evidence": f"숏츠 감지 개수 {shorts_count_val}개 및 연속 숏츠 루프 점수, 타이틀 내 자극성/불안정 키워드 출현 비중",
            "caution": "Google Takeout 원본에는 실제 시청 지속 시간 정보가 확인 불가하여 1초만 시청하고 끈 영상도 연속 시청한 것으로 과잉 추정될 수 있습니다. (기록 기반 추정값)",
            "improvement_hint": "숏츠 연속 재생을 끊어내기 위해 유튜브 자동재생 옵션을 끄고, ASMR이나 자연 다큐멘터리 같은 잔잔한 교양 콘텐츠 비율을 늘려보세요."
        }

        dq_explanation = {
            "label": "데이터 품질 분석",
            "value": f"체류시간: {data_quality.get('duration', 'unknown')} · NLP: {data_quality.get('nlp_provider', 'unknown')}",
            "reason": "분석에 사용된 원본 Takeout 파일의 데이터 정합성과 사용된 분석 엔진(GCP/로컬 세종)을 평가한 신뢰성 지표입니다.",
            "evidence": f"체류시간 추정 여부({data_quality.get('duration')}), 언어 분석 수준({data_quality.get('nlp_provider')}), 평균 카테고리 신뢰도({data_quality.get('category_confidence')})",
            "caution": "구글 테이크아웃에서 시청 지속 시간이 확인 불가한 원천적 제약으로 인해, 체류 시간 데이터는 모두 기록 기반 추정값(estimated)으로 처리됩니다.",
            "improvement_hint": "품질 수준을 높여 더 정확히 진단하기 위해 향후 브라우저 확장 프로그램 기반의 실제 시청/정지 시간 수집 모델을 적용할 예정입니다."
        }

        explanations = {
            "weighted_health_score": health_explanation,
            "cognitive_misconception_index": misconception_explanation,
            "dsao_actual_type": dsao_explanation,
            "bias_risk_score": bias_explanation,
            "shorts_stimulation_risk": stim_explanation,
            "data_quality_flags": dq_explanation
        }

        return {
            "run_id": run_id,
            "user": {
                "nickname": profile.get("nickname", "사용자"),
                "email": profile.get("email", "user@example.com")
            },
            "survey_fallback": survey_fallback,
            "bias_risk_score": run["bias_risk_score"],
            "information_bias_risk": run.get("information_bias_risk", risk_overall["information_bias_risk"]),
            "shorts_stimulation_risk": run.get("shorts_stimulation_risk", risk_overall["shorts_stimulation_risk"]),
            "final_detox_risk": run.get("final_detox_risk", risk_overall["final_detox_risk"]),
            "shorts_weight": risk_overall["shorts_weight"],
            "weighted_health": run["weighted_health"],
            "internal_balance_type": mbti_code,
            "legacy_type": mbti_code,
            "balance_type": {
                "code": mbti_code,
                "name": mbti_details[0],
                "tags": mbti_details[1]
            },
            "mbti": {
                "code": mbti_code,
                "name": mbti_details[0],
                "tags": mbti_details[1]
            },
            "dsao_type": {
                "code": actual_dsao_code,
                "name": actual_dsao_name,
                "description": "4-letter type code representing 16 possible types",
                "is_duration_estimated": has_estimated_duration,
                "scores": {
                    "D": round(uas_score, 1),
                    "P": round(100.0 - uas_score, 1),
                    "W": round(tds_score, 1),
                    "N": round(100.0 - tds_score, 1),
                    "S": round(100.0 - sms_score, 1),
                    "M": round(sms_score, 1),
                    "F": round(100.0 - long_ratio, 1),
                    "L": round(long_ratio, 1)
                }
            },
            "actual_dsao": actual_dsao_response,
            "explanations": explanations,
            "exception_codes": exception_codes,
            "score_warnings": score_warnings,
            "data_coverage": data_coverage,
            "insights": insights,
            "meta_gap_available": meta_gap_available,
            "meta_gap": meta_gap,
            "misconception": {
                "index": misconception_index,
                "worst_axis_code": worst_gap_code,
                "worst_axis_name": worst_gap_name,
                "worst_gap_value": worst_gap_val,
                "message": misconception_message
            },
            "excluded_axes": excluded_axes,
            "overall_confidence": overall_confidence,
            "sampling_metadata": sampling_metadata,
            "score_details": score_details,
            "data_quality_flags": data_quality_flags,
            "data_quality": data_quality,
            "warnings": score_warnings,
            "score_basis": score_basis,
            "estimated_fields": estimated_fields,
            "nlp_summary": nlp_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard rendering failed: {str(e)}")
