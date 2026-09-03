#!/usr/bin/env python3
"""Reproduce proof certificates for eliminated KG(12,3) canonical cubes.

This script is deliberately independent of the long-running exploratory search.
For each named cube it:

1. rebuilds the exact triangle-free edge-coloring CNF;
2. checks UNSAT with CaDiCaL 1.9.5, Glucose 4.2, and MiniSat 2.2;
3. asks CaDiCaL for a DRAT proof;
4. checks that proof with an external DRAT-trim executable;
5. records content hashes and solver statistics.

The default list is the thirteen cubes independently eliminated on
3 September 2026.  The large DRAT files are regenerated rather than committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

import pysat
from pysat.solvers import Cadical195, Glucose42, Minisat22

from kneser_r3_barrier_cubes import build_cube as build_barrier_cube
from kneser_r3_point_cubes import build_cube as build_point_cube


CERTIFIED_CUBES = (
    "P-barrier-a2-blue",
    "P-barrier-a3",
    "P-point-blue-Q",
    "B-barrier-a0-b0",
    "B-barrier-a1-b0-blue",
    "B-barrier-a1-b0-red",
    "B-barrier-a2-b0-blue",
    "B-barrier-a2-b0-red",
    "B-barrier-a2-b1-blue",
    "B-barrier-a2-b1-red",
    "B-barrier-a3-b0",
    "B-barrier-a3-b1",
    "B-point-blue-T",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_named_cube(name: str):
    if name.startswith("P-"):
        instance, spec = build_point_cube(name[2:])
        branch = "point"
    elif name.startswith("B-"):
        instance, spec = build_barrier_cube(name[2:])
        branch = "barrier"
    else:
        raise ValueError(f"cube name must start with P- or B-: {name}")
    return instance, spec, branch


def cube_clauses(instance) -> list[list[int]]:
    clauses: list[list[int]] = []
    for x, y, z in instance.triangles:
        clauses.append([x, y, z])
        clauses.append([-x, -y, -z])
    clauses.extend([[literal] for literal in instance.seed_units])
    return clauses


def write_dimacs(path: Path, variable_count: int, clauses: Iterable[Iterable[int]]) -> None:
    clause_list = [tuple(clause) for clause in clauses]
    with path.open("w") as handle:
        handle.write(f"p cnf {variable_count} {len(clause_list)}\n")
        for clause in clause_list:
            handle.write(" ".join(map(str, clause)) + " 0\n")


def solve_once(solver_type, clauses, *, proof: bool = False):
    options = {"bootstrap_with": clauses}
    if proof:
        options["with_proof"] = True
    started = time.monotonic()
    with solver_type(**options) as solver:
        satisfiable = bool(solver.solve())
        elapsed = time.monotonic() - started
        statistics = solver.accum_stats()
        proof_lines = solver.get_proof() if proof and not satisfiable else None
    return satisfiable, elapsed, statistics, proof_lines


def certify_cube(
    name: str,
    out_dir: Path,
    drat_trim: Path,
) -> dict[str, object]:
    instance, spec, first_level_branch = build_named_cube(name)
    clauses = cube_clauses(instance)
    slug = name.lower()
    cnf_path = out_dir / f"{slug}.cnf"
    proof_path = out_dir / f"{slug}.drat"
    checker_log_path = out_dir / f"{slug}.drat-trim.log"
    write_dimacs(cnf_path, len(instance.edges), clauses)

    solver_results: dict[str, bool] = {}
    solver_seconds: dict[str, float] = {}
    solver_statistics: dict[str, object] = {}

    sat, elapsed, stats, proof_lines = solve_once(
        Cadical195,
        clauses,
        proof=True,
    )
    solver_results["cadical195"] = sat
    solver_seconds["cadical195"] = elapsed
    solver_statistics["cadical195"] = stats
    if sat or proof_lines is None:
        raise RuntimeError(f"{name}: CaDiCaL did not prove UNSAT")
    proof_path.write_text("\n".join(proof_lines) + "\n")

    for label, solver_type in (
        ("glucose42", Glucose42),
        ("minisat22", Minisat22),
    ):
        sat, elapsed, stats, _ = solve_once(solver_type, clauses)
        solver_results[label] = sat
        solver_seconds[label] = elapsed
        solver_statistics[label] = stats
        if sat:
            raise RuntimeError(f"{name}: {label} found a satisfying assignment")

    checker_started = time.monotonic()
    completed = subprocess.run(
        [str(drat_trim), str(cnf_path), str(proof_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    checker_seconds = time.monotonic() - checker_started
    checker_log_path.write_text(completed.stdout)
    verified = completed.returncode == 0 and "VERIFIED" in completed.stdout
    if not verified:
        raise RuntimeError(
            f"{name}: DRAT-trim rejected the certificate "
            f"(exit={completed.returncode})"
        )

    return {
        "cube": name,
        "first_level_branch": first_level_branch,
        "cube_specification": spec.__dict__,
        "variables": len(instance.edges),
        "clauses": len(clauses),
        "fixed_units": len(instance.seed_units),
        "solver_satisfiable": solver_results,
        "solver_seconds": solver_seconds,
        "solver_statistics": solver_statistics,
        "drat_verified": True,
        "drat_trim_seconds": checker_seconds,
        "cnf_bytes": cnf_path.stat().st_size,
        "proof_bytes": proof_path.stat().st_size,
        "cnf_sha256": sha256_file(cnf_path),
        "proof_sha256": sha256_file(proof_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument(
        "--cubes",
        nargs="*",
        default=list(CERTIFIED_CUBES),
    )
    parser.add_argument("--drat-trim-commit")
    args = parser.parse_args()

    if not args.drat_trim.is_file():
        raise SystemExit(f"DRAT-trim executable not found: {args.drat_trim}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for cube in args.cubes:
        result = certify_cube(cube, args.out_dir, args.drat_trim)
        results.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)

    summary = {
        "claim_boundary": (
            "These certificates eliminate thirteen of the twenty-three "
            "complete second-level canonical cubes. They do not decide the "
            "ten remaining cubes."
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "python_sat": pysat.__version__,
        "drat_trim_commit": args.drat_trim_commit,
        "all_cubes_unsatisfiable": True,
        "all_drat_proofs_verified": True,
        "results": results,
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
