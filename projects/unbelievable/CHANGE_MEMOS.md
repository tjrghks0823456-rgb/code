# Change Memos

## 2026-06-04 Interest gap report and dashboard UI note
- Updated `build_interest_gap_report()` to return `summary`, `search_vs_watch_gap`, `recommendation_flow_candidate_categories`, `intent_matched_categories`, and warnings while keeping the old `algorithm_drift_categories` key only as a compatibility alias.
- Recalculated `interest_mismatch_score` from category-ratio L1 distance: standard-video search gap is primary, shorts gap is a 0.3 weighted helper only when shorts data exists.
- Recommendation-flow candidates now use cautious language: they mean topics that appear more in non-search viewing than direct search, not a confirmed recommendation path.
- Updated Gemini/rule-based explanations and dashboard copy to avoid the banned visible phrases such as “알고리즘이 많이 보여준 관심사”.
- Dashboard now shows `관심사 비교 리포트` with TOP 3 cards for direct search, standard-video viewing, and shorts repetition, plus expandable map details with subcategories, entities, raw evidence, and confidence.

## 2026-06-04 Data cleanup phase 2 note
- Added explicit helpers in `content_filters.py`: `is_google_ad_event()`, `extract_search_query()`, and `detect_content_format()`.
- Ad filtering now requires stronger evidence such as Google Ads details, ad/tracking URLs, `gclid`, `dclid`, `utm_campaign`, `utm_medium=cpc`, `Shortened:`, or campaign-style creative codes. Brand names such as `Google Cloud`, `Hotels.com`, and `Sony` are not treated as ads by name alone.
- Search history parsing now stores a `search_query` only when the query is explicit through `Searched for ...`, `You searched for ...`, Korean `검색어:`/`검색:` patterns, or query-like fields. Ambiguous landing-page titles are skipped unless they are counted as excluded ad events.
- Content format detection now keeps `/shorts/` as `shorts`, normal `youtube.com/watch?v=` URLs as `standard_video`, clear live evidence as `live`, and unclear surfaces as `unknown`.
- Takeout records with no confirmed watch time keep `time_delta_sec=None`; timeline/default fallbacks are stored only as `estimated_duration_sec` with `duration_confidence`.
- Verification: backend `compileall` passed, and manual checks confirmed brand-only titles are not ads, ad URLs/details are excluded, search extraction works, and shorts/standard video separation works.

## 2026-06-03 Dashboard interest maps API note
- Expanded `build_search_interest_map`, `build_standard_video_interest_map`, and `build_shorts_interest_map` response details without removing existing fields.
- Category distribution now exposes percent `ratio`, legacy-friendly `value`, internal `ratio_fraction`, and subcategory metadata including `entities`, `raw_items`, `confidence`, `matched_keywords`, `source_groups`, and `secondary_tags`.
- Search, standard-video, and shorts maps still use separate inclusion filters so view events cannot enter search maps, shorts cannot enter standard-video maps, and standard videos cannot enter shorts maps.
- Shorts maps now include `repeat_topic_score` and a warning that shorts maps represent short-form repeated exposure patterns, not direct search intent.
- Dashboard `data_coverage.parsed_source_counts` now always includes `search_history`, `standard_video`, `shorts`, `live`, and `unknown` defaults to avoid undefined frontend reads.

## 2026-06-03 Interest classifier detail engine note
- Expanded `classify_interest_topic(text, raw_category="", channel_name="")` so it can return category, subcategory, confidence, entities, matched keywords, raw text, raw category, source group, and secondary tags.
- Kept existing dashboard/API wiring unchanged for this step; the richer helper output is available for the next API response integration stage.
- Added entity-aware mappings for examples such as `류현진 인터뷰 -> 스포츠/야구`, `이강인 -> 스포츠/축구`, and `FC모바일 -> 게임/모바일게임` with secondary `스포츠/축구` tags.
- Added politics/social source grouping without political-leaning judgment: `매불쇼`, `가로세로연구소`, `MBC 뉴스`, and `TV조선` are classified as political/social content consumption sources only.
- Added raw NLP category fallback mapping such as `Computers & Electronics -> IT/테크`, while ambiguous `People & Society` stays low-confidence unless text/channel evidence clarifies it.

