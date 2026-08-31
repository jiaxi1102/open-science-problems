#!/usr/bin/env python3
"""Independent finite cross-check for the hedgehog indexing convention.

For every Boolean delay pattern through ``--max-leaves`` this script compares:

1. the specialized first-pluck recursion, using a separately recursive ordinary
   star polynomial; and
2. the factorized polynomial ``p_n(q) [n-1]_q!``.

It also checks weak unimodality directly.  This is not part of the proof; it is
an implementation-independent regression test for the formal statement and
right-to-left exponent convention.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import product
from typing import Iterable, Sequence

Polynomial = tuple[int, ...]


def trim(coeffs: list[int]) -> Polynomial:
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return tuple(coeffs)


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    out = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        out[index] += value
    for index, value in enumerate(right):
        out[index] += value
    return trim(out)


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] += x * y
    return trim(out)


def shift(poly: Polynomial, exponent: int) -> Polynomial:
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    return (0,) * exponent + poly


def q_factorial(n: int) -> Polynomial:
    if n < 0:
        raise ValueError("n must be nonnegative")
    out: Polynomial = (1,)
    for r in range(1, n + 1):
        out = multiply(out, (1,) * r)
    return out


@lru_cache(maxsize=None)
def recursive_plain_star(n: int) -> Polynomial:
    """Ordinary n-leaf star from the leaf-plucking recursion."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return (1,)
    remainder = recursive_plain_star(n - 1)
    out: Polynomial = (0,)
    for exponent in range(n):
        out = add(out, shift(remainder, exponent))
    return out


def recursive_delayed_star(eligible: Sequence[bool]) -> Polynomial:
    """Initial delays in {1,2}; true means delay 1 and hence eligible."""
    n = len(eligible)
    if n == 0:
        return (1,)
    remainder = recursive_plain_star(n - 1)
    out: Polynomial = (0,)
    for exponent, is_eligible in enumerate(eligible):
        if is_eligible:
            out = add(out, shift(remainder, exponent))
    return out


def factorized_star(eligible: Sequence[bool]) -> Polynomial:
    n = len(eligible)
    if n == 0:
        return (1,)
    indicator = tuple(int(value) for value in eligible)
    return multiply(indicator, q_factorial(n - 1))


def is_weakly_unimodal(coeffs: Sequence[int]) -> bool:
    return any(
        all(coeffs[i] <= coeffs[i + 1] for i in range(mode))
        and all(
            coeffs[i] >= coeffs[i + 1]
            for i in range(mode, len(coeffs) - 1)
        )
        for mode in range(len(coeffs))
    )


def patterns(n: int) -> Iterable[tuple[bool, ...]]:
    return product((False, True), repeat=n)


def run(max_leaves: int) -> int:
    if max_leaves < 0:
        raise ValueError("--max-leaves must be nonnegative")

    checked = 0
    for n in range(max_leaves + 1):
        assert recursive_plain_star(n) == q_factorial(n), (
            "ordinary star mismatch",
            n,
            recursive_plain_star(n),
            q_factorial(n),
        )
        for eligible in patterns(n):
            recursive = recursive_delayed_star(eligible)
            factorized = factorized_star(eligible)
            assert recursive == factorized, (
                "factorization mismatch",
                n,
                eligible,
                recursive,
                factorized,
            )
            assert is_weakly_unimodal(recursive), (
                "unimodality failure",
                n,
                eligible,
                recursive,
            )
            checked += 1

    print(
        f"PASS: {checked} delay patterns checked through "
        f"{max_leaves} leaves"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-leaves", type=int, default=12)
    args = parser.parse_args()
    return run(args.max_leaves)


if __name__ == "__main__":
    raise SystemExit(main())
