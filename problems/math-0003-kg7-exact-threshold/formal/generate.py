#!/usr/bin/env python3
"""Generate a self-contained Lean certificate. Python is not a proof oracle."""
from itertools import combinations
from pathlib import Path
import hashlib
import json

V = list(combinations(range(7), 2))
E = [(i, j) for i, j in combinations(range(21), 2)
     if set(V[i]).isdisjoint(V[j])]
EI = {e: i for i, e in enumerate(E)}
# A discovered 15-vertex induced subgraph suffices for the obstruction.
S = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 17, 18, 19]
N = {a: [b for b in S if tuple(sorted((a, b))) in EI] for a in S}
C = []
for size in (3, 5):
    def walk(p):
        if len(p) == size:
            if p[0] in N[p[-1]] and p[1] < p[-1]:
                C.append(tuple(p))
            return
        for v in N[p[-1]]:
            if v > p[0] and v not in p:
                walk(p + [v])
    for a in S:
        walk([a])
CE = [[EI[tuple(sorted((c[i], c[(i + 1) % len(c)])))]
       for i in range(len(c))] for c in C]
assert len(V) == 21 and len(E) == 105 and len(C) == 1144
for c, es in zip(C, CE):
    assert len(c) in (3, 5) and len(set(c)) == len(c)
    assert all(E[e] == tuple(sorted((c[i], c[(i + 1) % len(c)])))
               for i, e in enumerate(es))

def seq(xs):
    return '[' + ', '.join(map(str, xs)) + ']'

def pairs(xs):
    return '[' + ', '.join(f'({a}, {b})' for a, b in xs) + ']'

head = '''import Std.Tactic.BVDecide

/-!
A finite Ramsey certificate for KG(7,2).
Vertices are lexicographically ordered two-subsets of {0,...,6}.
Edges are lexicographically ordered disjoint vertex pairs.
The cycle list is only a sufficient subset, not a completeness assumption.
Its embedding and both explicit 5:2 color assignments are checked below.
No SAT solver output is assumed as an axiom.
-/
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace KG7

'''
text = head
text += 'def vertices : List (Nat × Nat) :=\n  ' + pairs(V) + '\n\n'
text += 'def edges : List (Nat × Nat) :=\n  ' + pairs(E) + '\n\n'
text += 'def certificate : List (List Nat × List Nat) := [\n'
text += ',\n'.join('  (' + seq(c) + ', ' + seq(es) + ')'
                   for c, es in zip(C, CE)) + '\n]\n\n'
text += '''def disjointPairs (a b : Nat × Nat) : Bool :=
  a.1 != b.1 && a.1 != b.2 && a.2 != b.1 && a.2 != b.2

def canonicalVertices : List (Nat × Nat) :=
  (List.range 7).flatMap fun a =>
    ((List.range 7).filter fun b => decide (a < b)).map fun b => (a, b)

def canonicalEdges : List (Nat × Nat) :=
  (List.range 21).flatMap fun a =>
    ((List.range 21).filter fun b =>
      decide (a < b) && disjointPairs vertices[a]! vertices[b]!).map fun b => (a, b)

theorem vertices_complete : vertices = canonicalVertices := by decide

theorem edges_complete : edges = canonicalEdges := by decide

def validCycle (q : List Nat × List Nat) : Bool :=
  let vs := q.1
  let es := q.2
  (vs.length == 3 || vs.length == 5) &&
  (vs.length == es.length) &&
  (vs.eraseDups.length == vs.length) &&
  (List.range vs.length).all fun i =>
    let u := vs[i]!
    let v := vs[(i + 1) % vs.length]!
    let e := es[i]!
    decide (u < 21) && decide (v < 21) && decide (e < 105) &&
    (edges[e]! == (min u v, max u v))

/-- Every listed witness is a genuine simple triangle or pentagon. -/
theorem certificate_valid : certificate.all validCycle = true := by decide

def monochromatic (colour : BitVec 105) (es : List Nat) : Bool :=
  es.all (fun e => colour.getLsbD e) || es.all (fun e => !colour.getLsbD e)

/-- Every red/blue edge coloring contains a monochromatic C3 or C5. -/
theorem odd_cycle_ramsey (colour : BitVec 105) :
    certificate.any (fun q => monochromatic colour q.2) = true := by
  bv_decide

/-- Five-color masks for the first 2-fold coloring. -/
def firstPalette (v : Nat × Nat) : Nat :=
  if v.2 < 5 then 2 ^ v.1 + 2 ^ v.2
  else if v.1 == 5 || v.2 == 5 then 3 else 12

/-- Five-color masks for the second 2-fold coloring. -/
def secondPalette (v : Nat × Nat) : Nat :=
  if v.2 < 5 then 3 else 12

def paletteSize (m : Nat) : Nat :=
  ((List.range 5).filter fun i => (m / 2 ^ i) % 2 == 1).length

def palettesValid : Bool :=
  vertices.all fun v =>
    (paletteSize (firstPalette v) == 2) &&
    (paletteSize (secondPalette v) == 2) &&
    decide (firstPalette v < 32) && decide (secondPalette v < 32)

def palettesCover : Bool :=
  edges.all fun e =>
    ((firstPalette vertices[e.1]! &&& firstPalette vertices[e.2]!) == 0) ||
    ((secondPalette vertices[e.1]! &&& secondPalette vertices[e.2]!) == 0)

/-- Each vertex receives two colors from a five-color palette in each map. -/
theorem upper_palettes_valid : palettesValid = true := by decide

/-- Every graph edge is separated by at least one of the two maps. -/
theorem upper_palettes_cover : palettesCover = true := by decide

#print axioms vertices_complete
#print axioms edges_complete
#print axioms certificate_valid
#print axioms odd_cycle_ramsey
#print axioms upper_palettes_valid
#print axioms upper_palettes_cover

end KG7
'''
p = Path(__file__).parent
(p / 'KG7.lean').write_text(text)
(p / 'certificate.json').write_text(json.dumps(
    {'vertices': V, 'edges': E, 'cycles': C, 'cycle_edges': CE}, indent=2))
print(f'KG7.lean: {len(text)} bytes; sha256={hashlib.sha256(text.encode()).hexdigest()}')
print(f'{len(V)} vertices, {len(E)} edges, {len(C)} certified cycles')