## 2026-06-03 One-link sharing note
- Changed frontend API calls to use same-origin `/api` by default instead of browser-side `http://localhost:8000`, so shared visitors do not call their own localhost.
- Added a Next.js rewrite that proxies `/api/:path*` to `BACKEND_ORIGIN` or `http://127.0.0.1:8000`, allowing the frontend and backend to work behind one public frontend URL.
- Updated `dev-server.js` to allow host binding through `HOST` while keeping `127.0.0.1` as the default.
- Added `share_unbelievable.ps1` and `share_unbelievable.bat`; if `cloudflared` is installed, running the BAT starts local services and prints a public `trycloudflare.com` URL to share.
- For a permanent website, this still needs real hosting and persistent storage; the tunnel script is best for temporary demos while this PC is on.

## 2026-06-03 Gemini interest explanation note
- Added `GeminiClient.enrich_interest_report()` as an optional explanation layer for already-computed interest maps. It does not change scores, categories, or ad filtering decisions.
- If `GEMINI_API_KEY` is configured, the dashboard can receive a concise Gemini-generated Korean interpretation under `insights.interest_ai_summary`.
- If no real key is configured, the same field is filled by deterministic rule-based fallback text, so local demos remain stable.
- Added `GEMINI_MODEL` configuration with `gemini-2.5-flash` as the default model name.
- Dashboard UI now shows an `AI 해석 요약` block inside the interest comparison card and labels whether it came from Gemini or the rule-based fallback.

## 2026-06-03 Live Takeout verification note
- Restarted the backend/frontend so the latest ad-safe interest-map code was actually running on ports 8000/3000.
- Re-uploaded `takeout-20260601T113511Z-3-001.zip` through the running API and verified `total_parsed=3209`, `total_saved=2113`, and `excluded_ad_count=1014`.
- Dashboard summary for run `41545d26-27f4-4b76-9619-ae1dcd436fbc` now reports `search_interest_map.total_search_count=60`, `excluded_ad_count=1014`, and an `interest_gap_report.interest_mismatch_score=5.4`.
- The previous visible ad examples, including `Get Started on Google Cloud_KR_R1`, `[Sony Audio]`, `Hotels.com (KR)`, `The Android Show`, `Shortened: cid=...`, and `6s ver.2` creative titles, appear in `ad_skip_summary` instead of the search-interest list.

## 2026-06-03 Interest map category gap note
- Added `backend/app/core/interest_maps.py` so ad-safe search, standard-video, and shorts events each build separate rule-based interest maps with major/minor categories.
- Search interest maps now call the shared ad filter and `is_valid_search_event()` before extracting queries, so campaign titles and watch-history titles cannot become direct search interests.
- Dashboard summary now returns `search_interest_map`, `standard_video_interest_map`, `shorts_interest_map`, `interest_gap_report`, and richer `data_coverage` while preserving existing response fields.
- Source-balance scoring now prefers `channel_url`, then `channel_name`, then `author_id`, then `source_surface`, and counts only standard video watch events for the channel distribution.
- Dashboard UI now shows a compact comparison card for active search, standard video, shorts, and the interest mismatch score.

## 2026-06-03 Ad filtering hardening note
- Rebuilt the shared ad filter around Google Ads details, ad/tracking URL markers, and campaign-creative title patterns such as `_KR_R1`, `6s`, `ver.2`, `1080x1920`, and Korean creative labels like `가로형`.
- Search interest maps now use only valid `search_history`/`active_search` events after search-query cleanup, so watch history, shorts, subscriptions, playlists, comments, and detected ad/promotional events cannot appear as direct search interests.
- Upload and analysis responses now preserve ad exclusion coverage through `excluded_ad_count`, `ad_skip_summary`, and `skipped_sources_with_reason`, and the dashboard search card shows the excluded ad count.
- Real ZIP validation with `takeout-20260601T113511Z-3-001.zip` now excludes 1,014 ad/promotional events, saves 2,113 analysis events, and reduces the search interest map to 60 cleaned search entries.

