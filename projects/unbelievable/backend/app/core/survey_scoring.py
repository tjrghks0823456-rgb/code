from typing import Dict, Any, Optional

def convert_8axis_to_6axis(survey_scores: Dict[str, float]) -> Dict[str, Optional[float]]:
    """
    Converts 8-axis (D, P, W, N, S, M, F, L) self-survey values to 6-axis dashboard scores.
    
    Mapping Rules:
    - UAS (User Agency Score) = D / (D + P) * 100
    - TDS (Topic Diversity Score) = W / (W + N) * 100
    - SMS (Safety/Stimulus Score) = M / (S + M) * 100
    - VOS (Viewpoint Openness Score) = W / (W + N) * 100 (Temporary mapping until explicit VOS survey questions added)
    - EBS (Emotional Balance Score) = None (No direct counterpart in the 8-axis model, excluded from official gap calculation)
    - SBS (Source Balance Score) = None (No direct counterpart in the 8-axis model, excluded from official gap calculation)
    """
    def safe_div(num: float, den: float) -> Optional[float]:
        if den == 0:
            return None
        return round((num / den) * 100.0, 1)

    D = float(survey_scores.get("D", 0.0))
    P = float(survey_scores.get("P", 0.0))
    W = float(survey_scores.get("W", 0.0))
    N = float(survey_scores.get("N", 0.0))
    S = float(survey_scores.get("S", 0.0))
    M = float(survey_scores.get("M", 0.0))

    uas = safe_div(D, D + P)
    tds = safe_div(W, W + N)
    sms = safe_div(M, S + M)
    vos = safe_div(W, W + N)

    return {
        "UAS": uas,
        "TDS": tds,
        "SMS": sms,
        "VOS": vos,
        "EBS": None,
        "SBS": None
    }
