# unbelievable-digital-wellbeing

> Python · FastAPI · Next.js 기반 YouTube 시청 기록 분석 및 디지털 디톡스 추천 서비스

## 1. 프로젝트 개요

사용자가 YouTube Takeout으로 내려받은 시청 기록 데이터를 업로드하면, 미디어 소비 편향성을 6가지 지표로 분석하고 가벼운 디지털 디톡스 미션을 추천하는 웹 서비스입니다.

알고리즘 추천 피드에 반복적으로 노출되면서 사용자가 인지하지 못한 채 형성된 시청 편향을 수치로 보여주고, 자가진단 결과와 실제 데이터 분석 결과를 비교해 메타인지 격차를 시각화합니다.

팀 프로젝트로 진행했으며, FastAPI 백엔드와 Next.js 프론트엔드로 구성된 풀스택 MVP입니다.

## 2. 개발 배경

알고리즘 추천 피드의 편향성 문제에서 출발했습니다. 사용자가 실제로 어떤 콘텐츠를 얼마나 소비하는지 데이터로 보여주고, 스스로 인식한 소비 패턴과 얼마나 다른지 비교하는 서비스가 필요하다고 판단했습니다. 무거운 제한이나 강제보다 가볍고 자율적인 방식으로 행동 변화를 유도하는 것을 목표로 했습니다.

## 3. 주요 기능

**분석 파이프라인**
- Google Takeout JSON/HTML 다중 파싱 (watch-history.json, HTML 형식 모두 지원)
- 5초 미만 짧은 관람 데이터 제외 (무의식 스크롤 필터링)
- Shannon Entropy / HHI 공식 기반 6축 편향 지표 산출
- 데이터 부족 상황 점수 보정 (available: false 처리)

**DSAO 유형 분석**
- 시청 기록 기반 16가지 DSAO 유형 분류 (성격 판단이 아닌 소비 경향 시각화)
- 전체 유형 비교 도감 페이지 제공

**메타인지 격차 시각화**
- 자가진단 예측값 vs 실제 데이터 분석값 6축 레이더 차트 오버레이

**디톡스 루틴 추천**
- 강제성 없는 저부하 행동 미션 설계
- 미션 완료 상태 업데이트 API

**데이터 품질 경고**
- 시청 지속 시간 추정 시 경고 배너 출력 (P10_DURATION_ESTIMATED 등)

## 4. 시스템 구조

```
[Next.js 프론트엔드 :3000]
      ↕ HTTP (REST API)
[FastAPI 백엔드 :8000]
      ↕
[SQLite DB]
```

**API 흐름:**
1. `POST /api/v1/upload/takeout` → file_id 획득
2. `POST /api/v1/analysis/run?file_id={id}` → run_id 획득
3. `GET /api/v1/dashboard/summary?run_id={id}` → 6축 데이터, DSAO 유형
4. `POST /api/v1/detox/generate?run_id={id}` → 디톡스 플랜 생성

## 5. 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python, TypeScript |
| Frontend | Next.js, React, TailwindCSS |
| Backend | FastAPI (Python) |
| Database | SQLite |
| 분석 | Shannon Entropy, HHI, BeautifulSoup4 |
| 개발 환경 | Python 3.x, Node.js |

## 6. 폴더 구조

```
unbelievable/
├── README.md
├── CHANGELOG.md
├── start_unbelievable.bat     # 원클릭 실행 배치 파일
├── backend/
│   ├── app/                   # FastAPI 라우터 및 비즈니스 로직
│   ├── requirements.txt
│   └── test_*.py              # 분석 파이프라인 테스트
├── frontend/
│   ├── src/                   # Next.js 페이지 및 컴포넌트
│   ├── .env.local.example
│   └── package.json
├── db/
│   └── schema.sql
└── docs/
    ├── dashboard-explanation-and-detox.md
    └── interest-classification-roadmap.md
```

## 7. 핵심 구현 흐름

1. 사용자가 YouTube Takeout 파일을 업로드
2. JSON 또는 HTML 형식을 자동 감지하여 파싱
3. 5초 미만 짧은 시청 데이터 제외
4. 연속 시청 간 시간 간격으로 체류 시간 추정 (duration_source: simulated)
5. Shannon Entropy/HHI로 6축 편향 지표 계산
6. 지표 기반 DSAO 유형 16개 중 1개 판정
7. 자가진단 결과와 레이더 차트로 비교 시각화
8. 디톡스 미션 플랜 생성

## 8. MVP의 한계 및 솔직한 기술

- 자가진단 8축 중 EBS, SBS는 직접 대응하는 지표가 없어 MVP 기본값 50점 적용
- Google Takeout에 실제 시청 지속 시간이 포함되지 않아 시간 간격으로 추정
- Supabase 연동은 계획 단계이며 현재는 로컬 SQLite 사용

## 9. 트러블슈팅

**Google Takeout 형식 이중 처리**
- 문제: JSON과 HTML 두 가지 형식이 존재
- 해결: 파일 확장자 감지 후 각각 파서 분기, BeautifulSoup4 lazy import

**데이터 부족 축 처리**
- 문제: 채널명이 전부 Unknown인 경우 SBS 지표 계산 불가
- 해결: `available: false` 처리 후 해당 축을 가중 평균에서 제외

## 10. 배운 점

- FastAPI와 Next.js를 연동하는 풀스택 API 설계 흐름
- 실제 데이터(YouTube Takeout)의 품질 문제를 코드로 처리하는 방법
- Shannon Entropy를 활용한 다양성 지표 수치화
- 팀 프로젝트에서 CHANGELOG와 문서화의 중요성

## 11. 실행 방법

**원클릭 실행 (Windows)**
```
start_unbelievable.bat 더블클릭
```

**수동 실행**
```bash
# 백엔드
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 프론트엔드
cd frontend
npm run dev
```

> 환경 변수: `frontend/.env.local.example`을 참고해 `.env.local` 파일 생성
