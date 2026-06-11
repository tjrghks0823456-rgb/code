# 식각 HMI AI - ML 모델(models/etch)을 우선 사용하고, 실패하면 규칙 기반 스텁으로 폴백한다.

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict


# Flask 서버 기준으로 배포된 학습 모델이 저장되는 위치.
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models", "etch")


def etch_ai_status_payload() -> Dict[str, Any]:
    """AI 엔진의 로딩 상태를 UI가 바로 표시할 수 있는 payload로 반환한다."""
    try:
        from etch_model import get_engine

        return get_engine().status_payload()
    except Exception as ex:
        # 모델 파일 누락, joblib 로딩 실패 등은 웹 UI가 멈추지 않도록 스텁 상태로 알린다.
        return {
            "project": "etch_hmi",
            "models_dir": MODELS_DIR,
            "ready": False,
            "engine": "stub",
            "message": f"AI 엔진 초기화 실패: {ex}",
        }


def _predict_alarm_stub(payload: dict) -> tuple[str, float]:
    """AI-2: 규칙 기반 예상 알람을 반환한다. 이 결과는 조언용이며 인터락에는 개입하지 않는다."""
    # 이미 알람 코드가 들어온 경우에는 실제 알람을 최우선으로 신뢰한다.
    alarm = payload.get("alarmCode") or payload.get("alarm_code")
    if alarm:
        code = str(alarm).strip().upper()
        return code if code.startswith("A") else "A000", 0.92

    # 장비 상태가 ALARM이면 원인 미상 일반 알람으로 안내한다.
    state = (payload.get("equipmentState") or payload.get("equipment_state") or "").upper()
    if state == "ALARM":
        return "A001", 0.75

    # 인터락 실패는 안전 계통 확인이 필요한 징후로 분류한다.
    interlock = payload.get("interlockOk")
    if interlock is False:
        return "A004", 0.62

    # 압력 범위 이탈 여부를 점검한다. 범위값이 없으면 데모 기본값을 사용한다.
    pressure = payload.get("pressure")
    if pressure is not None:
        try:
            p = float(pressure)
            lo = float(payload.get("pressureMin") or 50)
            hi = float(payload.get("pressureMax") or 150)
            if p < lo or p > hi:
                return "A002", 0.68
        except (TypeError, ValueError):
            pass

    # 진동 상한 초과는 구동부 또는 이송부 이상 가능성으로 분류한다.
    vibration = payload.get("vibration")
    if vibration is not None:
        try:
            v = float(vibration)
            vmax = float(payload.get("vibrationMax") or 0.8)
            if v > vmax:
                return "A003", 0.65
        except (TypeError, ValueError):
            pass

    # WARNING은 즉시 알람보다 낮은 확신도로 추세 관찰을 유도한다.
    if state == "WARNING":
        return "A005", 0.45

    return "NONE", 0.18


def etch_ai_predict_stub(payload: dict) -> Dict[str, Any]:
    """ML 모델이 없거나 실패했을 때 사용하는 규칙 기반 폴백 예측."""
    alarm = payload.get("alarmCode") or payload.get("alarm_code")
    state = (payload.get("equipmentState") or payload.get("equipment_state") or "").upper()
    predicted_alarm, pred_confidence = _predict_alarm_stub(payload)

    # anomaly_score는 UI 경고 강도를 결정하는 단순 위험 점수다.
    score = 0.15
    if alarm:
        score = 0.85
    elif predicted_alarm not in (None, "", "NONE"):
        score = max(score, min(0.9, pred_confidence + 0.1))
    elif state == "WARNING":
        score = 0.55
    elif state == "ALARM":
        score = 0.92

    # 사용자에게 보일 조치 문구는 실제 알람, 예상 알람, 장비 상태 순으로 구체화한다.
    suggested = "정상 범위 모니터링을 유지하세요."
    if alarm:
        suggested = f"알람 {alarm} 원인 제거 후 Reset. 인터락·Load Lock 접촉을 확인하세요."
    elif predicted_alarm and predicted_alarm != "NONE":
        suggested = f"예상 알람 {predicted_alarm} - 추세·인터락·Load Lock을 점검하세요 (조언만)."
    elif state == "ALARM":
        suggested = "알람 상태 - 센서·접촉·EtherCAT 연결을 점검하세요."
    elif state == "WARNING":
        suggested = "환경(온·습도) 편차 - 공정 유지 시 추세를 강화 모니터링하세요."
    elif score >= 0.55:
        suggested = "이상 징후 가능 - 압력·진동 추세를 확인하세요."

    return {
        "success": True,
        "stub": True,
        "model": "rules",
        "anomaly_score": round(score, 3),
        "predicted_alarm": predicted_alarm,
        "prediction_confidence": round(pred_confidence, 3),
        "suggested_action": suggested,
        "note": "규칙 스텁 - models/etch/*.joblib 학습 후 ML로 전환됩니다.",
        "updatedAt": datetime.now().isoformat(),
    }


def etch_ai_predict(payload: dict) -> Dict[str, Any]:
    """ML 예측을 우선 수행하고, 사용할 수 없으면 규칙 기반 스텁 결과를 반환한다."""
    try:
        from etch_model import predict_ml

        ml = predict_ml(payload)
        if ml:
            ml["updatedAt"] = datetime.now().isoformat()
            return ml
    except Exception:
        # AI는 보조 기능이므로 예외가 발생해도 HMI 응답은 계속 제공한다.
        pass

    return etch_ai_predict_stub(payload)
