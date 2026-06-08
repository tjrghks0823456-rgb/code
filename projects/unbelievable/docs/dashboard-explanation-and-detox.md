# Dashboard Explanation & Detox Enhancement

> **작업 단계**: 3차 리팩토링  
> **목표**: 분석 결과 설명력 및 디톡스 추천 품질 고도화 (Additive only)

---

## 1. 개요

이번 3차 작업은 기존 기능을 깨지 않는 **additive** 방식으로 다음을 추가했습니다:

- `/dashboard/summary` 응답에 `explanations` 필드 추가 (점수별 이유·근거·주의·개선 힌트)
- `actual_dsao` 응답 구조 강화 (short_summary, strengths, risks, recommended_detox_direction, similar_types, opposite_type, confidence, based_on)
- `/detox/generate` 응답에서 미션별 `why_recommended`, `target_issue`, `confidence` 동적 생성
- 프론트엔드 데이터 품질 배너 UX 개선 (경고 대신 참고 안내로 표시)
- 프론트엔드 Explanations Card Grid 추가
- 시나리오 테스트 7종 전체 통과

---

## 2. 백엔드 변경 사항

### 2-1. `/dashboard/summary` — `explanations` 필드 추가

**파일**: `backend/app/routes/dashboard.py`

응답 JSON에 `explanations` 키가 추가되었습니다. 구조:

```json
{
  "explanations": {
    "weighted_health_score": {
      "label": "종합 미디어 건강 점수",
      "value": "65.3점",
      "reason": "6개 핵심 미디어 소비 지표의 가중 평균값...",
      "evidence": "사용자 주도성(72.0점), 주제 다양성(58.0점)...",
      "caution": "시청 기록에 시청 지속 시간 정보가 없으므로 ...",
      "improvement_hint": "가장 점수가 낮은 영역의 미션을 실행하여..."
    },
    "cognitive_misconception_index": { ... },
    "dsao_actual_type": { ... },
    "bias_risk_score": { ... },
    "shorts_stimulation_risk": { ... },
    "data_quality_flags": { ... }
  }
}
```

**핵심 원칙**:
- `reason`: 점수가 어떻게 계산되었는지 공식 설명
- `evidence`: 실제 사용자 데이터 수치 인용 (동적 생성)
- `caution`: 데이터 품질 제약 및 추정값 여부 명시
- `improvement_hint`: 개선 가능한 구체적 행동 제안

### 2-2. `actual_dsao` 구조 강화

`actual_dsao` 필드에 다음 필드가 추가되었습니다:

| 필드 | 설명 |
|------|------|
| `code` | 4자리 DSAO 코드 (e.g. `DNML`) |
| `name` | 유형명 (e.g. `한우물 연구형`) |
| `short_summary` | 한 줄 설명 |
| `detailed_description` | 상세 설명 |
| `strengths` | 강점 리스트 |
| `risks` | 위험 요소 리스트 |
| `recommended_detox_direction` | 맞춤 디톡스 방향 |
| `similar_types` | 유사 유형 코드 리스트 |
| `opposite_type` | 대비 유형 코드 |
| `confidence` | 신뢰도 레이블 (높음/보통/낮음) |
| `based_on` | 유형 결정 근거 (동적 생성) |
| `scores` | D/P/W/N/S/M/F/L 축 점수 |

**DSAO 설명 원칙**: "4-letter type code representing 16 possible types"  
**(주의: "16-character model"이라는 표현은 사용하지 않음)**

### 2-3. `/detox/generate` — 미션 동적 매칭

**파일**: `backend/app/routes/detox.py`, `backend/app/core/mission_loader.py`

기존 정적 미션 리스트에서 **실제 사용자 지표 기반 동적 매칭**으로 변경:

- 사용자의 `actual_dsao`, 주요 카테고리, 감지된 경보(warning_codes), 데이터 품질 플래그를 기반으로 미션 점수를 계산
- 가장 높은 점수의 미션 3개를 우선 추천
- 각 미션에 `why_recommended` (사용자 데이터 기반 설명), `target_issue`, `confidence` (HIGH/MEDIUM/LOW) 포함

```json
{
  "missions": [
    {
      "mission_id": "tds_m1",
      "title": "낯선 카테고리 하나 구경하기",
      "why_recommended": "DSAO DNML 성향 분석 결과 반영, 많이 소비하신 '💻 IT/테크' 카테고리 환기, 지표상 감지된 '주제 다양성 부족' 보완을(를) 위해 이 미션이 추천되었습니다.",
      "target_issue": "관심사 편중 및 특정 주제 카테고리 과다 노출",
      "confidence": "HIGH"
    }
  ]
}
```

**매칭 로직** (`mission_loader.py`):
1. 각 미션의 `target_axes` (TDS/SBS/EBS/SMS/UAS)와 사용자 약점 지표를 비교
2. DSAO 성향 매칭: 미션의 `suitable_for_dsao` 리스트와 `actual_dsao.code` 비교
3. 활성 경보 코드(warning_codes)와 미션의 `triggered_by_flags` 비교
4. `requires_proof: true`인 미션은 기본 추천에서 제외

---

## 3. JSON 설정 파일 변경

### 3-1. `dsao_persona_types.v1.json`

**위치**: `backend/app/data/persona/dsao_persona_types.v1.json`

