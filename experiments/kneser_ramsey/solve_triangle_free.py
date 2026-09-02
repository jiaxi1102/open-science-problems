#!/usr/bin/env python3
import argparse, itertools, json, time
from pathlib import Path
from pysat.solvers import Cadical195


def kneser_instance(n: int, k: int):
    vertices = list(itertools.combinations(range(n), k))
    edges = []
    edge_id = {}
    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if A.isdisjoint(b):
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles = []
    # A triangle in KG(n,k) is exactly three pairwise-disjoint k-sets.
    for i, a in enumerate(vertices):
        A = set(a)
        for j in range(i + 1, len(vertices)):
            b = vertices[j]
            if not A.isdisjoint(b):
                continue
            AB = A | set(b)
            for h in range(j + 1, len(vertices)):
                c = vertices[h]
                if AB.isdisjoint(c):
                    triangles.append((edge_id[(i, j)], edge_id[(i, h)], edge_id[(j, h)]))
    return vertices, edges, edge_id, triangles


def canonical_partition_units(n, k, vertices, edge_id, seed_type):
    if seed_type is None:
        return []
    if n != 4 * k:
        raise ValueError('canonical K4 seed requires n = 4k')
    blocks = [tuple(range(t*k, (t+1)*k)) for t in range(4)]
    vid = {a:i for i,a in enumerate(vertices)}
    bids = [vid[b] for b in blocks]
    def eid(a,b):
        i,j=sorted((bids[a],bids[b])); return edge_id[(i,j)]

    # Up to S4 relabeling and global color swap, every 2-coloring of K4
    # with no monochromatic triangle has exactly one of these two forms.
    if seed_type == 'matching':
        red = {(0,1),(2,3)}
    elif seed_type == 'path':
        red = {(0,1),(1,2),(2,3)}
    else:
        raise ValueError(seed_type)
    units=[]
    for a in range(4):
        for b in range(a+1,4):
            x=eid(a,b)
            units.append([x if (a,b) in red else -x])
    return units


def solve(n: int, k: int, out: Path, seed_type=None):
    vertices, edges, edge_id, triangles = kneser_instance(n, k)
    clauses = []
    for x, y, z in triangles:
        # Not all red and not all blue. True=red, False=blue.
        clauses.append([x, y, z])
        clauses.append([-x, -y, -z])
    units = canonical_partition_units(n,k,vertices,edge_id,seed_type)
    clauses.extend(units)
    if not units and edges:
        # Global color-swap symmetry only when no stronger canonical seed is used.
        clauses.append([1])

    started = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    elapsed = time.time() - started

    result = {
        'n': n, 'k': k, 'seed_type': seed_type,
        'vertices': len(vertices), 'edges': len(edges),
        'triangles': len(triangles), 'clauses': len(clauses),
        'satisfiable': bool(sat), 'elapsed_seconds': elapsed,
    }
    if sat:
        assignment = {abs(x): x > 0 for x in model if abs(x) <= len(edges)}
        # Independent direct validation of all triangle constraints.
        for x,y,z in triangles:
            vals=(assignment[x],assignment[y],assignment[z])
            assert not (vals[0] == vals[1] == vals[2])
        result['validated_all_triangles']=True
        red = []
        blue = []
        for eid_num, (i, j) in enumerate(edges, 1):
            pair = [list(vertices[i]), list(vertices[j])]
            (red if assignment.get(eid_num, False) else blue).append(pair)
        result['red_edges'] = red
        result['blue_edges'] = blue

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    keys=['n','k','seed_type','vertices','edges','triangles','clauses','satisfiable','elapsed_seconds']
    if sat: keys.append('validated_all_triangles')
    print(json.dumps({q:result[q] for q in keys}, indent=2))
    return sat


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed-type', choices=['matching','path'])
    args = ap.parse_args()
    solve(args.n, args.k, args.out, args.seed_type)
