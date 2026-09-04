#!/usr/bin/env python3
"""Expose circuits and use S8-transitivity to fix the first double-star core."""
from pathlib import Path
p = Path(__file__).with_name('KneserCover.lean')
s = p.read_text()
# Turn the double-star predicate into a proposition so simp can expose it.
start=s.index('def containedInDoubleStar')
end=s.index('\ndef blueOnChunk0',start)
core=s[start:end].replace(': Bool :=',': Prop :=',1)
core=core.replace(' == chosen',' = chosen').replace(' ||',' ∨')
s=s[:start]+core+s[end:]
matching=['popcount28','bitAsFive','matchingFree']+[f'matchingFreeChunk{i}' for i in range(18)]+['containedInDoubleStar']
s=s.replace('    containedInDoubleStar chosen = true := by\n  bv_decide',
'''    containedInDoubleStar chosen := by
  simp only [%s] at *
  bv_decide (config := { timeout := 300 })''' % ', '.join(matching))
# Keep all definitions and the concrete sharpness witness, but replace the
# fully symmetric expensive theorem by the transitivity-reduced statement.
cut=s.index('/-- No triangle-free red/blue colouring')
s=s[:cut]
defs=['popcount28','bitAsFive','containedInDoubleStar','blueOn']+[f'blueOnChunk{i}' for i in range(9)]+['redOn']+[f'redOnChunk{i}' for i in range(9)]+['triangleFree']+[f'triangleFreeChunk{i}' for i in range(18)]
s += '''/-- After relabelling the first double-star core to `{0,1}`, no
triangle-free red/blue colouring has opposite 11-vertex independent sets.
The second core remains completely arbitrary. -/
theorem core01_obstruction11
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 11#5)
    (hBCard : popcount28 B = 11#5)
    (hAStar : (A &&& 8191#28) = A)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [%s] at *
  bv_decide (config := { timeout := 1800 })

#print axioms ten_set_sharpness_witness
#print axioms matchingFree11_is_doubleStar
#print axioms core01_obstruction11

end KneserCover
''' % ', '.join(defs)
p.write_text(s)