추가된 필드:
- `short_summary`: 한 줄 요약
- `detailed_description`: 상세 설명 (기존 `description` 대체/보완)
- `strengths`: 강점 목록 (배열)
- `risks`: 위험 요소 목록 (배열)
- `recommended_detox_direction`: 맞춤 디톡스 방향
- `similar_types`: 유사 유형 코드 목록
- `opposite_type`: 대비 유형 코드

### 3-2. `detox_missions.v1.json`

**위치**: `backend/app/data/missions/detox_missions.v1.json`

추가된 필드:
- `target_axes`: 이 미션이 보완하는 점수 축 목록 (e.g. `["TDS", "VOS"]`)
- `triggered_by_flags`: 이 미션을 활성화하는 경보 코드 목록
- `suitable_for_dsao`: 이 미션이 잘 맞는 DSAO 유형 목록
- `requires_proof`: 증명이 필요한 미션 여부 (기본 추천 제외)
- `default_confidence`: 기본 신뢰도 레이블

### 3-3. `category_dictionary.v1.json` (버그 수정)

**위치**: `backend/app/data/dictionaries/category_dictionary.v1.json`

- `취미/일상` 카테고리 키워드 배열 내 `'셀프'` (단일 인용부호) → `"셀프"` (이중 인용부호) 수정
- JSON 파싱 오류 해결로 카테고리 사전이 정상 로드됨

---

## 4. Loader 변경 사항

### `persona_loader.py`

- `get_dsao_detail()` 함수: 신규 필드(`short_summary`, `strengths`, `risks`, `recommended_detox_direction`, `similar_types`, `opposite_type`) 반환 포함

### `mission_loader.py`

- `recommend_missions(user_stats, count=3)`: 사용자 통계를 받아 동적으로 미션 점수를 계산하고 상위 N개 반환
- `generate_mock_plan_data()`: mock 테스트용 플랜 생성

---

## 5. 프론트엔드 변경 사항

**파일**: `frontend/src/app/dashboard/page.tsx`

### 5-1. 데이터 품질 배너 UX 개선

- 기존: 빨간 경고 배너 → **변경**: 청록색 "분석 참고 안내" 배너
- 카드 그리드 형태로 여러 품질 이슈를 한 번에 표시
- `isConfidenceLow: true`인 항목에만 "참고용 (낮은 신뢰도)" 뱃지 표시

### 5-2. Enriched DSAO 카드 렌더링

- `actual_dsao.short_summary`, `detailed_description`, `strengths`, `risks`, `recommended_detox_direction` 표시
- `based_on` (분석 근거), `confidence` (신뢰도), `similar_types`, `opposite_type` 표시

### 5-3. Explanations Card Grid (신규)

- 서브스코어 카드 그리드 바로 아래에 삽입
- `processedData.explanations`가 있을 때만 렌더링 (additive, 하위 호환)
- 6개 지표 카드를 3열 그리드로 배치
- 각 카드: `label`, `value` (뱃지), `reason`, `evidence`, `caution`, `improvement_hint`

---

## 6. 금칙어 규정

이 시스템에서 **절대 사용해서는 안 되는 표현**:

| ❌ 금칙어 | ✅ 대체 표현 |
|-----------|-------------|
| `실제 시청 시간` | `시청 지속 시간`, `추정 체류 시간` |
| `watch duration` | `estimated dwell time`, `estimated exposure time` |
| `actual duration` | `estimated dwell time` |
| `simulated duration` | `기록 기반 추정값`, `estimated` |
| `16-character model` | `4-letter type code representing 16 possible types` |

---

## 7. 테스트 결과

### 시나리오 테스트 (`test_dashboard_explanations.py`)

7개 시나리오 **전체 통과**:

| 시나리오 | 설명 | 결과 |
|---------|------|------|
| `1_shorts_focused` | 숏츠 집중 소비 유저 | ✅ PASS |
| `2_politics_biased` | 정치/뉴스 편향 유저 | ✅ PASS |
| `3_sports_hobby` | 스포츠/취미 다양 유저 | ✅ PASS |
| `4_diverse_searches` | 검색 다양성 높은 유저 | ✅ PASS |
| `5_timestamp_fallback` | 타임스탬프 오류 유저 | ✅ PASS |
| `6_duration_unknown` | 단일 기록 유저 | ✅ PASS |
| `7_nlp_fallback` | NLP fallback 유저 | ✅ PASS |

**검증 항목**:
- `actual_dsao` 필드 전체 구조 (code, name, short_summary, strengths, risks, opposite_type, based_on, confidence, scores)
- `explanations` 6개 키 전체 존재 및 빈 값 없음 (label, value, reason, evidence, caution, improvement_hint)
- 금칙어 부재: `실제 시청 시간`, `watch duration`, `actual duration`
- 미션 `why_recommended` 비어있지 않음
- 미션 `confidence` ∈ {HIGH, MEDIUM, LOW}
- 미션 `target_issue` 비어있지 않음

### E2E 테스트 (`test_pipeline.py`)

기존 E2E 파이프라인 회귀 테스트 — 결과는 실행 후 확인.

---

## 8. 향후 개선 과제 (TODO)

- [ ] `why_recommended` 문장 품질 고도화: 현재 템플릿 기반 → LLM 생성 전환 검토
- [ ] `explanations` 필드 언어 다국어화 (현재 한국어 고정)
- [ ] 미션 `requires_proof` 항목의 선택적 활성화 UI (사용자 레벨 설정)
- [ ] DSAO `confidence`가 `낮음`일 때 추가 데이터 수집 유도 UX 흐름
- [ ] 프론트엔드 Explanations 카드 접기/펼치기 (accordion) 지원
