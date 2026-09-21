"""Run unchanged upstream text checks with revision-2 paths and LaTeX resolution."""
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
values = {'PAPER_DIR':'paper/revision2','ROOT_DIR':'.','MAIN_FILE':'paper/revision2/main.tex',
          'SECTIONS_DIR':'paper/revision2/sections','REFERENCES_FILE':'paper/revision2/references.tex',
          'FIGURES_DIR':'figures/npu2025-r2','RESULTS_FILE':'reports/RESULTS_REPORT.md',
          'PROBLEM_ANALYSIS_FILE':'reports/ANALYSIS_MODELING_REPORT.md',
          'ALL_RESULTS_FILE':'results/runs/npu2025-a-005/summary.json'}
os.environ.update({k:str((root/v).resolve()) for k,v in values.items()})
os.environ.update({'NO_INTERNAL_CHECK':'0','EXTRA_INTERNAL_TERMS_STR':''})
script = root/'.agents/skills/6verity/scripts/writing_check.sh'
body = script.read_text(encoding='utf-8').split("python3 - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
old = 'target = (path.parent / ref).resolve()'
assert body.count(old)==1
body = body.replace(old,"target = ((main.parent if main.suffix == '.tex' else path.parent) / ref).resolve()")
exec(compile(body,str(script),'exec'))
