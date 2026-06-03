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

logger = logging.getLogger(__name__)
router = APIRouter()

AXIS_NAMES = {
    "TDS": "주제 다양성",
    "SBS": "출처 균형",
    "EBS": "감정 균형",
    "VOS": "관점 개방성",
    "SMS": "유해/자극 안전",
    "UAS": "사용자 주도성",
    "ALL": "전체 지표"
}

SCORE_WARNING_MAP: Dict[str, Dict[str, str]] = {
    "P01_DATA_SHORT": {
        "axis": "ALL",
        "message": "분석 가능한 시청 이벤트가 부족하여 전체 지표는 참고용으로 표시됩니다."
    },
    "P02_TOPIC_SAMPLE_LIMITED": {
        "axis": "TDS",
        "message": "주제 카테고리 샘플이 부족하여 주제 다양성 지표는 참고용으로 표시됩니다."
    },
    "P02_SHORT_TEXT": {
        "axis": "TDS",
        "message": "분석 가능한 텍스트가 부족하여 주제 다양성 지표는 참고용으로 표시됩니다."
    },
    "P03_SENTIMENT_SAMPLE_LIMITED": {
        "axis": "EBS",
        "message": "감정 분석 샘플이 부족하여 감정 균형 지표는 참고용으로 표시됩니다."
    },
    "P04_NO_SEARCH": {
        "axis": "UAS",
        "message": "검색 기록 데이터가 포함되지 않았거나 검색 이벤트가 감지되지 않아 사용자 주도성 지표는 참고용으로 표시됩니다."
    },
    "P05_SOURCE_MISSING": {
        "axis": "SBS",
        "message": "채널 또는 출처 정보가 확인되지 않아 출처 균형 지표는 참고용으로 표시됩니다."
    },
    "P05_SOURCE_SAMPLE_LIMITED": {
        "axis": "SBS",
        "message": "유효한 채널 또는 출처 종류가 부족하여 출처 균형 지표는 참고용으로 표시됩니다."
    },
    "P06_VIEWPOINT_SAMPLE_LIMITED": {
        "axis": "VOS",
        "message": "분석 가능한 주제 샘플이 부족하여 관점 개방성 지표는 참고용으로 표시됩니다."
    },
    "P07_SAFETY_SAMPLE_LIMITED": {
        "axis": "SMS",
        "message": "유해/자극 안전성을 판단할 NLP 샘플이 부족하여 해당 지표는 참고용으로 표시됩니다."
    }
}

SCORE_WARNING_MAP.update({
    "P08_MOCK_DATA_USED": {
        "axis": "ALL",
        "message": "Mock analysis data was detected, so related scores should be read as low-confidence references."
    },
    "P09_FALLBACK_DATA_USED": {
        "axis": "ALL",
        "message": "Fallback analysis data was detected, so related scores should be read as low-confidence references."
    },
    "P10_DIRECT_SELECTION_UNAVAILABLE": {
        "axis": "UAS",
        "message": "Direct selection ratio is not available in the current normalized event schema."
    }
})

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
    if not topic_shares:
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
    algorithm_interest_summary = (
        " · ".join(item["name"] for item in topic_shares[:3])
        if topic_shares
        else (" · ".join(item["name"] for item in channel_shares[:3]) if channel_shares else "분류 데이터 부족")
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
        "algorithm_interest_summary": algorithm_interest_summary
    }

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    run_id: str,
    user_id: str = "00000000-0000-0000-0000-000000000001"
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
        
        exception_codes = normalize_exception_codes(run.get("exception_codes", []))
        score_warnings = build_score_warnings(exception_codes)

        for code, name in AXIS_NAMES.items():
            if code == "ALL":
                continue

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
        
        DSAO_NAMES = {
            "DWSF": "다채로운 숏폼 탐색형",
            "DWSL": "다채로운 롱폼 탐색형",
            "DWMF": "지식 스낵 탐색형",
            "DWML": "깊이 있는 지식 항해형",
            "DNSF": "특정 관심 숏폼 집중형",
            "DNSL": "특정 주제 장기 몰입형",
            "DNMF": "전문 정보 압축형",
            "DNML": "한우물 연구형",
            "PWSF": "추천 피드 유람형",
            "PWSL": "자동재생 감상형",
            "PWMF": "편안한 정보 스낵형",
            "PWML": "편안한 롱폼 흐름형",
            "PNSF": "추천 피드 반복형",
            "PNSL": "추천 주제 정주행형",
            "PNMF": "조용한 추천 루틴형",
            "PNML": "자동재생 한우물형"
        }
        actual_dsao_name = DSAO_NAMES.get(actual_dsao_code, "미지의 미디어 탐험가")
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
        risk_overall = build_overall_risk(run["bias_risk_score"], insights.get("shorts_analysis", {}))
        
        return {
            "run_id": run_id,
            "user": {
                "nickname": profile["nickname"],
                "email": profile["email"]
            },
            "bias_risk_score": run["bias_risk_score"],
            "information_bias_risk": run.get("information_bias_risk", risk_overall["information_bias_risk"]),
            "shorts_stimulation_risk": run.get("shorts_stimulation_risk", risk_overall["shorts_stimulation_risk"]),
            "final_detox_risk": run.get("final_detox_risk", risk_overall["final_detox_risk"]),
            "shorts_weight": risk_overall["shorts_weight"],
            "weighted_health": run["weighted_health"],
            "mbti": {
                "code": mbti_code,
                "name": mbti_details[0],
                "tags": mbti_details[1]
            },
            "actual_dsao": {
                "code": actual_dsao_code,
                "name": actual_dsao_name,
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
            "exception_codes": exception_codes,
            "score_warnings": score_warnings,
            "data_coverage": data_coverage,
            "insights": insights,
            "meta_gap": meta_gap,
            "misconception": {
                "index": misconception_index,
                "worst_axis_code": max_gap_axis,
                "worst_axis_name": AXIS_NAMES[max_gap_axis],
                "worst_gap_value": round(meta_gap[max_gap_axis]["gap"], 1),
                "message": f"스스로 사전 인지했던 점수 대비 실제 YouTube 소비 데이터상으로 '{AXIS_NAMES[max_gap_axis]}' 영역의 차이가 가장 크게 집계되었습니다. 가벼운 일상 추천 루틴 수정을 통해 성향의 균형을 복원하시는 것을 추천합니다."
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard rendering failed: {str(e)}")
