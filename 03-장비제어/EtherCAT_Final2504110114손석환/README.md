# EtherCAT 장비 제어 프로젝트

반도체 장비 HMI와 EtherCAT 기반 IO/모션 제어 코드를 기능별로 정리한 프로젝트입니다.

## 폴더 구조

```text
EtherCAT_Final2504110114손석환/
├─ 00-프로젝트문서/              # 구조 설명, 모듈 설명, 실행 가이드
├─ 01-레거시_수동제어폼/         # 최초 단일 Form1 수동 제어 코드
├─ 02-외부장비_DLL/              # EtherCAT 장비 제어 DLL
├─ 03-HMI_애플리케이션/          # 실제 HMI 애플리케이션 소스
├─ README.md
└─ SemiToolHMI.sln
```

## 핵심 위치

- 실제 실행 프로젝트: `03-HMI_애플리케이션/SemiToolHMI`
- 솔루션 파일: `SemiToolHMI.sln`
- 장비 제어 DLL: `02-외부장비_DLL/IEG3268_Dll.dll`
- 프로젝트 설명 문서: `00-프로젝트문서`

## HMI 코드 분류

`03-HMI_애플리케이션/SemiToolHMI` 안쪽 코드는 다음 기준으로 정리했습니다.

```text
SemiToolHMI/
├─ App/          # 프로그램 진입점
├─ Forms/        # 사용자가 직접 여는 화면
├─ Panels/       # 화면 안에 붙는 장비/상태 패널
├─ Hardware/     # EtherCAT, IO, 경광등, 장비 제어 계층
├─ Process/      # 공정 시나리오, 스케줄러, 웨이퍼 흐름
├─ Data/         # DB 초기화, 레시피 저장소, 템플릿
├─ Models/       # 공정/레시피/웨이퍼 상태 모델
├─ Logging/      # 로봇 로그 기록
├─ Legacy/       # 이전 방식의 보관 코드
├─ Properties/   # 리소스와 설정
└─ SemiToolHMI.csproj
```

## 실행 방법

Visual Studio에서 `SemiToolHMI.sln`을 열고 `SemiToolHMI` 프로젝트를 빌드하면 됩니다. NuGet 패키지 복원이 필요할 수 있으며, EtherCAT DLL은 `02-외부장비_DLL` 경로를 참조합니다.