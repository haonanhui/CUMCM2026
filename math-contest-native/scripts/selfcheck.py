"""Exercise real execution, failure, collision and source-change evidence in a sandbox."""
import json
from pathlib import Path
import shutil
import tempfile
from run import execute

root = Path(__file__).resolve().parents[1]
local = root / '.local'
local.mkdir(exist_ok=True)
checks = []
with tempfile.TemporaryDirectory(prefix='selfcheck-', dir=local) as directory:
    box = Path(directory)
    shutil.copytree(root / 'examples', box / 'examples')
    (box / 'scripts').mkdir()
    shutil.copy2(root / 'scripts/run.py', box / 'scripts/run.py')
    config_name = 'examples/mean/config.json'
    config_path = box / config_name
    config = json.loads(config_path.read_text(encoding='utf-8'))
    first = execute(box, config_name, 'first')
    second = execute(box, config_name, 'second')
    assert first['status'] == second['status'] == 'EXECUTED'
    assert first['outputs'] == second['outputs']
    assert json.loads((box / 'results/runs/first/numbers.json').read_text())['mean'] == 5
    checks.append('two independent runs reproduce known result')
    try:
        execute(box, config_name, 'first')
        raise AssertionError('duplicate run accepted')
    except FileExistsError:
        checks.append('duplicate run refused')
    config['argv'] = ['{python}', '-c', 'raise SystemExit(7)']
    config_path.write_text(json.dumps(config))
    failed = execute(box, config_name, 'failed')
    assert failed['status'] == 'FAIL' and failed['exit_code'] == 7 and not failed['outputs']
    checks.append('failed command and missing output preserved')
    config['expect'] = ['../escape.json']
    config_path.write_text(json.dumps(config))
    try:
        execute(box, config_name, 'escape')
        raise AssertionError('path escape accepted')
    except ValueError:
        checks.append('output path escape refused')
    config['expect'] = ['numbers.json']
    config['argv'] = ['{python}', '-c', 'from pathlib import Path; Path("examples/mean/data.json").write_text("[0]"); Path(r"{run}/numbers.json").write_text("{}")']
    config_path.write_text(json.dumps(config))
    changed = execute(box, config_name, 'changed')
    assert changed['status'] == 'FAIL'
    assert any(e.startswith('INPUT_OR_SOURCE_CHANGED') for e in changed['errors'])
    checks.append('input mutation detected despite zero exit')
    config['expect'] = []
    config_path.write_text(json.dumps(config))
    try:
        execute(box, config_name, 'empty')
        raise AssertionError('empty expectations accepted')
    except ValueError:
        checks.append('empty expected coverage refused')
print(json.dumps({'status': 'PASS', 'checks': checks, 'scientific_validation': 'UNVERIFIED'}, indent=2))
