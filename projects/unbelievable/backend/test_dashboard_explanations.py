import json
import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Define 7 user scenarios
scenarios_data = {
    "1_shorts_focused": [
        {"header": "YouTube", "title": "Watched 숏츠 1", "titleUrl": "https://www.youtube.com/shorts/s1", "time": "2026-06-08T08:00:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 2", "titleUrl": "https://www.youtube.com/shorts/s2", "time": "2026-06-08T08:01:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 3", "titleUrl": "https://www.youtube.com/shorts/s3", "time": "2026-06-08T08:02:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 4", "titleUrl": "https://www.youtube.com/shorts/s4", "time": "2026-06-08T08:03:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 5", "titleUrl": "https://www.youtube.com/shorts/s5", "time": "2026-06-08T08:04:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 6", "titleUrl": "https://www.youtube.com/shorts/s6", "time": "2026-06-08T08:05:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 7", "titleUrl": "https://www.youtube.com/shorts/s7", "time": "2026-06-08T08:06:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 8", "titleUrl": "https://www.youtube.com/shorts/s8", "time": "2026-06-08T08:07:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 9", "titleUrl": "https://www.youtube.com/shorts/s9", "time": "2026-06-08T08:08:00Z"},
        {"header": "YouTube", "title": "Watched 숏츠 10", "titleUrl": "https://www.youtube.com/shorts/s10", "time": "2026-06-08T08:09:00Z"},
    ],
    "2_politics_biased": [
        {"header": "YouTube", "title": "Watched 정치 평론 논란 이슈", "titleUrl": "https://www.youtube.com/watch?v=p1", "time": "2026-06-08T08:00:00Z"},
        {"header": "YouTube", "title": "Watched 국회 청문회 속보 폭로", "titleUrl": "https://www.youtube.com/watch?v=p2", "time": "2026-06-08T08:15:00Z"},
        {"header": "YouTube", "title": "Watched 대통령 후보 논조 비평", "titleUrl": "https://www.youtube.com/watch?v=p3", "time": "2026-06-08T08:30:00Z"},
        {"header": "YouTube", "title": "Watched 뉴스 특보 긴급 토론", "titleUrl": "https://www.youtube.com/watch?v=p4", "time": "2026-06-08T08:45:00Z"},
        {"header": "YouTube", "title": "Watched 정당 갈등 폭탄 발언", "titleUrl": "https://www.youtube.com/watch?v=p5", "time": "2026-06-08T09:00:00Z"},
        {"header": "YouTube", "title": "Watched 사회적 논란 팩트체크", "titleUrl": "https://www.youtube.com/watch?v=p6", "time": "2026-06-08T09:15:00Z"},
        {"header": "YouTube", "title": "Watched 선거 여론조사 긴급 분석", "titleUrl": "https://www.youtube.com/watch?v=p7", "time": "2026-06-08T09:30:00Z"},
        {"header": "YouTube", "title": "Watched 시사 토크쇼 폭소", "titleUrl": "https://www.youtube.com/watch?v=p8", "time": "2026-06-08T09:45:00Z"},
        {"header": "YouTube", "title": "Watched 국회 국정감사 생중계", "titleUrl": "https://www.youtube.com/watch?v=p9", "time": "2026-06-08T10:00:00Z"},
        {"header": "YouTube", "title": "Watched 정치인 폭탄 발언 논란", "titleUrl": "https://www.youtube.com/watch?v=p10", "time": "2026-06-08T10:15:00Z"},
    ],
    "3_sports_hobby": [
        {"header": "YouTube", "title": "Watched 해외 축구 손흥민 골 하이라이트", "titleUrl": "https://www.youtube.com/watch?v=s1", "time": "2026-06-08T08:00:00Z"},
        {"header": "YouTube", "title": "Watched 프로야구 홈런 더블헤더 분석", "titleUrl": "https://www.youtube.com/watch?v=s2", "time": "2026-06-08T08:20:00Z"},
        {"header": "YouTube", "title": "Watched 골프 드라이버 스윙 레슨", "titleUrl": "https://www.youtube.com/watch?v=s3", "time": "2026-06-08T08:40:00Z"},
        {"header": "YouTube", "title": "Watched 솔로 캠핑 감성 우중 브이로그", "titleUrl": "https://www.youtube.com/watch?v=s4", "time": "2026-06-08T09:00:00Z"},
        {"header": "YouTube", "title": "Watched 주말 낚시 명소 대어 낚기", "titleUrl": "https://www.youtube.com/watch?v=s5", "time": "2026-06-08T09:20:00Z"},
        {"header": "YouTube", "title": "Watched 등산 초보 북한산 코스 추천", "titleUrl": "https://www.youtube.com/watch?v=s6", "time": "2026-06-08T09:40:00Z"},
        {"header": "YouTube", "title": "Watched 자전거 정비 및 자가 세차 꿀팁", "titleUrl": "https://www.youtube.com/watch?v=s7", "time": "2026-06-08T10:00:00Z"},
        {"header": "YouTube", "title": "Watched 홈트레이닝 초보 가슴 운동 루틴", "titleUrl": "https://www.youtube.com/watch?v=s8", "time": "2026-06-08T10:20:00Z"},
        {"header": "YouTube", "title": "Watched 테니스 백핸드 자세 교정 강좌", "titleUrl": "https://www.youtube.com/watch?v=s9", "time": "2026-06-08T10:40:00Z"},
        {"header": "YouTube", "title": "Watched 캠핑 장비 내돈내산 추천 리뷰", "titleUrl": "https://www.youtube.com/watch?v=s10", "time": "2026-06-08T11:00:00Z"},
    ],
    "4_diverse_searches": [
        {"header": "YouTube", "title": "Searched for 파이썬 장고 강의", "titleUrl": "https://www.youtube.com/results?search_query=Django", "time": "2026-06-08T08:00:00Z"},
        {"header": "YouTube", "title": "Searched for 세계 역사 다큐", "titleUrl": "https://www.youtube.com/results?search_query=History", "time": "2026-06-08T08:10:00Z"},
        {"header": "YouTube", "title": "Searched for 헬스 등 운동법", "titleUrl": "https://www.youtube.com/results?search_query=Workout", "time": "2026-06-08T08:20:00Z"},
        {"header": "YouTube", "title": "Searched for 부동산 청약 정보", "titleUrl": "https://www.youtube.com/results?search_query=RealEstate", "time": "2026-06-08T08:30:00Z"},
        {"header": "YouTube", "title": "Searched for 인문학 철학 입문", "titleUrl": "https://www.youtube.com/results?search_query=Philosophy", "time": "2026-06-08T08:40:00Z"},
        {"header": "YouTube", "title": "Searched for 강아지 훈련 시키기", "titleUrl": "https://www.youtube.com/results?search_query=DogTraining", "time": "2026-06-08T08:50:00Z"},
        {"header": "YouTube", "title": "Searched for 여행 브이로그 도쿄", "titleUrl": "https://www.youtube.com/results?search_query=TokyoTravel", "time": "2026-06-08T09:00:00Z"},
        {"header": "YouTube", "title": "Searched for 신용 카드 재테크", "titleUrl": "https://www.youtube.com/results?search_query=Finance", "time": "2026-06-08T09:10:00Z"},
        {"header": "YouTube", "title": "Searched for 맛있는 찌개 요리법", "titleUrl": "https://www.youtube.com/results?search_query=Cooking", "time": "2026-06-08T09:20:00Z"},
        {"header": "YouTube", "title": "Searched for 우주 기원 다큐", "titleUrl": "https://www.youtube.com/results?search_query=Universe", "time": "2026-06-08T09:30:00Z"},
    ],
    "5_timestamp_fallback": [
        {"header": "YouTube", "title": "Watched 파이썬 코딩", "titleUrl": "https://www.youtube.com/watch?v=1", "time": "invalid_timestamp_1"},
        {"header": "YouTube", "title": "Watched 자바스크립트 강의", "titleUrl": "https://www.youtube.com/watch?v=2", "time": "invalid_timestamp_2"},
        {"header": "YouTube", "title": "Watched 데이터베이스 강론", "titleUrl": "https://www.youtube.com/watch?v=3", "time": "invalid_timestamp_3"},
        {"header": "YouTube", "title": "Watched 네트워크 기초", "titleUrl": "https://www.youtube.com/watch?v=4", "time": "invalid_timestamp_4"},
        {"header": "YouTube", "title": "Watched 운영체제 론", "titleUrl": "https://www.youtube.com/watch?v=5", "time": "invalid_timestamp_5"},
        {"header": "YouTube", "title": "Watched 자료구조 개념", "titleUrl": "https://www.youtube.com/watch?v=6", "time": "invalid_timestamp_6"},
        {"header": "YouTube", "title": "Watched 알고리즘 문제풀이", "titleUrl": "https://www.youtube.com/watch?v=7", "time": "invalid_timestamp_7"},
        {"header": "YouTube", "title": "Watched 컴파일러 개론", "titleUrl": "https://www.youtube.com/watch?v=8", "time": "invalid_timestamp_8"},
        {"header": "YouTube", "title": "Watched 소프트웨어 공학", "titleUrl": "https://www.youtube.com/watch?v=9", "time": "invalid_timestamp_9"},
        {"header": "YouTube", "title": "Watched 프로젝트 관리 실무", "titleUrl": "https://www.youtube.com/watch?v=10", "time": "invalid_timestamp_10"},
    ],
    "6_duration_unknown": [
        {"header": "YouTube", "title": "Watched 단일 시청 영상 기록", "titleUrl": "https://www.youtube.com/watch?v=single", "time": "2026-06-08T08:00:00Z"},
    ],
    "7_nlp_fallback": [
        # Naturally fallback will occur because google API key is mock, so local Sejong parser is used!
        {"header": "YouTube", "title": "Watched 한글 형태소 테스트 문장", "titleUrl": "https://www.youtube.com/watch?v=kor1", "time": "2026-06-08T08:00:00Z"},
        {"header": "YouTube", "title": "Watched 자연어 처리 기술 공부", "titleUrl": "https://www.youtube.com/watch?v=kor2", "time": "2026-06-08T08:15:00Z"},
        {"header": "YouTube", "title": "Watched 머신러닝 모델 평가 방법", "titleUrl": "https://www.youtube.com/watch?v=kor3", "time": "2026-06-08T08:30:00Z"},
        {"header": "YouTube", "title": "Watched 인공신경망 딥러닝 입문", "titleUrl": "https://www.youtube.com/watch?v=kor4", "time": "2026-06-08T08:45:00Z"},
        {"header": "YouTube", "title": "Watched 어그로 자극 기사 요약", "titleUrl": "https://www.youtube.com/watch?v=kor5", "time": "2026-06-08T09:00:00Z"},
        {"header": "YouTube", "title": "Watched 컴퓨터 비전 기초 강의", "titleUrl": "https://www.youtube.com/watch?v=kor6", "time": "2026-06-08T09:15:00Z"},
        {"header": "YouTube", "title": "Watched 음성 인식 모델 원리", "titleUrl": "https://www.youtube.com/watch?v=kor7", "time": "2026-06-08T09:30:00Z"},
        {"header": "YouTube", "title": "Watched 강화학습 에이전트 설계", "titleUrl": "https://www.youtube.com/watch?v=kor8", "time": "2026-06-08T09:45:00Z"},
        {"header": "YouTube", "title": "Watched 대규모 언어 모델 동향", "titleUrl": "https://www.youtube.com/watch?v=kor9", "time": "2026-06-08T10:00:00Z"},
        {"header": "YouTube", "title": "Watched 추천 시스템 알고리즘", "titleUrl": "https://www.youtube.com/watch?v=kor10", "time": "2026-06-08T10:15:00Z"},
    ]
}

