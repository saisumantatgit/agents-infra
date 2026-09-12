# Red-team round 9 — PROVENANCE ONLY — 2026-09-13

**Status: IN PROGRESS** (started 00:28 IST, adversaries time-boxed to 01:05,
hard close 01:20). Created before the work so an interrupted round still
delivers what it found.

## Scope — the closed class, deliberately

Round 9 attacks **only** the provenance half: does every certified claim cite a
source that was actually retrieved this session, captured verbatim, and is
every uncited assertion actually scored? **Entailment findings are OUT OF
SCOPE** and are discarded — rounds 3–8 already show that class is open.

Why run it before the product call: if provenance ships, the product stakes its
name on this class. A closed class is one a red team can actually exhaust.

| adversary | surface |
|---|---|
| P1 | citation-id resolution: fabricated, lookalike, unicode, zero-width, bracket/case/suffix forms, placement, mixed real+fabricated |
| P2 | source-type and denominator integrity: summary-vs-verbatim spoofing, empty/snippet text, malformed or duplicate store records, claims that escape citation detection or the scored denominator |

## Results — P1 in (00:38), P2 running

### CORRECTION FIRST: "provenance cannot lose a round" was FALSE

On 2026-09-12 I told Sai the provenance half was "done, never lost a red-team
round, cannot lose one — it's set membership, not language." **It had never
been attacked on its own.** The first round scoped to it found a fabricated
citation certified at PASS 100.0 on two independent paths. The claim was a
belief about the *logic* (set membership is closed) mistaken for a fact about
the *code* (whether every path actually performs the membership check). It is
yesterday's lesson again — a guard can be correct and unreached.

### R9P1-01 — ERROR-B — a fabricated citation on a RELATIONAL claim is ignored

Verified by me, 00:40:

```
draft:  Insulin resistance causes type 2 diabetes [S2][S3][S99].
store:  S2, S3 (real, verbatim). S99 does not exist.
result: PASS   GROUNDED   100.0
evidence_basis on the SAME row: "S99 is cited but was NEVER RETRIEVED this session."
```

`ground_relational` skips citations that do not resolve (`continue`). The report
certifies the claim and, in the same row, states that one of its citations was
never retrieved.

### R9P1-02 — ERROR-B — ABSENCE claims never check their citations at all

Verified by me, 00:41, on the corpus's certified q13 store:

```
[S99] We found no evidence of a safety recall affecting the X200 drone.
    -> PASS  ABSENCE_SUPPORTED  100.0
We found no evidence ... the X200 drone [source:fake-survey].
    -> PASS  ABSENCE_SUPPORTED  100.0
```

`check_absence` never looks at `claim.citations`. (A trailing `[S99]` happened to
FAIL in my first attempt only because the marker's text leaked into subject
matching — held by accident, not by a check.)

### R9P1-03 — the shared root

`ground()` dispatches RELATIONAL and ABSENCE to their own checkers **before** the
"any citation unresolved → UNVERIFIED_CITATION" branch, so the provenance check
exists and is never reached for two of the five claim kinds. **Fixing one
checker leaves the other open** — the fix belongs in `ground()`, ahead of the
dispatch. That fix is fail-closed (it can only refuse) and is small; it is
deliberately NOT applied tonight (hard stop, and every same-night moat patch in
this project's last two rounds has closed its fixture and not its class).

### R9P1-04 — misresolution

`load_store` accepts duplicate `source_id`s, including ids equal only after NFKC
(`S1` and `Ｓ1`); the later line silently wins and can yield PASS. That violates
the project's own fail-loud convention for the store.

### Held only by accident (P1's list — guard candidates)

`[S1][Ѕ99]` (Cyrillic S), zero-width/RTL inside ids, `[s99]`, `[ S99 ]`,
`[Source:x]` — refused because leftover marker characters break a match, not
because any check fires.

