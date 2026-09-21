"""Tables and comparison figures for the revised paper, from recorded evidence."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT / '.local/mpl-npu-r2')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.family': 'Microsoft YaHei', 'font.size': 11, 'pdf.fonttype': 42, 'axes.unicode_minus': False})
rows = json.loads((ROOT/'results/runs/npu2025-a-005/summary.json').read_text())
analysis = json.loads((ROOT/'results/runs/npu-paper-r2-analysis-001/analysis.json').read_text(encoding='utf-8'))['rows']
tables = ROOT/'paper/revision2/tables'
figures = ROOT/'figures/npu2025-r2'
labels = ['卷积小图','卷积大图','注意力小图','注意力大图','矩阵乘小图','矩阵乘大图']


def table(name, headers, body):
    text = '\\begin{tabular}{l'+'r'*(len(headers)-1)+'}\\toprule\n'
    text += ' & '.join(headers) + '\\\\\\midrule\n'
    text += '\n'.join(' & '.join(map(str,row))+'\\\\' for row in body)
    text += '\n\\bottomrule\\end{tabular}\n'
    (tables/(name+'.tex')).write_text(text, encoding='utf-8')


table('peaks', ['计算图','$H_{\\rm id}$','$H_1$','$L_H$','$H_1/L_H$'],
      [[label,r['baseline']['peak']['total'],r['problem1']['peak']['total'],a['h_lower'],f"{r['problem1']['peak']['total']/a['h_lower']:.2f}"] for label,r,a in zip(labels,rows,analysis)])
table('traffic', ['计算图','$D_{\\rm id}$','$D_2$','降幅/\\%','换出次数'],
      [[label,r['baseline']['traffic'],r['problem2']['traffic'],f"{100*(1-r['problem2']['traffic']/r['baseline']['traffic']):.2f}",r['problem2']['spills']] for label,r in zip(labels,rows)])
table('stages', ['计算图','$T_2$','$T_A$','$T_F$','$T_3$','降幅/\\%'],
      [[label,r['problem2']['cycles'],a['initial_time_best']['cycles'],a['fixed_p2_best']['cycles'],r['problem3']['cycles'],f"{r['cycle_improvement_pct']:.2f}"] for label,r,a in zip(labels,rows,analysis)])
table('bounds', ['计算图','$L_0$','$L_{\\rm work}$','$L_R$','$T_3$','$g_R$/\\%'],
      [[label,a['mandatory_lower'],a['stages']['3']['lower_bound'],a['stages']['3']['residency_lower'],a['stages']['3']['cycles'],f"{a['stages']['3']['gap_pct']:.2f}"] for label,a in zip(labels,analysis)])
table('utilization', ['计算图','最大工作量单元','$W_p$','$W_p/T_2$/\\%','$W_p/T_3$/\\%'],
      [[label,a['stages']['3']['bottleneck'],max(a['stages']['3']['pipe_work'].values()),f"{100*max(a['stages']['2']['pipe_work'].values())/a['stages']['2']['cycles']:.2f}",f"{100*max(a['stages']['3']['pipe_work'].values())/a['stages']['3']['cycles']:.2f}"] for label,a in zip(labels,analysis)])
table('sensitivity', ['计算图','$H_{32}$','$H_{128}$','$D_{32}$','$D_{128}$','顺序相同'],
      [[label,a['parameter_comparison'][2]['peak']['total'],a['parameter_comparison'][3]['peak']['total'],a['parameter_comparison'][2]['traffic'],a['parameter_comparison'][3]['traffic'],'是' if a['window_orders_equal'] else '否'] for label,a in zip(labels,analysis)])

fig, ax = plt.subplots(figsize=(6.5,3.2))
x = np.arange(6)
for offset, key, label, marker, color in [(-.1,'initial_time_best','扩展候选后','s','#7f7f7f'),(.1,'final','固定驻留图重排后','o','#176b80')]:
    values = [100*(1-(a[key]['cycles'] if key != 'final' else r['problem3']['cycles'])/r['problem2']['cycles']) for r,a in zip(rows,analysis)]
    ax.plot(x+offset,values,linestyle='none',marker=marker,color=color,label=label,markersize=6)
    for i,v in enumerate(values):
        if key=='final': ax.annotate(f'{v:.2f}',(i+offset,v),xytext=(0,6),textcoords='offset points',ha='center',fontsize=10)
ax.set_xticks(x,labels,rotation=15)
ax.set_ylabel('相对问题二的时间降幅（%）')
ax.set_ylim(-2,41)
ax.grid(axis='y',alpha=.2)
ax.legend(frameon=False,loc='upper left',fontsize=10)
fig.tight_layout()
fig.savefig(figures/'stage_gain.pdf',bbox_inches='tight')
plt.close(fig)

fig,axes=plt.subplots(2,1,figsize=(6.5,4.4),sharex=True)
pipes=['MTE2','MTE1','CUBE','VECTOR','MTE3','FIXP']
names={'MTE2':'输入搬运','MTE1':'级间搬运','CUBE':'矩阵计算','VECTOR':'向量计算','MTE3':'输出搬运','FIXP':'结果搬运'}
for ax,number in zip(axes,(2,3)):
    data=json.loads((ROOT/f'results/runs/npu-paper-r2-analysis-001/attention_p{number}_timeline.json').read_text())
    present=[p for p in pipes if any(v[1]==p for v in data)]
    for i,p in enumerate(present):
        for spill,color in [(False,'#8c8c8c'),(True,'#176b80')]:
            intervals=[(v[2]/1000,(v[3]-v[2])/1000) for v in data if v[1]==p and v[3]>v[2] and v[4].startswith('SPILL')==spill]
            ax.broken_barh(intervals,(i-.3,.6),facecolors=color,edgecolors='none')
    ax.set_yticks(range(len(present)),[names[p] for p in present])
    ax.set_title('（甲）缓存优先方案' if number==2 else '（乙）固定驻留图重排后',loc='left',fontsize=11)
    ax.grid(axis='x',alpha=.2)
axes[-1].set_xlabel('执行时间（千周期）')
axes[-1].set_xlim(0,49)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor='#8c8c8c',label='原始操作'),Patch(facecolor='#176b80',label='换入换出')],loc='upper center',ncol=2,fontsize=10,frameon=False)
fig.tight_layout(rect=(0,0,1,.94))
fig.savefig(figures/'attention_compare.pdf',bbox_inches='tight')
plt.close(fig)
print('Generated six tables and two figures from recorded runs.')
