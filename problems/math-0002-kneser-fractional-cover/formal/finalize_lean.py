#!/usr/bin/env python3
"""Expose circuits and use S8-transitivity to fix the first double-star core."""
from pathlib import Path
p = Path(__file__).with_name('KneserCover.lean')
s = p.read_text()
# supported propositional bitvector equality
start=s.index('def containedInDoubleStar')
end=s.index('\ndef blueOnChunk0',start)
core=s[start:end].replace(': Bool :=',': Prop :=',1)
core=core.replace(' == chosen',' = chosen').replace(' ||',' ∨')
s=s[:start]+core+s[end:]
matching=['popcount28','bitAsFive','matchingFree']+[f'matchingFreeChunk{i}' for i in range(18)]+['containedInDoubleStar']
s=s.replace('    containedInDoubleStar chosen = true := by\n  bv_decide',
'''    containedInDoubleStar chosen := by
  simp only [%s] at *
  bv_decide (config := { timeout := 180 })''' % ', '.join(matching))
cut=s.index('/-- No triangle-free red/blue colouring')
s=s[:cut]
defs=['popcount28','bitAsFive','containedInDoubleStar','blueOn']+[f'blueOnChunk{i}' for i in range(9)]+['redOn']+[f'redOnChunk{i}' for i in range(9)]+['triangleFree']+[f'triangleFreeChunk{i}' for i in range(18)]
# CORE_MASKS[0] = double star centered at {0,1}; generated from lexicographic V
s += '''/-- After relabelling the first double-star core to `{0,1}`, no
triangle-free red/blue colouring has opposite 12-vertex independent sets.
The second core remains completely arbitrary. -/
theorem core01_obstruction
    (A B : BV28) (colour : BV210)
    (hACard : popcount28 A = 12#5)
    (hBCard : popcount28 B = 12#5)
    (hAStar : (A &&& 8191#28) = A)
    (hBStar : containedInDoubleStar B)
    (hABlue : blueOn A colour = true)
    (hBRed : redOn B colour = true)
    (hTriangles : triangleFree colour = true) : False := by
  simp only [%s] at *
  bv_decide (config := { timeout := 600 })

#print axioms matchingFree12_is_doubleStar
#print axioms core01_obstruction

end KneserCover
''' % ', '.join(defs)
p.write_text(s)
