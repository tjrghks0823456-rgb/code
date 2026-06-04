# 원격 모니터링 (2대 PC) 구성

## 관련 문서

| 문서 | 경로 |
|------|------|
| **구현 상태 체크리스트** | `d:\wpf과제프로젝트\구현_상태_체크리스트.md` |
| **WPF 실행 순서** | `D:\WPFProject\etch_ui\PROTO_실행순서.md` |
| **EtherCAT I/O 매핑** | `D:\WPFProject\etch_ui\PLC_IO_매핑.md` |
| **Flask README** | `C:\etchflask\README.md` |

## 역할

| PC | 설치·실행 | 역할 |
|----|-----------|------|
| **현장 PC** | TwinCAT EtherCAT I/O, WPF HMI, `run_flask.bat` | 장비 제어·안전, 센서 수집, Flask로 텔레메트리 **송신** |
| **모니터링 PC** | 브라우저만 | `http://<현장PC_IP>:5000` **조회** (제어 없음) |

Flask·WPF·EtherCAT 마스터를 **모니터링 PC 한 대에 모두** 둘 필요는 없습니다.

## 현장 PC 설정

1. `C:\etchflask\run_flask.bat` 실행 (기본 `0.0.0.0:5000` 바인딩)
2. WPF `appsettings.json`:
   ```json
   "FlaskBaseUrl": "http://127.0.0.1:5000"
   ```
   WPF는 **같은 PC**의 Flask로 POST 합니다.
3. Windows 방화벽: **인바운드 TCP 5000** 허용 (모니터링 PC 접속용)

현장 PC IP 확인: `ipconfig` → IPv4 (예: `192.168.0.10`)

## 모니터링 PC 설정

1. Flask/WPF 설치 **불필요**
2. 브라우저 주소: `http://192.168.0.10:5000` (현장 PC IP로 변경)
3. EtherCAT 미연결 시 센서 카드는 **「-」**, 상단 **「EtherCAT: 미연결」** — WPF와 동일 정책

## 센서 표시 조건

- WPF·Flask 모두 `sensorsLive` / EtherCAT 실측일 때만 온도·습도·압력·진동 표시
- 시뮬·미연결: 상태·알람·사용자·이벤트만 전송·표시 가능

## 환경 변수 (선택)

```bat
set ETCH_FLASK_HOST=0.0.0.0
set ETCH_FLASK_PORT=5000
python app.py
```
