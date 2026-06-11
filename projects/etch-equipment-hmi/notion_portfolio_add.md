# 📁 [포트폴리오 추가 항목] PLC · WPF · Flask 기반 플라즈마 식각 장비 상태 관리 HMI 시스템

> **본 항목을 드래그 후 복사(Ctrl+C)하여 노션 포트폴리오 페이지의 프로젝트 섹션에 추가해 주시면 기존 디자인 양식과 완벽히 부합하게 배치할 수 있습니다.**

---

## 📌 프로젝트 정보
* **프로젝트명:** PLC · WPF · Flask 기반 플라즈마 식각 장비 상태 관리 HMI 프로젝트
* **개발 부문:** 장비 시스템 소프트웨어 개발 (식각 장비)
* **개발 기간:** 2026.05 ~ 2026.06
* **개발 인원:** 3인 (손석환, 김도겸, 신선혜)
* **담당 역할 (손석환):**
  * **PLC 파트:** TwinCAT 3 기반의 압력, 진동, 온도, 습도 센서 정보 스캔 로직 구현 및 HMI 연동 상태 판정 알고리즘 구축.
  * **WPF HMI 파트:** TwinCAT ADS 프로토콜을 사용한 실시간 변수 바인딩, 장비 및 시뮬레이션 상태 램프 연동. 가상 진공 이송 챔버(TM) 시뮬레이션 모듈 구현.
  * **AI/API 파트:** Flask 백엔드 서버 연동(REST API), 시뮬레이션 센서 스냅샷 수집 파이프라인 및 Scikit-Learn 분류 모델 재학습 스크립트 작성.
* **GitHub Repository:** [https://github.com/tjrghks0823456-rgb/etch-equipment-system-sw](https://github.com/tjrghks0823456-rgb/etch-equipment-system-sw)

---

## 🛠️ 사용 기술 및 개발 환경 (Tech Stack)
* **HMI / 제어:** C#, WPF, .NET Framework, Beckhoff TwinCAT 3 (ADS Protocol)
* **백엔드 / 데이터베이스:** Python, Flask, SQLite
* **AI / 머신러닝:** Scikit-Learn (Anomaly Detection & State Classifier), joblib
* **형설관리 및 도구:** Git, GitHub, Visual Studio 2022, PyCharm, PowerShell

---

## 💡 주요 기능 및 구현 내용
### 1. 실시간 센서 스캔 및 4단계 장비 상태 판정 (PLC)
* 압력 센서(SEN_PRESS), 진동 센서(SEN_VIB), 온습도 센서 및 Load Lock 접근 센서를 PLC가 ADS 인터페이스로 수집.
* 센서 임계치 및 상태 조합을 활용하여 **Ready(대기) / Run(운전) / Warning(경고) / Alarm(알람)**의 4단계 장비 상태를 자동 판정하고 경고/알람 발생 시 즉시 하드웨어 인터록 수행.

### 2. 가상 이송 챔버(TM) 시뮬레이션 및 WPF HMI 제어
* 가상 이송 모듈(`TmTransferSimulator.cs`)을 통해 3개 FOUP(LP1~3) ➡️ Aligner ➡️ Load Lock ➡️ PM2~4(Etch) ➡️ PM1(Strip) ➡️ Side Storage ➡️ 카세트 출하의 실시간 공정 시뮬레이션을 구현하고 이를 시각화.
* WPF 제어판에서 설비 운전 제어(Start, Stop, Reset, Maintenance) 기능 구현.

### 3. Flask 데이터 수집 및 머신러닝 기반 AI 고장 진단
* 이송 과정의 1Hz 센서 데이터 스냅샷(JSONL)을 수집하여 오프라인에서 의사결정나무(Decision Tree) 등 Scikit-Learn 분류기 모델을 학습.
* 학습된 모델(`joblib`)을 Flask 백엔드 서버에 서빙하여, WPF HMI 화면에 실시간으로 **AI 알람 고장 위험성 신뢰도(Confidence)** 및 예상 알람 코드를 제공.

### 4. 원격 모니터링 웹 대시보드
* 공장 외부 네트워크에서도 모바일/PC 브라우저를 통해 장비의 현재 모듈 상태, 액티브 레시피 정보, 과거 알람/이력 로그를 실시간 조회할 수 있는 대시보드 구축.
