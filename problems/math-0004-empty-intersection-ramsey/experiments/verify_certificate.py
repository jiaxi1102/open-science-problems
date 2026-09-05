#!/usr/bin/env python3
"""Replay the finite certificate independently, using only the standard library."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time


def verify(path: Path) -> dict:
    record = json.loads(path.read_text())
    vertices = [list(s) for s in itertools.combinations(range(6), 3)]
    edges = [list(e) for e in itertools.combinations(range(20), 2)]
    edge_id = {tuple(e): i + 1 for i, e in enumerate(edges)}
    triples, original = [], []
    for a, b, c in itertools.combinations(range(20), 3):
        if set(vertices[a]).intersection(vertices[b], vertices[c]):
            continue
        triples.append([a, b, c])
        cl = [edge_id[a, b], edge_id[a, c], edge_id[b, c]]
        original.extend([cl, [-x for x in cl]])
    for name, expected in [('vertices', vertices), ('edges', edges),
                           ('triangles', triples), ('original_clauses', original)]:
        if record.get(name) != expected:
            raise ValueError(f'Geometric data mismatch: {name}')
    database = list(original)
    count = 0
    for di, step in enumerate(record['derivations']):
        target, hints = step['clause'], step['steps']
        if any(type(x) is not int or x == 0 or abs(x) > 190 for x in target):
            raise ValueError(f'Invalid target literal at derivation {di}')
        assigned = {-x for x in target}
        if any(-x in assigned for x in assigned):
            raise ValueError('Unexpected tautological target')
        if not hints or hints[-1][1] != 0:
            raise ValueError(f'Missing terminal contradiction at derivation {di}')
        for hi, (ci, unit) in enumerate(hints):
            if type(ci) is not int or not 0 <= ci < len(database):
                raise ValueError('Reference must point to a previously proved clause')
            clause = database[ci]
            if any(lit in assigned for lit in clause):
                raise ValueError('A propagation hint references an already satisfied clause')
            remaining = {lit for lit in clause if -lit not in assigned}
            if unit == 0:
                if remaining or hi != len(hints)-1:
                    raise ValueError('Invalid contradiction hint')
            else:
                if remaining != {unit}:
                    raise ValueError('Hint is not a valid unit propagation')
                assigned.add(unit)
            count += 1
        database.append(target)
    if database[-1] != []:
        raise ValueError('The certificate does not end with the empty clause')
    return {'status': 'PASS', 'vertices': len(vertices), 'edge_variables': len(edges),
            'empty_intersection_triples': len(triples), 'original_clauses': len(original),
            'derived_clauses': len(record['derivations']), 'propagation_steps': count,
            'certificate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'trust_boundary': 'Independent executable check; not a substitute for Lean'}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    result = verify(args.certificate)
    result['seconds'] = time.perf_counter() - start
    text = json.dumps(result, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
