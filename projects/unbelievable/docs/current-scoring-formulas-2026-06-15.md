# Unbelievable 현재 계산식 보고서

작성일: 2026-06-15  
대상: `projects/unbelievable`

## 1. 전체 계산 흐름

현재 분석 파이프라인은 아래 순서로 동작한다.

1. Google Takeout 업로드 데이터를 `norm_event` 형태로 정규화한다.
2. 광고/프로모션성 이벤트는 분석 대상에서 제외한다.
3. 정규화 이벤트와 NLP 결과를 기반으로 특징값을 만든다.
4. 특징값으로 6축 점수 `UAS`, `SBS`, `TDS`, `EBS`, `SMS`, `VOS`를 계산한다.
5. 사용 가능한 축 점수 평균으로 `weighted_health`를 만든다.
6. `bias_risk_score = 100 - weighted_health`로 정보 편향 위험 점수를 만든다.
7. 숏츠 분석 결과가 있으면 최종 디톡스 위험도 `final_detox_risk`에 일부 반영한다.
8. 대시보드에서는 6축 점수와 시청 길이 비율을 조합해 실제 DSAO 유형을 표시한다.

핵심 파일:

- `backend/app/core/features.py`
- `backend/app/core/scoring.py`
- `backend/app/core/shorts_analysis.py`
- `backend/app/services/analysis_service.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/core/interest_maps.py`
- `backend/app/core/survey_scoring.py`
- `backend/app/data/rules/scoring_rules.v1.json`

## 2. 설정값 기준

주요 가중치와 임계값은 `backend/app/data/rules/scoring_rules.v1.json`에서 읽는다.

### 공통

- 점수 범위: `0 ~ 100`
- 중립 점수: `50`
- 최소 데이터 기준:
  - 전체 이벤트: `10`
  - 시청 이벤트: `10`
  - 검색 이벤트: `3`
  - 주제 수: `3`
  - 채널 수: `3`
  - 감정 샘플: `2`
  - 안전성 샘플: `2`

### UAS 가중치

사용자 주도성 점수는 아래 비율을 가중 평균한다.

```text
UAS =
  search_ratio * 0.35
+ direct_selection_ratio * 0.25
+ curation_ratio * 0.25
+ participation_ratio * 0.15
```

단, 값이 `None`인 항목은 계산에서 제외하고 남은 가중치만 재정규화한다.

### SMS 가중치

안전/자극 점수는 위험 패널티를 먼저 계산한 뒤 `100 - penalty`로 만든다.

```text
SMS penalty =
  toxic_ratio * 0.35
+ harmful_keyword_ratio * 0.25
+ shorts_ratio * 0.20
+ repeated_short_exposure_ratio * 0.20

SMS = 100 - SMS penalty
```

### VOS 가중치

관점 개방성 점수도 집중도 패널티를 먼저 계산한 뒤 `100 - concentration`으로 만든다.

```text
VOS concentration =
  topic_concentration * 0.45
+ channel_concentration * 0.35
+ search_repetition * 0.20

VOS = 100 - VOS concentration
```

## 3. 특징값 산출식

`features.py`에서 이벤트 기반 특징값을 만든다.

### 검색 비율

```text
search_ratio = search_count / (watch_count + search_count)
```

검색 이벤트가 0개면 `None`으로 처리한다. 따라서 검색 데이터가 없으면 사용자 주도성 판단 신뢰도가 떨어진다.

### 직접 선택 비율

```text
direct_selection_ratio = direct_selection_count / watch_count
```

단, `source_surface`가 명확한 이벤트가 하나도 없으면 `None`이다. Google Takeout만으로 홈피드, 추천, 검색결과 클릭을 확정하기 어렵기 때문에 모호한 경우 임의로 채우지 않는다.

### 큐레이션 비율

```text
curation_ratio = min(1, curation_count / total_events)
```

