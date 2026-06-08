# Changelog — unbelievable

모든 주요 변경 사항을 기록합니다.  
형식: [날짜] [단계] 변경 내용

---

## [3차] 2026-06-08 — 분석 결과 설명력 강화 & 디톡스 추천 품질 고도화

### 목표
사용자가 대시보드 결과를 봤을 때 **"왜 이런 점수가 나왔는지"** 이해할 수 있도록 설명력을 추가하고, 디톡스 미션 추천을 실제 사용자 데이터 기반으로 고도화.

### 추가된 사항 (Additive)

#### Backend
- `dashboard.py`: `/dashboard/summary` 응답에 `explanations` 필드 추가
  - 6개 지표 × `{label, value, reason, evidence, caution, improvement_hint}` 구조
  - 사용자 실측 수치 인용, 데이터 품질 제약 명시
- `dashboard.py`: `actual_dsao` 구조 강화
  - `short_summary`, `strengths`, `risks`, `recommended_detox_direction`
  - `similar_types`, `opposite_type`, `confidence`, `based_on`, `scores{D/P/W/N/S/M/F/L}`
- `detox.py`: 미션 동적 매칭으로 변경
  - `why_recommended` (사용자 데이터 반영), `target_issue`, `confidence` (HIGH/MEDIUM/LOW)
- `mission_loader.py`: `recommend_missions()` — 사용자 통계 기반 점수 계산 후 상위 3개 추천
- `persona_loader.py`: `get_dsao_detail()` 신규 필드 반환

#### JSON 설정 파일
- `dsao_persona_types.v1.json`: `short_summary`, `strengths`, `risks`, `recommended_detox_direction`, `similar_types`, `opposite_type` 추가
- `detox_missions.v1.json`: `target_axes`, `triggered_by_flags`, `suitable_for_dsao`, `requires_proof`, `default_confidence` 추가

#### Bug Fixes
- `dashboard.py`: 금칙어 `"실제 시청 시간"` → `"시청 지속 시간"` 수정 (2곳)
- `category_dictionary.v1.json`: `'셀프'` 단일 인용부호 → `"셀프"` (JSON 파싱 오류 수정)

#### Frontend
- `page.tsx`: 데이터 품질 배너 → 빨간 경고 대신 청록색 "분석 참고 안내" UX
- `page.tsx`: Enriched DSAO 카드 (`strengths`, `risks`, `recommended_detox_direction`, `based_on` 표시)
- `page.tsx`: **Explanations Card Grid 신규 추가** (서브스코어 그리드 아래, 6개 지표 × 3열)

#### Tests
- `test_dashboard_explanations.py`: 시나리오 7종 전체 통과
- `test_pipeline.py`: E2E 회귀 테스트 통과

#### Docs
- `docs/dashboard-explanation-and-detox.md` 신규 작성

---

## [2차] 2026-06-08 — 하드코딩 제거 & JSON/YAML Loader 리팩토링

### 목표
코드 내부에 직접 박혀 있는 카테고리 사전, 금칙어, 점수 기준, DSAO 유형 설명, 디톡스 미션, 경고 메시지 등을 **외부 JSON 설정 파일로 분리**.

### 변경 사항

#### 신규 JSON 파일
| 파일 | 내용 |
|------|------|
| `backend/app/data/dictionaries/category_dictionary.v1.json` | 카테고리 사전 (카테고리명, 키워드, 가중치, enabled) |
| `backend/app/data/dictionaries/stop_words.v1.json` | 불용어 목록 |
| `backend/app/data/dictionaries/stimulus_words.v1.json` | 자극성 키워드 목록 |
| `backend/app/data/dictionaries/unstable_words.v1.json` | 불안정 키워드 목록 |
| `backend/app/data/dictionaries/youtube_category_map.v1.json` | YouTube 카테고리 ID 매핑 |
| `backend/app/data/rules/scoring_rules.v1.json` | 점수 기준 및 위험도 threshold |
| `backend/app/data/persona/dsao_persona_types.v1.json` | DSAO 16유형 설명 |
| `backend/app/data/missions/detox_missions.v1.json` | 디톡스 미션 목록 |
| `backend/app/data/messages/warning_messages.ko.v1.json` | 경고 메시지 한국어 텍스트 |

#### 신규 Loader 모듈
- `category_loader.py`: JSON 카테고리 사전 로더 + schema validation
- `scoring_rule_loader.py`: 점수 기준 로더
- `persona_loader.py`: DSAO 유형 설명 로더
- `mission_loader.py`: 디톡스 미션 로더
- `message_loader.py`: 경고 메시지 로더

#### 기존 파일 (Compatibility Layer 유지)
- `category_dictionary.py`: 기존 import 호환성 유지, 실제 데이터는 JSON 로더에서
- `score_config.py`: 기존 상수 호환성 유지

#### Docs
- `docs/refactoring-hardcoding.md` 신규 작성

---

## [1차] 2026-06-08 — 핵심 결함 1차 안정화

### 목표
Google Takeout 파서 안정화, duration 추정값 명시, NLP fallback 경고 표시, DSAO 용어 오표기 수정.

### 변경 사항

#### Duration 명칭 정정
- `simulated duration`, `watch duration` 등 실제 시청 시간처럼 오해되는 표현을 전면 제거
- 대체 표현: `추정 체류 시간`, `기록 기반 추정값`, `estimated dwell time`
- 계산식: `estimated_dwell_time = min(next_event_gap, video_duration * 1.5, 3600)`

#### Takeout Parser 안정화
- `takeout_parser.py`: JSON/HTML 포맷 모두 지원
- 원본 `time` 필드 보존, 타임스탬프 오류 시 fallback 처리
- `timestamp_fallback_used`, `duration_unknown`, `duration_estimated` 품질 플래그 누적

#### NLP Fallback 경고
- KoNLPy/JPype/GCP 인증 오류를 `try-except` 대신 구체적 예외 타입으로 분리
- Fallback 발생 시 `nlp_fallback_used` 플래그 + warning log 기록
- Dashboard 응답에 `data_quality_flags`, `exception_codes` 포함

#### DSAO 용어 수정
- `"16-character model"` → `"4-letter type code representing 16 possible types"`

#### Dashboard & API
- `/dashboard/summary`: `data_quality`, `data_quality_flags`, `exception_codes` 필드 추가
- Frontend 데이터 품질 배너 기반 구조 확보

---

## 프로젝트 금칙어 규정

| ❌ 사용 금지 | ✅ 올바른 표현 |
|------------|-------------|
| `실제 시청 시간` | `시청 지속 시간`, `추정 체류 시간` |
| `watch duration` | `estimated dwell time` |
| `actual duration` | `estimated dwell time` |
| `simulated duration` | `기록 기반 추정값` |
| `16-character model` | `4-letter type code representing 16 possible types` |
