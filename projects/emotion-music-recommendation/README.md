# 감정 음악 추천 앱

사용자가 입력한 문장을 GPT로 감정 분석하고, 감정에 맞는 Spotify 음악을 추천하는 Flask 기반 웹 앱입니다.

## 주요 기능

- GPT 기반 감정 분류
- 감정별 최신곡 / 클래식 추천
- Spotify API 기반 트랙 검색
- MySQL 기반 감정 기록, 댓글, 사용자 감정 통계 저장
- 오늘의 감정 비율 통계 화면

## 실행 준비

1. `flask_app/flaskex/requirements.txt`의 패키지를 설치합니다.
2. `flask_app/flaskex/.env.example`을 참고해 `.env` 파일을 만듭니다.
3. `Mysql-DB.zip` 안의 SQL 파일로 `emotion_db` 데이터베이스를 구성합니다.
4. `flask_app/flaskex/app.py`를 실행한 뒤 `http://127.0.0.1:5000`으로 접속합니다.

`.env`에는 OpenAI, Spotify, MySQL 접속 정보가 필요합니다. 실제 키와 비밀번호는 GitHub에 올리지 않습니다.
