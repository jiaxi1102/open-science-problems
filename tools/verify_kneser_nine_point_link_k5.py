#!/usr/bin/env python3
"""Verify the sharp nine-point link theorem used in the KG(12,3) program.

The theorem is finite and exact:

    Every red/blue coloring of the triples of a nine-point set with no
    monochromatic perfect matching contains a monochromatic complete
    3-uniform hypergraph on five vertices.

Equivalently, if both color classes have matching number at most two, then one
class has transversal number at most four.

The script constructs a deterministic unit-propagation DPLL refutation of the
negation, independently checks every node of the resulting proof DAG, and
separately checks a Fano-star construction showing that five is the largest
guaranteed monochromatic clique order.  No SAT solver or third-party package
is used.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


Triple = tuple[int, int, int]
Clause = tuple[int, ...]

EXPECTED_CNF_SHA256 = "0db7c378b5fdf09326e5190ad6697e64b2a508ce39075864bcb3cd4918b84314"
EXPECTED_RAW_CERTIFICATE_SHA256 = "30a35dcd239712ee87e4f65ddb5ab71a0965facf63d5595fd237ad95e9c6223d"
EXPECTED_NODES = 9536
EXPECTED_RECURSIVE_CALLS = 19073


def triples_on_nine() -> tuple[Triple, ...]:
    return tuple(itertools.combinations(range(9), 3))


def partitions_into_triples() -> tuple[tuple[Triple, Triple, Triple], ...]:
    points = tuple(range(9))
    out: set[tuple[Triple, Triple, Triple]] = set()
    for first in itertools.combinations(points, 3):
        remaining = tuple(point for point in points if point not in first)
        for second in itertools.combinations(remaining, 3):
            third = tuple(point for point in remaining if point not in second)
            out.add(tuple(sorted((tuple(first), tuple(second), tuple(third)))))
    result = tuple(sorted(out))
    assert len(result) == 280
    return result


def theorem_cnf() -> tuple[tuple[Clause, ...], tuple[Triple, ...]]:
    """CNF for: no monochromatic perfect matching and no monochromatic K5."""
    triples = triples_on_nine()
    variable = {triple: index + 1 for index, triple in enumerate(triples)}
    clauses: list[Clause] = []

    for partition in partitions_into_triples():
        variables = tuple(variable[block] for block in partition)
        clauses.append(variables)
        clauses.append(tuple(-x for x in variables))

    # Iterate by the complementary four-set to pin the certificate order.
    for cover in itertools.combinations(range(9), 4):
        five_set = tuple(point for point in range(9) if point not in cover)
        variables = tuple(
            variable[triple] for triple in itertools.combinations(five_set, 3)
        )
        assert len(variables) == 10
        clauses.append(variables)
        clauses.append(tuple(-x for x in variables))

    # Remove global red/blue swap symmetry.
    clauses.append((1,))

    result = tuple(clauses)
    assert len(result) == 813
    assert Counter(map(len, result)) == Counter({3: 560, 10: 252, 1: 1})
    digest = hashlib.sha256(
        json.dumps(result, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == EXPECTED_CNF_SHA256
    return result, triples


def clause_masks(clauses: Sequence[Clause]) -> tuple[tuple[int, int], ...]:
    masks = []
    for clause in clauses:
        positive = 0
        negative = 0
        for literal in clause:
            bit = 1 << (abs(literal) - 1)
            if literal > 0:
                positive |= bit
            else:
                negative |= bit
        assert positive & negative == 0
        masks.append((positive, negative))
    return tuple(masks)


def propagate(
    positive_assignment: int,
    negative_assignment: int,
    masks: Sequence[tuple[int, int]],
) -> tuple[tuple[int, int] | None, int | None]:
    """Deterministic unit propagation, returning the first conflict index."""
    assert positive_assignment & negative_assignment == 0
    while True:
        changed = False
        assigned = positive_assignment | negative_assignment
        for index, (positive, negative) in enumerate(masks):
            if positive & positive_assignment or negative & negative_assignment:
                continue
            unassigned_positive = positive & ~assigned
            unassigned_negative = negative & ~assigned
            unassigned = unassigned_positive | unassigned_negative
            if not unassigned:
                return None, index
            if unassigned & (unassigned - 1) == 0:
                bit = unassigned
                if unassigned_positive:
                    assert not bit & negative_assignment
                    if not bit & positive_assignment:
                        positive_assignment |= bit
                        changed = True
                else:
                    assert not bit & positive_assignment
                    if not bit & negative_assignment:
                        negative_assignment |= bit
                        changed = True
        if not changed:
            return (positive_assignment, negative_assignment), None


def choose_branch_variable(
    positive_assignment: int,
    negative_assignment: int,
    masks: Sequence[tuple[int, int]],
    variable_count: int,
) -> int:
    """Branch in the shortest unresolved clauses, then by frequency."""
    assigned = positive_assignment | negative_assignment
    minimum_length = variable_count + 1
    scores = [0] * variable_count
    for positive, negative in masks:
        if positive & positive_assignment or negative & negative_assignment:
            continue
        unassigned = (positive | negative) & ~assigned
        length = unassigned.bit_count()
        if length < minimum_length:
            minimum_length = length
            scores = [0] * variable_count
        if length == minimum_length:
            remaining = unassigned
            while remaining:
                bit = remaining & -remaining
                scores[bit.bit_length() - 1] += 1
                remaining -= bit
    # Tuple ordering pins ties in favor of the larger variable index.
    return max((score, index) for index, score in enumerate(scores))[1]


def generate_certificate(
    clauses: Sequence[Clause],
) -> tuple[dict[str, object], bytes, bytes]:
    """Construct a deterministic DPLL proof DAG."""
    masks = clause_masks(clauses)
    variable_count = 84
    full_mask = (1 << variable_count) - 1
    nodes: list[list[object] | None] = []
    state_to_id: dict[tuple[int, int], int] = {}
    recursive_calls = 0

    def prove(positive_assignment: int = 0, negative_assignment: int = 0) -> int:
        nonlocal recursive_calls
        recursive_calls += 1
        closure, conflict = propagate(
            positive_assignment, negative_assignment, masks
        )
        if closure is None:
            assert conflict is not None
            return -1 - conflict

        positive, negative = closure
        key = (positive, negative)
        if key in state_to_id:
            return state_to_id[key]
        if positive | negative == full_mask:
            raise AssertionError("the CNF is satisfiable")

        variable_index = choose_branch_variable(
            positive, negative, masks, variable_count
        )
        bit = 1 << variable_index
        node_id = len(nodes)
        state_to_id[key] = node_id
        nodes.append(None)

        zero_child = prove(positive, negative | bit)
        one_child = prove(positive | bit, negative)
        nodes[node_id] = [
            format(positive, "x"),
            format(negative, "x"),
            variable_index + 1,
            zero_child,
            one_child,
        ]
        return node_id

    root = prove()
    assert root == 0
    assert recursive_calls == EXPECTED_RECURSIVE_CALLS
    assert len(nodes) == EXPECTED_NODES
    assert all(node is not None for node in nodes)

    certificate: dict[str, object] = {
        "format": "unit-propagation-dpll-dag-v1",
        "theorem": (
            "Every two-coloring of C([9],3) with no monochromatic perfect "
            "matching has a monochromatic K5^(3)."
        ),
        "variables": variable_count,
        "clauses": len(clauses),
        "root": root,
        "nodes": nodes,
    }
    raw = json.dumps(
        certificate, separators=(",", ":"), sort_keys=True
    ).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_RAW_CERTIFICATE_SHA256
    return certificate, raw, compressed


def write_encoded_certificate(compressed: bytes, path: Path) -> None:
    encoded = base64.b64encode(compressed).decode()
    wrapped = "\n".join(
        encoded[index:index + 96] for index in range(0, len(encoded), 96)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(wrapped + "\n")


def load_certificate(path: Path) -> dict[str, object]:
    encoded = "".join(path.read_text().split())
    compressed = base64.b64decode(encoded, validate=True)
    raw = gzip.decompress(compressed)
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_RAW_CERTIFICATE_SHA256
    certificate = json.loads(raw)
    assert certificate["format"] == "unit-propagation-dpll-dag-v1"
    assert certificate["variables"] == 84
    assert certificate["clauses"] == 813
    assert certificate["root"] == 0
    assert len(certificate["nodes"]) == EXPECTED_NODES
    return certificate


def verify_refutation(
    certificate: dict[str, object],
    masks: Sequence[tuple[int, int]],
) -> dict[str, int | bool]:
    nodes = certificate["nodes"]
    assert isinstance(nodes, list)
    status = [0] * len(nodes)
    recursive_references = 0
    conflict_leaves = 0

    def check_reference(reference: int, pre_positive: int, pre_negative: int) -> None:
        nonlocal recursive_references, conflict_leaves
        recursive_references += 1
        closure, conflict = propagate(pre_positive, pre_negative, masks)

        if reference < 0:
            conflict_leaves += 1
            expected_conflict = -reference - 1
            assert closure is None
            assert conflict == expected_conflict
            return

        assert closure is not None and conflict is None
        assert 0 <= reference < len(nodes)
        positive, negative = closure
        node = nodes[reference]
        assert isinstance(node, list) and len(node) == 5
        stored_positive = int(node[0], 16)
        stored_negative = int(node[1], 16)
        branch_variable = int(node[2])
        zero_child = int(node[3])
        one_child = int(node[4])

        assert (positive, negative) == (stored_positive, stored_negative)
        assert 1 <= branch_variable <= 84
        bit = 1 << (branch_variable - 1)
        assert not bit & (positive | negative)

        if status[reference] == 2:
            return
        assert status[reference] == 0, "cycle in proof DAG"
        status[reference] = 1
        check_reference(zero_child, positive, negative | bit)
        check_reference(one_child, positive | bit, negative)
        status[reference] = 2

    check_reference(int(certificate["root"]), 0, 0)
    assert all(value == 2 for value in status)
    assert recursive_references == EXPECTED_RECURSIVE_CALLS
    assert conflict_leaves == (EXPECTED_RECURSIVE_CALLS + 1) // 2
    return {
        "proof_nodes_checked": len(nodes),
        "recursive_references_checked": recursive_references,
        "conflict_leaves_checked": conflict_leaves,
        "all_nodes_reachable": True,
        "refutation_valid": True,
    }


def minimum_transversal(family: Iterable[Triple]) -> tuple[int, tuple[int, ...]]:
    edges = tuple(family)
    for size in range(10):
        for cover in itertools.combinations(range(9), size):
            chosen = set(cover)
            if all(chosen.intersection(edge) for edge in edges):
                return size, tuple(cover)
    raise AssertionError("the whole point set is a transversal")


def monochromatic_sets(
    red: set[Triple], size: int
) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    all_triples = set(triples_on_nine())
    blue = all_triples - red
    red_sets = []
    blue_sets = []
    for subset in itertools.combinations(range(9), size):
        induced = set(itertools.combinations(subset, 3))
        if induced <= red:
            red_sets.append(subset)
        if induced <= blue:
            blue_sets.append(subset)
    return red_sets, blue_sets


def verify_fano_star_sharpness() -> dict[str, object]:
    # Fano plane on 0,...,6; point 7 ordinary; point 8 the star center.
    fano_lines: set[Triple] = {
        (0, 1, 2),
        (0, 3, 4),
        (0, 5, 6),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 4, 5),
    }
    assert all(
        len(set(a).intersection(b)) == 1
        for a, b in itertools.combinations(fano_lines, 2)
    )

    triples = set(triples_on_nine())
    red = {triple for triple in triples if 8 in triple or triple in fano_lines}
    blue = triples - red
    assert (len(red), len(blue)) == (35, 49)

    mono_matchings = []
    for partition in partitions_into_triples():
        colors = tuple(block in red for block in partition)
        if colors[0] == colors[1] == colors[2]:
            mono_matchings.append(partition)
    assert not mono_matchings

    red_tau, red_cover = minimum_transversal(red)
    blue_tau, blue_cover = minimum_transversal(blue)
    assert red_tau == 4
    assert blue_tau == 5

    red_fives, blue_fives = monochromatic_sets(red, 5)
    red_sixes, blue_sixes = monochromatic_sets(red, 6)
    assert not red_fives
    assert len(blue_fives) == 7
    assert not red_sixes and not blue_sixes

    family_word = ";".join(
        ",".join(map(str, triple)) for triple in sorted(red)
    )
    return {
        "construction": "star at point 8 plus the seven Fano lines on points 0..6",
        "red_triples": len(red),
        "blue_triples": len(blue),
        "monochromatic_perfect_matchings": 0,
        "red_transversal_number": red_tau,
        "red_minimum_transversal": list(red_cover),
        "blue_transversal_number": blue_tau,
        "blue_minimum_transversal": list(blue_cover),
        "monochromatic_red_K5": len(red_fives),
        "monochromatic_blue_K5": len(blue_fives),
        "monochromatic_K6": 0,
        "red_family_sha256": hashlib.sha256(family_word.encode()).hexdigest(),
        "sharpness_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate",
        type=Path,
        help="verify an existing base64-gzip proof DAG instead of regenerating it",
    )
    parser.add_argument(
        "--write-certificate",
        type=Path,
        help="write the deterministic base64-gzip proof DAG after generation",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    clauses, triples = theorem_cnf()
    if args.certificate is None:
        certificate, raw_certificate, compressed_certificate = generate_certificate(clauses)
        if args.write_certificate is not None:
            write_encoded_certificate(compressed_certificate, args.write_certificate)
    else:
        certificate = load_certificate(args.certificate)
        raw_certificate = json.dumps(
            certificate, separators=(",", ":"), sort_keys=True
        ).encode()
        compressed_certificate = gzip.compress(
            raw_certificate, compresslevel=9, mtime=0
        )

    proof_result = verify_refutation(certificate, clause_masks(clauses))
    proof_result["raw_certificate_bytes"] = len(raw_certificate)
    proof_result["gzip_certificate_bytes"] = len(compressed_certificate)
    proof_result["raw_certificate_sha256"] = hashlib.sha256(raw_certificate).hexdigest()
    proof_result["gzip_certificate_sha256"] = hashlib.sha256(compressed_certificate).hexdigest()
    sharpness = verify_fano_star_sharpness()

    result = {
        "theorem": (
            "Every red/blue coloring of C([9],3) with no monochromatic "
            "perfect matching contains a monochromatic K5^(3)."
        ),
        "equivalent_transversal_statement": (
            "For complementary 3-graphs on nine vertices, if both matching "
            "numbers are at most two, then one transversal number is at most four."
        ),
        "variables": len(triples),
        "perfect_matching_constraints": 280,
        "five_set_constraints": 126,
        "cnf_clauses": len(clauses),
        "cnf_sha256": EXPECTED_CNF_SHA256,
        "certificate": proof_result,
        "sharpness": sharpness,
        "largest_guaranteed_monochromatic_complete_3_graph_order": 5,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)


if __name__ == "__main__":
    main()
