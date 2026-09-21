"""Synthetic infrastructure exercise. Not competition data or a scientific model."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
values = json.loads(args.input.read_text(encoding='utf-8'))
result = {'kind': 'synthetic_example', 'count': len(values), 'mean': sum(values) / len(values)}
args.output.write_text(json.dumps(result, sort_keys=True) + '\n', encoding='utf-8')
