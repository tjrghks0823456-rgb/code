"""가상 공정 레시피 캐시 (WPF POST recipe 필드)."""
from __future__ import annotations

from typing import Any, Dict, Optional


def normalize_recipe(raw: Any) -> Optional[Dict[str, Any]]:
    if not raw or not isinstance(raw, dict):
        return None
    return {
        'id': raw.get('id') or 'default',
        'name': raw.get('name') or '',
        'version': raw.get('version') or '1',
        'etchPmSequence': raw.get('etchPmSequence') or 'PM2,PM3,PM4',
        'etchProcessTicks': raw.get('etchProcessTicks'),
        'stripProcessTicks': raw.get('stripProcessTicks'),
        'alignProcessTicks': raw.get('alignProcessTicks'),
    }
