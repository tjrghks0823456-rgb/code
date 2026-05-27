# Code Portfolio

반도체 장비 제어, AI, 데이터, GUI, 시스템 통신 수업과 개인 프로젝트를 정리한 포트폴리오 저장소입니다.

이 저장소는 과목명을 첫 기준으로 두기보다, GitHub에서 바로 확인하기 좋은 **프로젝트 중심 구조**를 사용합니다. 과목 정보는 각 프로젝트 README와 `coursework/`에 보조 정보로 남깁니다.

## Structure

```text
code/
├─ projects/       # 완성 프로젝트와 포트폴리오로 보여줄 앱
├─ coursework/     # 과목별 실습, 예제, 빈 분류 자리
├─ shared/         # 여러 프로젝트에서 공통으로 쓸 자료
├─ docs/           # 저장소 운영/구조 문서
└─ README.md
```

## Projects

| Project | Summary | Main Stack | Related Area |
| --- | --- | --- | --- |
| [course-registration-system](projects/course-registration-system/) | 학생, 교수, 과목 모델을 사용한 수강신청 시스템 | C# | Programming Basics |
| [emotion-music-recommendation](projects/emotion-music-recommendation/) | 감정 기반 음악 추천 Flask 앱과 발표 자료 | Python, Flask, MySQL | AI Programming |
| [semitool-hmi](projects/semitool-hmi/) | 반도체 장비 HMI, EtherCAT 제어, 공정 시나리오 통합 프로젝트 | C#, WinForms, EtherCAT | Equipment Control |
| [flask-csharp-integration](projects/flask-csharp-integration/) | Flask 백엔드와 C# 클라이언트를 연동한 모니터링 시스템 | Python, Flask, C# | System Communication |
| [equipment-management-winforms](projects/equipment-management-winforms/) | MySQL 기반 장비 등록/삭제, 대여/반납, 고장 처리, 이력 조회, 관리자 일정 관리 WinForms 앱 | C#, WinForms, MySQL | GUI |
| [winforms-gui-portfolio](projects/winforms-gui-portfolio/) | 로그인, 숫자 맞추기, 계산기, Todo로 WinForms 이벤트/UI 패턴을 연습한 런처형 앱 | C#, WinForms | GUI |

## Coursework

| Folder | Purpose |
| --- | --- |
| [programming-basics](coursework/programming-basics/) | 프로그래밍 기초 실습 분류 |
| [ai-programming](coursework/ai-programming/) | AI 프로그래밍 실습 분류 |
| [equipment-control](coursework/equipment-control/) | 장비 제어 실습 분류 |
| [data-analysis](coursework/data-analysis/) | 데이터 분석 실습 분류 |
| [system-communication](coursework/system-communication/) | 시스템 통신 실습과 TCP 예제 |
| [gui-apps](coursework/gui-apps/) | GUI 화면 실습 분류 |
| [cloud-operations](coursework/cloud-operations/) | 클라우드 운영 실습 분류 |
| [quality-control](coursework/quality-control/) | 품질관리 실습 분류 |
| [semiconductor-process](coursework/semiconductor-process/) | 반도체 공정 이론/실습 분류 |

## Repository Rules

- 완성도가 있는 앱은 `projects/` 아래에 둡니다.
- 과목 실습이나 작은 예제는 `coursework/` 아래에 둡니다.
- 과목명은 프로젝트 폴더명보다 README의 메타 정보로 남깁니다.
- `bin/`, `obj/`, `.vs/`, 개인 설정 파일, 실행 파일, 로그 파일은 새로 커밋하지 않습니다.
- 장비 DLL, DB zip, 발표 자료처럼 재배포 여부가 애매한 바이너리는 가능하면 README로 위치만 설명하고 원본은 로컬에 보관합니다.
