"""Generate Chinese research figures and tables from revision-three traces."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT / '.local/mpl-npu-r3')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({'font.family': 'Microsoft YaHei', 'font.size': 10, 'pdf.fonttype': 42, 'axes.unicode_minus': False})
run = ROOT/'results/runs/npu-paper-r3-analysis-001'
figdir = ROOT/'figures/npu2025-r3'
figdir.mkdir(exist_ok=True)
tables = ROOT/'paper/revision3/tables'
a = json.loads((run/'analysis.json').read_text(encoding='utf-8'))
labels = ['卷积小图','卷积大图','注意力小图','注意力大图','矩阵乘小图','矩阵乘大图']

def table(name, headers, rows):
    text = '\\begin{tabular}{l'+'r'*(len(headers)-1)+'}\\toprule\n'
    text += ' & '.join(headers)+'\\\\\\midrule\n'
    text += '\n'.join(' & '.join(map(str,row))+'\\\\' for row in rows)
    text += '\n\\bottomrule\\end{tabular}\n'
    (tables/(name+'.tex')).write_text(text, encoding='utf-8')

table('structure', ['计算图','操作数','缓冲区数','多使用者对象','最多使用者'],
      [[label,r['operations'],r['buffers'],r['reused_buffers'],r['max_users']] for label,r in zip(labels,a['rows'])])
table('spill_types', ['计算图','$D_{L1}$','$D_{UB}$','不同对象','重复事件','最大次数'],
      [[label,r['stages']['2']['traffic_by_type'].get('L1',0),r['stages']['2']['traffic_by_type'].get('UB',0),
        r['stages']['2']['distinct_spilled'],r['stages']['2']['repeat_events'],r['stages']['2']['max_repeats']] for label,r in zip(labels,a['rows'])])
table('peak_composition', ['计算图','$L1$','$UB$','$L0A$','$L0B$','$L0C$'],
      [[label]+[r['q1']['selected']['types_at_peak'].get(t,0) for t in ['L1','UB','L0A','L0B','L0C']] for label,r in zip(labels,a['rows'])])

fig, axes = plt.subplots(2,1,figsize=(6.7,5.4))
for key,label,color,style in [('id','编号基准','#555555','--'),('selected','选定深度优先','#12687a','-'),('memory','局部缓存贪心','#b46536',':')]:
    d=json.loads((run/f'conv_{key}_trajectory.json').read_text())
    axes[0].plot([p[0] for p in d['points']],[p[1] for p in d['points']],label=label,color=color,ls=style,lw=1)
    if key != 'memory':
        points=[p for p in d['points'] if 2180<=p[0]<=2350]
        axes[1].step([p[0] for p in points],[p[1] for p in points],where='post',label=label,color=color,ls=style)
        axes[1].plot(d['position'],d['peak'],'o',color=color)
        axes[1].annotate(str(d['peak']),(d['position'],d['peak']),xytext=(10,8 if key=='id' else -17),textcoords='offset points',fontsize=10)
for ax in axes:
    ax.set_ylabel('驻留量（容量单位）'); ax.set_xlabel('已处理节点位置'); ax.grid(alpha=.18)
fig.legend(*axes[0].get_legend_handles_labels(),frameon=False,ncol=3,fontsize=9,loc='upper center')
axes[0].set_title('（甲）完整序列中的驻留变化',loc='left')
axes[1].set_title('（乙）两种较低峰值方案的局部窗口',loc='left')
fig.tight_layout(rect=(0,0,1,.94)); fig.savefig(figdir/'conv_trajectory.pdf'); plt.close(fig)

fig, axes=plt.subplots(2,1,figsize=(6.7,4.7))
d=json.loads((run/'attention_p2_occupancy.json').read_text())
for ax,index,label,capacity in [(axes[0],1,'一级缓存',4096),(axes[1],2,'统一缓存',1024)]:
    ax.step([x[0] for x in d['trace']],[x[index] for x in d['trace']],where='post',color='#12687a',lw=1)
    ax.axhline(capacity,color='#a15238',ls='--',label='物理容量')
    ax.set_ylabel('驻留量（容量单位）'); ax.set_title(label,loc='left'); ax.grid(alpha=.18)
    ax.legend(frameon=False,loc='upper right',fontsize=9)
axes[-1].set_xlabel('扩展调度序列位置')
fig.tight_layout(); fig.savefig(figdir/'attention_occupancy.pdf'); plt.close(fig)

names={'MTE2':'输入搬运','MTE1':'级间搬运','CUBE':'矩阵计算','VECTOR':'向量计算','MTE3':'输出搬运','FIXP':'结果搬运'}
fig,axes=plt.subplots(2,1,figsize=(6.7,5.4),sharex=True)
for ax,stage in zip(axes,(2,3)):
    data=json.loads((run/f'attention_p{stage}_detail.json').read_text())
    present=[p for p in names if any(v['pipe']==p for v in data)]
    for i,p in enumerate(present):
        for spill,color in [(False,'#8a8a8a'),(True,'#12687a')]:
            intervals=[(v['start'],v['end']-v['start']) for v in data if v['pipe']==p and v['end']>v['start'] and v['op'].startswith('SPILL')==spill and v['end']>8500 and v['start']<11500]
            ax.broken_barh(intervals,(i-.28,.56),facecolors=color,edgecolors='white',linewidth=.35)
        for v in data:
            if v['id'] in (136,172,173) and v['pipe']==p:
                ax.annotate(str(v['id']),(max(8500,v['start']),i+.30),fontsize=9,ha='left')
    ax.set_yticks(range(len(present)),[names[p] for p in present]); ax.grid(axis='x',alpha=.18)
    ax.set_title('（甲）问题二方案' if stage==2 else '（乙）固定驻留图重排后',loc='left')
axes[-1].set_xlim(8500,11500); axes[-1].set_xlabel('执行时间（周期）')
fig.legend(handles=[Patch(facecolor='#8a8a8a',label='原始操作'),Patch(facecolor='#12687a',label='换入换出')],loc='upper center',ncol=2,frameon=False)
fig.tight_layout(rect=(0,0,1,.94)); fig.savefig(figdir/'attention_window.pdf'); plt.close(fig)
print('Three figures and three tables generated from recorded traces.')
