#!/usr/bin/env python3
"""Verify the uniform one-point-saturation construction.

For every r >= 3 the proof uses red- and blue-defect odd trace cycles through
the same base trace {0,1}. Anonymous fillers are supplied by an elementary
cyclic-interval construction. The program checks all symbolic conditions for
r=3,...,1000 and materializes the actual filler sets at representative ranks.
"""

from __future__ import annotations

import hashlib
import itertools
import json

from verify_kneser_five_point import trace_color


def mask(*points: int) -> int:
    value = 0
    for point in points:
        value |= 1 << point
    return value


BASE = mask(0, 1)
RED_BASE = (BASE, mask(2, 3, 4), mask(1), mask(0, 3, 4), mask(2))
RED_BLOCK = (mask(1), mask(2, 3, 4), mask(0), mask(2, 3), mask(0, 4), mask(2))
BLUE_BASE = (BASE, mask(3), mask(0, 1, 2), mask(4), mask(3))
BLUE_BLOCK = (mask(0), mask(4), mask(0, 1, 2), mask(3))


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def red_repetitions(r: int) -> int:
    return max(0, ceil_div(r - 6, 4))


def blue_repetitions(r: int) -> int:
    return max(0, ceil_div(r - 4, 2))


def red_cycle(r: int) -> tuple[int, ...]:
    return RED_BASE + RED_BLOCK * red_repetitions(r)


def blue_cycle(r: int) -> tuple[int, ...]:
    return BLUE_BASE + BLUE_BLOCK * blue_repetitions(r)


