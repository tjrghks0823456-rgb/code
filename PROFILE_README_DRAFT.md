# PROFILE README DRAFT

> 이 파일을 GitHub 프로필 저장소 (`tjrghks0823456-rgb/tjrghks0823456-rgb`)의 `README.md`에 붙여넣으면 GitHub 프로필에 표시됩니다.

---

# 손석환 | C# · WPF 기반 장비 제어 SW 개발 지망

C#과 WPF를 기반으로 반도체·디스플레이 장비의 PC 제어 소프트웨어를 공부하고 있습니다.  
장비 상태 관리, HMI 화면 구성, PLC 및 EtherCAT 통신 연동, DB 기반 레시피 관리, 로그/알람 처리 흐름에 관심이 있습니다.

---

## 관심 분야

- Equipment Control Software (C# / WPF)
- Semiconductor / Etch Equipment HMI
- PLC / EtherCAT / Serial / TCP-IP 통신 연동
- DB 기반 Recipe 관리 및 Alarm / Log 처리
- Sensor Monitoring 및 상태 머신 설계
- Data Analysis 및 Recommendation System

---

## Tech Stack

**Language**  
C#  &nbsp;|&nbsp;  Python  &nbsp;|&nbsp;  Java  &nbsp;|&nbsp;  JavaScript / TypeScript

**UI / HMI**  
WPF  &nbsp;|&nbsp;  WinForms  &nbsp;|&nbsp;  Next.js (React)

**Backend**  
Flask  &nbsp;|&nbsp;  FastAPI  &nbsp;|&nbsp;  Spring Boot

**Database**  
SQLite  &nbsp;|&nbsp;  MySQL  &nbsp;|&nbsp;  Supabase

**Communication**  
TCP/IP  &nbsp;|&nbsp;  PLC (TwinCAT ADS)  &nbsp;|&nbsp;  EtherCAT DLL

**Tools**  
Visual Studio 2022  &nbsp;|&nbsp;  GitHub  &nbsp;|&nbsp;  Notion  &nbsp;|&nbsp;  Wireshark

---

## Main Portfolio Projects

### 1. semiconductor-etch-hmi-system
> TwinCAT PLC · WPF · Flask · AI 기반 반도체 식각 장비 상태 관리 HMI 시스템

**주요 기술:** C#, WPF, TwinCAT ADS, Flask, SQLite, Scikit-Learn  
**핵심 구현:**
- PLC ADS 통신으로 압력·진동·온습도 센서 실시간 수집 및 장비 명령 하달
- 가상 웨이퍼 이송 시뮬레이션 (FOUP → Aligner → Load Lock → PM Chamber)
- Flask + Scikit-Learn 기반 AI 고장 예측 모델 서빙 및 HMI 결과 표시

**배운 점:** PLC와 PC SW 간 ADS 프로토콜 통신 구조, WPF 상태 바인딩, 3계층 아키텍처 설계

[→ 저장소 보기](https://github.com/tjrghks0823456-rgb/code/tree/main/projects/etch-equipment-hmi)

---

### 2. etch-equipment-control-simulator
> C# · WinForms · EtherCAT DLL 기반 반도체 장비 HMI 개발 기록

**주요 기술:** C#, WinForms, EtherCAT DLL (IEG3268_Dll.dll)  
**핵심 구현:**
- EtherCAT 외부 장비 DLL 연동 및 IO 제어
- 레거시 단일 폼 코드 → Hardware/Process/Data 계층 분리 리팩토링
- 공정 시나리오, 레시피 저장, 장비 동작 로그 기록 구조

**배운 점:** EtherCAT DLL 연동, 계층 분리 리팩토링 경험, 공정 시나리오 코딩

[→ 저장소 보기](https://github.com/tjrghks0823456-rgb/code/tree/main/projects/semitool-hmi)

---

### 3. smart-logistics-plc-system
> Flask · C# WinForms · REST API 기반 실시간 센서 모니터링 및 가상 장비 제어

**주요 기술:** C#, WinForms, Flask, HTTP REST API  
**핵심 구현:**
- C# HttpClient로 센서 데이터 Flask 서버에 실시간 전송
- Flask 백엔드 State Machine: 정전(전력<300) 자동 감지 → 비상전력 10초 고정 → 복구
- 지진 경보(진동>0.5) → 팝업 → 방화벽 가동으로 전체 시뮬레이션 리셋

**배운 점:** REST API 설계, 상태 머신 백엔드 구현, 프론트엔드 폴링 기반 실시간 데이터 표시

[→ 저장소 보기](https://github.com/tjrghks0823456-rgb/code/tree/main/projects/flask-csharp-integration)

---

### 4. unbelievable-digital-wellbeing
> FastAPI · Next.js 기반 YouTube 시청 기록 분석 및 디지털 디톡스 추천 서비스 (팀 프로젝트)

**주요 기술:** Python, FastAPI, Next.js, TypeScript, SQLite  
**핵심 구현:**
- YouTube Takeout JSON/HTML 다중 파싱 및 무의식 스크롤 필터링
- Shannon Entropy / HHI 공식 기반 6축 편향 지표 수치화
- DSAO 16유형 분류, 자가진단 vs 실제 데이터 메타인지 격차 레이더 차트

**배운 점:** 실제 데이터의 품질 문제를 코드로 처리하는 방법, FastAPI 풀스택 흐름, CHANGELOG 기반 팀 협업

[→ 저장소 보기](https://github.com/tjrghks0823456-rgb/code/tree/main/projects/unbelievable)

---

### 5. emotion-based-music-recommender
> Flask · GPT API · Spotify API 기반 복합 감정 분석 음악 추천 서비스 (팀 프로젝트)

**주요 기술:** Python, Flask, OpenAI GPT API, Spotify API, MySQL  
**핵심 구현:**
- GPT API로 복합 감정 후보 추출 (단일 감정 분류 한계 극복)
- Spotify API 연동 감정별 최신곡/클래식 트랙 추천
- 사용자 피드백을 MySQL에 저장하는 추천 개선 구조

**배운 점:** 외부 API 연동 및 Rate Limit 처리, 문제 정의에서 출발한 구조 설계

[→ 저장소 보기](https://github.com/tjrghks0823456-rgb/code/tree/main/projects/emotion-music-recommendation)

---

## Practice Labs

학습 실습과 수업 과제는 프로젝트와 혼재되지 않도록 별도로 분리해 정리했습니다.

| 실습 | 내용 |
|------|------|
| `winforms-gui-practice` | C# WinForms 기초 UI/이벤트 연습 |
| `csharp-course-registration-practice` | C# 콘솔 앱 수강신청 과제 |
| `winforms-equipment-management-practice` | MySQL 연동 WinForms 장비 관리 실습 |

> 작은 실습 저장소들은 프로젝트로 포장하지 않고, 기술 학습 기록으로 분리해 정리했습니다.

---

📫 [GitHub](https://github.com/tjrghks0823456-rgb)
