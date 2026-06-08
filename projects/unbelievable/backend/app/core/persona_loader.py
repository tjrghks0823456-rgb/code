import json
import logging
import os
from typing import Dict, Tuple, List, Any

logger = logging.getLogger(__name__)

# Minimal python code configurations for fallback protection to avoid server startup crashes
FALLBACK_LEGACY_MBTI_MAP = {
    ("H", "H", "H", "H"): ("진정한 탐험가", ["#호기심", "#도전", "#학습"]),
    ("H", "H", "H", "L"): ("자기주도적 탐구자", ["#탐구", "#목표", "#확장"]),
    ("H", "H", "L", "H"): ("지적 모험가", ["#신선함", "#공부", "#흥미"]),
    ("H", "H", "L", "L"): ("에너지 넘치는 사색가", ["#창의", "#이슈", "#소통"]),
    ("H", "L", "H", "H"): ("조화로운 관점 설계자", ["#공감", "#독해력", "#다양성"]),
    ("H", "L", "H", "L"): ("주도적 감성 관찰자", ["#감성분석", "#내면성찰", "#표현"]),
    ("H", "L", "L", "H"): ("친화적 소통가", ["#키워드", "#친화력", "#소통"]),
    ("H", "L", "L", "L"): ("감성 아웃사이더", ["#아웃라이어", "#독특함", "#예술"]),
    ("L", "H", "H", "H"): ("효율적 정보 관리자", ["#효율성", "#전문성", "#집중"]),
    ("L", "H", "H", "L"): ("주도적 분석 매니아", ["#데이터", "#실용적", "#심층분석"]),
    ("L", "H", "L", "H"): ("소통 지향 마니아", ["#트렌드", "#민감", "#교류"]),
    ("L", "H", "L", "L"): ("감성적 정보 몰입러", ["#몰입형", "#감수성", "#애청자"]),
    ("L", "L", "H", "H"): ("추천 흐름 점검형", ["#반복패턴", "#균형회복", "#자기조절"]),
    ("L", "L", "H", "L"): ("흥미 반응형", ["#자극", "#쇼츠", "#재미"]),
    ("L", "L", "L", "H"): ("수동적 수용자", ["#알고리즘", "#흘러가는대로", "#피동"]),
    ("L", "L", "L", "L"): ("조용한 휴식형", ["#차분함", "#휴식", "#균형회복"]),
}

FALLBACK_DSAO_TYPES = {
    "DWSF": {"name": "다채로운 숏폼 탐색형", "character": "지식 스낵 탐험가", "description": "다양한 주제의 짧은 영상을 스스로 주도하여 탐색하고 시청하는 유형입니다."},
    "PNMF": {"name": "조용한 추천 루틴형", "character": "수동형 정보 구독자", "description": "알고리즘이 추천하는 관심 분야의 정보 요약본을 루틴화하여 수동적으로 시청하는 유형입니다."}
}

class PersonaLoader:
    def __init__(self):
        self.persona_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "persona", "dsao_persona_types.v1.json"
        )
        self.legacy_mbti_map: Dict[Tuple[str, str, str, str], Tuple[str, List[str]]] = {}
        self.dsao_types: Dict[str, Dict[str, Any]] = {}
        
        self.load_persona()

    def load_persona(self):
        if not os.path.exists(self.persona_file):
            logger.warning(f"Persona JSON file not found at {self.persona_file}. Using minimal fallback.")
            self._apply_fallback()
            return

        try:
            with open(self.persona_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Legacy mapping parsing
            raw_mbti = data.get("legacy_mbti_map", {})
            for key_str, details in raw_mbti.items():
                if len(key_str) == 4:
                    key_tuple = (key_str[0], key_str[1], key_str[2], key_str[3])
                    name = details.get("name", "알 수 없는 성향")
                    tags = details.get("tags", [])
                    self.legacy_mbti_map[key_tuple] = (name, tags)
            
            # DSAO type details
            self.dsao_types = data.get("dsao_types", {})
            
            if not self.legacy_mbti_map or not self.dsao_types:
                raise ValueError("Parsed legacy MBTI map or DSAO types lists are empty.")
            
            logger.info("Successfully loaded persona types configurations.")
        except Exception as e:
            logger.warning(f"Error loading persona configs: {e}. Using fallback defaults.")
            self._apply_fallback()

    def _apply_fallback(self):
        self.legacy_mbti_map = FALLBACK_LEGACY_MBTI_MAP
        self.dsao_types = FALLBACK_DSAO_TYPES

    def get_legacy_mbti_detail(self, key_tuple: Tuple[str, str, str, str]) -> Tuple[str, List[str]]:
        return self.legacy_mbti_map.get(key_tuple, ("미지의 미디어 관찰자", ["#분석대기", "#신규성향"]))

    def get_dsao_name(self, code: str) -> str:
        return self.dsao_types.get(code, {}).get("name", "미지의 미디어 탐험가")

    def get_dsao_detail(self, code: str) -> Dict[str, Any]:
        default_detail = {
            "code": code,
            "name": "미지의 미디어 탐험가",
            "short_summary": "데이터 분석 대기 중",
            "detailed_description": "성향 분석 데이터가 충분하지 않거나 대기 중인 상태입니다.",
            "character": "탐색 대기자",
            "strengths": ["분석 대기"],
            "risks": ["기록 축적 필요"],
            "recommended_detox_direction": "시청 기록을 충분히 확보한 뒤 성향 진단을 실행해 보세요.",
            "similar_types": [],
            "opposite_type": ""
        }
        item = self.dsao_types.get(code)
        if not item:
            return default_detail
        res = dict(default_detail)
        res.update(item)
        res["code"] = item.get("code", code)
        if "description" in item and "detailed_description" not in item:
            res["detailed_description"] = item["description"]
        return res


persona_loader = PersonaLoader()
