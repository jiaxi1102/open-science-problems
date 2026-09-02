#!/usr/bin/env python3
"""Search for union-factor colorings of KG(4r,r).

The color of a Kneser edge AB depends only on the balanced cut
{A union B, (A union B)^c}.  For a partition of [4r] into four r-blocks,
the six Kneser edges occur in three opposite pairs with the same cut.
Thus every triangle is nonmonochromatic exactly when the three cut colors
of every four-block partition satisfy a not-all-equal constraint.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Cadical195


def bitmask(items):
    out = 0
    for x in items:
        out |= 1 << x
    return out


def canonical_cut(mask: int, full: int) -> int:
    comp = full ^ mask
    return min(mask, comp)


def set_partitions_equal_blocks(n: int, r: int):
    """Generate each unlabeled partition of [n] into equal r-blocks once."""
    full = tuple(range(n))

    def rec(remaining: tuple[int, ...], blocks_left: int):
        if blocks_left == 1:
            yield (remaining,)
            return
        first = remaining[0]
        tail = remaining[1:]
        for rest in itertools.combinations(tail, r - 1):
            block = (first,) + rest
            chosen = set(block)
            next_remaining = tuple(x for x in remaining if x not in chosen)
            for suffix in rec(next_remaining, blocks_left - 1):
                yield (block,) + suffix

    yield from rec(full, n // r)


def solve(r: int, out: Path):
    n = 4 * r
    full = (1 << n) - 1
    cuts = [
        mask
        for mask in range(1 << n)
        if mask.bit_count() == 2 * r and mask < (full ^ mask)
    ]
    cut_var = {mask: i + 1 for i, mask in enumerate(cuts)}

    clauses: list[list[int]] = []
    constraint_keys: set[tuple[int, int, int]] = set()
    partitions = 0
    for blocks in set_partitions_equal_blocks(n, r):
        partitions += 1
        b = [bitmask(x) for x in blocks]
        vars3 = tuple(
            sorted(
                (
                    cut_var[canonical_cut(b[0] | b[1], full)],
                    cut_var[canonical_cut(b[0] | b[2], full)],
                    cut_var[canonical_cut(b[0] | b[3], full)],
                )
            )
        )
        constraint_keys.add(vars3)

    for x, y, z in sorted(constraint_keys):
        clauses.append([x, y, z])
        clauses.append([-x, -y, -z])
    if cuts:
        clauses.append([1])

    started = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    elapsed = time.time() - started

    result = {
        "r": r,
        "n": n,
        "balanced_cut_variables": len(cuts),
        "four_block_partitions": partitions,
        "unique_nae_constraints": len(constraint_keys),
        "clauses": len(clauses),
        "satisfiable": bool(sat),
        "elapsed_seconds": elapsed,
    }
    if sat and model is not None:
        assignment = {
            abs(lit): lit > 0 for lit in model if abs(lit) <= len(cuts)
        }
        result["red_cut_representatives"] = [
            [i for i in range(n) if mask >> i & 1]
            for mask, var in cut_var.items()
            if assignment.get(var, False)
        ]
        # Independent validation of every partition constraint.
        for x, y, z in constraint_keys:
            vals = (assignment[x], assignment[y], assignment[z])
            assert not (vals[0] == vals[1] == vals[2])
        result["validated_all_partitions"] = True

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "red_cut_representatives"},
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.r, args.out)
