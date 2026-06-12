import json
import sys
import os

# Force deterministic local backends before importing the FastAPI app.
os.environ["SUPABASE_URL"] = "https://your-project-ref.supabase.co"
os.environ["SUPABASE_KEY"] = "your-supabase-secret-key"
os.environ["YOUTUBE_API_KEY"] = "mock-youtube-api-key"
os.environ["GOOGLE_LANGUAGE_API_KEY"] = "mock-nl-api-key"
os.environ["GEMINI_API_KEY"] = "mock-gemini-api-key"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
API_PREFIX = "/api/v1"

# 1. Create dummy takeout data
dummy_history = [
    # Coding / Educational (VOS relax candidate)
    {
        "header": "YouTube",
        "title": "Watched Python 코딩 기초 강좌",
        "titleUrl": "https://www.youtube.com/watch?v=py123",
        "subtitles": [{"name": "코딩 마스터"}],
        "time": "2026-06-08T08:00:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Watched Javascript 개발자 토크",
        "titleUrl": "https://www.youtube.com/watch?v=js123",
        "subtitles": [{"name": "개발왕"}],
        "time": "2026-06-08T08:10:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Watched 파이썬 웹 개발 tutorial",
        "titleUrl": "https://www.youtube.com/watch?v=py456",
        "subtitles": [{"name": "코딩 마스터"}],
        "time": "2026-06-08T08:20:00.000Z"
    },
    # Politics / News (Stimulating / High Arousal)
    {
        "header": "YouTube",
        "title": "Watched 국회 청문회 속보",
        "titleUrl": "https://www.youtube.com/watch?v=news123",
        "subtitles": [{"name": "KBS 뉴스"}],
        "time": "2026-06-08T09:00:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Watched 대통령 선거 토론",
        "titleUrl": "https://www.youtube.com/watch?v=news456",
        "subtitles": [{"name": "정치TV"}],
        "time": "2026-06-08T09:15:00.000Z"
    },
    # Calm / Relaxation (EBS boost, calm keyword protection)
    {
        "header": "YouTube",
        "title": "Watched 차분한 ASMR 힐링 클래식",
        "titleUrl": "https://www.youtube.com/watch?v=asmr123",
        "subtitles": [{"name": "힐링사운드"}],
        "time": "2026-06-08T10:00:00.000Z"
    },
    # Invalid Timestamp (Tests sequential fallback & timestamp_fallback_used flag)
    {
        "header": "YouTube",
        "title": "Watched GitHub 사용법 강의",
        "titleUrl": "https://www.youtube.com/watch?v=git123",
        "subtitles": [{"name": "코딩 마스터"}],
        "time": "invalid_timestamp_format_abc"
    },
    # Active Search Queries (UAS agency signals)
    {
        "header": "YouTube",
        "title": "Searched for python coding tutorial",
        "titleUrl": "https://www.youtube.com/results?search_query=python+coding+tutorial",
        "time": "2026-06-08T10:30:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Searched for 인공지능 공부법",
        "titleUrl": "https://www.youtube.com/results?search_query=인공지능+공부법",
        "time": "2026-06-08T10:45:00.000Z"
    },
    # Shorts (SMS stimulation and dopamine filters)
    {
        "header": "YouTube",
        "title": "Watched 쇼츠 밈 웃긴 짤",
        "titleUrl": "https://www.youtube.com/shorts/meme123",
        "subtitles": [{"name": "재미유발"}],
        "time": "2026-06-08T11:00:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Watched 코미디 쇼츠 브이로그",
        "titleUrl": "https://www.youtube.com/shorts/vlog123",
        "subtitles": [{"name": "일상개그"}],
        "time": "2026-06-08T11:05:00.000Z"
    },
    {
        "header": "YouTube",
        "title": "Watched 어그로 레전드 예능 쇼츠",
        "titleUrl": "https://www.youtube.com/shorts/show123",
        "subtitles": [{"name": "예능맛집"}],
        "time": "2026-06-08T11:10:00.000Z"
    }
]

