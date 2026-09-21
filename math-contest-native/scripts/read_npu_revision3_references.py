"""Extract selected local reference pages and official archived instructions."""
import json
import sys
from pathlib import Path
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parents[1]
records = json.loads((root/'reports/paper-organization-measurements-20260921.json').read_text(encoding='utf-8'))
parts = []
for index, pages in [(1,[16,28,29]),(2,[15,16,27]),(4,[25])]:
    path = Path(records[index]['file'])
    reader = PdfReader(path)
    for p in pages:
        parts.append(f'FILE {path.name} PAGE {p}\n'+reader.pages[p-1].extract_text())
for path in (root/'provenance/official2025').glob('*.pdf'):
    reader = PdfReader(path)
    parts.append('FILE '+path.name+'\n'+'\n'.join(p.extract_text() for p in reader.pages))
(root/'reports/npu-r3-evidence/reference-reading.txt').write_text('\n\n'.join(parts),encoding='utf-8')
print('\n\n'.join(parts))
