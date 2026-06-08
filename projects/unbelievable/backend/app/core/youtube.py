import logging
import re
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

ISO8601_DURATION_RE = re.compile(
    r"^P"
    r"(?:(?P<days>\d+)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+)H)?"
    r"(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)S)?"
    r")?$"
)


def parse_iso8601_duration(duration: Optional[str]) -> Optional[int]:
    if not duration:
        return None

    match = ISO8601_DURATION_RE.match(duration)
    if not match:
        return None

    parts = {key: int(value or 0) for key, value in match.groupdict().items()}
    total_seconds = (
        parts["days"] * 24 * 60 * 60
        + parts["hours"] * 60 * 60
        + parts["minutes"] * 60
        + parts["seconds"]
    )
    return total_seconds if total_seconds > 0 else None


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
            result = self._get_mock_video(video_id)
            result["fallback_used"] = False
            return result
            
        try:
            import httpx
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,contentDetails,topicDetails",
                "id": video_id,
                "key": self.api_key
            }
            response = httpx.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    snippet = items[0].get("snippet", {})
                    content_details = items[0].get("contentDetails", {})
                    topic_details = items[0].get("topicDetails", {})
                    duration_sec = parse_iso8601_duration(content_details.get("duration"))
                    
                    return {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", ""),
                        "channelId": snippet.get("channelId", ""),
                        "topicDetails": topic_details.get("topicIds", []) + topic_details.get("relevantTopicIds", []),
                        "duration_iso8601": content_details.get("duration", ""),
                        "duration_sec": duration_sec,
                        "api_success": True,
                        "mock_used": False,
                        "fallback_used": False
                    }
            logger.warning(f"YouTube videos.list returned code {response.status_code}")
            result = self._get_mock_video(video_id)
            result["fallback_used"] = True
            return result
        except Exception as e:
            logger.error(f"Failed to fetch YouTube video metadata: {e}")
            result = self._get_mock_video(video_id)
            result["fallback_used"] = True
            return result

    def get_videos_metadata_batch(self, video_ids: list) -> Dict[str, Dict[str, Any]]:
        """
        Fetches metadata for up to 50 video IDs in a single batch request to YouTube API.
        Returns a dictionary mapping video_id to its metadata dictionary.
        """
        if not video_ids:
            return {}
            
        # Limit to 50 video IDs (YouTube API limit per request)
        ids_to_query = video_ids[:50]
        
        if self.is_mock:
            return {vid: self._get_mock_video(vid) for vid in ids_to_query}
            
        try:
            import httpx
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,contentDetails,topicDetails",
                "id": ",".join(ids_to_query),
                "key": self.api_key
            }
            response = httpx.get(url, params=params, timeout=5.0)
            result_map = {}
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                logger.info(f"YouTube videos.list batch query returned {len(items)} items")
                for item in items:
                    vid = item.get("id")
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    topic_details = item.get("topicDetails", {})
                    duration_sec = parse_iso8601_duration(content_details.get("duration"))
                    
                    result_map[vid] = {
                        "video_id": vid,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "tags": snippet.get("tags", []),
                        "categoryId": snippet.get("categoryId", ""),
                        "channelId": snippet.get("channelId", ""),
                        "topicDetails": topic_details.get("topicIds", []) + topic_details.get("relevantTopicIds", []),
                        "duration_iso8601": content_details.get("duration", ""),
                        "duration_sec": duration_sec,
                        "api_success": True,
                        "mock_used": False,
                        "fallback_used": False
                    }
                
                # For any requested video IDs that were not returned by the API (e.g. deleted or private)
                for vid in ids_to_query:
                    if vid not in result_map:
                        mock_res = self._get_mock_video(vid)
                        mock_res["fallback_used"] = True
                        result_map[vid] = mock_res
                return result_map
                
            logger.warning(f"YouTube videos.list batch query returned code {response.status_code}")
            return {vid: {**self._get_mock_video(vid), "fallback_used": True} for vid in ids_to_query}
        except Exception as e:
            logger.error(f"Failed to fetch YouTube videos batch metadata: {e}")
            return {vid: {**self._get_mock_video(vid), "fallback_used": True} for vid in ids_to_query}
            
    def get_channel_metadata(self, channel_id: str) -> Dict[str, Any]:
        """
        Fetches channel details using channels.list.
        Falls back to mock data if API key is not configured.
        """
        if self.is_mock or not channel_id:
            result = self._get_mock_channel(channel_id)
            result["fallback_used"] = False
            return result
            
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
                        "api_success": True,
                        "mock_used": False,
                        "fallback_used": False
                    }
            result = self._get_mock_channel(channel_id)
            result["fallback_used"] = True
            return result
        except Exception as e:
            logger.error(f"Failed to fetch YouTube channel metadata: {e}")
            result = self._get_mock_channel(channel_id)
            result["fallback_used"] = True
            return result

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
            "duration_iso8601": "PT8M30S",
            "duration_sec": 510,
            "api_success": False,
            "mock_used": True,
            "fallback_used": False
        }
        
    def _get_mock_channel(self, channel_id: str) -> Dict[str, Any]:
        """Generates realistic mock channel details."""
        return {
            "channel_id": channel_id or "UC_mock_semiconductor_channel",
            "title": "반도체 장비 통신 아카데미",
            "customUrl": "@semitool_hmi",
            "topicDetails": ["/m/06lxs"],
            "api_success": False,
            "mock_used": True,
            "fallback_used": False
        }

youtube_client = YouTubeClient()
