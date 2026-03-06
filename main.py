from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from cli import run_cli

APP_NAME = "Smart Maintenance Diagnostic (SDM)"
APP_VERSION = "0.2"


def print_header() -> None:
    print("=" * 40)
    print(f"{APP_NAME} v{APP_VERSION}")
    print("ผู้ช่วยวิเคราะห์อาการเสียของอาคาร (CLI)")
    print("=" * 40)


def run() -> None:
    print_header()
    run_cli(APP_NAME, APP_VERSION)


if __name__ == "__main__":
    run()