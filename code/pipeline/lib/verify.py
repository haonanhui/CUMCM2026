"""Stage 04 — Verify: rerun solution scripts, diff numeric outputs, sanity checks.

Usage:
    python verify.py --config <contest.yaml> --scripts code/solve/q1.py [code/solve/q2.py ...]
    python verify.py --config <contest.yaml> --rerun q1        # rerun only, keep first outputs
    python verify.py --config <contest.yaml> --sanity 04_solve/q1/checks.json

Rerun protocol:
  1. snapshot current outputs in 04_solve/<q>/ to 04_solve/<q>/_snapshot/
  2. clear outputs, rerun script (subprocess, same interpreter)
  3. diff every CSV in snapshot vs rerun with numeric tolerance (default 1e-6)
  4. verdict per script: rerun_verified true/false

Sanity checks schema (checks.json):
  {"file": "result.csv", "column": "area", "min": 0, "max": null}
null means unbounded on that side.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

from common import (FAIL, PASS, UNVERIFIED, WARN, contest_workdir,
                    enable_utf8_stdout, load_config, print_banner, write_json)

SNAPSHOT = "_snapshot"


def _read_csv_numeric(path: Path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    header, body = rows[0], rows[1:]
    numeric = []
    for row in body:
        vals = []
        for cell in row:
            try:
                vals.append(float(cell))
            except ValueError:
                vals.append(None)
        numeric.append(vals)
    return header, numeric


def diff_csv(a: Path, b: Path, tol: float) -> tuple[str, str]:
    ha, na = _read_csv_numeric(a)
    hb, nb = _read_csv_numeric(b)
    if ha != hb:
        return FAIL, f"header mismatch: {ha} vs {hb}"
    if len(na) != len(nb):
        return FAIL, f"row count {len(na)} vs {len(nb)}"
    for i, (ra, rb) in enumerate(zip(na, nb)):
        for j, (va, vb) in enumerate(zip(ra, rb)):
            if va is None and vb is None:
                continue
            if (va is None) != (vb is None):
                return FAIL, f"cell[{i}][{j}] type mismatch: {va!r} vs {vb!r}"
            if abs(va - vb) > tol + tol * abs(va):
                return FAIL, f"cell[{i}][{j}] {ha[j]}={va} vs {vb} (>{tol})"
    return PASS, f"{len(na)} rows all within tol={tol}"


def rerun(script: Path, qdir: Path, tol: float) -> dict:
    snap = qdir / SNAPSHOT
    csvs = sorted(qdir.glob("*.csv"))
    if snap.exists():
        shutil.rmtree(snap)
    if csvs:
        snap.mkdir(parents=True, exist_ok=True)
        for c in csvs:
            shutil.copy2(c, snap / c.name)
    for c in csvs:  # clear outputs
        c.unlink()

    proc = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=str(Path.cwd()),
    )
    if proc.returncode != 0:
        return {"script": str(script), "verdict": FAIL,
                "detail": f"rerun exit={proc.returncode}\n{proc.stderr[-2000:]}"}

    results = []
    verdict = PASS
    for old in (snap.glob("*.csv") if snap.exists() else []):
        new = qdir / old.name
        if not new.exists():
            verdict = FAIL
            results.append({"file": old.name, "verdict": FAIL, "detail": "rerun did not reproduce file"})
            continue
        v, detail = diff_csv(old, new, tol)
        verdict = v if v == FAIL else verdict
        results.append({"file": old.name, "verdict": v, "detail": detail})
    return {
        "script": str(script),
        "verdict": verdict,
        "rerun_verified": verdict == PASS,
        "tolerance": tol,
        "files": results,
        "stdout_tail": proc.stdout[-1500:],
    }


def sanity(checks_file: Path) -> list[dict]:
    import json

    with open(checks_file, "r", encoding="utf-8") as f:
        checks = json.load(f)
    out = []
    for ck in checks:
        path, col = Path(ck["file"]), ck.get("column")
        lo, hi = ck.get("min"), ck.get("max")
        header, rows = _read_csv_numeric(path)
        idx = header.index(col) if col in header else None
        if idx is None:
            out.append({"check": ck, "verdict": UNVERIFIED, "detail": f"column {col!r} not found in {path}"})
            continue
        bad = []
        for i, row in enumerate(rows):
            v = row[idx]
            if v is None:
                continue
            if (lo is not None and v < lo) or (hi is not None and v > hi):
                bad.append((i, v))
        out.append({
            "check": ck,
            "verdict": PASS if not bad else WARN,
            "detail": "all in range" if not bad else f"{len(bad)} violations, first: {bad[:3]}",
        })
    return out


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--scripts", nargs="*", default=[], help="solution scripts to rerun")
    ap.add_argument("--tolerance", type=float, default=1e-6)
    ap.add_argument("--sanity", help="checks.json for range sanity")
    args = ap.parse_args()

    cfg = load_config(args.config)
    work = contest_workdir(cfg)
    solve_dir = work / "04_solve"
    print_banner("Stage 04 verify")

    report = {"rerun": [], "sanity": []}
    for s in args.scripts:
        script = Path(s)
        qdir = solve_dir / script.stem
        report["rerun"].append(rerun(script, qdir, args.tolerance))
        r = report["rerun"][-1]
        print(f"[{r['verdict']}] rerun {script.name}: {r.get('detail', 'ok')[:120]}")

    if args.sanity:
        report["sanity"] = sanity(Path(args.sanity))
        for c in report["sanity"]:
            print(f"[{c['verdict']}] sanity {c['check'].get('file')}:{c['check'].get('column')} — {c['detail'][:120]}")

    write_json(solve_dir / "verify_report.json", report)
    hard = any(r["verdict"] == FAIL for r in report["rerun"])
    print(f"[OK] report -> {solve_dir / 'verify_report.json'}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
