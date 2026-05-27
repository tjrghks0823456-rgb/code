# Equipment Management WinForms

반도체/실습 장비의 등록, 대여, 반납, 고장 처리, 이력 조회, 관리자 일정을 관리하는 C# Windows Forms 데스크톱 앱입니다.

단순한 목록 화면이 아니라 `장비 선택 -> 상태 변경 -> 이력 기록 -> 대시보드 반영` 흐름을 구현한 장비 관리 시스템입니다. MySQL 데이터베이스를 중심으로 장비 상태와 사용 이력을 관리하고, 각 화면은 `UserControl` 단위로 분리되어 있습니다.

## What It Solves

장비가 여러 명에게 대여되고 고장/수리 상태가 자주 바뀌면, 현재 사용 가능 여부와 책임자, 변경 이력을 한눈에 보기 어렵습니다. 이 프로젝트는 장비 목록, 대여 상태, 고장 신고, 수리 완료, 사용 이력을 하나의 WinForms 앱에서 관리하도록 만든 실습형 관리 도구입니다.

## Core Features

- 로그인 및 사용자 관리
- 장비 목록 조회, 검색, 신규 장비 등록
- 장비별 상태 색상 표시: 정상, 대여중, 고장
- 장비 종류별 스펙, 사용 가이드, 이미지 표시
- 장비 대여/반납 처리와 반납 예정일 관리
- 고장 신고, 수리 완료 처리와 수리 예정일 관리
- 전체 이력 조회 및 기간별 검색
- 대시보드 상태 차트와 관리자 근무 일정 관리

## Main Screens

| Screen | Purpose |
| --- | --- |
| `LoginForm` | 사용자 로그인과 관리자 사용자 관리 진입 |
| `Form1` | 왼쪽 메뉴 기반 메인 화면 전환 |
| `UC_Dashboard` | 장비 상태 통계 차트, 월간 관리자 일정 |
| `UC_EquipmentList` | 장비 목록, 검색, 상세 스펙/가이드, 신규 등록 |
| `UC_Rental` | 장비 대여, 반납, 반납 예정일 설정 |
| `UC_Fault` | 고장 신고, 수리 완료 처리 |
| `UC_History` | 대여/반납/고장/수리 이력 조회 |
| `UserManagementForm` | 관리자 계정의 사용자 추가/삭제 |

## Technical Notes

- UI와 DB 접근을 분리하기 위해 Repository 패턴을 사용했습니다.
- `EquipmentRepository`, `HistoryRepository`, `ScheduleRepository`, `UserRepository`가 MySQL 작업을 담당합니다.
- `Equipment`, `History`, `User` 모델이 화면 표시용 데이터 변환을 맡습니다.
- 주요 테이블은 `equipment`, `history`, `users`, `manager_schedule`입니다.

## Environment

- Visual Studio 2022
- .NET Framework 4.7.2
- C# Windows Forms
- MySQL
- `MySql.Data` NuGet package

## Run

1. MySQL에서 `create_db.sql` 또는 `equipmentdb_*.sql` 파일로 `equipmentdb` 데이터베이스를 준비합니다.
2. `Repositories.cs`의 `DbManager.ConnectionString` 값을 로컬 MySQL 계정에 맞게 수정합니다.
3. Visual Studio에서 `WindowsFormsApp1.sln`을 엽니다.
4. NuGet 패키지를 복원한 뒤 실행합니다.
5. 기본 관리자 계정은 `admin` / `1234`입니다.

## Portfolio Point

이 프로젝트는 WinForms 화면 구성뿐 아니라 DB 연동, 상태 전환, 이력 기록, 검색, 일정 관리까지 포함합니다. 그래서 단일 화면 실습보다 한 단계 더 나아간 "작은 업무용 관리 프로그램"으로 보여줄 수 있습니다.

> Note: 현재 DB 접속 정보와 기본 계정은 학습용 설정입니다. 실제 배포용이라면 접속 정보는 설정 파일이나 환경 변수로 분리하고, 비밀번호는 해시 처리하는 것이 좋습니다.
