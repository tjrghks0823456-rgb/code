# 식각 WPF UI

식각 장비 상태를 표시하고 Flask 대시보드로 장비/센서 데이터를 전송하는 WPF 클라이언트입니다.

## 실행

Visual Studio에서 `etch_ui.sln`을 열고 복원 후 실행합니다.

## 주요 파일

- `MainWindow.xaml`, `MainWindow.xaml.cs`: 메인 HMI 화면
- `ViewModels/MainViewModel.cs`: 화면 상태와 장비 데이터 바인딩
- `Plc/`: ADS PLC 통신과 아날로그 스케일링
- `Services/EtchFlaskClient.cs`: Flask 서버 연동
- `Security/`: 사용자 로그인, 계정 관리, 비밀번호 해시 처리
- `appsettings.json`: Flask 주소, ADS 포트, 인터록 기준값

## 제외한 파일

`.vs`, `bin`, `obj`, `*.user` 같은 개인 IDE 설정과 빌드 산출물은 GitHub 업로드 대상에서 제외했습니다.
