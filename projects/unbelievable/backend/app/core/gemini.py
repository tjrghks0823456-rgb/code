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
        # Find the lowest score axis
        sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1])
        lowest_axis, lowest_score = sorted_axes[0]
        
        # Prepare content based on the lowest axis
        reverse_queries = []
        missions = []
        overall_summary = ""
        
        if lowest_axis == "TDS": # 주제다양성
            overall_summary = f"소비 중인 콘텐츠 주제가 '{', '.join(dominant_topics[:2])}'에 다소 집중되어 있어 관심 영역의 편향 가능성이 있습니다. 수동 소비 흐름에서 벗어나 새로운 카테고리의 유익 정보를 가볍게 탐색하며 뇌의 균형 잡힌 자극을 유도하는 루틴을 제안합니다."
            reverse_queries = [
                {"query_text": "역사 및 세계사 핵심 정리 다큐", "expected_topic": "History", "why_this_helps": "IT 및 정보 위주의 관심사에서 인문학 교양으로 영역을 다양하게 넓혀 줍니다."},
                {"query_text": "현대 미술 쉽게 감상하는 법", "expected_topic": "Arts", "why_this_helps": "낯선 주제의 영상을 통해 시각적 자극을 다양화하고 폭넓은 미디어 관찰 능력을 돕습니다."}
            ]
            missions = [
                {
                    "id": "m1",
                    "title": "낯선 카테고리 하나 구경하기",
                    "description": "평소 전혀 보지 않던 '교양/다큐' 섹션 영상을 하나 클릭하고 무엇에 관한 것인지 확인해 보세요.",
                    "success_condition": "선택만 하면 완료",
                    "effort_level": "low",
                    "input_type": "choice",
                    "choices": ["역사/문학", "예술/디자인", "우주/자연과학", "경제/비즈니스"]
                },
                {
                    "id": "m2",
                    "title": "관심 도서 가벼운 한 줄 메모",
                    "description": "오늘 온라인 서점에서 가장 관심이 생기는 도서 제목 하나를 복사하거나 메모해 보세요.",
                    "success_condition": "메모 작성 시 완료",
                    "effort_level": "low",
                    "input_type": "text"
                }
            ]
        elif lowest_axis == "SBS": # 출처균형
            overall_summary = "소수 채널이나 유사 정보원의 영상만 지속 수용하여 편향적 확신이 생길 가능성이 관찰됩니다. 균형 잡힌 시각 형성을 돕기 위해 공영 언론사나 국제 외신 등의 신뢰도 높은 다른 정보원들을 가볍게 비교 분석해보는 루틴을 권장합니다."
            reverse_queries = [
                {"query_text": "공영방송 대기획 다큐멘터리", "expected_topic": "News", "why_this_helps": "1인 미디어 편중에서 탈피해 고도의 팩트체크를 거친 공인 정보원으로 출처 균형을 도모합니다."},
                {"query_text": "국제 시사 보도 및 시각 비교", "expected_topic": "Global News", "why_this_helps": "국내 크리에이터의 관점을 넘어 다각도의 균형 잡힌 세계적 안목을 돕습니다."}
            ]
            missions = [
                {
                    "id": "m1",
                    "title": "서로 다른 언론사 뉴스 헤드라인 체크",
                    "description": "두 개의 서로 다른 언론사의 동일 이슈 관련 뉴스를 읽어본 뒤, 더 객관적이라고 느껴지는 논조를 골라보세요.",
                    "success_condition": "체크 완료 시 인정",
                    "effort_level": "low",
                    "input_type": "choice",
                    "choices": ["언론사 A가 객관적", "언론사 B가 객관적", "두 관점이 균형 잡힘"]
                },
                {
                    "id": "m2",
                    "title": "신뢰할 만한 대안 정보 채널 하나 추천받기",
                    "description": "평소 보던 채널 외에 유용하다고 생각되는 학술적 채널 이름 하나만 적어보세요.",
                    "success_condition": "입력 완료 시 자동 인정",
                    "effort_level": "low",
                    "input_type": "text"
                }
            ]
        else: # Default (UAS/SMS/EBS/VOS 등 주도성 및 유해안전 관련)
            overall_summary = "알고리즘 추천 영상 피드의 연속 노출 및 자동 시청의 영향으로 미디어 소비 주도성이 감소한 경향성이 발견되었습니다. 의도적인 단어 검색과 클릭 전 짧은 생각 루틴을 통해 수동적 흐름을 완화하고 미디어 조절 능력을 복원하는 데 도움을 드립니다."
            reverse_queries = [
                {"query_text": "미디어 소비 조절과 디지털 웰빙", "expected_topic": "Lifestyle", "why_this_helps": "수동적 추천 노출에서 주체적인 사용 패턴 개선 방향을 직접 인지하도록 돕습니다."},
                {"query_text": "자연의 소리 명상 유도", "expected_topic": "Health", "why_this_helps": "빠르고 자극적인 전개가 아닌 소리와 흐름에 집중하여 뇌의 휴식과 여유를 유도합니다."}
            ]
            missions = [
                {
                    "id": "m1",
                    "title": "영상 재생 전 '클릭 의도' 멈춤 및 선택",
                    "description": "영상을 클릭하여 시청하기 전, 내가 이 영상을 왜 누르는지 이유를 가볍게 골라보세요.",
                    "success_condition": "선택 즉시 완료",
                    "effort_level": "low",
                    "input_type": "choice",
                    "choices": ["정보 습득", "오락 및 기분전환", "무의식적 습관", "심심함"]
                },
                {
                    "id": "m2",
                    "title": "오늘 본 최선/최악의 제목 한 줄 남기기",
                    "description": "오늘 본 콘텐츠 중 가장 가치 있었던 영상 제목이나 가장 호기심만 유도했던 낚시성 제목 하나를 적어보세요.",
                    "success_condition": "한 줄 작성 시 완료",
                    "effort_level": "low",
                    "input_type": "text"
                }
            ]
            
        shorts_count = int(shorts_analysis.get("shorts_count") or 0)
        if shorts_count > 0:
            shorts_keywords = shorts_analysis.get("top_shorts_keywords") or []
            keyword_hint = (
                shorts_keywords[0].get("keyword")
                if shorts_keywords and isinstance(shorts_keywords[0], dict)
                else "반복 주제"
            )
            overall_summary += (
                f" 숏츠는 관심사 편향 점수에 직접 섞지 않고, 짧은 영상 반복 소비 루프 관점에서 별도로 참고했습니다."
                f" 현재 숏츠 자극 소비 위험은 {shorts_analysis.get('shorts_stimulation_risk', 0)}점입니다."
            )
            missions = [
                {
                    "id": "shorts_m1",
                    "title": "숏츠 5개 뒤 키워드 하나 적기",
                    "description": f"다음 숏츠 묶음을 본 뒤 방금 반복된 단어를 하나만 적어보세요. 감지된 반복 힌트는 '{keyword_hint}'입니다.",
                    "success_condition": "반복 키워드 1개 입력",
                    "effort_level": "low",
                    "input_type": "text"
                },
                {
                    "id": "shorts_m2",
                    "title": "다음 숏츠 제목 먼저 읽기",
                    "description": "다음 숏츠를 바로 넘기기 전에 제목을 한 번 읽고, 정말 볼지 3초만 선택해보세요.",
                    "success_condition": "선택 완료",
                    "effort_level": "low",
                    "input_type": "choice",
                    "choices": ["보고 넘기기", "저장만 하기", "일반 영상으로 바꾸기"]
                },
            ] + missions

        return {
            "overall_summary": overall_summary,
            "reverse_queries": reverse_queries,
            "missions": missions
        }

gemini_client = GeminiClient()
