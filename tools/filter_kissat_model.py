#!/usr/bin/env python3
"""Project a complete Kissat model onto variables 1..limit.

This is used when an exact SAT encoding introduces Tseitin auxiliaries but the
independent mathematical checker consumes only the original edge variables.
The projection rejects missing, contradictory, or out-of-range assignments in
the retained prefix and emits a standard complete SAT model for that prefix.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def project(source: Path, destination: Path, limit: int) -> None:
    status = None
    assignments: list[bool | None] = [None] * (limit + 1)
    for raw in source.read_text(errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for token in line[2:].split():
                literal = int(token)
                if literal == 0:
                    continue
                variable = abs(literal)
                if variable > limit:
                    continue
                value = literal > 0
                previous = assignments[variable]
                if previous is not None and previous != value:
                    raise ValueError(f"contradictory assignment for variable {variable}")
                assignments[variable] = value
    if status != "SATISFIABLE":
        raise ValueError(f"expected SATISFIABLE output, observed {status!r}")
    missing = [variable for variable in range(1, limit + 1) if assignments[variable] is None]
    if missing:
        raise ValueError(f"projected model is incomplete: {len(missing)} missing variables")

    with destination.open("w", encoding="ascii", newline="\n") as out:
        out.write("s SATISFIABLE\n")
        for start in range(1, limit + 1, 20):
            stop = min(limit + 1, start + 20)
            literals = [
                variable if assignments[variable] else -variable
                for variable in range(start, stop)
            ]
            out.write("v " + " ".join(map(str, literals)) + " 0\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--limit", type=int, required=True)
    args = parser.parse_args()
    if args.limit < 1:
        raise SystemExit("limit must be positive")
    project(args.source, args.destination, args.limit)


if __name__ == "__main__":
    main()
