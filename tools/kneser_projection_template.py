#!/usr/bin/env python3
"""Search projection-only good colorings of KG(4r-1,r).

Split the ground set into P of size 2r and Q of size 2r-1.  An r-set A is
represented, for coloring purposes, only by X=A∩Q.  A color assigned to each
admissible disjoint pair (X,Y) pulls back to every Kneser edge AB with
A∩Q=X and B∩Q=Y.

Three projected labels X,Y,Z can occur on a Kneser triangle exactly when
  * they are pairwise disjoint (nonempty labels cannot repeat), and
  * |X|+|Y|+|Z| >= r.
The latter condition says that their three P-parts fit disjointly inside P.
Thus the projected construction is an exact finite NAE-SAT problem on Q.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195


def popcount(x: int) -> int:
    return x.bit_count()


def pair_key(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x <= y else (y, x)


def masks_upto(q: int, r: int) -> list[int]:
    return [m for m in range(1 << q) if popcount(m) <= r]


def admissible_pairs(labels: list[int]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for i, x in enumerate(labels):
        for y in labels[i:]:
            if x & y:
                continue
            if x == y and x != 0:
                continue
            pairs.append((x, y))
    return pairs


def projected_triangles(q: int, r: int) -> list[tuple[int, int, int]]:
    """Enumerate unordered feasible triples of pairwise disjoint labels.

    Each point of Q is assigned to unused/X/Y/Z.  Sorting the three masks
    quotients by permutation of the triangle vertices.  Q has size 2r-1, so
    this costs 4^(2r-1), which is practical for the exploratory range.
    """
    triples: set[tuple[int, int, int]] = set()
    states = 4 ** q
    for code0 in range(states):
        code = code0
        masks = [0, 0, 0]
        sizes = [0, 0, 0]
        valid = True
        for bit in range(q):
            bucket = code & 3
            code >>= 2
            if bucket:
                idx = bucket - 1
                sizes[idx] += 1
                if sizes[idx] > r:
                    valid = False
                    break
                masks[idx] |= 1 << bit
        if not valid or sum(sizes) < r:
            continue
        triple = tuple(sorted(masks))
        # Repeated nonempty masks cannot arise from the labeled partition,
        # while repeated zero labels are legitimate distinct Kneser vertices.
        triples.add(triple)
    return sorted(triples)


def mask_elements(mask: int, q: int) -> list[int]:
    return [i for i in range(q) if (mask >> i) & 1]


def solve(r: int, out: Path, include_model: bool) -> dict:
    q = 2 * r - 1
    labels = masks_upto(q, r)
    pairs = admissible_pairs(labels)
    var = {p: i + 1 for i, p in enumerate(pairs)}

    generation_started = time.time()
    triangles = projected_triangles(q, r)
    generation_seconds = time.time() - generation_started

    clauses: list[list[int]] = []
    for x, y, z in triangles:
        a = var[pair_key(x, y)]
        b = var[pair_key(x, z)]
        c = var[pair_key(y, z)]
        clauses.append([a, b, c])
        clauses.append([-a, -b, -c])
    if pairs:
        clauses.append([1])  # quotient by global color swap

    solve_started = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    solve_seconds = time.time() - solve_started

    result: dict = {
        "r": r,
        "ground_size": 4 * r - 1,
        "projection_size": q,
        "projected_labels": len(labels),
        "edge_variables": len(pairs),
        "projected_triangle_constraints": len(triangles),
        "clauses": len(clauses),
        "generation_seconds": generation_seconds,
        "solve_seconds": solve_seconds,
        "satisfiable": bool(sat),
    }

    if sat and model is not None:
        assignment = {
            abs(lit): lit > 0 for lit in model if abs(lit) <= len(pairs)
        }
        for x, y, z in triangles:
            colors = (
                assignment[var[pair_key(x, y)]],
                assignment[var[pair_key(x, z)]],
                assignment[var[pair_key(y, z)]],
            )
            assert not (colors[0] == colors[1] == colors[2])
        result["validated_all_projected_triangles"] = True
        red = [p for p, v in var.items() if assignment[v]]
        result["red_edge_variables"] = len(red)
        if include_model:
            result["red_projected_pairs"] = [
                [mask_elements(x, q), mask_elements(y, q)] for x, y in red
            ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "red_projected_pairs"},
            indent=2,
            sort_keys=True,
        )
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-model", action="store_true")
    args = parser.parse_args()
    solve(args.r, args.out, args.include_model)