`subscription`, `playlist`, `channel` 관련 이벤트가 큐레이션 신호로 들어간다.

### 참여 비율

```text
participation_ratio = min(1, participation_count / total_events)
```

`comment`, `live_chat` 관련 이벤트가 참여 신호로 들어간다.

### 숏츠 비율

```text
shorts_ratio = shorts_count / watch_count
```

`content_format = "shorts"`로 감지된 이벤트만 숏츠로 계산한다.

### 반복 숏츠 노출 비율

```text
repeated_short_exposure_ratio = consecutive_shorts_count / watch_count
```

정렬된 이벤트에서 숏츠가 연속으로 등장하면 반복 숏츠 노출로 본다. 실제 스크롤 체류 시간이 아니라 이벤트 순서 기반 휴리스틱이다.

### 데이터 신뢰도

```text
data_confidence =
  sample_confidence * 0.45
+ source_confidence * 0.20
+ topic_confidence * 0.20
+ duration_confidence * 0.15
```

각 항목은 0~1 범위로 제한된다.

## 4. 6축 점수 계산식

## 4.1 UAS: 사용자 주도성 점수

UAS는 검색, 직접 선택, 큐레이션, 댓글/채팅 참여를 기반으로 한다.

```text
UAS = weighted_ratio_score(
  search_ratio,
  direct_selection_ratio,
  curation_ratio,
  participation_ratio
)
```

현재 의미:

- 높을수록 직접 검색하거나 능동적으로 선택한 흔적이 많다.
- 낮을수록 수동 소비 또는 출처 불명 이벤트 비중이 높다고 해석된다.

주의점:

- Takeout만으로 직접 선택 경로를 확정하기 어렵다.
- `search_ratio`와 `direct_selection_ratio`가 둘 다 없으면 UAS는 사용할 수 없는 축으로 처리되고 표시 점수는 중립값 50에 가까워진다.

## 4.2 SBS: 출처 균형 점수

SBS는 채널 분포의 HHI를 사용한다.

```text
hhi = sum(channel_ratio ^ 2)
```

채널이 2개 이상이면 아래 식을 사용한다.

```text
relative_balance = ((1 - hhi) / (1 - 1 / source_count)) * 100
source_count_factor = 0.65 + 0.35 * (1 - exp(-source_count / 3))
SBS = relative_balance * source_count_factor
```

현재 의미:

- 높을수록 여러 출처를 고르게 본다.
- 낮을수록 특정 채널이나 출처에 집중되어 있다.

주의점:

- 채널 정보가 없으면 사용 불가 축으로 처리된다.
- 채널이 1개뿐이면 SBS는 0점이다.

## 4.3 TDS: 주제 다양성 점수

TDS는 주제 분포의 Shannon entropy를 사용한다.

```text
entropy = -sum(p * log2(p))
TDS = entropy / log2(15) * 100
```

NLP 샘플이 부족하면 로컬 키워드 카테고리 분포로 대체한다.

```text
use_local_fallback = nlp_count < 2 or topic_total < 3
```

현재 의미:

- 높을수록 주제가 다양하다.
- 낮을수록 일부 주제에 몰려 있다.

주의점:

- 정규화 기준이 항상 `15개 카테고리`라서 실제 카테고리 수가 적은 데이터에서는 점수가 낮게 나올 수 있다.
- `기타/미분류` 비중이 70% 이상이면 경고가 붙고, 80% 이상이면 신뢰도를 0으로 낮춘다.

## 4.4 EBS: 감정 균형 점수

EBS는 부정 감정, 자극 키워드, 안정 신호를 조합한다.

```text
negative_ratio = negative_count / sentiment_total
negative_penalty = negative_ratio * 40

stimulus_ratio = stimulus_event_count / total_events
stimulus_penalty = stimulus_ratio * 30

stability_ratio =
  (neutral_count + stable_local_category_count + calm_event_count)
  / (total_events + nlp_count)

stability_boost = stability_ratio * 20

EBS = 100 - negative_penalty - stimulus_penalty + stability_boost
```

