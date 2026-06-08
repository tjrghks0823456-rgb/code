import json
import logging
import os
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

# Minimal python code configurations for fallback protection to avoid server startup crashes
FALLBACK_CATEGORY_DICT = {
    "📈 경제/금융": ["주식", "투자", "경제", "재테크"],
    "💻 IT/테크": ["코딩", "개발", "AI", "인공지능", "프로그래밍"],
    "🎮 게임": ["게임", "스팀", "롤"],
    "🔬 과학/지식": ["과학", "우주", "역사", "다큐"],
    "🍿 엔터/예능": ["예능", "영화", "음악", "유머"]
}
FALLBACK_STOP_WORDS = ["정말", "진짜", "오늘", "저희", "여러분", "그냥"]
FALLBACK_UNSTABLE_WORDS = ["불안", "분노", "슬픔", "우울"]
FALLBACK_STIMULUS_WORDS = ["경악", "폭로", "사건", "사고", "충격"]
FALLBACK_YOUTUBE_CATEGORY_MAP = {
    "1": "🎬 애니/웹툰",
    "10": "🎵 음악",
    "20": "🎮 게임",
    "24": "🍿 엔터/예능",
    "25": "⚖️ 뉴스/정치/사회"
}

class CategoryLoader:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dictionaries")
        self.category_dict: Dict[str, List[str]] = {}
        self.stop_words: List[str] = []
        self.unstable_words: List[str] = []
        self.stimulus_words: List[str] = []
        self.youtube_category_map: Dict[str, str] = {}
        
        self.load_all()

    def load_all(self):
        self.category_dict = self._load_category_dict()
        self.stop_words = self._load_list("stop_words.v1.json", FALLBACK_STOP_WORDS)
        self.unstable_words = self._load_list("unstable_words.v1.json", FALLBACK_UNSTABLE_WORDS)
        self.stimulus_words = self._load_list("stimulus_words.v1.json", FALLBACK_STIMULUS_WORDS)
        self.youtube_category_map = self._load_dict("youtube_category_map.v1.json", FALLBACK_YOUTUBE_CATEGORY_MAP)

    def _load_category_dict(self) -> Dict[str, List[str]]:
        path = os.path.join(self.data_dir, "category_dictionary.v1.json")
        if not os.path.exists(path):
            logger.warning(f"Category dictionary JSON file not found at {path}. Using minimal fallback.")
            return FALLBACK_CATEGORY_DICT

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Schema validation
            if not isinstance(data, list):
                raise ValueError("Root category dictionary JSON must be a list of objects.")
            
            loaded_dict = {}
            for item in data:
                if not isinstance(item, dict):
                    logger.warning("Category dictionary item is not a dictionary. Skipping.")
                    continue
                
                # Check required fields
                required = ["category_code", "display_name", "keywords", "weight", "enabled"]
                missing = [r for r in required if r not in item]
                if missing:
                    logger.warning(f"Category item missing fields {missing}. Skipping.")
                    continue
                
                if item.get("enabled", True):
                    code = item["category_code"]
                    kws = item["keywords"]
                    if isinstance(kws, list):
                        loaded_dict[code] = [str(k) for k in kws]
            
            if not loaded_dict:
                raise ValueError("No valid category entries loaded from JSON.")
            
            return loaded_dict

        except Exception as e:
            logger.warning(f"Error loading category dictionary JSON from {path}: {e}. Using minimal fallback.")
            return FALLBACK_CATEGORY_DICT

    def _load_list(self, filename: str, fallback: List[str]) -> List[str]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"{filename} not found at {path}. Using minimal fallback.")
            return fallback

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON root must be a list.")
            return [str(item) for item in data]
        except Exception as e:
            logger.warning(f"Error loading list from {filename}: {e}. Using minimal fallback.")
            return fallback

    def _load_dict(self, filename: str, fallback: Dict[str, str]) -> Dict[str, str]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"{filename} not found at {path}. Using minimal fallback.")
            return fallback

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("JSON root must be a dictionary.")
            return {str(k): str(v) for k, v in data.items()}
        except Exception as e:
            logger.warning(f"Error loading dict from {filename}: {e}. Using minimal fallback.")
            return fallback

category_loader = CategoryLoader()
