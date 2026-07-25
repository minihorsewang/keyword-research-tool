import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
INPUT_DIR = Path(__file__).resolve().parent.parent / "input"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def load_json(filename):
    path = CONFIG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_config_path(filename):
    return CONFIG_DIR / filename


def ensure_dirs():
    for d in [INPUT_DIR, OUTPUT_DIR, LOGS_DIR, CONFIG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def get_input_files():
    csv_files = []
    for ext in ["*.csv", "*.tsv", "*.txt"]:
        csv_files.extend(INPUT_DIR.glob(ext))
    return sorted(csv_files)


def format_tw_currency(value):
    if value is None or value == "":
        return ""
    try:
        return f"NT${float(value):,.0f}"
    except (ValueError, TypeError):
        return str(value)


def safe_float(value, default=0.0):
    if value is None or value == "":
        return default
    try:
        cleaned = str(value).replace(",", "").replace(" ", "")
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    if value is None or value == "":
        return default
    try:
        cleaned = str(value).replace(",", "").replace(" ", "")
        if cleaned.strip() == "< 10":
            return 5
        return int(float(cleaned))
    except (ValueError, TypeError):
        return default
