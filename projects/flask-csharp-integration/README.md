# smart-logistics-plc-system

> Flask · C# WinForms · REST API 기반 실시간 센서 모니터링 및 가상 장비 제어 시스템

## 1. 프로젝트 개요

Flask 웹 서버와 C# WinForms 클라이언트 간 REST API 통신을 구현하여, 가상 반도체 장비의 센서 데이터를 실시간으로 모니터링하고 원격 제어 시나리오를 처리하는 시스템입니다.

C# 클라이언트가 전력·온도·습도·진동 등의 센서값을 Flask 서버로 주기적으로 전송하고, 웹 대시보드에서 실시간 차트와 제어 버튼으로 장비 상태를 확인하고 조작할 수 있습니다.

수업 프로젝트로 진행한 Flask-C# 연동 실습입니다. 실제 PLC 연동은 아니며, C# 클라이언트가 가상의 센서 역할을 합니다.

## 2. 개발 배경

Flask 백엔드와 C# 클라이언트 간 HTTP REST 통신 구조를 직접 구현해보고, 센서 데이터 흐름과 시나리오 기반 상태 제어 로직을 경험하기 위해 진행한 프로젝트입니다.

## 3. 시스템 구조

```
[C# WinForms 클라이언트]     [Flask 백엔드]          [웹 대시보드]
  가상 센서값 생성        ──→  REST API 처리    ←──   실시간 폴링
  HTTP POST 전송              SQLite/JSON 저장       차트 시각화
  제어 명령 수신         ←──  시나리오 State Machine   원격 제어 UI
```

## 4. 주요 기능

**실시간 센서 모니터링**
- C# 클라이언트에서 전력(Power), 온도, 습도, 진동 값을 초 단위로 Flask 서버에 전송
- 웹 대시보드 차트에 실시간 반영

**시나리오 기반 자동 제어 (State Machine)**
- 정전 시나리오: 전력 < 300 → 자동 정전 발생 → 비상 전력 활성화 시 10초간 전력 400 고정 → 정상 복구
- 지진 경보: 진동 > 0.5 → 경보 팝업 출력 → 방화벽 가동 시 모든 시뮬레이션 리셋

**보관 물품 관리**
- 창고 보관 물품의 잔여 보관 기한 자동 계산
- JSON 데이터 중복 제거 로직 (items.json 95개 → 39개 고유 항목)

**웹 대시보드**
- 다크 모드 기반 실시간 센서 차트 (glassmorphism 스타일)
- 원격 제어 버튼 (비상 전력, 방화벽 등)

## 5. 기술 스택

| 구분 | 기술 |
|------|------|
| Language | C#, Python |
| Client UI | C# WinForms |
| Backend | Flask (Python) |
| 통신 방식 | HTTP REST API |
| 데이터 저장 | JSON 파일 (items.json) |
| 웹 대시보드 | HTML/CSS/JavaScript |
| 개발 환경 | Visual Studio 2022, Python 3.x |

## 6. 폴더 구조

```
flask-csharp-integration/
├── CS_Client/              # C# WinForms 클라이언트
│   ├── Form1.cs            # 메인 폼 (센서 전송 로직)
│   ├── flaskConnect.sln
│   └── flaskConnect.csproj
├── Flask_Backend/          # Flask 서버
│   ├── app.py              # REST API, 상태 머신
│   ├── items.json          # 보관 물품 데이터
│   ├── static/             # CSS, JS
│   └── templates/          # HTML 대시보드
├── images/
│   └── project02_flowchart.jpg
└── README.md
```

## 7. 핵심 구현 흐름

**센서 데이터 흐름**
1. C# WinForms에서 타이머로 센서값 생성
2. `HttpClient`로 `POST /api/sensor_data` 요청
3. Flask 서버가 데이터 수신 및 상태 머신 조건 확인
4. 웹 대시보드가 `GET /api/sensor_data`로 폴링하여 차트 업데이트

**정전 시나리오 흐름**
1. 전력값 < 300 감지 → 정전 상태 플래그 설정
2. 웹 대시보드에 정전 경보 표시
3. 비상 전력 버튼 클릭 → 10초간 전력 400 고정
4. 10초 후 정상 상태 복구

## 8. 트러블슈팅

**JSON 데이터 중복 문제**
- 문제: items.json에 중복 키 데이터가 쌓여 95개로 증가
- 원인: 서버 재시작 시 데이터 append 로직의 중복 처리 누락
- 해결: clean_items.py 작성으로 고유 항목만 추출하여 39개로 정리

**C#-Flask 비동기 통신 타이밍**
- 문제: 초 단위 폴링에서 데이터 불일치
- 해결: Flask에서 최신 데이터 항상 반환하도록 상태 저장 구조 단순화

## 9. 배운 점

- C# HttpClient를 이용한 비동기 HTTP POST/GET 구현
- Flask REST API 설계 및 JSON 데이터 처리
- 상태 머신 개념을 백엔드 로직으로 구현하는 방법
- 프론트엔드 폴링 기반 실시간 데이터 표시 구조

## 10. 실행 방법

**Flask 서버**
```bash
cd Flask_Backend
pip install flask
python app.py
# http://localhost:5000 에서 대시보드 확인
```

**C# 클라이언트**
1. Visual Studio에서 `CS_Client/flaskConnect.sln` 열기
2. Flask 서버 주소 확인 (기본값: localhost:5000)
3. 빌드 후 실행
