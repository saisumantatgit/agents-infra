# Phase 1a — Final Whole-Branch Review

**Artifact:** Agent-Assure deterministic claim-grounding engine
**Scope:** 16 commits, `d825fb3..1940fb6`; `scripts/ground_check.py` (1306 lines); full test suite 129 passing.
**Reviewer role:** Final whole-branch gate — cross-cutting concerns the per-task reviews could not see + triage of deferred Minor findings.
**Date:** 2026-06-27

---

## Verdict: READY-WITH-FIXES

The engine is internally consistent, deterministic, and the anti-gaming invariant on the *denominator* (no verdict removed from S) holds exactly as documented. The suite passes (129/129, 0.38s). One **Important** cross-cutting finding (verbless-fabrication escape via the NON_CLAIM classifier × empty-denominator interaction) and two **Minor** cross-task duplications were discovered that the per-task gates could not have seen. None is a hard merge blocker given the documented spec and provisional-calibration posture, but the duplication fixes and one test-hygiene fix should land before merge.

Evidence: `uv run pytest -q` → `129 passed in 0.38s`.

---

## 1. Cross-cutting checks

### 1.1 Verdict-taxonomy consistency end-to-end — PASS

All 9 `Verdict` members are both produced and handled:

| Verdict | Produced in | Scored in `score_report` |
|---|---|---|
| `GROUNDED` | `ground` (NON_CLAIM short-circuit; T1/T2 hit), `ground_relational` | numerator |
| `ABSENCE_SUPPORTED` | `check_absence` | numerator |
| `UNGROUNDED` | `ground` (default tail) | denominator-only (retained) |
| `UNCITED` | `ground` (no citations) | denominator-only |
| `UNVERIFIED_CITATION` | `ground` (unresolved citation) | denominator-only + **hard override** → caps gate at NEEDS_WORK |
| `UNVERIFIED_NUMBER` | `ground` (NUMERIC + numeric_ok False) | denominator-only |
| `UNVERIFIED_ABSENCE` | `check_absence` | denominator-only |
| `UNVERIFIED_RELATION` | `ground_relational` | denominator-only |
| `UNGROUNDABLE` | `ground` (falsy text / no verbatim) | denominator-only |

No orphan verdict; no verdict produced but missing from §4.5 scoring. `_NUMERATOR_VERDICTS = {GROUNDED, ABSENCE_SUPPORTED}`; every other scored verdict correctly falls into the retained appendix. The denominator (`scored_count`) counts every non-NON_CLAIM claim regardless of verdict — the anti-gaming invariant is intact (verified by direct trace, lines 1198–1223).

### 1.2 Cross-task drift / duplicate helpers — TWO DUPLICATIONS FOUND (Minor)

These are exactly the class of finding the per-task reviews could not see — each helper is locally correct; the duplication is only visible across tasks.

**(a) Two verb detectors.** `_has_verb_like_token(tokens: list[str])` (line 124, decompose task) and `_has_finite_verb(text: str)` (line 301, classify task) implement *identical* auxiliary-membership + capitalized-skip + suffix logic. The `_has_finite_verb` docstring even states "Mirrors `_has_verb_like_token`." They differ only in input type (`list[str]` vs `str`, the latter splitting on `\s+` internally) and share `_AUXILIARIES`, `_VERB_SUFFIXES`, `_VERB_SUFFIX_MIN_LEN`. This is genuine logic duplication: a future change to verb heuristics must be made in two places or the two paths silently diverge. **Recommend** collapsing to one core: `_has_finite_verb` should call `_has_verb_like_token(text.split())` (or both delegate to a shared `_token_is_verb_like(tok)`), preserving identical behaviour.

**(b) Relational triggers encoded twice.** `_RELATIONAL_TRIGGERS` (tuple, line 250 — used by `extract_arguments`) and `_RELATIONAL_RE` (regex, line 270 — used by `classify`) list the **same 10 triggers** in two formats. Verified in sync today, but classification and argument-extraction will drift if one is edited (e.g. add a trigger to the regex → claims classify RELATIONAL but `extract_arguments` returns None → silent UNVERIFIED_RELATION). **Recommend** deriving the regex from the tuple: `_RELATIONAL_RE = _re.compile(r"\b(?:" + "|".join(_re.escape(t) for t in _RELATIONAL_TRIGGERS) + r")\b", _re.IGNORECASE)`. (Note: the current regex uses `\b` boundaries; `due to`/`because of` end in vowel+consonant so `\b` is fine, but escaping-from-tuple keeps them aligned for free.)

