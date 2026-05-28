# 식각 HMI용 AI 연동 스텁.
# farmui의 ml_trainer / models 디렉터리 패턴을 그대로 확장하면 됨.

import os


MODELS_DIR = os.path.join(os.path.dirname(__file__), "models", "etch")


def etch_ai_status_payload():
    if not os.path.isdir(MODELS_DIR):
        has_models = False
    else:
        has_models = any(
            f.endswith(".pkl") or f.endswith(".joblib")
            for f in os.listdir(MODELS_DIR)
        )
    return {
        "project": "etch_hmi",
        "models_dir": MODELS_DIR,
        "ready": has_models,
        "message": (
            "학습된 식각용 모델이 없습니다. 학습 후 models/etch 에 배치하면 진단 패널이 활성화됩니다."
            if not has_models
            else "모델 파일이 감지되었습니다. 추론 파이프라인만 연결하면 됩니다."
        ),
    }


def etch_ai_predict_stub(payload: dict):
    """실제 모델 전 규칙 기반 플레이스홀더."""
    alarm = payload.get("alarmCode") or payload.get("alarm_code")
    state = (payload.get("equipmentState") or payload.get("equipment_state") or "").upper()
    score = 0.15
    if alarm:
        score = 0.85
    elif state == "WARNING":
        score = 0.55
    elif state == "ALARM":
        score = 0.92
    return {
        "success": True,
        "stub": True,
        "anomaly_score": round(score, 3),
        "note": "실제 추론 연결 시 ETCH_AI.md 또는 models/etch 절차를 따릅니다.",
    }
