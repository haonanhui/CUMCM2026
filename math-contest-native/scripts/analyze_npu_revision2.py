"""Derive paper evidence from immutable artifacts; do not alter solver outputs."""
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from interfaces.npu import load, CAPACITY
from validation.npu_replay import read_solution, replay
from solvers.npu_schedule import peaks, schedule


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / 'results/runs/npu-paper-r2-analysis-001'
    output.mkdir(exist_ok=False)
    source = ROOT / 'results/runs/npu2025-a-005'
    base = ROOT / 'results/runs/npu2025-a-003'
    rows = json.loads((source / 'summary.json').read_text())
    candidates = json.loads((source / 'candidates.json').read_text())
    refinements = json.loads((source / 'refinements.json').read_text())
    result, inputs = [], [source / 'summary.json', source / 'candidates.json', source / 'refinements.json']
    for row in rows:
        name = row['graph']
        path = next((ROOT / 'data/raw/npu2025').rglob(name + '.json'))
        inputs.append(path)
        g = load(path)
        cp, original_work = {}, {}
        order = list(map(int, (source / 'Attachment/Problem1' / (name + '_schedule.txt')).read_text().splitlines()))
        assert peaks(g, order) == row['problem1']['peak']
        max_required = {t: 0 for t in CAPACITY}
        for v in order:
            node = g.nodes[v]
            cp[v] = max((cp[u] for u in g.pred[v]), default=0) + node.get('Cycles', 0)
            if node.get('Pipe'):
                pipe = node['Pipe']
                original_work[pipe] = original_work.get(pipe, 0) + node['Cycles']
            for t in CAPACITY:
                required = sum(g.buffers[b]['size'] for b in node.get('Bufs', []) if g.buffers[b]['type'] == t)
                max_required[t] = max(max_required[t], required)
        assert all(max_required[t] <= CAPACITY[t] for t in CAPACITY)
        record = {'graph': name, 'h_lower': max(sum(g.buffers[b]['size'] for b in n.get('Bufs', [])) for n in g.nodes),
                  'mandatory_lower': max(list(cp.values()) + list(original_work.values())),
                  'original_work': original_work, 'max_required': max_required, 'stages': {}}
        for number in (2, 3):
            folder = source / 'Attachment' / ('Problem' + str(number))
            inputs.extend(folder.glob(name + '_*.txt'))
            seq, mem, spills = read_solution(folder, name)
            ev = replay(g, seq, mem, spills, capture_dependencies=True)
            assert ev['cycles'] == row['problem' + str(number)]['cycles']
            assert ev['traffic'] == row['problem' + str(number)]['traffic']
            structural_cp = {}
            for v in seq:
                duration = g.nodes[v].get('Cycles', 0) if v < len(g.nodes) else (0 if (v-len(g.nodes)) % 2 == 0 and spills[(v-len(g.nodes))//2]['buf'] in g.copies else 2*g.buffers[spills[(v-len(g.nodes))//2]['buf']]['size']+150)
                structural_cp[v] = max((structural_cp[u] for u in ev['dependencies'][v]), default=0) + duration
            bound = max(max(structural_cp.values()), ev['lower_bound'])
            record['stages'][str(number)] = {k: v for k, v in ev.items() if k not in ('dependencies', 'timeline')}
            record['stages'][str(number)].update({'residency_lower': bound, 'residency_cp': max(structural_cp.values()),
                                                'gap_pct': 100*(ev['cycles']/bound-1),
                                                'bottleneck': max(ev['pipe_work'], key=ev['pipe_work'].get)})
            if name == 'FlashAttention_Case0':
                (output / ('attention_p' + str(number) + '_timeline.json')).write_text(json.dumps(ev['timeline']))
        pool = [x for x in candidates if x['graph'] == name]
        eligible = [x for x in pool if x['traffic'] <= row['problem2']['traffic']]
        record['initial_time_best'] = min(eligible, key=lambda x: x['cycles'])
        record['fixed_p2_best'] = min([x for x in refinements if x['graph'] == name and x['candidate'].startswith('fixed-memory-p2')], key=lambda x:x['cycles'])
        record['parameter_comparison'] = [x for x in pool if x['candidate'] in ('id-w1-a0-distance', 'id-w1-a0-cost', 'memory-w32-a1-distance', 'memory-w128-a1-distance', 'memory-w64-a2-distance', 'dfs-w1-a0-distance', 'dfs-w1-a0-cost')]
        a, b = schedule(g, 'memory', 32, 1), schedule(g, 'memory', 128, 1)
        record['window_orders_equal'] = a == b
        record['window_order_different_positions'] = sum(x != y for x,y in zip(a,b))
        assert record['stages']['3']['traffic'] <= record['stages']['2']['traffic']
        result.append(record)
    inputs.extend((ROOT / 'code').rglob('*.py'))
    inputs.append(Path(__file__).resolve())
    evidence = {'python': platform.python_version(), 'command': '.venv/Scripts/python.exe scripts/analyze_npu_revision2.py',
                'seed': None, 'deterministic': True, 'inputs_sha256': {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(inputs))},
                'coverage': '12 selected attachments replayed; Q1 peaks recomputed; fixed-residency lower bounds derived; parameter orders recomputed',
                'rows': result}
    (output / 'analysis.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
