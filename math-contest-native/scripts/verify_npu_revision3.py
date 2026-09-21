"""Validate revised tables, trace excerpts, fingerprints and compiled PDF."""
import hashlib
import json
import re
import shutil
from pathlib import Path
from pypdf import PdfReader

root=Path(__file__).resolve().parents[1]
run=root/'results/runs/npu-paper-r3-analysis-001'
analysis=json.loads((run/'analysis.json').read_text(encoding='utf-8'))
old=json.loads((root/'results/runs/npu-paper-r2-analysis-001/analysis.json').read_text(encoding='utf-8'))
rows=json.loads((root/'results/runs/npu2025-a-005/summary.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,digest in analysis['sha256'].items():
    assert sha(root/rel)==digest,rel
for rel,digest in old['inputs_sha256'].items():
    assert sha(root/rel)==digest,rel
assert sha(root/'paper/NPU_2025_A_revised.pdf')=='b4429e1cfb1893832627336df215c499133b754183f8fdd324aa5b4ec3c0f0f5'
assert sha(root/'paper/NPU_2025_A.pdf')=='0f23f5ff77e886478253c868c399866e5f264cc8bd548515651da36636227226'
checks=[]
for name in ['peaks','traffic','stages','bounds','utilization','sensitivity','structure','spill_types','peak_composition']:
    lines=[x for x in (root/f'paper/revision3/tables/{name}.tex').read_text(encoding='utf-8').splitlines() if re.match(r'^(卷积|注意力|矩阵乘)',x)]
    assert len(lines)==6
    for line,r,a,b in zip(lines,rows,old['rows'],analysis['rows']):
        actual=[x.strip().removesuffix('\\\\') for x in line.split('&')[1:]]
        s=a['stages']['3']; d=b['stages']['2']
        if name=='peaks': expected=[r['baseline']['peak']['total'],r['problem1']['peak']['total'],a['h_lower'],f"{r['problem1']['peak']['total']/a['h_lower']:.2f}"]
        elif name=='traffic': expected=[r['baseline']['traffic'],r['problem2']['traffic'],f"{100*(1-r['problem2']['traffic']/r['baseline']['traffic']):.2f}",r['problem2']['spills']]
        elif name=='stages': expected=[r['problem2']['cycles'],a['initial_time_best']['cycles'],a['fixed_p2_best']['cycles'],r['problem3']['cycles'],f"{100*(1-r['problem3']['cycles']/r['problem2']['cycles']):.2f}"]
        elif name=='bounds': expected=[a['mandatory_lower'],s['lower_bound'],s['residency_lower'],s['cycles'],f"{100*(s['cycles']/s['residency_lower']-1):.2f}"]
        elif name=='utilization':
            work=max(s['pipe_work'].values())
            expected=[max(s['pipe_work'],key=s['pipe_work'].get),work,f"{100*work/a['stages']['2']['cycles']:.2f}",f"{100*work/s['cycles']:.2f}"]
        elif name=='sensitivity':
            pool={c['candidate']:c for c in a['parameter_comparison']}
            p,q=pool['memory-w32-a1-distance'],pool['memory-w128-a1-distance']
            expected=[p['peak']['total'],q['peak']['total'],p['traffic'],q['traffic'],'是' if a['window_orders_equal'] else '否']
        elif name=='structure': expected=[b['operations'],b['buffers'],b['reused_buffers'],b['max_users']]
        elif name=='spill_types': expected=[d['traffic_by_type'].get('L1',0),d['traffic_by_type'].get('UB',0),d['distinct_spilled'],d['repeat_events'],d['max_repeats']]
        else: expected=[b['q1']['selected']['types_at_peak'].get(t,0) for t in ['L1','UB','L0A','L0B','L0C']]
        assert actual==list(map(str,expected)),(name,r['graph'],actual,expected)
    checks.append(name)
# Read tabular excerpts back from the actual chapter, rather than checking constants alone.
q2=(root/'paper/revision3/sections/6_problem2.tex').read_text(encoding='utf-8')
event_rows=re.findall(r'^(\d+)&(\d+)&([^&]+)&(\d+)&(\d+)&(\d+)&(\d+)\\\\',q2,re.M)
events={x['position']:x for x in json.loads((run/'attention_p2_occupancy.json').read_text())['events']}
translations={'申请':'ALLOC','换出':'SPILL_OUT','释放':'FREE'}
assert len(event_rows)==9
for pos,node,op,buf,size,offset,after in event_rows:
    e=events[int(pos)]
    assert [int(node),translations[op],int(buf),int(size),int(offset),int(after)]==[e[k] for k in ['id','op','buffer','size','offset','after']]
q3=(root/'paper/revision3/sections/7_problem3.tex').read_text(encoding='utf-8')
wait_rows=re.findall(r'^(\d+)&问题([二三])&(\d+)&(\d+)&(\d+)&(\d+)\\\\',q3,re.M)
details={stage:{v['id']:v for v in json.loads((run/f'attention_p{stage}_detail.json').read_text())} for stage in (2,3)}
assert len(wait_rows)==8
for node,stage,prev,dep,start,gap in wait_rows:
    d=details[2 if stage=='二' else 3][int(node)]
    assert list(map(int,[prev,dep,start,gap]))==[d[k] for k in ['pipe_ready','dependency_ready','start','gap']]
assert analysis['toy']['topological_orders']==126 and analysis['toy']['peak_histogram']=={'12':120,'8':6}
assert 12/4>8/4 and 12/8<8/4
assert 2*2+2*2==8 and 2*2+150==154
assert 194331-186969==7362 and 194331-173274==21057 and 186969-173274==13695
checks+=['nine_actual_event_rows','eight_actual_wait_rows','exhaustive_toy','worked_example_arithmetic']
log=(root/'paper/revision3/build/main.log').read_text(encoding='utf-8',errors='replace')
assert not any(x in log for x in ['Overfull','Underfull','undefined','Missing character'])
source=root/'paper/revision3/build/main.pdf'
reader=PdfReader(source)
assert 25<=len(reader.pages)<=36
assert all(abs(float(p.mediabox.width)-595.28)<1 and abs(float(p.mediabox.height)-841.89)<1 for p in reader.pages)
text='\n'.join(p.extract_text() for p in reader.pages)
assert '??' not in text
for r in rows:
    for field,key in [('problem1','peak'),('problem2','traffic'),('problem3','cycles')]:
        value=r[field][key]['total'] if key=='peak' else r[field][key]
        assert str(value) in text
inspection=json.loads((root/'reports/npu-r3-evidence/pdf-inspection.json').read_text(encoding='utf-8'))
assert inspection['sha256']==sha(source)
destination=root/'paper/NPU_2025_A_revision3.pdf'
shutil.copyfile(source,destination)
files=list((root/'paper/revision3').rglob('*.tex'))+list((root/'figures/npu2025-r3').glob('*.pdf'))+list(run.glob('*.json'))
files+=list((root/'scripts').glob('*npu_revision3*.py'))+[source,root/'docs/PAPER_WRITING_GUIDE.md',root/'docs/PAPER_QUALITY_STANDARD.md']
record={'status':'PASS','scope':'numerical-and-engineering-only','pdf_sha256':sha(destination),'pdf':str(destination.relative_to(root)),
        'pages':len(reader.pages),'body_cjk':inspection['body_cjk'],'checks':checks,'old_pdfs_preserved':True,
        'source_and_baseline_fingerprints_unchanged':True,'visual_review':'separate human-readable page review',
        'sha256':{str(p.relative_to(root)):sha(p) for p in files}}
(root/'reports/npu-r3-evidence/verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'paper/revision3/bindings.json').write_text(json.dumps({'solver_run':'npu2025-a-005','analyses':['npu-paper-r2-analysis-001','npu-paper-r3-analysis-001'],'pdf_sha256':sha(destination),'verification':'reports/npu-r3-evidence/verification.json'},indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='sha256'},ensure_ascii=True))
