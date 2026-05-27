# 🧠 언블리버블 (SH.SON_UNBELIEVABLE)

> **LLM 기반 디지털 콘텐츠 편향성 정량 진단 및 거울 치료형 디톡스 시스템**
>
> 본 프로젝트는 사용자가 인지하지 못한 채 알고리즘에 수동 노출되어 발생한 미디어 소비 편향성을 교정하기 위한 융합형 웹 애플리케이션 프로토타입입니다. 

---

## 🌟 핵심 컨셉 (Core Concept)

1. **가짜 도파민 필터링 (Fake Dopamine Filtering)**:
   - 무의식적 스크롤(세로형 숏폼 등)로 인한 5초 미만의 초단기 무의식 관람 데이터를 과감하게 제거합니다.
   - 이를 통해 정량 분석의 신뢰도를 극대화하여 진정한 정보 습득 시간 중심의 편향성을 포착합니다.

2. **메타인지 갭 (Meta-cognitive Gap) & 거울 치료**:
   - 파일 업로드 전 사용자가 직접 작성하는 **주관적 6축 진단 점수**와 실제 시청 데이터를 분석해 얻은 **객관적 6축 점수**를 동일한 레이더 차트에 오버레이합니다.
   - 인지부조화 수준을 **'착각 지수(Misconception Index)'**로 정량 수치화하여 시각적 충격을 주는 거울 치료 요법을 구현합니다.

3. **정량-생성 결합형 보완 아키텍처**:
   - **정량적 스코어링 엔진**: 통계 수식(Shannon Entropy, Herfindahl-Hirschman Index)을 적용하여 파이썬 코드가 점수와 16가지 미디어 MBTI 성향을 결정적(Deterministic)으로 산출합니다.
   - **생성형 AI (Gemini 2.5 Flash)**: 산출된 점수 데이터와 부족한 관심 키워드를 기반으로, 자연어 디톡스 행동 지침 및 대안 검색어(Reverse Query) 후보를 안전하고 실용적인 JSON 스키마 구조로 생성하는 역할에만 특화시킵니다.

---

## 📁 디렉터리 및 모듈 아키텍처 (Architecture)

프로토타입은 향후 확장 및 개별 컴포넌트 교체가 극히 용이하도록 철저하게 레이어를 나눈 클린 아키텍처(Clean Architecture) 구조로 설계되었습니다.

```text
projects/unbelievable/
├── db/
│   └── schema.sql         # Supabase PostgreSQL DDL 스키마 (RLS 정책 및 FK)
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py    # 환경 설정 및 API 키 관리 (Pydantic Settings)
│   │   │   ├── database.py  # Supabase 통신 및 오프라인 데모 세션 스텁(Stub)
│   │   │   ├── nlp.py       # Google Cloud Natural Language API 통신 및 모의 처리
│   │   │   ├── scoring.py   # 6축 지표 수학적 채점 및 16유형 분류 코어 엔진
│   │   │   ├── youtube.py   # YouTube Data API 채널 정보 탐색 및 캐싱
│   │   │   └── gemini.py    # Gemini 2.5 Flash 연동 및 구조화된 JSON 디톡스 플랜 생성
│   │   ├── routes/
│   │   │   ├── upload.py    # Google Takeout 시청 및 검색기록 파일 전처리
│   │   │   ├── analysis.py  # 자연어 파싱, 점수화 및 Supabase 테이블 적재 오케스트레이션
│   │   │   ├── detox.py     # Gemini 연동 디톡스 생성 및 진척도 체크용 라우트
│   │   │   └── dashboard.py # 메타인지 갭(자가진단 vs 실제분석) 편차 계산 라우트
│   │   └── main.py          # FastAPI 진입점 및 CORS 초기화
│   └── requirements.txt     # Python 의존성 정의
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx   # Google Fonts 연동 및 전역 그라데이션 레이아웃
    │   │   ├── page.tsx     # 다크 테마 및 유리모핑 카드 중심 웅장한 서비스 랜딩
    │   │   ├── upload/      # 동의서 서명 -> 파일 드롭 -> 사전 자가진단 3단계 위저드
    │   │   ├── dashboard/   # 5단계 위험 신호등, Recharts 레이더 오버레이, 착각지수 카드
    │   │   └── mission/     # 카피 가능한 Reverse Query, 체크리스트, 미션 진척도 바
    │   └── components/
    │       └── RadarChart.tsx # Recharts 기반 6축 메타인지 갭 가시화 컴포넌트
    ├── tailwind.config.js   # Tailwind 네온 섀도우 및 폰트 테마 설정
    ├── postcss.config.js    # PostCSS 빌드 파이프라인
    ├── tsconfig.json        # Next.js 전용 TypeScript 빌드 환경 구성
    └── package.json         # React 18, Next.js 14, Recharts 등 프론트엔드 의존성
```

