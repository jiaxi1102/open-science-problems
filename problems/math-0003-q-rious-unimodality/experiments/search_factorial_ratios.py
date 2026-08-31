#!/usr/bin/env python3
"""Exhaustive search that discovered the math-0003 counterexample.

Scope: balanced integer-partition pairs with total sum <= MAX_SUM, positive
height <= MAX_HEIGHT, gcd 1, and no cancellable common tuple entries.
All arithmetic is exact. SymPy is used only to construct cyclotomic polynomials.
"""
from __future__ import annotations

import argparse
import json
import time
from fractions import Fraction
from functools import lru_cache
from math import gcd
from typing import Sequence

import sympy as sp

Q = sp.Symbol("q")


@lru_cache(maxsize=None)
def partitions(n: int, maximum: int | None = None) -> tuple[tuple[int, ...], ...]:
    if n == 0:
        return ((),)
    maximum = n if maximum is None else min(maximum, n)
    result: list[tuple[int, ...]] = []
    for first in range(maximum, 0, -1):
        for tail in partitions(n - first, first):
            result.append((first,) + tail)
    return tuple(result)


def primitive_without_cancellation(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    if set(a) & set(b):
        return False
    common_gcd = 0
    for value in a + b:
        common_gcd = gcd(common_gcd, value)
    return common_gcd == 1


def floor_fraction(x: Fraction) -> int:
    return x.numerator // x.denominator


def satisfies_landau(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    """Check the balanced, one-periodic step function on every constant cell."""
    breakpoints = {Fraction(0), Fraction(1)}
    for value in a + b:
        breakpoints.update(Fraction(k, value) for k in range(1, value + 1))
    ordered = sorted(breakpoints)
    tests = set(ordered)
    tests.update((left + right) / 2 for left, right in zip(ordered, ordered[1:]))
    for x in tests:
        step = sum(floor_fraction(value * x) for value in a)
        step -= sum(floor_fraction(value * x) for value in b)
        if step < 0:
            return False
    return True


@lru_cache(maxsize=None)
def cyclotomic_coefficients(index: int) -> tuple[int, ...]:
    polynomial = sp.Poly(sp.cyclotomic_poly(index, Q), Q)
    return tuple(int(c) for c in reversed(polynomial.all_coeffs()))


def multiply(left: Sequence[int], right: Sequence[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if not a:
            continue
        for j, b in enumerate(right):
            if b:
                result[i + j] += a * b
    return result


def power(polynomial: Sequence[int], exponent: int) -> list[int]:
    result = [1]
    base = list(polynomial)
    while exponent:
        if exponent & 1:
            result = multiply(result, base)
        exponent //= 2
        if exponent:
            base = multiply(base, base)
    return result


def ratio_polynomial(
    a: tuple[int, ...], b: tuple[int, ...]
) -> tuple[list[int], list[tuple[int, int]]]:
    result = [1]
    factorization: list[tuple[int, int]] = []
    for index in range(2, max(a + b) + 1):
        exponent = sum(value // index for value in a)
        exponent -= sum(value // index for value in b)
        if exponent < 0:
            raise ValueError("Landau-valid pair unexpectedly has negative cyclotomic exponent")
        if exponent:
            result = multiply(result, power(cyclotomic_coefficients(index), exponent))
            factorization.append((index, exponent))
    return result, factorization


def multiply_by_one_plus_q(coefficients: Sequence[int]) -> list[int]:
    result = [0] * (len(coefficients) + 1)
    for index, coefficient in enumerate(coefficients):
        result[index] += coefficient
        result[index + 1] += coefficient
    return result


def is_weakly_unimodal(coefficients: Sequence[int]) -> bool:
    descending = False
    for left, right in zip(coefficients, coefficients[1:]):
        if right < left:
            descending = True
        elif right > left and descending:
            return False
    return True


def scan(max_sum: int, max_height: int, max_degree: int) -> list[dict[str, object]]:
    started = time.monotonic()
    total_tested = 0
    total_landau = 0
    counterexamples: list[dict[str, object]] = []

    for total in range(2, max_sum + 1):
        grouped: dict[int, list[tuple[int, ...]]] = {}
        for partition in partitions(total):
            grouped.setdefault(len(partition), []).append(partition)
        sum_tested = 0
        sum_landau = 0
        sum_counterexamples = 0

        for numerator_length, numerators in grouped.items():
            for height in range(1, max_height + 1):
                denominators = grouped.get(numerator_length + height, ())
                for a in numerators:
                    for b in denominators:
                        total_tested += 1
                        sum_tested += 1
                        if not primitive_without_cancellation(a, b):
                            continue
                        if not satisfies_landau(a, b):
                            continue
                        total_landau += 1
                        sum_landau += 1
                        degree = sum(v * (v - 1) // 2 for v in a)
                        degree -= sum(v * (v - 1) // 2 for v in b)
                        if degree < 0 or degree > max_degree:
                            continue
                        d_coefficients, factors = ratio_polynomial(a, b)
                        q_coefficients = multiply_by_one_plus_q(d_coefficients)
                        if is_weakly_unimodal(q_coefficients):
                            continue
                        record: dict[str, object] = {
                            "total_sum": total,
                            "a": a,
                            "b": b,
                            "height": height,
                            "degree_D": degree,
                            "D_positive": all(c >= 0 for c in d_coefficients),
                            "cyclotomic_factors": factors,
                            "D_coefficients": d_coefficients,
                            "one_plus_q_D_coefficients": q_coefficients,
                        }
                        counterexamples.append(record)
                        sum_counterexamples += 1
                        print("COUNTEREXAMPLE " + json.dumps(record, separators=(",", ":")))

        print(
            f"SUM {total}: tested={sum_tested} landau_valid={sum_landau} "
            f"counterexamples={sum_counterexamples}"
        )

    print(
        f"TOTAL: tested={total_tested} landau_valid={total_landau} "
        f"counterexamples={len(counterexamples)} elapsed_seconds={time.monotonic() - started:.3f}"
    )
    return counterexamples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-sum", type=int, default=22)
    parser.add_argument("--max-height", type=int, default=6)
    parser.add_argument("--max-degree", type=int, default=1000)
    args = parser.parse_args()
    records = scan(args.max_sum, args.max_height, args.max_degree)
    expected = [
        record
        for record in records
        if tuple(record["a"]) == (12, 5, 3, 2)
        and tuple(record["b"]) == (9, 6, 4, 1, 1, 1)
    ]
    if args.max_sum == 22 and args.max_height == 6 and args.max_degree >= 23:
        assert len(records) == 1, records
        assert len(expected) == 1


if __name__ == "__main__":
    main()
