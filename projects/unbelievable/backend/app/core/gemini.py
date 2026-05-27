import logging
import json
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.is_mock = self.api_key == "mock-gemini-api-key"
        
    def generate_detox_plan(
        self, 
        risk_score: float, 
        axis_scores: Dict[str, float], 
        mbti_type: str,
        dominant_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Generates structured Reverse Queries and Detox Missions using Gemini 2.5 Flash.
        If using mock credentials, generates high-quality realistic mock responses.
        """
        if self.is_mock:
            return self._generate_mock_plan(risk_score, axis_scores, mbti_type, dominant_topics)
            
        try:
            # Placeholder for actual Gemini API call utilizing google-generativeai SDK
            # with response_mime_type="application/json" and response_schema.
            # (Included in prototype for easy replacement/connection)
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            prompt = f"""
            Analyze this media consumption profile:
            - Bias Risk Score: {risk_score} (0 is healthy, 100 is highly biased/polarized)
            - 6-Axis Scores (TDS, SBS, EBS, VOS, SMS, UAS): {json.dumps(axis_scores)}
            - Personality Type: {mbti_type}
            - Dominant Topics Consumed: {json.dumps(dominant_topics)}
            
            Generate a JSON containing:
            1. overall_summary: A 2-3 sentence warning/explanation.
            2. reverse_queries: 3-5 alternative search query objects (query_text, expected_topic, why_this_helps).
            3. missions: A 3-day or 7-day plan containing action items (title, action_steps, success_condition, blocked_surface).
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Failed to call Gemini API: {e}")
            return self._generate_mock_plan(risk_score, axis_scores, mbti_type, dominant_topics)
            
    def _generate_mock_plan(
        self, 
        risk_score: float, 
        axis_scores: Dict[str, float], 
        mbti_type: str,
        dominant_topics: List[str]
    ) -> Dict[str, Any]:
        """Generates dynamic, high-quality, realistic detox plans based on scores."""
        # Find the lowest score axis
        sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1])
        lowest_axis, lowest_score = sorted_axes[0]
        
        # Prepare content based on the lowest axis
        reverse_queries = []
        missions = []
        overall_summary = ""
        
        if lowest_axis == "TDS": # 주제다양성
            overall_summary = f"소비 중인 콘텐츠 주제가 '{', '.join(dominant_topics[:2])}'에 과도하게 편중되어 있어 미디어 시야가 좁아진 상태입니다. 다양한 관심사를 수동적으로 알고리즘에 의존해 시청하기보다, 새로운 분야의 정보를 의도적으로 검색하여 뇌의 균형 잡힌 인지 자극을 유도해야 합니다."
            reverse_queries = [
                {"query_text": "인문학 기초 입문 강연", "expected_topic": "Humanities", "why_this_helps": "IT/엔터에 편향된 관심사에서 인문학적 교양으로 영역을 대폭 확장합니다."},
                {"query_text": "미술사조 쉽게 이해하기", "expected_topic": "Arts", "why_this_helps": "새로운 시각적 자극과 예술적 뇌 영역을 활성화시킵니다."}
            ]
            missions = [
                {"id": "m1", "title": "낯선 카테고리 영상 시청", "action_steps": "평소 한 번도 보지 않았던 '역사' 혹은 '다큐멘터리' 채널 영상을 의도적으로 1개 시청합니다.", "success_condition": "영상 10분 이상 시청 완료", "blocked_surface": "shorts_feed"},
                {"id": "m2", "title": "서점 또는 온라인 도서 주제 검색", "action_steps": "베스트셀러 인문/철학 섹션을 살펴보고 관심이 생기는 키워드를 1개 검색해 봅니다.", "success_condition": "관심 도서 정보 탐색 완료", "blocked_surface": "none"}
            ]
        elif lowest_axis == "SBS": # 출처균형
            overall_summary = "소수의 지배적인 유튜버/채널 영상만 집중적으로 청취하여 에코챔버(Echo Chamber) 현상에 갇힐 위험성이 높습니다. 정보원(Source)의 고착화는 인지적 동조 현상을 부추기므로, 다채로운 뉴스사나 공영 채널 등 출처의 균형을 복원하는 시도가 급선무입니다."
            reverse_queries = [
                {"query_text": "KBS 다큐 공감", "expected_topic": "News", "why_this_helps": "개인 크리에이터 위주의 출처에서 신뢰도 있는 공영 채널로 정보원을 넓힙니다."},
                {"query_text": "BBC News 코리아", "expected_topic": "News", "why_this_helps": "외신 채널을 통해 국내 관점에서 벗어난 해외 시각을 경험합니다."}
            ]
            missions = [
                {"id": "m1", "title": "공영/외신 뉴스 1회 시청", "action_steps": "개인 해설 방송 대신 공인된 뉴스 미디어가 직접 보도하는 뉴스를 1회 정독합니다.", "success_condition": "보도 영상 5분 이상 시청", "blocked_surface": "personal_stream"},
                {"id": "m2", "title": "정보 출처 리스트 정리", "action_steps": "오늘 본 채널들을 분석하고 평소 시청하지 않던 채널명을 3개 적어 구독 목록에 추가해 봅니다.", "success_condition": "3개 채널 신규 추가 완료", "blocked_surface": "none"}
            ]
        else: # Default or safety/emotion/agency issues
            overall_summary = "알고리즘이 주는 즉각적인 숏폼 도파민 피드와 검색 없이 흘러가는 피동적 소비가 축적되어 미디어 주도성이 많이 무너진 상태입니다. 화면 흑백 모드 가동 및 주체적인 목표 검색을 통해 자가 제어력을 회복하고 도파민 소비 회로를 깨끗이 씻어내야 합니다."
            reverse_queries = [
                {"query_text": "디지털 디톡스 실천 방안", "expected_topic": "Lifestyle", "why_this_helps": "스스로 미디어 중독 상태를 인지하고 실천적인 복원 팁을 검색합니다."},
                {"query_text": "마음 챙김 명상 음악", "expected_topic": "Health", "why_this_helps": "빠른 자극적 화면 대신 소리 중심의 뇌 휴식을 경험합니다."}
            ]
            missions = [
                {"id": "m1", "title": "스마트폰 화면 흑백 모드 설정", "action_steps": "스마트폰의 접근성 설정에서 화면 색상을 '흑백'으로 전환하여 시각적 도파민 유도를 원천 차단합니다.", "success_condition": "흑백 모드로 하루 3시간 이상 사용", "blocked_surface": "youtube_shorts"},
                {"id": "m2", "title": "알고리즘 피드 숨기기 실천", "action_steps": "유튜브 홈 화면에 진입하자마자 피드를 보지 않고, 오직 상단 '검색창'에 사전에 정해둔 검색어만 검색해 영상을 찾습니다.", "success_condition": "추천 피드 클릭 0회 달성", "blocked_surface": "home_feed"}
            ]
            
        return {
            "overall_summary": overall_summary,
            "reverse_queries": reverse_queries,
            "missions": missions
        }

gemini_client = GeminiClient()
