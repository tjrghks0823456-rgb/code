import os
from datetime import datetime

# Force deterministic local settings before importing application modules.
os.environ["SUPABASE_URL"] = "https://your-project-ref.supabase.co"
os.environ["SUPABASE_KEY"] = "your-supabase-secret-key"
os.environ["YOUTUBE_API_KEY"] = "mock-youtube-api-key"
os.environ["GOOGLE_LANGUAGE_API_KEY"] = "mock-nl-api-key"
os.environ["GEMINI_API_KEY"] = "mock-gemini-api-key"

from app.core.content_filters import detect_ad_event_reason
from app.core.interest_maps import classify_interest_topic
from app.core.takeout_parser import parse_single_item, parse_takeout_timestamp
from app.services.upload_service import apply_timeline_duration_estimates, build_data_quality_summary


def assert_timestamp_guards():
    korean, korean_warnings = parse_takeout_timestamp("2026. 6. 8. 오후 8:15:30 KST")
    assert korean == "2026-06-08 20:15:30", korean
    assert not korean_warnings

    english, english_warnings = parse_takeout_timestamp("Jun 8, 2026, 8:15:30 PM UTC")
    assert english == "2026-06-08 20:15:30", english
    assert not english_warnings

    unknown, unknown_warnings = parse_takeout_timestamp("令和8年6月8日 20時15分30秒")
    assert unknown is None
    assert "timestamp_format_unrecognized" in unknown_warnings

    parsed, _ = parse_single_item(
        {
            "title": "Watched 일본어 타임스탬프 샘플",
            "titleUrl": "https://www.youtube.com/watch?v=jp1",
            "time": "令和8年6月8日 20時15分30秒",
        },
        file_kind="watch",
    )
    assert parsed["event_time"] is None
    assert parsed["raw_timestamp"] == "令和8年6月8日 20時15分30秒"
    assert parsed["timestamp_parse_failed"] is True
    assert parsed["timestamp_parse_status"] == "failed"


def assert_ad_filter_guards():
    assert detect_ad_event_reason({
        "action_type": "view",
        "source_type": "watch_history",
        "title": "Watched 블랙프라이데이 세일 정보와 쿠폰 꿀팁",
        "titleUrl": "https://www.youtube.com/watch?v=dealinfo",
    }) is None

    ad_reason = detect_ad_event_reason({
        "action_type": "view",
        "source_type": "watch_history",
        "title": "Watched 광고 랜딩",
        "titleUrl": "https://googleadservices.com/pagead/aclk?adurl=https%3A%2F%2Fexample.com",
    })
    assert ad_reason and ad_reason.startswith("url_marker:"), ad_reason


def assert_category_metadata_fallbacks():
    category_topic = classify_interest_topic(
        "알 수 없는 제목",
        raw_item={"categoryId": "28"},
    )
    assert category_topic["category"] == "IT/테크"
    assert category_topic["classification_source"] == "metadata_category_id"

    topic_category = classify_interest_topic(
        "unknown title",
        raw_item={"topicCategories": ["https://en.wikipedia.org/wiki/Google_Cloud"]},
    )
    assert topic_category["category"] == "IT/테크"
    assert topic_category["classification_source"] == "metadata_topic_category"


def assert_timeline_gap_capping():
    first = {
        "action_type": "view",
        "source_type": "watch_history",
        "text_base": "2시간 공백 전 영상",
        "raw_item": {},
    }
    second = {
        "action_type": "view",
        "source_type": "watch_history",
        "text_base": "2시간 뒤 영상",
        "raw_item": {},
    }
    apply_timeline_duration_estimates(
        [
            (datetime(2026, 6, 8, 8, 0, 0), first),
            (datetime(2026, 6, 8, 10, 0, 0), second),
        ],
        mock_estimation_enabled=True,
    )
    assert first["duration_estimation_method"] == "idle_capped"
    assert first["estimated_duration_sec"] == 600
    assert first["estimated_duration_confidence"] == "low"

    short_gap = {
        "action_type": "view",
        "source_type": "watch_history",
        "text_base": "10분 공백 영상",
        "raw_item": {},
    }
    after_short_gap = {
        "action_type": "view",
        "source_type": "watch_history",
        "text_base": "10분 뒤 영상",
        "raw_item": {},
    }
    apply_timeline_duration_estimates(
        [
            (datetime(2026, 6, 8, 8, 0, 0), short_gap),
            (datetime(2026, 6, 8, 8, 10, 0), after_short_gap),
        ],
        mock_estimation_enabled=True,
    )
    assert short_gap["duration_estimation_method"] == "timeline_gap"
    assert short_gap["estimated_duration_sec"] == 600
    assert short_gap["estimated_duration_confidence"] == "medium"


def assert_data_quality_summary():
    events = []
    for idx in range(8):
        events.append({
            "action_type": "view",
            "source_type": "watch_history",
            "text_base": f"분류 불가 샘플 {idx}",
            "timestamp_parse_failed": True,
            "duration_estimation_method": "default_estimate",
        })
    for idx in range(2):
        events.append({
            "action_type": "view",
            "source_type": "watch_history",
            "text_base": f"메타데이터 샘플 {idx}",
            "categoryId": "17",
            "timestamp_parse_failed": False,
            "duration_estimation_method": "metadata",
        })

    summary = build_data_quality_summary(events, excluded_ad_count=3)
    assert summary["total_events"] == 10
    assert summary["valid_watch_events"] == 10
    assert summary["timestamp_parse_failed_count"] == 8
    assert summary["ad_filtered_count"] == 3
    assert summary["metadata_category_used_count"] == 2
    assert summary["uncategorized_ratio"] >= 0.8
    assert "timestamp_parse_low_confidence" in summary["warnings"]
    assert "high_uncategorized_ratio" in summary["warnings"]
    assert summary["analysis_confidence"] == "low"


def run_tests():
    assert_timestamp_guards()
    assert_ad_filter_guards()
    assert_category_metadata_fallbacks()
    assert_timeline_gap_capping()
    assert_data_quality_summary()
    print("SUCCESS: Takeout quality guard tests passed.")


if __name__ == "__main__":
    run_tests()
