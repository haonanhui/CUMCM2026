"""Read-only source ingestion for the 2025 NPU problem."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    target = Path('data/raw/npu2025')
    target.mkdir(parents=True, exist_ok=True)
    manifest = []
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_bytes()
        if destination.exists():
            assert destination.read_bytes() == content
        else:
            shutil.copyfile(path, destination)
        manifest.append({'source': str(path), 'local': destination.as_posix(),
                         'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    Path('provenance/npu2025_inputs.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    doc = next(target.glob('*.docx'))
    with ZipFile(doc) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
        paragraphs = []
        for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            text = ''.join(t.text or '' for t in p.iter() if t.tag.endswith('}t'))
            if text:
                paragraphs.append(text)
    derived = Path('data/derived/npu2025')
    derived.mkdir(parents=True, exist_ok=True)
    (derived / 'statement.txt').write_text('\n'.join(paragraphs), encoding='utf-8')
    print(json.dumps({'files': len(manifest), 'paragraphs': len(paragraphs)}))


if __name__ == '__main__':
    main()
