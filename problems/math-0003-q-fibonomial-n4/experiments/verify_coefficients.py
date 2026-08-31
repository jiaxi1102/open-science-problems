#!/usr/bin/env python3
"""Independent exact checks for the n=4 q-Fibonomial proof.

This script uses the closed partition formula and the complete numerator
expansion.  It is diagnostic only; the mathematical proof and Lean certificate
do not depend on it.
"""

from __future__ import annotations

import argparse


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def g(t: int) -> int:
    if t < 0:
        return 0
    return (t * t + 6 * t + 12) // 12


def full_delta(x: int, y: int, k: int) -> int:
    return (
        g(k)
        - g(k - x)
        - g(k - y)
        + g(k - (2 * x + y))
        + g(k - (x + 3 * y))
        - g(k - (3 * x + 3 * y))
        - g(k - (2 * x + 4 * y))
        + g(k - (3 * x + 4 * y))
    )


def reduced_delta(x: int, y: int, k: int) -> int:
    return g(k) - g(k - x) - g(k - y) + g(k - (2 * x + y))


def coefficients(m: int) -> list[int]:
    x, y = fib(m + 1), fib(m + 2)
    degree = 3 * x + 4 * y - 7
    out: list[int] = []
    running = 0
    for k in range(degree + 1):
        running += full_delta(x, y, k)
        out.append(running)
    return out


def verify(m: int) -> None:
    x, y = fib(m + 1), fib(m + 2)
    degree = 3 * x + 4 * y - 7
    coeffs = coefficients(m)
    assert all(c >= 0 for c in coeffs)
    assert coeffs == coeffs[::-1]
    assert all(coeffs[k] <= coeffs[k + 1] for k in range(degree // 2))
    for k in range(1, degree // 2 + 1):
        assert full_delta(x, y, k) == reduced_delta(x, y, k)
        assert reduced_delta(x, y, k) >= 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-m", type=int, default=20)
    args = parser.parse_args()
    for m in range(args.max_m + 1):
        verify(m)
        print(f"m={m}: verified")


if __name__ == "__main__":
    main()