NLP 결과에 `stability_factor`가 있으면 아래처럼 섞는다.

```text
EBS = EBS * 0.7 + average(stability_factor) * 100 * 0.3
```

현재 의미:

- 높을수록 감정적으로 안정적인 시청/검색 패턴에 가깝다.
- 낮을수록 부정 감정, 자극적 제목, 과격한 키워드가 많다.

주의점:

- 자극 키워드와 안정 키워드 일부가 아직 코드에 하드코딩되어 있다.
- 제목 기반 키워드 휴리스틱이라 실제 영상 내용 전체를 판정하는 것은 아니다.

## 4.5 SMS: 안전/자극 점수

SMS는 위험 신호를 패널티로 계산한 뒤 100에서 뺀다.

```text
SMS penalty =
  toxic_ratio * 0.35
+ harmful_keyword_ratio * 0.25
+ shorts_ratio * 0.20
+ adjusted_repeated_short_ratio * 0.20

SMS = 100 - SMS penalty
```

반복 숏츠 비율은 실제 체류 시간이 있느냐에 따라 보정된다.

```text
adjusted_repeated_short_ratio =
  repeated_short_exposure_ratio * 1.0  if actual_duration_exists
  repeated_short_exposure_ratio * 0.2  if actual_duration_missing
```

NLP 결과에 `safety_factor`가 있으면 아래처럼 섞는다.

```text
SMS = SMS * 0.8 + average(safety_factor) * 100 * 0.2
```

현재 의미:

- 높을수록 안전하고 자극 위험이 낮다.
- 낮을수록 유해 키워드, 독성 카테고리, 숏츠 반복 소비 위험이 크다.

주의점:

- `toxic_ratio`는 NLP 샘플이 2개 미만이면 제외된다.
- 숏츠 반복은 정확한 체류 시간이 아니라 이벤트 순서와 URL 감지에 크게 의존한다.

## 4.6 VOS: 관점 개방성 점수

VOS는 주제, 채널, 검색어 반복 집중도를 패널티로 계산한다.

```text
topic_concentration = max(topic_category_ratio)
channel_concentration = max(channel_ratio)
search_repetition = max(search_keyword_ratio)

concentration =
  topic_concentration * 0.45
+ channel_concentration * 0.35
+ search_repetition * 0.20

VOS = 100 - concentration
```

학습, 코딩, 금융, 건강처럼 생산적 몰입으로 볼 수 있는 카테고리는 집중도에 완화 계수를 적용한다.

```text
adjusted_concentration = raw_concentration * 0.5
```

현재 의미:

- 높을수록 특정 주제나 채널에 과도하게 갇히지 않는다.
- 낮을수록 특정 주제, 채널, 검색어에 몰려 있다.

주의점:

- 생산적 몰입 완화 기준은 현재 룰 파일과 코드 값에 의존한다.
- 반복 검색이 꼭 나쁜 것은 아니지만, 현재는 관점 좁아짐 후보로 계산된다.

## 5. 종합 점수 계산식

`analysis_service.py`에서 사용 가능한 축만 평균낸다.

```text
weighted_health = average(available_axis_scores)
bias_risk_score = 100 - weighted_health
```

중요:

- 이름은 `weighted_health`지만 현재는 축별 별도 가중치가 없는 단순 평균이다.
- 사용할 수 없는 축은 평균에서 제외된다.
- 사용 가능한 축이 하나도 없으면 `weighted_health = 50`이다.

전체 신뢰도:

```text
excluded_axes >= 2  -> low
excluded_axes == 1  -> medium
excluded_axes == 0  -> high
```

## 6. 숏츠 전용 위험 계산식

`shorts_analysis.py`에서 숏츠만 따로 분석한다.

### 숏츠 반복 주제 점수

