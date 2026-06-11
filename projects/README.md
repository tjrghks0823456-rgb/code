# Main Portfolio Projects

> 목표 직무: **C# / WPF 기반 반도체·디스플레이 장비 PC 제어 소프트웨어 개발자**

C# WPF 기반 HMI, EtherCAT/PLC 통신 연동, Flask 백엔드, 데이터 분석 서비스를 학습하며 진행한 프로젝트들입니다.

---

## 🏭 장비 제어 / HMI 프로젝트

### 1. semiconductor-etch-hmi-system
[`etch-equipment-hmi/`](./etch-equipment-hmi/)

> **TwinCAT PLC · WPF · Flask · Scikit-Learn 기반 반도체 식각 장비 상태 관리 HMI 시스템**

| 항목 | 내용 |
|------|------|
| 기술 | C#, WPF, TwinCAT ADS, Flask, SQLite, Scikit-Learn |
| 역할 | PLC 센서 수집 → WPF HMI 제어/시뮬레이션 → Flask AI 예측 3계층 통합 |
| 특징 | Load Lock/Chamber 상태 관리, 가상 웨이퍼 이송 시뮬레이션, AI 고장 예측 |

```
csharp  wpf  hmi  semiconductor  etch-equipment  plc  ethercat  state-machine  recipe  alarm
```

---

### 2. etch-equipment-control-simulator
[`semitool-hmi/`](./semitool-hmi/)

> **C# · WinForms · EtherCAT DLL 기반 반도체 식각 장비 HMI 개발 기록**

| 항목 | 내용 |
|------|------|
| 기술 | C#, WinForms, EtherCAT DLL (IEG3268_Dll.dll) |
| 역할 | 레거시 수동 제어 → HMI 계층 분리 구조로 발전 과정 담음 |
| 특징 | EtherCAT 실장비 DLL 연동, Hardware/Process/Data 계층 분리, 레시피/로그 |

> `semiconductor-etch-hmi-system`은 TwinCAT ADS + WPF, 이 프로젝트는 EtherCAT DLL + WinForms로 접근이 다릅니다.

```
csharp  winforms  ethercat  hmi  equipment-control  semiconductor  dll-integration
```

---

### 3. smart-logistics-plc-system
[`flask-csharp-integration/`](./flask-csharp-integration/)

> **Flask · C# WinForms · REST API 기반 실시간 센서 모니터링 및 가상 장비 제어 실습**

| 항목 | 내용 |
|------|------|
| 기술 | C#, WinForms, Flask (Python), HTTP REST API |
| 역할 | C# 가상 센서 → Flask 백엔드 → 웹 대시보드 실시간 연동 |
| 특징 | 정전/지진 시나리오 State Machine, 실시간 센서 차트, 원격 제어 |

```
flask  csharp  winforms  rest-api  sensor-monitoring  real-time  state-machine
```

---

## 🌐 풀스택 / 데이터 분석 프로젝트

### 4. unbelievable-digital-wellbeing
[`unbelievable/`](./unbelievable/)

> **FastAPI · Next.js 기반 YouTube 시청 기록 분석 및 디지털 디톡스 추천 서비스 (팀 프로젝트)**

| 항목 | 내용 |
|------|------|
| 기술 | Python, FastAPI, Next.js, TypeScript, SQLite |
| 역할 | YouTube Takeout 데이터 파싱 → 6축 편향 지표 분석 → DSAO 유형 분류 → 디톡스 추천 |
| 특징 | Shannon Entropy/HHI 지수 계산, 메타인지 격차 시각화, CHANGELOG 관리 |

```
python  fastapi  nextjs  data-analysis  youtube  digital-wellbeing  dashboard
```

---

### 5. emotion-based-music-recommender
[`emotion-music-recommendation/`](./emotion-music-recommendation/)

> **Flask · GPT API · Spotify API 기반 복합 감정 분석 및 음악 추천 서비스 (팀 프로젝트)**

| 항목 | 내용 |
|------|------|
| 기술 | Python, Flask, OpenAI GPT API, Spotify API, MySQL |
| 역할 | 감정 문장 입력 → GPT 감정 분류 → Spotify 트랙 추천 → 피드백 DB 저장 |
| 특징 | 복합 감정 처리, 피드백 기반 추천 개선 구조, 오늘의 감정 통계 |

```
flask  openai  spotify  mysql  emotion-analysis  music-recommendation  gpt
```

---

## 📚 학습 실습 (Practice Labs)

학습 실습과 수업 과제는 별도로 분리해 정리했습니다.

| 폴더 | 내용 |
|------|------|
| [`winforms-gui-portfolio/`](./winforms-gui-portfolio/) | WinForms 기초 UI/이벤트 연습 모음 |
| [`course-registration-system/`](./course-registration-system/) | C# 콘솔 앱 수강신청 시스템 과제 |
| [`equipment-management-winforms/`](./equipment-management-winforms/) | MySQL 연동 장비 대여/반납 관리 실습 |
| [`digital-detox/`](./digital-detox/) | 디지털 디톡스 서비스 기획 플로우차트 자료 |

> 작은 실습 결과물을 프로젝트처럼 포장하지 않고, 학습 기록으로 분리해 정리했습니다.

---

## 저장소 분류 문서

상세 분류 기준과 GitHub Topics 추천은 [`docs/github-repository-classification.md`](../docs/github-repository-classification.md)를 참조하세요.