**Not duplications (verified):** `_NUMERIC_RE` (claim side) vs `_SOURCE_NUMERIC_RE` (source side) are intentionally different — the source pattern adds `(?!\d)` lookahead and `percent` to avoid substring mis-parses in prose. Single `_nfkc` wrapper, single `_tokenize`, single `_split_sentences` — no shadowing. `_HEAD_NOUN_STOPS` is reused (not re-defined) by `extract_arguments`. Good.

### 1.3 Module size — SPLIT RECOMMENDED (advisory, not a blocker)

At 1306 lines the file is past the plan's "~600 line" split trigger and is doing the entire pipeline. It is still navigable (clear section banners, one concern per band), so this is a recommendation. Suggested package layout, by existing section boundaries (zero logic change, pure move):

```
ground_check/
  __init__.py        # re-export public API: load_store, decompose, classify,
                     #   ground, score_report, main  (keeps import paths stable)
  models.py          # Verdict, ClaimKind, RetrievedSource, Claim, _nfkc, load_store
  decompose.py       # _AUXILIARIES, verb detection, syntok seg, _conjunction_split, decompose
  classify.py        # regexes, _is_non_claim, classify   (imports verb helper from decompose/text_utils)
  tiers.py           # _tokenize, _strip_citations, _content_words, _f1, T1, T2
  numeric.py         # _parse_numeric_token, _extract_source_pairs, numeric_ok
  absence.py         # _extract_absence_subject, check_absence
  relational.py      # extract_arguments, window_supports, ground_relational, resolve
  score.py           # ground, _session_queries, score_report
  cli.py             # main
```
Pull the shared verb/tokenizer/NFKC helpers into a small `text_utils.py` to resolve §1.2(a) at the same time. Tests import the public names, so re-exporting from `__init__.py` keeps the 129-test suite green without edits. **Do this in Phase 1b's opening commit, not as a merge blocker for 1a** — splitting now risks churn against the in-flight capture-hook work.

### 1.4 Determinism holistically — PASS

No residual nondeterminism reaches output. `ground_relational` builds `a_supported_in`/`b_supported_in` as **sets**, but iterates them only in a nested loop that early-returns a bool on the first cross-source pair — set order cannot leak into the result. `_session_queries` returns store-insertion order (dict preserves insertion order; `load_store` inserts in file order) → deterministic list. `numeric_ok` uses `any()` over a list. `score_report` emits `per_claim` in input order and `retained_appendix` in claim order. CLI serializes with `sort_keys=True` for both JSON and YAML. No `set`/`dict` iteration feeds an ordered output anywhere. Top-level is pure (syntok imported lazily inside `_iter_raw_sentences`); no random, wall-clock, or network.

### 1.5 Forward-compat contract for the capture hook (Phase 1b) — NAMED

The engine consumes `RetrievedSource` and assumes the hook guarantees these invariants. **The hook MUST honor this contract:**

1. **`source_id` uniqueness & normalization.** `load_store` keys the dict on `_nfkc(source_id)`; a later duplicate `source_id` **silently overwrites** the earlier source (line 104). The hook must emit unique source_ids or accept last-write-wins.
2. **`full_text_source == "verbatim"` is the load-bearing literal.** `ground` (line 1116) and `ground_relational` (line 1014) filter on the exact string `"verbatim"`. Any other value (`"haiku_summary"`, snippet, typo) is treated as non-verbatim → `UNGROUNDABLE`. The hook must set this field to the exact string `"verbatim"` for full-text captures.
3. **`text` non-empty ⇔ groundable.** `ground` maps falsy `text` → `UNGROUNDABLE` (line 1113). The hook must populate `text` with the *verbatim* source content for any source it labels `"verbatim"` (the engine trusts this — there is no re-fetch/re-hash verification of `content_sha256` in Phase 1a).
4. **`query_provenance` is the absence-search ledger.** `_session_queries` → `check_absence` counts DISTINCT `query_provenance` substrings against the absence subject. The hook must record the actual search/fetch query string per source; if it stuffs a placeholder (constant string), absence verification collapses (distinct count = 1 → never reaches `min_absence_searches=2`).
5. **All required fields present.** `load_store` does `obj["fetched_at"]`, `obj["tool"]`, `obj["content_sha256"]`, `obj["text"]`, `obj["full_text_source"]`, `obj["captured_via"]`, `obj["query_provenance"]`, `obj["source_id"]` as **required keys** (only `url`/`file_path` use `.get`). A capture record missing any of these raises `KeyError` at load — the hook's JSONL schema must be a superset of these eight keys.

