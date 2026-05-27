# 🧠 언블리버블 (SH.SON_UNBELIEVABLE)

> **디지털 콘텐츠 소비 편향 진단 및 행동 교정용 맞춤형 디톡스 포털 (MVP)**
>
> 본 프로젝트는 사용자가 인지하지 못한 채 알고리즘 추천 피드에 노출되어 발생한 미디어 소비 편향성을 시각화하고, 사전 인지 결과와의 비교 분석을 통해 메타인지 인식을 환기하며, 작은 행동 변화로 미디어 주도성을 회복하도록 돕는 웹 서비스입니다.

---

## 🌟 핵심 기능 (Core Features)

1. **무의식 노출 필터링**:
   - 무의식적 스크롤로 인한 5초 미만의 짧은 관람 데이터를 제외하여, 실제 의식적인 정보 소비 상태 중심의 정량 진단 결과를 산출합니다.

2. **메타인지 격차 (Meta-gap) 대조**:
   - 사용자가 사전 수행한 **자가진단 결과(예측)**와 실제 시청 데이터를 분석하여 도출된 **실제 데이터 분석 결과(사후)**를 6축 레이더 차트에 오버레이하여 두 지표 간의 격차(메타인지 갭)를 인지할 수 있도록 제공합니다.

3. **DSAO 16유형 캐릭터 매핑 및 도감**:
   - 분석 결과(UAS, TDS, SMS 및 롱폼 비율)를 기준으로 16가지 고유 DSAO 유형(예: `PNSF` - 알고리즘 도파민 루프, `DNML` - 한우물 연구자)을 판정하고, 재미있으면서도 학술적인 설명 카드 형태로 보여줍니다.
   - 전체 16가지 알고리즘 유형을 카드로 비교할 수 있는 **유형 성향 도감 (`/types`)**을 제공합니다.

4. **가볍고 자율적인 디톡스 루틴**:
   - 사용자에게 완료 증빙이나 차단 강제성을 부여하는 무거운 형태를 배제하고, '재생 전 질문에 응답하기', '한 줄 소감 남기기' 등 일상에서 바로 실천 가능한 저부하(Low-effort) 행동 미션을 설계하여 자율적인 참여를 권장합니다.

---

## 🔌 프론트엔드 - 백엔드 API 연결 구조 (API Architecture)

FastAPI 백엔드는 `/api/v1` prefix 라우터 환경에서 동작하며, 프론트엔드는 다음 백엔드 API 세트와 유기적으로 통신합니다.

* **업로드 및 분석 흐름**:
  1. `POST http://localhost:8000/api/v1/upload` : 시청 기록 파일 업로드 ➡️ `file_id` 획득
  2. `POST http://localhost:8000/api/v1/analysis/run?file_id={file_id}` : 정량 채점 파이프라인 가동 ➡️ `run_id` 획득
  3. `GET http://localhost:8000/api/v1/dashboard/summary?run_id={run_id}` : 6축 데이터, 메타인지 격차 및 실제 DSAO 유형 획득 ➡️ 대시보드 시각화
* **디톡스 및 미션 흐름**:
  1. `POST http://localhost:8000/api/v1/detox/generate?run_id={run_id}` : 대시보드 진입 버튼 클릭 시 Gemini 또는 Mock 플랜 설계 ➡️ `plan_id` 획득
  2. `GET http://localhost:8000/api/v1/detox/plan?plan_id={plan_id}` : 특정 plan_id의 대체 키워드 및 미션 목록 조회 (plan_id 생략 시 최신 플랜 반환)
  3. `PATCH http://localhost:8000/api/v1/detox/mission/{log_id}` : 미션 자율 수행 상태 업데이트

---

## 🛠️ 실행 및 사용 방법 (How to Run)

프로젝트 루트에 위치한 배치 파일로 프론트엔드와 백엔드를 즉시 일괄 실행하거나, 개별 쉘에서 수동 가동할 수 있습니다.

### 1. 원클릭 원격 가동 (추천)
* 프로젝트 루트의 `start_unbelievable.bat` 파일을 더블클릭합니다.
* 자동으로 Python 가상환경(`venv`) 활성화, uvicorn 포트 8000 실행, Next.js 프론트엔드 포트 3000 구동 후 브라우저가 자동 기동됩니다.

### 2. 수동 기동
* **백엔드 (FastAPI)**:
  ```bash
  cd backend
  # 가상환경 활성화 (Windows 기준)
  .\venv\Scripts\activate
  uvicorn app.main:app --reload --port 8000
  ```
* **프론트엔드 (Next.js)**:
  ```bash
  cd frontend
  npm run dev
  ```

---

## 📊 현재 MVP의 구현 상태 (Implementation Status)

