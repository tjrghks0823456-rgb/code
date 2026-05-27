# SemiToolHMI 소스 구조

이 폴더가 실제 Windows Forms 프로젝트입니다.

```text
SemiToolHMI/
├─ App/                 # Program.cs
├─ Forms/
│  ├─ Auth/             # LoginForm, UserManagementForm
│  ├─ DeviceControl/    # EtherCAT 수동 장비 제어 화면
│  ├─ Foup/             # FOUP 상세 화면
│  ├─ Main/             # MainForm
│  ├─ Monitoring/       # TransferMonitor, Verification, Log 화면
│  └─ Recipes/          # 레시피 선택/편집/스텝 입력 화면
├─ Panels/
│  ├─ Arm/
│  ├─ Chamber/
│  ├─ Foup/
│  └─ Robot/
├─ Hardware/            # EtherCAT/IO/StackLight 제어
├─ Process/             # 공정 순서와 시나리오
├─ Data/                # DB, Repository, LinqToDB 템플릿
├─ Models/              # 상태/레시피/웨이퍼 모델
├─ Logging/             # 로그 기록
├─ Legacy/              # 이전 구현 보관
├─ Properties/
└─ SemiToolHMI.csproj
```

`SemiToolHMI.csproj`의 파일 참조도 위 폴더 구조에 맞춰 반영되어 있습니다.