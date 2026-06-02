"""Configuration for the first scoring-model hardcoding cleanup.

Values here are intentionally simple and explainable. They are not final
calibration constants; they make the scoring formula explicit and movable.
"""

AXIS_CODES = ["TDS", "SBS", "EBS", "VOS", "SMS", "UAS"]

SCORE_RANGE = {
    "min": 0.0,
    "max": 100.0,
}

# Used only for legacy API compatibility when a score cannot be calculated.
# The detailed v2 result still exposes low confidence and warnings.
NEUTRAL_COMPAT_SCORE = 50.0

MIN_DATA_REQUIREMENTS = {
    "event_count": 10,
    "watch_count": 10,
    "search_count": 3,
    "topic_count": 3,
    "channel_count": 3,
    "sentiment_count": 2,
    "safety_count": 2,
}

CONFIDENCE_WEIGHTS = {
    "real_data": 1.0,
    "estimated_duration": 0.5,
    "fallback": 0.2,
    "mock": 0.0,
    "missing": 0.0,
}

# UAS measures active user agency. The available terms are re-normalized when
# a field cannot be measured from the current Takeout schema.
UAS_WEIGHTS = {
    "search_ratio": 0.35,
    "direct_selection_ratio": 0.25,
    "curation_ratio": 0.25,
    "participation_ratio": 0.15,
}

# SMS is a safety score, so these weights define a penalty mix rather than a
# positive-score mix. All available terms are re-normalized before use.
SMS_WEIGHTS = {
    "toxic_ratio": 0.35,
    "harmful_keyword_ratio": 0.25,
    "shorts_ratio": 0.20,
    "repeated_short_exposure_ratio": 0.20,
}

VOS_WEIGHTS = {
    "topic_concentration": 0.45,
    "channel_concentration": 0.35,
    "search_repetition": 0.20,
}

SENTIMENT_THRESHOLDS = {
    "positive": 0.25,
    "negative": -0.25,
}

DURATION_CONFIDENCE_VALUES = {
    "timeline": 1.0,
    "api": 1.0,
    "medium": 0.5,
    "estimated": 0.5,
    "low": 0.25,
    "unknown": 0.0,
}

CLASSIFICATION_THRESHOLDS = {
    "diversity": 50.0,
    "stability": 60.0,
    "agency": 40.0,
    "openness": 50.0,
}

HARMFUL_KEYWORDS = [
    "adult",
    "violence",
    "violent",
    "drugs",
    "weapons",
    "gore",
    "hate",
    "sexual",
    "suicide",
    "self-harm",
]

TOXIC_CATEGORY_KEYWORDS = [
    "adult",
    "violence",
    "drugs",
    "weapons",
    "gore",
    "hate",
]

# Next-phase TODOs requested by the implementation brief:
# - Move upload parser 300-item caps into parser configuration.
# - Replace upload duration estimates with YouTube API duration and richer
#   chronological timeline inference.
# - Keep frontend insightMock removal for the separate dashboard phase.
