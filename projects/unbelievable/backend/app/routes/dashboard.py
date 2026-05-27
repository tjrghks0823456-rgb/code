import logging
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from app.core.database import db_client
from app.core.scoring import PERSONALITY_MAP

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
        events = db_client.fetch_data("norm_event", {"file_id": file_id})
        view_events = [e for e in events if e.get("action_type") == "view"]
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
