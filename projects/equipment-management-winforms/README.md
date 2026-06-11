# winforms-equipment-management-practice

> C# · WinForms · MySQL 기반 장비 대여/반납 관리 실습 프로젝트

## 1. 실습 목적

MySQL 데이터베이스와 연동하여 장비의 등록, 대여, 반납, 고장 처리, 이력 조회를 WinForms 앱에서 관리하는 흐름을 직접 구현해보는 실습 프로젝트입니다.

단순한 목록 조회를 넘어 `장비 선택 → 상태 변경 → 이력 기록 → 대시보드 반영` 흐름을 만들어보는 것이 목표였습니다.

## 2. 실습 내용

- 로그인 및 사용자 관리
- 장비 목록 조회, 검색, 신규 등록 및 삭제
- 장비 상태 색상 표시 (정상 / 대여중 / 고장)
- 장비 대여/반납 처리, 반납 예정일 관리
- 고장 신고, 수리 완료 처리
- 전체 이력 조회 및 기간별 검색
- 대시보드 상태 차트 및 관리자 일정 관리

## 3. 사용 기술

| 구분 | 기술 |
|------|------|
| Language | C# |
| UI | WinForms (.NET Framework 4.7.2) |
| Database | MySQL |
| 패키지 | MySql.Data (NuGet) |
| 아키텍처 | Repository 패턴 (UI와 DB 분리) |
| 개발 환경 | Visual Studio 2022 |

## 4. 주요 화면

| 화면 | 역할 |
|------|------|
| `LoginForm` | 사용자 로그인, 관리자 사용자 관리 |
| `Form1` | 왼쪽 메뉴 기반 메인 화면 전환 |
| `UC_Dashboard` | 장비 상태 차트, 관리자 일정 |
| `UC_EquipmentList` | 장비 목록, 검색, 등록/삭제 |
| `UC_Rental` | 대여, 반납, 반납 예정일 설정 |
| `UC_Fault` | 고장 신고, 수리 완료 처리 |
| `UC_History` | 이력 조회 |

## 5. 실행 방법

1. MySQL에서 `create_db.sql` 또는 `equipmentdb_*.sql`로 `equipmentdb` 데이터베이스 구성
2. `Repositories.cs`의 `DbManager.ConnectionString`을 로컬 MySQL 계정에 맞게 수정
3. Visual Studio에서 `WindowsFormsApp1.sln` 열기
4. NuGet 패키지 복원 후 실행
5. 기본 로그인: `admin` / `1234` (학습용)

> 참고: DB 접속 정보와 기본 계정은 학습용 설정입니다. 실제 배포 환경이라면 접속 정보를 환경 변수로 분리하고 비밀번호를 해시 처리하는 것이 좋습니다.

## 6. 배운 점

- Repository 패턴으로 UI와 DB 코드 분리
- WinForms UserControl 기반 화면 전환 구조
- MySQL 연동 CRUD 구현 (MySql.Data 라이브러리)
- 상태 전환 흐름 설계 (정상 → 대여중 → 고장 → 수리 완료)