## 2026-06-03 Takeout ZIP QA note
- Ran the real `takeout-20260601T113511Z-3-001.zip` upload flow through the backend TestClient. It parsed 3,209 Takeout items, saved 2,023 non-ad events, and excluded 1,096 ad-origin events.
- Adjusted `content_format_counts` to count only watch/video events so search, subscription, playlist, comment, live chat, and channel records do not inflate the `unknown` content-format bucket.
- After the adjustment, the same ZIP reports `standard_video=322`, `unknown=285`, `shorts=0`, and `live=0` for watch-format counts while source-type counts still keep all parsed Takeout categories separate.

## 2026-06-03 Shorts phase 2 analysis note
- Follow-up: added `passive_feed_score` as a heuristic estimate from shorts ratio, loop pressure, repeated topics, time concentration, and active-search scarcity. It does not claim to identify home-feed or recommendation origin.
- Added `backend/app/core/shorts_analysis.py` for deterministic shorts-only metrics: loop grouping, repeated keyword scoring, time-bucket concentration, and `shorts_stimulation_risk`.
- Dashboard and analysis responses now include `information_bias_risk`, `shorts_stimulation_risk`, and `final_detox_risk` while keeping `shorts_ratio` backward compatible as a 0-1 ratio.
- Detox generation now passes backend-computed `shorts_analysis` into Gemini/mock mission generation and prepends gentle shorts reset missions when shorts data exists.
- Dashboard UI now has a dedicated shorts section with loop, repeated-scroll, time-bucket, keyword, warning, and empty-state displays.
- Validation covered upload -> analysis -> dashboard -> detox with 6 consecutive shorts events grouped into one meaningful loop.

## 2026-06-03 Shorts phase 1 UI note
- Upload completion now shows the basic `shorts_analysis` metrics: `shorts_count`, `shorts_ratio`, and `top_shorts_keywords`.

## 2026-06-03 숏츠/일반 영상 1차 분리 메모

### 14. content_format, intent_level 기반 시청 유형 분리
- 무엇을 수정했나: `norm_event`에 `content_format`과 `intent_level`을 저장하도록 업로드 파이프라인을 바꿨다. `/shorts/` URL은 `shorts`, 일반 `watch?v=` URL은 `standard_video`, 라이브 URL은 `live`, 판단 불가는 `unknown`으로 저장한다.
- 검색 기록 기준: 검색 기록은 `action_type=search`, `source_type=search_history`, `intent_level=active_search`, `source_surface=unknown`으로 저장한다.
- 유입 경로 기준: Google Takeout만으로 홈피드/추천/구독탭/직접 클릭 여부를 확정할 수 없으므로 더 이상 `home_feed`나 `search_results`를 임의로 넣지 않는다.
- 숏츠 분석 기준: 숏츠는 일반 TDS/SBS/VOS 신호에 무작정 섞지 않고 `shorts_analysis`로 별도 집계한다. 1차 지표는 `shorts_count`, `shorts_ratio`, `top_shorts_keywords`다.
- 2차 TODO: `dopamine_loop_score`, `passive_feed_score`, 시간대별 연속 스크롤 패턴, 숏츠 전용 UI, 숏츠 전용 디톡스 미션은 다음 고도화 단계로 남겼다.

## 2026-06-03 광고/프로모션 검색어 필터 보강

### 13. 검색어 버블 광고성 제목 제거 보강
- 무엇을 수정했나: `Shortened: cid=...`, `gclid`, `utm_`, `adurl`, `aclk` 같은 광고 클릭 추적 패턴과 `공식몰`, `타임딜`, `인기 제품`, `닥터패치`, `LGE.COM`, `The Android Show` 같은 화면에서 확인된 캠페인성 제목을 광고/노이즈 필터에 추가했다.
- 왜 수정했나: 기존 필터는 `From Google Ads`처럼 명시적인 광고 출처만 잡아서, 검색어 버블에 광고 랜딩/쇼핑 프로모션 제목이 남았다.
- 확인 방법: 테스트 ZIP에서 검색 기록 7건 중 광고성 6건을 제외하고 일반 검색어 1건만 분석 대상으로 남기는 것을 확인했다. 응답 기준은 `total_parsed=8`, `total_saved=2`, `excluded_ad_count=6`이다.
- 주의사항: 실제 사용자가 쇼핑몰/제품명을 의도적으로 검색한 경우까지 일부 제외될 수 있으므로, 이후에는 제외 목록을 설정 화면이나 별도 allowlist로 조정하는 개선이 필요하다.

