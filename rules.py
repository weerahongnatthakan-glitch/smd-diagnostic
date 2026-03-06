from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from knowledge_base import get_symtom_knowledge
from models import DiagnosisRusult


AskFunc = Callable[str, List[Tuple[str, str]]], str]
AskYesNoFunce = Callable[[str], bool]


def _make_result(
    title: str,
    confdence: int,
    *,
    causes: List[str] | None = None,
    checks: List[str] | None = None,
    tools: List[str] | None = None,
    notes: List[str] | None = None,
) -> DiagnosisResult:
    return DiagnosisResult(
        title=title,
        confidence=confidence,
        causes=causes or [],
        checks=checks or [],
        tools=tools or [],
        notes=notes or [],
    )

def _ask_yesno_with_ctx(ctx, qid: str, question: str, ask_yes_no_fn: AskYesNoFunc) ->
bool:
    """
    ถามคำถาม yes/no แล้วเก็บลง ctx.data[qid] เพื่อให้ใช้ต่อได้
    ctx = DiagnosisContext จาก diagnosis.py (เราไม่ import type เพื่อกันวง import)
    """
    ans = ask_yes_no_fn(question)
    ctx. set(qid, ans)
    return ans


def evaluete(category: str, symptom: str, ctx, ask: AskFunc, ask_yes_no_fn:
AskYesNoFunc) -> DiagnosisResult:
    """
    จุดรวมกฎทั้งหมด
    - category: เช่น 'ac'
    - symptom: เช่น 'ac_not_cold'
    - ctx: DiagnosisContext (เก็บคำตอบ)
    - ask / ask_yes_no_fn: ฟังชั่นถามจาก CLI
    """
    # ตอนนี้เรารองรับเแพาะ "แอร์ไม่เย็น" ก่อน
    if category == "ac" and symptom == "ac_not_cold":
        return _rule_ac_not_cold(ctx, ask_yes_no_fn)

    return _make_result(
        title="ยังไม่รองรับอาการนี้",
        confidence=5,
        causes=["ยังไม่มี rule สำหรับเคสนี้"],
        checks=["เพิ่ม rule ใน rules.py แล้งลองใหม่"],
        notes=[f"category={category}, symptom={symptom}"],
    )

