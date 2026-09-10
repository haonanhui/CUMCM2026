"""Stage 03 — Novelty gate: record delta claims, rule PASS/WARN/FAIL.

Usage:
    python novelty_gate.py --input 03_model/deltas.json --config <contest.yaml>

Input schema (deltas.json, filled by agent during modeling):
{
  "Q1": {
    "baseline": "加权线性规划",
    "baseline_precedent_freq": "high" | "medium" | "low",
    "deltas": [
      {"layer": "b", "claim": "加入时空耦合约束 ...", "evidence": "建模方案.md §2.3"}
    ]
  }
}

Ruling (see stages/03_model_novelty.md):
  - >=1 delta in layers b/c/d                        -> PASS
  - only layer-a deltas AND baseline_precedent_freq=high -> WARN (algorithm reskin)
  - only layer-a deltas AND freq=medium/low          -> PASS
  - no deltas                                        -> FAIL (must not enter stage 04)
"""
from __future__ import annotations

import argparse
import sys

from common import (FAIL, PASS, WARN, contest_workdir, enable_utf8_stdout,
                    load_config, print_banner, read_json, write_json)

LAYERS = {"a": "方法层", "b": "模型层", "c": "数据层", "d": "验证层"}
STRONG_LAYERS = {"b", "c", "d"}


def rule(question: str, spec: dict) -> dict:
    deltas = spec.get("deltas", [])
    layers = {d.get("layer", "") for d in deltas}
    freq = spec.get("baseline_precedent_freq", "high")
    if not deltas:
        verdict, reason = FAIL, "无 delta 声明：必须换方案或补角度，不允许进入 04"
    elif layers & STRONG_LAYERS:
        strong = sorted(layers & STRONG_LAYERS)
        verdict = PASS
        reason = f"存在强层 delta（{'/'.join(LAYERS[x] for x in strong)}）：模型层/数据层/验证层差异最有说服力"
    elif freq == "high":
        verdict = WARN
        reason = "仅有方法层 delta 且 baseline 先例频率=高：算法换皮，撞车风险中等，需真人决定是否接受"
    else:
        verdict = PASS
        reason = f"仅有方法层 delta，但 baseline 先例频率={freq}，撞车风险可接受"
    return {
        "question": question,
        "baseline": spec.get("baseline", ""),
        "baseline_precedent_freq": freq,
        "deltas": deltas,
        "verdict": verdict,
        "reason": reason,
        "stop_point": "WARN/FAIL 均须真人确认后才能进入 Stage 04",
    }


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="deltas.json 路径")
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    specs = read_json(args.input)
    print_banner("Stage 03 novelty gate")

    results = {q: rule(q, spec) for q, spec in specs.items()}
    out = contest_workdir(cfg) / "03_model" / "novelty_gate.json"
    write_json(out, {"rulings": list(results.values())})

    hard_fail = False
    for q, r in results.items():
        print(f"[{r['verdict']}] {q}: baseline={r['baseline']} | {r['reason']}")
        if r["verdict"] == FAIL:
            hard_fail = True
    print(f"[OK] written -> {out}")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
