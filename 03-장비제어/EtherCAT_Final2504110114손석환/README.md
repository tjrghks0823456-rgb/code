# EtherCAT 반도체 장비 제어 HMI

EtherCAT 기반 반도체 장비 제어를 위한 Windows Forms HMI 프로젝트입니다. 이송 로봇, FOUP, 챔버, 도어, 진공, 램프, 경광등 상태를 화면에서 제어하고 공정 시나리오 흐름을 확인할 수 있도록 구성했습니다.

## 주요 기능

- EtherCAT 장비 연결 상태 확인
- 이송 로봇 상하/좌우 축 제어
- 서보 ON/OFF, 원점 복귀, 조그 이동, 목표 위치 이동
- A/B/C 챔버 도어 및 램프 제어
- 웨이퍼 진공 흡기/배기 제어
- FOUP A에서 챔버 A/B/C를 거쳐 FOUP B로 이동하는 공정 시나리오
- 레시피 생성, 수정, 선택, 챔버별 적용
- 공정 진행 상태 및 이송 모니터링
- 사용자 로그인 및 사용자 관리 화면
- 로봇 동작 로그와 디버그 화면

## 프로젝트 구조

```text
EtherCAT_Final2504110114손석환
├─ SemiToolHMI.sln
├─ IEG3268_Dll.dll
├─ Form1.cs
├─ SemiToolHMI
│  ├─ Controls
│  ├─ Data
│  ├─ Log
│  ├─ Logic
│  ├─ Models
│  ├─ Monitor
│  ├─ System
│  ├─ DeviceControlForm.cs
│  ├─ MainForm.cs
│  └─ Program.cs
└─ docs
   ├─ ARCHITECTURE.md
   ├─ MODULES.md
   └─ RUN_GUIDE.md
```

## 주요 화면

- `MainForm`: 전체 HMI 메인 화면
- `DeviceControlForm`: EtherCAT 기반 장비 수동 제어 화면
- `RecipeEditorForm`: 레시피 생성 및 수정 화면
- `RecipeSelectForm`: 챔버별 레시피 선택 화면
- `TransferMonitorForm`: 웨이퍼 이송 위치와 TM 작업 상태 모니터링
- `UserManagementForm`: 사용자 계정 관리

## 개발 환경

- Visual Studio 2022
- C# Windows Forms
- .NET Framework 4.8
- EtherCAT 장비 제어 DLL: `IEG3268_Dll.dll`

## 실행 방법

1. Visual Studio 2022에서 `SemiToolHMI.sln`을 엽니다.
2. NuGet 패키지 복원을 확인합니다.
3. `SemiToolHMI` 프로젝트를 시작 프로젝트로 설정합니다.
4. Debug 또는 Release 구성으로 빌드합니다.
5. 장비 연결이 필요한 기능은 EtherCAT 보드와 제어 DLL이 정상 연결된 환경에서 실행합니다.

자세한 실행 방법은 [docs/RUN_GUIDE.md](docs/RUN_GUIDE.md)를 참고하세요.

