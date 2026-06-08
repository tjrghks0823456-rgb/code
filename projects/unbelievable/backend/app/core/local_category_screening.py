import re

CATEGORY_KEYWORDS = {
    "게임": [
        "게임", "game", "롤", "league of legends", "minecraft", "마인크래프트", 
        "오버워치", "overwatch", "배틀그라운드", "pubg", "스팀", "steam", "공략", "플레이"
    ],
    "정치/뉴스": [
        "뉴스", "news", "정치", "민주당", "공화당", "대통령", "선거", "국회", "의원", 
        "속보", "이슈", "사건", "토론", "비판", "여론"
    ],
    "코딩/기술": [
        "코딩", "coding", "프로그래밍", "programming", "python", "파이썬", 
        "javascript", "자바스크립트", "개발자", "developer", "it", "tech", "ai", 
        "artificial intelligence", "인공지능", "gpt", "github", "깃허브", "서버", "server",
        "computers & electronics", "computer"
    ],
    "금융/투자": [
        "금융", "finance", "투자", "invest", "주식", "stock", "부동산", "코인", 
        "crypto", "재테크", "달러", "금리", "워렌 버핏", "자산", "경제", "시장"
    ],
    "예능/쇼츠/밈": [
        "예능", "쇼츠", "shorts", "밈", "meme", "코미디", "comedy", "유머", 
        "짤", "개그", "웃긴", "브이로그", "vlog", "썰"
    ],
    "음악": [
        "음악", "music", "노래", "song", "플레이리스트", "playlist", "커버", 
        "cover", "라이브", "mv", "뮤직비디오", "가사", "lyrics", "bgm"
    ],
    "교육/강의": [
        "교육", "강의", "강좌", "lecture", "tutorial", "튜토리얼", "수학", 
        "영어", "과학", "역사", "study", "공부", "배우기", "개념", "해설"
    ],
    "건강/운동": [
        "건강", "health", "운동", "workout", "헬스", "fitness", "다이어트", 
        "diet", "스포츠", "sports", "축구", "soccer", "야구", "baseball", "홈트"
    ]
}

def estimate_local_category(text: str) -> str:
    if not text:
        return "기타"
    lower_text = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            return category
    return "기타"
