import Lake
open Lake DSL

package KneserFivePoint where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.33.1"

@[default_target]
lean_lib KneserFivePoint where
  roots := #[`KneserFivePoint, `KneserFivePoint.LowerBound]
