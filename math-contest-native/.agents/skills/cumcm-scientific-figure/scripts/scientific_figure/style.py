"""Central style and explicit serif font resolution."""
import json
import copy
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.ticker import AutoMinorLocator, LogLocator, LogFormatterMathtext, ScalarFormatter

PROFILE = json.loads((Path(__file__).resolve().parents[2] / "references/profile.json").read_text(encoding="utf-8"))
_CURRENT = ContextVar("scientific_figure_profile", default=None)


def profile():
    current = _CURRENT.get()
    if current is None:
        raise RuntimeError("Create and inspect figures inside style_context()")
    return current


def resolve_fonts():
    """Never silently substitute the scientific Latin face with CJK or sans."""
    latin = profile()["fonts"]["latin"]
    latin_path = font_manager.findfont(latin, fallback_to_default=False)
    for cjk in profile()["fonts"]["cjk"]:
        try:
            cjk_path = font_manager.findfont(cjk, fallback_to_default=False)
            return {"latin": latin, "latin_path": latin_path, "cjk": cjk, "cjk_path": cjk_path}
        except ValueError:
            continue
    raise RuntimeError("Missing CJK serif: install SimSun, Source Han Serif SC or Noto Serif CJK SC; fonts are not bundled.")


@contextmanager
def style_context(profile_id="native_zh_12pt_v1", *, math_fontset=None):
    p = copy.deepcopy(PROFILE)
    if isinstance(profile_id, dict):
        p = copy.deepcopy(profile_id)
    elif profile_id == "native_zh_12pt_v1":
        p["id"] = profile_id
        p["sizes"] = {key: p["native_override"]["font_pt"] for key in p["sizes"]}
        p["qa"]["min_font_pt"] = p["native_override"]["font_pt"]
    elif profile_id != PROFILE["id"]:
        raise ValueError("Unknown figure profile: " + str(profile_id))
    if math_fontset:
        if math_fontset not in ("stix", "cm"):
            raise ValueError("Supported math fontsets: stix, cm; verify against the actual paper PDF")
        p["fonts"]["math"] = math_fontset
    token = _CURRENT.set(p)
    try:
        fonts = resolve_fonts()
        with mpl.rc_context({
        "font.family": [fonts["latin"], fonts["cjk"]],
        "font.size": p["sizes"]["tick"], "mathtext.fontset": p["fonts"]["math"],
        "mathtext.default": "it", "mathtext.fallback": "stix", "text.usetex": False,
        "mathtext.rm": fonts["latin"], "mathtext.bf": fonts["latin"] + ":bold",
        "mathtext.it": "STIXGeneral:italic" if p["fonts"]["math"] == "stix" else "cmmi10",
        "mathtext.bfit": "STIXGeneral:italic:bold", "mathtext.sf": fonts["latin"],
        "mathtext.tt": fonts["latin"], "mathtext.cal": "STIXNonUnicode:italic",
        "axes.linewidth": p["stroke"]["axes"], "axes.labelsize": p["sizes"]["label"],
        "axes.grid": False, "axes.facecolor": "white", "figure.facecolor": "white",
        "axes.edgecolor": "black", "axes.labelcolor": "black",
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
        "xtick.minor.visible": True, "ytick.minor.visible": True,
        "xtick.major.width": p["stroke"]["axes"], "ytick.major.width": p["stroke"]["axes"],
        "xtick.minor.width": p["stroke"]["axes"], "ytick.minor.width": p["stroke"]["axes"],
        "xtick.labelsize": p["sizes"]["tick"], "ytick.labelsize": p["sizes"]["tick"],
        "legend.frameon": False, "legend.fontsize": p["sizes"]["legend"],
        "legend.handlelength": 2.3, "legend.labelspacing": 0.25,
        "lines.linewidth": p["stroke"]["data"], "lines.markersize": p["stroke"]["marker_size"],
        "lines.markeredgewidth": p["stroke"]["marker_edge"],
        "pdf.fonttype": p["export"]["pdf_fonttype"], "ps.fonttype": 42,
        "svg.fonttype": p["export"]["svg_fonttype"], "savefig.dpi": p["export"]["dpi"],
        }):
            yield fonts
    finally:
        _CURRENT.reset(token)


def format_axes(ax, xscale="linear", yscale="linear"):
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    for axis, scale in ((ax.xaxis, xscale), (ax.yaxis, yscale)):
        if scale == "log":
            axis.set_major_locator(LogLocator(base=10))
            axis.set_major_formatter(LogFormatterMathtext())
            axis.set_minor_locator(LogLocator(base=10, subs=range(2, 10)))
        else:
            axis.set_minor_locator(AutoMinorLocator(2))
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_powerlimits((-3, 4))
            axis.set_major_formatter(formatter)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    for spine in ax.spines.values():
        spine.set_visible(True)


def series_style(role):
    line, marker, fill = profile()["series"][role]
    return {"color": profile()["colors"][role], "linestyle": line, "marker": marker,
            "fillstyle": fill, "linewidth": profile()["stroke"]["data"],
            "markersize": profile()["stroke"]["marker_size"],
            "markeredgewidth": profile()["stroke"]["marker_edge"]}
