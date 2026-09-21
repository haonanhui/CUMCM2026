"""AI-assisted with OpenAI Codex; exact model/release unknown. See AI_USAGE.md.

Fixed-traffic refinement and full attachment replay from a completed search run.
"""
import argparse
import json
import shutil
import time
from pathlib import Path
from interfaces.npu import load
from solvers.npu_pipeline import reorder, canonicalize_spills
from solvers.npu_schedule import peaks
from validation.npu_replay import read_solution, replay
from run_npu import write_solution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--base', required=True, type=Path)
    args = parser.parse_args()
    run, base = args.run, args.base
    summary = json.loads((base / 'summary.json').read_text(encoding='utf-8'))
    refinements = []
    shutil.copytree(base / 'Attachment', run / 'Attachment')
    for name in ('audit.json', 'candidates.json', 'environment.json'):
        shutil.copyfile(base / name, run / name)
    for row in summary:
        name = row['graph']
        g = load(next(Path('data/raw/npu2025').rglob(name + '.json')))
        p1path = run / 'Attachment/Problem1' / (name + '_schedule.txt')
        seq1 = list(map(int, p1path.read_text().splitlines()))
        assert peaks(g, seq1) == row['problem1']['peak']
        best_time = row['problem3']['cycles']
        best_data = read_solution(base / 'Attachment/Problem3', name)
        best_info = row['problem3']
        for problem in (2, 3):
            seq, memory, spills = read_solution(base / 'Attachment' / f'Problem{problem}', name)
            evaluated = replay(g, seq, memory, spills, capture_dependencies=True)
            for policy in ('earliest', 'critical'):
                started = time.perf_counter()
                candidate = reorder(g, seq, spills, evaluated['dependencies'], policy)
                candidate, candidate_spills = canonicalize_spills(len(g.nodes), candidate, spills)
                ev = replay(g, candidate, memory, candidate_spills)
                assert ev['traffic'] == evaluated['traffic']
                tag = f'fixed-memory-p{problem}-{policy}'
                write_solution(run / 'refinements' / tag, name, {'schedule': candidate, 'memory': memory, 'spills': candidate_spills})
                info = {'graph': name, 'candidate': tag, 'seconds': time.perf_counter()-started,
                        **{k: v for k, v in ev.items() if k != 'timeline'}}
                refinements.append(info)
                if ev['traffic'] <= row['problem2']['traffic'] and ev['cycles'] < best_time:
                    best_time, best_data, best_info = ev['cycles'], (candidate, memory, candidate_spills), info
                print(json.dumps(info), flush=True)
        row['problem3'] = best_info
        row['cycle_improvement_pct'] = 100*(row['problem2']['cycles']-best_time)/row['problem2']['cycles']
        write_solution(run / 'Attachment/Problem3', name, {'schedule': best_data[0], 'memory': best_data[1], 'spills': best_data[2]})
        final = replay(g, *read_solution(run / 'Attachment/Problem3', name))
        assert final['cycles'] == row['problem3']['cycles'] and final['traffic'] == row['problem3']['traffic']
        (run / (name + '_timeline.json')).write_text(json.dumps(final['timeline']))
        (run / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (run / 'refinements.json').write_text(json.dumps(refinements, indent=2), encoding='utf-8')
    (run / 'validation.json').write_text(json.dumps({'status': 'PASS', 'graphs': len(summary), 'attachment_files': len(list((run/'Attachment').rglob('*.txt'))), 'coverage': ['node-permutation', 'all-original-edges', 'spill-pairing', 'cache-bounds', 'no-overlap', 'resident-use', 'reuse-timing', 'pipe-exclusion', 'transfer-nonincreasing'], 'official_evaluator': 'UNVERIFIED'}, indent=2))


if __name__ == '__main__':
    main()
