"""Reproducible six-instance heuristic comparison and exported-result replay."""
import argparse
import csv
import json
import platform
import time
from pathlib import Path
from interfaces.npu import load
from solvers.npu_schedule import schedule, peaks
from solvers.npu_memory import allocate
from validation.npu_replay import read_solution, replay


def write_solution(folder, name, solution):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (name + '_schedule.txt')).write_text(''.join(str(v) + '\n' for v in solution['schedule']))
    (folder / (name + '_memory.txt')).write_text(''.join(f'{b}:{o}\n' for b, o in sorted(solution['memory'].items())))
    (folder / (name + '_spill.txt')).write_text(''.join(f"{s['buf']}:{s['offset']}\n" for s in solution['spills']))


def audit_csv(g, source):
    path = next(source.rglob(g.name + '_Nodes.csv'))
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(g.nodes)
    for row, node in zip(rows, g.nodes):
        assert int(row['Id']) == node['Id'] and row['Op'] == node['Op']
        if node['Op'] in ('ALLOC', 'FREE'):
            assert int(row['BufId']) == node['BufId'] and int(row['Size']) == node['Size'] and row['Type'] == node['Type']
        else:
            assert row['Pipe'] == node['Pipe'] and int(row['Cycles']) == node['Cycles']
            assert sorted(int(x) for x in row['Bufs'].split(',') if x.strip()) == sorted(node['Bufs'])
    with next(source.rglob(g.name + '_Edges.csv')).open(encoding='utf-8-sig', newline='') as stream:
        edges = [(int(r['StartNodeId']), int(r['EndNodeId'])) for r in csv.DictReader(stream)]
    assert edges == g.edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--source', type=Path, default=Path('data/raw/npu2025'))
    args = parser.parse_args()
    run = args.run
    run.mkdir(parents=True, exist_ok=True)
    rows, audits, all_candidates = [], [], []
    variants = [('id', 1, 0), ('memory', 32, 1), ('memory', 128, 1),
                ('memory', 64, 2), ('pipeline', 64, 0), ('pipeline', 64, 1),
                ('dfs', 1, 0), ('dfs_reverse', 1, 0)]
    for path in sorted(args.source.rglob('*.json')):
        began = time.perf_counter()
        g = load(path)
        audit_csv(g, args.source)
        audits.append({'name': g.name, 'nodes': len(g.nodes), 'edges': len(g.edges),
                       'buffers': len(g.buffers), 'csv_json_equal': True})
        candidates = []
        for mode, window, weight in variants:
            tag = f'{mode}-w{window}-a{weight}'
            order = schedule(g, mode, window, weight)
            peak = peaks(g, order)
            for policy in ('distance', 'cost'):
                name = tag + '-' + policy
                begin = time.perf_counter()
                solution = allocate(g, order, policy)
                folder = run / 'candidates' / name
                write_solution(folder, g.name, solution)
                evaluation = replay(g, *read_solution(folder, g.name))
                record = {'graph': g.name, 'candidate': name, 'peak': peak, 'allocation_seconds': time.perf_counter()-begin,
                          **{k: v for k, v in evaluation.items() if k != 'timeline'}}
                candidates.append((record, order, solution, evaluation['timeline']))
                all_candidates.append(record)
                print(json.dumps(record), flush=True)
        # Address rotation spreads reuse across available cache, without changing
        # original operation order. Keep all attempts; traffic gating happens below.
        for prior in list(candidates):
            if not prior[0]['candidate'].endswith('-distance'):
                continue
            name = prior[0]['candidate'] + '-rotate'
            begin = time.perf_counter()
            solution = allocate(g, prior[1], 'distance', 'rotate')
            folder = run / 'candidates' / name
            write_solution(folder, g.name, solution)
            evaluation = replay(g, *read_solution(folder, g.name))
            record = {'graph': g.name, 'candidate': name, 'peak': prior[0]['peak'],
                      'allocation_seconds': time.perf_counter()-begin,
                      **{k: v for k, v in evaluation.items() if k != 'timeline'}}
            candidates.append((record, prior[1], solution, evaluation['timeline']))
            all_candidates.append(record)
            print(json.dumps(record), flush=True)
        best1 = min(candidates, key=lambda x: (x[0]['peak']['total'], x[0]['candidate']))
        # Q2: memory candidates, lexicographic traffic then makespan.
        memory_candidates = [x for x in candidates if not x[0]['candidate'].startswith('pipeline-') and not x[0]['candidate'].endswith('-rotate')]
        best2 = min(memory_candidates, key=lambda x: (x[0]['traffic'], x[0]['cycles']))
        eligible = [x for x in candidates if x[0]['traffic'] <= best2[0]['traffic']]
        best3 = min(eligible, key=lambda x: (x[0]['cycles'], x[0]['traffic']))
        p1 = run / 'Attachment' / 'Problem1'
        p1.mkdir(parents=True, exist_ok=True)
        (p1 / (g.name + '_schedule.txt')).write_text(''.join(f'{v}\n' for v in best1[1]))
        for number, candidate in ((2, best2), (3, best3)):
            folder = run / 'Attachment' / f'Problem{number}'
            write_solution(folder, g.name, candidate[2])
            replay(g, *read_solution(folder, g.name))
        base = candidates[0][0]
        rows.append({'graph': g.name, 'baseline': base, 'problem1': best1[0], 'problem2': best2[0], 'problem3': best3[0],
                     'cycle_improvement_pct': 100 * (best2[0]['cycles']-best3[0]['cycles'])/best2[0]['cycles'],
                     'elapsed_seconds': time.perf_counter()-began})
        (run / (g.name + '_timeline.json')).write_text(json.dumps(best3[3]), encoding='utf-8')
        (run / 'summary.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (run / 'audit.json').write_text(json.dumps(audits, indent=2), encoding='utf-8')
    (run / 'candidates.json').write_text(json.dumps(all_candidates, indent=2), encoding='utf-8')
    (run / 'environment.json').write_text(json.dumps({'python': platform.python_version(), 'platform': platform.platform(), 'seed': None, 'deterministic': True}, indent=2))


if __name__ == '__main__':
    main()
