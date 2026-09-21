"""Reproducible synthetic A-F suite; never presented as physical observations."""
import argparse
import hashlib
import json
import html
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt

from scientific_figure import (style_context, parametric_curve, time_phase_spectrum,
                               flow_field, regime_map, convergence_validation,
                               dual_axis_frequency, schematic, export_bundle)
from scientific_figure.style import profile


def examples():
    x = np.geomspace(0.1, 100, 80)
    a = parametric_curve(x, [
        {"y": 0.2 + 0.5 / (1 + (np.log10(x) - 0.6)**2), "label": r"第一响应 $A_1$", "role": "primary"},
        {"y": 0.1 + 0.25 / (1 + (np.log10(x) - 0.9)**2), "label": r"第二响应 $A_2$", "role": "secondary"}],
        xlabel=r"弯曲刚度 $\gamma$", ylabel=r"平均倾角 $\bar{\theta}$ (°)", mode=(1.5, 8), reference=0.15,
        annotation={"text": r"模态 II", "xy": (4, 0.7), "xytext": (15, 0.78)})
    a.axes[0].set_ylim(0, 1.15)
    a.axes[0].legend(loc="upper left")
    yield "A", a, "合成参数响应。(空心圆、实心方块)分别表示两条响应；浅蓝区表示示例模态区间，点划线为参考值。无物理结论。"

    t = np.linspace(0, 12, 601, endpoint=False)
    b = time_phase_spectrum(t, [
        {"y": np.sin(2*np.pi*t), "role": "primary", "label": "第一响应"},
        {"y": 0.65*np.sin(2*np.pi*1.5*t + 0.2), "role": "secondary", "label": "第二响应"}],
        time_label=r"时间 $t/T$", response_label=r"位移 $y/D$", velocity_label=r"速度 $\dot{y}T/D$",
        frequency_label=r"频率 $fT$", psd_label=r"谱密度 $S_y/T$")
    for ax in (b.axes[2], b.axes[5]):
        ax.set_xlim(0, 5)  # Explicit fixture view, not a generic PSD truncation.
    yield "B", b, "合成振动的时历、相图及单边 PSD。第一行(a–c)为红实线，第二行(d–f)为蓝虚线。去均值、矩形窗；均匀采样。"

    xx, yy = np.linspace(0, 6, 100), np.linspace(-1.5, 1.5, 50)
    X, Y = np.meshgrid(xx, yy)
    snapshots = []
    for i in range(4):
        phase = i*np.pi/2
        values = np.sin(2*X-phase)*np.exp(-Y**2*2)
        snapshots.append({"field": values, "u": np.ones_like(X), "v": 0.3*np.cos(X-phase)*np.exp(-Y**2),
                          "label": r"时刻 $t/T=" + str(i/4) + "$"})
    c = flow_field(xx, yy, snapshots, xlabel=r"位置 $x/D$", ylabel=r"位置 $y/D$",
                   colorbar_label=r"涡量 $\omega D/U$")
    yield "C", c, "合成有符号场及流线快照，共用对称色标。(a–d)分别对应无量纲时刻t/T=0、0.25、0.5、0.75。黑实线/虚线分别标记正/负半极值等值线，辅助灰度辨识；细灰线为独立构造的示例速度场流线。并非数值求解结果。"

    rx = np.geomspace(1, 100, 9)
    d = regime_map([
        {"x": rx, "y": 0.5*rx**0.6, "label": "模态 I", "role": "primary"},
        {"x": rx, "y": 2*rx**0.6, "label": "模态 II", "role": "secondary"}],
        rx, rx**0.6, xlabel=r"雷诺数 $Re$", ylabel=r"约化速度 $U_r$")
    d.axes[0].set_ylim(0.2, 150)
    d.axes[0].legend(loc="upper left")
    yield "D", d, "合成参数空间的离散类别：空心圆与实心方块表示两个模态；灰色点划线为示例理论关系，浅色带为其±20%区间。"

    cx = np.linspace(0, 1, 60)
    exact = np.sin(np.pi*cx)
    e = convergence_validation(cx, exact + 0.15*cx, exact + 0.05*cx, exact + 0.01*cx, exact,
        xlabel=r"位置 $x/L$", ylabel=r"响应 $y/D$",
        labels={"coarse": "粗网格", "baseline": "基准网格", "refined": "细网格", "reference": r"解析解 $\sin(\pi x/L)$"})
    e.axes[0].set_ylim(-0.05, 1.65)
    e.axes[0].legend(loc="upper left", ncol=1 if profile()["id"] == "native_zh_12pt_v1" else 2)
    if profile()["id"] == "native_zh_12pt_v1":
        e.axes[0].set_ylim(-0.05, 2.7)
    yield "E", e, "合成网格验证示例。蓝虚线方块、灰点线菱形和红实线空心圆分别表示粗、基准和细网格；黑点划线为解析函数。误差为人为注入，不证明任何求解器收敛。"

    fx = np.linspace(2, 12, 70)
    f = dual_axis_frequency(fx, 0.8 + 0.15*np.tanh(fx-6), 0.95 + 0.08*np.sin(fx),
                           xlabel=r"约化速度 $U_r$", frequency_label=r"频率 $f/f_n$",
                           ratio_label=r"幅值比 $A_2/A_1$", lock_in=(5, 8))
    f.axes[0].set_ylim(0.55, 1.35)
    f.secondary_axes[0].set_ylim(0.7, 1.3)
    f.axes[0].legend(handles=f.data_lines, loc="upper left")
    yield "F", f, "合成双轴响应。左轴红实线空心圆为频率比，右轴蓝虚线实心方块为幅值比；浅蓝带为示例锁定区。两轴均为黑色。"


