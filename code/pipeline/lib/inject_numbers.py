"""Stage 05 — Inject frozen numbers into LaTeX via {{NUM:key}} placeholders.

Usage:
    python inject_numbers.py --config <contest.yaml> --tex paper/src/main.tex [--out paper/src/main.tex]

Replaces {{NUM:key}} with the frozen value (formatting: up to 6 significant
decimals, trailing zeros trimmed). Unknown key -> hard FAIL (no silent blanks).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import (PASS, contest_workdir, enable_utf8_stdout, load_config,
                    print_banner, read_json)

PLACEHOLDER = re.compile(r"\{\{NUM:([A-Za-z0-9_]+)\}\}")


def fmt(v) -> str:
    if isinstance(v, float):
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        return s if s else "0"
    return str(v)


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--tex", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()

    cfg = load_config(args.config)
    frozen_path = contest_workdir(cfg) / "04_solve" / "frozen_numbers.json"
    if not frozen_path.exists():
        print(f"[FAIL] frozen_numbers.json 不存在: {frozen_path}（先跑 Stage 04 freeze）")
        return 2
    frozen = {k: v for k, v in read_json(frozen_path).items() if not k.startswith("_")}

    tex = Path(args.tex)
    text = tex.read_text(encoding="utf-8")
    missing = []

    def sub(m):
        key = m.group(1)
        if key not in frozen:
            missing.append(key)
            return m.group(0)
        return fmt(frozen[key]["value"])

    new_text = PLACEHOLDER.sub(sub, text)

    print_banner("inject_numbers")
    if missing:
        print(f"[FAIL] 未冻结的 key: {sorted(set(missing))} —— 先把这些数字 freeze 再注入")
        return 1
    out = Path(args.out) if args.out else tex
    out.write_text(new_text, encoding="utf-8")
    n = len(PLACEHOLDER.findall(text))
    print(f"[{PASS}] injected {n} numbers -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
