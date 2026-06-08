import json
import logging
import os
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

FALLBACK_MISSIONS = [
    {
        "mission_id": "tds_m1",
        "title": "낯선 카테고리 하나 구경하기",
        "description": "평소 전혀 보지 않던 '교양/다큐' 섹션 영상을 하나 클릭하고 무엇에 관한 것인지 확인해 보세요.",
        "target_flags": ["TDS_LOW"],
        "difficulty": "low",
        "estimated_minutes": 5,
        "requires_proof": False,
        "enabled": True,
        "input_type": "choice",
        "choices": ["역사/문학", "예술/디자인", "우주/자연과학", "경제/비즈니스"]
    },
    {
        "mission_id": "sbs_m1",
        "title": "서로 다른 언론사 뉴스 헤드라인 체크",
        "description": "두 개의 서로 다른 언론사의 동일 이슈 관련 뉴스를 읽어본 뒤, 더 객관적이라고 느껴지는 논조를 골라보세요.",
        "target_flags": ["SBS_LOW"],
        "difficulty": "low",
        "estimated_minutes": 10,
        "requires_proof": False,
        "enabled": True,
        "input_type": "choice",
        "choices": ["언론사 A가 객관적", "언론사 B가 객관적", "두 관점이 균형 잡힘"]
    },
    {
        "mission_id": "uas_m1",
        "title": "영상 재생 전 '클릭 의도' 멈춤 및 선택",
        "description": "영상을 클릭하여 시청하기 전, 내가 이 영상을 왜 누르는지 이유를 가볍게 골라보세요.",
        "target_flags": ["UAS_LOW"],
        "difficulty": "low",
        "estimated_minutes": 1,
        "requires_proof": False,
        "enabled": True,
        "input_type": "choice",
        "choices": ["정보 습득", "오락 및 기분전환", "무의식적 습관", "심심함"]
    }
]

