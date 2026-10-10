# Red-team round 9 — PROVENANCE ONLY — 2026-09-13

**Status: COMPLETE** (00:28 → 00:50 IST). Both adversaries reported early. Created before the work so an interrupted round still
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

## Results — 2 ERROR-B, 3 denominator escapes, 5 silent repairs

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


## P2 — source type and denominator (in 00:43)

**Promise (a) HELD — 0 ERROR-B.** No spelling, case, whitespace, NFKC, null or
list variant of `full_text_source` is treated as verbatim; summary-only claims
stay out of PASS on factual, numeric and relational paths. This is the one
provenance promise that survived intact.

**R9P2-01 — duplicate `source_id` launders a summary to verbatim.** Verified by
me, 00:46: store `[S1 summary, S1 verbatim]` → **PASS / GROUNDED**; the same two
records reversed → **FAIL / UNGROUNDABLE**. The verdict depends on line order.
`load_store` has no duplicate check, contrary to the project's own "duplicate key
→ raise" convention. -02 (NFKC id collision `Ｓ1`/`S1`) and -03 (duplicate JSON
key inside one record) are the same class by two more entry paths; -04 (a
`WebFetch` record claiming `verbatim`, bad sha, null/wrong-type fields load and
certify) and -09 (the same URL fetched twice counts as two relational sources —
reachable by ordinary capture, no tampering) complete it.

**R9P2-05/06/07 — three new denominator escapes, same family as R8B-01/02.**
Verified -06 by me: `<!--` and `-->` inside 4-space indented code blocks delete
the visible prose between them → **PASS 100.0, 1 claim scored**, two uncited
fabrications on the page. Tilde fences (-05) and a backslash-escaped opener
(-07) do the same. P2 confirmed all three render as ordinary paragraphs under
`pandoc -f commonmark`.

## Disposition

| | |
|---|---|
| ERROR-B | **2** (R9P1-01 relational, R9P1-02 absence) — verified, tripwired |
| denominator escapes | **3** new — one verified and tripwired, -05/-07 recorded |
| silent repairs | **5** — -01 verified and tripwired |
| promise (a), summary never certified | **HELD** |
| fixed tonight | **none** — deliberately |

Tripwires: `tests/red_team_moat/test_moat_r9_provenance_open.py` — 4 strict
xfails + 1 control that keeps the relational tripwire honest.

## What round 9 means for the launch

Provenance is still the right thing to ship and still the spec's identity. But
"it cannot lose a round" is withdrawn. The launch-blocker list for provenance is
now concrete and short, and every item is fail-closed:

1. **Run the unresolved-citation check in `ground()` BEFORE the kind dispatch**
   — closes R9P1-01 and R9P1-02 together (fixing either checker alone leaves the
   other open).
2. **`load_store` raises on a duplicate normalised id, duplicate JSON keys,
   wrong types, and a `tool`/`full_text_source` mismatch** — closes R9P2-01…04.
3. **Replace the comment stripper's backtick-only code detection with real
   CommonMark block detection, or stop stripping comments** — closes
   R8B-01/02 and R9P2-05/06/07, one family.
4. **Spec §7.5** — absence claims fail open on an incomplete store (D-37).

Then round 10, provenance-only again, against the repaired tree.
