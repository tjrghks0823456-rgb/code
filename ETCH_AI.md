# 식각 Flask AI (ML + 규칙 폴백)

## 동작

1. `models/etch/anomaly_classifier.joblib`, `alarm_classifier.joblib`, `manifest.json` 존재 시 **sklearn ML** 추론 (`etch_model.py`)
2. 없거나 `joblib` 미설치 시 **규칙 스텁** (`etch_ai.py` → `etch_ai_predict_stub`)
3. `etch_ai_predict()` — ML 우선, 실패 시 스텁

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/etch/ai/status` | `ready`, `engine`, `manifest`, `metrics` |
| POST | `/api/etch/ai/predict` | 수동 추론 + latest 갱신 |
| GET | `/api/etch/ai/latest` | WPF·웹 폴링 |

`POST /api/etch/sensor-data` 저장(`stored`) 시 자동으로 `etch_ai_predict` 호출.

## 학습·배포 (WPF repo)

```powershell
cd d:\WPFProject\etch_ui
python tools/ai/generate_synthetic_dataset.py -n 3000
python tools/ai/train_sklearn.py
.\tools\ai\deploy_model.ps1
```

Flask 재시작 후 `GET /api/etch/ai/status` → `"ready": true`, `"engine": "sklearn"`.

## 입력 필드

WPF sensor-data와 동일: `temperature`, `humidity`, `pressure`, `vibration`, `equipmentState`, `alarmCode`, `interlockOk`, `accessSafe`, `benchMode`, `modules[]` (또는 `moduleRunningCount` 등 집계).

## 의존성

```text
pip install scikit-learn joblib numpy
```

`requirements.txt`에 포함됨.
