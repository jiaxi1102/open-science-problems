#!/usr/bin/env python3
"""Verify the symbolic trace templates for uniform one-point saturation.

For every r >= 3 the proof uses a red-defect odd trace cycle and a blue-defect
odd trace cycle through the same base trace {0,1}. Anonymous fillers exist by
the weighted odd-cycle multicoloring lemma once two elementary inequalities
are met. This program verifies the finite trace blocks and those inequalities
for r=3,...,1000; the accompanying proof establishes the formulas for all r.
"""

from __future__ import annotations

import hashlib
import json

from verify_kneser_five_point import trace_color


def mask(*points: int) -> int:
    value = 0
    for point in points:
        value |= 1 << point
    return value


BASE = mask(0, 1)

RED_BASE = (
    BASE,
    mask(2, 3, 4),
    mask(1),
    mask(0, 3, 4),
    mask(2),
)
RED_BLOCK = (
    mask(1),
    mask(2, 3, 4),
    mask(0),
    mask(2, 3),
    mask(0, 4),
    mask(2),
)

BLUE_BASE = (
    BASE,
    mask(3),
    mask(0, 1, 2),
    mask(4),
    mask(3),
)
BLUE_BLOCK = (
    mask(0),
    mask(4),
    mask(0, 1, 2),
    mask(3),
)


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


def verify_trace_cycle(
    r: int,
    traces: tuple[int, ...],
    first_color: bool,
) -> dict[str, object]:
    assert r >= 3
    assert traces[0] == BASE
    assert len(traces) % 2 == 1

    edge_colors = []
    adjacent_trace_sums = []
    for index, left in enumerate(traces):
        right = traces[(index + 1) % len(traces)]
        assert left & right == 0
        color = trace_color(left, right)
        expected = first_color if index % 2 == 0 else not first_color
        assert color == expected
        edge_colors.append(int(color))
        adjacent_trace_sums.append(left.bit_count() + right.bit_count())

    trace_weight = sum(trace.bit_count() for trace in traces)
    demands = tuple(r - trace.bit_count() for trace in traces)
    assert min(demands) >= 0

    anonymous_points = 2 * r - 2
    independence_number = (len(traces) - 1) // 2
    max_adjacent_demand = max(
        demands[index] + demands[(index + 1) % len(demands)]
        for index in range(len(demands))
    )
    total_demand = sum(demands)

    # These are exactly the clique and odd-hole inequalities saying that the
    # demand vector lies in (2r-2) STAB(C_{2q+1}). The integer decomposition
    # property of odd-cycle stable-set polytopes then supplies filler sets.
    assert min(adjacent_trace_sums) >= 2
    assert max_adjacent_demand <= anonymous_points
    assert total_demand <= independence_number * anonymous_points
    assert trace_weight >= len(traces) + r - 1

    return {
        "length": len(traces),
        "trace_weight": trace_weight,
        "first_and_last_edge_color": "red" if first_color else "blue",
        "edge_color_word": "".join("R" if value else "B" for value in edge_colors),
        "anonymous_points": anonymous_points,
        "total_filler_demand": total_demand,
        "odd_cycle_capacity": independence_number * anonymous_points,
        "max_adjacent_filler_demand": max_adjacent_demand,
        "adjacent_capacity": anonymous_points,
        "weighted_cycle_conditions_hold": True,
    }


def verify_rank(r: int) -> dict[str, object]:
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

    return {
        "r": r,
        "base_trace": [0, 1],
        "red_repetitions": red_t,
        "blue_repetitions": blue_t,
        "red_defect_cycle": verify_trace_cycle(r, red, True),
        "blue_defect_cycle": verify_trace_cycle(r, blue, False),
    }


def main() -> None:
    # The range is a regression sweep, not the logical reason for universality.
    sweep = [verify_rank(r) for r in range(3, 1001)]
    selected = {
        str(row["r"]): row
        for row in sweep
        if row["r"] in {3, 4, 5, 6, 7, 8, 9, 10, 25, 100, 1000}
    }

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
        "proof_dependency": (
            "Integer decomposition / weighted multicoloring for an odd cycle: "
            "edge-demand inequalities plus the odd-cycle inequality suffice."
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
        "ranks_checked": [3, 1000],
        "all_998_regression_ranks_passed": True,
        "selected_ranks": selected,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
