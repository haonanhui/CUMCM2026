"""Stage 04/05 — Frozen numbers: the ONLY legal source of numbers for the paper.

Usage:
    python frozen_numbers.py freeze  --config <yaml> --input 04_solve/frozen_input.json
    python frozen_numbers.py list    --config <yaml>
    python frozen_numbers.py check   --config <yaml> --tex paper/src/main.tex
    python frozen_numbers.py refreeze --config <yaml> --subquestion Q1 --reason "改了约束"

freeze input schema (frozen_input.json, produced by solver scripts):
{
  "q1_obj":  {"value": 1234.56,   "source_file": "code/solve/q1.py", "source_line": 42, "tolerance": 0.01},
  ...
}
Paper writing MUST reference {{NUM:key}} placeholders and run inject_numbers.py;
any literal number in the .tex not present in frozen_numbers.json is flagged by `check`.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import (FAIL, PASS, WARN, contest_workdir, enable_utf8_stdout,
                    load_config, print_banner, read_json, write_json)


def frozen_path(cfg: dict) -> Path:
    return contest_workdir(cfg) / "04_solve" / "frozen_numbers.json"


def load_frozen(cfg: dict) -> dict:
    p = frozen_path(cfg)
    return read_json(p) if p.exists() else {}


def cmd_freeze(cfg: dict, args) -> int:
    entries = read_json(args.input)
    frozen = load_frozen(cfg)
    # three-step protocol: thaw happens implicitly; log the reason if refreezing
    changed = [k for k, v in entries.items()
               if k not in frozen or frozen[k].get("value") != v.get("value")]
    frozen.update(entries)
    frozen["_meta"] = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(Path(args.input)),
        "changed_keys": changed,
    }
    write_json(frozen_path(cfg), frozen)
    print(f"[OK] frozen {len(entries)} numbers ({len(changed)} changed) -> {frozen_path(cfg)}")
    return 0


def cmd_list(cfg: dict, _args) -> int:
    frozen = {k: v for k, v in load_frozen(cfg).items() if not k.startswith("_")}
    for k, v in sorted(frozen.items()):
        print(f"  {k:24s} = {v.get('value')!r}  (src {v.get('source_file')}:{v.get('source_line')})")
    print(f"total: {len(frozen)}")
    return 0


_NUM_RE = re.compile(r"(?<![\w.])\d+\.\d+(?![\w%])")  # decimal literals only; ints are too noisy for now


def cmd_check(cfg: dict, args) -> int:
    frozen = {k: v for k, v in load_frozen(cfg).items() if not k.startswith("_")}
    values = {round(float(v["value"]), 10) for v in frozen.values()
              if isinstance(v.get("value"), (int, float))}
    tex = Path(args.tex)
    text = tex.read_text(encoding="utf-8")
    missing = sorted({m for m in _NUM_RE.findall(text)
                      if round(float(m), 10) not in values})
    report = {"tex": str(tex), "unfrozen_numbers": missing,
              "verdict": PASS if not missing else WARN}
    write_json(tex.parent / "frozen_check.json", report)
    print(f"[{report['verdict']}] {len(missing)} decimal literals not in frozen_numbers.json")
    for m in missing:
        print(f"  - {m}")
    if missing:
        print("  修法：把数字换成 {{NUM:key}} 占位符并跑 inject_numbers.py，或补进 frozen_input.json。")
    return 0 if not missing else 1


def cmd_refreeze(cfg: dict, args) -> int:
    frozen = load_frozen(cfg)
    log = frozen.setdefault("_refreeze_log", [])
    log.append({"subquestion": args.subquestion, "reason": args.reason,
                "at": datetime.now(timezone.utc).isoformat()})
    frozen.setdefault("_meta", {})["updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(frozen_path(cfg), frozen)
    print(f"[OK] refreeze logged for {args.subquestion}: {args.reason}")
    return 0


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["freeze", "list", "check", "refreeze"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--input")
    ap.add_argument("--tex")
    ap.add_argument("--subquestion")
    ap.add_argument("--reason")
    args = ap.parse_args()

    cfg = load_config(args.config)
    print_banner(f"frozen_numbers {args.command}")
    if args.command == "freeze":
        return cmd_freeze(cfg, args)
    if args.command == "list":
        return cmd_list(cfg, args)
    if args.command == "check":
        return cmd_check(cfg, args)
    return cmd_refreeze(cfg, args)


if __name__ == "__main__":
    sys.exit(main())
