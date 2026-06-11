# 🖥️ PLC · WPF · Flask 기반 반도체 식각 장비 상태 관리 HMI 시스템
> **반도체 장비 소프트웨어 개발 프로젝트**  
> 실장비(PLC) 센서 수집 및 제어, WPF HMI 모니터링/시뮬레이션, Flask 웹 대시보드 및 AI 고장 진단 시스템이 유기적으로 통합된 반도체 식각 장비 SW 솔루션입니다.

---

## 🛠️ 시스템 개요 (System Overview)
본 프로젝트는 실제 산업현장의 플라즈마 식각 장비(Plasma Etcher) 공정을 모사하여, **"센서 데이터 수집(PLC) ➡️ 장비 제어 및 가상 이송 시뮬레이션(WPF) ➡️ 원격 모니터링 및 AI 예측 정비(Flask & ML)"**의 3계층 아키텍처로 구현되었습니다.

```
                    [ 3계층 시스템 구성도 ]
   
    TwinCAT PLC  ◀───(ADS Protocol)───▶  WPF HMI (C#)
    (실장비/센서/IO)                       │ (실시간 제어/시뮬레이션)
                                           │
                                         (HTTP / REST API)
                                           ▼
                                    Flask 서버 (Python)
                                     ├─ SQLite Database (이력 로그)
                                     └─ Scikit-Learn (AI 고장 진단 엔진)
                                           ▲
                                           │ (Web Page)
                                           ▼
                                    웹 대시보드 (원격 조회)
```

### 1. 계층별 역할 및 기능
- **PLC 계층 (TwinCAT 3):**
  - 압력, 진동, 온습도, Load Lock 도어 접촉 센서 등 물리 센서 값과 버튼 입력을 스캔합니다.
  - Ready/Run/Warning/Alarm 상태 판정 및 램프 출력을 제어하고, 안전을 위한 하드웨어 인터록을 수행합니다.