```text
repeated_topic_score = min(100, repeated_keyword_count * 12)
```

동일 키워드가 3회 이상 반복되면 반복 키워드로 본다.

### 도파민 루프 점수

숏츠 간격이 180초 이하로 이어지면 하나의 루프로 묶는다.

```text
base = min(100, meaningful_loop_count * 15)
length_bonus = min(30, max_loop_length * 2)
duration_bonus = min(20, max_loop_duration_min * 1.5)

dopamine_loop_score = min(100, base + length_bonus + duration_bonus)
```

의미 있는 루프 기준:

- `MEANINGFUL_LOOP_MIN_COUNT = 5`
- `HIGH_LOOP_MIN_COUNT = 10`

### 시간대 집중 점수

```text
peak_ratio = peak_time_bucket_count / timed_shorts_count * 100
late_night_ratio = (dawn_count + night_count) / timed_shorts_count * 100

time_concentration_score =
  min(100, peak_ratio * 1.2 + 10 if late_night_ratio >= 60 else peak_ratio * 1.2)
```

시간대:

- dawn: 0~5시
- morning: 6~11시
- afternoon: 12~17시
- night: 18~23시

### 수동 피드 점수

```text
active_search_ratio = active_search_count / (shorts_count + active_search_count)

passive_feed_score =
  shorts_ratio * 35
+ dopamine_loop_score * 0.35
+ repeated_topic_score * 0.15
+ time_concentration_score * 0.10
+ (1 - active_search_ratio) * 15
```

### 숏츠 자극 위험

```text
shorts_stimulation_risk =
  dopamine_loop_score * 0.35
+ repeated_topic_score * 0.25
+ time_concentration_score * 0.20
+ passive_feed_score * 0.20
```

## 7. 최종 디톡스 위험도

정보 편향 위험도와 숏츠 자극 위험도를 섞는다.

```text
if shorts_count <= 0:
    shorts_weight = 0.0
elif shorts_count < 20:
    shorts_weight = 0.10
else:
    shorts_weight = 0.30

final_detox_risk =
  bias_risk_score * (1 - shorts_weight)
+ shorts_stimulation_risk * shorts_weight
```

현재 의미:

- 숏츠가 없으면 최종 위험도는 정보 편향 위험도와 같다.
- 숏츠가 1~19개면 숏츠 위험이 10% 반영된다.
- 숏츠가 20개 이상이면 숏츠 위험이 30% 반영된다.

## 8. DSAO 실제 유형 계산식

대시보드의 실제 DSAO 유형은 아래 기준으로 만든다.

```text
D/P = D if UAS >= 50 else P
W/N = W if TDS >= 50 else N
S/M = M if SMS >= 50 else S
F/L = L if long_video_ratio >= 50 else F
```

긴 영상 비율은 일반 영상 중 `time_delta_sec >= 180`인 이벤트 비율이다.

```text
long_video_ratio =
  long_standard_video_view_count / standard_video_view_count * 100
```

일반 영상 이벤트가 없으면 `long_video_ratio = 100`으로 처리한다.

주의점:

- 대시보드 DSAO 판정은 모두 50점 기준이다.
- 반면 `scoring.py`의 기존 16유형 판정은 설정 파일의 `classification_thresholds`를 사용한다.
- 따라서 내부 legacy 유형과 대시보드 DSAO 유형 기준이 완전히 같지는 않다.

## 9. 자가진단 점수 변환식

자가진단 8축 점수는 `survey_scoring.py`에서 6축으로 변환된다.

```text
UAS = D / (D + P) * 100
TDS = W / (W + N) * 100
SMS = M / (S + M) * 100
VOS = W / (W + N) * 100
EBS = None
SBS = None
```

주의점:

- 현재 VOS는 별도 질문이 없어서 W/N 답변을 임시 재사용한다.
- EBS와 SBS는 자가진단 대응축이 없어 공식 갭 계산에서 제외된다.

