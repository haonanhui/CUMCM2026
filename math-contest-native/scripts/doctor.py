"""Read-only environment inventory, with a temporary project-local write probe."""
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import tempfile


def inspect(root):
    local = root / '.local'
    local.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='doctor-', dir=local) as directory:
        probe = Path(directory) / 'write.txt'
        probe.write_text('native-workspace', encoding='utf-8')
        writable = probe.read_text(encoding='utf-8') == 'native-workspace'
    packages = {}
    for name in ('numpy', 'scipy', 'pandas', 'matplotlib', 'scikit-learn', 'openpyxl', 'PyYAML'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    tools = {name: shutil.which(name) for name in ('git', 'codex', 'dsh', 'typst', 'xelatex', 'latexmk', 'drawio', 'pdftoppm', 'mutool')}
    skills = sorted(p.parent.name for p in (root / '.agents/skills').glob('*/SKILL.md') if not p.parent.name.startswith('_'))
    return {
        'root': str(root), 'python': sys.executable, 'python_version': sys.version,
        'project_writable': writable, 'git_root_present': (root / '.git').exists(),
        'skills_on_disk': skills, 'tools_on_path': tools, 'python_packages': packages,
        'paper_compiler_on_path': bool(tools['typst'] or tools['xelatex']),
        'native_model_read_write': 'UNVERIFIED', 'teammate_device': 'UNVERIFIED',
        'note': 'PATH inventory is not a complete installation search; tool presence is not runtime or model verification.'
    }


if __name__ == '__main__':
    print(json.dumps(inspect(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2))
