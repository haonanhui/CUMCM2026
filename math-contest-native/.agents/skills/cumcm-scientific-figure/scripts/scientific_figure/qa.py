"""Artist-level geometry/style checks plus independently opened export checks."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.mathtext import MathTextParser
from matplotlib.path import Path as MplPath
from matplotlib.text import Text
from matplotlib.ticker import NullLocator

from .style import profile, resolve_fonts
from .typography import prepare_text, CJK


def check_figure(bundle):
    fig = bundle.figure
    prepare_text(fig)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    failures = []
    def require(condition, category, detail):
        if not condition:
            failures.append({"category": category, "detail": detail})
    p = profile()
    tol = p["qa"]["stroke_tolerance"]
    fonts = resolve_fonts()
    faces = [FT2Font(fonts["latin_path"]), FT2Font(fonts["cjk_path"])]
    glyph_evidence = {}
    for text in fig.findobj(Text):
        value = text.get_text()
        if not text.get_visible() or not value.strip():
            continue
        mixed = hasattr(text, "_scientific_original")
        require(text.get_fontfamily() == ([fonts["cjk"]] if mixed else [fonts["latin"], fonts["cjk"]]), "font", value)
        require(text.get_math_fontfamily() == ("custom" if mixed else p["fonts"]["math"]), "math", value)
        require(text.get_fontsize() >= p["qa"]["min_font_pt"], "final-size", value)
        require(not re.search(r"\d[eE][+-]\d", value), "math", "literal scientific notation: " + value)
        plain = re.sub(r"\$[^$]*\$", "", value)
        for char in plain:
            if char.isspace():
                continue
            face = next((face for face in faces if face.get_char_index(ord(char))), None)
            require(face is not None, "font", "missing glyph " + char)
            if face:
                glyph_evidence[char] = face.family_name
                if char.isascii() and char.isalnum():
                    require(face.family_name == fonts["latin"], "mixed-text", char)
        if "$" in value:
            try:
                parsed = MathTextParser("path").parse(value, prop=text.get_fontproperties())
                actual_cjk = []
                for face, size, codepoint, x, y in parsed.glyphs:
                    require(not any(s in face.family_name.lower() for s in ("dejavu", "arial", "sans")),
                            "math", face.family_name)
                    glyph_evidence[chr(codepoint)] = face.family_name
                    if CJK.match(chr(codepoint)):
                        actual_cjk.append(chr(codepoint))
                        require(face.family_name == fonts["cjk"], "mixed-text", "wrong CJK face")
                require(actual_cjk == CJK.findall(value), "mixed-text", "CJK glyphs lost in mathtext: " + value)
            except (ValueError, RuntimeError) as error:
                require(False, "math", str(error))
        # Out-of-view tick labels have no rendered counterpart and are intentionally ignored.
        box = text.get_window_extent(renderer)
        tick_owner = next((axis for ax in fig.axes for axis in (ax.xaxis, ax.yaxis)
                           if any(text is t.label1 or text is t.label2 for t in axis.get_major_ticks())), None)
        if tick_owner:
            lo, hi = sorted(tick_owner.get_view_interval())
            tick = next(t for t in tick_owner.get_major_ticks() if text is t.label1 or text is t.label2)
            if not lo <= tick.get_loc() <= hi:
                continue
        eps = p["qa"]["clipping_tolerance_px"]
        require(box.x0 >= -eps and box.y0 >= -eps and box.x1 <= fig.bbox.x1 + eps and box.y1 <= fig.bbox.y1 + eps,
                "clipping", value)
    for ax in bundle.axes + bundle.secondary_axes:
        require(not ax.get_title(), "panel", "descriptive title belongs in the separate explanation")
        for text in ax.texts:
            anchor = ax.transAxes.inverted().transform(text.get_transform().transform(text.get_position()))
            if text not in bundle.panel_labels and anchor[1] > 1:
                require(False, "panel", "external explanatory text belongs in the separate explanation")
        require(all(s.get_visible() for s in ax.spines.values()), "axes", "hidden spine")
        require(all(abs(s.get_linewidth() - p["stroke"]["axes"]) < tol for s in ax.spines.values()), "stroke", "spine")
        require(not any(line.get_visible() for line in ax.get_xgridlines() + ax.get_ygridlines()), "axes", "grid")
        for axis in (ax.xaxis, ax.yaxis):
            require(not isinstance(axis.get_minor_locator(), NullLocator), "axes", "missing minor ticks")
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                require(tick.get_tickdir() == "in", "axes", "outward tick")
                require(abs(tick.tick1line.get_markeredgewidth() - p["stroke"]["axes"]) < tol,
                        "stroke", "tick")
                if not bundle.secondary_axes:
                    require(tick.tick1line.get_visible() and tick.tick2line.get_visible(), "axes", "missing top/right ticks")
        for line in ax.lines:
            require(line.get_linewidth() <= p["stroke"]["data"] + tol, "stroke", "abnormally thick line")
        legend = ax.get_legend()
        if legend:
            require(not legend.get_frame_on(), "legend", "frame")
            box = legend.get_window_extent(renderer)
            for line in bundle.data_lines:
                if line.axes is ax or (ax in bundle.axes and line.axes in bundle.secondary_axes):
                    points = line.get_transform().transform(line.get_xydata())
                    if line.get_linestyle() == "None":
                        overlap = any(box.contains(*xy) for xy in points)
                    else:
                        overlap = MplPath(points).intersects_bbox(box, filled=False)
                    require(not overlap, "legend", "overlaps " + line.get_label())
            for label in ax.texts:
                if label.get_visible() and label not in bundle.panel_labels:
                    # Annotation's union bbox contains empty corners between its text and arrow.
                    require(not box.overlaps(Text.get_window_extent(label, renderer)), "legend", "overlaps annotation text")
                    arrow = getattr(label, "arrow_patch", None)
                    if arrow is not None:
                        arrow_path = arrow.get_transform().transform_path(arrow.get_path())
                        require(not arrow_path.intersects_bbox(box, filled=False), "legend", "overlaps annotation arrow")
    for line in bundle.data_lines:
        require(abs(line.get_linewidth() - p["stroke"]["data"]) < tol, "stroke", line.get_label())
    for ax in bundle.axes:
        lines = [line for line in bundle.data_lines if line.axes is ax]
        signatures = [(l.get_linestyle(), l.get_marker(), l.get_fillstyle()) for l in lines]
        require(len(signatures) == len(set(signatures)), "grayscale", "duplicate visual encoding")
    boxes = [ax.get_position() for ax in bundle.axes]
    if len(boxes) > 1:
        require(np.ptp([b.width for b in boxes]) < p["qa"]["panel_size_tolerance"], "panel", "unequal widths")
        require(np.ptp([b.height for b in boxes]) < p["qa"]["panel_size_tolerance"], "panel", "unequal heights")
        for i, label in enumerate(bundle.panel_labels):
            require(label.get_text() == f"({chr(97+i)})", "panel", "numbering")
            require(label.get_position() == (p["layout"]["panel_x"], p["layout"]["panel_y"]), "panel", "label position")
            require(label.get_ha() == "right" and label.get_va() == "top", "panel", "not aligned left of y-axis at top")
            label_box = label.get_window_extent(renderer)
            require(label_box.x1 < label.axes.bbox.x0 and label_box.y1 <= label.axes.bbox.y1 + 0.1,
                    "panel", "label must be left of y-axis and not above top frame")
            for line in bundle.data_lines:
                if line.axes is label.axes:
                    points = line.get_transform().transform(line.get_xydata())
                    require(not MplPath(points).intersects_bbox(label_box, filled=False), "panel", "label obscures data")
        for i, box in enumerate(boxes):
            require(not any(box.overlaps(other) for other in boxes[i+1:]), "panel", "axes overlap")
        rows = {}
        for box in boxes:
            rows.setdefault(round(box.y0, 3), []).append(box)
        gaps = []
        for row in rows.values():
            row.sort(key=lambda box: box.x0)
            gaps.extend(b.x0 - a.x1 for a, b in zip(row, row[1:]))
        if gaps:
            require(np.ptp(gaps) < p["qa"]["panel_size_tolerance"], "panel", "unequal horizontal gaps")
    return {"status": "PASS" if not failures else "FAIL", "failures": failures,
            "fonts": fonts, "glyphs": glyph_evidence, "panel_count": len(boxes),
            "width_mm": float(fig.get_figwidth() * 25.4),
            "limits": ["Mechanism/units/math semantics require source review.",
                       "Legend geometry checks line paths; field/annotation salience also needs visual review."]}


def check_exports(stem, figure):
    stem = Path(stem)
    failures, font_names = [], []
    dimensions = figure.get_size_inches() * 72
    with fitz.open(stem.with_suffix(".pdf")) as doc:
        page = doc[0]
        expected_cjk = set(CJK.findall("".join(t.get_text() for t in figure.findobj(Text) if t.get_visible())))
        actual_cjk = set(CJK.findall(page.get_text()))
        if not expected_cjk <= actual_cjk:
            failures.append("PDF missing CJK text: " + "".join(sorted(expected_cjk - actual_cjk)))
        if len(doc) != 1 or not np.allclose([page.rect.width, page.rect.height], dimensions, atol=0.1):
            failures.append("PDF dimensions")
        for font in page.get_fonts(full=True):
            xref, ext, kind, name = font[:4]
            font_names.append(name)
            if not doc.extract_font(xref)[3]:
                failures.append("Unembedded PDF font: " + name)
            if any(s in name.lower() for s in ("dejavu", "arial", "calibri")):
                failures.append("Unexpected PDF font: " + name)
        pdf_pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pdf_image = Image.frombytes("RGB", [pdf_pix.width, pdf_pix.height], pdf_pix.samples)
    svg = stem.with_suffix(".svg")
    root = ET.parse(svg).getroot()
    ns = {"s": "http://www.w3.org/2000/svg"}
    if root.findall(".//s:text", ns):
        failures.append("SVG has unembedded external text (expected portable glyph outlines)")
    if not root.findall(".//s:path", ns):
        failures.append("SVG lacks vector paths")
    # MuPDF independently opens and rasterizes both vector formats.
    with fitz.open(svg) as svg_doc:
        pix = svg_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        svg_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    metrics = {}
    with Image.open(stem.with_suffix(".png")) as png:
        png.load()
        if min(png.info.get("dpi", (0, 0))) < profile()["export"]["dpi"] - 1:
            failures.append("PNG resolution below 600 dpi")
        for name, candidate in (("pdf", pdf_image), ("svg", svg_image)):
            ref = np.asarray(png.convert("RGB").resize(candidate.size, Image.Resampling.LANCZOS), dtype=float)
            actual = np.asarray(candidate, dtype=float)
            # Differences at antialiased edges are expected between engines.
            error = float(np.mean(np.abs(ref - actual)) / 255)
            metrics[name + "_png_mean_absolute_error"] = error
            if error > 0.08:
                failures.append(name + " visual mismatch exceeds 0.08")
    return {"status": "PASS" if not failures else "FAIL", "failures": failures,
            "pdf_fonts": font_names, "svg_text": "embedded vector glyph outlines, not editable text",
            "cross_renderer_metrics": metrics}
