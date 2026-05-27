import os
import random

import pymysql
import spotipy
from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI
from spotipy.oauth2 import SpotifyClientCredentials
# --------------------------
# 0️⃣ 환경변수(.env) 로드
# --------------------------
load_dotenv()


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# OpenAI 최신 SDK 클라이언트 생성
client = OpenAI(api_key=required_env("OPENAI_API_KEY"))

app = Flask(__name__)

# --------------------------
# 1️⃣ MySQL 연결 설정
# --------------------------
db = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=required_env("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "emotion_db"),
    charset="utf8mb4"
)

# --------------------------
# 2️⃣ Spotify 인증
# --------------------------
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=required_env("SPOTIFY_CLIENT_ID"),
    client_secret=required_env("SPOTIFY_CLIENT_SECRET")
))

# --------------------------
# 3️⃣ GPT 기반 감정 분석
# --------------------------
def detect_emotion_gpt(text):
    prompt = f"""
    아래 문장의 감정을 joy, sadness, anger, fear, neutral, love, hope, calm, healing, tired 중 하나로 분류해줘.

    문장: "{text}"

    출력: 감정 단어만 반환.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    emotion = response.choices[0].message.content.strip().lower()

    valid = ["joy","sadness","anger","fear","neutral","love","hope","calm","healing","tired"]
    if emotion not in valid:
        emotion = "neutral"

    return emotion


def detect_emotion_advanced(text, user_id="guest"):
    cursor = db.cursor()

    # 1) 키워드 사전 기반 보정 (emotion_keywords 사용)
    cursor.execute("""
        SELECT emotion_code
        FROM emotion_keywords
        WHERE %s LIKE CONCAT('%%', keyword, '%%')
        LIMIT 1
    """, (text,))
    row = cursor.fetchone()
    if row:
        emotion = row[0]
    else:
        # 2) GPT 기반 감정 분석
        emotion = detect_emotion_gpt(text)

    # 3) 과거 동일 문장이 감정 데이터에 있으면 그 감정을 우선 사용 (학습 효과)
    cursor.execute("""
        SELECT predicted_emotion
        FROM emotion_training_data
        WHERE user_input = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (text,))
    prev = cursor.fetchone()
    if prev:
        emotion = prev[0]

    # 4) 학습 데이터 저장 (모델 개선)
    cursor.execute("""
        INSERT INTO emotion_training_data (user_input, predicted_emotion)
        VALUES (%s, %s)
    """, (text, emotion))
    db.commit()

    # 5) 사용자 감정 프로필 업데이트 (개인화 추천)
    cursor.execute("""
        INSERT INTO user_emotion_profile (user_id, emotion_code, cnt)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE
            cnt = cnt + 1,
            last_update = CURRENT_TIMESTAMP
    """, (user_id, emotion))
    db.commit()

    return emotion

# --------------------------
# 4️⃣ 감정 → 장르 & 메시지
# --------------------------
mood_to_genre = {
    "joy": "pop",
    "sadness": "acoustic",
    "anger": "metal",
    "fear": "ambient",
    "neutral": "chill",
    "love": "romance",
    "hope": "k-pop",
    "calm": "piano",
    "healing": "acoustic",
    "tired": "sleep"
}

emotion_messages = {
    "joy": "기분이 좋아보이네요! 오늘 하루도 즐겁게 보내세요 🎉",
    "sadness": "오늘 많이 힘드셨죠? 따뜻한 음악으로 마음을 달래드릴게요 💙",
    "anger": "화나는 날엔 음악이 도움이 돼요. 같이 진정해볼까요? 🔥",
    "fear": "걱정되는 마음, 이해해요. 차분한 곡으로 안정시켜볼게요 🌙",
    "love": "사랑의 감정은 언제나 아름답죠 💕",
    "hope": "희망이 느껴지네요! 밝은 에너지로 응원할게요 ☀️",
    "calm": "마음이 평온하신가 봐요 🌿",
    "healing": "위로가 필요한 순간, 조용히 마음을 감싸줄 노래를 드릴게요 🌸",
    "tired": "오늘 정말 수고 많았어요 😴 이제 쉬어가요.",
    "neutral": "편하게 들을 수 있는 곡들을 추천드릴게요."
}

