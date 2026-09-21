"""Small hand-calculated cases and mutation rejection for replay semantics."""
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interfaces.npu import load
from validation.npu_replay import replay
from solvers.npu_schedule import schedule, peaks


def main():
    nodes = [
        {'Id': 0, 'Op': 'ALLOC', 'BufId': 0, 'Size': 4, 'Type': 'UB'},
        {'Id': 1, 'Op': 'COPY_IN', 'Pipe': 'MTE2', 'Cycles': 10, 'Bufs': [0]},
        {'Id': 2, 'Op': 'FREE', 'BufId': 0, 'Size': 4, 'Type': 'UB'},
        {'Id': 3, 'Op': 'ALLOC', 'BufId': 1, 'Size': 4, 'Type': 'UB'},
        {'Id': 4, 'Op': 'COPY_OUT', 'Pipe': 'MTE3', 'Cycles': 20, 'Bufs': [1]},
        {'Id': 5, 'Op': 'FREE', 'BufId': 1, 'Size': 4, 'Type': 'UB'}]
    raw = {'Nodes': nodes, 'Edges': [[0, 1], [1, 2], [3, 4], [4, 5]]}
    results = []
    with tempfile.TemporaryDirectory(prefix='npu-check-', dir='.local') as temp:
        p = Path(temp) / 'tiny.json'
        p.write_text(json.dumps(raw))
        g = load(p)
        seq = list(range(6))
        result = replay(g, seq, {0: 0, 1: 4}, [])
        assert result['cycles'] == 20
        results.append('independent-pipes-overlap:20')
        result = replay(g, seq, {0: 0, 1: 0}, [])
        assert result['cycles'] == 30
        results.append('reused-address-serializes:30')
        assert peaks(g, schedule(g))['total'] == 4
        results.append('known-optimal-peak:4')
        for bad_seq, bad_mem in [([0, 3, 1, 4, 2, 5], {0: 0, 1: 0}),
                                 ([1, 0, 2, 3, 4, 5], {0: 0, 1: 4}),
                                 (seq, {0: 1022, 1: 4}),
                                 ([0, 1, 2, 3, 4, 4], {0: 0, 1: 4})]:
            try:
                replay(g, bad_seq, bad_mem, [])
            except AssertionError:
                pass
            else:
                raise AssertionError('invalid attachment accepted')
        results.append('overlap-topology-bounds-duplicates:rejected')
        spillseq = [0, 1, 6, 3, 4, 5, 7, 2]
        result = replay(g, spillseq, {0: 0, 1: 0}, [{'buf': 0, 'offset': 0}])
        assert result['traffic'] == 4 and result['cycles'] == 188
        results.append('copy-in-spill-cost-and-release:4/188')
        result = replay(g, [3, 4, 6, 0, 1, 2, 7, 5], {0: 0, 1: 0}, [{'buf': 1, 'offset': 0}])
        assert result['traffic'] == 8 and result['cycles'] == 346
        results.append('intermediate-spill-cost:8/346')
    print(json.dumps({'status': 'PASS', 'checks': results}, indent=2))


if __name__ == '__main__':
    main()
