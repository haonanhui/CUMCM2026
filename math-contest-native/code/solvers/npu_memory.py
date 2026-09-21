"""Contiguous best-fit allocator with farthest-next-use eviction."""
from collections import deque
from interfaces.npu import CAPACITY


def allocate(g, order, victim_policy='distance', placement='best'):
    future = {b: deque() for b in g.buffers}
    for i, v in enumerate(order):
        for b in g.nodes[v].get('Bufs', []):
            future[b].append(i)
    cells = {t: [None] * size for t, size in CAPACITY.items()}
    resident, initial, spilled, spills, extended = {}, {}, {}, [], []
    alloc_done, freed = set(), set()
    cursor = {t: 0 for t in CAPACITY}

    def gap(t, size):
        free = []
        start = None
        for j, value in enumerate(cells[t] + [False]):
            if value is None and start is None:
                start = j
            if value is not None and start is not None:
                if j - start >= size:
                    free.append((j - start, start))
                start = None
        if not free:
            return None
        if placement == 'rotate':
            starts = []
            for length, begin in free:
                latest = begin + length - size
                candidate = cursor[t] if begin <= cursor[t] <= latest else begin
                starts.append(candidate)
            return min(starts, key=lambda x: (x-cursor[t]) % CAPACITY[t])
        return min(free)[1]

    def release(b):
        offset = resident.pop(b)
        info = g.buffers[b]
        cells[info['type']][offset:offset + info['size']] = [None] * info['size']

    def evict(b):
        index = len(spills)
        out_id = len(g.nodes) + 2 * index
        spills.append({'buf': b, 'offset': None, 'out': out_id, 'in': out_id + 1})
        spilled[b] = index
        extended.append(out_id)
        release(b)

    def ensure(b, protected, i):
        if b in resident:
            return
        info = g.buffers[b]
        t, size = info['type'], info['size']
        offset = gap(t, size)
        while offset is None:
            choices = [a for a in resident if g.buffers[a]['type'] == t and a not in protected]
            if not choices:
                raise ValueError(('cannot fit operation buffers', g.name, i, b, protected))
            def score(a):
                distance = future[a][0] - i if future[a] else len(order) + 1
                cost = g.buffers[a]['size'] * (1 if a in g.copies else 2)
                return ((distance / cost if victim_policy == 'cost' else distance), g.buffers[a]['size'], -a)
            a = max(choices, key=score)
            evict(a)
            offset = gap(t, size)
        resident[b] = offset
        cursor[t] = (offset + size) % CAPACITY[t]
        cells[t][offset:offset + size] = [b] * size
        if b in spilled:
            entry = spills[spilled.pop(b)]
            entry['offset'] = offset
            extended.append(entry['in'])
        else:
            assert b not in alloc_done and b not in freed
            initial[b] = offset
            alloc_done.add(b)
            extended.append(info['alloc'])

    for i, v in enumerate(order):
        n = g.nodes[v]
        if n['Op'] == 'ALLOC':
            ensure(n['BufId'], {n['BufId']}, i)
        elif n['Op'] == 'FREE':
            b = n['BufId']
            # Even a no-longer-used evicted buffer must receive its paired IN.
            ensure(b, {b}, i)
            extended.append(v)
            release(b)
            freed.add(b)
        else:
            protected = set(n['Bufs'])
            for t, capacity in CAPACITY.items():
                assert sum(g.buffers[b]['size'] for b in protected if g.buffers[b]['type'] == t) <= capacity
            try:
                for b in sorted(protected, key=lambda a: (-g.buffers[a]['size'], a)):
                    ensure(b, protected, i)
            except ValueError:
                # Protected buffers can fragment a cache although their sum fits.
                # Explicitly spill all resident buffers in required types, then pack;
                # never silently relocate live data or discard prior failed work.
                types = {g.buffers[b]['type'] for b in protected}
                for b in list(resident):
                    if g.buffers[b]['type'] in types:
                        evict(b)
                for b in sorted(protected, key=lambda a: (-g.buffers[a]['size'], a)):
                    ensure(b, protected, i)
            extended.append(v)
            for b in protected:
                assert future[b].popleft() == i
    assert not resident and not spilled
    assert all(x['offset'] is not None for x in spills)
    return {'schedule': extended, 'memory': initial, 'spills': spills}
