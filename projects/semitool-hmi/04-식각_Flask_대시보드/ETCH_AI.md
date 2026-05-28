# 식각 Flask AI 확장 가이드

`farmui`와 동일하게 `ml_trainer.py` + `models/` 디렉터리를 쓰면 됩니다.

## 현재 상태

- `GET /api/etch/ai/status` — `models/etch` 아래 `.pkl` / `.joblib` 존재 여부만 확인
- `POST /api/etch/ai/predict` — 실제 모델 전 **스텁(가짜 점수)** 응답

## 다음 작업(권장 순서)

1. `C:\etchflask\models\etch\` 폴더를 만들고, 센서 이력(`event_logs` 또는 Flask 메모리 시계열)으로 이상 탐지 또는 상태 분류 모델 학습
2. `etch_ai.py`에 `joblib.load` 또는 `pickle` 로 모델 로드 후 `predict` 호출
3. WPF 또는 웹 대시보드에서 주기적으로 `POST /api/etch/ai/predict` 호출 (TwinCAT 값과 동일 스냅샷 JSON)

데이터 필드는 WPF가 보내는 것과 맞추면 됩니다: `temperature`, `humidity`, `pressure`, `vibration`, `equipmentState`, `alarmCode` 등.
