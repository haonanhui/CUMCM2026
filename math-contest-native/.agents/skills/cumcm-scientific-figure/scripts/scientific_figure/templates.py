"""Seven data-driven templates; synthetic inputs belong only to regression.py."""
from dataclasses import dataclass, field

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from .style import profile, format_axes, series_style


@dataclass
class FigureBundle:
    figure: object
    axes: list
    kind: str
    style: dict = field(default_factory=dict)
    data_lines: list = field(default_factory=list)
    panel_labels: list = field(default_factory=list)
    secondary_axes: list = field(default_factory=list)
    colorbars: list = field(default_factory=list)
    caption: str = ""
    synthetic: bool = False


def layout(kind, shape=(1, 1), sharex=False, sharey=False, height_mm=None):
    if shape not in ((1, 1), (1, 2), (2, 1), (2, 2), (2, 3)):
        raise ValueError("Supported layouts: 1x1, 1x2, 2x1, 2x2, 2x3")
    p = profile()["layout"]
    width = p["single_mm"] if shape[1] == 1 else p["double_mm"]
    height = height_mm or (68 if shape[0] == 1 else 125)
    fig, axes = plt.subplots(*shape, figsize=(width / 25.4, height / 25.4),
                             squeeze=False, sharex=sharex, sharey=sharey, layout="constrained")
    fig.get_layout_engine().set(w_pad=p["w_pad_in"], h_pad=p["h_pad_in"],
                               wspace=p["wspace"], hspace=p["hspace"])
    bundle = FigureBundle(fig, list(axes.flat), kind, style=profile())
    for index, ax in enumerate(bundle.axes):
        format_axes(ax)
        if len(bundle.axes) > 1:
            label = ax.text(p["panel_x"], p["panel_y"], f"({chr(97 + index)})", transform=ax.transAxes,
                            ha="right", va="top", fontsize=profile()["sizes"]["panel"], zorder=20)
            bundle.panel_labels.append(label)
    return bundle


