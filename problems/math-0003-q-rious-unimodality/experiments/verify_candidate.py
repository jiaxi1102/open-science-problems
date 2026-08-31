#!/usr/bin/env python3
"""Independent exact verifier for the math-0003 q-rious counterexample.

This script uses only Python's standard library and integer arithmetic. It
checks balance, coprimality, Landau's criterion over one exact period, exact
q-factorial polynomial division, the complete coefficient vectors, and the
non-unimodality witness.
"""
from __future__ import annotations

from math import factorial, gcd, lcm
from typing import Iterable, Sequence

A = (12, 5, 3, 2)
B = (9, 6, 4, 1, 1, 1)
EXPECTED_D = (
    1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 8, 7,
    7, 8, 8, 7, 6, 5, 4, 3, 2, 2, 2, 1,
)
EXPECTED_Q = (
    1, 3, 4, 4, 5, 7, 9, 11, 13, 15, 16, 15, 14,
    15, 16, 15, 13, 11, 9, 7, 5, 4, 4, 3, 1,
)


def trim(p: list[int]) -> list[int]:
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def mul(p: Sequence[int], q: Sequence[int]) -> list[int]:
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return trim(out)


def q_integer(n: int) -> list[int]:
    if n < 1:
        raise ValueError("q-integer index must be positive")
    return [1] * n


def q_factorial(n: int) -> list[int]:
    out = [1]
    for k in range(1, n + 1):
        out = mul(out, q_integer(k))
    return out


def product(polynomials: Iterable[Sequence[int]]) -> list[int]:
    out = [1]
    for p in polynomials:
        out = mul(out, p)
    return out


def divmod_monic(num: Sequence[int], den: Sequence[int]) -> tuple[list[int], list[int]]:
    """Polynomial long division in Z[q], coefficients in ascending order."""
    den = trim(list(den))
    if den == [0] or den[-1] != 1:
        raise ValueError("denominator must be nonzero and monic")
    rem = trim(list(num))
    quotient = [0] * max(1, len(rem) - len(den) + 1)
    while rem != [0] and len(rem) >= len(den):
        shift = len(rem) - len(den)
        coefficient = rem[-1]
        quotient[shift] += coefficient
        for j, d in enumerate(den):
            rem[shift + j] -= coefficient * d
        trim(rem)
    return trim(quotient), trim(rem)


def landau_value_at_residue(r: int, period: int) -> int:
    return sum((a * r) // period for a in A) - sum((b * r) // period for b in B)


def is_weakly_unimodal(coefficients: Sequence[int]) -> bool:
    descending = False
    for left, right in zip(coefficients, coefficients[1:]):
        if right < left:
            descending = True
        elif right > left and descending:
            return False
    return True


def main() -> None:
    assert sum(A) == sum(B) == 22
    assert gcd(*A, *B) == 1
    assert not (set(A) & set(B))

    period = lcm(*A, *B)
    assert period == 180
    values = [landau_value_at_residue(r, period) for r in range(period)]
    counts = {v: values.count(v) for v in sorted(set(values))}
    assert min(values) >= 0
    assert counts == {0: 68, 1: 44, 2: 68}

    numerator = product(q_factorial(a) for a in A)
    denominator = product(q_factorial(b) for b in B)
    quotient, remainder = divmod_monic(numerator, denominator)
    assert remainder == [0]
    assert tuple(quotient) == EXPECTED_D

    q_times = [0] + quotient
    one_times = quotient + [0]
    q_polynomial = [x + y for x, y in zip(one_times, q_times)]
    assert tuple(q_polynomial) == EXPECTED_Q
    assert q_polynomial[10] == 16
    assert q_polynomial[12] == 14
    assert q_polynomial[14] == 16
    assert not is_weakly_unimodal(q_polynomial)

    classical_numerator = 1
    classical_denominator = 1
    for a in A:
        classical_numerator *= factorial(a)
    for b in B:
        classical_denominator *= factorial(b)
    classical_ratio, classical_remainder = divmod(classical_numerator, classical_denominator)
    assert classical_remainder == 0
    assert classical_ratio == sum(quotient) == 110

    print("candidate_a=", A)
    print("candidate_b=", B)
    print("balanced_sum=22 height=2 gcd=1 no_cancellation=true")
    print("landau_period=180")
    print("landau_value_counts=", counts)
    print("q_factorial_division_remainder=0")
    print("D_coefficients=", quotient)
    print("(1+q)D_coefficients=", q_polynomial)
    print("nonunimodality_witness=(degree 10:16, degree 12:14, degree 14:16)")
    print("classical_factorial_ratio=110")
    print("VERIFIED")


if __name__ == "__main__":
    main()
