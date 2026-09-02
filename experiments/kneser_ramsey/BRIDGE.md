# Fractional-host bridge for Kneser Ramsey asymptotics

**Status:** theorem candidate / literature-priority search incomplete.  
**Scope:** conceptual reduction accompanying the exact Kneser-Ramsey computations on this branch.  
**Do not cite as established novelty without independent literature review.**

## 1. Setup

For fixed graphs `F,G`, define the Kneser-Ramsey threshold

\[
a_r(F,G)=\min\{n: KG(n,r)\to(F,G)\},
\]

where `H -> (F,G)` means every red/blue edge-colouring of `H` contains a red copy of `F` or a blue copy of `G`.

For clique targets `F=K_s`, `G=K_t`, this is the parameter denoted \(R_r^{KG}(s,t)\) in Heath--McCourt--Parker--Schwieder--Zerbib.

Define the fractional-chromatic host Ramsey value

\[
\rho_f(F,G)=\inf\{\chi_f(H): H\to(F,G)\}.
\]

This is an instance of the classical general `f`/`rho`-Ramsey host-parameter framework. It should not be confused with the unrelated `fractional Ramsey number` of Jacobson--Levin--Scheinerman, which fractionalizes clique/chromatic values inside colour classes of a complete graph.

## 2. Bridge theorem for clique targets

### Theorem candidate

For fixed integers \(s,t\ge2\),

\[
\boxed{\lim_{r\to\infty}\frac{R_r^{KG}(s,t)}{r}=\rho_f(K_s,K_t).}
\]

In fact,

\[
\inf_{r\ge1}\frac{R_r^{KG}(s,t)}r=\rho_f(K_s,K_t).
\]

### Proof of the infimum identity

Let \(a_r=R_r^{KG}(s,t)\) and \(\rho=\rho_f(K_s,K_t)\).

For every `r`, the graph `KG(a_r,r)` arrows `(K_s,K_t)` by definition and

\[
\chi_f(KG(a_r,r))=a_r/r.
\]

Therefore

\[
\rho\le a_r/r
\]

for every `r`, hence \(\rho\le\inf_r a_r/r\).

Conversely, take any finite graph `H` with `H -> (K_s,K_t)`. Since finite fractional chromatic numbers are rational and are realized by a multicolouring, write

\[
\chi_f(H)=p/q
\]

with a graph homomorphism

\[
H\longrightarrow KG(p,q).
\]

Pull any red/blue edge-colouring of `KG(p,q)` back along this homomorphism. Since `H` arrows `(K_s,K_t)`, the pullback contains a monochromatic `K_s` or `K_t`. A homomorphism from a clique into a loopless graph is injective, so its image is a monochromatic clique of the same order in `KG(p,q)`. Consequently

\[
KG(p,q)\to(K_s,K_t),
\]

and hence \(a_q\le p\). Thus

\[
\inf_r a_r/r\le p/q=\chi_f(H).
\]

Taking the infimum over all Ramsey hosts `H` gives the reverse inequality and proves

\[
\inf_r a_r/r=\rho.
\]

### Proof that the full limit exists

Fix \(\varepsilon>0\). By the infimum identity, choose `q` such that

\[
a_q/q<\rho+\varepsilon/2.
\]

Let

\[
H=KG(a_q,q),
\]

so `H -> (K_s,K_t)` and \(\chi_f(H)=a_q/q\).

Let \(\chi_r(H)\) denote the `r`-fold chromatic number of `H`: the least integer `p` such that

\[
H\longrightarrow KG(p,r).
\]

The standard multicolouring characterization of fractional chromatic number gives

\[
\lim_{r\to\infty}\chi_r(H)/r=\chi_f(H).
\]

For every `r`, the homomorphism `H -> KG(chi_r(H),r)` transfers the Ramsey property to the target for clique targets, by the same pullback/injectivity argument above. Therefore

\[
a_r\le\chi_r(H).
\]

For all sufficiently large `r`,

\[
\frac{a_r}{r}\le\frac{\chi_r(H)}r<\chi_f(H)+\varepsilon/2<\rho+\varepsilon.
\]

But the infimum identity already gives \(a_r/r\ge\rho\) for every `r`. Hence

\[
\lim_{r\to\infty}a_r/r=\rho.
\]

## 3. Triangle case

For `(K_3,K_3)`, write

\[
\rho_{3,3}=\rho_f(K_3,K_3).
\]

Every Ramsey host contains a triangle, so

\[
\rho_{3,3}\ge3.
\]

The current Kneser-Ramsey literature gives an asymptotic upper coefficient at most `4`, hence the bridge reformulates the central asymptotic gap as

\[
3\le\rho_{3,3}\le4.
\]

Thus proving

\[
\rho_{3,3}=3
\]

is equivalent to proving

\[
R_r^{KG}(3,3)=3r+o(r).
\]

This reframing may be more useful than attacking the Kneser graphs directly: it asks for triangle-Ramsey host graphs whose fractional chromatic numbers approach `3`.

## 4. Exact-data conjecture

Known/computational evidence currently points to the much stronger finite statement

\[
\boxed{R_r^{KG}(3,3)=3r+3.}
\]

Evidence:

- `r=1`: classical `R(3,3)=6`;
- `r=2`: the published exact value is `9`;
- `r=3`: this branch contains an independently validated SAT witness on `KG(11,3)`, so the lower bound improves to `12`; the `KG(12,3)` upper/lower decision is still being solved and must not yet be quoted as settled.

The `r=4` graph `KG(14,4)` is also being tested as the first new lower-bound instance predicted by the conjecture.

## 5. Novelty boundary

The ingredients used above are classical:

1. general graph-parameter Ramsey host numbers;
2. the homomorphism/multicolouring characterization of fractional chromatic number by Kneser graphs;
3. convergence of `r`-fold chromatic numbers to `chi_f`;
4. injectivity of clique homomorphisms into loopless graphs.

A targeted literature search through September 2, 2026 found literature on general `f`-Ramsey host parameters, chromatic/circular chromatic Ramsey numbers, fractional chromatic graph products, and the newly introduced Kneser-Ramsey numbers, but did not find the displayed asymptotic bridge theorem stated explicitly. This is not an exhaustive priority proof. Before publication, search MathSciNet/zbMATH/Google Scholar by formula, terminology, cited-by chains, and contact the authors of the Kneser-Ramsey paper.

## 6. Research gates

The highest-value next steps are:

1. settle `KG(12,3)` with a reproducible SAT certificate and preferably Lean/LRAT verification;
2. settle or construct `KG(14,4)` and inspect the witness for recursive structure;
3. attack `rho_{3,3}=3` using Ramsey-minimal graphs, signal senders, graph products, or explicit fractional-colouring constructions;
4. determine whether the exact conjecture `R_r^{KG}(3,3)=3r+3` can be proved recursively;
5. independently verify novelty of the bridge theorem.
