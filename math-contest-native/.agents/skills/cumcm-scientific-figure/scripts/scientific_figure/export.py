"""Final-size export with fail-closed QA and provenance."""
import hashlib
import json
import logging
import warnings
from pathlib import Path

from PIL import Image

from .qa import check_figure, check_exports
from .style import profile, style_context


class FontLogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        message = record.getMessage()
        if "glyph" in message.lower() or "substitut" in message.lower():
            self.messages.append(message)


def export_bundle(bundle, directory, name, *, provenance):
    if not name or Path(name).name != name or "." in name:
        raise ValueError("Use a plain figure name without a suffix")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / name
    suffixes = (".pdf", ".svg", ".png", ".gray.png", ".caption.txt", ".qa.json")
    if any(stem.with_suffix(s).exists() for s in suffixes):
        raise FileExistsError("Refusing to replace previous figure evidence: " + str(stem))
    font_log = FontLogCapture()
    logger = logging.getLogger("matplotlib")
    logger.addHandler(font_log)
    try:
        with style_context(bundle.style), warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            artist_qa = check_figure(bundle)
            # Freeze geometry after final renderer layout so PDF/SVG do not reflow labels differently.
            bundle.figure.set_layout_engine("none")
            for ext in ("pdf", "svg", "png"):
                bundle.figure.savefig(stem.with_suffix("." + ext), dpi=profile()["export"]["dpi"], facecolor="white")
            export_qa = check_exports(stem, bundle.figure)
    finally:
        logger.removeHandler(font_log)
    missing = font_log.messages + [str(w.message) for w in captured if "Glyph" in str(w.message) and "missing" in str(w.message)]
    with Image.open(stem.with_suffix(".png")) as image:
        image.convert("L").save(stem.with_suffix(".gray.png"), dpi=(600, 600))
    stem.with_suffix(".caption.txt").write_text(bundle.caption, encoding="utf-8")
    report = {"schema": "scientific-figure-qa/v1", "profile": bundle.style["id"],
              "profile_sha256": hashlib.sha256(json.dumps(bundle.style, sort_keys=True).encode()).hexdigest(),
              "kind": bundle.kind, "synthetic": bundle.synthetic, "provenance": provenance,
              "artist": artist_qa, "export": export_qa, "missing_glyph_warnings": missing,
              "human_review": "pending", "visual_review": "pending",
              "paper_math_font_match": "UNVERIFIED until checked against the target paper PDF",
              "status": "PASS" if artist_qa["status"] == export_qa["status"] == "PASS" and not missing else "FAIL"}
    report["files"] = {stem.with_suffix(s).name: hashlib.sha256(stem.with_suffix(s).read_bytes()).hexdigest()
                       for s in suffixes if s != ".qa.json"}
    stem.with_suffix(".qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
