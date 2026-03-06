from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CaseRecord:
    category: str
    symptom: str
    result_title: str
    confidence: int
    causes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "symptom": self.symptom,
            "result_title": self.result_title,
            "confidence": self.confidence,
            "causes": self.causes,
        }