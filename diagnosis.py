from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class DiagnosisContext:
    data: Dict[str, object] = field(default_factory=dict)

    def get_str(self, key: str, default: str = "") -> str:
        v = self.data.get(key, default)
        return str(v) if v is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        v = self.data.get(key, default)
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in {"y", "yes", "true", "1"}
        if isinstance(v, (int, float)):
            return bool(v)
        return default

    def set(self, key: str, value: object) -> None:
        self.data[key] = value


@dataclass
class DiagnosisResult:
    title: str
    confidence: int
    causes: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def display(self) -> None:
        print("\n" + "*" * 40)
        print(f"[ผลวิเคราะห์] {self.title} (ความมั่นใจ {self.confidence}%)")
        print("-" * 40)

        if self.causes:
            print("สาเหตุที่เป็นไปได้:")
            for c in self.causes:
                print(f"- {c}")

        if self.checks:
            print("\nจุดตรวจเช็คก่อน:")
            for i, ck in enumerate(self.checks, start=1):
                print(f"{i}. {ck}")

        if self.tools:
            print("\nเครื่องมือที่ใช้:")
            for t in self.tools:
                print(f"- {t}")

        if self.notes:
            print("\nหมายเหตุ:")
            for n in self.notes:
                print(f"- {n}")


AskFunc = Callable[[str, List[Tuple[str, str]]], str]
AskYesNoFunc = Callable[[str], bool]


def run_diagnosis(
    category: str,
    symptom: str,
    ctx: Optional[DiagnosisContext] = None,
    *,
    ask: Optional[AskFunc] = None,
    ask_yes_no_fn: Optional[AskYesNoFunc] = None,
) -> DiagnosisResult:

    if ctx is None:
        ctx = DiagnosisContext()

    ctx.set("category", category)
    ctx.set("symptom", symptom)

    if ask is None or ask_yes_no_fn is None:
        return DiagnosisResult(
            title="ระบบวิเคราะห์ยังไม่เชื่อมกับ CLI เต็มรูปแบบ",
            confidence=10,
            causes=["ระบบถามคำถามยังไม่เชื่อม"],
            checks=["ต้องส่ง ask และ ask_yes_no_fn จาก cli.py"],
            tools=[],
            notes=["ตอนนี้เป็นโครงสร้างเริ่มต้นของระบบ"],
        )

    if category == "ac" and symptom == "ac_not_cold":
        fan_running = ask_yes_no_fn("พัดลมคอยล์เย็นเป่าลมออกมาหรือไม่")
        weak_air = ask_yes_no_fn("แรงลมอ่อนผิดปกติหรือไม่")
        coil_iced = ask_yes_no_fn("มีน้ำแข็งเกาะที่คอยล์เย็นหรือไม่")
        compressor_running = ask_yes_no_fn("คอมเพรสเซอร์ด้านนอกทำงานหรือไม่")

        causes = []
        checks = []
        tools = ["แคลมป์มิเตอร์", "เทอร์โมมิเตอร์", "เกจน้ำยาแอร์"]
        notes = []
        confidence = 60

        if not fan_running:
            causes.append("พัดลมคอยล์เย็นไม่ทำงาน")
            checks.append("ตรวจมอเตอร์พัดลม / คาปาซิเตอร์ / ไฟเลี้ยงคอยล์เย็น")
            confidence = 85

        if weak_air:
            causes.append("ฟิลเตอร์อากาศตันหรือคอยล์เย็นสกปรก")
            checks.append("ล้างฟิลเตอร์และตรวจคอยล์เย็น")
            confidence = max(confidence, 80)

        if coil_iced:
            causes.append("คอยล์เย็นเป็นน้ำแข็งจากลมผ่านน้อยหรือน้ำยาแอร์ผิดปกติ")
            checks.append("ปิดเครื่องให้ละลายน้ำแข็งและตรวจระบบน้ำยา")
            confidence = max(confidence, 85)

        if not compressor_running:
            causes.append("คอมเพรสเซอร์หรือชุดคอยล์ร้อนไม่ทำงาน")
            checks.append("ตรวจไฟเข้าชุดภายนอก / คอนแทคเตอร์ / คาปาซิเตอร์ / เบรกเกอร์")
            confidence = max(confidence, 90)

        if not causes:
            causes.extend([
                "น้ำยาแอร์ต่ำ",
                "คอยล์ร้อนระบายความร้อนไม่ดี",
                "ระบบสกปรก",
            ])
            checks.extend([
                "ตรวจแรงดันน้ำยา",
                "ตรวจพัดลมคอยล์ร้อน",
                "เช็คอุณหภูมิลมเข้า-ออก",
            ])
            notes.append("กรณีนี้ควรตรวจวัดค่าหน้างานเพิ่มเพื่อยืนยัน")
            confidence = 70

        return DiagnosisResult(
            title="แอร์ไม่เย็น (วิเคราะห์เบื้องต้น)",
            confidence=confidence,
            causes=causes,
            checks=checks,
            tools=tools,
            notes=notes,
        )

    return DiagnosisResult(
        title="ยังไม่รองรับอาการนี้",
        confidence=0,
        causes=["ยังไม่มี rule สำหรับอาการนี้"],
        checks=["เพิ่ม rule ใน diagnosis.py ภายหลัง"],
        tools=[],
        notes=[],
    )