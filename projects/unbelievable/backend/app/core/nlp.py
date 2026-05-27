import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class NLPClient:
    def __init__(self):
        self.api_key = settings.GOOGLE_LANGUAGE_API_KEY
        self.is_mock = self.api_key == "mock-nl-api-key"
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the text using Google Cloud Natural Language API.
        If using mock credentials, returns high-quality realistic mock results.
        """
        if self.is_mock:
            return self._get_mock_analysis(text)
            
        try:
            # Placeholder for actual Google Cloud Natural Language API request
            # with google.cloud.language SDK or HTTP POST requests
            # (Included in prototype for easy replacement/connection)
            import httpx
            url = f"https://language.googleapis.com/v1/documents:annotateText?key={self.api_key}"
            payload = {
                "document": {
                    "type": "PLAIN_TEXT",
                    "content": text
                },
                "features": {
                    "extractDocumentSentiment": True,
                    "extractEntities": True,
                    "classifyText": len(text.split()) >= 20 # Only classify if 20+ words/tokens
                }
            }
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"NL API error {response.status_code}: {response.text}")
                return self._get_mock_analysis(text)
        except Exception as e:
            logger.error(f"Failed to call Google NL API: {e}")
            return self._get_mock_analysis(text)
            
    def _get_mock_analysis(self, text: str) -> Dict[str, Any]:
        """Generates rich, realistic mock NLP responses based on text keywords."""
        text_lower = text.lower()
        
        # Determine sentiment score
        sentiment = 0.15 # default neutral positive
        if any(w in text_lower for w in ["화남", "짜증", "슬픔", "우울", "분노", "비극", "충격", "망했다"]):
            sentiment = -0.65
        elif any(w in text_lower for w in ["기쁨", "행복", "즐거운", "추천", "꿀팁", "대박", "혁신", "성공"]):
            sentiment = 0.8
            
        # Determine categories
        categories = [{"name": "/Computers & Electronics/Software", "confidence": 0.95}]
        if any(w in text_lower for w in ["주식", "코인", "투자", "금융", "재테크"]):
            categories = [{"name": "/Finance/Investing", "confidence": 0.9}]
        elif any(w in text_lower for w in ["쇼츠", "릴스", "틱톡", "밈"]):
            categories = [{"name": "/Arts & Entertainment/Humor", "confidence": 0.88}]
        elif any(w in text_lower for w in ["연애", "고민", "이별", "결혼"]):
            categories = [{"name": "/People & Society/Family & Relationships", "confidence": 0.85}]
        elif any(w in text_lower for w in ["게임", "롤", "오버워치", "배틀그라운드"]):
            categories = [{"name": "/Games/Computer & Video Games", "confidence": 0.92}]
            
        # Determine entities
        entities = []
        if "주식" in text_lower:
            entities.append({"name": "주식", "type": "OTHER", "salience": 0.75})
        if "코인" in text_lower:
            entities.append({"name": "코인", "type": "OTHER", "salience": 0.8})
            
        return {
            "documentSentiment": {
                "score": sentiment,
                "magnitude": abs(sentiment) * 1.5
            },
            "entities": entities,
            "categories_json": categories, # DB matches categories_json directly
            "language_code": "ko"
        }

nlp_client = NLPClient()
