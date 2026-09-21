"""Synthetic numerical -> plot -> XeLaTeX -> PDF check; not a competition paper."""
import argparse
import json
from pathlib import Path
import os
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from run import execute, digest

parser = argparse.ArgumentParser()
parser.add_argument('--tex-bin', required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
identifier = 'paper-smoke-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
result = execute(root, 'examples/mean/config.json', identifier)
if result['status'] != 'EXECUTED':
    raise SystemExit('Synthetic solver failed')
numbers = json.loads((root / 'results/runs' / identifier / 'numbers.json').read_text())
assert numbers['mean'] == 5 and numbers['count'] == 4
build = root / '.local' / identifier
build.mkdir(parents=True)
os.environ['MPLCONFIGDIR'] = str(build / 'mpl-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
available_fonts = {font.name for font in font_manager.fontManager.ttflist}
chinese_font = next((name for name in ('Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'SimSun') if name in available_fonts), None)
if chinese_font is None:
    raise SystemExit('No verified Chinese font is installed')
matplotlib.rcParams['font.family'] = [chinese_font]
values = json.loads((root / 'examples/mean/data.json').read_text())
fig, ax = plt.subplots(figsize=(5, 2.4))
ax.plot(range(1, len(values) + 1), values, 'o-', label='合成数据')
ax.axhline(numbers['mean'], color='gray', linestyle='--', label=r'均值 $\bar{x}=5$')
ax.set(xlabel='样本序号', ylabel='数值')
ax.legend()
with warnings.catch_warnings(record=True) as rendered_warnings:
    warnings.simplefilter('always')
    fig.tight_layout()
    fig.savefig(build / 'figure.pdf')
glyph_warnings = [str(item.message) for item in rendered_warnings if 'Glyph' in str(item.message) and 'missing' in str(item.message)]
if glyph_warnings:
    raise RuntimeError(glyph_warnings)
plt.close(fig)
tex = r'''\documentclass{ctexart}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\begin{document}
\section*{原生工作区工具链演练}
本页使用合成数据，仅验证计算、绘图、中文排版和 PDF 生成，不是竞赛论文。
样本数为 COUNT，均值为 MEAN。数字直接读取本次运行输出。
\begin{center}\includegraphics[width=0.85\linewidth]{figure.pdf}\end{center}
\end{document}
'''.replace('COUNT', str(numbers['count'])).replace('MEAN', str(numbers['mean']))
(build / 'main.tex').write_text(tex, encoding='utf-8')
env = os.environ.copy()
env['PATH'] = str(args.tex_bin.resolve()) + os.pathsep + env.get('PATH', '')
command = [str(args.tex_bin.resolve() / 'xelatex.exe'), '-interaction=nonstopmode', '-halt-on-error', 'main.tex']
for iteration in range(2):
    with (build / ('compile-' + str(iteration) + '.log')).open('wb') as log:
        subprocess.run(command, cwd=build, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=90)
from pypdf import PdfReader
pdf = build / 'main.pdf'
pages = len(PdfReader(pdf).pages)
assert pages == 1
evidence = {'status': 'PASS', 'kind': 'synthetic_infrastructure', 'run_id': identifier,
            'pdf': str(pdf), 'pdf_fingerprint': digest(pdf), 'pages': pages,
            'visual_review': 'UNVERIFIED', 'official_template': 'NOT_TESTED',
            'figure_font': chinese_font, 'missing_glyph_warnings': glyph_warnings}
(build / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(evidence, ensure_ascii=False, indent=2))
