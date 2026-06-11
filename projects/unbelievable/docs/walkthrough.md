# YouTube 시청 기록 분석 파이프라인 및 대시보드 개선 Walkthrough

## 최종 완료 상태

> **작업 단계**: YouTube Takeout 시청 기록 추정 판별 및 대시보드 UI/UX 가독성 간소화 (탭/아코디언 개편) 완료  
> **대상 모듈**: 
> - 백엔드 분석 서비스 ([scoring.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/core/scoring.py), [features.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/core/features.py), [upload_service.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/services/upload_service.py), [dashboard_service.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/services/dashboard_service.py))
> - 프론트엔드 대시보드 ([page.tsx](file:///c:/Users/son/Documents/한이음/projects/unbelievable/frontend/src/app/dashboard/page.tsx), [globals.css](file:///c:/Users/son/Documents/한이음/projects/unbelievable/frontend/src/app/globals.css))  
> **모든 테스트 통과 확인**: ✅ 시나리오 7종 (`test_dashboard_explanations.py`) + ✅ E2E Pipeline (`test_pipeline.py`)  
> **Next.js 프로덕션 빌드**: ✅ `npm run build` 100% 컴파일 및 정적 웹 빌드 완료  

---

## 완료된 작업 목록

### ✅ 1. 백엔드 데이터 품질 요약 API 및 성향 평가 보정 고도화

Google Takeout 원본 데이터의 숏츠/일반 영상 판별 완화 로직이 제대로 작동하고 있는지 프론트엔드에서 상시 모니터링하고, 미분류/시간대 왜곡 문제를 방어하기 위해 다음과 같이 고도화했습니다.

*   **TDS 카테고리 미분류 신뢰도 패널티 적용**:
    *   **파일**: [scoring.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/core/scoring.py)
    *   **로직**: NLP 또는 로컬 형태소 분류 결과에서 "기타/미분류" 비중이 70% 이상일 때 대시보드 경고 문구를 포함하고, 80% 이상으로 극단적으로 치우치면 `TDS` (주제 다양성) 지표의 `confidence`를 `0.0`으로 패널티 강하합니다. 또한 `tds_confidence`와 `topic_diversity_confidence` 필드를 세분화하여 API 상세 구조에 함께 추가했습니다.
*   **체류 시간 비정상 Timeline Gap 보정 (Capping)**:
    *   **파일**: [upload_service.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/services/upload_service.py)
    *   **로직**: `apply_timeline_duration_estimates`에서 실제 metadata duration이 없는 경우 30분을 초과하는 간격은 자리 비움(`idle_capped`)으로 간주하여 `DEFAULT_ESTIMATED_WATCH_SEC = 600` (10분)으로 Capping하고, 30분 이내는 기존대로 gap 기반으로 추정하되 `MAX_ESTIMATED_WATCH_SEC_WITHOUT_METADATA = 1800` (30분)의 상한선을 강제 적용합니다.
    *   각 이벤트별로 어떤 방식(`metadata` | `timeline_gap` | `idle_capped` | `default_estimate` | `unknown`)으로 체류 시간이 계산되었는지를 나타내는 `duration_estimation_method`를 dynamic하게 마킹하고 이를 데이터베이스 `raw_item` JSONB 컬럼에 보존합니다.
*   **다국어 타임스탬프 오류 및 품질 플래그 연동**:
    *   **파일**: [upload_service.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/services/upload_service.py) 및 [features.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/core/features.py)
    *   타임스탬프 분석 오류 발생 시, API `data_quality_flags`에 `"timestamp_fallback_used"`가 안정적으로 연동될 수 있도록 flag 핸들링을 보완하였습니다.
    *   `features.py`에서 `estimated_duration_sec` 변수 정의 충돌로 인한 분석 실행(500) 버그를 `estimated_duration`으로 올바르게 수정 완료했습니다.
*   **디버깅 메타데이터 및 품질 요약 API 통합**:
    *   **파일**: [dashboard_service.py](file:///c:/Users/son/Documents/한이음/projects/unbelievable/backend/app/services/dashboard_service.py)
    *   **로직**: `get_dashboard_summary`에서 전체 파싱 실패율, 미분류율(기타/미분류 비율), Capped 수량 등을 종합 집계해 `data_quality_summary` 및 `analysis_debug` 구조체를 반환하며, `category_missing_ratio >= 0.8`인 경우 `TDS` 지표에 `P17_CATEGORY_MISSING_EXCESSIVE` 경고 코드를 추가하고 종합 신뢰도를 낮추는 로직을 추가했습니다.

### ✅ 2. 프론트엔드 대시보드 품질 안내 배너 보강

디버깅 메타데이터 및 Capping 정보를 연동하여 대시보드 상단에 데이터 품질 수준에 맞춘 친절한 설명 배너를 노출하도록 개선했습니다.

*   **파일**: [page.tsx](file:///c:/Users/son/Documents/한이음/projects/unbelievable/frontend/src/app/dashboard/page.tsx)
*   **배너 노출 조건 및 문구**:
    *   **카테고리 미분류 쏠림 (70% 이상)**:
        *   *"일부 콘텐츠의 카테고리 정보가 부족하여 로컬 키워드 기반으로 추정했습니다. ‘기타/미분류’ 비율이 높을 경우 주제 다양성 점수는 참고용으로 해석해야 합니다."* 배너 추가.
    *   **타임스탬프 파싱 실패율 (20% 이상)**:
        *   *"일부 날짜 형식을 해석하지 못해 시간대별 분석 정확도가 낮아질 수 있습니다."* 배너 추가.
    *   **체류 시간 긴 공백 보정(Idle Capping)이 작동한 경우**:
        *   *"긴 공백 시간은 자리 비움 가능성으로 보고 체류 시간 계산에서 보정했습니다."* 배너 추가.

---

## 검증 결과 요약

### 1. 백엔드 E2E 및 시나리오 테스트
*   **결과**: `=== ALL TESTS PASSED SUCCESSFULLY ===` 및 `=== ALL SCENARIOS VERIFIED SUCCESSFULLY! ===`
*   **테스트 커맨드**:
    ```powershell
    venv\Scripts\python.exe test_pipeline.py
    venv\Scripts\python.exe test_dashboard_explanations.py
    ```
*   **비고**: 추가된 디버깅용 API 키가 기존 E2E 테스트 및 7대 가상 시나리오의 API 응답 스키마 호환성을 전혀 깨뜨리지 않고 성공적으로 작동함을 증명했습니다.

### 2. Next.js 프론트엔드 프로덕션 빌드
*   **결과**: `next build` 컴파일 및 정적 페이지 생성 (9/9) 100% 성공
*   **테스트 커맨드**:
    ```powershell
    $env:PATH = "C:\Users\son\.unbelievable_launcher\node\node-v20.11.1-win-x64;" + $env:PATH
    npm run build
    ```
*   **비고**: `data_quality_summary` 와 관련된 분기 및 바인딩 코드가 Next.js의 타입 안전성 및 컴파일 최적화 빌드를 에러 없이 통과했습니다.

### ✅ 3. 대시보드 UI/UX 레이아웃 간소화 및 가독성 개선 (클릭으로 보는 상세 정보)

페이지 로딩 속도 및 사용자의 시각적 인지 부하를 줄이기 위해, 화면의 난잡한 요소를 숨기고 필요할 때 클릭하여 전개하는 인터랙티브 아키텍처로 개편했습니다.

*   **관심사 마인드맵 3종의 탭(Tabs) 전환 방식 적용**:
    *   기존: 430px 높이의 네트워크 그래프 3종(검색 기반, 일반 시청, 숏츠 반복)이 세로로 줄줄이 렌더링되어 스크롤 압박이 매우 심함.
    *   개선: `activeMapTab` 상태를 연동한 **[🔍 직접 검색 맵] | [📺 일반 시청 맵] | [🔥 숏츠 반복 맵]** 프리미엄 탭 스위처를 제공하여, 사용자가 원하는 맵 하나만 띄워 집중해서 볼 수 있도록 간소화했습니다.
*   **6대 핵심 점수 상세 가이드의 아코디언 카드 전환**:
    *   기존: 6개 지표의 측정 근거, 주의 사항, 개선 행동 등의 상세 텍스트가 그리드 안에 전체 노출되어 텍스트 과부하를 일으킴.
    *   개선: 카드를 클릭할 때만 하단 상세 내용이 `transition-max-height` CSS 애니메이션을 타고 부드럽게 아래로 펼쳐지는 **원터치 아코디언 리스트**로 개편하여 카드 영역을 깔끔하게 유지했습니다.
*   **자가진단 vs 실제 기록 비교 영역의 아코디언 전환**:
    *   기존: 상세 설명, 주요 강점, 위험 요소, 맞춤 디톡스 추천 정보 등 엄청난 텍스트 양이 비교 영역의 절반 이상을 차지함.
    *   개선: `showDsaoDetails` 상태를 도입하여 기본형 캐릭터 이름과 핵심 요약만 표시하고, 상세한 설명과 강점/리스크 리스트는 **[상세 분석 보기 ▼]** 버튼 클릭 시 부드럽게 서랍이 열리도록 디자인했습니다.
*   **숏츠 자극 소비 루프 섹션의 서랍식 아코디언 전환**:
    *   기존: 5가지 상세 지표 카드, 반복 키워드, 시간대별 숏츠 분석 및 warnings 리스트가 한 번에 다 보여 무겁고 거대함.
    *   개선: `showShortsDetails` 상태를 연동하여 평상시에는 숏츠 건수와 위험도만 보여주고, 복잡한 하위 요약 지표 및 세부 차트 영역은 **[상세 분석 보기 ▼]** 버튼으로 토글하도록 축소했습니다.
*   **AI 해석 요약 상세 분석의 아코디언 전환**:
    *   기존: AI가 생성한 핵심 해석 문단 아래에 검색 의도, 일반 노출, 숏츠 데이터 분석 등의 3개 요약 카드가 항상 세로로 나열됨.
    *   개선: `showAiSummaryDetails` 상태를 통해 핵심 요약문만 깔끔히 남기고, 3개 상세 정보 컬럼 및 맞춤 힌트는 **[상세 정보 보기 ▼]** 버튼을 통해 유동적으로 나타나도록 개선했습니다.
*   **품질 알림 가이드 배너의 서랍식 축소**:
    *   기존: 데이터 결손, 분석 한계 등을 안내하는 노란색 품질 배너가 화면에 대량 노출되어 초기 시선을 분산시킴.
    *   개선: 배너 리스트를 **"💡 미디어 분석 데이터 품질 안내 (총 N건)"** 1줄 요약과 함께 우측에 **[자세히 보기 ▼]** 아코디언 버튼을 추가하여 필요시에만 펼쳐볼 수 있게 서랍식으로 축소했습니다.
*   **기술 명세 및 신뢰도 분석 섹션의 아코디언 통합**:
    *   기존: 페이지 하단에 배치된 약 150줄 분량의 샘플링 기술 정보 및 심사위원용 로직 설명이 페이지 스크롤을 끝없이 늘림.
    *   개선: **"분석 신뢰도 및 데이터 품질"** 영역 하단에 `showTechnicalSpecs` 상태를 탑재하여 일반 사용자는 요약본만 보게 하고, 평가자는 **[상세 명세 펼치기 ▼]** 버튼으로 정밀한 결손 보정 정책과 한계 대응 명세를 열어볼 수 있도록 정리했습니다.

---

## 남아있는 한계점 (Limitation)
*   **정보의 불확실성**: YouTube Takeout 데이터 자체에는 동영상의 상세 길이, 정교한 카테고리 정보 등이 존재하지 않는 경우가 많기 때문에, 이번 분석 로직 완화 역시 **"기록 간의 시차"** 및 **"비디오 타이틀 단어 힌트"**에 절대적으로 의존하는 **추정값**입니다.
*   **신뢰성 제약**: 따라서 정확도가 100%가 아닐 수 있음을 사용자에게 경고 배너로 친절히 명시하여 투명성을 확보했습니다.
