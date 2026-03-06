from __future__ import annotations

from diagnosis import run_diagnosis
from models import CaseRecord
from storage import append_case
from ui import header, menu, pause, clear


def main_menu() -> str:
    print("\nเมนูหลัก")
    print("1) เริ่มวิเคราะห์อาการ")
    print("2) เกี่ยวกับโปรแกรม")
    print("0) ออก")
    return input("> ").strip()


def about(app_name: str, app_version: str) -> None:
    print("\nเกี่ยวกับโปรแกรม")
    print(f"- ชื่อ: {app_name}")
    print(f"- เวอร์ชัน: {app_version}")
    print("- เป้าหมาย: ช่วยช่างวิเคราะห์อาการ -> สาเหตุ -> ขั้นตอนการตรวจ")
    print("- สถานะ: ใช้งานจริงเบื้องต้น")


def ask_choice(prompt, choices):
    print("\n" + prompt)
    for key, label in choices:
        print(f"{key}) {label}")

    valid = [k for k, _ in choices]

    while True:
        ans = input("> ").strip()
        if ans in valid:
            return ans
        print("เลือกใหม่อีกครั้ง")


def ask_yes_no(prompt):
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("พิมพ์ y หรือ n")


def run_analysis() -> None:
    print("\nเลือกหมวด")
    print("1) แอร์")
    print("0) กลับ")

    category_choice = input("> ").strip()

    if category_choice == "0":
        return

    if category_choice != "1":
        print("\nตอนนี้ยังรองรับเฉพาะหมวดแอร์ก่อน")
        return

    print("\nอาการแอร์")
    print("1) แอร์ไม่เย็น")
    print("0) กลับ")

    symptom_choice = input("> ").strip()

    if symptom_choice == "0":
        return

    if symptom_choice != "1":
        print("\nตอนนี้ยังรองรับเฉพาะ 'แอร์ไม่เย็น' ก่อน")
        return

    print("\n[เริ่มวิเคราะห์]")

    result = run_diagnosis(
        category="ac",
        symptom="ac_not_cold",
        ask=ask_choice,
        ask_yes_no_fn=ask_yes_no,
    )

    result.display()

    record = CaseRecord(
        category="ac",
        symptom="ac_not_cold",
        result_title=result.title,
        confidence=result.confidence,
        causes=result.causes,
    )

    append_case(record)
    print("\n[บันทึกเคสแล้ว]")


def run_cli(app_name, app_version):
    while True:
        clear()
        header(f"{app_name} v{app_version}", "ผู้ช่วยวิเคราะห์อาการเสียของอาคาร")
        choice = menu("เมนูหลัก", [("1","เริ่มวิเคราะห์อาการ"), ("2","เกี่ยวกับโปรแกรม"), ("0","ออก")])

        if choice == "1":
            run_analysis()
            pause()
        elif choice == "2":
            show_about()
            pause()
        elif choice == "0":
            break