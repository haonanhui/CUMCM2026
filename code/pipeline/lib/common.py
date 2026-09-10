# CUMCM/HSC Contest pipeline shared utilities.
# All file IO must be explicit UTF-8 (Windows default is GBK).
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

# Project canonical root = three levels above this file (code/pipeline/lib/common.py)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

PASS, WARN, FAIL, UNVERIFIED = "PASS", "WARN", "FAIL", "UNVERIFIED"


def enable_utf8_stdout() -> None:
    """Avoid UnicodeEncodeError when printing Chinese on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def load_config(config_path: str | Path) -> dict:
    """Load contest.yaml; resolve paths relative to PROJECT_ROOT when not absolute."""
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in ("official_dir",):
        if key in cfg and cfg[key] and not Path(cfg[key]).is_absolute():
            cfg[key] = str((PROJECT_ROOT / cfg[key]).resolve())
    cfg["_config_path"] = str(config_path)
    cfg["_project_root"] = str(PROJECT_ROOT)
    return cfg


def contest_workdir(cfg: dict) -> Path:
    """data/contest/<contest>/<problem>/ — canonical working directory."""
    return Path(cfg["_project_root"]) / "data" / "contest" / cfg["contest"] / str(cfg["problem"])


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def write_json(path: str | Path, obj) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


def read_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_md(path: str | Path, title: str, body: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n\n# {title}\n\n{body}\n")


def print_banner(stage: str) -> None:
    print(f"=== [{stage}] ===")
