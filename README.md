# Etch HMI — Flask 모니터링 서버

식각 장비 **원격 모니터링**용 웹 대시보드. 제어는 현장 **WPF HMI**에서 수행합니다.

## 빠른 실행

```bat
C:\etchflask\run_flask.bat
```

- 현장 PC: `http://127.0.0.1:5000`
- 모니터링 PC: `http://<현장PC IP>:5000`

## 관련 문서

| 문서 | 경로 |
|------|------|
| **구현 상태 체크리스트** | `d:\wpf과제프로젝트\구현_상태_체크리스트.md` |
| **원격 모니터링 (2대 PC)** | [REMOTE_MONITORING.md](REMOTE_MONITORING.md) |
| **WPF 실행 순서** | `D:\WPFProject\etch_ui\PROTO_실행순서.md` |
| **EtherCAT I/O 매핑** | `D:\WPFProject\etch_ui\PLC_IO_매핑.md` |
| **PyCharm 안내** | [README_PYCHARM.md](README_PYCHARM.md) |
| **AI 스텁** | [ETCH_AI.md](ETCH_AI.md) |

## 주요 API

- `GET /` — 대시보드
- `GET /api/sensors` — 최신 스냅샷
- `POST /api/etch/sensor-data` — WPF 텔레메트리
- `GET /api/etch/history` · `events` · `summary`

## 센서 표시

`sensorsLive=true` 이고 EtherCAT 실측일 때만 온도·습도·압력·진동 숫자 표시 (WPF와 동일).
