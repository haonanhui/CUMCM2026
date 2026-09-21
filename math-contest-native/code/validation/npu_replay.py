"""Independent artifact reader and spatial/temporal replay; no solver imports."""
from collections import defaultdict
from interfaces.npu import CAPACITY


def read_solution(folder, name):
    schedule = [int(x) for x in (folder / (name + '_schedule.txt')).read_text().splitlines()]
    memory = {}
    for line in (folder / (name + '_memory.txt')).read_text().splitlines():
        b, offset = map(int, line.split(':'))
        assert b not in memory
        memory[b] = offset
    spills = []
    for line in (folder / (name + '_spill.txt')).read_text().splitlines():
        b, offset = map(int, line.split(':'))
        spills.append({'buf': b, 'offset': offset})
    return schedule, memory, spills


def replay(g, sequence, memory, spills, capture_dependencies=False):
    n = len(g.nodes)
    assert len(sequence) == n + 2 * len(spills)
    assert set(sequence) == set(range(n + 2 * len(spills)))
    assert [v for v in sequence if v >= n and (v-n) % 2 == 0] == list(range(n, n+2*len(spills), 2)), 'spill file order'
    assert set(memory) == set(g.buffers)
    position = {v: i for i, v in enumerate(sequence)}
    assert all(position[u] < position[v] for u, v in g.edges)
    for j, spill in enumerate(spills):
        b = spill['buf']
        assert b in g.buffers
        assert position[g.buffers[b]['alloc']] < position[n+2*j] < position[n+2*j+1] < position[g.buffers[b]['free']]
    # Occupancy, prior release node per address, and residency readiness.
    occupied = {t: [None] * c for t, c in CAPACITY.items()}
    release_at = {t: [None] * c for t, c in CAPACITY.items()}
    resident, active, suspended, last_uses = {}, set(), {}, defaultdict(list)
    end, start, pipe_end, pipe_work = {}, {}, defaultdict(int), defaultdict(int)
    ready_at = {}
    transfer = 0
    timeline = []
    reuse_edges = set()
    original_cp = {}
    dependencies = [None] * len(sequence) if capture_dependencies else None
    for v in sequence:
        if v < n:
            node = g.nodes[v]
            op = node['Op']
            deps = set(g.pred[v])
            cycles, pipe = node.get('Cycles', 0), node.get('Pipe')
            b = node.get('BufId')
        else:
            j, parity = divmod(v - n, 2)
            b = spills[j]['buf']
            op = 'SPILL_OUT' if parity == 0 else 'SPILL_IN'
            cycles = 0 if parity == 0 and b in g.copies else 2 * g.buffers[b]['size'] + 150
            pipe = 'MTE3' if parity == 0 else 'MTE2'
            deps = set()
        if op in ('ALLOC', 'SPILL_IN'):
            info = g.buffers[b]
            if op == 'ALLOC':
                assert b not in active
                active.add(b)
                offset = memory[b]
            else:
                assert b in active and suspended.get(b) == v - 1
                deps.add(suspended.pop(b))
                offset = spills[(v-n)//2]['offset']
            assert b not in resident
            assert isinstance(offset, int) and 0 <= offset <= CAPACITY[info['type']] - info['size']
            indices = range(offset, offset + info['size'])
            for i in indices:
                assert occupied[info['type']][i] is None, ('overlap', v, b)
                prior = release_at[info['type']][i]
                if prior is not None:
                    deps.add(prior)
                    reuse_edges.add((prior, v))
                occupied[info['type']][i] = b
            resident[b] = offset
            ready_at[b] = v
        elif op in ('FREE', 'SPILL_OUT'):
            assert b in active and b in resident
            deps.add(ready_at[b])
            deps.update(last_uses[b])
            last_uses[b] = []
            info = g.buffers[b]
            offset = resident.pop(b)
            for i in range(offset, offset + info['size']):
                assert occupied[info['type']][i] == b
                occupied[info['type']][i] = None
                release_at[info['type']][i] = v
            if op == 'FREE':
                active.remove(b)
            else:
                suspended[b] = v
                transfer += info['size'] * (1 if b in g.copies else 2)
        else:
            for b in node['Bufs']:
                assert b in active and b in resident, ('nonresident use', v, b)
                deps.add(ready_at[b])
                last_uses[b].append(v)
        assert all(u in end for u in deps), ('backward temporal edge', v, deps - end.keys())
        if capture_dependencies:
            dependencies[v] = sorted(deps)
        start[v] = max([end[u] for u in deps] + ([pipe_end[pipe]] if pipe else [0]))
        end[v] = start[v] + cycles
        if v < n:
            original_cp[v] = max((original_cp[u] for u in g.pred[v]), default=0) + cycles
        if pipe:
            pipe_end[pipe] = end[v]
            pipe_work[pipe] += cycles
            timeline.append([v, pipe, start[v], end[v], op])
    assert not active and not resident and not suspended
    return {'cycles': max(end.values(), default=0), 'traffic': transfer,
            'spills': len(spills), 'reuse_edges': len(reuse_edges),
            'lower_bound': max([max(original_cp.values(), default=0)] + list(pipe_work.values())),
            'pipe_work': dict(pipe_work), 'validation': 'PASS', 'timeline': timeline,
            **({'dependencies': dependencies} if capture_dependencies else {})}
