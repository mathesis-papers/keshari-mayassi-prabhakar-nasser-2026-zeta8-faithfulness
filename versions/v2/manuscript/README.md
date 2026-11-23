# A color-kernel extension of the zeta8 unfaithfulness theorem

Haobo Ma (ChronoAI Pte Ltd, Singapore), followed by Wenlin Zhang
(National University of Singapore; ChronoAI Pte Ltd, Singapore).
License: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Statements

Keshari–Mayassi–Prabhakar–Nasser's Question 4.3, arXiv:2605.13090v1,
page 17, has a negative answer on three strands with at least three virtual
colors. The element `[rho_1^0 rho_1^1,rho_1^0 rho_1^2]` has infinite order
and identity image for every allowed parameter of the eighth homogeneous
2-local family. Both associated subgroup restrictions and all eight families
have the same obstruction in this range.

Theorem 1 gives a stronger structural statement. The same-position virtual
subgroup is a free product of k involution groups. Its even subgroup F is free
on `x_beta=rho_1^0 rho_1^beta`. Its kernel consists exactly of even words h
whose exponent sums satisfy
`product_beta (y_beta/y_0)^e_beta(h) = 1`.
The intersection over all parameter choices is the derived subgroup F'.
For two colors this restriction is faithful exactly when `y_1/y_0` has infinite
multiplicative order; that statement is about the virtual subgroup, not the
whole multi-virtual twin group.

Corollary 4 supplies an infinite-order kernel element for Nasser–Ocampo's
multi-welded family on three strands with at least two colors, strengthening
their already established unfaithfulness result (arXiv:2605.31298v1,
Proposition 3.4). The note's coverage table separates this prior result from
the extensions and from representation classifications not covered here.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a TeX installation with `amsmath`, `amssymb`, `amsthm`,
`booktabs`, `tabularx`, `geometry`, `fontenc`, `lmodern` and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in `note.tex`; no BibTeX database is needed.

## Exact arithmetic and finite controls

Use Python 3.10 or later, without extra packages:

```sh
python3 verify.py > checked-identities.json
```

The deterministic result is `status: pass`. Exact integer Laurent-polynomial
arithmetic establishes the 20 defining matrix equalities at k=n=3 and the
commutator identity. An independent permutation calculation gives `[2,3,0,1]`.
The added welded calculation establishes 23 matrix equalities for three colors
and the identity image of `[s1 rho_1^0,s1 rho_1^1]`.

Finite controls cover quotient relations for 1–8 colors, powers 1–20, and
all 766 reduced color words of length at most 8 on three involutions
(511 even, 255 odd). They check the exponent-sum formula and the parity
obstruction. General ranges, subgroup embeddings, infinite order and the
complete kernel descriptions have the written proofs in `note.tex`.

The pinned Lean declaration and its helper declarations cover nonidentity,
identity image and noninjectivity at exactly three strands and three colors,
and the negation of a universal affirmative formulation of Question 4.3.
Their exact scope and pinned file link appear in the note; the structural,
all-color, all-family and welded extensions are written proofs.

## Contents

- `note.tex`: complete mathematical statements, proofs and bibliography.
- `note.pdf`: readable note, when supplied separately.
- `metadata.json`: creator order, affiliations, license and formal-source link.
- `verify.py`: dependency-free exact-arithmetic and finite-word checker.
- `checked-identities.json`: deterministic mathematical output.
