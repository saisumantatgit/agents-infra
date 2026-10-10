# Citation-regex systemic fix (letter-suffixed IDs)

**Worktree:** `/Users/saisumanthbattepati/vibe-coding/Agents/agents-infra/.claude/worktrees/wf_f5845e10-a39-16` (branch `worktree-wf_f5845e10-a39-16`)
**Commit:** `9d14ff1` — NOT merged to main.
**Classification:** Systemic Fix (root cause in the shared `_CITATION_RE`, not a per-draft patch).

---

## 1. Finding & root-cause trace

The citation matcher was `\[(?:S\d+|source:[^\]]+)\]`. For a letter-suffixed marker like `[S12a]`, the `S\d+` branch consumes `S12`, then requires `]` but hits `a` — the whole match fails. The marker is therefore **invisible** to every consumer of `_CITATION_RE` (extraction, NON_CLAIM guard, numeric strip).

**Why it is an Error-B (unrecoverable) hole, not a cosmetic one.** In `ground()` (scripts/ground_check.py:1180-1185):
- no citations extracted → `if not claim.citations: return UNCITED`.
- a *recognized but unresolvable* citation → `resolve()` returns `None` → `UNVERIFIED_CITATION`.

`score_report` (line 1236, 1313) applies a **hard gate override**: `UNVERIFIED_CITATION` caps the gate at `NEEDS_WORK` regardless of score. `UNCITED` does **not** — it only lowers the score. Store keys are assigned digit-only (`next_source_id` → `S<n>`, capture_core.py:342-360), so a letter-suffixed marker can **never** resolve to a real source; it is always a fabricated/unresolvable citation.

Net: the old regex silently **downgraded a fabricated-source citation from the moat-blocking `UNVERIFIED_CITATION` to the non-blocking `UNCITED`**, letting an unsupported claim slip to gate `PASS`. Reproduced concretely in the red run below (`gate=PASS score=66.7`, `[S9a] → UNCITED`).

## 2. Decision on merit: WIDEN, not FAIL-LOUD

**Chosen: (a) WIDEN** the S-marker branch to `S\d+[A-Za-z]*`. Rationale (strictly dominant on the asymmetric invariant):

- **Reduces Error-B without introducing any.** A widened marker is extracted, resolved, and — because store keys are digit-only — returns `None` → `UNVERIFIED_CITATION` → hard cap. Widening only makes *more* brackets count as citations; a citation still only grounds on an exact store-key match, so it can never manufacture a PASS. Error-B is monotonically reduced.
- **Does not raise Error-A.** Genuinely grounded claims already use digit-only markers that matched before and still match identically (zero-letter suffix). No previously-passing claim changes verdict (verified: 326/326 pre-existing tests green on the widened source).
- **Why not FAIL-LOUD (b):** (i) it produces a *crash*, not a closed-taxonomy verdict — no gate output at all; (ii) it massively raises Error-A — any legitimate draft using sub-reference notation (`[S12a]`, `[S12b]`) aborts the whole gate; (iii) the "fail loud, never fallback" convention is scoped to the **audit-evidence STORE** (malformed JSONL), not to untrusted model-produced **draft** text — applying store-integrity semantics to draft parsing is a category error; (iv) it yields **no** incremental moat protection over WIDEN, which already routes the fabrication to the existing hard-cap verdict.

Taxonomy: unchanged/closed — the fix reuses the existing `UNVERIFIED_CITATION` verdict. No new verdict invented. No LLM added to the grounding path. NFKC normalization boundary untouched (`classify` still `_nfkc`-normalizes before the regex).

## 3. Red-first evidence (INS-005)

New test `tests/test_citation_regex_letter_suffix.py` run against **pre-fix** `ground_check.py` — all three FAIL:

