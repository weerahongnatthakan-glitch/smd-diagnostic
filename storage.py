from __future__ import annotations

import json
from pathlib import Path
from typing import List

from models import CaseRecord

DATA_DIR = Path(__file__).parent / "DATA"
CASES_FILE = DATA_DIR / "cases.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _safe_read_json(path: Path):
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def load_cases(path: Path = CASES_FILE) -> List[CaseRecord]:
    _ensure_data_dir()
    raw = _safe_read_json(path)
    cases: List[CaseRecord] = []

    for item in raw:
        if isinstance(item, dict):
            try:
                cases.append(CaseRecord(**item))
            except TypeError:
                pass

    return cases


def save_cases(cases: List[CaseRecord], path: Path = CASES_FILE) -> None:
    _ensure_data_dir()
    payload = [case.to_dict() for case in cases]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_case(record: CaseRecord, path: Path = CASES_FILE) -> None:
    cases = load_cases(path)
    cases.append(record)
    save_cases(cases, path)