#!/usr/bin/env python3
"""Generate an ordinary Lean proof from a checked resolution certificate.

Z3 is an untrusted discovery tool. Every learned clause is independently
checked by reverse unit propagation (RUP), then reconstructed using only
Or.elim, False.elim, and classical contradiction in Lean. No native_decide,
bv_decide, unchecked axiom, or proof placeholder is generated.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time


def geometry():
    vertices = list(itertools.combinations(range(6), 3))
    edges = list(itertools.combinations(range(20), 2))
    index = {pair: i + 1 for i, pair in enumerate(edges)}
    triangles = [t for t in itertools.combinations(range(20), 3)
                 if not (set(vertices[t[0]]) & set(vertices[t[1]]) & set(vertices[t[2]]))]
    clauses = []
    for a, b, c in triangles:
        clause = [index[a, b], index[a, c], index[b, c]]
        clauses.extend([clause, [-x for x in clause]])
    assert (len(vertices), len(edges), len(triangles), len(clauses)) == (20, 190, 480, 960)
    return vertices, edges, triangles, clauses


def discover(clauses):
    import z3
    z3.set_param(proof=True)
    variables = [z3.Bool(f'e{i}') for i in range(190)]
    solver = z3.Solver()
    for clause in clauses:
        solver.add(z3.Or(*[variables[x - 1] if x > 0 else z3.Not(variables[-x - 1])
                          for x in clause]))
    if solver.check() != z3.unsat:
        raise RuntimeError('The finite instance was not proved unsatisfiable')
    root = solver.proof()
    visited = set()
    ordered = []
    stack = [(root, False)]
    while stack:
        expression, exiting = stack.pop()
        key = expression.get_id()
        if key in visited:
            continue
        children = expression.children()
        if exiting:
            visited.add(key)
            ordered.append(expression)
        else:
            stack.append((expression, True))
            stack.extend((child, False) for child in children if child.get_id() not in visited)

    def read_clause(expression):
        if z3.is_or(expression):
            return [lit for child in expression.children() for lit in read_clause(child)]
        if z3.is_false(expression):
            return []
        if z3.is_not(expression):
            return [-x for x in read_clause(expression.arg(0))]
        name = str(expression.decl().name())
        if not name.startswith('e') or not name[1:].isdigit():
            raise ValueError(f'Not a propositional literal: {expression}')
        return [int(name[1:]) + 1]

    learned = [read_clause(expression.arg(expression.num_args() - 1))
               for expression in ordered if str(expression.decl().name()) == 'lemma']
    return learned, {'z3_version': z3.get_full_version(), 'proof_dag_nodes': len(ordered)}


def rup(target, database):
    """Independently justify a learned clause, with explicit propagation hints."""
    assigned = set(-x for x in target)
    if any(-x in assigned for x in assigned):
        raise ValueError('Tautological learned clause not supported')
    steps = []
    while True:
        progress = False
        for ci, clause in enumerate(database):
            if any(lit in assigned for lit in clause):
                continue
            remaining = [lit for lit in clause if -lit not in assigned]
            if not remaining:
                return steps + [[ci, 0]]
            if len(remaining) == 1:
                lit = remaining[0]
                assigned.add(lit)
                steps.append([ci, lit])
                progress = True
        if not progress:
            raise ValueError(f'Failed RUP check for clause {target}')


def literal(lit):
    return f'p {abs(lit)-1}' if lit > 0 else f'¬ p {abs(lit)-1}'


def disjunction(clause):
    return ' ∨ '.join(literal(lit) for lit in clause) or 'False'


def inject(clause, position, proof):
    if len(clause) == 1:
        return proof
    if position == 0:
        return f'(Or.inl {proof})'
    return f'(Or.inr {inject(clause[1:], position-1, proof)})'


def eliminate(clause, reference, target, assigned):
    if len(clause) == 1:
        lit = clause[0]
        if lit == target:
            return reference
        contrary = assigned[-lit]
        if lit < 0:
            contrary = f'(fun hneg => hneg {contrary})'
        contradiction = f'({contrary} {reference})'
        return contradiction if target == 0 else f'(False.elim {contradiction})'
    left = eliminate(clause[:1], 'hx', target, assigned)
    right = eliminate(clause[1:], 'hy', target, assigned)
    return f'(Or.elim {reference} (fun hx => {left}) (fun hy => {right}))'


def emit_lean(original, derivations, output):
    database = list(original)
    lines = ['import Std', 'set_option maxRecDepth 16000',
             'set_option maxHeartbeats 0', 'namespace EmptyIntersection', '',
             'def clause (p : Nat → Prop) : Nat → Prop']
    for i, clause in enumerate(original):
        lines.append(f'  | {i} => {disjunction(clause)}')
    lines += ['  | _ => True', '',
              'theorem impossible (p : Nat → Prop) (h : ∀ i, clause p i) : False := by']
    for i, clause in enumerate(original):
        lines.append(f'  have c{i} : {disjunction(clause)} := h {i}')
    unit_count = 0
    for derivation in derivations:
        clause, steps = derivation['clause'], derivation['steps']
        origins = {-lit: None for lit in clause}
        dependencies = {}
        for j, (ci, lit) in enumerate(steps):
            deps = [-x for x in database[ci] if x != lit]
            if lit:
                origins[lit] = j
            dependencies[j] = [origins[x] for x in deps if origins[x] is not None]
        needed = set()
        todo = [len(steps)-1]
        while todo:
            j = todo.pop()
            if j not in needed:
                needed.add(j)
                todo.extend(dependencies[j])
        assigned = {}
        if clause:
            lines += [f'  have c{len(database)} : {disjunction(clause)} := by',
                      '    apply Classical.byContradiction', '    intro hn']
            indent = '    '
            for j, lit in enumerate(clause):
                expression = f'(fun hx => hn {inject(clause, j, "hx")})'
                if lit < 0:
                    expression = f'(Classical.byContradiction {expression})'
                name = f'a{j}'
                lines.append(f'{indent}have {name} : {literal(-lit)} := {expression}')
                assigned[-lit] = name
        else:
            indent = '  '
        for j in sorted(needed):
            ci, lit = steps[j]
            expression = eliminate(database[ci], f'c{ci}', lit, assigned)
            if lit:
                name = f'u{j}'
                lines.append(f'{indent}have {name} : {literal(lit)} := {expression}')
                assigned[lit] = name
            else:
                lines.append(f'{indent}exact {expression}')
            unit_count += 1
        database.append(clause)
    lines += ['', '#print axioms impossible', 'end EmptyIntersection']
    output.write_text('\n'.join(lines) + '\n')
    return unit_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    vertices, edges, triangles, original = geometry()
    learned, metadata = discover(original)
    database = list(original)
    derivations = []
    for clause in learned + [[]]:
        steps = rup(clause, database)
        derivations.append({'clause': clause, 'steps': steps})
        database.append(clause)
    certificate = {'vertices': vertices, 'edges': edges, 'triangles': triangles,
                   'original_clauses': original, 'derivations': derivations}
    (args.out / 'rup-certificate.json').write_text(json.dumps(certificate, separators=(',', ':')) + '\n')
    unit_count = emit_lean(original, derivations, args.out / 'Resolution.lean')
    metadata.update({'vertices': 20, 'edge_variables': 190, 'empty_intersection_triples': 480,
                     'original_clauses': 960, 'learned_clauses_including_empty': len(derivations),
                     'lean_unit_steps': unit_count, 'elapsed_seconds': time.time()-start,
                     'resolution_source_sha256': hashlib.sha256((args.out / 'Resolution.lean').read_bytes()).hexdigest(),
                     'status': 'RUP-checked; Lean compilation is a separate required gate'})
    (args.out / 'generation.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == '__main__':
    main()
