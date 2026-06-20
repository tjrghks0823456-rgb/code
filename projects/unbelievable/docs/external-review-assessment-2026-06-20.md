# 외부 코드 평가 검토 (2026-06-20)

## 결론

외부 평가는 전체적으로 70~80% 정도 타당하다. 특히 이 프로젝트를 정확한 심리/AI 진단기가 아니라, YouTube Takeout에서 관찰 가능한 소비 패턴을 설명하는 휴리스틱 MVP로 규정한 점은 정확하다.

## 동의하는 지적

- 정답 라벨 데이터셋과 사용자 교정 루프가 없어 분류 정확도를 실증했다고 말하기 어렵다.
- 감정 균형(EBS), 관점 개방성(VOS), 사용자 주도성(UAS)은 직접 측정값보다 제목, 키워드, 검색 및 집중도 기반 대리지표에 가깝다.
- 범용 사용자 피드백 저장/적용 API와 UI는 아직 없다.
- `mock_estimation=False`에서도 view 이벤트를 처음 만들 때 `is_duration_estimated=True`, `duration_source="simulated"`로 설정한다. 이후 추정 함수가 duration 값과 source를 `None`/`none`으로 바꾸지만 `is_duration_estimated`를 False로 되돌리지 않아 대시보드가 추정 사용으로 판단할 수 있다. 이 불일치는 우선 수정 대상이다.

## 보정이 필요한 지적

- 피드백 DB 구조가 전혀 없는 것은 아니다. `content_classification_feedback` 테이블, RLS 정책, DB 컬럼 허용 목록은 이미 존재한다. 다만 이를 호출하는 라우터, 서비스, 프론트 UI가 없어 실제 기능으로 완성되지 않은 상태다.
- 카테고리 분류가 전부 첫 키워드 일치 방식인 것은 아니다. `category_classifier.py`에는 복수 신호 점수화, 후보 3개, confidence 계산이 구현되어 있다. 하지만 `local_category_screening.py`의 첫 일치 방식도 보조 분포 계산에 사용되므로 개선 필요성은 남아 있다.
- UAS의 `direct_selection_ratio`가 완전히 미구현인 것은 아니다. 알려진 `source_surface`가 있을 때 계산한다. 다만 Takeout에서 추천 피드 클릭 여부를 안정적으로 알기 어려워 대부분 제한된 대리지표라는 비판은 맞다.
- 제안된 범용 `analysis_feedback` 테이블을 바로 추가하기보다, 이미 존재하는 `content_classification_feedback` 경로를 먼저 완성하는 편이 범위와 데이터 책임이 명확하다.

## 권장 우선순위

1. duration 플래그와 실제 값의 불일치 수정 및 회귀 테스트 추가.
2. 기존 `content_classification_feedback`에 대한 저장 API와 카테고리 교정 UI 연결.
3. 교정 전/후 결과를 저장만 하고 즉시 전역 모델 정답으로 사용하지 않는 개인 범위 정책 적용.
4. 라벨링된 검증 데이터셋으로 카테고리 precision/recall과 오분류 사례 측정.
5. EBS/VOS/UAS 표시명을 직접 측정처럼 보이지 않는 표현으로 조정.

## 최종 판단

현재 구현은 기능적으로는 좋은 MVP지만 정확도 측면에서는 검증된 AI 진단 서비스가 아니다. 외부 평가의 점수는 다소 거칠지만 위험 지점의 방향은 맞다. 가장 중요한 발견은 duration 불일치이며, 피드백 기능은 새 범용 구조를 만들기 전에 이미 준비된 카테고리 피드백 스키마를 실제 API/UI로 완성하는 것이 좋다.
