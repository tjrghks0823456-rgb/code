# Change Memos

## 2026-06-02

### 1. Google Takeout 분류 오류 수정
- 무엇을 수정했나: `YouTube and YouTube Music` 기본 폴더 안의 `watch-history`와 `search-history`가 음악 파일로 오분류되지 않도록 분류 순서를 조정했다.
- 왜 수정했나: 실제 Google Takeout 기본 경로에 `Music` 단어가 포함되어 정상 시청 기록이 업로드 대상에서 빠질 수 있었다.
- 확인 방법: `classify_takeout_file("Takeout/YouTube and YouTube Music/history/watch-history.json")` 결과가 `watch_history`인지 확인한다.

### 2. 짧은 노출 필터 로직 보강
- 무엇을 수정했나: 정확한 재생 시간이 없는 Takeout 기록에서 인접 기록 간 시간 차이를 이용해 짧은 노출 시간을 추정하도록 보강했다.
- 왜 수정했나: 기존 새 업로드 흐름에서는 `time_delta_sec`가 비어 있어 5초 미만 노출 필터가 실질적으로 거의 작동하지 않았다.
- 확인 방법: 5초 이내로 이어지는 연속 시청 기록 샘플을 업로드했을 때 `skipped_fake_dopamine` 값이 증가하는지 확인한다.

### 3. 누락된 HTML 파서 의존성 추가
- 무엇을 수정했나: `beautifulsoup4`를 백엔드 `requirements.txt`에 추가했다.
- 왜 수정했나: HTML Takeout 파싱에서 `BeautifulSoup`을 사용하지만 새 설치 환경에서는 의존성이 빠져 백엔드 import가 실패할 수 있었다.
- 확인 방법: 새 가상환경에서 `pip install -r requirements.txt` 후 `import bs4`가 성공하는지 확인한다.

### 4. `.env` 로딩 설정 정리
- 무엇을 수정했나: Pydantic settings가 백엔드 `.env` 파일을 읽도록 `env_file = ".env"` 설정을 추가했다.
- 왜 수정했나: 실행 환경마다 API 키와 저장소 설정이 다르게 들어가는 문제를 줄이기 위해서다.
- 확인 방법: 백엔드 루트의 `.env`에 값을 넣고 앱 import 또는 실행 시 설정값이 반영되는지 확인한다.

### 5. 업로드 화면 UI 마감 정리
- 무엇을 수정했나: 정의되지 않았던 `animate-fadeIn`, `animate-shake` CSS를 추가하고, 업로드 화면의 상태 문구와 아이콘 표현을 정리했다.
- 왜 수정했나: 화면은 컴파일되지만 없는 CSS 클래스와 이모지 중심 표기가 남아 있어 UI 완성도가 떨어졌다.
- 확인 방법: `/upload`에서 개인정보 동의 후 파일 선택 단계로 이동해 콘솔 오류 없이 버튼, 안내 카드, 애니메이션이 표시되는지 확인한다.

### 6. 민감 파일 업로드 방지 메모
- 무엇을 수정했나: GitHub 반영본의 `.gitignore`에 `.env.txt`를 추가했다.
- 왜 수정했나: `.env`는 이미 무시되지만 `.env.txt`는 무시되지 않아 API 키 파일이 실수로 커밋될 수 있었다.
- 확인 방법: `git status --ignored`에서 `.env.txt`가 추적 대상이 아닌지 확인한다.

### 7. 한국어 Google Takeout 보조 폴더 감지 보강
- 무엇을 수정했나: 프론트와 백엔드가 `댓글`, `실시간 채팅`, `재생목록`, `채널`, `구독정보` 폴더와 `.csv/.txt` 파일을 감지하고 분류하도록 확장했다.
- 왜 수정했나: 한국어 Takeout 폴더를 업로드하면 화면에는 `시청 기록`, `검색 기록` 두 파일만 반영되고 나머지 폴더가 후보/분석 대상에 들어가지 않는 문제가 있었다.
- 확인 방법: Takeout 루트 폴더를 선택했을 때 감지 결과에 시청/검색 외 보조 폴더 파일이 배지로 표시되고, 업로드 응답의 `parsed_source_counts`에 `comment`, `live_chat`, `playlist`, `subscription`, `channel` 값이 반영되는지 확인한다.

### 8. 보조 Takeout 데이터 점수 기준 반영
- 무엇을 수정했나: 실제 한국어 CSV 헤더(`채널 제목`, `댓글 텍스트`, `실시간 채팅 텍스트`, `재생목록 제목(원본)` 등)를 파싱하고, 보조 데이터 텍스트를 별도 분석 세션으로 저장하도록 했다.
- 왜 수정했나: 구독정보/재생목록/댓글/실시간채팅/채널 카운트가 0으로 표시되고, 점수 계산도 시청/검색 기록 중심으로만 돌아가 실제 사용자의 큐레이션과 참여 행동이 빠졌다.
- 확인 방법: 실제 Takeout 폴더 업로드 후 `parsed_source_counts`에 보조 카테고리가 0보다 크게 나오고, 분석 응답의 `axis_scores`가 예외 코드 없이 계산되는지 확인한다.
- 점수 기준: 구독정보/재생목록/채널은 의도적 큐레이션, 댓글/실시간채팅은 능동 참여 신호로 보고 `UAS`를 보정한다. 보조 카테고리 종류의 다양성은 `TDS`와 `VOS`에 일부 반영한다.

### 9. 하드코딩 제거 1차 계산 기반 정리
- 무엇을 수정했나: `features.py`를 추가해 현재 `norm_event` dict를 feature 구조로 변환하고, `score_config.py`로 점수 범위, 최소 데이터 기준, 축별 가중치, confidence 기준을 분리했다.
- 왜 수정했나: `scoring.py`에 있던 `search_ratio * 400.0`, `toxic_ratio * 300.0`, 고정 entropy 기준 `3.5` 같은 임의 배수/상수를 실제 비율, HHI, entropy, 가중합 기반 계산으로 바꾸기 위해서다.
- 반환 호환성: 기존 `compute_6axis_scores(events, nlp_results)`는 `{axis: float}`와 exception code list를 계속 반환한다. 새 상세 함수 `calculate_scores_v2()`와 `compute_6axis_score_details()`는 score/confidence/reason/warnings를 제공한다.
- mock/fallback 처리: NLP와 YouTube mock 응답에 `mock_used`/`fallback_used` 플래그를 추가했다. 분석 라우터는 더 이상 fake NLP 기본 카테고리를 만들지 않고, 실패 시 낮은 confidence warning으로 처리한다.
- 확인 방법: `backend`에서 `.\venv\Scripts\python.exe -m compileall app`를 실행해 문법 검사를 통과했고, 샘플 `norm_event` dict로 6축 상세 점수와 warning이 생성되는 것을 확인했다.
- 다음 단계 TODO: 프론트 dashboard 연결, `insightMock` 제거, upload parser 300개 제한 설정화, YouTube duration API 연동은 이번 1차 범위에서 제외하고 다음 단계로 남겼다.
