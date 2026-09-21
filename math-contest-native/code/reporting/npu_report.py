"""AI-assisted with OpenAI Codex; exact model/release unknown. See AI_USAGE.md.
Generate tables, Chinese figures and evidence bindings from one completed run.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run = args.run
    rows = json.loads((run / 'summary.json').read_text(encoding='utf-8'))
    candidates = json.loads((run / 'candidates.json').read_text(encoding='utf-8'))
    figures, tables = Path('figures/npu2025'), Path('paper/tables')
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    os.environ['MPLCONFIGDIR'] = str(Path('.local/mpl-npu').resolve())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import numpy as np
    available = {x.name for x in font_manager.fontManager.ttflist}
    font = next(x for x in ('Microsoft YaHei', 'SimHei', 'SimSun') if x in available)
    plt.rcParams.update({'font.family': font, 'font.size': 10, 'pdf.fonttype': 42})
    labels = ['卷积小图', '卷积大图', '注意力小图', '注意力大图', '矩阵乘小图', '矩阵乘大图']
    x = np.arange(6)
    saved = []

    def save(fig, name):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            fig.tight_layout()
            fig.savefig(figures / (name + '.pdf'), bbox_inches='tight')
            fig.savefig(figures / (name + '.png'), dpi=160, bbox_inches='tight')
        assert not [w for w in caught if 'Glyph' in str(w.message) and 'missing' in str(w.message)]
        saved.append(name)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(x-.18, [r['baseline']['peak']['total'] for r in rows], .36, label='编号基准', color='#8598ad')
    ax.bar(x+.18, [r['problem1']['peak']['total'] for r in rows], .36, label='最小峰值候选', color='#1c756c')
    ax.set_xticks(x, labels)
    ax.set_ylabel('驻留峰值（题面容量单位）')
    ax.legend(frameon=False)
    save(fig, 'peak')
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(x-.18, [r['problem2']['cycles']/1000 for r in rows], .36, label='缓存优先方案', color='#8598ad')
    ax.bar(x+.18, [r['problem3']['cycles']/1000 for r in rows], .36, label='流水优化方案', color='#1c756c')
    ax.set_xticks(x, labels)
    ax.set_ylabel('执行时间（千周期）')
    ax.legend(frameon=False)
    save(fig, 'time')
    fig, axes = plt.subplots(2, 3, figsize=(9, 5.3))
    for row, label, ax in zip(rows, labels, axes.flat):
        data = [c for c in candidates if c['graph'] == row['graph']]
        ax.scatter([c['traffic']/1000 for c in data], [c['cycles']/1000 for c in data], s=14, color='#8598ad', label='初始候选')
        ax.scatter([row['problem3']['traffic']/1000], [row['problem3']['cycles']/1000], marker='*', s=80, color='#b85536', label='最终方案')
        ax.text(.03, .94, label, va='top', transform=ax.transAxes)
        ax.set_xlabel('搬运量（千容量单位）')
        ax.set_ylabel('执行时间（千周期）')
    axes[0, 0].legend(loc='lower right', fontsize=8, frameon=False)
    save(fig, 'tradeoff')
    timeline = json.loads((run / 'FlashAttention_Case0_timeline.json').read_text())
    pipes = ['MTE2', 'MTE1', 'CUBE', 'FIXP', 'VECTOR', 'MTE3']
    pipelabels = ['输入搬运单元', '片内搬运单元', '矩阵计算单元', '结果搬运单元', '向量计算单元', '输出搬运单元']
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for i, pipe in enumerate(pipes):
        ordinary = [(s, e-s) for _, p, s, e, op in timeline if p == pipe and not op.startswith('SPILL') and e > s]
        spill = [(s, e-s) for _, p, s, e, op in timeline if p == pipe and op.startswith('SPILL') and e > s]
        ax.broken_barh(ordinary, (i-.32, .64), facecolors='#1c756c')
        ax.broken_barh(spill, (i-.32, .64), facecolors='#b85536')
    ax.set_yticks(range(6), pipelabels)
    ax.set_xlabel('时间（周期）')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color='#1c756c', label='原始操作'), Patch(color='#b85536', label='换入换出')], frameon=False, ncol=2, loc='lower center', bbox_to_anchor=(.5, 1.02))
    save(fig, 'pipeline')
    escaped = lambda name: name.replace('_', r'\_')
    q1 = []
    q2 = []
    q3 = []
    for row in rows:
        name = escaped(row['graph'])
        q1.append(f"{name} & {row['baseline']['peak']['total']} & {row['problem1']['peak']['total']} " + r'\\')
        q2.append(f"{name} & {row['problem2']['traffic']} & {row['problem2']['spills']} & {row['problem2']['cycles']} " + r'\\')
        q3.append(f"{name} & {row['problem3']['traffic']} & {row['problem3']['cycles']} & {row['cycle_improvement_pct']:.2f} " + r'\\')
    for name, content, columns, header in [('problem1', q1, 'lrr', '计算图 & 编号基准 & 问题一结果'),
                                          ('problem2', q2, 'lrrr', '计算图 & 搬运量 & 换出次数 & 周期'),
                                          ('problem3', q3, 'lrrr', r'计算图 & 搬运量 & 周期 & 降低比例（\%）')]:
        body = r'\begin{tabular}{' + columns + r'}\toprule ' + header + r'\\\midrule' + '\n'
        body += '\n'.join(content) + '\n' + r'\bottomrule\end{tabular}' + '\n'
        (tables / (name+'.tex')).write_text(body, encoding='utf-8')
    low, high = min(r['cycle_improvement_pct'] for r in rows), max(r['cycle_improvement_pct'] for r in rows)
    (tables / 'abstract_numbers.tex').write_text(f'在额外搬运量保持不变时，六个计算图的总执行时间降低 {low:.2f}\\% 至 {high:.2f}\\%。', encoding='utf-8')
    md = ['# 计算结果', '', '## 运行环境与证据', '',
          f'采用 `{run.as_posix()}`，上游候选搜索为 npu2025-a-003。Python 版本见 environment.json；求解仅用标准库，绘图依赖版本另记 figure_manifest.json。无随机过程。', '',
          '六图 JSON/CSV 全字段一致；节点连续、依赖无重复、ALLOC 根/FREE 叶结构通过。数据未清洗改写。', '',
          '## 三问结果', '', '|计算图|编号基准峰值|问题一峰值|问题二搬运量|问题二周期|问题三搬运量|问题三周期|时间降低|',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        md.append(f"|{r['graph']}|{r['baseline']['peak']['total']}|{r['problem1']['peak']['total']}|{r['problem2']['traffic']}|{r['problem2']['cycles']}|{r['problem3']['traffic']}|{r['problem3']['cycles']}|{r['cycle_improvement_pct']:.2f}%|")
    md += ['', '上述容量和搬运量均为题面抽象单位，不能自行标成字节。所有结果是实测启发式可行解，没有全局最优性证明。问题一在五图上没有超过生命周期收缩后的编号基准，应保留该基准。', '',
           '## 候选选择与敏感性', '', '每图比较 8 种顺序（编号、三组内存贪心、两组流水贪心、两种深度优先）、两种换出准则，并对距离换出增加地址轮换，共 24 个候选；六图合计 144 个。固定驻留图的两个优先级在两个出发方案上再比较，共 24 次优化。参数组合与完整指标保存在 candidates.json 和 refinements.json。', '',
           '局部缓存贪心在多图上恶化，因此没有因算法命名而强行采用。逆向前驱 DFS 也不稳定。问题二在编号、内存及 DFS 的最佳适配候选中先最小化搬运量再最小化时间；问题三筛选搬运量不增加的全部方案，再进行固定驻留图优化。该选择属于同一批输入上的算法比较，不是独立泛化测试。', '',
           '## 校验与失败记录', '', '42 个题面格式文本附件已从磁盘重新读回，验证原节点/新增节点唯一、全部原始依赖、SPILL 编号与配对、缓存边界、连续区间不重叠、操作使用时驻留、复用同步和同单元互斥。独立校验器不导入求解器。check_npu.py 的手算图同时验证并行、地址复用和两类搬运耗时，并拒绝重叠、逆依赖、越界及重复节点。', '',
           '001 因受保护区间碎片失败；002 为首次完整基准；003 增加 DFS 和地址轮换；004 固定驻留图重排；005 将新增 SPILL 编号按实际 OUT 出现顺序规范化，修正附件排序歧义。旧 run 均保留，不覆盖。', '',
           'SPILL 释放地址按驻留段进行同步，是对附录 C 未详细展开情形的明确解释；官方评测器未提供，官方评测一致性仍为 UNVERIFIED。', '',
           '## 图表', '', '四图位于 figures/npu2025：peak.pdf（问题一峰值）、time.pdf（问题三时间）、tradeoff.pdf（候选敏感性）、pipeline.pdf（注意力小图完整流水）。图内说明为中文，字体 '+font+'；生成时缺字检查通过，最终视觉检查另见 VERIFY_REPORT。对应数据为本 run 的 summary/candidates/timeline。', '',
           '## 可复现命令', '', '`.venv/Scripts/python.exe -B scripts/run.py --config configs/npu2025.json --id <新的搜索ID>`', '',
           '固定驻留优化使用 configs/npu2025-refine.json，其 base 明确指向已保留的 003；更换 base 后必须同步 config.inputs 的全部文件。', '',
           '本结果与代码由 OpenAI Codex 辅助完成；精确模型版本及发布日期未确证，详见 AI_USAGE.md。']
    Path('reports/RESULTS_REPORT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    bindings = {'schema_version': '1.0', 'status': 'COMPUTED', 'run_id': run.name,
                'numbers_path': (run/'summary.json').as_posix(), 'numbers_sha256': hashlib.sha256((run/'summary.json').read_bytes()).hexdigest(),
                'entries': [{'graph': r['graph'], 'problem1': r['problem1'], 'problem2': r['problem2'], 'problem3': r['problem3']} for r in rows], 'human_review': 'pending'}
    Path('paper/bindings.json').write_bytes((json.dumps(bindings, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    (figures / 'figure_manifest.json').write_text(json.dumps({'run': run.name, 'font': font, 'matplotlib': matplotlib.__version__, 'numpy': np.__version__, 'missing_glyph_warnings': [], 'figures': saved, 'visual_review': 'UNVERIFIED'}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'figures': saved, 'run': run.name}))


if __name__ == '__main__':
    main()