def _rule_ac_not_cold(ctx, ask_yes_no_fn: AskYesNoFunc) -> DiagnosisResult:
    """
    Rule-based logic: แอร์ไม่เย็น
    ใส่คำถามจาก knowledge_base เป็นตัวช่วย แต่ logic อยู่ที่นี่
    """
    kb = get_symptom_knowledge("ac_not_cold")

    # ถ้า kb ไม่มี (ไฟล์ knowledge_base ยังไม่ได้ใส่ key) ก็ยังให้โปรแกรมรันต่อได้
    base_causes = kb.possible_causes if kb else []
    base_checks = kb.basic_checks if kb else []
    base_tools = kb.required_tools if kb else []

    print("\nกำลังวิเคราะห์ (Rule-base)...")

    # 1) พัดลมคอยส์เย็นทำงานไหม
    fan_running = _ask_yesno_with_ctx(ctx, "fan_running", "พัดลมคอยส์เย็นเป่าออกมาหรือไหม? (y/n): ", ask_yes_no_fn)
    if not fan_running:
        return _make_result(
            title="แอร์ไม่เย็น: พัดลมคอยส์เย็นไม่ทำงาน",
            confidence=85,
            causes=[
                "มอเตอร์พัดลมคอยส์เย็นเสีย",
                "คาปา๙ิเตอร์พัดลมเสีย (ถ้ามี)",
                "แผงคอนโทรล/ไฟเลี้ยงพัดลมมีปัญหา",
            ],
            checks=[
                "เช็คไฟเข้าชุกคอยส์เย็น / ตรวจฟิวส์หรือคอนเน็คเตอร์หลวม",
                "ลองปรับสปีดพัลม (ถ้าเป็นรุ่นที่ปรับได้)",
                "วัดกระแสมอเตอร์พัดลม (ถ้าทำได้)",
            ],
            tools=["มัลติมิเตอร์", "แคลมป์มิเตอร์"],
            notes=["ถ้าพัดลมไม่หมุน ลมไม่พาเอาความเย็นออกมา ห้องจะไม่เย็น"],
        )
    # 2) แรงลมอ่อนผิกปกติไหม
    air_weak = _ask_yesno_with_ctx(ctx, "air_weak", "แรงลมออกจากแอร์อ่อนผิดปกติหรือไม่? (y/n): ", ask_yes_no_fn)
    if air_weak:
        return _make_result(
            title="แอร์ไม่เย็น: แรงลมอ่อน",
            confidence=80,
            causes=[
                "ฟิลเตอร์อากาศตัน/สกปรก",
                "คอยส์เย็นสกปรก",
                "โบเวอร์/ใบพัดลมสกปรก",
            ],
            checks=[
                "ถอดล้างฟิลเตอร์อากาศ",
                "ส่องดูคอยส์เย็นว่ามีฝุ่นเกาะแน่นหรือไม่",
                "เช็คทางลมกลับ (return air) ไม่ถูกบัง",
            ],
            tools=["ไฟฉาย", "อุปกรณ์, (ตามหน้างาน)",],
            notes=["อาการนี้เจอบ่อยในห้องที่ไม่ได้ล้างแอร์นาน"],
        )
    # 3) มีน้ำแข็งเกาะที่คอยส์เย็นไหม
    coil_iced = _ask_yesno_with_ctx(ctx, "coil_iced", "มีน้ำแข็งเกาะที่คอยส์เย็นหรือไม่? (y/n): ", ask_yes_no_fn)
    if coil_iced:
        return _make_result(
            title="แอร์ไม่เย็น: คอยส์เย็นมีน้ำแข็ง",
            confidence=88,
            causes=[
                "น้ำยาแอร์ขาดฝรั่ว (ความดันต่ำทำให้คอยส์มีน้ำแข็ง)",
                "ฟิลเตอร์ตัน/ลมผ่านน้อย (ทำให้คอยส์เย็นเย็นจัด)",
            ],
            checks=[
                "ปิดแอร์ให้ละลายน้ำแข็งก่อน (เพื่อไม่ให้คอมทำงานหนัก)",
                "เช็คฟิลเตอร์/ทางลม",
                "ถ้ามีช่างแอร์: เช็คแรงดันน้ำยาและรอยรั่ว",
            ],
            tools=["เทอร์โมมิเตอร์", "แคลมป์มิเตอร์", "เกจวัดน้ำยา (ถ้ามี)"],
            notes=["ถ้าน้ำแข็งเกาะ ห้ามเปิดนาน เสี่ยงคอมเสีย"],
        )
    # 4) คอมเพรสเ๙อร์ด้านนอกทำงานไหม
    compressor_running = ask_yesno_with_ctx(ctx, "compressor_running", "คอมเพรสเชอร์ด้านนอกทำงานปกติหรือไม่? (y/n): ", ask_yes_no_fn)
    if not compressor_running:
        return _make_result(
            title="แอร์ไม่เย็น: คอมเพรสเชอร์ไม่ทำงาน",
            confidence=85,
            causes=[
                "คาปาชิเตอร์คอมเพรสเชอร์เสีย (ถ้ามี)",
                "โอเวอร์โหลดตัด",
                "แผงคอนโทร/รีเลย/คอนแทรคเตอร์มีปัญหา",
                "ไฟไม่เข้า outdoor unit",
            ],
            checks=[
                "ฟัง/ดูว่าคอยส์ร้อนหมุนหรือไม่ (บางรุ่นคอมไม่ทำงานพัดลมก็ไม่หมุน)",
                "เช็คเบรคเกอร์/ฟิวส์/คอนแน็คเตอร์สายหลวม",
                "จัดแรงดันที่ขี่วจ่ายไฟ outdoor (ถ้าปลอดภัยและทำได้)",
            ],
            tools=["มัลติมิเตอร์", "แคลมป์มิเตอร์"],
            notes=["ถ้าคอมไม่ทำงานจะมีแค่ลม แต่ไม่เย็น"],
        )
    # 5) ถ้าทุกอย่างดูทำงานปกติแต่ไม่เย็น -> โยงไปยังน้ำยา/คอยส์ร้อน
    return _make_result(
        title="แอร์ไม่เย็น: ระบบทำงานแต่ความเย็นไม่พอ",
        confidence=70,
        causes=[
            "น้ำยาแอร์ขาด/เริ่มรั่ว",
            "คอยส์ร้อนสกปรก ระบายความร้อนไม่ดี",
            "พัดลมคอยส์ร้อนหมุนช้า",
        ] + base_causes,
        checks=[
            "เช็คคอยส์ร้อนสกปรก/มีสิ่งขวางลม",
            "เช็คอุณภมูิลมออก (เปรัยบเทียบก่อนและหลัง)",
            "ถ้ามีช่างแอร์: เช็คแรงดันน้ำยาแอร์",
        ] + base_checks,
        tools=base_tools or ["แคลมป์มิเตอร์", "เทอร์โมมิเตอร์"],
        notes=["เคสนี้มักต้องตรวจ outdoor unit และสภาพน้ำยาเพิ่มเติม"],
        )
            
                
    
