"""G1-G6 gate status checker — cold-start self-audit for the whole pipeline.

Usage:
    python gates.py --config <contest.yaml>

Checks artifact existence per stage and prints PASS/FAIL per gate so any agent
session can see exactly where the pipeline stands. Novelty verdicts are read
from 03_model/novelty_gate.json; rerun verification from 04_solve/verify_report.json.
"""
from __future__ import annotations

import argparse
import sys

from common import (FAIL, PASS, contest_workdir, enable_utf8_stdout,
                    load_config, print_banner, read_json)

GATES = [
    ("G1", "题目解析完整", ["00_ingest/manifest.json", "00_ingest/problem.md"]),
    ("G2", "方法齐备", ["02_retrieve/candidates.md"]),
    ("G3", "模型可求解+新颖性记录", ["03_model/建模方案.md", "03_model/novelty_gate.json"]),
    ("G4", "数字可复现", ["04_solve/frozen_numbers.json", "04_solve/复现清单.json"]),
    ("G5", "论文合规", ["paper/main.pdf"]),
    ("G6", "提交就绪", ["06_audit/audit_report.md"]),
]


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    work = contest_workdir(cfg)
    print_banner(f"gates: {cfg['contest']}/{cfg['problem']}")

    status = {}
    for gate, desc, artifacts in GATES:
        missing = [a for a in artifacts if not (work / a).exists()]
        status[gate] = {"desc": desc, "verdict": FAIL if missing else PASS, "missing": missing}
        print(f"[{status[gate]['verdict']}] {gate} {desc}" + (f" — missing: {missing}" if missing else ""))

    # enrich G3 with novelty verdicts
    ng = work / "03_model" / "novelty_gate.json"
    if ng.exists():
        rulings = read_json(ng).get("rulings", [])
        verdicts = {r["question"]: r["verdict"] for r in rulings}
        if any(v == FAIL for v in verdicts.values()):
            status["G3"]["verdict"] = FAIL
            status["G3"]["novelty"] = verdicts
        print(f"      novelty: {verdicts if verdicts else 'n/a'}")

    # enrich G4 with rerun verification
    vr = work / "04_solve" / "verify_report.json"
    if vr.exists():
        rep = read_json(vr)
        ok = all(r.get("rerun_verified") for r in rep.get("rerun", [])) and rep.get("rerun")
        if not ok:
            status["G4"]["verdict"] = FAIL
        print(f"      rerun_verified: {ok}")

    done = sum(1 for g in GATES if status[g[0]]["verdict"] == PASS)
    print(f"--- {done}/{len(GATES)} gates PASS ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
