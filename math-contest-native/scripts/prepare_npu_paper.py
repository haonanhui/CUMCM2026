"""Adapt the supplied Huawei Cup template; no fabricated team information."""
from pathlib import Path

template = Path('.agents/skills/5writing/templates/zh/huaweibei-latex/main.tex').read_text(encoding='utf-8')
preamble = template.split('\\newcommand{\\coverpage}')[0]
preamble = preamble.replace('fontset=mac', 'fontset=windows').replace('\\linespread{1.68}', '\\linespread{1.0}')
preamble = preamble.replace('\\IfFontExistsTF{Menlo}{\\setmonofont{Menlo}}{}', '\\setmonofont{Consolas}')
preamble = preamble.replace('\\heiti\\bfseries', '\\heiti')
document = r'''
\usepackage{amssymb}
\usepackage{float}
\usepackage{url}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\begin{document}
\begin{titlepage}
\centering
\vspace*{1.6cm}
{\zihao{2}\heiti 2025 年中国研究生数学建模竞赛\par}
\vspace{.6cm}{\zihao{3}A 题\par}\vspace{2cm}
{\zihao{2}\heiti 通用神经网络处理器下的核内调度\par}
\vspace{1cm}
{\zihao{3}\heiti 基于驻留段约束的缓存与流水协同优化\par}
\vspace{1.6cm}
{\zihao{4}2025 年 A 题历史真题研究\par}
\vfill
本稿为学习研究材料，未填写参赛身份信息。\par
\end{titlepage}
\setcounter{page}{1}
\begin{center}
{\zihao{3}\heiti 基于驻留段约束的缓存与流水协同优化}\par
\vspace{1em}{\zihao{4}\heiti 摘\quad 要}
\end{center}
\input{abstract}
\par\noindent\textbf{关键词：}有向无环图；缓存驻留；连续地址分配；换入换出；流水调度
\clearpage
\input{sections/1_restatement}
\input{sections/2_analysis}
\input{sections/3_assumptions}
\input{sections/4_symbols}
\input{sections/5_problem1}
\input{sections/6_problem2}
\input{sections/7_problem3}
\input{sections/8_sensitivity}
\input{sections/9_evaluation}
\input{references}
\clearpage
\appendix
\titleformat{\section}{\centering\fontsize{14pt}{16.8pt}\heiti}{\thesection.}{1em}{}
\input{sections/A_code}
\end{document}
'''
Path('paper/main.tex').write_text(preamble + document, encoding='utf-8')
