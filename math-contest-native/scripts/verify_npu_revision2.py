"""Bind revised PDF/tables to preserved solver evidence and inspect source maths."""
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
evidence = root/'reports/npu-r2-evidence'
analysis_path = root/'results/runs/npu-paper-r2-analysis-001/analysis.json'
analysis = json.loads(analysis_path.read_text(encoding='utf-8'))
rows = json.loads((root/'results/runs/npu2025-a-005/summary.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path, fingerprint in analysis['inputs_sha256'].items():
    assert sha(root/path) == fingerprint, path
assert len(analysis['rows']) == len(rows) == 6
assert sha(root/'paper/NPU_2025_A.pdf') == '0f23f5ff77e886478253c868c399866e5f264cc8bd548515651da36636227226'
checked=[]
for table in ['peaks','traffic','stages','bounds','utilization','sensitivity']:
    lines=[line for line in (root/f'paper/revision2/tables/{table}.tex').read_text(encoding='utf-8').splitlines() if re.match(r'^(卷积|注意力|矩阵乘)',line)]
    assert len(lines)==6
    for line,r,a in zip(lines,rows,analysis['rows']):
        actual=[x.strip().removesuffix('\\\\') for x in line.split('&')[1:]]
        s=a['stages']['3']
        if table=='peaks': expected=[r['baseline']['peak']['total'],r['problem1']['peak']['total'],a['h_lower'],f"{r['problem1']['peak']['total']/a['h_lower']:.2f}"]
        elif table=='traffic': expected=[r['baseline']['traffic'],r['problem2']['traffic'],f"{100*(1-r['problem2']['traffic']/r['baseline']['traffic']):.2f}",r['problem2']['spills']]
        elif table=='stages': expected=[r['problem2']['cycles'],a['initial_time_best']['cycles'],a['fixed_p2_best']['cycles'],r['problem3']['cycles'],f"{100*(1-r['problem3']['cycles']/r['problem2']['cycles']):.2f}"]
        elif table=='bounds': expected=[a['mandatory_lower'],s['lower_bound'],s['residency_lower'],s['cycles'],f"{100*(s['cycles']/s['residency_lower']-1):.2f}"]
        elif table=='utilization':
            assert a['stages']['2']['pipe_work']==s['pipe_work']
            work=max(s['pipe_work'].values())
            expected=[max(s['pipe_work'],key=s['pipe_work'].get),work,f"{100*work/a['stages']['2']['cycles']:.2f}",f"{100*work/s['cycles']:.2f}"]
        else:
            by_name={c['candidate']:c for c in a['parameter_comparison']}
            p,q=by_name['memory-w32-a1-distance'],by_name['memory-w128-a1-distance']
            expected=[p['peak']['total'],q['peak']['total'],p['traffic'],q['traffic'],'是' if a['window_orders_equal'] else '否']
        assert actual==list(map(str,expected)),(table,r['graph'],actual,expected)
    checked.append(table)
log=(root/'paper/revision2/build/main.log').read_text(encoding='utf-8',errors='replace')
assert not any(x in log for x in ['Overfull','Underfull','undefined','Missing character'])
source=root/'paper/revision2/build/main.pdf'
reader=PdfReader(source)
assert len(reader.pages)==17
assert all(abs(float(p.mediabox.width)-595.28)<1 and abs(float(p.mediabox.height)-841.89)<1 for p in reader.pages)
paper_text='\n'.join(p.extract_text() for p in reader.pages)
assert '??' not in paper_text
for row in rows:
    for section,key in [('problem1','peak'),('problem2','traffic'),('problem3','cycles')]:
        value=row[section][key]['total'] if key=='peak' else row[section][key]
        assert str(value) in paper_text
docx=next((root/'data/raw/npu2025').glob('*.docx'))
with ZipFile(docx) as archive:
    xml=ET.fromstring(archive.read('word/document.xml'))
ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
maths=[''.join(m.itertext()) for m in xml.findall('.//m:oMath',ns)]
(evidence/'statement-math.txt').write_text('\n'.join(f'{i+1}: {m}' for i,m in enumerate(maths)),encoding='utf-8')
destination=root/'paper/NPU_2025_A_revised.pdf'
shutil.copyfile(source,destination)
assert sha(source)==sha(destination)
files=list((root/'paper/revision2').rglob('*.tex'))+list((root/'figures/npu2025-r2').glob('*.pdf'))
files+=list((root/'results/runs/npu2025-a-005/Attachment').rglob('*.txt'))
files+=list((root/'scripts').glob('*npu_revision2*.py'))
files+=[analysis_path,source,docx,root/'docs/PAPER_QUALITY_STANDARD.md']
record={'status':'PASS','scope':'engineering-and-numerical-consistency-only','pdf':str(destination.relative_to(root)),
        'pdf_sha256':sha(destination),'pages':len(reader.pages),'tables_checked':checked,'omml_count':len(maths),
        'old_pdf_preserved':True,'source_fingerprints_unchanged':True,
        'inputs_and_outputs_sha256':{str(p.relative_to(root)):sha(p) for p in sorted(set(files))},
        'official_evaluator':'UNVERIFIED','human_review':'UNVERIFIED'}
(evidence/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'paper/revision2/bindings.json').write_text(json.dumps({'solver_run':'npu2025-a-005','derived_analysis':'npu-paper-r2-analysis-001','pdf_sha256':sha(destination),'evidence':'reports/npu-r2-evidence/verification.json'},indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='inputs_and_outputs_sha256'},ensure_ascii=False))
