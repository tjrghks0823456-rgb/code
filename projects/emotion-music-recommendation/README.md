# emotion-based-music-recommender

> Flask · GPT · Spotify API · MySQL 기반 복합 감정 분석 및 음악 추천 서비스

## 1. 프로젝트 개요

사용자가 현재 기분을 문장으로 입력하면 GPT로 감정을 분류하고, Spotify API를 통해 감정에 맞는 음악을 추천하는 Flask 기반 웹 앱입니다.

단순한 단일 감정 분류의 한계를 인식하고, "피곤하지만 후련함"처럼 복합 감정을 처리할 수 있도록 API 보조 분석과 사용자 피드백 DB를 활용한 추천 구조를 구현했습니다. 팀 프로젝트로 진행했습니다.

## 2. 개발 배경

기존의 감정 분류 모델은 감정을 하나의 카테고리로만 분류합니다. 하지만 실제 사람의 감정은 여러 감정이 섞여 있는 경우가 많습니다. 이 한계를 해결하기 위해 GPT API를 활용한 감정 후보 추출과 사용자 피드백을 DB에 저장해 추천을 개선하는 구조를 시도했습니다.

## 3. 주요 기능

- **GPT 기반 감정 분류**: 사용자 문장을 GPT로 분석해 감정 카테고리 추출
- **복합 감정 처리**: 단일 감정이 아닌 여러 감정 후보 동시 처리
- **Spotify 음악 추천**: 감정별 최신곡 / 클래식 트랙 검색 및 추천
- **MySQL 기록 저장**: 감정 기록, 댓글, 사용자 감정 통계 저장
- **피드백 DB**: 사용자 반응을 저장해 추천 개선 구조 구현
- **오늘의 감정 통계**: 전체 사용자 감정 비율 시각화

## 4. 시스템 구조

```
[사용자 입력 (감정 문장)]
        ↓
[Flask 서버]
  ├─ GPT API → 감정 분류
  ├─ Spotify API → 트랙 검색
  └─ MySQL DB → 기록/피드백 저장
        ↓
[추천 결과 페이지]
```

## 5. 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python |
| Framework | Flask |
| 감정 분류 | OpenAI GPT API |
| 음악 추천 | Spotify API |
| Database | MySQL |
| 개발 환경 | Python 3.x |

## 6. 폴더 구조

```
emotion-music-recommendation/
├── README.md
├── .gitignore
├── Mysql-DB.zip            # DB 스키마 및 초기 데이터
├── 감정 음악 추천.pptx     # 발표 자료
├── flask_app/
│   └── flaskex/
│       ├── app.py
│       ├── requirements.txt
│       ├── .env.example    # 환경변수 예시 파일
│       ├── templates/      # HTML 템플릿
│       └── static/         # CSS, JS
└── images/                 # 스크린샷
```

## 7. 핵심 구현 흐름

1. 사용자가 현재 감정을 문장으로 입력
2. GPT API로 감정 카테고리 추출 (복합 감정 후보 포함)
3. 감정 기반 Spotify API 쿼리 생성
4. 최신곡 / 클래식 필터 적용 후 트랙 목록 반환
5. 추천 결과 페이지에 Spotify 플레이어 임베드
6. 사용자 피드백(좋아요 등) MySQL에 저장
7. 오늘의 감정 통계 집계 및 시각화

## 8. 보안 관련

API Key (OpenAI, Spotify), MySQL 접속 정보는 `.env` 파일로 관리합니다.  
실제 키와 비밀번호는 GitHub에 올리지 않습니다.  
`.env.example`을 참고해 로컬에서 `.env` 파일을 생성해 사용하세요.

## 9. 트러블슈팅

**Spotify API 트랙 결과 불일치**
- 문제: 동일한 감정 키워드로도 검색 결과가 매번 달라짐
- 해결: 최신곡 / 클래식 필터를 명확히 분리하고 정렬 기준 고정

**GPT 응답 형식 파싱**
- 문제: GPT 응답이 일정하지 않아 감정 카테고리 추출 실패
- 해결: 프롬프트에 JSON 형식 응답 요청 추가, 파싱 실패 시 기본값 처리

## 10. 배운 점

- 외부 API(OpenAI, Spotify) 연동과 Rate Limit 처리
- 복합 감정이라는 문제 정의에서 출발해 해결 구조를 설계하는 경험
- MySQL DB 기반 사용자 기록 저장 및 통계 집계
- 팀 프로젝트에서 역할 분담과 Flask 앱 구조 설계

## 11. 실행 방법

1. `flask_app/flaskex/requirements.txt` 패키지 설치
2. `.env.example`을 참고해 `.env` 파일 생성 (OpenAI, Spotify, MySQL 정보)
3. `Mysql-DB.zip` 내 SQL 파일로 `emotion_db` 데이터베이스 구성
4. `app.py` 실행 후 `http://127.0.0.1:5000` 접속

```bash
cd flask_app/flaskex
pip install -r requirements.txt
python app.py
```
