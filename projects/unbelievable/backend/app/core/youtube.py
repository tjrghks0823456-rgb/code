import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeClient:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.is_mock = self.api_key == "mock-youtube-api-key"
        
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        Fetches title, description, tags, categoryId, and topicDetails for a video_id.
        Gracefully falls back to high-quality mock data if API key is not configured.
        """
        if self.is_mock or not video_id:
            return self._get_mock_video(video_id)
            
        try:
            import httpx
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,topicDetails",
                "id": video_id,
                "key": self.api_key
            }
            response = httpx.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    snippet = items[0].get("snippet", {})
                    topic_details = items[0].get("topicDetails", {})
                    
                    return {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", ""),
                        "channelId": snippet.get("channelId", ""),
                        "topicDetails": topic_details.get("topicIds", []) + topic_details.get("relevantTopicIds", []),
                        "api_success": True
                    }
            logger.warning(f"YouTube videos.list returned code {response.status_code}")
            return self._get_mock_video(video_id)
        except Exception as e:
            logger.error(f"Failed to fetch YouTube video metadata: {e}")
            return self._get_mock_video(video_id)
            
    def get_channel_metadata(self, channel_id: str) -> Dict[str, Any]:
        """
        Fetches channel details using channels.list.
        Falls back to mock data if API key is not configured.
        """
        if self.is_mock or not channel_id:
            return self._get_mock_channel(channel_id)
            
        try:
            import httpx
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "snippet,topicDetails",
                "id": channel_id,
                "key": self.api_key
            }
            response = httpx.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    snippet = items[0].get("snippet", {})
                    topic_details = items[0].get("topicDetails", {})
                    return {
                        "channel_id": channel_id,
                        "title": snippet.get("title", ""),
                        "customUrl": snippet.get("customUrl", ""),
                        "topicDetails": topic_details.get("topicIds", []),
                        "api_success": True
                    }
            return self._get_mock_channel(channel_id)
        except Exception as e:
            logger.error(f"Failed to fetch YouTube channel metadata: {e}")
            return self._get_mock_channel(channel_id)

    def _get_mock_video(self, video_id: str) -> Dict[str, Any]:
        """Generates realistic mock video details."""
        return {
            "video_id": video_id or "dQw4w9WgXcQ",
            "title": f"가상 반도체 제조 공정과 AI 최적화 - {video_id}",
            "description": "이 비디오는 반도체 제조 공정 중 발생하는 다차원 센서 로그 데이터를 딥러닝 AI 모델로 실시간 학습하고 장비 이상을 사전에 예방하는 스마트팩토리 자동화 솔루션 소개 영상입니다.",
            "tags": ["반도체", "장비제어", "AI", "스마트팩토리"],
            "categoryId": "28", # Science & Technology
            "channelId": "UC_mock_semiconductor_channel",
            "topicDetails": ["/m/07g4xs", "/m/06lxs"],
            "api_success": False
        }
        
    def _get_mock_channel(self, channel_id: str) -> Dict[str, Any]:
        """Generates realistic mock channel details."""
        return {
            "channel_id": channel_id or "UC_mock_semiconductor_channel",
            "title": "반도체 장비 통신 아카데미",
            "customUrl": "@semitool_hmi",
            "topicDetails": ["/m/06lxs"],
            "api_success": False
        }

youtube_client = YouTubeClient()