---

## 📊 6대 인지 지표 및 산출 공식 (Scoring Engine)

- **주제 다양성 (TDS - Topic Diversity Score)**:
  - 수집된 영상 카테고리의 갯수를 기반으로 Shannon Entropy 수식 적용: $H = -\sum P_i \ln P_i$
  - 다양하게 볼수록 점수가 100점에 가깝게 전사됩니다.
- **출처 균형 (SBS - Source Balance Score)**:
  - 특정 채널 독점 편중성을 측정하기 위해 HHI(Herfindahl-Hirschman Index) 산출: $HHI = \sum S_i^2$
  - 독점 채널 점유율이 높을수록 감점 처리됩니다.
- **감정 균형 (EBS - Emotion Balance Score)**:
  - 구글 NL API의 감정 점수(Sentiment Magnitude & Score)의 평균치를 구합니다.
- **관점 개방성 (VOS - Viewpoint Openness Score)**:
  - 시청 채널의 미디어 포지셔닝 스코어의 분산(Variance)과 고유성 강도를 연계합니다.
- **유해/자극 안전 (SMS - Stimulus Media Safety)**:
  - 구글 NL API의 유해성 카테고리 감지 빈도 및 자극적 어휘(썸네일 유도용 낚시 단어군)의 매칭 강도를 반영하여 계산합니다.
- **사용자 주도성 (UAS - User Action Sovereignty)**:
  - 유튜브 전체 시청 행동 로그 중 수동적인 알고리즘 피드 연속 재생 대비 능동적 통합 검색(Search) 시도의 비율을 계산합니다.

### 🧬 16가지 미디어 소비 성향 유형 (Media MBTI)
6축 지표의 이진(High/Low) 조합을 바탕으로 4비트 코드를 구성하여 **16가지 고유 성향**을 판정합니다. (예: `LLLH` - 자극만을 쫓는 **도파민 추적자**)

---

## 🛠️ 로컬 설치 및 실행 가이드 (Setup Guide)

### 1. Database 설정 (Supabase)
1. Supabase 콘솔에서 새 프로젝트를 생성합니다.
2. `db/schema.sql` 내용을 복사하여 SQL Editor에 넣고 실행합니다.
3. RLS 정책 및 테이블 구조가 자동으로 활성화됩니다.

### 2. 백엔드 실행 (FastAPI)
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API 서버는 `http://localhost:8000` 에서 구동됩니다.
- 외부 API 키가 설정되지 않은 경우에도 동작하도록 지능적인 Mock Fallback 로직이 내장되어 있습니다.

### 3. 프론트엔드 실행 (Next.js)
```bash
cd frontend
npm install
npm run dev
```
- 브라우저에서 `http://localhost:3000` 에 접속하면 웅장한 다크 모드 디지털 디톡스 포털을 즉시 감상하실 수 있습니다.
- 백엔드 서버가 구동 중이지 않은 상태에서도 끊김 없는 프로토타입 시연을 위한 **하이브리드 오프라인 스텁 세션**을 지원합니다.
