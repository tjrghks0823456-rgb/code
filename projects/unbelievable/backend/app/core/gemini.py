import logging
import json
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.is_mock = not self.api_key or self.api_key == "mock-gemini-api-key"

    def _model_name(self) -> str:
        return getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        raw = (text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end >= start:
            raw = raw[start:end + 1]
        return json.loads(raw)
        
    def generate_detox_plan(
        self, 
        risk_score: float, 
        axis_scores: Dict[str, float], 
        mbti_type: str,
        dominant_topics: List[str],
        shorts_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generates structured Reverse Queries and Detox Missions using Gemini 2.5 Flash.
        If using mock credentials, generates high-quality realistic mock responses.
        """
        shorts_analysis = shorts_analysis or {}
        if self.is_mock:
            return self._generate_mock_plan(risk_score, axis_scores, mbti_type, dominant_topics, shorts_analysis)
            
        try:
            # Placeholder for actual Gemini API call utilizing google-generativeai SDK
            # with response_mime_type="application/json" and response_schema.
            # (Included in prototype for easy replacement/connection)
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self._model_name())
            
            prompt = f"""
            Analyze this media consumption profile:
            - Bias Risk Score: {risk_score} (0 is healthy, 100 is highly biased/polarized)
            - 6-Axis Scores (TDS, SBS, EBS, VOS, SMS, UAS): {json.dumps(axis_scores)}
            - Personality Type: {mbti_type}
            - Dominant Topics Consumed: {json.dumps(dominant_topics)}
            - Backend-computed shorts analysis: {json.dumps(shorts_analysis, ensure_ascii=False)}
            
            Generate a JSON containing:
            1. overall_summary: A 2-3 sentence academic explanation.
            2. reverse_queries: 3 alternative search query objects (query_text, expected_topic, why_this_helps).
            3. missions: A 3-day plan containing action items (id, title, description, success_condition, effort_level, input_type, choices).
            Do not invent scores. Use shorts_analysis only to explain short-form repeated consumption loops and to suggest gentle 1-3 minute reset missions.
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._extract_json(response.text)
        except Exception as e:
            logger.error(f"Failed to call Gemini API: {e}")
            return self._generate_mock_plan(risk_score, axis_scores, mbti_type, dominant_topics, shorts_analysis)

    def enrich_interest_report(
        self,
        search_interest_map: Dict[str, Any],
        standard_video_interest_map: Dict[str, Any],
        shorts_interest_map: Dict[str, Any],
        interest_gap_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Explain deterministic interest maps without changing scores or categories.
        Uses Gemini only when a real GEMINI_API_KEY is configured.
        """
        if self.is_mock:
            return self._generate_rule_based_interest_report(
                search_interest_map,
                standard_video_interest_map,
                shorts_interest_map,
                interest_gap_report,
                mode="rule_based_fallback",
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self._model_name())

            compact_payload = {
                "search_interest_map": {
                    "total_search_count": search_interest_map.get("total_search_count", 0),
                    "top_keywords": (search_interest_map.get("top_keywords") or [])[:8],
                    "category_distribution": (search_interest_map.get("category_distribution") or [])[:6],
                },
                "standard_video_interest_map": {
                    "total_video_count": standard_video_interest_map.get("total_video_count", 0),
                    "top_keywords": (standard_video_interest_map.get("top_keywords") or [])[:8],
                    "category_distribution": (standard_video_interest_map.get("category_distribution") or [])[:6],
                },
                "shorts_interest_map": {
                    "total_shorts_count": shorts_interest_map.get("total_shorts_count", 0),
                    "top_shorts_keywords": (shorts_interest_map.get("top_shorts_keywords") or [])[:8],
                    "category_distribution": (shorts_interest_map.get("category_distribution") or [])[:6],
                },
                "interest_gap_report": {
                    "interest_mismatch_score": interest_gap_report.get("interest_mismatch_score", 0),
                    "recommendation_flow_candidate_categories": (
                        interest_gap_report.get("recommendation_flow_candidate_categories")
                        or interest_gap_report.get("algorithm_drift_categories")
                        or []
                    )[:5],
                    "intent_matched_categories": (interest_gap_report.get("intent_matched_categories") or [])[:5],
                },
            }
            prompt = f"""
            You are explaining a YouTube Takeout interest-analysis result in Korean.
            Use only the deterministic data below. Do not invent new scores, sources, or paths.
            If shorts_count is 0, clearly say shorts data is insufficient.

            Data:
            {json.dumps(compact_payload, ensure_ascii=False)}

            Return strict JSON with these keys:
            - summary: one concise sentence.
            - search_intent_read: one sentence about active searches.
            - watch_exposure_read: one sentence about standard-video consumption.
            - shorts_read: one sentence about shorts repeated consumption.
            - next_action_hint: one practical next action.
            - confidence: high, medium, or low.
            - warnings: array of short Korean warning strings.
            """

            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            parsed = self._extract_json(response.text)
            parsed["mode"] = "gemini"
            parsed["model"] = self._model_name()
            return self._normalize_interest_report(parsed)
        except Exception as e:
            logger.error(f"Failed to call Gemini interest enrichment: {e}")
            fallback = self._generate_rule_based_interest_report(
                search_interest_map,
                standard_video_interest_map,
                shorts_interest_map,
                interest_gap_report,
                mode="rule_based_fallback",
            )
            fallback["warnings"].append("Gemini 해석 호출에 실패해 룰 기반 요약으로 대체했습니다.")
            return fallback

    def _top_category(self, interest_map: Dict[str, Any]) -> str:
        distribution = interest_map.get("category_distribution") or []
        if not distribution:
            return "데이터 부족"
        return distribution[0].get("category") or distribution[0].get("name") or "데이터 부족"

    def _generate_rule_based_interest_report(
        self,
        search_interest_map: Dict[str, Any],
        standard_video_interest_map: Dict[str, Any],
        shorts_interest_map: Dict[str, Any],
        interest_gap_report: Dict[str, Any],
        mode: str = "rule_based_fallback",
    ) -> Dict[str, Any]:
        search_top = self._top_category(search_interest_map)
        watch_top = self._top_category(standard_video_interest_map)
        shorts_top = self._top_category(shorts_interest_map)
        mismatch = round(float(interest_gap_report.get("interest_mismatch_score") or 0.0), 1)
        search_total = int(search_interest_map.get("total_search_count") or 0)
        watch_total = int(standard_video_interest_map.get("total_video_count") or 0)
        shorts_total = int(shorts_interest_map.get("total_shorts_count") or 0)

        candidates = (
            interest_gap_report.get("recommendation_flow_candidate_categories")
            or interest_gap_report.get("algorithm_drift_categories")
            or []
        )
        if candidates:
            drift_hint = f"추천 흐름 영향 후보로는 {candidates[0].get('category', '특정 주제')}가 먼저 보입니다."
        else:
            drift_hint = "검색 의도와 일반 영상 소비의 큰 이탈은 아직 뚜렷하지 않습니다."

        warnings: List[str] = []
        if search_total < 3:
            warnings.append("검색 표본이 적어 의도 해석은 참고용입니다.")
        if watch_total < 3:
            warnings.append("일반 영상 표본이 적어 노출 해석은 참고용입니다.")
        if shorts_total == 0:
            warnings.append("숏츠 기록이 부족해 숏츠 관심사 해석은 제외했습니다.")

        return self._normalize_interest_report({
            "mode": mode,
            "model": "rule_based",
            "summary": f"현재 검색 의도와 시청 소비의 관심사 격차는 {mismatch}점으로 계산되었습니다.",
            "search_intent_read": f"광고를 제외한 실제 검색은 {search_total}건이며, 상위 관심사는 {search_top}입니다.",
            "watch_exposure_read": f"일반 영상 소비는 {watch_total}건이며, 상위 관심사는 {watch_top}입니다. {drift_hint}",
            "shorts_read": (
                f"숏츠는 {shorts_total}건이며, 상위 관심사는 {shorts_top}입니다."
                if shorts_total > 0
                else "이번 데이터에서는 숏츠 관심사 표본이 부족합니다."
            ),
            "next_action_hint": "상위 검색 관심사와 비검색 시청 관심사가 다른 경우, 다음 시청 전 검색어를 먼저 정해 추천 흐름을 잠깐 끊어보세요.",
            "confidence": "medium" if search_total >= 3 and watch_total >= 3 else "low",
            "warnings": warnings,
        })

    def _normalize_interest_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        warnings = report.get("warnings")
        if not isinstance(warnings, list):
            warnings = []
        return {
            "mode": report.get("mode") or "rule_based_fallback",
            "model": report.get("model") or ("mock" if self.is_mock else self._model_name()),
            "summary": str(report.get("summary") or "관심사 해석 데이터가 부족합니다."),
            "search_intent_read": str(report.get("search_intent_read") or "검색 의도 데이터가 부족합니다."),
            "watch_exposure_read": str(report.get("watch_exposure_read") or "일반 영상 노출 데이터가 부족합니다."),
            "shorts_read": str(report.get("shorts_read") or "숏츠 데이터가 부족합니다."),
            "next_action_hint": str(report.get("next_action_hint") or "다음 분석을 위해 시청 기록을 더 확보하세요."),
            "confidence": str(report.get("confidence") or "low"),
            "warnings": [str(item) for item in warnings[:5]],
        }
            
    def _generate_mock_plan(
        self, 
        risk_score: float, 
        axis_scores: Dict[str, float], 
        mbti_type: str,
        dominant_topics: List[str],
        shorts_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generates dynamic, high-quality, realistic detox plans based on scores."""
        shorts_analysis = shorts_analysis or {}
        sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1])
        lowest_axis, lowest_score = sorted_axes[0]
        
        shorts_count = int(shorts_analysis.get("shorts_count") or 0)
        shorts_stimulation_risk = int(shorts_analysis.get("shorts_stimulation_risk") or 0)
        
        from app.core.mission_loader import generate_mock_plan_data
        return generate_mock_plan_data(
            lowest_axis=lowest_axis,
            dominant_topics=dominant_topics,
            shorts_count=shorts_count,
            shorts_stimulation_risk=shorts_stimulation_risk
        )

gemini_client = GeminiClient()
