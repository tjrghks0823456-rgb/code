# UI Simplification Report - 2026-06-27

## Verdict

현재 UI는 기능이 부족한 문제가 아니라, 결과 화면에 너무 많은 근거·기술 설명·보조 지표가 동시에 노출되는 문제가 크다. 특히 대시보드는 첫 화면에서 사용자가 알아야 할 핵심 결론, 위험도, 다음 행동보다 세부 계산 근거와 데이터 품질 설명의 존재감이 강하다.

따라서 기능 삭제보다는 기본 화면을 줄이고, 상세 정보는 `자세히 보기`, `전문가 모드`, `근거 보기`로 접는 방식이 맞다.

## Main UX Problem

- 첫 화면에서 사용자가 바로 이해해야 할 질문은 3개다.
  - 나는 어떤 미디어 소비 유형인가?
  - 지금 조심해야 할 위험은 무엇인가?
  - 오늘 무엇을 하면 되는가?
- 현재 화면은 여기에 더해 레이더 차트, 5개 점수 카드, detailed explanations, shorts analysis, interest gap, DSAO 상세 설명, axis별 계산 근거, data reliability, technical specifications가 이어진다.
- 결과적으로 사용자는 “분석을 받았다”는 느낌보다 “보고서 전체를 해석해야 한다”는 부담을 먼저 받는다.

## Keep On Default Screen

첫 화면에 남길 항목:

1. 최종 DSAO 유형
2. 한 줄 요약
3. 핵심 위험 3개
4. 오늘의 추천 미션 1개
5. 데이터 신뢰도 배지 1개
6. 자세히 보기 버튼

이 정도면 사용자는 10초 안에 결과를 이해하고 다음 행동으로 갈 수 있다.

## Move Behind Disclosure

기본 화면에서 접을 항목:

- 레이더 차트
- 5개 축 점수 카드 전체
- detailed evidence & explanations 카드 그리드
- shorts analysis 4개 세부 점수
- interest flow / interest gap 상세표
- self survey vs actual axis 비교
- data reliability & pipeline
- technical specifications
- skipped source / ignored source 상세 목록

이 항목들은 삭제하지 말고 `상세 분석`, `근거`, `기술 정보` 탭으로 이동하는 것이 좋다.

## Remove Or Merge

줄여도 되는 항목:

- 업로드 완료 화면의 source count 7개 카드
  - 시청/검색/저장 건수 3개로 축소
  - 구독, 플레이리스트, 댓글, 실시간 채팅, 채널은 `상세 로그`로 이동
- 대시보드 상단의 5개 ScoreCard
  - 핵심 위험, 관심 다양성, 사용자 주도성 3개만 유지
  - meta gap과 detox risk는 DSAO 카드 내부 보조 문장으로 흡수
- 데이터 품질 경고 카드 여러 개
  - `분석 참고사항 3건` 같은 단일 배너로 축소
  - 클릭 시 상세 설명 표시
- DSAO 상세 설명의 strength/risk/similar/opposite 전체 노출
  - 기본은 `요약`, `강점 1개`, `주의 1개`만 표시
  - 나머지는 유형 상세 페이지로 이동

## Recommended Information Architecture

대시보드 기본 구조:

```text
[Top bar]
UNBELIEVABLE        분석 | 대시보드 | 미션

[Result Hero]
당신의 유형: PNMF 조용한 추천 루틴형
한 줄 요약: 추천 피드 중심으로 안정적인 정보 요약을 반복 소비하는 패턴입니다.

핵심 위험
[관심 쏠림 57] [주도성 낮음 23%] [체류시간 신뢰도 낮음]

오늘 할 일
[낯선 카테고리 하나 검색하기]     [미션 시작]

[분석 참고사항 3건] [자세히 보기]

------------------------------------------------
[상세 분석 탭]
요약 | 점수 | 근거 | 데이터 품질
```

업로드 화면 기본 구조:

```text
[Step 1] 동의
개인정보 안내 요약
[동의하고 계속]

[Step 2] 업로드
큰 드롭존
[Takeout ZIP 선택] [폴더 선택]
감지 결과: YouTube 시청 기록 1개, 검색 기록 1개
[분석 준비]

[Step 3] 분석 완료
분석 대상: 시청 100건 + 검색 100건
제외됨: 광고/음악 등 12건
[결과 보기]
[상세 처리 로그 보기]
```

모바일 예상도:

```text
UNBELIEVABLE

PNMF
조용한 추천 루틴형

추천 피드 중심으로 안정적인 정보 요약을 반복 소비하는 패턴입니다.

[관심 쏠림 주의]
[주도성 낮음]
[데이터 신뢰도 낮음]

오늘의 미션
낯선 카테고리 하나 검색하기
[시작하기]

상세 분석
[요약] [점수] [근거]
```

## Visual Direction

- 카드 수를 줄이고, 첫 화면은 넓은 result hero 1개와 action card 1개 중심으로 구성한다.
- 색상은 현재처럼 여러 색 점수 카드를 동시에 쓰기보다 위험도 1색, 안정/완료 1색, 일반 정보 1색으로 제한한다.
- 둥근 대형 카드가 너무 많아 화면이 무거워 보이므로, 반복 카드의 radius는 8~12px로 낮추고 hero/result 카드만 크게 둔다.
- 영어 eyebrow는 줄이고 한국어 정보 구조를 우선한다. `first glance`, `detailed evidence`, `technical specs` 같은 라벨은 시연 화면에서 혼잡도를 올린다.
- 기본 화면에서는 숫자보다 문장을 먼저 보여준다. 숫자는 상세 탭에서 확인하게 한다.

## Proposed Tabs

대시보드 상세 영역은 아래 4탭으로 정리한다.

1. `요약`
   - DSAO 유형
   - 핵심 위험 3개
   - 추천 미션

2. `점수`
   - 레이더 차트
   - 5개 축 점수
   - 자가진단 대비 차이

3. `근거`
   - 각 축 계산 근거
   - 주요 키워드
   - 관심사 흐름

4. `데이터`
   - Takeout 한계
   - duration missing/estimated 안내
   - skipped source 로그
   - technical specifications

## Priority

1. 대시보드 첫 화면을 DSAO 결과 + 핵심 위험 + 미션 CTA로 축소한다.
2. detailed explanations, data reliability, score component details를 탭/아코디언으로 이동한다.
3. 업로드 완료 화면의 통계 카드를 3개로 줄이고 나머지는 상세 로그로 접는다.
4. 네비게이션에서 `유형`은 대시보드 내부 링크 또는 하단 보조 링크로 낮춘다.
5. 한국어 문구가 깨져 보이는 환경이 있는지 인코딩/폰트 렌더링을 점검한다.

## Final Recommendation

기능은 유지하되 기본 화면의 정보량을 60% 정도 줄이는 것이 좋다. “분석 보고서 전체”를 보여주는 화면에서 “사용자가 바로 이해하고 행동하는 화면”으로 바꾸는 게 핵심이다.

가장 먼저 고칠 화면은 대시보드다. 업로드 화면은 복잡하지만 흐름이 단계형이라 아직 버틸 만하고, 대시보드는 결과를 읽는 곳이라 혼잡도가 바로 신뢰도 하락으로 이어진다.
