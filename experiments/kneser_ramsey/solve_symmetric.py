#!/usr/bin/env python3
import argparse, itertools, json, math, time
from pathlib import Path
from pysat.solvers import Cadical195


def rot_set(a, n, shift):
    return tuple(sorted(((x + shift) % n for x in a)))


def edge_key(a, b):
    return tuple(sorted((tuple(a), tuple(b))))


def orbit_key(a, b, n, step):
    order = n // math.gcd(n, step)
    cur = []
    for t in range(order):
        sh = (t * step) % n
        cur.append(edge_key(rot_set(a, n, sh), rot_set(b, n, sh)))
    return min(cur)


def solve(n, k, step, out):
    V = list(itertools.combinations(range(n), k))
    vid = {a:i for i,a in enumerate(V)}

    orbit_to_var = {}
    edge_orbit = {}
    edge_count = 0
    for i,a in enumerate(V):
        A=set(a)
        for j in range(i+1,len(V)):
            b=V[j]
            if A.isdisjoint(b):
                edge_count += 1
                key=orbit_key(a,b,n,step)
                if key not in orbit_to_var:
                    orbit_to_var[key]=len(orbit_to_var)+1
                edge_orbit[(i,j)]=orbit_to_var[key]

    triangles=[]
    clause_set=set()
    for i,a in enumerate(V):
        A=set(a)
        for j in range(i+1,len(V)):
            b=V[j]
            if not A.isdisjoint(b): continue
            AB=A|set(b)
            for h in range(j+1,len(V)):
                c=V[h]
                if AB.isdisjoint(c):
                    x=edge_orbit[(i,j)]; y=edge_orbit[(i,h)]; z=edge_orbit[(j,h)]
                    triangles.append((x,y,z))
                    clause_set.add(tuple(sorted((x,y,z))))
                    clause_set.add(tuple(sorted((-x,-y,-z))))
    clauses=[list(c) for c in clause_set]
    if orbit_to_var:
        clauses.append([1])

    start=time.time()
    with Cadical195(bootstrap_with=clauses) as s:
        sat=s.solve()
        model=s.get_model() if sat else None
    elapsed=time.time()-start
    result={
        'n':n,'k':k,'rotation_step':step,
        'vertices':len(V),'edges':edge_count,'edge_orbits':len(orbit_to_var),
        'triangles':len(triangles),'unique_clauses':len(clauses),
        'satisfiable':bool(sat),'elapsed_seconds':elapsed,
    }
    if sat:
        assn={abs(x):x>0 for x in model if abs(x)<=len(orbit_to_var)}
        result['orbit_colors']=[
            {'representative':[list(key[0]),list(key[1])], 'red':bool(assn[var])}
            for key,var in sorted(orbit_to_var.items(), key=lambda kv:kv[1])
        ]
        # Independent validation against every actual Kneser triangle.
        for x,y,z in triangles:
            vals=(assn[x],assn[y],assn[z])
            assert not (vals[0]==vals[1]==vals[2])
        result['validated_all_triangles']=True

    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({q:result[q] for q in result if q not in {'orbit_colors'}},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--n',type=int,required=True)
    ap.add_argument('--k',type=int,required=True)
    ap.add_argument('--step',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); solve(a.n,a.k,a.step,a.out)
