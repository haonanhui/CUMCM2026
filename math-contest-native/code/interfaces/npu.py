"""Shared immutable graph contract. Sizes use the statement's abstract units."""
from dataclasses import dataclass
from pathlib import Path
import json

CAPACITY = {'L1': 4096, 'UB': 1024, 'L0A': 256, 'L0B': 256, 'L0C': 512}


@dataclass
class Graph:
    name: str
    nodes: list
    edges: list
    pred: list
    succ: list
    buffers: dict
    users: dict
    copies: set


def load(path: Path) -> Graph:
    raw = json.loads(path.read_text(encoding='utf-8'))
    nodes = sorted(raw['Nodes'], key=lambda n: n['Id'])
    assert [n['Id'] for n in nodes] == list(range(len(nodes)))
    pred, succ = [[] for _ in nodes], [[] for _ in nodes]
    edges = [tuple(e) for e in raw['Edges']]
    assert len(edges) == len(set(edges)), 'duplicate edge'
    for u, v in edges:
        assert 0 <= u < len(nodes) and 0 <= v < len(nodes)
        pred[v].append(u)
        succ[u].append(v)
    buffers, users, copies = {}, {}, set()
    for n in nodes:
        if n['Op'] == 'ALLOC':
            b = n['BufId']
            assert b not in buffers and not pred[n['Id']]
            assert n['Type'] in CAPACITY and 0 < n['Size'] <= CAPACITY[n['Type']]
            buffers[b] = {'alloc': n['Id'], 'size': n['Size'], 'type': n['Type']}
            users[b] = []
    for n in nodes:
        if n['Op'] == 'FREE':
            b = n['BufId']
            assert not succ[n['Id']] and 'free' not in buffers[b]
            assert n['Size'] == buffers[b]['size'] and n['Type'] == buffers[b]['type']
            buffers[b]['free'] = n['Id']
        elif n['Op'] != 'ALLOC':
            assert n['Cycles'] >= 0 and n['Pipe']
            n['Bufs'] = list(dict.fromkeys(n['Bufs']))
            for b in n['Bufs']:
                users[b].append(n['Id'])
            if n['Op'] == 'COPY_IN':
                copies.update(n['Bufs'])
    assert all('free' in b for b in buffers.values())
    return Graph(path.stem, nodes, edges, pred, succ, buffers, users, copies)
