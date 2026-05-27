# Project Structure Guide

이 저장소는 GitHub에서 보는 사람이 먼저 프로젝트를 이해할 수 있도록 프로젝트 중심으로 정리합니다.

## Top-Level Folders

```text
code/
├─ projects/
├─ coursework/
├─ shared/
├─ docs/
└─ README.md
```

## Classification Rules

| Target | Put Here |
| --- | --- |
| `projects/` | 실행 가능한 앱, 발표 가능한 결과물, 포트폴리오로 보여줄 프로젝트 |
| `coursework/` | 수업 실습, 작은 예제, 과목별 보관 자료 |
| `shared/` | 여러 프로젝트에서 공통으로 쓰는 자료 |
| `docs/` | 저장소 운영 문서, 구조 기준, 정리 기록 |

## Naming Rules

- 폴더명은 영어 소문자와 하이픈을 사용합니다.
- 프로젝트 이름은 기술이나 기능이 드러나게 작성합니다.
- 과목명과 학번은 폴더명보다 README에 보조 정보로 적습니다.

## Promotion Rule

수업 실습이 다음 조건을 만족하면 `coursework/`에서 `projects/`로 옮깁니다.

- 별도 README가 있음
- 실행 방법이 정리되어 있음
- 주요 기능이 한 문장으로 설명 가능함
- 소스, 문서, 실행 준비물이 한 폴더 안에 모여 있음
