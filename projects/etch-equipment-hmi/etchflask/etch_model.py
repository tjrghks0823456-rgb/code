"""식각 HMI sklearn 모델 로드·추론 (models/etch/*.joblib)."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models", "etch")
MANIFEST_NAME = "manifest.json"
ANOMALY_NAME = "anomaly_classifier.joblib"
ALARM_NAME = "alarm_classifier.joblib"

FEATURE_NAMES = [
    "temperature",
    "humidity",
    "pressure",
    "vibration",
    "interlock_ok",
    "access_safe",
    "bench_mode",
    "module_running_count",
    "module_alarm_count",
    "module_processing_count",
    "chamber_processing_count",
    "state_idle",
    "state_ready",
    "state_running",
    "state_warning",
    "state_alarm",
    "state_maint",
]

_engine: Optional["EtchAiEngine"] = None


def get_engine() -> "EtchAiEngine":
    global _engine
    if _engine is None:
        _engine = EtchAiEngine()
    return _engine


def reload_engine() -> "EtchAiEngine":
    global _engine
    _engine = EtchAiEngine()
    return _engine


class EtchAiEngine:
    def __init__(self) -> None:
        self.models_dir = MODELS_DIR
        self.manifest: Dict[str, Any] = {}
        self.anomaly_clf = None
        self.alarm_clf = None
        self.ready = False
        self._load()

    def _load(self) -> None:
        os.makedirs(self.models_dir, exist_ok=True)
        manifest_path = os.path.join(self.models_dir, MANIFEST_NAME)
        if os.path.isfile(manifest_path):
            with open(manifest_path, encoding="utf-8") as f:
                self.manifest = json.load(f)

        anomaly_path = os.path.join(self.models_dir, ANOMALY_NAME)
        alarm_path = os.path.join(self.models_dir, ALARM_NAME)
        try:
            import joblib
        except ImportError:
            return

        if os.path.isfile(anomaly_path):
            self.anomaly_clf = joblib.load(anomaly_path)
        if os.path.isfile(alarm_path):
            self.alarm_clf = joblib.load(alarm_path)

        self.ready = self.anomaly_clf is not None and self.alarm_clf is not None

    def status_payload(self) -> Dict[str, Any]:
        base: Dict[str, Any] = {
            "project": "etch_hmi",
            "models_dir": self.models_dir,
            "ready": self.ready,
            "engine": "sklearn" if self.ready else "stub",
            "manifest": self.manifest if self.manifest else None,
        }
        if self.ready and self.manifest.get("metrics"):
            base["metrics"] = self.manifest["metrics"]
            base["message"] = (
                f"ML 모델 로드됨 (v{self.manifest.get('version', '?')}) — "
                f"이상 정확도 {self.manifest.get('metrics', {}).get('anomaly_accuracy', '—')}"
            )
        elif self.ready:
            base["message"] = f"ML 모델 로드됨 (v{self.manifest.get('version', '?')})"
        else:
            base["message"] = (
                "ML 미로드 — tools/ai/train_sklearn.py 학습 후 "
                "models/etch/*.joblib 배포"
            )
        return base


def _float(payload: Dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for k in keys:
        if k in payload and payload[k] is not None:
            try:
                return float(payload[k])
            except (TypeError, ValueError):
                pass
    return default


def _bool01(payload: Dict[str, Any], key: str, default: bool = False) -> float:
    v = payload.get(key)
    if v is None:
        return 1.0 if default else 0.0
    return 1.0 if bool(v) else 0.0


def _module_stats(modules: Any) -> Tuple[int, int, int, int]:
    if not isinstance(modules, list):
        return 0, 0, 0, 0
    running = alarm = processing = chamber = 0
    pm_ids = {"PM1", "PM2", "PM3", "PM4"}
    for m in modules:
        if not isinstance(m, dict):
            continue
        st = str(m.get("state") or m.get("stateText") or "").upper()
        mid = str(m.get("id") or "").upper()
        if st == "RUNNING":
            running += 1
        if st == "ALARM":
            alarm += 1
        if st == "PROCESSING":
            processing += 1
            if mid in pm_ids:
                chamber += 1
    return running, alarm, processing, chamber


def payload_to_features(payload: Dict[str, Any]) -> List[float]:
    st = (payload.get("equipmentState") or payload.get("equipment_state") or "IDLE").upper()
    flags = {s: 0.0 for s in ["IDLE", "READY", "RUNNING", "WARNING", "ALARM", "MAINTENANCE"]}
    if st in flags:
        flags[st] = 1.0

    run_c, alarm_c, proc_c, chamber_c = _module_stats(payload.get("modules"))
    if payload.get("moduleRunningCount") is not None:
        run_c = int(payload.get("moduleRunningCount") or run_c)
    if payload.get("moduleAlarmCount") is not None:
        alarm_c = int(payload.get("moduleAlarmCount") or alarm_c)

    return [
        _float(payload, "temperature"),
        _float(payload, "humidity"),
        _float(payload, "pressure", "pressure_mtorr"),
        _float(payload, "vibration", "vibration_g"),
        _bool01(payload, "interlockOk", default=True),
        _bool01(payload, "accessSafe", default=True),
        _bool01(payload, "benchMode"),
        float(run_c),
        float(alarm_c),
        float(proc_c),
        float(chamber_c),
        flags["IDLE"],
        flags["READY"],
        flags["RUNNING"],
        flags["WARNING"],
        flags["ALARM"],
        flags["MAINTENANCE"],
    ]


def predict_ml(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    engine = get_engine()
    if not engine.ready or engine.anomaly_clf is None or engine.alarm_clf is None:
        return None

    import numpy as np

    x = np.array([payload_to_features(payload)], dtype=np.float64)
    anom_proba = float(engine.anomaly_clf.predict_proba(x)[0][1])
    predicted_alarm = str(engine.alarm_clf.predict(x)[0])
    alarm_proba = engine.alarm_clf.predict_proba(x)[0]
    confidence = float(max(alarm_proba)) if len(alarm_proba) else 0.5

    actual = payload.get("alarmCode") or payload.get("alarm_code")
    if actual:
        predicted_alarm = str(actual).strip().upper()
        confidence = max(confidence, 0.9)

    if predicted_alarm == "NONE" and anom_proba >= 0.55:
        predicted_alarm = _guess_alarm_from_features(payload)
        confidence = max(confidence, anom_proba)

    score = min(0.98, max(anom_proba, confidence * 0.85))
    suggested = _suggested_text(predicted_alarm, score, payload)

    return {
        "success": True,
        "stub": False,
        "model": "sklearn",
        "anomaly_score": round(score, 3),
        "predicted_alarm": predicted_alarm,
        "prediction_confidence": round(confidence, 3),
        "suggested_action": suggested,
        "note": f"ML 추론 (manifest v{engine.manifest.get('version', '?')})",
        "updatedAt": None,
    }


def _guess_alarm_from_features(payload: Dict[str, Any]) -> str:
    p = _float(payload, "pressure")
    lo = _float(payload, "pressureMin", default=50)
    hi = _float(payload, "pressureMax", default=150)
    if p < lo or p > hi:
        return "A002"
    if _float(payload, "vibration") > _float(payload, "vibrationMax", default=0.8):
        return "A003"
    if payload.get("interlockOk") is False or payload.get("accessSafe") is False:
        return "A004"
    return "NONE"


def _suggested_text(predicted: str, score: float, payload: Dict[str, Any]) -> str:
    alarm = payload.get("alarmCode") or payload.get("alarm_code")
    if alarm:
        return f"알람 {alarm} 확인 — Reset 전 원인 제거 (ML·현장 교차 확인)."
    if predicted and predicted != "NONE":
        return f"ML 예상 알람 {predicted} — 추세·인터락 점검 (조언만, 자동 Start 없음)."
    if score >= 0.75:
        return "이상 가능성 높음 — 압력·진동·모듈 상태를 확인하세요."
    if score >= 0.45:
        return "경미한 이상 징후 — 모니터링 강화."
    return "ML: 정상 범위로 추정. 추세 모니터링 유지."