## 2026-06-02 광고 데이터 제외 메모

### 12. 광고 출처 이벤트 분석 제외
- 무엇을 수정했나: `content_filters.py`를 추가해 `From Google Ads`, `YouTube Ads`, `doubleclick`, `googleadservices`, `광고에서`, `광고를 시청` 같은 광고 출처 신호를 공통으로 감지하도록 했다.
- 업로드 반영: 광고로 감지된 이벤트는 YouTube 메타데이터 조회, 타임라인 시청시간 계산, `norm_event` 저장, 세션 텍스트 생성 전에 제외된다.
- 분석 반영: 기존 저장 데이터에 광고 이벤트가 남아 있어도 `analysis/run`, feature 추출, dashboard 인사이트 생성 단계에서 다시 제외한다.
- 화면 반영: 업로드 완료 카드에 `광고 출처 제외` 건수를 표시해 몇 건이 분석에서 빠졌는지 확인할 수 있게 했다.
- 확인 기준: 검색어 버블과 점수 계산에는 광고 출처 이벤트가 들어가지 않아야 하며, 응답의 `excluded_ad_count`로 제외 건수를 확인한다.

## 2026-06-02 추가 메모

### 11. 업로드 파서 제한값과 시청시간 계산식 정리
- 무엇을 수정했나: `upload_config.py`를 추가해 ZIP 제한, HTML/JSON/CSV 파서 최대 처리량, 시청시간 추정 기본값, 타임라인 최대 간격, YouTube 메타데이터 조회 한도를 한 곳에서 관리하도록 바꿨다.
- 왜 수정했나: `upload.py` 안에 흩어져 있던 `300개 제한`, `45초/300초 추정`, `5초 필터`, `6시간 타임라인 간격` 같은 값이 실제 계산 기준인지 임시값인지 구분하기 어려웠다.
- 실제 계산 기준: 시청 이벤트는 먼저 YouTube Data API의 `contentDetails.duration`을 사용하고, API duration이 없으면 다음 이벤트까지의 시간 간격으로 상한을 잡으며, 그래도 부족하면 쇼츠/일반 영상 휴리스틱을 쓴다.
- 분석 반영: `duration_source_counts`를 업로드 응답에 추가해 `youtube_api`, `timeline_capped_api`, `timeline_gap`, `shorts_heuristic`, `default_heuristic` 중 어떤 기준이 쓰였는지 확인할 수 있게 했다.
- 확인 방법: 백엔드에서 `.\venv\Scripts\python.exe -m compileall app`를 통과했고, `parse_iso8601_duration('PT1H2M3S')`가 `3723`초로 계산되는 것을 확인했다.

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

### 10. 대시보드 실제 인사이트 연결
- 무엇을 수정했나: `dashboard/summary` API가 `norm_event`와 `nlp_result`를 다시 읽어 검색어 상위 목록, NLP 카테고리 비중, 출처 비중, 짧은 해석 문장을 `insights`로 반환하도록 했다.
- 왜 수정했나: 대시보드가 `insightMock`의 고정 검색어/카테고리/해석을 사용하고 있어 실제 업로드 결과와 화면 인사이트가 맞지 않았다.
- 프론트 반영: `dashboard/page.tsx`에서 `insightMock` import를 제거하고 `processedData.insights`를 사용하도록 변경했다. 검색어나 NLP 주제가 부족하면 임시값 대신 데이터 부족 상태를 표시한다.
- 설정 정리: `apiConfig.ts`를 추가해 `API_BASE_URL`과 `DEFAULT_USER_ID`를 공통 관리하고, dashboard/upload/mission의 하드코딩된 API 주소를 이 설정으로 교체했다.
- 확인 방법: 백엔드 `compileall`, 프론트 TypeScript `tsc --noEmit`, 승인 권한의 Next production build를 모두 통과했다.
