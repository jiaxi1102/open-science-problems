#!/usr/bin/env python3
"""Reconstruct small opaque Lean lemmas and certified geometric metadata."""
from build_certificate import geometry, literal, disjunction, inject, eliminate
import build_certificate as producer


def emit_geometry(out):
    vertices, edges, triples, _ = geometry()
    lines = ['import Std', 'set_option maxRecDepth 16000', 'set_option maxHeartbeats 0',
             'namespace EmptyIntersection', 'abbrev Vertex := Fin 20',
             'abbrev Triple := Vertex × Vertex × Vertex',
             'def mask (i : Vertex) : BitVec 6 :=', '  match i.val with']
    lines += [f'  | {i} => {sum(1 << x for x in v)}#6' for i, v in enumerate(vertices)]
    lines += ['  | _ => 0#6', 'def edgeAt : Nat → Vertex × Vertex']
    lines += [f'  | {i} => ({a}, {b})' for i, (a, b) in enumerate(edges)]
    lines += ['  | _ => (0, 0)', 'def row (i : Fin 480) : Triple :=', '  match i.val with']
    lines += [f'  | {i} => ({a}, {b}, {c})' for i, (a, b, c) in enumerate(triples)]
    lines += ['  | _ => (0, 0, 0)', '''
def edgeIndex (a b : Vertex) : Nat :=
  a.val * (39 - a.val) / 2 + b.val - a.val - 1

abbrev EmptyTriple (a b c : Vertex) : Prop :=
  mask a &&& mask b &&& mask c = 0#6

abbrev Mono (color : Vertex → Vertex → Bool) (a b c : Vertex) : Prop :=
  color a b = color a c ∧ color a c = color b c

def positive (p : Nat → Prop) (t : Triple) : Prop :=
  p (edgeIndex t.1 t.2.1) ∨ p (edgeIndex t.1 t.2.2) ∨ p (edgeIndex t.2.1 t.2.2)

def negative (p : Nat → Prop) (t : Triple) : Prop :=
  ¬ p (edgeIndex t.1 t.2.1) ∨ ¬ p (edgeIndex t.1 t.2.2) ∨ ¬ p (edgeIndex t.2.1 t.2.2)

def clause (p : Nat → Prop) (i : Nat) : Prop :=
  if hi : i < 960 then
    let t := row ⟨i / 2, by omega⟩
    if i % 2 = 0 then positive p t else negative p t
  else True

theorem rowValid : ∀ i : Fin 480,
    let t := row i
    t.1 < t.2.1 ∧ t.2.1 < t.2.2 ∧ EmptyTriple t.1 t.2.1 t.2.2 := by
  decide +kernel

theorem edgeLookup : ∀ a b : Vertex, a < b → edgeAt (edgeIndex a b) = (a, b) := by
  decide +kernel

theorem booleanClauses : ∀ a b c : Bool,
    ¬ (a = b ∧ b = c) →
      (a = true ∨ b = true ∨ c = true) ∧
      (¬ a = true ∨ ¬ b = true ∨ ¬ c = true) := by
  decide +kernel

end EmptyIntersection
''']
    (out / 'CoreData.lean').write_text('\n'.join(lines) + '\n')


def emit_lean(original, derivations, output):
    emit_geometry(output.parent)
    database = list(original)
    lines = ['import CoreData', 'set_option maxRecDepth 16000', 'set_option maxHeartbeats 0',
             'namespace EmptyIntersection', '']
    for i, clause in enumerate(original):
        lines.append(f'private theorem c{i} (p : Nat → Prop) (h : ∀ i, clause p i) : {disjunction(clause)} := h {i}')
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
        todo = [len(steps) - 1]
        while todo:
            j = todo.pop()
            if j not in needed:
                needed.add(j)
                todo.extend(dependencies[j])
        lines += ['', f'private theorem c{len(database)} (p : Nat → Prop) (h : ∀ i, clause p i) : {disjunction(clause)} := by']
        assigned = {}
        if clause:
            lines += ['  apply Classical.byContradiction', '  intro hn']
            for j, lit in enumerate(clause):
                expression = f'(fun hx => hn {inject(clause, j, "hx")})'
                if lit < 0:
                    expression = f'(Classical.byContradiction {expression})'
                name = f'a{j}'
                lines.append(f'  have {name} : {literal(-lit)} := {expression}')
                assigned[-lit] = name
        for j in sorted(needed):
            ci, lit = steps[j]
            expression = eliminate(database[ci], f'(c{ci} p h)', lit, assigned)
            if lit:
                name = f'u{j}'
                lines.append(f'  have {name} : {literal(lit)} := {expression}')
                assigned[lit] = name
            else:
                lines.append(f'  exact {expression}')
            unit_count += 1
        database.append(clause)
    lines += ['', 'theorem impossible (p : Nat → Prop) (h : ∀ i, clause p i) : False :=',
              f'  c{len(database)-1} p h', '#print axioms impossible', 'end EmptyIntersection']
    output.write_text('\n'.join(lines) + '\n')
    return unit_count


if __name__ == '__main__':
    producer.emit_lean = emit_lean
    producer.main()
