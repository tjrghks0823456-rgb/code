# etch-equipment-control-simulator

> C# · WinForms · EtherCAT DLL 기반 반도체 식각 장비 HMI 개발 기록

## 1. 프로젝트 개요

EtherCAT 기반 외부 장비 제어 DLL(IEG3268_Dll.dll)을 연동하여 반도체 식각 장비용 HMI를 구축한 실습 프로젝트입니다.
레거시 수동 제어 단일 폼에서 출발하여, 하드웨어 추상화 계층·공정 시나리오·레시피 관리·로그 기록 구조를 단계적으로 분리하고 발전시키는 과정을 담고 있습니다.
수업 프로젝트로 진행되었으며, 실무 구조를 참고해 직접 설계해보는 것에 초점을 맞췄습니다.

## 2. 개발 배경

EtherCAT 기반 장비 제어 DLL을 C# WinForms 환경에서 연동하는 실습을 목표로 시작했습니다.
초기에는 단일 Form1 안에 모든 제어 코드가 뒤섞인 레거시 방식이었고, 이를 역할별 계층 구조(Hardware / Process / Data)로 분리·리팩토링하는 과정이 핵심 학습 내용이었습니다.

## 3. 폴더 구조 및 발전 과정

```
semitool-hmi/
├── 00-프로젝트문서/         # 구조 설명, 모듈 설명, 실행 가이드
├── 01-레거시_수동제어폼/    # 초기 단일 Form1 수동 제어 코드
├── 02-외부장비_DLL/         # EtherCAT 장비 제어 DLL (IEG3268_Dll.dll)
├── 03-HMI_애플리케이션/    # 실제 HMI 소스 (메인 프로젝트)
├── SemiToolHMI.sln
└── README.md
```

**03-HMI_애플리케이션/SemiToolHMI 내부 구조**

```
SemiToolHMI/
├── App/          # 프로그램 진입점
├── Forms/        # 사용자가 여는 화면 (FormMain 등)
├── Panels/       # 화면 내 장비·상태 패널
├── Hardware/     # EtherCAT, IO, 경광등, 장비 제어 계층
├── Process/      # 공정 시나리오, 스케줄러, 웨이퍼 흐름
├── Data/         # DB 초기화, 레시피 저장소, 템플릿
├── Models/       # 공정/레시피/웨이퍼 상태 모델
├── Logging/      # 로봇 동작 로그 기록
├── Legacy/       # 이전 방식 보관
└── Properties/
```

## 4. 주요 기능

- EtherCAT 외부 장비 DLL 연동 (IEG3268_Dll.dll)
- 레거시 수동 제어 → 계층 분리 HMI 구조로 발전
- 공정 시나리오 및 웨이퍼 흐름 처리
- 레시피 저장 및 DB 초기화
- 장비 동작 로그 기록
- 경광등(Tower Lamp) IO 제어

## 5. 기술 스택

| 구분 | 기술 |
|------|------|
| Language | C# |
| UI | WinForms (.NET) |
| 장비 통신 | EtherCAT DLL (IEG3268_Dll.dll) |
| 개발 환경 | Visual Studio 2022 |

## 6. 이 프로젝트와 etch-equipment-hmi의 차이

| 항목 | 이 프로젝트 (semitool-hmi) | etch-equipment-hmi |
|------|--------------------------|-----------------------------------------------------|
| 통신 방식 | EtherCAT DLL 직접 연동 | TwinCAT ADS 프로토콜 |
| UI 프레임워크 | WinForms | WPF |
| AI 연동 | 없음 | Flask + Scikit-Learn |
| 웹 대시보드 | 없음 | Flask 웹 서버 |
| 목적 | EtherCAT DLL 연동 실습 및 HMI 구조 학습 | 3계층 통합 HMI 시스템 구현 |

두 프로젝트는 같은 식각 장비 주제지만 접근 방식과 목적이 다릅니다.

## 7. 실행 방법

1. Visual Studio 2022에서 `SemiToolHMI.sln` 열기
2. `SemiToolHMI` 프로젝트를 시작 프로젝트로 설정
3. NuGet 패키지 복원
4. EtherCAT DLL이 `02-외부장비_DLL` 경로에 있는지 확인
5. 빌드 후 실행

> EtherCAT 실장비가 없으면 일부 기능이 제한될 수 있습니다.

## 8. 배운 점

- EtherCAT 기반 외부 장비 DLL을 C#에서 P/Invoke 또는 래퍼 클래스로 연동하는 방식
- 레거시 단일 폼 코드를 역할 기반 계층 구조(Hardware/Process/Data)로 분리하는 리팩토링 경험
- 공정 시나리오와 웨이퍼 이동 흐름을 코드로 표현하는 방법
- DB 기반 레시피 저장소 설계
