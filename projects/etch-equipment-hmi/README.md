# semiconductor-etch-hmi-system

> C# · WPF · PLC · Flask · AI 기반 반도체 식각 장비 상태 관리 HMI 시스템

## 1. 프로젝트 개요

TwinCAT PLC ADS 통신으로 실장비 센서 데이터를 수집하고, WPF HMI에서 실시간 상태 관리 및 가상 웨이퍼 이송 흐름을 시뮬레이션하며, Flask Python 서버가 이력 데이터를 SQLite에 저장하고 Scikit-Learn 기반 AI 고장 예측 모델을 서빙하는 3계층 구조의 반도체 식각 장비 HMI 시스템이다.
PLC Layer → WPF HMI Layer → Flask + AI Layer로 이어지는 계층 구조를 통해 장비 제어, 상태 감시, 이력 관리, 이상 예측을 통합적으로 처리한다.
대학 수업 프로젝트로 진행한 장비 제어 SW 개발 결과물로, 반도체 장비 PC 제어 소프트웨어의 전반적인 흐름을 직접 구현해본 것이 핵심 목적이다.

## 2. 개발 배경

반도체 장비 PC 제어 소프트웨어 개발자를 목표로, 실제 장비 제어 흐름을 이해하기 위해 진행한 프로젝트이다.
PLC와 HMI 간 ADS 통신 구조, 장비 상태 머신 설계, 레시피 관리, 알람/로그 처리를 직접 구현해보는 것이 목표였다.
Flask 백엔드와 Scikit-Learn AI 모델을 연동하여 이력 기반 고장 예측 기능까지 포함하는 범위로 확장하였다.
실제 반도체 클린룸 장비 수준의 완성도를 목표로 한 것은 아니며, 제어 SW의 기본 구조와 통신 흐름 학습에 초점을 두었다.

## 3. 시스템 구조

```
[ 3계층 아키텍처 ]

TwinCAT PLC ◀───ADS Protocol───▶ WPF HMI (C#)
(센서 입력 / IO 제어)              │ 실시간 제어 · 시뮬레이션
                                   │
                                 HTTP / REST API
                                   ▼
                             Flask 서버 (Python)
                              ├─ SQLite DB (이력 로그)
                              └─ Scikit-Learn (고장 예측)
                                   ▲
                               Web Dashboard
```

## 4. 주요 기능