```
FAILED tests/test_citation_regex_letter_suffix.py::test_letter_suffixed_marker_is_extracted_as_citation
FAILED tests/test_citation_regex_letter_suffix.py::test_letter_suffixed_unresolvable_citation_is_unverified_not_uncited
FAILED tests/test_citation_regex_letter_suffix.py::test_fabricated_letter_suffixed_citation_cannot_reach_pass

E  AssertionError: a draft with a fabricated letter-suffixed citation must NOT reach PASS;
   gate=PASS score=66.7 per_claim=[
     {... 'verdict': 'GROUNDED'},
     {... 'verdict': 'GROUNDED'},
     {'text': 'Our platform holds a dominant global market position [S9a].',
      'kind': 'NUMERIC', 'verdict': 'UNCITED'}]
E  assert 'PASS' != 'PASS'
3 failed in 0.61s
```

The moat test proves the release-blocker: pre-fix, the fabricated `[S9a]` reads `UNCITED` and the draft reaches `gate=PASS`.

## 4. Green after fix

New test post-fix:
```
3 passed in 0.11s
```

Full suite (final):
```
329 passed in 12.65s
```
(326 pre-existing + 3 new. NOTE: task cited a "334" baseline and CLAUDE.md "327"; artifact truth on this branch, verified by `git stash`-ing the source edit and re-collecting, is **326 pre-existing tests, all green on both pre-fix and post-fix source** — the widening regresses zero existing tests. The `syntok` runtime dep had to be provisioned via `uv sync --extra dev` before the suite could run; the 39 initial `ModuleNotFoundError` failures were environmental, not from this change.)

## 5. Unified diff (source)

```diff
@@ -241,8 +241,17 @@ def decompose(draft: str) -> list[Claim]:
 
 import re as _re
 
-# Citation pattern: [S1], [S12], [source:some-text]
-_CITATION_RE = _re.compile(r"\[(?:S\d+|source:[^\]]+)\]")
+# Citation pattern: [S1], [S12], [S12a] (letter-suffixed sub-reference),
+# [source:some-text].
+#
+# MOAT: the S-marker branch accepts an optional letter suffix (``[S12a]``).
+# Store keys are assigned as ``S<n>`` (digits only) by next_source_id, so a
+# letter-suffixed marker never resolves to a real source — it is always an
+# unresolvable citation. Widening the pattern routes such a marker through
+# resolve() -> UNVERIFIED_CITATION (the hard-cap verdict) instead of leaving it
+# unmatched, where the claim silently read as UNCITED and bypassed the gate's
+# UNVERIFIED_CITATION override (an Error-B / fabrication-reaching-PASS hole).
+_CITATION_RE = _re.compile(r"\[(?:S\d+[A-Za-z]*|source:[^\]]+)\]")
```

Test file `tests/test_citation_regex_letter_suffix.py` (+144 lines) — 3 tests: extraction, verdict (`UNVERIFIED_CITATION` not `UNCITED`), and gate-level moat (fabricated letter-suffixed citation cannot reach PASS).

## 6. Load-bearing assumption (surfaced)

The fix's correctness rests on **store keys being digit-only** (`next_source_id` → `S<n>`). If a future capture path ever assigned letter-suffixed source_ids (e.g. `S12a`), a widened marker `[S12a]` would then *resolve* and could ground — which is still correct behavior, but the "letter-suffixed ⇒ always unresolvable" reasoning would no longer hold. Any change to source-id assignment must re-examine this. Verified today: `next_source_id` emits only `S<n>`.

## 7. Follow-up (calibration hygiene, not a blocker)

Per CLAUDE.md Failure-Mode 9, `_CITATION_RE` feeds `classify`. Classification of letter-suffixed drafts changed (they now extract a citation instead of leaking a bracket digit as numeric). The calibration set `labeling.csv` uses digit-only markers, so CR-001 `lex_tau=0.71` is unaffected in practice, but a re-run + fresh CR is the disciplined next step if any gold label uses a letter-suffixed marker. Carried as a follow-up, not done here (out of task scope; no gold-label uses letter suffixes today).
