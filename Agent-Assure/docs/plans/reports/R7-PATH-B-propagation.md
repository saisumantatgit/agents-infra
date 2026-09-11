# R7 PATH B — Citation propagation red team

Status: IN PROGRESS (skeleton written at start; appended as runs complete)

Target: `_propagate_sentence_citation` (~L203), `_propagate_across_semicolon` (~L238),
`_conjunction_split` (~L173) in `scripts/ground_check.py`.

Hypothesis under test: the ";" discriminator is an author-controlled surface property,
so a fabricated clause can inherit a genuine clause's citation and then ground against it.

## Findings

(appended below)

## Families tried and unbroken

(appended below)
