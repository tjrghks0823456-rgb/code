import json
import logging
import os
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Fallback configurations matching original parameters
FALLBACK_SCORING_RULES = {
    "axis_codes": ["TDS", "SBS", "EBS", "VOS", "SMS", "UAS"],
    "score_range": {"min": 0.0, "max": 100.0},
    "neutral_compat_score": 50.0,
    "min_data_requirements": {
        "event_count": 10,
        "watch_count": 10,
        "search_count": 3,
        "topic_count": 3,
        "channel_count": 3,
        "sentiment_count": 2,
        "safety_count": 2
    },
    "confidence_weights": {
        "real_data": 1.0,
        "estimated_duration": 0.5,
        "fallback": 0.2,
        "mock": 0.0,
        "missing": 0.0
    },
    "uas_weights": {
        "search_ratio": 0.35,
        "direct_selection_ratio": 0.25,
        "curation_ratio": 0.25,
        "participation_ratio": 0.15
    },
    "sms_weights": {
        "toxic_ratio": 0.35,
        "harmful_keyword_ratio": 0.25,
        "shorts_ratio": 0.20,
        "repeated_short_exposure_ratio": 0.20
    },
    "vos_weights": {
        "topic_concentration": 0.45,
        "channel_concentration": 0.35,
        "search_repetition": 0.20
    },
    "sentiment_thresholds": {
        "positive": 0.25,
        "negative": -0.25
    },
    "duration_confidence_values": {
        "timeline": 1.0,
        "timeline_capped_api": 1.0,
        "timeline_api": 1.0,
        "api": 1.0,
        "medium": 0.5,
        "estimated": 0.5,
        "low": 0.25,
        "unknown": 0.0
    },
    "classification_thresholds": {
        "diversity": 50.0,
        "stability": 60.0,
        "agency": 40.0,
        "openness": 50.0
    },
    "harmful_keywords": [
        "adult", "violence", "violent", "drugs", "weapons", "gore", "hate", "sexual", "suicide", "self-harm"
    ],
    "toxic_category_keywords": [
        "adult", "violence", "drugs", "weapons", "gore", "hate"
    ],
    "max_topic_categories": 15,
    "concentration_beta": 0.5,
    "educational_categories": [
        "코딩/기술", "금융/투자", "교육/강의", "건강/운동",
        "Science", "Computers & Electronics", "Finance",
        "Business & Industrial", "Books & Literature",
        "Education", "Reference", "Jobs & Education"
    ]
}

class ScoringRuleLoader:
    def __init__(self):
        self.rules_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "rules", "scoring_rules.v1.json"
        )
        self.rules: Dict[str, Any] = {}
        self.load_rules()

    def load_rules(self):
        if not os.path.exists(self.rules_file):
            logger.warning(f"Scoring rules JSON file not found at {self.rules_file}. Using minimal fallback.")
            self.rules = FALLBACK_SCORING_RULES
            return

        try:
            with open(self.rules_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Simple schema validation
            if not isinstance(data, dict):
                raise ValueError("Root element of scoring rules must be a JSON dictionary.")
            
            required_keys = ["axis_codes", "score_range", "min_data_requirements", "uas_weights", "sms_weights", "vos_weights"]
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise ValueError(f"Missing required configuration blocks: {missing}")
            
            self.rules = data
            logger.info("Successfully loaded scoring rules config from JSON.")

        except Exception as e:
            logger.warning(f"Error loading scoring rules config: {e}. Using fallback defaults.")
            self.rules = FALLBACK_SCORING_RULES

    def get(self, key: str, default: Any = None) -> Any:
        return self.rules.get(key, FALLBACK_SCORING_RULES.get(key, default))

scoring_rule_loader = ScoringRuleLoader()