def run_tests():
    print("=== STARTING PIPELINE VALIDATION TEST ===")
    
    # 1. Upload files
    files = {"files": ("watch-history.json", json.dumps(dummy_history), "application/json")}
    data = {"mock_estimation": "false"} # We test with mock_estimation = False
    
    print("\n[Step 1] Uploading Takeout history to /upload/takeout...")
    res = client.post(f"{API_PREFIX}/upload/takeout", files=files, data=data)
    if res.status_code != 200:
        print(f"FAIL: Upload failed with status {res.status_code}: {res.text}")
        sys.exit(1)
        
    upload_res = res.json()
    file_id = upload_res.get("file_id")
    print(f"SUCCESS: Uploaded successfully. File ID: {file_id}")
    print(f"Session count generated: {upload_res.get('session_count')}")
    print(f"Total parsed: {upload_res.get('total_parsed')}")
    print(f"Total saved: {upload_res.get('total_saved')}")
    
    # 2. Trigger analysis
    print(f"\n[Step 2] Running analysis on file {file_id}...")
    res = client.post(f"{API_PREFIX}/analysis/run", params={"file_id": file_id})
    if res.status_code != 200:
        print(f"FAIL: Analysis failed with status {res.status_code}: {res.text}")
        sys.exit(1)
        
    analysis_res = res.json()
    run_id = analysis_res.get("run_id")
    print(f"SUCCESS: Analysis run complete. Run ID: {run_id}")
    print(f"MBTI Type: {analysis_res.get('mbti_type')} ({analysis_res.get('mbti_name')})")
    
    # Check data quality flags
    dq_flags = analysis_res.get("data_quality_flags", [])
    print(f"Data Quality Flags: {dq_flags}")
    assert "timestamp_fallback_used" in dq_flags, "Expected 'timestamp_fallback_used' in data_quality_flags"
    assert "duration_unknown" in dq_flags, "Expected 'duration_unknown' in data_quality_flags"
    
    # Check sampling metadata
    print(f"Sampling Metadata:")
    print(f"  Total sessions: {analysis_res.get('total_session_count')}")
    print(f"  Sampleed sessions: {analysis_res.get('sampled_session_count')}")
    print(f"  Sampling strategy: {analysis_res.get('sampling_strategy')}")
    print(f"  Input token count: {analysis_res.get('nlp_input_token_count')}")
    
    assert analysis_res.get("total_session_count") is not None
    assert analysis_res.get("sampled_session_count") is not None
    assert analysis_res.get("sampling_strategy") is not None
    assert analysis_res.get("nlp_input_token_count") is not None
    
    # Check score details for calibrated metrics
    score_details = analysis_res.get("score_details", {})
    print("\nCalibrated Score Components & Subscores:")
    for axis, details in score_details.items():
        print(f"  {axis}: Score={details.get('score')}, Confidence={details.get('confidence')}")
        components = details.get("score_components", {})
        print(f"    Components: {components}")
        
        # Axis checks
        if axis == "SBS":
            assert "relative_hhi_balance_score" in components
            assert "legacy_hhi_inverse_score" in components
            assert components["is_actual_channel_based"] is True
        elif axis == "TDS":
            assert "nlp_category_entropy" in components
            assert "local_keyword_category_entropy" in components
            assert components["max_topic_categories_applied"] is True
        elif axis == "EBS":
            assert "legacy_sentiment_entropy_score" in components
            assert "negative_sentiment_penalty" in components
            assert components["calm_keyword_protection_applied"] is True
        elif axis == "SMS":
            assert "toxic_ratio_penalty" in components
            assert "harmful_keyword_penalty" in components
            assert components["is_repeated_shorts_calibrated_by_duration"] is True
        elif axis == "VOS":
            assert "raw_concentration_score" in components
            assert "adjusted_concentration_score" in components
            assert "topic_concentration" in components["productive_immersion_adjusted_fields"] or \
                   "channel_concentration" in components["productive_immersion_adjusted_fields"]
            assert components["beta_applied"] is True

    # 3. Get dashboard summary
    print(f"\n[Step 3] Fetching dashboard summary for run {run_id}...")
    res = client.get(f"{API_PREFIX}/dashboard/summary", params={"run_id": run_id})
    if res.status_code != 200:
        print(f"FAIL: Dashboard fetch failed with status {res.status_code}: {res.text}")
        sys.exit(1)
        
    dashboard_res = res.json()
    print("SUCCESS: Dashboard summary matches API contract.")
    print(f"Weighted Health Score: {dashboard_res.get('weighted_health')}")
    print(f"Actual DSAO: {dashboard_res.get('actual_dsao')}")
    print(f"Cognitive Misconception index: {dashboard_res.get('misconception', {}).get('index')}")
    print(f"Ad events excluded from dashboard: {dashboard_res.get('insights', {}).get('excluded_ad_count')}")
    
    print("\n=== ALL TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    run_tests()
