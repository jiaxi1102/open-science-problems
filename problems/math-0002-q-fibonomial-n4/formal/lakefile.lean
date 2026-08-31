import Lake
open Lake DSL

package QFibonomial4 where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.33.1"

@[default_target]
lean_lib QFibonomial4 where
  roots := #[
    `QFibonomial4,
    `QFibonomial4All,
    `QFibonomial4Series,
    `QFibonomial4PowerSeries,
    `QFibonomial4Unimodal
  ]
