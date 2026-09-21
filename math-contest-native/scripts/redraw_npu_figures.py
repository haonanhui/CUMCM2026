"""Redraw the five revision-three figures without rerunning or changing analysis.

Usage: .venv/Scripts/python.exe -B scripts/redraw_npu_figures.py --out figures/npu2025-fonts-001
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.agents/skills/cumcm-scientific-figure/scripts'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.transforms import Bbox
from scientific_figure import style_context, export_bundle
from scientific_figure.style import profile, series_style
from scientific_figure.templates import layout, draw_series


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs = {}
    plotted = {}
    results = {}

    def read(relative):
        path = ROOT / relative
        inputs[relative] = sha(path)
        return json.loads(path.read_text(encoding='utf-8'))

    def make(name, rows=2, height=135):
        b = layout(name, (rows, 1), height_mm=height)
        b.figure.set_size_inches(165 / 25.4, height / 25.4)
        b.figure.set_layout_engine(None)
        b.figure.subplots_adjust(left=.235, right=.975, bottom=.13,
                                 top=.965, hspace=.48)
        for ax in b.axes:
            for axis in (ax.xaxis, ax.yaxis):
                # Explicit integer ticks avoid implicit scale factors above the frame.
                fmt = ScalarFormatter(useMathText=False)
                fmt.set_scientific(False)
                fmt.set_useOffset(False)
                axis.set_major_formatter(fmt)
        return b

    def save(b, explanation):
        b.caption = explanation
        # Balance the plotting body plus axis text, not the PDF canvas or the
        # isolated panel letters: those letters must not pull the chart right.
        for label in b.panel_labels:
            label.set_in_layout(False)
        b.figure.canvas.draw()
        renderer = b.figure.canvas.get_renderer()
        bounds = Bbox.union([ax.get_tightbbox(renderer) for ax in b.axes])
        dx = (b.figure.bbox.width / 2 - (bounds.x0 + bounds.x1) / 2) / b.figure.bbox.width
        for ax in b.axes:
            pos = ax.get_position()
            ax.set_position([pos.x0 + dx, pos.y0, pos.width, pos.height])
        b.figure.canvas.draw()
        renderer = b.figure.canvas.get_renderer()
        centered = Bbox.union([ax.get_tightbbox(renderer) for ax in b.axes])
        center_error_mm = ((centered.x0 + centered.x1 - b.figure.bbox.width) / 2
                           / b.figure.dpi * 25.4)
        if abs(center_error_mm) > .1:
            raise RuntimeError('Visible plotting body is not horizontally centered')
        geometry = {'method': 'axes_and_axis_text_union_excluding_panel_letters',
                    'horizontal_shift_mm': dx * 165,
                    'center_error_mm': center_error_mm,
                    'left_margin_mm': centered.x0 / b.figure.dpi * 25.4,
                    'right_margin_mm': (b.figure.bbox.width-centered.x1) / b.figure.dpi * 25.4}
        for ax in b.axes:
            if ax.get_legend():
                box = ax.get_legend().get_window_extent(renderer)
                for label in ax.texts:
                    if label not in b.panel_labels and box.overlaps(label.get_window_extent(renderer)):
                        print('Legend collision:', b.kind, label.get_text(),
                              list(box.bounds), list(label.get_window_extent(renderer).bounds))
        report = export_bundle(b, out, b.kind, provenance={
            'inputs_sha256': dict(inputs), 'source_script': 'scripts/redraw_npu_figures.py',
            'source_sha256': sha(Path(__file__)), 'original_scripts': {
                p: sha(ROOT / p) for p in ('scripts/figures_npu_revision2.py',
                                           'scripts/figures_npu_revision3.py')},
            'processing': 'Same recorded arrays, windows, units and reduction formula as original scripts.',
            'paper_width_mm': 165, 'embedding_scale': 1.0, 'visual_centering': geometry})
        results[b.kind] = {'status': report['status'], 'failures': report['artist']['failures'],
                           'export_failures': report['export']['failures']}
        plt.close(b.figure)

    r3 = 'results/runs/npu-paper-r3-analysis-001/'
    r2 = 'results/runs/npu-paper-r2-analysis-001/'
    with style_context(math_fontset='cm'):
        b = make('conv_trajectory', height=140)
        plotted[b.kind] = {}
        for key, label, role in [('id', '编号基准', 'reference'),
                                  ('selected', '选定深度优先', 'primary'),
                                  ('memory', '局部缓存贪心', 'secondary')]:
            d = read(r3 + f'conv_{key}_trajectory.json')
            points = np.asarray(d['points'])
            draw_series(b, b.axes[0], points[:, 0], points[:, 1], label, role, False)
            plotted[b.kind][key] = {'points': d['points']}
            if key != 'memory':
                points = np.asarray([p for p in d['points'] if 2180 <= p[0] <= 2350])
                line = draw_series(b, b.axes[1], points[:, 0], points[:, 1], label, role, False)
                line.set_drawstyle('steps-post')
                b.axes[1].plot(d['position'], d['peak'], linestyle='none',
                               **{k: v for k, v in series_style(role).items() if k != 'linestyle'})
                plotted[b.kind][key].update(window=points.tolist(), peak=d['peak'], position=d['position'])
        for ax in b.axes:
            ax.set(xlabel='已处理节点位置', ylabel='驻留量（容量单位）')
        b.axes[0].set_ylim(0, b.axes[0].get_ylim()[1] * 1.55)
        b.axes[0].legend(loc='upper right', ncol=1)
        b.axes[1].set_xlim(2180, 2350)
        save(b, '（a）卷积小图完整序列的驻留轨迹；（b）节点位置 2180–2350 的局部阶梯轨迹。灰色点线为编号基准，红色实线为选定深度优先，蓝色虚线为局部缓存贪心；局部图中的菱形和圆形分别标出前两种方案的峰值。纵轴均使用题面容量单位。')

        b = make('attention_occupancy', height=130)
        d = read(r3 + 'attention_p2_occupancy.json')
        plotted[b.kind] = {'trace': d['trace'], 'capacities': [4096, 1024]}
        for ax, index, capacity in zip(b.axes, (1, 2), (4096, 1024)):
            line = draw_series(b, ax, [v[0] for v in d['trace']],
                               [v[index] for v in d['trace']], '物理驻留', 'primary', False)
            line.set_drawstyle('steps-post')
            ax.axhline(capacity, color=profile()['colors']['reference'], ls=':',
                       linewidth=profile()['stroke']['helper'])
            ax.set(xlabel='扩展调度序列位置', ylabel='驻留量（容量单位）', ylim=(0, capacity * 1.13))
        save(b, '注意力小图问题二方案的物理驻留过程。（a）一级缓存，容量为 4096；（b）统一缓存，容量为 1024。红色阶梯线为驻留量，灰色水平点线为物理容量；横轴为同一扩展调度序列的位置，纵轴使用题面容量单位。')

        b = make('stage_gain', rows=1, height=90)
        b.figure.subplots_adjust(left=.19, bottom=.24, top=.965)
        ax = b.axes[0]
        rows = read('results/runs/npu2025-a-005/summary.json')
        analysis = read(r2 + 'analysis.json')['rows']
        plotted[b.kind] = {}
        for offset, key, label, role in [(-.1, 'initial_time_best', '扩展候选后', 'secondary'),
                                          (.1, 'final', '固定驻留图重排后', 'primary')]:
            values = [100*(1-(a[key]['cycles'] if key != 'final' else r['problem3']['cycles'])/
                          r['problem2']['cycles']) for r, a in zip(rows, analysis)]
            line = draw_series(b, ax, np.arange(6)+offset, values, label, role)
            line.set_linestyle('None')
            line.set_markevery(1)
            plotted[b.kind][key] = values
            if key == 'final':
                for i, value in enumerate(values):
                    ax.annotate(f'{value:.2f}', (i+offset, value), xytext=(0, 7),
                                textcoords='offset points', ha='center')
        ax.set_xticks(np.arange(6), ['卷积\n小图', '卷积\n大图', '注意力\n小图', '注意力\n大图', '矩阵乘\n小图', '矩阵乘\n大图'])
        ax.set(ylabel='相对问题二的时间降幅（%）', ylim=(-2, 49), xlim=(-.5, 5.5))
        ax.legend(loc='upper left')
        save(b, '六个计算图在共同搬运预算约束下的完成时间改善。蓝色实心方块为扩展候选后的结果，红色空心圆为最终固定驻留图重排后的结果；圆形上方数字为后者降幅。降幅均按 100×（1−当前完成时间／问题二完成时间）计算，单位为百分比。')

        names = {'MTE2': '输入搬运', 'MTE1': '级间搬运', 'CUBE': '矩阵计算',
                 'VECTOR': '向量计算', 'MTE3': '输出搬运', 'FIXP': '结果搬运'}
        for name, local in [('attention_compare', False), ('attention_window', True)]:
            b = make(name, height=135)
            plotted[name] = {}
            for ax, stage in zip(b.axes, (2, 3)):
                data = read((r3 + f'attention_p{stage}_detail.json') if local else
                            (r2 + f'attention_p{stage}_timeline.json'))
                if not local:
                    data = [dict(id=v[0], pipe=v[1], start=v[2], end=v[3], op=v[4]) for v in data]
                present = [p for p in names if any(v['pipe'] == p for v in data)]
                plotted[name][str(stage)] = {}
                for i, pipe in enumerate(present):
                    for spill, role in [(False, 'reference'), (True, 'primary')]:
                        scale = 1 if local else 1000
                        intervals = [(v['start']/scale, (v['end']-v['start'])/scale) for v in data
                                     if v['pipe'] == pipe and v['end'] > v['start']
                                     and v['op'].startswith('SPILL') == spill
                                     and (not local or (v['end'] > 8500 and v['start'] < 11500))]
                        plotted[name][str(stage)][pipe + ('_spill' if spill else '_original')] = intervals
                        ax.broken_barh(intervals, (i-.28, .56),
                                       facecolors=profile()['colors'][role],
                                       edgecolors='white', linewidth=.35 if local else 0,
                                       hatch='///' if spill else None)
                    if local:
                        for v in data:
                            if v['id'] in (136, 172, 173) and v['pipe'] == pipe:
                                ax.text(max(8500, v['start']), i+.31, str(v['id']), ha='left')
                ax.set_yticks(range(len(present)), [names[p] for p in present])
                ax.set_ylim(-.65, len(present)+2.2)
                ax.set_xlim((8500, 11500) if local else (0, 49))
                ax.xaxis.set_major_locator(MultipleLocator(1000 if local else 10))
                ax.set_xlabel('执行时间（周期）' if local else '执行时间（千周期）')
                if stage == 2:
                    ax.legend(handles=[Patch(facecolor=profile()['colors']['reference'], label='原始操作'),
                                   Patch(facecolor=profile()['colors']['primary'], hatch='///',
                                         edgecolor='white', label='换入换出')],
                          loc='upper right', ncol=2, handlelength=1.3, columnspacing=.8)
            save(b, ('注意力小图的局部流水，窗口为 8500–11500 周期。' if local else
                     '注意力小图的完整流水，两个分面使用相同的 0–49 千周期时间尺度。') +
                 '（a）问题二方案；（b）固定驻留图重排后的问题三方案。灰色条段为原始操作，红色斜线条段为换入换出；各行对应一个执行单元。' +
                 ('条段上方数字为原始节点编号 136、172、173。' if local else ''))

    if not all(sha(ROOT/p) == digest for p, digest in inputs.items()):
        raise RuntimeError('Input changed during redraw')
    (out/'plotted-data.json').write_text(json.dumps(plotted, ensure_ascii=False), encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({'inputs_sha256': inputs, 'results': results,
        'plotted_data_sha256': sha(out/'plotted-data.json')}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if any(r['status'] != 'PASS' for r in results.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
