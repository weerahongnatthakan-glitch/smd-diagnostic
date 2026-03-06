from __future__ import annotations

import os
from typing import Iterable, Optional

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLOR = True
except Exception:
    COLOR = False

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def c(text: str, color: str) -> str:
    if not COLOR:
        return text
    return color + text + Style.RESET_ALL

def header(title: str, subtitle: Optional[str] = None) -> None:
    line = "=" * 44
    print(c(line, Fore.CYAN) if COLOR else line)
    print(c(f"{title}", Fore.CYAN) if COLOR else title)
    if subtitle:
        print(subtitle)
    print(c(line, Fore.CYAN) if COLOR else line)

def section(name: str) -> None:
    print("\n" + (c(f"[{name}]", Fore.YELLOW) if COLOR else f"[{name}]"))

def menu(title: str, items: Iterable[tuple[str, str]]) -> str:
    section(title)
    for k, label in items:
        print(f"{k}) {label}")
    return input("> ").strip()

def pause(msg: str = "กด Enter เพื่อไปต่อ...") -> None:
    input(msg)