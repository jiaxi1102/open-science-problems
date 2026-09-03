#!/usr/bin/env python3
"""Classify 2-colorings of the triples of [9] with no monochromatic 3-matching.

These are exactly the possible one-color incidence neighborhoods at a vertex
of a hypothetical monochromatic-triangle-free coloring of KG(12,3).

The script performs an independent exhaustive DPLL enumeration with only the
NAE propagation rule. It then compares every model against the explicit
threshold family

    color(T) = [|T intersect S| >= ceil(|S|/3)]

and its complement, for |S| in {1,2,4}.  The expected classification has
342 colorings, or 171 after fixing one triple blue by global color symmetry.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

N = 9
K = 3

Trip = tuple[int, int, int]


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def build_hypergraph():
    triples: list[Trip] = list(itertools.combinations(range(N), K))
    triple_id = {triple: i for i, triple in enumerate(triples)}
    partitions: set[tuple[int, int, int]] = set()
    for a in triples:
        remaining_a = tuple(x for x in range(N) if x not in a)
        for b in itertools.combinations(remaining_a, K):
            remaining_ab = tuple(x for x in remaining_a if x not in b)
            c = tuple(remaining_ab)
            parts = tuple(sorted((triple_id[a], triple_id[b], triple_id[c])))
            partitions.add(parts)
    partitions_sorted = sorted(partitions)
    assert len(triples) == 84
    assert len(partitions_sorted) == 280
    return triples, partitions_sorted


def explicit_threshold_models(triples: list[Trip]) -> dict[int, dict]:
    models: dict[int, dict] = {}
    for size in (1, 2, 4):
        threshold = (size + 2) // 3
        for subset in itertools.combinations(range(N), size):
            subset_set = set(subset)
            bits = 0
            for i, triple in enumerate(triples):
                if len(subset_set.intersection(triple)) >= threshold:
                    bits |= 1 << i
            for complemented in (False, True):
                model = bits if not complemented else bits ^ ((1 << len(triples)) - 1)
                descriptor = {
                    "subset": list(subset),
                    "subset_size": size,
                    "threshold": threshold,
                    "complemented": complemented,
                }
                if model in models and models[model] != descriptor:
                    raise AssertionError((model, models[model], descriptor))
                models[model] = descriptor
    assert len(models) == 342
    return models


class Enumerator:
    def __init__(self, variables: int, constraints: list[tuple[int, int, int]]):
        self.n = variables
        self.constraints = constraints
        self.by_var: list[list[int]] = [[] for _ in range(variables)]
        for ci, row in enumerate(constraints):
            for variable in row:
                self.by_var[variable].append(ci)
        self.assignment = [-1] * variables
        self.trail: list[int] = []
        self.models: list[int] = []
        self.nodes = 0
        self.propagations = 0

    def assign(self, variable: int, value: int) -> bool:
        current = self.assignment[variable]
        if current != -1:
            return current == value
        self.assignment[variable] = value
        self.trail.append(variable)
        return True

    def propagate(self) -> bool:
        queue = list(self.trail)
        seen = 0
        while seen < len(queue):
            variable = queue[seen]
            seen += 1
            for ci in self.by_var[variable]:
                row = self.constraints[ci]
                values = [self.assignment[x] for x in row]
                assigned = [(x, v) for x, v in zip(row, values) if v != -1]
                if len(assigned) == 3:
                    if values[0] == values[1] == values[2]:
                        return False
                elif len(assigned) == 2 and assigned[0][1] == assigned[1][1]:
                    missing = next(x for x in row if self.assignment[x] == -1)
                    if not self.assign(missing, 1 - assigned[0][1]):
                        return False
                    queue.append(missing)
                    self.propagations += 1
        return True

    def choose_variable(self) -> int | None:
        best = None
        best_score = -1
        for variable, value in enumerate(self.assignment):
            if value != -1:
                continue
            score = 0
            for ci in self.by_var[variable]:
                values = [self.assignment[x] for x in self.constraints[ci]]
                assigned_values = [v for v in values if v != -1]
                if len(assigned_values) == 2 and assigned_values[0] != assigned_values[1]:
                    continue
                score += 1 + 4 * len(assigned_values)
            if score > best_score:
                best = variable
                best_score = score
        return best

    def rollback(self, mark: int) -> None:
        while len(self.trail) > mark:
            variable = self.trail.pop()
            self.assignment[variable] = -1

    def search(self) -> None:
        self.nodes += 1
        mark = len(self.trail)
        if not self.propagate():
            self.rollback(mark)
            return
        variable = self.choose_variable()
        if variable is None:
            bits = sum(value << i for i, value in enumerate(self.assignment))
            self.models.append(bits)
            self.rollback(mark)
            return
        propagated_mark = len(self.trail)
        for value in (0, 1):
            if self.assign(variable, value):
                self.search()
            self.rollback(propagated_mark)
        self.rollback(mark)


def verify_model(model: int, constraints: list[tuple[int, int, int]]) -> None:
    for a, b, c in constraints:
        values = ((model >> a) & 1, (model >> b) & 1, (model >> c) & 1)
        if values[0] == values[1] == values[2]:
            raise AssertionError((a, b, c, values))


def main() -> None:
    triples, partitions = build_hypergraph()
    explicit = explicit_threshold_models(triples)

    enumerator = Enumerator(len(triples), partitions)
    # The first triple is fixed blue; complements recover the other half.
    assert enumerator.assign(0, 0)
    enumerator.search()

    models = sorted(set(enumerator.models))
    assert len(models) == len(enumerator.models)
    assert len(models) == 171, len(models)
    for model in models:
        verify_model(model, partitions)
        if model not in explicit:
            raise AssertionError(f"non-threshold model: {model:x}")
    normalized_explicit = sorted(model for model in explicit if (model & 1) == 0)
    assert models == normalized_explicit

    degree_counts = Counter(model.bit_count() for model in explicit)
    descriptor_counts = Counter(
        (d["subset_size"], d["complemented"])
        for d in explicit.values()
    )
    model_hex = [model.to_bytes(11, "little").hex() for model in models]
    result = {
        "theorem": (
            "Every red/blue coloring of the 3-subsets of [9] with no "
            "monochromatic partition into three triples is a threshold "
            "coloring from a subset of size 1, 2, or 4, or its complement."
        ),
        "triples": len(triples),
        "perfect_matching_constraints": len(partitions),
        "normalized_models_enumerated": len(models),
        "all_models_including_color_complements": 2 * len(models),
        "explicit_threshold_models": len(explicit),
        "search_nodes": enumerator.nodes,
        "unit_propagations": enumerator.propagations,
        "model_red_degree_distribution": dict(sorted(degree_counts.items())),
        "descriptor_counts": {
            f"size_{size}_complemented_{complemented}": count
            for (size, complemented), count in sorted(descriptor_counts.items())
        },
        "triple_order_sha256": stable_hash(triples),
        "partition_order_sha256": stable_hash(partitions),
        "normalized_model_list_sha256": stable_hash(model_hex),
    }
    out = Path(__file__).resolve().parents[1] / "problems" / \
        "math-0003-kneser-ramsey-lower-bound" / "experiments" / \
        "kg12-r3" / "local-neighborhood-classification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