### 1.6 Anti-gaming integrity holistically — ONE IMPORTANT GAP

The denominator invariant (no verdict shrinks S) is solid. But there is a way to make the **gate report PASS while the draft contains fabricated, unsupported assertions** — through the *classifier*, not the scorer.

**Exploit (verified, reproduced):**
```
Draft:
  The fastest database on Earth.
  A 99% market share for our product.
  Total dominance over every competitor.

Result: gate=PASS  grounding_score=100.0  scored_claims=0
```
Every line is a verbless noun phrase. `_has_finite_verb` finds no auxiliary and no ≥4-char suffix-matching lowercase token, so `_is_non_claim` → True → `classify` assigns `NON_CLAIM` → `ground` short-circuits to `GROUNDED` → `score_report` excludes it from the denominator. With all claims excluded, `scored_count == 0`, which is the documented "vacuous pass" → `grounding_score=100.0, gate=PASS`.

**Why this is the seam between two tasks:** Task 2's classifier rule "no finite verb → NON_CLAIM" and Task 9's "NON_CLAIM excluded from denominator + empty-denominator → PASS" are each individually defensible and individually documented (README line 79; the empty-S choice at lines 1168–1172). The defect lives in their *composition*: a heuristic meant to drop section headers and transition phrases also drops any fabricated assertion an adversary phrases without a finite verb, and the empty-denominator branch then reports the strongest possible signal (`PASS`, `100.0`) for a draft of pure fabrication.

**Severity: Important, not Critical**, because: (a) the verbless→NON_CLAIM rule and the denominator exclusion are both documented spec, not bugs; (b) the `scored_claims` field exposes the vacuous pass — a conformant caller that treats `scored_claims == 0` as "no claims verified, do not trust PASS" is protected; (c) the heuristic is provisional pending calibration (§12.5). It is nonetheless a real hole: the *gate string itself* says PASS, and any downstream that keys on `gate == "PASS"` alone (as the CLI exit code does — `exit(0)` on PASS, line 1302) is gameable.

**Recommended hardening (carry to Phase 1b / calibration, not a 1a blocker):**
- Make the empty-denominator gate `NEEDS_WORK` (or a distinct `VACUOUS` gate), not `PASS`, so the CLI exit code and the gate string both refuse to greenlight a zero-claim draft. This is a one-line change at lines 1225–1235 and is the highest-leverage fix.
- Alternatively/additionally, tighten `_is_non_claim`: a noun phrase containing a numeric token or a superlative should not be silently dropped as NON_CLAIM. (Calibration territory — log as systemic follow-up.)

Other gaming vectors tested and **safe**: fabricated citations cannot shrink the denominator (UNVERIFIED_CITATION stays in S *and* triggers the hard override → caps at NEEDS_WORK); a real header `# Foo bar baz` with trailing clause is split by syntok so the post-`#` clause is still scored; numeric unit-confusion (`25%` vs `25`) is blocked by the percent/absolute unit split in `_parse_numeric_token`.

**Classification of the §1.6 finding:** This is flagged as a **Systemic** issue (the empty-denominator-PASS composition), with a concrete plan above. It is carried forward as a Phase-1b/calibration follow-up, not silently band-aided.

---

## 2. Triage of deferred Minor findings

