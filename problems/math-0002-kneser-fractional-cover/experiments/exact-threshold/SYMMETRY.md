# Symmetry reductions used

The `petersen` formula fixes only global colour complementation by setting one edge colour; this is valid because the counterexample property is invariant under swapping red and blue.

The `petersen-template` formula does not impose that extra colour bit. Instead it fixes the monochromatic Petersen to be red and its five ground points to `{3,4,5,6,7}`. The action of `S_8` is transitive on five-subsets, and colour complementation exchanges a blue Petersen with a red one, so this represents every case without loss.