class MissionLoader:
    def __init__(self):
        self.missions_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "missions", "detox_missions.v1.json"
        )
        self.missions: List[Dict[str, Any]] = []
        self.load_missions()

    def load_missions(self):
        if not os.path.exists(self.missions_file):
            logger.warning(f"Missions JSON file not found at {self.missions_file}. Using minimal fallback.")
            self.missions = FALLBACK_MISSIONS
            return

        try:
            with open(self.missions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Root element of missions file must be a JSON list.")
            
            validated_missions = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                # Verify required fields
                required = ["mission_id", "title", "description", "difficulty", "estimated_minutes", "requires_proof", "enabled"]
                if any(k not in item for k in required):
                    continue
                if item.get("enabled", True):
                    validated_missions.append(item)
            
            if not validated_missions:
                raise ValueError("No valid mission entries found after schema validation.")
            self.missions = validated_missions
            logger.info(f"Successfully loaded {len(self.missions)} detox missions from JSON.")

        except Exception as e:
            logger.warning(f"Error loading missions from JSON: {e}. Using fallback defaults.")
            self.missions = FALLBACK_MISSIONS

    def filter_missions(self, target_flags: List[str] = None, dsao_type: str = None) -> List[Dict[str, Any]]:
        results = []
        for m in self.missions:
            # Match target flags
            if target_flags:
                m_flags = m.get("target_flags", [])
                if not any(f in target_flags for f in m_flags):
                    continue
            # Match DSAO type
            if dsao_type:
                m_dsao = m.get("target_dsao_types", [])
                if m_dsao and dsao_type not in m_dsao:
                    continue
            results.append(m)
        return results if results else self.missions[:2]

    def recommend_missions(
        self,
        keywords: List[str],
        local_category: str,
        category_candidates: List[str],
        category_confidence: float,
        actual_dsao: str,
        data_quality_flags: List[str],
        warning_codes: List[str],
        axis_scores: Dict[str, float],
        bias_risk_score: float,
        shorts_count: int,
        shorts_stimulation_risk: int
    ) -> List[Dict[str, Any]]:
        scored_missions = []
        for m in self.missions:
            # 1. Exclude missions requiring proof by default
            if m.get("requires_proof", False):
                continue
            
            score = 10.0
            if m.get("difficulty") == "low":
                score += 5.0
            if m.get("estimated_minutes", 10) <= 5:
                score += 3.0
                
            # Match DSAO
            dsao_types = m.get("target_dsao_types", [])
            dsao_matched = False
            if dsao_types:
                if actual_dsao in dsao_types:
                    score += 8.0
                    dsao_matched = True
            else:
                score += 2.0
                
            # Match flags (TDS_LOW, SBS_LOW, UAS_LOW, SHORTS_HIGH)
            target_flags = m.get("target_flags", [])
            flag_matched = False
            matched_flag_name = ""
            for f in target_flags:
                if f == "TDS_LOW" and (axis_scores.get("TDS", 50.0) < 50.0 or "P02_TOPIC_SAMPLE_LIMITED" in warning_codes):
                    score += 10.0
                    flag_matched = True
                    matched_flag_name = "주제 다양성 부족"
                elif f == "SBS_LOW" and (axis_scores.get("SBS", 50.0) < 50.0 or "P05_SOURCE_SAMPLE_LIMITED" in warning_codes or "P05_SOURCE_MISSING" in warning_codes):
                    score += 10.0
                    flag_matched = True
                    matched_flag_name = "출처 균형 부족"
                elif f == "UAS_LOW" and (axis_scores.get("UAS", 50.0) < 50.0 or "P04_NO_SEARCH" in warning_codes):
                    score += 10.0
                    flag_matched = True
                    matched_flag_name = "사용자 주도성 부족"
                elif f == "SHORTS_HIGH" and (shorts_count > 0 or shorts_stimulation_risk > 40 or "P10_DURATION_ESTIMATED" in warning_codes):
                    score += 12.0
                    flag_matched = True
                    matched_flag_name = "숏츠 과다 노출"

            # Match Categories
            target_cats = m.get("target_categories", [])
            cat_matched = False
            matched_cat_name = ""
            if target_cats:
                all_cats = [local_category] + category_candidates
                for c in all_cats:
                    if not c:
                        continue
                    c_clean = c.split()[-1] if len(c.split()) > 1 else c
                    for tc in target_cats:
                        tc_clean = tc.split()[-1] if len(tc.split()) > 1 else tc
                        if c_clean in tc_clean or tc_clean in c_clean:
                            score += 8.0
                            cat_matched = True
                            matched_cat_name = c
                            break
                    if cat_matched:
                        break

            # Match Keywords
            rel_kws = m.get("related_keywords", [])
            kw_matched = False
            matched_kw_name = ""
            for kw in keywords:
                if not kw:
                    continue
                for rk in rel_kws:
                    if kw in rk or rk in kw:
                        score += 5.0
                        kw_matched = True
                        matched_kw_name = kw
                        break
                if kw_matched:
                    break
            
            # Match warnings
            warning_matched = False
            matched_warning_name = ""
            for wc in warning_codes + data_quality_flags:
                if wc == "P10_DURATION_ESTIMATED" and m.get("mission_id") == "shorts_m1":
                    score += 5.0
                    warning_matched = True
                    matched_warning_name = "추정 체류 시간 사용"
                elif wc == "P15_NLP_FALLBACK_USED" and "TDS" in target_flags:
                    score += 4.0
                    warning_matched = True
                    matched_warning_name = "형태소 분석 폴백"
                elif wc == "P16_CATEGORY_CONFIDENCE_LOW" and "TDS" in target_flags:
                    score += 4.0
                    warning_matched = True
                    matched_warning_name = "카테고리 낮은 신뢰도"

            if bias_risk_score > 50.0:
                score += 3.0

            # Confidence calculation
            match_indicators = [dsao_matched, cat_matched, flag_matched or warning_matched, kw_matched]
            num_matches = sum(1 for indicator in match_indicators if indicator)
            if num_matches >= 3:
                confidence = "HIGH"
            elif num_matches >= 1:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            # Personal explanation logic for why_recommended
            reasons = []
            if dsao_matched:
                reasons.append(f"DSAO {actual_dsao} 성향 분석 결과 반영")
            if cat_matched and matched_cat_name:
                reasons.append(f"많이 소비하신 '{matched_cat_name}' 카테고리 환기")
            if kw_matched and matched_kw_name:
                reasons.append(f"자주 등장한 키워드 '{matched_kw_name}' 관심사 우회")
            if flag_matched and matched_flag_name:
                reasons.append(f"지표상 감지된 '{matched_flag_name}' 보완")
            if warning_matched and matched_warning_name:
                reasons.append(f"'{matched_warning_name}' 분석 참고 안내 보완")

            if not reasons:
                reasons.append("가벼운 일상 환기 루틴 제안")

            why_rec = ", ".join(reasons) + "을(를) 위해 이 미션이 추천되었습니다."

            scored_missions.append({
                "score": score,
                "mission_id": m["mission_id"],
                "id": m["mission_id"],
                "title": m["title"],
                "description": m["description"],
                "why_recommended": why_rec,
                "target_issue": m.get("target_issue", "미디어 소비 습관 개선"),
                "estimated_minutes": m.get("estimated_minutes", 5),
                "difficulty": m["difficulty"],
                "effort_level": m["difficulty"],
                "requires_proof": m.get("requires_proof", False),
                "expected_effect": m.get("expected_effect", "균형 잡힌 소비"),
                "related_keywords": m.get("related_keywords", []),
                "confidence": confidence,
                "success_condition": "미션 참여 완료 후 소감 기록",
                "input_type": m.get("input_type", "text"),
                "choices": m.get("choices")
            })

        scored_missions.sort(key=lambda x: x["score"], reverse=True)
        return scored_missions[:3]

mission_loader = MissionLoader()

def generate_mock_plan_data(
    lowest_axis: str,
    dominant_topics: List[str],
    shorts_count: int,
    shorts_stimulation_risk: int,
    keyword_hint: str = "반복 주제"
) -> Dict[str, Any]:
    """
    Decouples gemini.py from direct loaders dependency.
    Provides overall summary, reverse queries, and matches missions dynamically from loaded rules.
    """
    keywords = [keyword_hint] + dominant_topics
    local_category = dominant_topics[0] if dominant_topics else "기타/미분류"
    category_candidates = dominant_topics[1:]
    category_confidence = 0.8
    actual_dsao = "PNMF" if lowest_axis == "UAS" else "DWSF"
    data_quality_flags = ["duration_estimated"] if shorts_count > 0 else []
    warning_codes = ["P10_DURATION_ESTIMATED"] if shorts_count > 0 else []
    axis_scores = {lowest_axis: 35.0}
    bias_risk_score = 45.0
    
    recs = mission_loader.recommend_missions(
        keywords=keywords,
        local_category=local_category,
        category_candidates=category_candidates,
        category_confidence=category_confidence,
        actual_dsao=actual_dsao,
        data_quality_flags=data_quality_flags,
        warning_codes=warning_codes,
        axis_scores=axis_scores,
        bias_risk_score=bias_risk_score,
        shorts_count=shorts_count,
        shorts_stimulation_risk=shorts_stimulation_risk
    )
    
    overall_summary = ""
    reverse_queries = []
    
    if lowest_axis == "TDS":
        overall_summary = f"소비 중인 콘텐츠 주제가 '{', '.join(dominant_topics[:2])}'에 다소 집중되어 있어 관심 영역의 편향 가능성이 있습니다. 수동 소비 흐름에서 벗어나 새로운 카테고리의 유익 정보를 가볍게 탐색하며 뇌의 균형 잡힌 자극을 유도하는 루틴을 제안합니다."
        reverse_queries = [
            {"query_text": "역사 및 세계사 핵심 정리 다큐", "expected_topic": "History", "why_this_helps": "IT 및 정보 위주의 관심사에서 인문학 교양으로 영역을 다양하게 넓혀 줍니다."},
            {"query_text": "현대 미술 쉽게 감상하는 법", "expected_topic": "Arts", "why_this_helps": "낯선 주제의 영상을 통해 시각적 자극을 다양화하고 폭넓은 미디어 관찰 능력을 돕습니다."}
        ]
    elif lowest_axis == "SBS":
        overall_summary = "소수 채널이나 유사 정보원의 영상만 지속 수용하여 편향적 확신이 생길 가능성이 관찰됩니다. 균형 잡힌 시각 형성을 돕기 위해 공영 언론사나 국제 외신 등의 신뢰도 높은 다른 정보원들을 가볍게 비교 분석해보는 루틴을 권장합니다."
        reverse_queries = [
            {"query_text": "공영방송 대기획 다큐멘터리", "expected_topic": "News", "why_this_helps": "1인 미디어 편중에서 탈피해 고도의 팩트체크를 거친 공인 정보원으로 출처 균형을 도모합니다."},
            {"query_text": "국제 시사 보도 및 시각 비교", "expected_topic": "Global News", "why_this_helps": "국내 크리에이터의 관점을 넘어 다각도의 균형 잡힌 세계적 안목을 돕습니다."}
        ]
    else:
        overall_summary = "알고리즘 추천 영상 피드의 연속 노출 및 자동 시청의 영향으로 미디어 소비 주도성이 감소한 경향성이 발견되었습니다. 의도적인 단어 검색과 클릭 전 짧은 생각 루틴을 통해 수동적 흐름을 완화하고 미디어 조절 능력을 복원하는 데 도움을 드립니다."
        reverse_queries = [
            {"query_text": "미디어 소비 조절과 디지털 웰빙", "expected_topic": "Lifestyle", "why_this_helps": "수동적 추천 노출에서 주체적인 사용 패턴 개선 방향을 직접 인지하도록 돕습니다."},
            {"query_text": "자연의 소리 명상 유도", "expected_topic": "Health", "why_this_helps": "빠르고 자극적인 전개가 아닌 소리와 흐름에 집중하여 뇌의 휴식과 여유를 유도합니다."}
        ]

    if shorts_count > 0:
        overall_summary += (
            f" 숏츠는 관심사 편향 점수에 직접 섞지 않고, 짧은 영상 반복 소비 루프 관점에서 별도로 참고했습니다."
            f" 현재 숏츠 자극 소비 위험은 {shorts_stimulation_risk}점입니다. (기록 기반 추정값)"
        )

    for idx, r in enumerate(recs, 1):
        r["id"] = f"m{idx}"

    return {
        "overall_summary": overall_summary,
        "reverse_queries": reverse_queries,
        "missions": recs
    }