**WPF HMI (C# / .NET)**
- PLC와 실시간 ADS 통신: 센서값·상태 동기화, Start/Stop/Reset 명령 전달
- 가상 웨이퍼 이송 시뮬레이션: FOUP 3개, Aligner, Load Lock, PM(챔버) 4개 간 이송 흐름 시각화 (`TmTransferSimulator.cs`)
- AI 고장 예측 패널: Flask에서 추론된 예측 결과(신뢰도 · 예상 알람 코드) 실시간 표시
- 장비 상태 전환: Ready → Run → Warning → Alarm 상태 머신 구현

**Flask + AI (Python)**
- WPF로부터 실시간 텔레메트리 데이터 수신 및 SQLite 저장
- Scikit-Learn 분류 모델(joblib) 기반 고장 예측 서빙
- 원격 모니터링 웹 대시보드 제공

**PLC (TwinCAT 3)**
- 압력/진동/온도/습도 센서 스캔
- Ready/Run/Warning/Alarm 상태 판정 및 램프 출력
- Load Lock 도어 인터록 처리

## 5. PLC 입출력 매핑

| 구분 | 신호명 | 변수명 | 설명 |
|------|--------|--------|------|
| 입력 DI | Start 버튼 | BTN_START | 장비 가동 시작 |
| 입력 DI | Stop 버튼 | BTN_STOP | 비상 정지 |
| 입력 DI | Reset 버튼 | BTN_RESET | 알람 해제 |
| 입력 DI | Maintenance 버튼 | BTN_MAINT | 유지보수 모드 진입 |
| 입력 DI | Load Lock 접촉 | SEN_ACCESS | 도어 안착 인터록 |
| 입력 AI | 압력 센서 | SEN_PRESS | Chamber / Load Lock 압력 |
| 입력 AI | 진동 센서 | SEN_VIB | 진공 펌프 진동 계측 |
| 입력 AI | 온도 센서 | SEN_TEMP | 챔버 내부 온도 |
| 입력 AI | 습도 센서 | SEN_HUMI | 환경 습도 |
| 출력 DO | Ready 램프 | LAMP_READY | 대기 상태 |
| 출력 DO | Run 램프 | LAMP_RUN | 운전 중 |
| 출력 DO | Warning 램프 | LAMP_WARN | 이상 징후 |
| 출력 DO | Alarm 램프 | LAMP_ALARM | 정지 상태 |

## 6. 기술 스택

| 구분 | 기술 |
|------|------|
| Language | C#, Python |
| UI / HMI | WPF (.NET) |
| PLC 통신 | TwinCAT ADS Protocol |
| Backend | Flask (Python) |
| Database | SQLite |
| AI / ML | Scikit-Learn, joblib |
| 개발 환경 | Visual Studio 2022, TwinCAT 3, Python 3.x |

## 7. 폴더 구조

```
etch-equipment-hmi/
├── README.md
├── .gitignore
├── etch_ui/                      # WPF HMI (C#)
│   ├── etch_ui.sln
│   └── etch_ui/
│       ├── MainWindow.xaml       # HMI UI 레이아웃
│       ├── MainWindow.xaml.cs    # UI 제어 로직 · ADS 통신
│       ├── AppSettings.cs        # 설비 설정 파서
│       ├── Services/
│       │   ├── PlcAdsService.cs  # Beckhoff ADS 연동
│       │   └── Simulation/
│       │       └── TmTransferSimulator.cs  # 가상 이송 시뮬레이터
│       └── tools/ai/
│           ├── train_from_sim.ps1  # 모델 재학습 스크립트
│           └── train_sklearn.py    # Scikit-Learn 학습
└── etchflask/                    # Flask 서버 (Python)
    ├── app.py
    ├── data_manager.py
    └── etch_ai.py
```

## 8. 핵심 구현 흐름

**장비 상태 전환 흐름**
1. TwinCAT PLC가 센서값(압력·진동·온도·습도)을 스캔
2. 인터록 조건(Load Lock 도어 접촉) 확인 후 상태 판정
3. WPF HMI가 ADS 통신으로 상태·센서값 실시간 동기화
4. HMI 화면에 Ready/Run/Warning/Alarm 상태 램프 표시
5. 사용자 명령(Start/Stop/Reset)을 PLC로 하달
6. 장비 텔레메트리를 Flask REST API로 전송
7. Flask가 SQLite에 이력 저장 + ML 모델로 고장 예측
8. HMI 화면에 AI 예측 결과(예상 알람 코드·신뢰도) 표시

## 9. 실행 화면

추후 스크린샷 추가 예정

## 10. 트러블슈팅 및 배운 점

**배운 점**
- TwinCAT ADS 프로토콜을 통한 PLC와 PC SW 간 실시간 통신 구조 이해
- WPF MVVM 패턴에서 PLC 상태 동기화 및 UI 바인딩 흐름
- 장비 상태 머신(Ready → Run → Warning → Alarm) 전환 로직 설계
- Flask REST API와 C# HttpClient 간 비동기 데이터 교환
- Scikit-Learn 분류 모델을 Flask로 서빙하는 기본 구조

**트러블슈팅**
- ADS 통신 연결 실패 시: TwinCAT ADS 라우터 실행 여부 및 AMS NetId 설정 확인 필요
- Flask 서버 미실행 시: WPF에서 HTTP 연결 예외 처리로 오프라인 모드 전환

## 11. 실행 방법

**WPF HMI**
1. Visual Studio 2022에서 `etch_ui/etch_ui.sln` 열기
2. TwinCAT 3 ADS 라우터 실행 확인
3. `AppSettings.cs`에서 AMS NetId 설정
4. 빌드 후 실행

**Flask 서버**
```bash
cd etchflask
pip install flask flask-cors scikit-learn joblib
python app.py
```

> 참고: TwinCAT PLC 없이 WPF 시뮬레이션 모드로도 동작 가능
