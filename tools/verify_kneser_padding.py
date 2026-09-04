#!/usr/bin/env python3
"""Exhaustive finite regressions for the padded five-point Kneser coloring.

True is red. Universal r,s validity requires the separate proof; these tests
are not extrapolated into a universal theorem. Uses only the standard library.
"""
from __future__ import annotations
import hashlib
import itertools
import json


def five_point_red(a: int, b: int) -> bool:
    if not 0 <= a < 32 or not 0 <= b < 32:
        raise ValueError("Five-point masks must lie in [0,32)")
    sa, sb = a.bit_count() == 1, b.bit_count() == 1
    if not sa and not sb:
        return (a == 0) == (b == 0)
    if sa and sb:
        return ((a.bit_length() - b.bit_length()) % 5) in (1, 4)
    singleton, other = (a, b) if sa else (b, a)
    return other == 0 or bool(other & (1 << ((singleton.bit_length() - 2) % 5)))


def padded_red(a: int, b: int) -> bool:
    """Low five bits encode P; remaining bits encode the padding set D."""
    if a < 0 or b < 0:
        raise ValueError("Masks must be nonnegative")
    if (a >> 5) or (b >> 5):
        return a != 0 and b != 0
    return five_point_red(a & 31, b & 31)


def disjoint_families(m: int, length: int):
    """Sorted disjoint masks; repeated empty traces are deliberately allowed."""
    def rec(remaining: int, lower: int, chosen: tuple[int, ...]):
        if len(chosen) == length:
            yield chosen
            return
        sub = remaining
        choices = []
        while True:
            if sub >= lower:
                choices.append(sub)
            if sub == 0:
                break
            sub = (sub - 1) & remaining
        for a in reversed(choices):
            yield from rec(remaining ^ a, a, chosen + (a,))
    yield from rec((1 << m) - 1, 0, ())


def verify_gadget():
    triples = 0
    for a, b, c in itertools.product(range(32), repeat=3):
        if a & b or a & c or b & c:
            continue
        triples += 1
        colors = five_point_red(a,b), five_point_red(a,c), five_point_red(b,c)
        if not any(colors):
            raise AssertionError(('blue trace triangle', a,b,c))
        if a and b and c and all(colors):
            raise AssertionError(('nonempty red trace triangle', a,b,c))
    for a in range(32):
        if five_point_red(0,a) != (a.bit_count() <= 1):
            raise AssertionError(('empty interface', a))
    for a,b in itertools.product(range(32), repeat=2):
        if five_point_red(a,b) != five_point_red(b,a):
            raise AssertionError(('symmetry', a,b))
    return {'ordered_disjoint_triples': triples, 'blue_triangles': 0,
            'nonempty_red_triangles': 0, 'empty_interface_cases': 32}


def verify_padded(s: int):
    if s < 3:
        raise ValueError('s must be at least three')
    m = s+2
    triples = 0
    for a,b,c in disjoint_families(m,3):
        triples += 1
        if not any((padded_red(a,b),padded_red(a,c),padded_red(b,c))):
            raise AssertionError(('blue padded triangle',s,a,b,c))
    families, red_families, max_coverage = 0, 0, -1
    for family in disjoint_families(m,s):
        families += 1
        if all(padded_red(a,b) for a,b in itertools.combinations(family,2)):
            red_families += 1
            coverage = sum(a.bit_count() for a in family)
            max_coverage = max(max_coverage,coverage)
            if coverage > 2:
                raise AssertionError(('red family covering three points',s,family))
    return {'s': s, 'distinguished_points': m,
            'triangle_trace_families': triples, 's_trace_families': families,
            'red_s_trace_families': red_families, 'maximum_red_s_coverage': max_coverage,
            'blue_triangles': 0, 'red_s_families_covering_at_least_three': 0}


def main():
    table = bytes(five_point_red(a,b) for a in range(32) for b in range(32) if not a&b)
    result = {'theorem': 'R_r^KG(s,3) >= s*(r+1), r>=1, s>=3',
              'verification_scope': 'finite regressions; universal proof separate',
              'five_point_lemmas': verify_gadget(),
              'padding_regressions': [verify_padded(s) for s in range(3,9)],
              'table_encoding': 'one byte 0/1 per ordered disjoint mask pair; lexicographic',
              'table_sha256': hashlib.sha256(table).hexdigest()}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
