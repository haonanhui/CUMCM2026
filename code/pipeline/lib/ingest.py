"""Stage 00 — Ingest: build manifest.json + extract problem text + convert attachments.

Usage:
    python ingest.py --config code/pipeline/config/contest.yaml [--dry-run]

Reads official_dir from contest.yaml, copies everything into
data/contest/<contest>/<problem>/official/ (read-only afterwards), then extracts:
  .pdf  -> text into 00_ingest/problem.md
  .docx -> paragraphs+tables into 00_ingest/problem.md
  .xlsx -> one CSV per sheet into 00_ingest/data/
  .csv  -> copied into 00_ingest/data/
  other -> copied unchanged into 00_ingest/data/ (status UNPARSED)
Files > 50MB: hash + register only (status SKIPPED, UNVERIFIED content).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from common import (FAIL, PASS, UNVERIFIED, WARN, contest_workdir,
                    enable_utf8_stdout, load_config, print_banner,
                    sha256_file, write_json)

LARGE_FILE_BYTES = 50 * 1024 * 1024


def extract_pdf(pdf_path: Path) -> tuple[str, str]:
    """Return (text, status). Chinese PDFs sometimes extract garbled -> WARN."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        parts = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            parts.append(f"[PDF p.{i + 1}]\n{t}")
        text = "\n\n".join(parts)
        # crude CJK garbling heuristic: many replacement chars / no CJK at all
        cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        status = PASS if (len(text.strip()) > 0 and cjk > 20) else WARN
        if status == WARN:
            text += "\n\n[WARN] 文本提取质量存疑（缺中文或空文本），需人工核对或 OCR。\n"
        return text, status
    except Exception as e:  # noqa: BLE001
        return f"[FAIL] pypdf 提取失败: {e}", FAIL


def extract_docx(docx_path: Path) -> tuple[str, str]:
    try:
        import docx  # python-docx

        d = docx.Document(str(docx_path))
        parts = [p.text for p in d.paragraphs if p.text.strip()]
        for tbl in d.tables:
            rows = ["\t".join(c.text.strip() for c in r.cells) for r in tbl.rows]
            parts.append("[表格]\n" + "\n".join(rows))
        return "\n\n".join(parts), PASS
    except Exception as e:  # noqa: BLE001
        return f"[FAIL] python-docx 提取失败: {e}", FAIL


def extract_xlsx(xlsx_path: Path, out_dir: Path) -> tuple[list[str], str]:
    """One CSV per sheet. Returns (output files, status)."""
    import pandas as pd

    outputs, statuses = [], []
    xls = pd.ExcelFile(str(xlsx_path))
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        safe_sheet = str(sheet).replace("/", "_").replace("\\", "_")
        out = out_dir / f"{xlsx_path.stem}__{safe_sheet}.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        outputs.append(str(out))
        statuses.append(PASS if len(df) > 0 else WARN)
    return outputs, PASS if all(s == PASS for s in statuses) else WARN


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    work = contest_workdir(cfg)
    official = work / "official"
    ingest_dir = work / "00_ingest"
    data_dir = ingest_dir / "data"
    problem_md = ingest_dir / "problem.md"

    src = Path(cfg["official_dir"])
    if not src.is_dir():
        print(f"[FAIL] official_dir 不存在: {src}")
        return 2

    print_banner(f"Stage 00 ingest: {cfg['contest']}/{cfg['problem']}")
    if args.dry_run:
        print(f"[dry-run] work dir = {work}")
        for f in sorted(src.rglob("*")):
            if f.is_file():
                print(f"  would ingest: {f.relative_to(src)} ({f.stat().st_size} bytes)")
        return 0

    # 1. copy official files (never modify originals afterwards)
    if not official.exists():
        shutil.copytree(src, official)
        print(f"[OK] copied {src} -> {official}")
    else:
        print(f"[OK] official/ already exists, skip copy (idempotent)")

    data_dir.mkdir(parents=True, exist_ok=True)
    problem_md.write_text("", encoding="utf-8")

    manifest = {
        "contest": cfg["contest"],
        "problem": cfg["problem"],
        "official_dir": str(src),
        "generated_by": "code/pipeline/lib/ingest.py",
        "files": [],
    }

    for f in sorted(official.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(official).as_posix()
        entry = {
            "file": rel,
            "size_bytes": f.stat().st_size,
            "sha256": sha256_file(f),
            "extract": UNVERIFIED,
            "outputs": [],
        }
        suffix = f.suffix.lower()
        if f.stat().st_size > LARGE_FILE_BYTES:
            entry["extract"] = "SKIPPED_LARGE"
            entry["note"] = ">50MB: hash registered only, content UNVERIFIED"
        elif suffix == ".pdf":
            text, st = extract_pdf(f)
            entry["extract"], entry["outputs"] = st, ["00_ingest/problem.md"]
            with open(problem_md, "a", encoding="utf-8") as fh:
                fh.write(f"\n\n## 来源文件: {rel}\n\n{text}\n")
        elif suffix == ".docx":
            text, st = extract_docx(f)
            entry["extract"], entry["outputs"] = st, ["00_ingest/problem.md"]
            with open(problem_md, "a", encoding="utf-8") as fh:
                fh.write(f"\n\n## 来源文件: {rel}\n\n{text}\n")
        elif suffix == ".xlsx":
            outs, st = extract_xlsx(f, data_dir)
            entry["extract"] = st
            entry["outputs"] = [str(Path(o).relative_to(work)).replace("\\", "/") for o in outs]
        elif suffix == ".csv":
            shutil.copy2(f, data_dir / f.name)
            entry["extract"], entry["outputs"] = PASS, [f"00_ingest/data/{f.name}"]
        else:
            shutil.copy2(f, data_dir / f.name)
            entry["extract"], entry["outputs"] = "UNPARSED", [f"00_ingest/data/{f.name}"]
        manifest["files"].append(entry)

    # data README (agent fills column meanings later during analysis)
    (data_dir / "README.md").write_text(
        "# 附件数据说明\n\n本目录由 ingest 自动生成。每张表列含义、单位、量纲需在 Stage 01 数据预检时人工补充。\n",
        encoding="utf-8",
    )

    write_json(ingest_dir / "manifest.json", manifest)

    # contest README
    n_pass = sum(1 for e in manifest["files"] if e["extract"] == PASS)
    n_warn = sum(1 for e in manifest["files"] if e["extract"] == WARN)
    n_fail = sum(1 for e in manifest["files"] if e["extract"] == FAIL)
    readme = work / "README.md"
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text(
        f"# {cfg['contest']} {cfg['problem']} 题工作目录\n\n"
        f"- 官方文件数: {len(manifest['files'])}\n"
        f"- 提取状态: PASS={n_pass} WARN={n_warn} FAIL={n_fail}\n"
        f"- 数据表清单: 见 00_ingest/manifest.json\n\n"
        f"official/ 只读；所有产物写入 00_ingest/ 及后续 stage 目录。\n",
        encoding="utf-8",
    )

    print(f"[OK] manifest -> {ingest_dir / 'manifest.json'}")
    print(f"     files={len(manifest['files'])} PASS={n_pass} WARN={n_warn} FAIL={n_fail}")
    if n_fail:
        print("[FAIL] 有文件提取失败，人工检查后再进 Stage 01")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