현재 프로토타입은 프론트엔드 화면 구성 중심의 단계에서 나아가, 실제 로직이 매끄럽게 연결되는 **MVP(최소 기능 제품)**로 고도화되었습니다.

### ✅ 실제 구현된 것 (Live Implementation)
* **프론트-백 실제 데이터 연동**: 업로드 버튼 비활성화, 실시간 업로드 ➡️ 분석 실행 ➡️ 분석 완료 ID 수신 후 대시보드 리다이렉트 흐름이 실서버 요청 및 JSON 응답으로 구현되어 있습니다.
* **Google Takeout JSON 파싱**: 업로드된 파일이 JSON 포맷일 경우, 실제 구글 테이크아웃 YouTube `watch-history.json` 배열을 직접 파싱하여 비디오 제목(Watched 제거), 검색어(Searched for 제거), 타임스탬프를 읽어와 DB 세션에 적재합니다. (CSV/TXT의 경우 줄 단위 읽기 자동 대응)
* **결정적 6축 계산 엔진**: Shannon Entropy와 HHI 공식을 활용하여 실제 데이터셋에 비례하는 `TDS`, `SBS`, `SMS` 지표를 수학적으로 산출합니다.
* **DSAO 유형 도감 및 캐릭터 카드**: `actual_dsao` 판정 결과에 매핑되는 학술적 성향 도감 및 실시간 대조 카드 렌더링이 구현되어 있습니다.
* **자율형 미션 컴포넌트**: 완료 확인을 위해 미션 페이지 내부에서 객관식 문항(Choice)을 즉각 선택하거나 한 줄 소감(Text)을 기록하면 PATCH 요청이 전송되는 행동 유도가 동작합니다.
* **MockDB 로컬 지속성**: 로컬 MockDB의 검색 매핑 처리 및 upsert 구현을 통해 Supabase 연결 유무와 상관없이 로컬 인메모리에서 세션 조회가 가능합니다.

### ⚠️ 시연 및 Fallback용 모의(Mock) 영역
* **Gemini & NL API 키 Fallback**: 환경변수 설정 파일(`app/core/config.py`)에 구글 인증 API 키가 바인딩되지 않은 경우, 서버가 중단되는 대신 채점 지표와 최저점 카테고리를 계산하여 Gemini 및 NL 분석 응답 형식에 준하는 Mock 지침서와 미션 데이터셋을 실시간 생성하여 반환합니다.
* **시청 지속 시간 추정 (중요 한계)**:
  - Google Takeout 원천 파일에는 개별 영상의 실제 시청 지속 시간(실측 초 단위)이 포함되어 있지 않습니다.
  - YouTube Data API(`contentDetails`)를 통해 영상의 **총 재생 길이(duration)**는 보완 가능하지만, 사용자가 **실제로 몇 초 동안 시청했는지**는 YouTube 공식 API에서 제공하지 않습니다. 이 데이터는 브라우저 확장 프로그램이나 YouTube 내장 플레이어와의 연동 없이는 수집할 수 없습니다.
  - 따라서 현재 MVP에서는 롱폼(L)/숏폼(F) 분류를 위해 인덱스 분산 비율에 따른 **모의 지속 시간**을 가변 적재합니다. 이 값은 실제 시청 행동을 정확히 반영하지 않으며, 데이터 분석 경향성 파악을 위한 근사치입니다.
* **사용자 계정 통합**: 현재 MVP 로컬 테스트를 위해 user_id는 Supabase PK 규격을 맞춘 전용 테스트 UUID(`00000000-0000-0000-0000-000000000001`)로 고정하여 임시 바인딩 처리되어 있습니다.
* **localStorage 자가진단 저장**: 자가진단 결과는 브라우저의 `localStorage`에 저장됩니다. 브라우저 캐시 초기화나 다른 기기에서는 자가진단 데이터가 유지되지 않습니다.

---

## 🚀 향후 개선 예정 (Future Roadmap)

* **Supabase 실데이터 저장소 이전**: 로컬 `localStorage`에 스텁으로 저장 중인 자가진단 정보를 Supabase `profiles.survey_scores` 컬럼 테이블에 원격 Insert/Fetch하는 API 연결
* **YouTube Data API 보완적 활용**: YouTube Data API로 영상의 총 재생 길이(duration)를 수집하여 숏폼/롱폼 분류 기준을 실제 영상 길이 기반으로 개선. 단, 실제 시청 초 단위는 API로 제공되지 않으므로 별도 측정 수단 없이는 정확한 시청 지속 시간 분석에 한계가 있음
* **사용자 세션 관리**: 테스트 UUID 고정 구조에서 Supabase Auth 회원가입 및 로그인을 통한 개인별 영구 대시보드 이력 모니터링 활성화
