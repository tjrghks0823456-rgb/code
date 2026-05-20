# 모듈 설명

## Controls

화면에서 재사용되는 패널과 공정 시나리오 UI를 담당합니다.

| 파일 | 역할 |
| --- | --- |
| `ArmPanel.cs` | 이송 로봇 암의 각도와 웨이퍼 보유 상태를 표시 |
| `ChamberPanel.cs` | 챔버 도어, 웨이퍼 존재 여부, 공정 상태 표시 |
| `ChamberDetailForm.cs` | 챔버별 레시피, 스텝, 시간, PV/SV 표시 |
| `ChamberStatusPanel.cs` | 챔버 상태 요약 패널 |
| `EquipmentStatusPanel.cs` | FOUP 웨이퍼 수량과 잠금 상태 표시 |
| `FOUPPanel.cs` | FOUP 슬롯과 웨이퍼 상태 표시 |
| `RobotScenario.cs` | 실제 로봇 동작 시나리오와 안전 조건 처리 |
| `TransferMonitorForm.cs` | 웨이퍼 위치와 TM 작업 상태 모니터링 |

## Data

레시피와 데이터베이스 관련 기능입니다.

| 파일 | 역할 |
| --- | --- |
| `DatabaseInitializer.cs` | 데이터베이스와 기본 테이블 생성 |
| `RecipeRepository.cs` | 레시피 저장, 조회, 수정, 삭제 |
| `RecipeEditorForm.cs` | 레시피 생성 및 수정 UI |
| `StepEditForm.cs` | 개별 레시피 스텝 수정 UI |

## Logic

공정 순서와 런타임 동작을 담당합니다.

| 파일 | 역할 |
| --- | --- |
| `ChamberRuntime.cs` | 챔버별 레시피 실행 시간과 스텝 진행 관리 |
| `ProcessSequence.cs` | 기본 공정 시퀀스 정의 |
| `ChamberProcessSequence.cs` | 챔버 공정 단위 흐름 정의 |
| `TmScheduler.cs` | 웨이퍼 이동 단계 스케줄링 |
| `WaferPipelineSimulator.cs` | FOUP A → A/B/C 챔버 → FOUP B 파이프라인 시뮬레이션 |

## System

하드웨어 제어와 IO 매핑입니다.

| 파일 | 역할 |
| --- | --- |
| `EthercatController.cs` | EtherCAT 연결과 제어 객체 관리 |
| `ChamberIo.cs` | 챔버 도어/램프 제어 |
| `IoMap.cs` | 디지털 입력/출력 번호 매핑 |
| `StackLightIo.cs` | 경광등 제어 |
| `WaferProcessScenario.cs` | 웨이퍼 공정 시나리오 보조 로직 |

## Monitor

공정 검증과 이송 상태 확인 화면입니다.

| 파일 | 역할 |
| --- | --- |
| `TransferMonitorForm.cs` | 이송 상태 표 형태 확인 |
| `VerificationForm.cs` | LOT 진행과 완료 상태 검증 |

## Log

장비 동작 로그와 로봇 디버그 화면입니다.

| 파일 | 역할 |
| --- | --- |
| `RobotLog.cs` | 로봇 시나리오 로그 기록 |
| `RobotLogicForm.cs` | 로봇 로직 및 디버그 로그 확인 |

