"""Run an explicit local experiment; execution evidence is not scientific validation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return {'sha256': h.hexdigest(), 'bytes': path.stat().st_size}


def inside(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('Expected a nonempty relative path')
    path = (root / value).resolve()
    path.relative_to(root.resolve())
    return path


def save(path, data):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def execute(root, config_name, run_id):
    root = Path(root).resolve()
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}', run_id):
        raise ValueError('Invalid run id')
    config_path = inside(root, config_name)
    raw = config_path.read_bytes()
    config = json.loads(raw)
    for key in ('argv', 'inputs', 'sources', 'expect'):
        if not isinstance(config.get(key), list) or not config[key]:
            raise ValueError(key + ' must be a nonempty list')
        if any(not isinstance(item, str) or not item for item in config[key]):
            raise ValueError(key + ' must contain nonempty strings')
    tracked = list(dict.fromkeys([config_name] + config['inputs'] + config['sources']))
    before = {name: digest(inside(root, name)) for name in tracked}
    if before[config_name]['sha256'] != hashlib.sha256(raw).hexdigest():
        raise ValueError('Configuration changed while preparing run')
    timeout = config.get('timeout_seconds', 300)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
        raise ValueError('timeout_seconds must be in (0, 86400]')
    run = inside(root, 'results/runs/' + run_id)
    for name in config['expect']:
        output = inside(run, name)
        if output.name in ('result.json', 'result.pending', 'stdout.log', 'stderr.log', 'config.json'):
            raise ValueError('Expected artifact conflicts with evidence file')
    run.mkdir(parents=True, exist_ok=False)
    argv = [part.replace('{python}', sys.executable).replace('{run}', str(run)) for part in config['argv']]
    record = {
        'run_id': run_id, 'status': 'RUNNING', 'scientific_validation': 'UNVERIFIED',
        'started_at': datetime.now(timezone.utc).isoformat(), 'argv': argv,
        'cwd': str(root), 'python': sys.executable, 'python_version': sys.version,
        'inputs_and_sources': before, 'exit_code': None, 'outputs': {},
        'expected': config['expect'], 'errors': [],
        'environment_note': 'Inherited process environment; credentials are not recorded. Freeze domain dependencies separately.'
    }
    save(run / 'result.json', record)
    (run / 'config.json').write_bytes(raw)
    env = os.environ.copy()
    env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1', 'CONTEST_RUN_DIR': str(run)})
    try:
        with (run / 'stdout.log').open('wb') as out, (run / 'stderr.log').open('wb') as err:
            completed = subprocess.run(argv, cwd=root, env=env, stdout=out, stderr=err, timeout=timeout, shell=False)
        record['exit_code'] = completed.returncode
        if completed.returncode:
            record['errors'].append('COMMAND_FAILED')
    except (OSError, subprocess.TimeoutExpired) as error:
        record['errors'].append(type(error).__name__ + ': ' + str(error))
    for name, expected in before.items():
        try:
            if digest(inside(root, name)) != expected:
                record['errors'].append('INPUT_OR_SOURCE_CHANGED: ' + name)
        except (OSError, ValueError):
            record['errors'].append('INPUT_OR_SOURCE_MISSING: ' + name)
    for name in config['expect']:
        try:
            output = inside(run, name)
            info = digest(output)
            if info['bytes'] == 0:
                raise ValueError('Empty output')
            record['outputs'][name] = info
        except (OSError, ValueError) as error:
            record['errors'].append('OUTPUT_INVALID: ' + name + ': ' + str(error))
    record['status'] = 'EXECUTED' if not record['errors'] else 'FAIL'
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    save(run / 'result.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--config', required=True)
    parser.add_argument('--id', required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root, args.config, args.id)
    except (OSError, ValueError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps({'run_id': result['run_id'], 'status': result['status'], 'errors': result['errors']}))
    return 0 if result['status'] == 'EXECUTED' else 1


if __name__ == '__main__':
    sys.exit(main())
