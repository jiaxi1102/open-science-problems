#!/usr/bin/env python3
"""Generate and independently check finite SAT instances for math-0002.

Modes
-----
``petersen`` searches for a red/blue coloring of E(KG(8,2)) with no
monochromatic Kneser triangle and no monochromatic induced KG(5,2).

``petersen-template`` fixes one red induced KG(5,2) on ground points
{3,4,5,6,7} and searches for a red-independent family violating the 31/10
dual template on the complementary triple {0,1,2}.  By ground-set and color
symmetry, UNSAT proves the template lemma for every monochromatic Petersen.

``template`` is a larger monolithic cross-check: it searches for a coloring
with no monochromatic Kneser triangle for which every one of the 112 candidate
(color, ground-triple) 31/10 dual certificates fails.  Failure is witnessed
by a selected independent family of total template weight at least 11.

SAT output is checked semantically in every mode.  An UNSAT claim is accepted
only together with an independently checked proof trace.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse, json, re, sys

V = list(combinations(range(8), 2))
VID = {v: i for i, v in enumerate(V)}
E = [(u, v) for u, v in combinations(range(28), 2)
     if set(V[u]).isdisjoint(V[v])]
EID = {e: i for i, e in enumerate(E)}
TRIANGLES = []
for a, b, c in combinations(range(28), 3):
    if (set(V[a]).isdisjoint(V[b]) and
        set(V[a]).isdisjoint(V[c]) and
        set(V[b]).isdisjoint(V[c])):
        TRIANGLES.append((EID[(a, b)], EID[(a, c)], EID[(b, c)]))
GROUND_TRIPLES = list(combinations(range(8), 3))
assert (len(V), len(E), len(TRIANGLES), len(GROUND_TRIPLES)) == (28, 210, 420, 56)

class CNF:
    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[tuple[int, ...]] = []
        self.names: dict[str, int] = {}
    def var(self, name: str) -> int:
        if name in self.names:
            return self.names[name]
        self.nvars += 1
        self.names[name] = self.nvars
        return self.nvars
    def fresh(self, prefix: str) -> int:
        self.nvars += 1
        self.names[f"{prefix}_{self.nvars}"] = self.nvars
        return self.nvars
    def add(self, *lits: int) -> None:
        if not lits:
            self.clauses.append(())
            return
        # Tautologies are harmless but removing them makes the artifact stable.
        s = set(lits)
        if any(-x in s for x in s):
            return
        self.clauses.append(tuple(dict.fromkeys(lits)))


def at_most_sinz(cnf: CNF, lits: list[int], k: int, prefix: str) -> None:
    """Sinz sequential encoding of sum(lits) <= k for arbitrary literals.

    Inputs may repeat.  This intentionally permits duplicate literals because
    the 31/10 weight gives the three boosted selection variables multiplicity
    two.  The sequential positions count occurrences, not distinct variables.
    """
    n = len(lits)
    if k < 0:
        cnf.add(); return
    if k >= n:
        return
    if k == 0:
        for lit in lits: cnf.add(-lit)
        return
    # s[i][j] means at least j+1 of input positions 0..i are true.
    s = [[cnf.fresh(f"{prefix}_s{i}_{j}") for j in range(k)]
         for i in range(n - 1)]
    cnf.add(-lits[0], s[0][0])
    for i in range(1, n - 1):
        cnf.add(-lits[i], s[i][0])
        cnf.add(-s[i - 1][0], s[i][0])
        for j in range(1, k):
            cnf.add(-lits[i], -s[i - 1][j - 1], s[i][j])
            cnf.add(-s[i - 1][j], s[i][j])
        cnf.add(-lits[i], -s[i - 1][k - 1])
    cnf.add(-lits[-1], -s[-1][k - 1])


def base_coloring(cnf: CNF, *, break_color_symmetry: bool = True) -> list[int]:
    x = [cnf.var(f"edge_color_{e}") for e in range(210)]  # true = red
    for a, b, c in TRIANGLES:
        cnf.add(x[a], x[b], x[c])       # not all blue
        cnf.add(-x[a], -x[b], -x[c])    # not all red
    if break_color_symmetry:
        # Global color complementation is an exact symmetry for the two
        # universal counterexample searches.  It is not used once a red
        # Petersen graph has been fixed explicitly.
        cnf.add(-x[0])
    return x



def petersen_edge_ids(ground_five_set: tuple[int, ...]) -> list[int]:
    vertices = [VID[e] for e in combinations(ground_five_set, 2)]
    edges = [EID[tuple(sorted((u, v)))]
             for u, v in combinations(vertices, 2)
             if set(V[u]).isdisjoint(V[v])]
    assert len(edges) == 15
    return edges

def build_petersen() -> tuple[CNF, dict]:
    cnf = CNF(); x = base_coloring(cnf)
    petersen_edges: list[list[int]] = []
    for T in combinations(range(8), 5):
        es = petersen_edge_ids(T)
        petersen_edges.append(es)
        cnf.add(*(x[e] for e in es))     # at least one red
        cnf.add(*(-x[e] for e in es))    # at least one blue
    meta = {
        "mode": "petersen", "edge_vars": x,
        "petersen_edge_ids": petersen_edges,
        "semantic_statement": (
            "counterexample to: every triangle-free red/blue coloring of "
            "E(KG(8,2)) contains a monochromatic induced KG(5,2)"
        ),
    }
    return cnf, meta


def build_petersen_template() -> tuple[CNF, dict]:
    """Counterexample to the fixed monochromatic-Petersen template lemma."""
    cnf = CNF()
    x = base_coloring(cnf, break_color_symmetry=False)
    S = (0, 1, 2)
    T = (3, 4, 5, 6, 7)
    p_edges = petersen_edge_ids(T)
    for edge in p_edges:
        cnf.add(x[edge])                 # the fixed Petersen graph is red

    z = [cnf.var(f"select_{v}") for v in range(28)]
    for edge, (u, v) in enumerate(E):
        cnf.add(-z[u], -z[v], -x[edge])  # selected family is red-independent

    boost = {VID[e] for e in combinations(S, 2)}
    weighted = z + [z[v] for v in sorted(boost)]
    assert len(weighted) == 31
    # Violate the proposed dual constraint by requiring weighted size >= 11.
    at_most_sinz(cnf, [-lit for lit in weighted], 20, "fixed_weight")
    meta = {
        "mode": "petersen-template",
        "edge_vars": x,
        "fixed_petersen_ground_set": list(T),
        "fixed_petersen_edge_ids": p_edges,
        "template_ground_triple": list(S),
        "selector_vars": z,
        "semantic_statement": (
            "counterexample to: a monochromatic Petersen graph forces the "
            "31/10 dual template on its complementary ground triple"
        ),
    }
    return cnf, meta


def build_template() -> tuple[CNF, dict]:
    cnf = CNF(); x = base_coloring(cnf)
    selector_vars: list[list[list[int]]] = []
    for si, S in enumerate(GROUND_TRIPLES):
        boost = {VID[e] for e in combinations(S, 2)}
        per_color: list[list[int]] = []
        for color in range(2):  # 0=independent in red, 1=independent in blue
            z = [cnf.var(f"select_{si}_{color}_{v}") for v in range(28)]
            per_color.append(z)
            for e, (u, v) in enumerate(E):
                if color == 0:
                    cnf.add(-z[u], -z[v], -x[e])  # no selected red edge
                else:
                    cnf.add(-z[u], -z[v], x[e])   # no selected blue edge
            # Weighted size >= 11.  There are 31 occurrence slots: one for
            # every K8 edge, plus a second copy of each of E(S).  Equivalently,
            # at most 20 of those selection occurrences are false.
            weighted = z + [z[v] for v in sorted(boost)]
            assert len(weighted) == 31
            at_most_sinz(cnf, [-lit for lit in weighted], 20,
                         f"weight_{si}_{color}")
        selector_vars.append(per_color)
    meta = {
        "mode": "template", "edge_vars": x,
        "ground_triples": [list(S) for S in GROUND_TRIPLES],
        "selector_vars": selector_vars,
        "semantic_statement": (
            "counterexample to the universal 31/10 three-point dual-template theorem"
        ),
    }
    return cnf, meta


def write_instance(mode: str, outdir: Path) -> None:
    builders = {
        "petersen": build_petersen,
        "petersen-template": build_petersen_template,
        "template": build_template,
    }
    cnf, meta = builders[mode]()
    outdir.mkdir(parents=True, exist_ok=True)
    cnf_path = outdir / f"{mode}.cnf"
    with cnf_path.open("w") as f:
        f.write(f"p cnf {cnf.nvars} {len(cnf.clauses)}\n")
        for clause in cnf.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    meta.update({
        "vertices": [list(v) for v in V],
        "kneser_edges": [list(e) for e in E],
        "triangle_edge_ids": [list(t) for t in TRIANGLES],
        "variables": cnf.nvars,
        "clauses": len(cnf.clauses),
        "cnf_sha256": sha256(cnf_path.read_bytes()).hexdigest(),
    })
    meta_path = outdir / f"{mode}.json"
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "mode": mode, "cnf": str(cnf_path), "metadata": str(meta_path),
        "variables": cnf.nvars, "clauses": len(cnf.clauses),
        "cnf_sha256": meta["cnf_sha256"],
        "metadata_sha256": sha256(meta_path.read_bytes()).hexdigest(),
    }, sort_keys=True))


def parse_model(path: Path) -> set[int]:
    text = path.read_text(errors="replace")
    if "UNSATISFIABLE" in text:
        raise ValueError("solver output is UNSAT, not a model")
    if "SATISFIABLE" not in text:
        raise ValueError("solver output has no SATISFIABLE status")
    vals: dict[int, bool] = {}
    for line in text.splitlines():
        if line.startswith("v "):
            for tok in line[2:].split():
                lit = int(tok)
                if lit: vals[abs(lit)] = lit > 0
    return {v for v, value in vals.items() if value}


def verify(mode: str, outdir: Path, model_path: Path) -> None:
    meta = json.loads((outdir / f"{mode}.json").read_text())
    true_vars = parse_model(model_path)
    xvars = meta["edge_vars"]
    bits = [v in true_vars for v in xvars]
    for a, b, c in TRIANGLES:
        assert not (bits[a] == bits[b] == bits[c])
    if mode == "petersen":
        for es in meta["petersen_edge_ids"]:
            colors = {bits[e] for e in es}
            assert colors == {False, True}
    elif mode == "petersen-template":
        assert all(bits[e] for e in meta["fixed_petersen_edge_ids"])
        S = tuple(meta["template_ground_triple"])
        boost = {VID[e] for e in combinations(S, 2)}
        selected = {v for v, var in enumerate(meta["selector_vars"])
                    if var in true_vars}
        assert len(selected) + len(selected & boost) >= 11
        for e, (u, v) in enumerate(E):
            if u in selected and v in selected:
                assert not bits[e]
    else:
        for si, S0 in enumerate(meta["ground_triples"]):
            S = tuple(S0)
            boost = {VID[e] for e in combinations(S, 2)}
            for color in range(2):
                selected = {v for v, var in enumerate(meta["selector_vars"][si][color])
                            if var in true_vars}
                weight = len(selected) + len(selected & boost)
                assert weight >= 11
                for e, (u, v) in enumerate(E):
                    if u in selected and v in selected:
                        assert bits[e] != (color == 0)
    result = {
        "mode": mode, "verified": True,
        "edge_coloring": "".join("1" if b else "0" for b in bits),
        "model_sha256": sha256(model_path.read_bytes()).hexdigest(),
    }
    result_path = outdir / f"{mode}-model-verification.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


def self_test() -> None:
    # Exact semantic regression for the graph lists.
    assert len(set(E)) == 210 and len(set(TRIANGLES)) == 420
    for e, (u, v) in enumerate(E):
        assert EID[(u, v)] == e and set(V[u]).isdisjoint(V[v])
    for a, b, c in TRIANGLES:
        assert len({a, b, c}) == 3
    # Check the sequential counter against all primary/auxiliary assignments
    # for small instances. Existential satisfiability must equal sum(inputs)<=k.
    for n in range(1, 6):
        for k in range(n + 1):
            for primary in product([False, True], repeat=n):
                c = CNF(); xs = [c.var(f"x{i}") for i in range(n)]
                at_most_sinz(c, xs, k, "test")
                aux = list(range(n + 1, c.nvars + 1))
                sat = False
                for av in product([False, True], repeat=len(aux)):
                    truth = {i + 1: primary[i] for i in range(n)}
                    truth.update(dict(zip(aux, av)))
                    if all(any((lit > 0) == truth[abs(lit)] for lit in cl)
                           for cl in c.clauses):
                        sat = True; break
                assert sat == (sum(primary) <= k), (n, k, primary)
    print("self-test: ok")


def main() -> None:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    modes = ["petersen", "petersen-template", "template"]
    g = sp.add_parser("generate"); g.add_argument("mode", choices=modes); g.add_argument("outdir", type=Path)
    v = sp.add_parser("verify"); v.add_argument("mode", choices=modes); v.add_argument("outdir", type=Path); v.add_argument("model", type=Path)
    sp.add_parser("self-test")
    a = p.parse_args()
    if a.cmd == "generate": write_instance(a.mode, a.outdir)
    elif a.cmd == "verify": verify(a.mode, a.outdir, a.model)
    else: self_test()
if __name__ == "__main__": main()
