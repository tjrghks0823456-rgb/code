import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

FALLBACK_API_WARNINGS = {
    "P01_DATA_SHORT": {"axis": "ALL", "message": "분석 가능한 시청 이벤트가 부족하여 전체 지표는 참고용으로 표시됩니다."},
    "P10_DURATION_ESTIMATED": {"axis": "ALL", "message": "시청 기록에 체류 시간 정보가 확인 불가하여 기록 간 간격 및 비디오 길이를 바탕으로 '추정 체류 시간'을 계산하였습니다. 일부 장기 방치 세션 등 현실 왜곡 가능성이 존재합니다. (기록 기반 추정값)"},
    "P10_DURATION_MISSING": {"axis": "ALL", "message": "시청 지속 시간이 기록되지 않았으며 간격 추정도 불가하여 일부 채점이 불가능합니다. (확인 불가)"},
    "P14_DSAO_LEGACY_MAPPING": {"axis": "ALL", "message": "DSAO 유형 결정을 위해 legacy MBTI 코드가 내부 호환용으로 대조되었습니다. (4-letter type code representing 16 possible types)"},
    "P15_NLP_FALLBACK_USED": {"axis": "TDS", "message": "Google Cloud Language API 인증 또는 한도 오류가 발생하여, 세종이 한글 형태소 분석 사전 및 로컬 규칙 엔진 기반으로 대체 분석을 수행했습니다."}
}

class MessageLoader:
    def __init__(self):
        self.message_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "messages", "warning_messages.ko.v1.json"
        )
        self.api_warnings: Dict[str, Dict[str, str]] = {}
        self.quality_flags: Dict[str, Dict[str, str]] = {}
        
        self.load_messages()

    def load_messages(self):
        if not os.path.exists(self.message_file):
            logger.warning(f"Warning messages JSON file not found at {self.message_file}. Using minimal fallback.")
            self.api_warnings = FALLBACK_API_WARNINGS
            return

        try:
            with open(self.message_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.api_warnings = data.get("api_warnings", {})
            self.quality_flags = data.get("quality_flags", {})
            logger.info("Successfully loaded localized messages configurations.")
        except Exception as e:
            logger.warning(f"Error loading messages config: {e}. Using fallback defaults.")
            self.api_warnings = FALLBACK_API_WARNINGS

    def get_api_warning(self, code: str) -> Dict[str, str]:
        return self.api_warnings.get(code, {"axis": "ALL", "message": f"주의사항이 발생했습니다: {code}"})

    def get_all_warnings(self) -> Dict[str, Dict[str, str]]:
        return self.api_warnings

message_loader = MessageLoader()
