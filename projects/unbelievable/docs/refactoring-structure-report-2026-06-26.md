# Refactoring Structure Report - 2026-06-26

## Verdict

현재 코드는 이전보다 리팩터링이 꽤 진행된 상태다. 백엔드는 `routes -> services -> repositories/core` 흐름으로 책임이 분리되어 있고, 업로드/분석/대시보드 검증도 수동 서버 의존 없이 `TestClient` 기반으로 실행된다.

다만 완성형 리팩터링은 아니다. 가장 큰 미완성 지점은 YouTube Takeout의 체류시간 상태가 여러 계층에서 서로 다른 기준으로 표시되던 점이다. 특히 `mock_estimation=false`인 기본 업로드에서도 view 이벤트가 초기 생성 시 `is_duration_estimated=true`, `duration_source=simulated`처럼 보일 수 있었고, 이후 보정 함수가 값을 비워도 일부 플래그가 남아 점수/대시보드가 추정 체류시간으로 오해할 수 있었다.

## What Was Fixed

- `upload_service.py`
  - 초기 이벤트 생성 시 duration 필드를 `build_initial_duration_fields()`로 모았다.
  - `mock_estimation=false`이면 view 이벤트도 `estimated_duration_sec=None`, `duration_source=none`, `is_duration_estimated=false`로 시작하게 정리했다.
  - `set_duration_estimated()`를 추가해 top-level 이벤트와 `raw_item`의 duration 추정 플래그가 같이 움직이게 했다.
  - YouTube 메타데이터 및 타임라인 추정 단계에서도 mock 추정 사용 여부에 맞춰 `is_duration_estimated`가 재설정되도록 했다.

- `features.py`
  - feature layer가 `is_duration_estimated`와 `estimated_duration_sec`를 함께 읽도록 수정했다.
  - 저장 이벤트와 feature normalization 사이의 이름 불일치로 추정 경고 카운트가 다르게 잡힐 가능성을 줄였다.

- `scoring.py`
  - `direct_selection_ratio` 값이 실제로 계산된 경우에도 status가 항상 `missing`으로 표시되던 부분을 `used/missing`으로 분기했다.

- `test_takeout_quality_guards.py`
  - `mock_estimation=false`에서 추정 duration 값과 플래그가 모두 제거되는 회귀 테스트를 추가했다.

## Structure Assessment

좋은 점:

- 라우터, 서비스, 저장소, core 계산 로직이 분리되어 있어 큰 흐름은 유지보수 가능한 편이다.
- CORS 설정, 테스트 실행 방식, Takeout 품질 가드가 최근 변경으로 실사용에 더 가까워졌다.
- 데이터 품질 경고와 점수 설명이 대시보드까지 이어지는 구조가 있다.

아직 약한 점:

- `upload_service.py`가 여전히 크다. 파싱 후 이벤트 enrichment, duration enrichment, MVP limit, 저장 응답 조립까지 한 파일에 많다.
- duration 관련 필드가 `duration_confidence`, `estimated_duration_confidence`, `duration_source`, `duration_estimation_method`, `is_duration_estimated`로 흩어져 있어 재발 위험이 있다.
- 관심사 피드백 테이블은 있지만 API/UI 루프가 없어 실제 사용자 교정 기능은 아직 완성되지 않았다.
- category 분류는 advanced classifier와 local fallback이 공존하지만, 어떤 화면/지표가 어느 결과를 쓰는지 문서화가 더 필요하다.

## Validation

로컬 백엔드에서 다음 검증을 통과했다.

- `python -m py_compile app/services/upload_service.py app/core/features.py app/core/scoring.py test_takeout_quality_guards.py`
- `python test_takeout_quality_guards.py`
- `python test_pipeline.py`
- `python test_dashboard_explanations.py`

검증 중 Supabase 연결은 의도대로 MockDB fallback으로 동작했고, Java runtime 미설치로 KoNLPy Okt는 우회되었다. 이는 이번 변경의 실패가 아니라 현재 로컬 테스트 환경의 예상 동작이다.

## Recommended Next Refactor

1. `upload_service.py`에서 duration enrichment를 별도 모듈로 분리한다.
2. duration 상태를 typed object 또는 작은 dataclass 형태로 관리해 필드 불일치를 줄인다.
3. 기존 `content_classification_feedback` 테이블에 저장 API와 프론트 교정 UI를 연결한다.
4. category source별 사용 지점을 문서화하고, feedback은 전역 정답이 아니라 사용자 개인 보정으로만 적용한다.
5. 대시보드의 “정확한 진단” 느낌을 줄이고 “Takeout 기반 추정/설명 지표”라는 표현을 더 일관되게 사용한다.
