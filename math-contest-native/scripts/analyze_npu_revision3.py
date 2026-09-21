"""Read-only trajectory analysis of retained NPU attachments; deterministic."""
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from interfaces.npu import load, CAPACITY
from solvers.npu_schedule import schedule, peaks
from validation.npu_replay import read_solution, replay


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def trajectory(g, seq):
    live, totals, points, peak_set = set(), Counter(), [], []
    peak = -1
    for k, v in enumerate(seq):
        node = g.nodes[v]
        if node['Op'] in ('ALLOC', 'FREE'):
            b = node['BufId']
            sign = 1 if node['Op'] == 'ALLOC' else -1
            if sign == 1:
                live.add(b)
            else:
                live.remove(b)
            totals[node['Type']] += sign * node['Size']
        total = sum(totals.values())
        points.append([k + 1, total] + [totals[t] for t in CAPACITY])
        if total > peak:
            peak, peak_set = total, sorted(live)
            peak_index, peak_node, peak_types = k + 1, v, dict(totals)
    assert not live and peak == peaks(g, seq)['total']
    return {'peak': peak, 'position': peak_index, 'node': peak_node,
            'types_at_peak': peak_types, 'active_count': len(peak_set),
            'active_buffers': peak_set, 'points': points}


def main():
    out = ROOT / 'results/runs/npu-paper-r3-analysis-001'
    out.mkdir(exist_ok=False)
    base = ROOT / 'results/runs/npu2025-a-005'
    inputs = list(base.rglob('*.json')) + list(base.joinpath('Attachment').rglob('*.txt'))
    inputs += list((ROOT / 'code').rglob('*.py')) + [Path(__file__)]
    rows = json.loads((base / 'summary.json').read_text())
    result = []
    for row in rows:
        name = row['graph']
        source = next((ROOT / 'data/raw/npu2025').rglob(name + '.json'))
        inputs.append(source)
        g = load(source)
        seq1 = list(map(int, (base / 'Attachment/Problem1' / (name + '_schedule.txt')).read_text().split()))
        record = {'graph': name, 'nodes': len(g.nodes), 'edges': len(g.edges),
                  'operations': sum(n['Op'] not in ('ALLOC', 'FREE') for n in g.nodes),
                  'buffers': len(g.buffers), 'op_counts': dict(Counter(n['Op'] for n in g.nodes)),
                  'buffer_types': dict(Counter(b['type'] for b in g.buffers.values())),
                  'max_users': max(map(len, g.users.values())),
                  'reused_buffers': sum(len(us) > 1 for us in g.users.values()),
                  'q1': {}, 'stages': {}}
        for label, seq in [('id', schedule(g, 'id')), ('selected', seq1)]:
            data = trajectory(g, seq)
            if name == 'Conv_Case0':
                (out / ('conv_' + label + '_trajectory.json')).write_text(json.dumps(data), encoding='utf-8')
            record['q1'][label] = {k: v for k, v in data.items() if k not in ('points', 'active_buffers')}
        if name == 'Conv_Case0':
            data = trajectory(g, schedule(g, 'memory', 32, 1))
            (out / 'conv_memory_trajectory.json').write_text(json.dumps(data), encoding='utf-8')
            record['q1']['memory'] = {k: v for k, v in data.items() if k not in ('points', 'active_buffers')}
        assert record['q1']['selected']['peak'] == row['problem1']['peak']['total']
        for stage in (2, 3):
            seq, mem, spills = read_solution(base / ('Attachment/Problem' + str(stage)), name)
            ev = replay(g, seq, mem, spills, capture_dependencies=True)
            assert (ev['cycles'], ev['traffic']) == (row['problem' + str(stage)]['cycles'], row['problem' + str(stage)]['traffic'])
            count, traffic, repeated = Counter(), Counter(), Counter(s['buf'] for s in spills)
            for s in spills:
                b = s['buf']; info = g.buffers[b]
                count[info['type']] += 1
                traffic[info['type']] += info['size'] * (1 if b in g.copies else 2)
            assert sum(traffic.values()) == ev['traffic']
            summary = {'cycles': ev['cycles'], 'traffic': ev['traffic'], 'count_by_type': dict(count),
                       'traffic_by_type': dict(traffic), 'distinct_spilled': len(repeated),
                       'max_repeats': max(repeated.values(), default=0),
                       'repeat_events': sum(v - 1 for v in repeated.values()), 'reuse_edges': ev['reuse_edges']}
            record['stages'][str(stage)] = summary
            if name == 'FlashAttention_Case0':
                by_id = {x[0]: x for x in ev['timeline']}
                ends, previous, detailed = {}, {}, []
                for v in seq:
                    deps = ev['dependencies'][v]
                    dep_end = max((ends[u] for u in deps), default=0)
                    if v in by_id:
                        _, pipe, start, end, op = by_id[v]
                        prior = previous.get(pipe)
                        prior_end = ends[prior] if prior is not None else 0
                        assert start == max(dep_end, prior_end)
                        detailed.append({'id': v, 'pipe': pipe, 'op': op, 'start': start, 'end': end,
                                         'previous': prior, 'pipe_ready': prior_end, 'dependency_ready': dep_end,
                                         'binding_predecessors': [u for u in deps if ends[u] == dep_end],
                                         'gap': start - prior_end})
                        ends[v] = end; previous[pipe] = v
                    else:
                        ends[v] = dep_end
                (out / ('attention_p' + str(stage) + '_detail.json')).write_text(json.dumps(detailed), encoding='utf-8')
                vector = [d for d in detailed if d['pipe'] == 'VECTOR']
                summary['largest_vector_gap'] = max(vector, key=lambda d: d['gap'])
                # Sequence occupancy is a logical replay trace, not cycle occupancy.
                occupancy, resident, trace, events = Counter(), {}, [], []
                for k, v in enumerate(seq):
                    node = g.nodes[v] if v < len(g.nodes) else None
                    op = node['Op'] if node else ('SPILL_OUT' if (v-len(g.nodes)) % 2 == 0 else 'SPILL_IN')
                    if op in ('ALLOC', 'FREE', 'SPILL_IN', 'SPILL_OUT'):
                        b = node['BufId'] if node else spills[(v-len(g.nodes))//2]['buf']
                        info = g.buffers[b]; t = info['type']; size = info['size']
                        before = occupancy[t]
                        if op in ('ALLOC', 'SPILL_IN'):
                            offset = mem[b] if op == 'ALLOC' else spills[(v-len(g.nodes))//2]['offset']
                            resident[b] = offset; occupancy[t] += size
                        else:
                            offset = resident.pop(b); occupancy[t] -= size
                        events.append({'position': k+1, 'id': v, 'op': op, 'buffer': b, 'type': t,
                                       'size': size, 'offset': offset, 'before': before, 'after': occupancy[t]})
                    trace.append([k+1] + [occupancy[t] for t in CAPACITY])
                assert not resident and not any(occupancy.values())
                (out / ('attention_p' + str(stage) + '_occupancy.json')).write_text(json.dumps({'trace': trace, 'events': events}), encoding='utf-8')
        result.append(record)
        print(name, 'replayed', flush=True)
    # Exhaust all legal topological orders of a defined nine-node teaching DAG.
    sizes = {'a': 4, 'b': 3, 'c': 5}
    nodes = ['Aa', 'Ab', 'Ac', 'u', 'v', 'w', 'Fa', 'Fb', 'Fc']
    edges = [('Aa','u'),('Aa','v'),('Ab','v'),('Ab','w'),('Ac','w'),
             ('u','v'),('v','w'),('v','Fa'),('w','Fb'),('w','Fc'),('u','Fa')]
    pred = {v: {u for u,w in edges if w == v} for v in nodes}
    hist = Counter()
    def visit(done, total, peak):
        if len(done) == len(nodes):
            assert total == 0
            hist[peak] += 1
            return
        for v in nodes:
            if v not in done and pred[v] <= done:
                nxt = total + (sizes[v[1]] if v[0] == 'A' else -sizes[v[1]] if v[0] == 'F' else 0)
                visit(done | {v}, nxt, max(peak, nxt))
    visit(set(), 0, 0)
    assert min(hist) == 8
    output = {'command': 'python -B scripts/analyze_npu_revision3.py', 'python': platform.python_version(),
              'seed': None, 'deterministic': True, 'capacity': CAPACITY, 'rows': result,
              'toy': {'sizes': sizes, 'edges': edges, 'topological_orders': sum(hist.values()),
                      'peak_histogram': dict(hist), 'minimum': min(hist)},
              'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(inputs))}}
    (out / 'analysis.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'rows': result, 'toy': output['toy']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
