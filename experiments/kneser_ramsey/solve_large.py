#!/usr/bin/env python3
import argparse, itertools, json, time, hashlib
from pathlib import Path
from pysat.solvers import Cadical195


def vertices(n, k):
    V = list(itertools.combinations(range(n), k))
    return V, {a:i for i,a in enumerate(V)}


def complement_tuple(n, used):
    U=set(used)
    return tuple(x for x in range(n) if x not in U)


def build_edges(n,k,V,vid):
    edges=[]; eid={}
    for i,A in enumerate(V):
        rem=complement_tuple(n,A)
        for B in itertools.combinations(rem,k):
            j=vid[B]
            if j<=i: continue
            eid[(i,j)]=len(edges)+1
            edges.append((i,j))
    return edges,eid


def triangle_iter(n,k,V,vid,eid):
    for i,A in enumerate(V):
        remA=complement_tuple(n,A)
        for B in itertools.combinations(remA,k):
            j=vid[B]
            if j<=i: continue
            remAB=complement_tuple(n,A+B)
            for C in itertools.combinations(remAB,k):
                h=vid[C]
                if h<=j: continue
                yield (eid[(i,j)],eid[(i,h)],eid[(j,h)])


def encode_bits(model, m):
    assn={abs(x):x>0 for x in model if abs(x)<=m}
    raw=bytearray((m+7)//8)
    for i in range(1,m+1):
        if assn.get(i,False): raw[(i-1)//8] |= 1 << ((i-1)%8)
    return raw.hex()


def solve(n,k,out):
    V,vid=vertices(n,k)
    edges,eid=build_edges(n,k,V,vid)
    started=time.time(); triangles=0
    with Cadical195() as s:
        s.add_clause([1]) # global color swap
        for x,y,z in triangle_iter(n,k,V,vid,eid):
            s.add_clause([x,y,z]); s.add_clause([-x,-y,-z]); triangles+=1
        built=time.time()
        sat=s.solve(); model=s.get_model() if sat else None
        solved=time.time()
    result={
        'n':n,'k':k,'vertices':len(V),'edges':len(edges),'triangles':triangles,
        'clauses':2*triangles+1,'satisfiable':bool(sat),
        'build_seconds':built-started,'solve_seconds':solved-built,
        'elapsed_seconds':solved-started,
        'edge_order_sha256':hashlib.sha256(repr(edges).encode()).hexdigest(),
    }
    if sat:
        result['assignment_hex']=encode_bits(model,len(edges))
        result['assignment_sha256']=hashlib.sha256(bytes.fromhex(result['assignment_hex'])).hexdigest()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({q:v for q,v in result.items() if q!='assignment_hex'},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--n',type=int,required=True); ap.add_argument('--k',type=int,required=True); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); solve(a.n,a.k,a.out)
