#!/usr/bin/env python3
"""Bounded discovery only: an UNSAT outcome is not labeled Lean-verified."""
import argparse
import hashlib
import itertools
import json
import multiprocessing as mp
from pathlib import Path
import time


def worker(n, k, out):
    from pysat.solvers import Cadical195
    started = time.monotonic()
    vertices = [sum(1 << x for x in subset) for subset in itertools.combinations(range(n), k)]
    edges = list(itertools.combinations(range(len(vertices)), 2))
    edge_id = {pair: i+1 for i, pair in enumerate(edges)}
    cnf = []
    triangles = []
    for a, b, c in itertools.combinations(range(len(vertices)), 3):
        if vertices[a] & vertices[b] & vertices[c]:
            continue
        tri = [edge_id[a,b], edge_id[a,c], edge_id[b,c]]
        triangles.append(tri)
        cnf.extend([tri, [-x for x in tri]])
    # No symmetry restrictions: a refutation concerns the full coloring space.
    stats = {'n': n, 'k': k, 'vertices': len(vertices), 'edge_variables': len(edges),
             'forbidden_triples': len(triangles), 'clauses': len(cnf),
             'build_seconds': time.monotonic()-started}
    (out/'instance.json').write_text(json.dumps(stats, indent=2)+'\n')
    with (out/'instance.cnf').open('w') as f:
        f.write(f'p cnf {len(edges)} {len(cnf)}\n')
        for clause in cnf:
            f.write(' '.join(map(str,clause))+' 0\n')
    stats['cnf_sha256'] = hashlib.sha256((out/'instance.cnf').read_bytes()).hexdigest()
    print(json.dumps(stats), flush=True)
    with Cadical195(bootstrap_with=cnf, with_proof=True) as solver:
        sat = solver.solve()
        stats.update(solver.accum_stats())
        stats['solver_result'] = 'SAT' if sat else 'UNSAT'
        if sat:
            model = set(solver.get_model())
            for a,b,c in triangles:
                assert not ((a in model)==(b in model)==(c in model))
            (out/'model.json').write_text(json.dumps(sorted(model,key=abs))+'\n')
            stats['all_forbidden_triples_checked'] = True
        else:
            proof = solver.get_proof()
            (out/'proof.drat').write_text('\n'.join(proof)+'\n')
            stats['proof_lines'] = len(proof)
            stats['proof_status'] = 'DRAT emitted; separate formal verification required'
    stats['elapsed_seconds'] = time.monotonic()-started
    (out/'result.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--n',type=int,required=True)
    p.add_argument('--k',type=int,required=True)
    p.add_argument('--seconds',type=int,default=180)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    child=mp.Process(target=worker,args=(a.n,a.k,a.out));child.start();child.join(a.seconds)
    if child.is_alive():
        child.terminate();child.join(10)
        if child.is_alive():child.kill();child.join()
        result={'n':a.n,'k':a.k,'solver_result':'UNKNOWN','reason':'wall-clock budget exhausted',
                'budget_seconds':a.seconds,'proof_status':'none'}
        (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    elif child.exitcode != 0:
        raise SystemExit(f'Worker failed with exit code {child.exitcode}')

if __name__=='__main__':main()
