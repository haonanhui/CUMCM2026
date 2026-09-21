"""Revalidate delivered attachments, source identity and LaTeX result tables."""
from pathlib import Path
import hashlib
import json
import sys
from zipfile import ZipFile, ZIP_DEFLATED
sys.path.insert(0, str(Path('code').resolve()))
from interfaces.npu import load
from solvers.npu_schedule import peaks
from validation.npu_replay import read_solution, replay
from pypdf import PdfReader

root = Path('.').resolve()
run = Path('results/runs/npu2025-a-005')
rows = json.loads((run/'summary.json').read_text())
assert len(rows) == 6
record = json.loads((run/'result.json').read_text())
assert record['status'] == 'EXECUTED'
for name, info in record['inputs_and_sources'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == info['sha256'], name
checked = []
for row in rows:
    name = row['graph']
    graph = load(next(Path('data/raw/npu2025').rglob(name+'.json')))
    sequence = list(map(int, (run/'Attachment/Problem1'/f'{name}_schedule.txt').read_text().splitlines()))
    assert peaks(graph, sequence) == row['problem1']['peak']
    for problem in (2, 3):
        answer = replay(graph, *read_solution(run/'Attachment'/f'Problem{problem}', name))
        expected = row[f'problem{problem}']
        assert answer['cycles'] == expected['cycles'] and answer['traffic'] == expected['traffic']
    assert row['problem3']['traffic'] <= row['problem2']['traffic']
    assert row['problem3']['cycles'] <= row['problem2']['cycles']
    esc = name.replace('_', r'\_')
    for problem in (1, 2, 3):
        table = Path(f'paper/tables/problem{problem}.tex').read_text(encoding='utf-8')
        line = next(x for x in table.splitlines() if x.startswith(esc+' &'))
        if problem == 1:
            expected_values = [row['baseline']['peak']['total'], row['problem1']['peak']['total']]
        elif problem == 2:
            expected_values = [row['problem2'][key] for key in ('traffic', 'spills', 'cycles')]
        else:
            expected_values = [row['problem3']['traffic'], row['problem3']['cycles']]
        actual = line.split(' & ')
        assert [int(x.strip().replace('\\', '')) for x in actual[1:1+len(expected_values)]] == expected_values
    checked.append(name)
files = sorted((run/'Attachment').rglob('*.txt'))
assert len(files) == 42
archive = Path('results/NPU_2025_A_Attachment.zip')
with ZipFile(archive, 'w', ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.relative_to(run/'Attachment').as_posix())
with ZipFile(archive) as z:
    assert z.testzip() is None and len(z.namelist()) == 42
    for p in files:
        assert z.read(p.relative_to(run/'Attachment').as_posix()) == p.read_bytes()
pdf = Path('paper/NPU_2025_A.pdf')
pdf.write_bytes(Path('paper/build/main.pdf').read_bytes())
reader = PdfReader(pdf)
text = '\n'.join(page.extract_text() for page in reader.pages)
assert len(reader.pages) == 11
assert '第二十一届' not in text
for row in rows:
    for value in (row['problem1']['peak']['total'], row['problem2']['traffic'], row['problem2']['cycles'], row['problem3']['cycles']):
        assert str(value) in text, (row['graph'], value)
result = {'status': 'PASS', 'run': run.name, 'graphs': checked, 'attachment_count': 42,
          'source_and_input_hashes': 'PASS', 'tables_and_pdf_numbers': 'PASS', 'archive_crc_and_contents': 'PASS',
          'pdf_pages': len(reader.pages), 'official_evaluator': 'UNVERIFIED', 'optimality': 'UNPROVEN',
          'rar_packaging': 'NOT_RUN_NO_RAR_TOOL',
          'artifacts': {str(p): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in (archive, pdf)}}
Path('reports/npu-delivery-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