def cyclic_interval_plan(
    demands: tuple[int, ...],
    palette_size: int,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return bounded gaps and interval starts for an admissible odd cycle."""

    length = len(demands)
    assert length >= 3 and length % 2 == 1
    assert palette_size >= 1
    q = (length - 1) // 2
    assert all(0 <= demand <= palette_size for demand in demands)
    assert all(
        demands[index] + demands[(index + 1) % length] <= palette_size
        for index in range(length)
    )
    total_demand = sum(demands)
    assert total_demand <= q * palette_size

    capacities = tuple(
        palette_size - demands[index] - demands[(index + 1) % length]
        for index in range(length)
    )
    required_gap = q * palette_size - total_demand
    assert sum(capacities) >= required_gap

    remaining = required_gap
    gaps = []
    for capacity in capacities:
        gap = min(capacity, remaining)
        gaps.append(gap)
        remaining -= gap
    assert remaining == 0

    starts = [0]
    for index, demand in enumerate(demands):
        starts.append((starts[-1] + demand + gaps[index]) % palette_size)

    assert starts[-1] == starts[0]
    assert sum(demands) + sum(gaps) == q * palette_size
    assert all(
        demands[index] + gaps[index] + demands[(index + 1) % length]
        <= palette_size
        for index in range(length)
    )
    return tuple(gaps), tuple(starts[:-1])


def materialize_intervals(
    demands: tuple[int, ...],
    palette_size: int,
    starts: tuple[int, ...],
) -> tuple[frozenset[int], ...]:
    fillers = tuple(
        frozenset((start + offset) % palette_size for offset in range(demand))
        for start, demand in zip(starts, demands)
    )
    assert all(len(fillers[index]) == demands[index] for index in range(len(demands)))
    assert all(
        fillers[index].isdisjoint(fillers[(index + 1) % len(fillers)])
        for index in range(len(fillers))
    )
    return fillers


def forcing_contradiction(edge_colors: tuple[bool, ...], initial_color: bool) -> bool:
    current = initial_color
    for old_edge_color in edge_colors:
        assert current == old_edge_color
        current = not current
    return current != initial_color


def verify_trace_cycle(
    r: int,
    traces: tuple[int, ...],
    first_color: bool,
    materialize: bool,
) -> tuple[dict[str, object], frozenset[int] | None]:
    assert r >= 3
    assert traces[0] == BASE
    assert len(traces) % 2 == 1

    edge_colors = []
    adjacent_trace_sums = []
    for index, left in enumerate(traces):
        right = traces[(index + 1) % len(traces)]
        assert left & right == 0
        color = trace_color(left, right)
        assert color == (first_color if index % 2 == 0 else not first_color)
        edge_colors.append(color)
        adjacent_trace_sums.append(left.bit_count() + right.bit_count())

    trace_weight = sum(trace.bit_count() for trace in traces)
    demands = tuple(r - trace.bit_count() for trace in traces)
    palette_size = 2 * r - 2
    q = (len(traces) - 1) // 2
    total_demand = sum(demands)
    max_adjacent_demand = max(
        demands[index] + demands[(index + 1) % len(demands)]
        for index in range(len(demands))
    )

    assert min(demands) >= 0
    assert min(adjacent_trace_sums) >= 2
    assert max_adjacent_demand <= palette_size
    assert total_demand <= q * palette_size
    assert trace_weight >= len(traces) + r - 1

    gaps, starts = cyclic_interval_plan(demands, palette_size)
    base_filler = None
    filler_digest = None
    if materialize:
        fillers = materialize_intervals(demands, palette_size, starts)
        old_sets = tuple(
            frozenset(point for point in range(5) if trace & (1 << point))
            | frozenset(5 + point for point in filler)
            for trace, filler in zip(traces, fillers)
        )
        assert all(len(old_set) == r for old_set in old_sets)
        assert all(
            old_sets[index].isdisjoint(old_sets[(index + 1) % len(old_sets)])
            for index in range(len(old_sets))
        )
        base_filler = fillers[0]
        filler_word = "|".join(
            ",".join(map(str, sorted(filler))) for filler in fillers
        )
        filler_digest = hashlib.sha256(filler_word.encode()).hexdigest()

    assert forcing_contradiction(tuple(edge_colors), first_color)
    result = {
        "length": len(traces),
        "trace_weight": trace_weight,
        "first_and_last_edge_color": "red" if first_color else "blue",
        "edge_color_word_sha256": hashlib.sha256(
            "".join("R" if value else "B" for value in edge_colors).encode()
        ).hexdigest(),
        "anonymous_points": palette_size,
        "total_filler_demand": total_demand,
        "odd_cycle_capacity": q * palette_size,
        "max_adjacent_filler_demand": max_adjacent_demand,
        "adjacent_capacity": palette_size,
        "required_total_gap": q * palette_size - total_demand,
        "actual_total_gap": sum(gaps),
        "interval_plan_closes": True,
        "forcing_cycle_closes_with_opposite_color": True,
        "actual_fillers_materialized": materialize,
        "filler_assignment_sha256": filler_digest,
    }
    return result, base_filler


def verify_rank(r: int, materialize: bool) -> dict[str, object]:
    red_t = red_repetitions(r)
    blue_t = blue_repetitions(r)
    red = red_cycle(r)
    blue = blue_cycle(r)

    assert len(red) == 5 + 6 * red_t
    assert sum(trace.bit_count() for trace in red) == 10 + 10 * red_t
    assert 6 + 4 * red_t >= r
    assert len(blue) == 5 + 4 * blue_t
    assert sum(trace.bit_count() for trace in blue) == 8 + 6 * blue_t
    assert 4 + 2 * blue_t >= r

    red_result, red_base_filler = verify_trace_cycle(r, red, True, materialize)
    blue_result, blue_base_filler = verify_trace_cycle(r, blue, False, materialize)
    if materialize:
        assert red_base_filler == blue_base_filler
        assert red_base_filler == frozenset(range(r - 2))

    return {
        "r": r,
        "base_trace": [0, 1],
        "red_repetitions": red_t,
        "blue_repetitions": blue_t,
        "red_defect_cycle": red_result,
        "blue_defect_cycle": blue_result,
        "both_cycles_use_same_old_base_vertex": True,
        "both_colors_for_that_new_edge_are_impossible": True,
    }


def exhaustive_small_filler_lemma_check() -> dict[str, int | bool]:
    instances = 0
    for palette_size in range(1, 6):
        for length in (3, 5, 7):
            q = (length - 1) // 2
            for demands in itertools.product(range(palette_size + 1), repeat=length):
                if sum(demands) > q * palette_size:
                    continue
                if any(
                    demands[index] + demands[(index + 1) % length] > palette_size
                    for index in range(length)
                ):
                    continue
                _, starts = cyclic_interval_plan(tuple(demands), palette_size)
                materialize_intervals(tuple(demands), palette_size, starts)
                instances += 1
    return {
        "palette_sizes_checked_through": 5,
        "odd_lengths_checked_through": 7,
        "admissible_instances_checked": instances,
        "all_constructed": True,
    }


def main() -> None:
    materialized_ranks = {3, 4, 5, 6, 7, 8, 9, 10, 25, 100, 1000}
    sweep = [verify_rank(r, r in materialized_ranks) for r in range(3, 1001)]
    selected = {str(row["r"]): row for row in sweep if row["r"] in materialized_ranks}

    block_payload = {
        "red_base": list(RED_BASE),
        "red_block": list(RED_BLOCK),
        "blue_base": list(BLUE_BASE),
        "blue_block": list(BLUE_BLOCK),
    }
    result = {
        "candidate_theorem": (
            "For every r >= 3, the explicit five-point coloring of "
            "KG(3r+2,r) is one-point saturated."
        ),
        "filler_lemma": (
            "Admissible integer demands on an odd cycle are realized by "
            "explicit cyclic intervals; no external decomposition theorem is used."
        ),
        "symbolic_formulas": {
            "red_length": "5 + 6 t_R",
            "red_trace_weight": "10 + 10 t_R",
            "t_R": "max(0, ceil((r-6)/4))",
            "blue_length": "5 + 4 t_B",
            "blue_trace_weight": "8 + 6 t_B",
            "t_B": "max(0, ceil((r-4)/2))",
        },
        "trace_blocks": block_payload,
        "trace_blocks_sha256": hashlib.sha256(
            json.dumps(block_payload, separators=(",", ":"), sort_keys=True).encode()
        ).hexdigest(),
        "small_filler_lemma_regression": exhaustive_small_filler_lemma_check(),
        "ranks_symbolically_checked": [3, 1000],
        "materialized_ranks": sorted(materialized_ranks),
        "all_998_rank_plans_passed": True,
        "selected_ranks": selected,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
