# 실행 및 확인 가이드

## 1. 솔루션 열기

Visual Studio 2022에서 다음 파일을 엽니다.

```text
SemiToolHMI.sln
```

## 2. 빌드 환경

- 대상 프레임워크: .NET Framework 4.8
- 프로젝트 타입: Windows Forms
- 시작 프로젝트: `SemiToolHMI`
- 필수 DLL: `IEG3268_Dll.dll`

## 3. 빌드

Visual Studio에서 `빌드 > 솔루션 빌드`를 실행합니다.

명령줄에서 확인할 경우:

```powershell
MSBuild.exe SemiToolHMI.sln /t:Build /p:Configuration=Debug
```

## 4. 실행 전 확인사항

- EtherCAT 장비 또는 테스트 환경 연결 여부
- `IEG3268_Dll.dll`이 실행 파일과 같은 출력 경로에 복사되는지 확인
- 장비 연결 없이 실행할 경우 실제 IO 제어 버튼은 정상 동작하지 않을 수 있음
- 레시피 기능을 사용할 경우 데이터베이스 연결 및 초기화 상태 확인

## 5. 기본 확인 순서

1. 프로그램 실행
2. 로그인 또는 메인 화면 진입
3. EtherCAT 연결 상태 확인
4. Servo ON
5. 원점 복귀
6. 조그 이동 또는 목표 위치 이동 테스트
7. 챔버 도어/램프/진공 출력 테스트
8. 레시피 선택 후 공정 시나리오 실행
9. 이송 모니터와 로그 화면에서 상태 확인

## 6. 제출 시 확인 포인트

- GitHub에서 `03-장비제어/EtherCAT_Final2504110114손석환` 폴더를 열면 코드 파일이 바로 보여야 합니다.
- `README.md`에서 프로젝트 개요와 실행 방법을 확인할 수 있어야 합니다.
- `docs/MODULES.md`에서 각 파일의 역할을 확인할 수 있어야 합니다.