- **WPF HMI 계층 (C# / .NET / ADS):**
  - PLC와 실시간 ADS 통신을 통해 센서 및 장비 상태를 동기화하고 조작 명령(Start, Stop, Reset 등)을 하달합니다.
  - 가상 웨이퍼 이송 모듈(`TmTransferSimulator.cs`)을 탑재하여 3개의 FOUP, Aligner, Load Lock, 4개의 PM(챔버) 사이의 가상 이송 과정을 시각적으로 보여줍니다.
  - Flask 백엔드에서 추론된 AI 고장 예측 정보(신뢰도 및 예상 알람 코드)를 화면에 실시간으로 표시(조언 패널)합니다.
- **Flask & AI 계층 (Python / SQLite / Scikit-Learn):**
  - WPF로부터 실시간으로 전송되는 장비 텔레메트리 데이터를 수집하여 SQLite DB에 저장합니다.
  - 수집된 가상 이송 센서 스냅샷 데이터(JSONL)를 통해 오프라인 기계학습(Scikit-Learn Classifier)을 수행하고 고장 예측 모델(`joblib`)을 서빙합니다.
  - 원격 모니터링 웹 대시보드를 제공하여 외부에서도 모듈 상태, 공정 이력, 현재 진행 중인 레시피 상태를 한눈에 볼 수 있도록 합니다.

---

## 📊 PLC 입출력 및 태그 매핑 (Hardware I/O Mapping)

| 구분 | 신호명 | 변수명/태그 | 물리 주소 (예시) | 설명 |
|------|------|------|------|------|
| **입력 (DI)** | Start 버튼 | `BTN_START` | %IX0.0 | 설비 가동 시작 요청 |
| **입력 (DI)** | Stop 버튼 | `BTN_STOP` | %IX0.1 | 설비 비상 정지 요청 |
| **입력 (DI)** | Reset 버튼 | `BTN_RESET` | %IX0.2 | 알람 해제 및 Ready 상태 복귀 |
| **입력 (DI)** | Maintenance 버튼 | `BTN_MAINT` | %IX0.3 | 장비 수동 유지보수 모드 진입 |
| **입력 (DI)** | Load Lock 접촉 | `SEN_ACCESS` | %IX0.5 | Load Lock 도어 안착 확인 센서 (인터록 대상) |
| **입력 (AI)** | 압력 센서 | `SEN_PRESS` | %IW0 | Chamber / Load Lock 압력 값 |
| **입력 (AI)** | 진동 센서 | `SEN_VIB` | %IW2 | 진공 펌프 및 TM 모터 진동 계측 |
| **입력 (AI)** | 온도 센서 | `SEN_TEMP` | %IW4 | 챔버 내부 및 설비 환경 온도 |
| **입력 (AI)** | 습도 센서 | `SEN_HUMI` | %IW6 | 설비 대기 중 습도 계측 |
| **출력 (DO)** | Ready 램프 | `LAMP_READY` | %QX0.0 | 운전 대기 상태 표시 |
| **출력 (DO)** | Run 램프 | `LAMP_RUN` | %QX0.1 | 정상 운전 중 상태 표시 |
| **출력 (DO)** | Warning 램프 | `LAMP_WARN` | %QX0.2 | 이상 징후 감지 시 경고 표시 (2% 경고 시뮬레이션 포함) |
| **출력 (DO)** | Alarm 램프 | `LAMP_ALARM` | %QX0.3 | 인터록 트립 및 장비 정지 상태 표시 |

---

## 📂 프로젝트 구조 (Repository Directory Structure)
```
etch-equipment-system-sw/
├── README.md                     # 프로젝트 총괄 설명서 (본 파일)
├── .gitignore                    # C# & Python 빌드/임시 파일 예외 설정
├── etch_ui/                      # WPF HMI 제어 프로그램 (C#)
│   ├── etch_ui.sln               # Visual Studio 솔루션 파일
│   └── etch_ui/
│       ├── MainWindow.xaml       # HMI UI 레이아웃 설계
│       ├── MainWindow.xaml.cs    # UI 제어 로직, ADS 통신 및 Flask 연동
│       ├── AppSettings.cs        # 설비 설정 파서
│       ├── Services/             
│       │   ├── PlcAdsService.cs  # Beckhoff ADS API 연동 모듈
│       │   └── Simulation/       
│       │       └── TmTransferSimulator.cs # 가상 진공 이송 챔버(TM) 시뮬레이터
│       └── tools/ai/             # AI 학습 및 오프라인 파이프라인
│           ├── train_from_sim.ps1 # 시뮬레이터 로그 분석 및 모델 자동 재학습 스크립트
│           └── train_sklearn.py  # Scikit-Learn 모델 학습 알고리즘
└── etchflask/                    # API 서버 및 AI 모니터링 시스템 (Python)
    ├── app.py                    # Flask 엔트리포인트 및 REST API 라우터
    ├── etch_model.py             # Scikit-Learn 분류 모델 로더 및 추론 인터페이스
    ├── data_manager.py           # 텔레메트리 센서 데이터 처리 및 DB 적재
    ├── etch_persistence.py       # SQLite 이벤트/알람 이력 데이터베이스 레이어
    ├── templates/                # 대시보드 웹 템플릿
    └── requirements.txt          # Python 필수 라이브러리 목록
```

---

## 🚀 시작하기 (Getting Started)

### 1. Flask 서버 구동 및 AI 모델 배포
1. `etchflask` 디렉터리로 이동하여 필요 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
2. Flask 서버를 구동합니다.
   ```bash
   run_flask.bat
   ```
   *서버는 기본적으로 `http://localhost:5000` 포트에서 실행되며 실시간 원격 대시보드를 제공합니다.*

### 2. WPF HMI 실행
1. `etch_ui/etch_ui.sln` 파일을 Visual Studio에서 엽니다.
2. `appsettings.json` 설정 파일에서 TwinCAT ADS NetID와 Port(기본 851)를 로컬 PLC 환경에 맞춰 변경합니다. (PLC 연결 없이 실행하려면 `SimulationEnabled: true` 설정)
3. 솔루션을 빌드(F5)하고 실행합니다.
4. 기본 관리자 계정(`admin` / `Admin1234`)으로 로그인하여 이송 시뮬레이션 가동 및 제어 인터페이스를 테스트합니다.

---

## 👥 팀원 및 역할 (Contributors)
- **손석환 (tjrghks0823456-rgb):** PLC 입출력 수집 로직 및 상태 판정 알고리즘 개발, WPF HMI 통신 브릿지 및 장비 도식 상태 UI 개발.
- **김도겸 / 신선혜:** 플라즈마 식각 공정 시나리오 수립, PPT 발표 문서 작성 및 데이터베이스 연동 테스트.