| # | Finding | Disposition | Rationale |
|---|---|---|---|
| 1 | `resolve()` returns None (not raise) on malformed unclosed-bracket `[S1` | **DEFER** | `None` flows to `ground` → `UNVERIFIED_CITATION` (fail-closed, conservative). Raising would crash the whole report on one bad marker. Current behaviour is safer and consistent with the fail-closed posture. Verified: `resolve("[S1", {})` → `None`. |
| 2 | Inline imports in `main()`; hardcoded `grounding-report.yaml` output path | **DEFER** | Inline imports keep module top-level pure (yaml/argparse only needed at CLI). Hardcoded path is a CLI ergonomics nit; add `--out` in Phase 1b. Neither affects engine correctness. |
| 3 | `_session_queries` docstring wording | **DEFER** | Cosmetic. |
| 4 | Test-helper pre-sets `kind` before `classify` (`test_classify.py:11`) | **DEFER** | Helper sets a placeholder `kind=FACTUAL` that `classify` overwrites; it does not weaken any assertion (classify recomputes kind from text). Not a tautology. |
| 5 | Unused `import pytest` | **FIX-BEFORE-MERGE** | **Scope correction:** the prompt said "one test file"; it is actually **four** — `test_relational.py:17`, `test_tiers.py:10`, `test_numeric.py:15`, `test_absence.py:15` (0 `pytest.` usages each; `test_golden_matrix.py` legitimately uses it 8×). Trivial dead imports but they will trip a `ruff`/`flake8 F401` gate and are a one-line-each delete. Clean the four before merge. |
| 6 | Double-NFKC on claim text in absence path | **DEFER** | `check_absence` does `_nfkc(claim.text)` then `_extract_absence_subject` re-`_nfkc`s. NFKC is idempotent → harmless redundancy. Remove the outer call opportunistically during any absence-path edit. |
| 7 | `import re` (`import re as _re`) placed mid-file (line 242) | **DEFER** | Unconventional but works; the module banner structure motivates it. Moves to top in the §1.3 split. |
| 8 | `numeric_tokens` populated even on NON_CLAIM | **DEFER** | Verified harmless: NON_CLAIM short-circuits to GROUNDED in `ground` before any numeric path consumes the field. Cosmetic. |
| 9 | Misc test doc-comment imprecisions | **DEFER** | Cosmetic. Includes the `t1_verbatim` docstring overstatement ("window size from min_quote_len up to n" — code only slides min_quote_len windows, which is *correct and sufficient*; any longer contiguous match contains a min_quote_len one). Doc nit, not a bug. |
| 10 | Empty-draft determinism test compares `[] == []` (`test_golden_matrix.py:340`) | **DEFER** | Weak (asserts `decompose("") == decompose("")` and `"   "` likewise — both sides `[]`, near-tautological) but not *false*. It does exercise the empty/whitespace guard. Strengthen to also assert `decompose("") == []` (the property, not self-equality) when convenient — not worth blocking merge. |
| 11 | Test-coverage gaps: absence stop-word-only subject + inline-trigger branch | **DEFER (note as follow-up)** | Confirmed: `test_absence.py` covers ≥2/1/0 query matches + NFKC subject, but has no test for (a) `_extract_absence_subject` returning `""` on a stop-word-only subject → `UNVERIFIED_ABSENCE`, nor (b) the inline-trigger `else`-branch (line 788, no leading trigger but trigger appears mid-sentence). Both are reachable, untested branches. Not a correctness defect today; add to the Phase-1b test backlog so calibration changes don't silently break them. |

**FIX-BEFORE-MERGE subset:** Finding #5 only (remove four unused `import pytest`).

---

## 3. Things confirmed NOT defects (per the intentional-list)

`extract_arguments` brittleness on complex subjects (§12.11), F1-vs-recall metric choice (§12.5), absence verifies "we searched" not "found nothing" (Phase-1a interface limit), and the provisional constants `min_quote_len=8` / `lex_tau=0.65` / `threshold=90` — all observed in code, all left untouched as documented open questions.

---

## 4. Merge recommendation

**READY-WITH-FIXES.** Land the one FIX-BEFORE-MERGE (remove 4 unused `import pytest`), re-run `uv run pytest -q` to reconfirm 129 passing, then merge. Open three follow-ups against Phase 1b:

1. **(Systemic, highest leverage)** Empty-denominator gate should be `NEEDS_WORK`/`VACUOUS`, not `PASS` — closes the verbless-fabrication exploit at the gate/exit-code level (§1.6).
2. **(Maintainability)** Collapse the two verb detectors and derive `_RELATIONAL_RE` from `_RELATIONAL_TRIGGERS` (§1.2); do the module split (§1.3) in the same opening commit.
3. **(Coverage)** Add the absence stop-word-only-subject and inline-trigger branch tests, and strengthen the empty-draft determinism assertion (§2 #10/#11).
