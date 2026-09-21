"""Behavioral regressions including deliberate invalid styles and mixed glyph loss."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.mathtext import MathTextParser

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from scientific_figure import style_context, parametric_curve, export_bundle, time_phase_spectrum
from scientific_figure.style import profile, resolve_fonts
from scientific_figure.templates import layout
from scientific_figure.qa import check_figure, check_exports
from scientific_figure.typography import prepare_text


def curve():
    return parametric_curve([1, 2, 3], [
        {"y": [0.1, 0.2, 0.1], "label": r"响应 $A_1$", "role": "primary"}],
        xlabel=r"雷诺数 $Re$", ylabel=r"均值 $\bar{\theta}$ (°)", xscale="linear")


class FiguresTest(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_context_restores_rc_and_nested_profile(self):
        old = matplotlib.rcParams["font.family"][:]
        with style_context():
            self.assertEqual(profile()["sizes"]["tick"], 12)
            with style_context("jfs_zh_reference_v1"):
                self.assertEqual(profile()["sizes"]["tick"], 8.5)
            self.assertEqual(profile()["sizes"]["tick"], 12)
        self.assertEqual(matplotlib.rcParams["font.family"], old)
        with self.assertRaises(RuntimeError):
            profile()

    def test_missing_font_fails_without_sans_substitute(self):
        with patch("scientific_figure.style.font_manager.findfont", side_effect=ValueError("font absent")):
            with self.assertRaises(ValueError):
                with style_context():
                    pass

    def test_cjk_serif_fallback(self):
        from matplotlib.font_manager import findfont
        def select(font, **kwargs):
            if font == "SimSun":
                raise ValueError("absent")
            if font == "Source Han Serif SC":
                return "declared-serif-test-path"
            return findfont(font, **kwargs)
        with patch("scientific_figure.style.font_manager.findfont", side_effect=select):
            with style_context() as fonts:
                self.assertEqual(fonts["cjk"], "Source Han Serif SC")

    def test_real_mixed_math_glyphs_not_dummy(self):
        with style_context("jfs_zh_reference_v1"):
            b = curve()
            prepare_text(b.figure)
            text = b.axes[0].yaxis.label
            parsed = MathTextParser("path").parse(text.get_text(), prop=text.get_fontproperties())
            glyphs = [(chr(code), face.family_name, face.style_name) for face, size, code, x, y in parsed.glyphs]
            self.assertIn(("均", "SimSun", "Regular"), glyphs)
            self.assertTrue(any(char == "θ" and "STIX" in face and "Italic" in style for char, face, style in glyphs))
            self.assertTrue(any(char == "°" and face == "Times New Roman" for char, face, style in glyphs))
            before = text.get_text()
            prepare_text(b.figure)
            self.assertEqual(text.get_text(), before)

    def test_qa_rejects_font_grid_stroke_and_hidden_spine(self):
        with style_context("jfs_zh_reference_v1"):
            b = curve()
            b.data_lines[0].set_linewidth(5)
            b.axes[0].grid(True)
            b.axes[0].spines["top"].set_visible(False)
            b.axes[0].set_title("BAD", fontfamily="Arial")
            categories = {f["category"] for f in check_figure(b)["failures"]}
            self.assertTrue({"stroke", "axes", "font"} <= categories)

    def test_qa_rejects_duplicate_grayscale_encoding(self):
        with style_context():
            b = parametric_curve([1,2,3], [
                {"y": [1,2,1], "label": "a", "role": "primary"},
                {"y": [2,3,2], "label": "b", "role": "primary"}], xlabel="x", ylabel="y")
            self.assertIn("grayscale", {f["category"] for f in check_figure(b)["failures"]})

    def test_qa_rejects_clipping_and_scientific_literal(self):
        with style_context():
            b = curve()
            b.figure.text(1.1, 0.5, "1e-3")
            categories = {f["category"] for f in check_figure(b)["failures"]}
            self.assertTrue({"clipping", "math"} <= categories)

    def test_qa_rejects_legend_over_curve(self):
        with style_context():
            b = curve()
            b.axes[0].set_ylim(0, 0.4)
            b.axes[0].legend(loc="center")
            self.assertIn("legend", {f["category"] for f in check_figure(b)["failures"]})

    def test_layouts_and_corrupt_panel(self):
        with style_context("jfs_zh_reference_v1"):
            for shape in ((1,2), (2,1), (2,2), (2,3)):
                b = layout("test", shape)
                self.assertEqual(check_figure(b)["status"], "PASS")
            b.panel_labels[1].set_text("(z)")
            self.assertIn("panel", {f["category"] for f in check_figure(b)["failures"]})

    def test_invalid_series_rejected(self):
        with style_context():
            with self.assertRaises(ValueError):
                parametric_curve([1,2], [{"y": [1,float('nan')], "label":"bad", "role":"primary"}], xlabel="x", ylabel="y")

    def test_psd_parseval_odd_even_and_reject_irregular_time(self):
        with style_context("jfs_zh_reference_v1"):
            for count in (100, 101):
                t = np.arange(count) * 0.02
                y = np.sin(2*np.pi*2*t)
                kwargs = dict(time_label="t", response_label="y", velocity_label="v", frequency_label="f", psd_label="PSD")
                signals = [{"y": y, "role": "primary", "label": "a"}]*2
                b = time_phase_spectrum(t, signals, **kwargs)
                line = b.data_lines[2]
                f, power = line.get_data()
                self.assertAlmostEqual(float(sum(power)*(f[1]-f[0])), float(np.var(y)), places=12)
                t[3] += 0.001
                with self.assertRaises(ValueError):
                    time_phase_spectrum(t, signals, **kwargs)

    def test_export_after_context_and_reject_overwrite(self):
        with style_context("jfs_zh_reference_v1"):
            b = curve()
        with tempfile.TemporaryDirectory(prefix="figure-export-") as tmp:
            report = export_bundle(b, tmp, "sample", provenance={"test": True})
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(report["profile"], "jfs_zh_reference_v1")
            with self.assertRaises(FileExistsError):
                export_bundle(b, tmp, "sample", provenance={})

    def test_missing_glyph_is_not_pass(self):
        with style_context("jfs_zh_reference_v1"):
            b = curve()
            b.axes[0].set_xlabel("\U0010ffff")
            self.assertIn("font", {f["category"] for f in check_figure(b)["failures"]})

    def test_native_minimum_size_fails_if_shrunk(self):
        with style_context():
            b = curve()
            b.axes[0].xaxis.label.set_fontsize(8)
            self.assertIn("final-size", {f["category"] for f in check_figure(b)["failures"]})

    def test_log_axis_rejects_nonpositive_observations(self):
        with style_context():
            with self.assertRaises(ValueError):
                parametric_curve([-1, 2], [{"y": [1,2], "label": "x", "role": "primary"}], xlabel="x", ylabel="y")

    def test_panel_labels_left_of_y_axis_not_above_frame(self):
        from scientific_figure.templates import draw_series
        with style_context("jfs_zh_reference_v1"):
            b = layout("test", (1,2))
            ax = b.axes[0]
            draw_series(b, ax, [0, 1], [0.95, 0.95], "line")
            ax.set(xlim=(0,1), ylim=(0,1))
            self.assertEqual(b.panel_labels[0].get_position(), (-0.18, 1))
            self.assertEqual(b.panel_labels[0].get_va(), "top")
            self.assertEqual(b.panel_labels[0].get_ha(), "right")
            b.panel_labels[0].set_position((0.025, 0.975))
            self.assertIn("panel", {f["category"] for f in check_figure(b)["failures"]})

    def test_low_resolution_export_is_rejected(self):
        from PIL import Image
        with style_context("jfs_zh_reference_v1"):
            b = curve()
            with tempfile.TemporaryDirectory(prefix="figure-dpi-") as tmp:
                export_bundle(b, tmp, "sample", provenance={"test": True})
                png = Path(tmp) / "sample.png"
                with Image.open(png) as source:
                    image = source.copy()
                image.save(png, dpi=(72,72))
                self.assertEqual(check_exports(Path(tmp)/"sample", b.figure)["status"], "FAIL")

    def test_external_right_explanation_is_rejected(self):
        with style_context("jfs_zh_reference_v1"):
            b = layout("test", (2,2))
            b.axes[0].text(1, 1.045, "time = 1", transform=b.axes[0].transAxes, ha="right")
            self.assertTrue(any("external explanatory" in f["detail"] for f in check_figure(b)["failures"]))


if __name__ == "__main__":
    unittest.main()