def draw_series(bundle, ax, x, y, label, role="primary", markers=True):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 1 or y.shape != x.shape or len(x) < 2 or not np.isfinite([x, y]).all():
        raise ValueError("Series need equal finite 1D arrays with at least two points")
    if (ax.get_xscale() == "log" and np.any(x <= 0)) or (ax.get_yscale() == "log" and np.any(y <= 0)):
        raise ValueError("Log axes require strictly positive data; do not silently hide observations")
    style = series_style(role)
    if markers:
        style["markevery"] = max(1, len(x) // 10)
    else:
        style["marker"] = "None"
    line, = ax.plot(x, y, label=label, **style)
    line.set_gid("scientific-data")
    bundle.data_lines.append(line)
    return line


def shade(ax, interval):
    if interval is not None:
        ax.axvspan(*interval, color=profile()["bands"]["color"],
                   alpha=profile()["bands"]["alpha"], zorder=-5)


def parametric_curve(x, series, *, xlabel, ylabel, xscale="log", mode=None,
                     annotation=None, reference=None):
    b = layout("parametric_curve")
    ax = b.axes[0]
    format_axes(ax, xscale)
    shade(ax, mode)
    for item in series:
        draw_series(b, ax, x, item["y"], item["label"], item["role"])
    if reference is not None:
        ax.axhline(reference, color=profile()["colors"]["reference"], ls="-.",
                   lw=profile()["stroke"]["helper"])
    if annotation:
        ax.annotate(annotation["text"], annotation["xy"], xytext=annotation["xytext"],
                    fontsize=profile()["sizes"]["annotation"], color="black",
                    arrowprops={"arrowstyle": "->", "color": "black", "lw": profile()["stroke"]["axes"]})
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.legend(loc="best")
    return b


def time_phase_spectrum(t, signals, *, time_label, response_label, velocity_label, frequency_label, psd_label):
    t = np.asarray(t, dtype=float)
    if len(signals) != 2 or t.ndim != 1 or len(t) < 8:
        raise ValueError("2x3 template needs two signals and at least eight time points")
    dt = np.diff(t)
    if not np.all(dt > 0) or not np.allclose(dt, dt[0], rtol=1e-5, atol=0):
        raise ValueError("PSD requires finite, increasing, uniformly sampled time")
    b = layout("time_phase_spectrum", (2, 3))
    for row, signal in enumerate(signals):
        y = np.asarray(signal["y"], dtype=float)
        if y.shape != t.shape or not np.isfinite(y).all():
            raise ValueError("Signal shape must match time; all values must be finite")
        role, label = signal["role"], signal["label"]
        a, phase, spectrum = b.axes[row * 3:row * 3 + 3]
        draw_series(b, a, t, y, label, role, False)
        a.set(xlabel=time_label, ylabel=response_label)
        draw_series(b, phase, y, np.gradient(y, t), label, role, False)
        phase.set(xlabel=response_label, ylabel=velocity_label)
        # One-sided density, rectangular window, mean removed; integral = variance.
        frequencies = np.fft.rfftfreq(len(t), dt[0])
        power = dt[0] / len(t) * np.abs(np.fft.rfft(y - y.mean())) ** 2
        power[1:-1 if len(t) % 2 == 0 else None] *= 2
        draw_series(b, spectrum, frequencies, power, label, role, False)
        spectrum.set(xlabel=frequency_label, ylabel=psd_label)
        spectrum.set_xlim(0, frequencies[-1])
    return b


def flow_field(x, y, snapshots, *, xlabel, ylabel, colorbar_label):
    x, y = np.asarray(x), np.asarray(y)
    if len(snapshots) != 4:
        raise ValueError("Flow layout requires four snapshots")
    fields = [np.asarray(s["field"]) for s in snapshots]
    if any(f.shape != (len(y), len(x)) or not np.isfinite(f).all() for f in fields):
        raise ValueError("Fields must be finite (len(y), len(x)) arrays")
    limit = max(float(np.max(np.abs(f))) for f in fields)
    if limit <= 0:
        raise ValueError("Signed flow fields need nonzero range")
    b = layout("flow_field", (2, 2), sharex=True, sharey=True, height_mm=122)
    for ax, snapshot, values in zip(b.axes, snapshots, fields):
        im = ax.pcolormesh(x, y, values, cmap=profile()["field"]["cmap"],
                           vmin=-limit, vmax=limit, shading="auto", rasterized=True)
        ax.streamplot(x, y, snapshot["u"], snapshot["v"], density=0.6,
                      color=profile()["colors"]["reference"], linewidth=profile()["stroke"]["stream"],
                      arrowsize=0.55)
        ax.contour(x, y, values, levels=[-limit/2, limit/2], colors="black",
                   linestyles=["--", "-"], linewidths=profile()["stroke"]["stream"])
        ax.set(xlabel=xlabel, ylabel=ylabel)
        ax.label_outer()
    bar = b.figure.colorbar(im, ax=b.axes, orientation="horizontal", shrink=0.65,
                           fraction=0.065, pad=0.06, aspect=35)
    bar.set_label(colorbar_label)
    b.colorbars.append(bar)
    b.caption = "；".join(f"({chr(97+i)}) {s['label']}" for i, s in enumerate(snapshots))
    return b


def regime_map(categories, theory_x, theory_y, *, xlabel, ylabel, band=(0.8, 1.2)):
    b = layout("regime_map")
    ax = b.axes[0]
    format_axes(ax, "log", "log")
    theory_x, theory_y = np.asarray(theory_x), np.asarray(theory_y)
    ax.fill_between(theory_x, theory_y * band[0], theory_y * band[1],
                    color=profile()["bands"]["color"], alpha=profile()["bands"]["alpha"], zorder=-5)
    ax.plot(theory_x, theory_y, color=profile()["colors"]["reference"], ls="-.",
            lw=profile()["stroke"]["helper"])
    for item in categories:
        line = draw_series(b, ax, item["x"], item["y"], item["label"], item["role"])
        line.set_linestyle("None")
        line.set_markevery(1)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.legend(loc="best")
    return b


def convergence_validation(x, coarse, baseline, refined, reference, *, xlabel, ylabel, labels):
    b = layout("convergence_validation")
    ax = b.axes[0]
    for key, values in (("coarse", coarse), ("baseline", baseline), ("refined", refined)):
        draw_series(b, ax, x, values, labels[key], profile()["validation_roles"][key])
    ax.plot(x, reference, color="black", ls="-.", lw=profile()["stroke"]["helper"], label=labels["reference"])
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.legend(loc="best")
    return b


def dual_axis_frequency(x, frequency, ratio, *, xlabel, frequency_label, ratio_label, lock_in=None):
    b = layout("dual_axis_frequency")
    ax = b.axes[0]
    right = ax.twinx()
    format_axes(right)
    right.tick_params(axis="y", which="both", left=False, right=True)
    ax.tick_params(axis="y", which="both", right=False)
    b.secondary_axes.append(right)
    shade(ax, lock_in)
    first = draw_series(b, ax, x, frequency, frequency_label, "primary")
    second = draw_series(b, right, x, ratio, ratio_label, "secondary")
    ax.set(xlabel=xlabel, ylabel=frequency_label)
    right.set_ylabel(ratio_label, color="black")
    ax.legend(handles=[first, second], loc="best")
    return b


def schematic(*, length=4.0, height=2.0, obstacle=(1.0, 1.0, 0.25), labels):
    """Physical domain with a locally refined mesh and dimension arrows (not draw.io)."""
    if length <= 0 or height <= 0 or obstacle[2] <= 0:
        raise ValueError("Physical dimensions must be positive")
    b = layout("schematic")
    ax = b.axes[0]
    cx, cy, radius = obstacle
    if not (radius < cx < length - radius and radius < cy < height - radius):
        raise ValueError("Obstacle must fit inside domain")
    for xpos in np.unique(np.r_[np.linspace(0, length, 13), np.linspace(cx - 2 * radius, cx + 2 * radius, 13)]):
        ax.plot([xpos] * 2, [0, height], color="#CCCCCC", lw=profile()["stroke"]["mesh"])
    for ypos in np.linspace(0, height, 13):
        ax.plot([0, length], [ypos] * 2, color="#CCCCCC", lw=profile()["stroke"]["mesh"])
    ax.add_patch(Rectangle((0, 0), length, height, fill=False, ec="black", lw=profile()["stroke"]["axes"]))
    ax.add_patch(plt.Circle((cx, cy), radius, fc="white", ec="black", lw=profile()["stroke"]["helper"], zorder=4))
    ax.text(0.1, height * 0.7 + 0.12, labels["inlet"], va="bottom",
            fontsize=profile()["sizes"]["annotation"])
    ax.annotate("", (0.75, height * 0.7), xytext=(0.1, height * 0.7),
                arrowprops={"arrowstyle": "->", "lw": profile()["stroke"]["axes"]})
    ax.annotate("", (0, -0.25), (length, -0.25),
                arrowprops={"arrowstyle": "<->", "lw": profile()["stroke"]["axes"]})
    ax.text(length / 2, -0.32, labels["length"], ha="center", va="top")
    ax.set(xlim=(-0.2, length + 0.2), ylim=(-0.6, height + 0.2), xlabel=labels["x"], ylabel=labels["y"])
    ax.set_aspect("equal")
    return b