# --------------------------
# 5️⃣ Flask 라우팅
# --------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    user_input = request.form.get("user_input", "").strip()

    # GPT 감정 분석
    # 나중에 로그인 기능 추가하면 user_id 바꾸면 됨
    user_id = "guest"

    emotion = detect_emotion_advanced(user_input, user_id=user_id)

    if not emotion:
        emotion = "neutral"

    # 감정 로그 DB 저장
    cursor = db.cursor()
    cursor.execute("INSERT INTO emotion_logs (emotion_code, user_input) VALUES (%s, %s)",
                   (emotion, user_input))
    db.commit()

    genre = mood_to_genre.get(emotion, "pop")
    message = emotion_messages.get(emotion, emotion_messages["neutral"])

    # Spotify 최신곡 검색
    results_new = sp.search(q=f"genre:{genre} year:2023-2025", type="track", limit=10)
    latest_tracks = results_new["tracks"]["items"] if "tracks" in results_new else []
    latest_hits = random.sample(latest_tracks, min(5, len(latest_tracks)))

    # Spotify 오래된 명곡 검색
    results_old = sp.search(q=f"genre:{genre} year:2000-2010", type="track", limit=10)
    old_tracks = results_old["tracks"]["items"] if "tracks" in results_old else []
    classic_hits = random.sample(old_tracks, min(5, len(old_tracks)))

    # 댓글 가져오기
    cursor.execute("SELECT comment_text FROM emotion_comments WHERE emotion_code=%s ORDER BY created_at DESC",
                   (emotion,))
    comments = [row[0] for row in cursor.fetchall()]

    def format_tracks(tracks):
        return [{
            "name": t.get("name"),
            "artist": t.get("artists", [{}])[0].get("name"),
            "url": t.get("external_urls", {}).get("spotify"),
            "album_image": t.get("album", {}).get("images", [{}])[0].get("url")
        } for t in tracks]

    return render_template("index.html",
                           emotion=emotion,
                           message=message,
                           latest_hits=format_tracks(latest_hits),
                           classic_hits=format_tracks(classic_hits),
                           comments=comments)

# --------------------------
# 6️⃣ 댓글 작성
# --------------------------
@app.route("/comment", methods=["POST"])
def comment():
    emotion = request.form.get("emotion")
    comment_text = request.form.get("comment_text", "").strip()

    # 댓글 저장
    if emotion and comment_text:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO emotion_comments (emotion_code, comment_text) VALUES (%s, %s)",
            (emotion, comment_text)
        )
        db.commit()

    # 댓글 다시 불러오기
    cursor = db.cursor()
    cursor.execute("SELECT comment_text FROM emotion_comments WHERE emotion_code=%s ORDER BY created_at DESC", (emotion,))
    comments = [row[0] for row in cursor.fetchall()]

    # 다시 추천곡도 재사용
    genre = mood_to_genre.get(emotion, "pop")
    message = emotion_messages.get(emotion, emotion_messages["neutral"])

    # 최신곡
    results_new = sp.search(q=f"genre:{genre} year:2023-2025", type="track", limit=10)
    latest_tracks = results_new["tracks"]["items"] if results_new and "tracks" in results_new else []
    latest_hits = random.sample(latest_tracks, min(5, len(latest_tracks)))

    # 클래식
    results_old = sp.search(q=f"genre:{genre} year:2000-2010", type="track", limit=10)
    old_tracks = results_old["tracks"]["items"] if results_old and "tracks" in results_old else []
    classic_hits = random.sample(old_tracks, min(5, len(old_tracks)))

    def format_tracks(tracks):
        return [{
            "name": t.get("name"),
            "artist": t.get("artists", [{}])[0].get("name"),
            "url": t.get("external_urls", {}).get("spotify"),
            "album_image": t.get("album", {}).get("images", [{}])[0].get("url") if t.get("album", {}).get("images") else None
        } for t in tracks]

    # 최종 렌더링 (감정 유지)
    return render_template(
        "index.html",
        emotion=emotion,
        message=message,
        latest_hits=format_tracks(latest_hits),
        classic_hits=format_tracks(classic_hits),
        comments=comments
    )

#감정 비율 가져오기
@app.route("/stats")
def stats():
    cursor = db.cursor()

    # 오늘 날짜 감정 데이터 가져오기
    cursor.execute("""
        SELECT predicted_emotion 
        FROM emotion_training_data
        WHERE DATE(created_at) = CURDATE()
    """)
    rows = cursor.fetchall()

    if not rows:
        emotions = []
    else:
        emotions = [r[0] for r in rows]

    # 감정 분류
    positive = ["joy", "love", "hope", "calm", "healing"]
    negative = ["sadness", "anger", "fear", "tired"]
    neutral = ["neutral"]

    pos = sum(e in positive for e in emotions)
    neg = sum(e in negative for e in emotions)
    neu = sum(e in neutral for e in emotions)

    total = len(emotions) if emotions else 1

    # 긍정/부정 비율 계산 → 0~100 게이지값
    gauge_value = int((pos - neg) / total * 50 + 50)
    gauge_value = max(0, min(100, gauge_value))  # 0~100 사이 제한

    # 배경 판단
    if gauge_value >= 65:
        mood = "positive"
    elif gauge_value <= 35:
        mood = "negative"
    else:
        mood = "neutral"

    return render_template(
        "stats.html",
        gauge=gauge_value,
        mood=mood,
        positive_count=pos,
        negative_count=neg,
        neutral_count=neu,
        total_count=total
    )



# --------------------------
# 7️⃣ 서버 실행
# --------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
