from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ----------------------------------------
# Data Model ของความรู้
# ----------------------------------------

@dataclass
class SymptomKnowledge:
    key: str
    name: str
    possible_causes: List[str] = field(default_factory=list)
    basic_checks: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    questions: List[Dict[str, str]] = field(default_factory=list)


# ------------------------------------------
# หมวดหมู่ระบบ
# ------------------------------------------
CATEGORIES: Dict[str, str] = {
    "ac": "เครื่องปรับอากาศ",
    "electrical": "ระบบไฟฟ้า",
    "pump": "ปั๊มน้ำ",
    "plumbing": "ระบบน้ำ/ท่อน้ำ",
}

# -------------------------------------------
# ฐานความรู้ (เริ่มจาก แอร์ไม่เย็น)
# -------------------------------------------

AC_NOT_COLD = SymptomKnowledge(
    key="ac_not_cold",
    name="แอร์ไม่เย็น",
    possible_causes=[
        "ฟิลเตอร์แอร์สกปรก",
        "คอยล์เย็นสกปรก",
        "น้ำยาแอร์ขาด",
        "พัดลมคอยล์ร้อนไม่หมุนหรือหมุนช้า",
        "คอมเพรสเซอร์ไม่ทำงาน",
    ],
    basic_checks=[
        "เปิดหน้ากากดูฟิลเตอร์อากาศ",
        "ดูว่าคอยล์เย็นมีน้ำแข็งเกาะหรือไม่",
        "ฟังเสียงคอมเพรสเซอร์ด้านนอก",
        "เช็คความร้อนที่คอยล์ร้อน",
        "วัดกระแสคอมเพรสเซอร์",
    ],
    required_tools=[
        "แคลมป์มิเตอร์",
        "เทอร์โมมิเตอร์",
        "เกจน้ำยาแอร์",
    ],
    # คำถามที่ rules.py จะถามผู้ใช้งาน
    questions=[
        {"id": "fan_running", "question": "พัดลมคอยล์ร้อนเป่าลมออกมาหรือไม่?", "type": "yesno"},
        {"id": "air_weak", "question": "แรงลมอ่อนผิดปกติหรือไม่?", "type": "yesno"},
        {"id": "coil_iced", "question": "มีน้ำแข็งเกาะที่คอยล์เย็นหรือไม่?", "type": "yesno"},
        {"id": "compressor_running", "question": "คอมเพรสเซอร์ด้านนอกทำงานหรือไม่?", "type": "yesno"},
    ],
)

# -----------------------------------------------------
# รวมทุกความรู้
# -----------------------------------------------------

KNOWLEDGE: Dict[str, SymptomKnowledge] = {
    AC_NOT_COLD.key: AC_NOT_COLD,
}

def get_symptom_knowledge(symptom_key: str) -> Optional[SymptomKnowledge]:
    return KNOWLEDGE.get(symptom_key)