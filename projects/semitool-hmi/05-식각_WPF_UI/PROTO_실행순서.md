# 식각 HMI 프로토타입 실행 순서

## 1) Flask (먼저 실행)

1. `C:\etchflask\run_flask.bat` 더블클릭  
   또는 터미널에서:
   ```bat
   cd C:\etchflask
   run_flask.bat
   ```
2. 브라우저에서 확인: `http://127.0.0.1:5000` — **탭**: 실시간 / 서버 이력 / 이벤트 / AI 진단(스텁).  
   - 최신 스냅샷: `GET /api/sensors`  
   - 시계열(메모리, 재시작 시 초기화): `GET /api/etch/history?limit=500`  
   - 상태·알람·인터록 이벤트: `GET /api/etch/events?limit=100`  
   - KPI 요약: `GET /api/etch/summary`

## 2) WPF HMI

1. Visual Studio에서 `D:\WPFProject\etch_ui\etch_ui.sln` 열기 → F5  
   또는:
   ```bat
   dotnet run --project D:\WPFProject\etch_ui\etch_ui.csproj
   ```
2. 로그인: `admin` / `Admin1234`
3. 상단 **Flask: OK**, **PLC: Connected** 또는 **SIMULATION** 확인 · **시뮬 허용**은 메인 창 버튼으로 켜고 끕니다(기본 끔).  
   - Flask가 꺼져 있으면 `OFF` — `run_flask.bat` 실행 후 앱만 다시 시작하거나, Flask를 켠 뒤 잠시 기다리면 주기 전송 성공 시 `OK`으로 갱신됩니다.

## 설정

- WPF 출력 폴더의 `appsettings.json`에서 `FlaskBaseUrl`, `AdsPort`(기본 851), `SimulationEnabled`(기본 `false` · **시작 시 시뮬 허용 여부 초깃값**), **`Interlock`**(압력·진동·온·습도 정상 범위, 인터락 판정에 사용) 변경 가능합니다.  
  - 실행 중에는 메인 상단 **「시뮬 허용」** 버튼으로 on/off 할 수 있습니다 (PLC 끊김 시에만 시뮬로 **대체**할지 여부).  
  - **끔**: 실데이터만 — PLC 없으면 오프라인·알람. **켬**: PLC 실패 시 데스크/비기능 테스트용 가짜 센서.

## 연동 데이터

- WPF → `POST /api/etch/sensor-data` (약 2초마다, 센서 이름 `압력`·`진동` 등)
- 웹/대시보드 → `GET /api/sensors` (최신 스냅샷 + `equipmentState`, `alarmCode` 등)
