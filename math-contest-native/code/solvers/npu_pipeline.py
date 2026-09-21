"""Reorder a fixed memory-residency DAG without changing transfer decisions."""
import heapq
from collections import defaultdict


def canonicalize_spills(node_count, sequence, spills):
    """Keep spill-file order equal to OUT appearance order after reordering."""
    old_indices = [(v-node_count)//2 for v in sequence if v >= node_count and (v-node_count) % 2 == 0]
    mapping = {old: new for new, old in enumerate(old_indices)}
    remapped = [v if v < node_count else node_count + 2*mapping[(v-node_count)//2] + (v-node_count)%2 for v in sequence]
    return remapped, [spills[old] for old in old_indices]


def reorder(g, sequence, spills, dependencies, policy='earliest'):
    count = len(sequence)
    succ = [[] for _ in range(count)]
    degree = [len(x) for x in dependencies]
    duration, pipes = [], []
    for v in range(count):
        if v < len(g.nodes):
            node = g.nodes[v]
            duration.append(node.get('Cycles', 0))
            pipes.append(node.get('Pipe', 'MANAGEMENT'))
        else:
            j, parity = divmod(v-len(g.nodes), 2)
            b = spills[j]['buf']
            duration.append(0 if parity == 0 and b in g.copies else 2*g.buffers[b]['size']+150)
            pipes.append('MTE3' if parity == 0 else 'MTE2')
        for u in dependencies[v]:
            succ[u].append(v)
    rank = [0] * count
    for v in reversed(sequence):
        rank[v] = duration[v] + max((rank[u] for u in succ[v]), default=0)
    ready = defaultdict(list)
    earliest = [0] * count
    pipe_clock = defaultdict(int)

    def push(v):
        heapq.heappush(ready[pipes[v]], (-rank[v], v))

    for v in range(count):
        if degree[v] == 0:
            push(v)
    output = []
    while len(output) < count:
        if ready['MANAGEMENT']:
            _, v = heapq.heappop(ready['MANAGEMENT'])
        else:
            heads = [heap[0][1] for pipe, heap in ready.items() if heap]
            assert heads, 'residency dependency cycle'
            if policy == 'critical':
                v = min(heads, key=lambda a: (-rank[a], earliest[a], a))
            else:
                v = min(heads, key=lambda a: (max(earliest[a], pipe_clock[pipes[a]]), -rank[a], a))
            heapq.heappop(ready[pipes[v]])
        output.append(v)
        finish = earliest[v] + duration[v]
        if pipes[v] != 'MANAGEMENT':
            finish = max(earliest[v], pipe_clock[pipes[v]]) + duration[v]
            pipe_clock[pipes[v]] = finish
        for u in succ[v]:
            earliest[u] = max(earliest[u], finish)
            degree[u] -= 1
            if degree[u] == 0:
                push(u)
    return output
