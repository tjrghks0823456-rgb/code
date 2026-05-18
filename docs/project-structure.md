# 프로젝트 구조 기준

이 문서는 과목별 프로젝트가 생겼을 때 어느 폴더에 정리할지 판단하는 기준입니다.

## 분류표

| 분류 | 주요 내용 | 관련 과목 |
|---|---|---|
| 01-programming-basic | 기초 코딩, Python 문법, 알고리즘 | 프로그래밍실습, AI프로그래밍기초 |
| 02-ai-programming | AI 모델, 머신러닝, 이상 탐지 | AI소프트웨어 활용 및 코딩, AI제어실습, AI프로그램심화 |
| 03-equipment-control | 장비 제어, 센서 제어, 로봇 제어 | 장비제어기초, 장비제어심화, 장비제어알고리즘, 장비로봇제어 |
| 04-data-analysis | 데이터 분석, 시각화, 빅데이터 | 빅데이터분석기초, 빅데이터활용 |
| 05-system-network | 운영체제, 통신, IoT, 시스템 설계 | 운영체제, 시스템분석및설계, 장비통신SW개발, 장비IoT센서제어 |
| 06-gui-frontend | GUI, 웹 화면, 대시보드 | 장비GUI제어, 프로그램실습 |
| 07-cloud-operation | 배포, 서버 운영, 클라우드 | 클라우드운영실습 |
| 08-quality-management | 테스트, 품질관리, 코드 리뷰 | 장비제어SW품질관리 |
| 09-semiconductor-process | 반도체 공정, 장비 이론 | 반도체제조공정, 반도체기초, 반도체장비개론 |

## 프로젝트 추가 규칙

새 프로젝트가 생기면 다음 기준으로 폴더를 만듭니다.

```text
분류폴더/
└─ project-name/
   ├─ README.md
   ├─ src/
   └─ tests/
```

데이터 분석 프로젝트처럼 데이터와 노트북이 필요한 경우에는 다음 구조를 사용할 수 있습니다.

```text
분류폴더/
└─ project-name/
   ├─ README.md
   ├─ data/
   ├─ notebooks/
   └─ src/
```

## 이름 작성 기준

- 폴더 이름은 영어 소문자와 하이픈을 사용합니다.
- 과목명보다 프로젝트 내용을 기준으로 이름을 정합니다.
- 예: `sensor-log-analysis`, `motor-control-basic`, `equipment-dashboard`

## README 작성 기준

각 프로젝트 폴더에는 `README.md`를 두고 다음 내용을 적습니다.

- 프로젝트 목적
- 사용 기술
- 실행 방법
- 주요 기능
- 배운 점
