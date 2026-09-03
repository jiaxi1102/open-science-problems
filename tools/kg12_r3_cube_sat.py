#!/usr/bin/env python3
"""Create an exhaustive 18-way cube split inside each canonical KG(12,3) branch.

The primary partition is
  012 | 345 | 678 | 9ab.
The overlapping secondary partition is
  036 | 149 | 27a | 58b.

Every red/blue K4 edge coloring without a monochromatic triangle is one of
exactly 18 six-bit patterns. Fixing each secondary pattern therefore partitions
each exact primary branch into 18 exhaustive cubes. SAT in any cube gives a
full coloring. Checked UNSAT in all 18 cubes proves the parent branch UNSAT.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

N = 12
R = 3


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allowed_k4_patterns() -> list[tuple[int, ...]]:
    # Edge order AB,AC,AD,BC,BD,CD.
    edge_pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    edge_index = {pair: i for i, pair in enumerate(edge_pairs)}
    triangles = ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))
    patterns = []
    for bits in itertools.product((0, 1), repeat=6):
        good = True
        for tri in triangles:
            indices = [edge_index[tuple(sorted(pair))] for pair in itertools.combinations(tri, 2)]
            values = [bits[i] for i in indices]
            if values[0] == values[1] == values[2]:
                good = False
                break
        if good:
            patterns.append(bits)
    assert len(patterns) == 18
    counts = {sum(bits) for bits in patterns}
    assert counts == {2, 3, 4}
    return patterns


def build():
    vertices = list(itertools.combinations(range(N), R))
    masks = [sum(1 << x for x in vertex) for vertex in vertices]
    vertex_id = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    edge_id: dict[tuple[int, int], int] = {}
    for i, a in enumerate(masks):
        for j in range(i + 1, len(vertices)):
            if a & masks[j] == 0:
                edge_id[(i, j)] = len(edges) + 1
                edges.append((i, j))

    triangles: list[tuple[int, int, int]] = []
    four_blocks: list[tuple[int, int, int, int]] = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if masks[i] & masks[j]:
                continue
            for k in range(j + 1, len(vertices)):
                if (masks[i] | masks[j]) & masks[k]:
                    continue
                triangles.append((edge_id[(i, j)], edge_id[(i, k)], edge_id[(j, k)]))
                remaining = ((1 << N) - 1) ^ (masks[i] | masks[j] | masks[k])
                l = next(index for index, mask in enumerate(masks) if mask == remaining)
                if l > k:
                    four_blocks.append((i, j, k, l))

    stars: list[tuple[int, int, int]] = []
    for block in four_blocks:
        for center in block:
            row=[]
            for other in block:
                if other == center:
                    continue
                row.append(edge_id[tuple(sorted((center, other)))])
            stars.append(tuple(sorted(row)))

    primary_vertices = [vertex_id[t] for t in ((0,1,2),(3,4,5),(6,7,8),(9,10,11))]
    secondary_vertices = [vertex_id[t] for t in ((0,3,6),(1,4,9),(2,7,10),(5,8,11))]
    edge_pairs = ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
    primary_edges = [edge_id[tuple(sorted((primary_vertices[i],primary_vertices[j])))] for i,j in edge_pairs]
    secondary_edges = [edge_id[tuple(sorted((secondary_vertices[i],secondary_vertices[j])))] for i,j in edge_pairs]
    assert (len(vertices),len(edges),len(triangles),len(four_blocks),len(stars)) == (220,9240,61600,15400,61600)
    return vertices,edges,triangles,stars,primary_edges,secondary_edges


def primary_pattern(branch: str) -> tuple[int, ...]:
    # AB,AC,AD,BC,BD,CD.
    if branch == "matching":
        return (1,0,0,0,0,1)
    if branch == "path":
        return (1,0,0,0,1,1)
    raise ValueError(branch)


def generate(branch: str, cube: int, cnf: Path, metadata: Path) -> None:
    patterns = allowed_k4_patterns()
    if not 0 <= cube < len(patterns):
        raise ValueError(cube)
    vertices,edges,triangles,stars,primary_edges,secondary_edges = build()
    p1=primary_pattern(branch)
    p2=patterns[cube]
    units=[]
    for variable,value in zip(primary_edges,p1):
        units.append(variable if value else -variable)
    for variable,value in zip(secondary_edges,p2):
        units.append(variable if value else -variable)
    clause_count=2*(len(triangles)+len(stars))+len(units)
    with cnf.open('w',encoding='ascii',newline='\n') as out:
        out.write(f'c Exact KG(12,3) branch={branch} secondary_cube={cube}\n')
        out.write(f'p cnf {len(edges)} {clause_count}\n')
        for family in (triangles,stars):
            for x,y,z in family:
                out.write(f'{x} {y} {z} 0\n')
                out.write(f'-{x} -{y} -{z} 0\n')
        for literal in units:
            out.write(f'{literal} 0\n')
    record={
        'scope':'exact exhaustive cube inside one of two primary K4 branches',
        'primary_branch':branch,
        'secondary_cube_index':cube,
        'secondary_pattern_ab_ac_ad_bc_bd_cd':list(p2),
        'all_secondary_patterns':len(patterns),
        'secondary_pattern_list_sha256':stable_hash(patterns),
        'primary_edge_variables':primary_edges,
        'secondary_edge_variables':secondary_edges,
        'unit_literals':units,
        'edge_variables':len(edges),
        'triangle_constraints':len(triangles),
        'redundant_star_constraints':len(stars),
        'cnf_clauses':clause_count,
        'cnf_sha256':file_hash(cnf),
        'coverage_statement':'The 18 cubes exhaust every nonmonochromatic coloring of the secondary K4.',
        'parent_UNSAT_rule':'Checked UNSAT for all cube indices 0..17 proves the primary branch UNSAT.',
        'global_exact_rule':'Checked UNSAT for all matching and path cubes proves R_3^KG(3,3)=12.',
    }
    metadata.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2,sort_keys=True))


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--branch',choices=('matching','path'),required=True)
    parser.add_argument('--cube',type=int,required=True)
    parser.add_argument('--cnf',type=Path,required=True)
    parser.add_argument('--metadata',type=Path,required=True)
    args=parser.parse_args()
    generate(args.branch,args.cube,args.cnf,args.metadata)


if __name__=='__main__':
    main()
