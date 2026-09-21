"""Generic bounded-frontier operation ordering and lifetime normalization."""
import heapq
from collections import Counter


def schedule(g, mode='id', window=64, weight=1.0):
    ops = {n['Id'] for n in g.nodes if n['Op'] not in ('ALLOC', 'FREE')}
    degree = {v: sum(u in ops for u in g.pred[v]) for v in ops}
    ready = {v for v in ops if degree[v] == 0}
    remaining = {b: len(us) for b, us in g.users.items()}
    live, done, order = set(), set(), []
    # Reverse topological longest downstream cycle count, independent of Id ordering.
    indeg = degree.copy()
    queue = sorted(ready)
    topo = []
    for v in queue:
        topo.append(v)
        for u in g.succ[v]:
            if u in ops:
                indeg[u] -= 1
                if indeg[u] == 0:
                    queue.append(u)
    assert len(topo) == len(ops), 'cycle'
    rank = {}
    for v in reversed(topo):
        rank[v] = g.nodes[v]['Cycles'] + max((rank[u] for u in g.succ[v] if u in ops), default=0)
    dfs_order, seen = [], set()
    if mode.startswith('dfs'):
        sinks = sorted(v for v in ops if not any(u in ops for u in g.succ[v]))
        for root in sinks:
            stack = [(root, False)]
            while stack:
                v, expanded = stack.pop()
                if expanded:
                    dfs_order.append(v)
                    continue
                if v in seen:
                    continue
                seen.add(v)
                stack.append((v, True))
                parents = sorted((u for u in g.pred[v] if u in ops), reverse=(mode == 'dfs_reverse'))
                stack.extend((u, False) for u in reversed(parents) if u not in seen)
        assert len(dfs_order) == len(ops)
    dfs_iter = iter(dfs_order)
    pipe_clock = Counter()
    ends = {}

    def emit(v):
        assert v not in done
        assert all(u in done for u in g.pred[v]), ('unmet edge', v)
        done.add(v)
        order.append(v)

    def key(v):
        n = g.nodes[v]
        new = sum(g.buffers[b]['size'] for b in n['Bufs'] if b not in live)
        release = sum(g.buffers[b]['size'] for b in n['Bufs'] if remaining[b] == 1)
        if mode == 'memory':
            return (new - weight * release, new, -rank[v], v)
        start = max(pipe_clock[n['Pipe']], max((ends.get(u, 0) for u in g.pred[v]), default=0))
        return (start + weight * new, -rank[v], -release, v)

    while ready:
        if mode.startswith('dfs'):
            v = next(dfs_iter)
            assert v in ready
        else:
            candidates = heapq.nsmallest(window, ready) if mode != 'id' else [min(ready)]
            v = min(candidates, key=key) if mode != 'id' else candidates[0]
        ready.remove(v)
        n = g.nodes[v]
        for b in n['Bufs']:
            if b not in live:
                emit(g.buffers[b]['alloc'])
                live.add(b)
        # Also honor management dependencies that do not occur in Bufs.
        for u in g.pred[v]:
            if g.nodes[u]['Op'] == 'ALLOC' and u not in done:
                emit(u)
                live.add(g.nodes[u]['BufId'])
        emit(v)
        ends[v] = max(pipe_clock[n['Pipe']], max((ends.get(u, 0) for u in g.pred[v]), default=0)) + n['Cycles']
        pipe_clock[n['Pipe']] = ends[v]
        for b in n['Bufs']:
            remaining[b] -= 1
        # A FREE is ready only after every explicit predecessor and every use.
        possible = {u for u in g.succ[v] if g.nodes[u]['Op'] == 'FREE'}
        possible.update(g.buffers[b]['free'] for b in n['Bufs'] if remaining[b] == 0)
        for u in sorted(possible):
            b = g.nodes[u]['BufId']
            if u not in done and remaining[b] == 0 and all(p in done for p in g.pred[u]):
                if b not in live:
                    emit(g.buffers[b]['alloc'])
                    live.add(b)
                emit(u)
                live.remove(b)
        for u in g.succ[v]:
            if u in ops:
                degree[u] -= 1
                if degree[u] == 0:
                    ready.add(u)
    # Empty buffers and purely management edges are unusual but supported.
    while len(done) < len(g.nodes):
        pending = [n['Id'] for n in g.nodes if n['Id'] not in done and all(u in done for u in g.pred[n['Id']])]
        assert pending, 'unreachable nodes'
        for v in pending:
            emit(v)
    return order


def peaks(g, order):
    resident = Counter()
    peak = Counter()
    total = 0
    position = {v: i for i, v in enumerate(order)}
    assert len(position) == len(g.nodes) == len(order)
    assert all(position[u] < position[v] for u, v in g.edges)
    for v in order:
        n = g.nodes[v]
        if n['Op'] in ('ALLOC', 'FREE'):
            resident[n['Type']] += n['Size'] * (1 if n['Op'] == 'ALLOC' else -1)
            assert resident[n['Type']] >= 0
            peak[n['Type']] = max(peak[n['Type']], resident[n['Type']])
            total = max(total, sum(resident.values()))
    assert not any(resident.values())
    return {'total': total, 'by_type': dict(peak)}