def run(out, profile_id="jfs_zh_reference_v1"):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    reports = {}
    source = Path(__file__)
    provenance = {"input": "deterministic synthetic functions in regression.py", "seed": None,
                  "generator_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                  "numpy": np.__version__, "matplotlib": matplotlib.__version__}
    skill = source.resolve().parents[1]
    sources = {p.relative_to(skill).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in skill.rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".md", ".txt")}
    (out / "source-manifest.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    with style_context(profile_id):
        for name, bundle, caption in examples():
            bundle.synthetic, bundle.caption = True, caption
            reports[name] = export_bundle(bundle, out, name, provenance=provenance)
            print(name, reports[name]["status"], flush=True)
            plt.close(bundle.figure)
        s = schematic(labels={"inlet": r"来流 $U$", "length": r"长度 $L$", "x": r"位置 $x/D$", "y": r"位置 $y/D$"})
        s.synthetic, s.caption = True, "合成计算域与局部网格加密示意；尺寸为示例。"
        reports["schematic"] = export_bundle(s, out, "schematic", provenance=provenance)
        plt.close(s.figure)
    summary = {"status": "PASS" if all(r["status"] == "PASS" for r in reports.values()) else "FAIL",
               "synthetic": True, "figures": {k: v["status"] for k,v in reports.items()},
               "human_review": "pending"}
    (out / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    sections = []
    for name, report in reports.items():
        width = report["artist"]["width_mm"]
        caption = (out / (name + ".caption.txt")).read_text(encoding="utf-8")
        sections.append(f'<section><h2>{name} — {report["status"]}</h2>'
                        f'<img style="width:{width}mm" src="{name}.svg" alt="{name}">'
                        f'<p>{html.escape(caption)}</p><p>'
                        + ' · '.join(f'<a href="{name}.{ext}">{ext}</a>' for ext in ("pdf", "svg", "png", "gray.png", "qa.json"))
                        + '</p></section>')
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>科研图合成回归</title>'
        '<style>body{font-family:serif;margin:24px}section{break-inside:avoid;margin-bottom:32px}'
        'img{height:auto}p{max-width:180mm}</style><h1>科研图合成回归 — '
        + html.escape(profile_id) + '</h1><p>图按声明的毫米宽度显示；所有数据为合成样例。</p>'
        + ''.join(sections), encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="New evidence directory; existing directories are rejected")
    parser.add_argument("--profile", default="jfs_zh_reference_v1", choices=["jfs_zh_reference_v1", "native_zh_12pt_v1"])
    args = parser.parse_args()
    raise SystemExit(0 if run(args.out, args.profile)["status"] == "PASS" else 1)
