"""Query a private short-lived Codex app-server; no thread or model turn is created."""
import json
from pathlib import Path
import queue
import shutil
import subprocess
import threading

root = Path(__file__).resolve().parents[1]
binary = shutil.which('codex')
if not binary:
    raise SystemExit('codex not on PATH')
local = root / '.local'
local.mkdir(exist_ok=True)
messages = queue.Queue()
with (local / 'codex-loader-stderr.log').open('w', encoding='utf-8') as errors:
    process = subprocess.Popen([binary, 'app-server', '--stdio'], cwd=root,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                               text=True, encoding='utf-8')
    def read_output():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass
    threading.Thread(target=read_output, daemon=True).start()
    def send(message):
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()
    def response(identifier):
        import time
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            message = messages.get(timeout=max(0.01, deadline - time.monotonic()))
            if message.get('id') == identifier:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message['result']
        raise TimeoutError('Codex loader response timeout')
    try:
        send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'native-workspace-probe', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}}})
        response(1)
        send({'method': 'initialized'})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(root)], 'forceReload': True}})
        result = response(2)
        project_skills = []
        loader_errors = []
        for entry in result.get('data', []):
            loader_errors.extend(entry.get('errors', []))
            for skill in entry.get('skills', []):
                path = Path(skill.get('path', ''))
                try:
                    path.resolve().relative_to(root)
                except ValueError:
                    continue
                project_skills.append({'name': skill['name'], 'path': str(path), 'enabled': skill.get('enabled')})
        print(json.dumps({'project_skills': project_skills, 'errors': loader_errors, 'model_turns': 0}, ensure_ascii=False, indent=2))
        expected = {p.parent.name for p in (root / '.agents/skills').glob('*/SKILL.md')
                    if not p.parent.name.startswith('_')}
        if {item['name'] for item in project_skills} != expected or len(project_skills) != len(expected) or loader_errors:
            raise SystemExit(1)
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()  # Only this process created above, never a shared Codex process.
            process.wait(timeout=5)