## 10. 검색 vs 시청 vs 숏츠 관심사 차이 계산식

`interest_maps.py`에서 관심사 비중 차이를 계산한다.

### 카테고리별 차이

```text
gap = target_ratio - search_ratio
abs_gap = abs(gap)
```

### 전체 불일치 점수

검색 기반 관심사와 일반 시청/숏츠 관심사의 L1 distance를 사용한다.

```text
standard_gap =
  sum(abs(standard_ratio[category] - search_ratio[category])) / 2

shorts_gap =
  sum(abs(shorts_ratio[category] - search_ratio[category])) / 2

interest_mismatch_score =
  min(100, (standard_gap * 0.7 + shorts_gap * 0.3) * 100)
```

### 추천 흐름 영향 후보 점수

```text
watch_lift = max(0, standard_video_ratio - search_ratio)
shorts_lift = max(0, shorts_ratio - search_ratio)

candidate_score = (watch_lift * 0.7 + shorts_lift * 0.3) * 100
```

`candidate_score < 8`이면 후보에서 제외한다.

주의점:

- 이 값은 알고리즘 확정 판정이 아니다.
- Google Takeout만으로 추천 경로를 확정할 수 없기 때문에 “검색 대비 실제 시청에서 많이 나타난 주제”로 해석해야 한다.

## 11. 현재 계산식의 장점

1. 점수별 구성요소가 `score_components`로 노출되어 설명 가능성이 높다.
2. 광고 이벤트를 제외하고 분석하려는 구조가 들어가 있다.
3. 검색, 일반 영상, 숏츠를 분리해 관심사 맵을 만들 수 있다.
4. 데이터 부족 축은 무리하게 확정하지 않고 `available=false`, `confidence=low`로 처리한다.
5. 숏츠는 일반 정보 편향 점수와 분리된 별도 위험 점수를 갖는다.

## 12. 현재 계산식의 한계

1. `weighted_health`는 이름과 달리 축별 가중 평균이 아니라 단순 평균이다.
2. EBS 감정 키워드, 숏츠 루프 임계값, 일부 시간대 구간은 아직 코드에 하드코딩되어 있다.
3. TDS는 항상 15개 카테고리 기준으로 정규화되어 실제 카테고리 수가 적으면 낮게 나올 수 있다.
4. DSAO 대시보드 판정 기준과 legacy 16유형 판정 기준이 다르다.
5. 숏츠 분석은 URL, 이벤트 시간, 제목 키워드에 의존하므로 Takeout 데이터 품질이 낮으면 과소 감지될 수 있다.
6. 검색 경로, 홈피드, 추천, 구독탭 유입은 Takeout만으로 확정할 수 없어 `unknown` 처리되는 것이 맞다.
7. 자가진단 VOS는 아직 별도 문항이 없어 W/N 답변을 임시 재사용한다.
8. 관심사 불일치와 추천 흐름 후보는 비중 차이 기반 추정이며 알고리즘 노출 확정값이 아니다.

## 13. 개선 우선순위 제안

1. `weighted_health`를 실제 축별 가중 평균으로 바꾸거나 이름을 `axis_average_health`로 변경한다.
2. EBS 키워드, 숏츠 임계값, 시간대 버킷, 후보 점수 임계값을 JSON 설정으로 분리한다.
3. DSAO 판정 기준을 대시보드와 legacy 16유형에서 하나로 통일한다.
4. TDS 정규화 기준을 실제 사용 카테고리 수 또는 서비스 카테고리 수에 맞춰 재검토한다.
5. 자가진단에 VOS, SBS, EBS 대응 문항을 추가해 실제 분석과 자가진단 갭의 품질을 높인다.
6. Gemini API는 미분류 감소와 엔티티/소분류 품질 개선용 보조 분류기로 적용하고, 점수 수식 자체는 먼저 고정된 룰 엔진으로 안정화한다.

