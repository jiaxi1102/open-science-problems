#!/usr/bin/env python3
"""Supplementary independent set-based MILP check, not a formal certificate."""
import argparse
import itertools
import json
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    start = time.perf_counter()
    vertices = list(itertools.combinations(range(6), 3))
    edges = list(itertools.combinations(range(20), 2))
    index = {e: i for i, e in enumerate(edges)}
    triples = [t for t in itertools.combinations(range(20), 3)
               if not (set(vertices[t[0]]) & set(vertices[t[1]]) & set(vertices[t[2]]))]
    rows, cols = [], []
    for row, (a, b, c) in enumerate(triples):
        for edge in [(a, b), (a, c), (b, c)]:
            rows.append(row)
            cols.append(index[edge])
    matrix = coo_matrix((np.ones(len(rows)), (rows, cols)),
                        shape=(len(triples), len(edges))).tocsc()
    result = milp(np.zeros(len(edges)), integrality=np.ones(len(edges)),
                  bounds=Bounds(0, 1), constraints=LinearConstraint(matrix, 1, 2),
                  options={'time_limit': args.seconds})
    record = {'vertices': len(vertices), 'variables': len(edges),
              'forbidden_triples': len(triples), 'status': int(result.status),
              'message': result.message, 'scipy_version': scipy.__version__,
              'seconds': time.perf_counter() - start,
              'method': 'SciPy/HiGHS MILP, set-based generator, no symmetry assumptions',
              'trust_boundary': 'Supplementary computation, not a formally checked certificate'}
    text = json.dumps(record, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    print(text, end='')
    if result.status != 2:
        raise SystemExit('The MILP did not establish infeasibility within its budget')


if __name__ == '__main__':
    main()