def validate_scenario(name, history):
    print(f"\n==================================================")
    print(f" TESTING SCENARIO: {name}")
    print(f"==================================================")

    # 1. Upload
    files = {"files": ("watch-history.json", json.dumps(history), "application/json")}
    res = httpx.post(f"{BASE_URL}/upload/takeout", files=files, data={"mock_estimation": "false"})
    if res.status_code != 200:
        print(f"FAIL: Upload failed: {res.text}")
        sys.exit(1)
        
    file_id = res.json()["file_id"]
    
    # 2. Run analysis
    res = httpx.post(f"{BASE_URL}/analysis/run", params={"file_id": file_id}, timeout=120.0)
    if res.status_code != 200:
        print(f"FAIL: Analysis run failed: {res.text}")
        sys.exit(1)
        
    run_id = res.json()["run_id"]
    
    # 3. Fetch summary & check explanations & DSAO cards
    res = httpx.get(f"{BASE_URL}/dashboard/summary", params={"run_id": run_id}, timeout=120.0)
    if res.status_code != 200:
        print(f"FAIL: Fetch summary failed: {res.text}")
        sys.exit(1)
        
    summary = res.json()
    
    # Check actual_dsao exists
    assert "actual_dsao" in summary, f"Scenario {name} missing 'actual_dsao' key"
    actual_dsao = summary["actual_dsao"]
    print(f"DSAO Code: {actual_dsao.get('code')}")
    print(f"DSAO Name: {actual_dsao.get('name')}")
    print(f"DSAO Short Summary: {actual_dsao.get('short_summary')}")
    print(f"DSAO Strengths: {actual_dsao.get('strengths')}")
    print(f"DSAO Risks: {actual_dsao.get('risks')}")
    print(f"DSAO opposite: {actual_dsao.get('opposite_type')}")
    print(f"DSAO based_on: {actual_dsao.get('based_on')}")
    print(f"DSAO confidence: {actual_dsao.get('confidence')}")
    
    # Verify legacy MBTI is not represented as actual main type for display
    # (i.e. actual_dsao has actual_dsao keys, MBTI remains under separate 'mbti' key)
    assert actual_dsao.get("code") is not None, "DSAO actual code is None"
    assert "scores" in actual_dsao, "DSAO scores dict missing"
    
    # Check explanations exists
    assert "explanations" in summary, f"Scenario {name} missing 'explanations' key"
    explanations = summary["explanations"]
    print("Explanations keys present:")
    for key, exp in explanations.items():
        print(f"  - {key}: value={exp.get('value')}, label={exp.get('label')}")
        required_fields = ["label", "value", "reason", "evidence", "caution", "improvement_hint"]
        for f in required_fields:
            assert f in exp, f"Explanation key '{key}' missing subfield '{f}'"
            assert exp[f] != "", f"Explanation key '{key}' subfield '{f}' is empty"
            
    # Verify duration related wording is clean in all explanations
    summary_str = json.dumps(summary, ensure_ascii=False)
    assert "실제 시청 시간" not in summary_str, "Wording violation: '실제 시청 시간' found in response!"
    assert "watch duration" not in summary_str, "Wording violation: 'watch duration' found in response!"
    assert "actual duration" not in summary_str, "Wording violation: 'actual duration' found in response!"

    # 4. Generate detox recommendations
    res = httpx.post(f"{BASE_URL}/detox/generate", params={"run_id": run_id}, timeout=120.0)
    if res.status_code != 200:
        print(f"FAIL: Generate detox failed: {res.text}")
        sys.exit(1)
        
    detox = res.json()
    assert "missions" in detox, f"Scenario {name} missing 'missions' key in detox"
    missions = detox["missions"]
    print(f"Recommended missions count: {len(missions)}")
    
    for m in missions:
        print(f"  * Mission ID: {m.get('mission_id') or m.get('id')}")
        print(f"    Title: {m.get('title')}")
        print(f"    Why recommended: {m.get('why_recommended')}")
        print(f"    Target issue: {m.get('target_issue')}")
        print(f"    Confidence: {m.get('confidence')}")
        
        # Verify fields are present and why_recommended is not empty
        assert m.get("why_recommended") is not None, "Mission why_recommended is None"
        assert m.get("why_recommended") != "", "Mission why_recommended is empty string"
        assert m.get("confidence") in ["HIGH", "MEDIUM", "LOW"], f"Invalid runtime confidence: {m.get('confidence')}"
        assert m.get("target_issue") != "", "Mission target_issue is empty string"

    print(f"SUCCESS: Scenario {name} passed all checks!")

def main():
    print("=== STARTING SCENARIOS EXPLANATION & DETOX TEST ===")
    for name, history in scenarios_data.items():
        validate_scenario(name, history)
    print("\n=== ALL SCENARIOS VERIFIED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
