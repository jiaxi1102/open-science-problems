#!/usr/bin/env python3
"""Run a DIMACS instance with PySAT's Glucose42 and emit standard output."""
from __future__ import annotations

import argparse
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Glucose42


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    args = parser.parse_args()

    formula = CNF(from_file=str(args.cnf))
    with Glucose42(bootstrap_with=formula.clauses, use_timer=True) as solver:
        satisfiable = solver.solve()
        if not satisfiable:
            print("s UNSATISFIABLE")
            print(f"c cpu_time {solver.time():.6f}")
            raise SystemExit(20)

        model = solver.get_model()
        print("s SATISFIABLE")
        for start in range(0, len(model), 20):
            print("v", *model[start:start + 20], 0)
        print(f"c cpu_time {solver.time():.6f}")
        raise SystemExit(10)


if __name__ == "__main__":
    main()
