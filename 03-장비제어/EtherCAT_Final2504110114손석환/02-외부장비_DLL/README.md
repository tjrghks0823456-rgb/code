# 외부 장비 DLL

EtherCAT 장비 제어에 필요한 외부 DLL을 보관하는 폴더입니다.

## 파일

- `IEG3268_Dll.dll`: EtherCAT 보드 및 장비 입출력 제어용 라이브러리

`SemiToolHMI.csproj`는 이 DLL을 참조하도록 설정되어 있습니다. 실제 장비 환경에서는 DLL 버전과 장비 드라이버 설치 상태를 함께 확인해야 합니다.

