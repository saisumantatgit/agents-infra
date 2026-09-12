# Ratification Register — autonomous session 2026-08-30

**Authority:** Sai's standing order (2026-08-30): "don't stall at a blocker — first
principles, platform robustness, UX to the end user; a blocker on one item isn't a
blocker on all; every autonomous call goes in the ratification register with its
undo; the park list holds — anything outward-facing."
**Budget sanctioned:** 10M tokens, objective = take Agent-Assure calibration to a close.
**Status column:** PENDING → DONE (commit) / DROPPED (with reason). Sai ratifies or
reverses each row; every row carries its one-step undo.

| # | Decision (autonomous call) | Basis (attackable why) | Undo | Status |
|---|---|---|---|---|
| D-01 | **Park-list interpretation:** "applying bindings" and "gross_wages adjudication" have zero artifacts in this repo (grep: no hits; both live in iVal 2.0). Read the park list here as its general clause: *anything outward-facing parks* (GitHub release, marketplace, client-visible). Intra-portfolio HQ correspondence is the normal ADR-028 rail, not outward-facing. | The named items are not addressable from this repo; the general clause is. | n/a (interpretation — flag if wrong) | DONE |
| D-02 | **Gold labels stay Sai's.** No self-labeling, no calibration on candidate labels, no CR-002. Proceed on the Alpha plan's own tripwire (α1 item >7 days old → ship-flagged path: build everything else, hold α5). | CLAUDE.md failure-mode 5 + Escalation 2 are standing gates the standing order does not name; the Alpha plan pre-authorized exactly this path. | n/a | DONE |
| D-03 | **AA-MOAT-007 fixed:** narrow the verbless NON_CLAIM exemption — a non-header, non-transition verbless fragment with ≥6 content tokens is scored (UNCITED if uncited). Headers/short labels stay NON_CLAIM. | First principles: NON_CLAIM exists to skip *structure*, not *assertions*; "no finite verb" is a gameable proxy for structure. Fail-closed direction only (claims can only move away from PASS). Error-A bounded to long verbless body prose — rare in genuine drafts; corpus diff adjudicated. | revert commit (single commit, tagged AA-MOAT-007 → OI-MOAT-07) | DONE `ce43259` |
| D-04 | **AA-MOAT-003 fixed:** T1 residual-coverage check — a verbatim span grounds a claim only if the claim's residual content tokens (outside the span) are covered by the source window; substantial uncovered residual → falls through to T2/UNGROUNDED. | The bug is T1 certifying words it never checked. Fail-closed; T3/NLI can later recover the Error-A per ADR-004 §3. Corpus diff adjudicated row-by-row. | revert commit | DONE `8cdd21b` |
| D-05 | **AA-MOAT-005 fixed:** relational grounding requires predicate support — the relation's predicate family must be supported in a window that also carries both endpoints (single- or cross-source per rule), not endpoint-presence in two disjoint sources. | The current rule certifies a relation no source asserts; corpus rows q25/q26/q48 are human-labeled violation and the gate grounds them — the labels themselves demand this fix. Fail-closed. | revert commit | DONE `c16e486` |
| D-06 | **OI-CAL-01 resolved: deploy lex_tau=0.71** as the running default, exposed as one constant + `--lex-tau` CLI flag (thresholds-as-data). | CR-001 is the only evidence in existence; measured in-sample this session: 0.65 and 0.71 predict **identically** on all 12 labeled claims (A=0.000/B=0.143 across the whole 0.60–0.71 band) — the deployment changes no measured prediction and honors the selector's tie-break-stricter principle. CR-002 supersedes when labels go gold. | set `_LEX_TAU_DEFAULT` back to 0.65 (one line) | DONE `203ed0a` |
| D-07 | **OI-ENV-01 fixed:** move pytest to `[dependency-groups] dev` (uv syncs it by default) + conftest fail-loud guard when pytest resolves outside the project `.venv`. **DISCLOSED SIDE EFFECT (found by my own three-hat audit, not by a test):** `install.sh` runs bare `uv sync`, so this now provisions pytest for **END USERS**, not just developers — I changed what the installer does without editing it, which is Escalation #4 in substance. Verified directly against `.venv/bin/python`. Judged correct on merit (the OI-ENV-01 trap WAS a first-time user running the suite; a user who can verify their own install is the point; cost ~5 pure-Python packages) but it is Sai's call. `install.sh` line 28's comment had become factually false and was corrected — **comment only, zero behaviour change**. | Platform robustness + first-time UX: ~46 bogus failures on a fresh checkout is an onboarding trap. | revert commit; **or**, to keep the fix but ship a leaner end-user env, change `install.sh`'s `uv sync` to `uv sync --no-dev` (one line) | DONE `c0ae710` + disclosure |
| D-08 | **ADR-039 compliance:** AA-MOAT-* → OI-MOAT-{NN} rename + register restructured to the ADR-039 template; HQ ack actioned, inbox item → done. | HQ-mandated ("on you, at your convenience"), mechanical. | revert commit | DONE `dec8a25` |
| D-09 | **cpc-book ask answered** (ack to HQ, Q1–Q3) + batch-label ingestion built: per-batch label files with provenance (labeler, batch_id, domain), accumulate-then-derive, per-domain sweep support. | 6-weeks-unanswered `ack_required` item; the binding labeler constraint (5–10/batch) requires exactly this ingestion shape; intra-portfolio per D-01. | ack is correspondence (send follow-up); code: revert commit | DONE `5ab4979` + HQ inbox `2c19ede` |
| D-10 | ~~Phase 2b NLI tier: rebase reference build, Option 4 semantics, DEFAULT-OFF~~ | **DROPPED this session** — Q1–Q4 of ADR-004 are genuine Sai rulings (moat *definition*, "ZERO LLM calls" slogan amendment); a default-off build would still pre-commit the semantics. D-03/D-04/D-05 close the Error-B holes deterministically, which removes 2b's urgency; its value is now Error-A recovery only. | n/a | DROPPED |
| D-13 | **Error-A harness built** (`tests/honest_drafts/`) — 4 honest drafts must PASS, 2 known false alarms strict-xfail against OI-T2-01. | Four adversarial rounds asked one question (*can a fabrication PASS?*). A red-teamer cannot surface a wrongful FAIL **by construction**, so the false-alarm side had never been measured. Sweeping it found OI-T2-01 in minutes: a **verbatim** 7-token sentence quote reads UNGROUNDED. Verified pre-existing (fails at 0.65 too). | revert commit | DONE `5769d79` |
| D-14 | **OI-T2-01 recorded, not fixed.** Fix options named (short-span T1 when the claim IS the span / claim-recall instead of F1 / the T3 tier). | All three move the Error-A/Error-B trade-off ⇒ Escalation #1 ⇒ Sai's, same test that kept OI-DEC-01 his. | n/a (record only) | DONE `5a8b575` |
| D-11 | **Red-team round 3** dispatched against the new fixes (fresh adversary, same discipline as rounds 1–2); findings recorded as OIs, any wrongful PASS fixed or xfail-tripwired before close. | "A fix to the moat gets red-teamed too" is a standing convention, not a choice. | n/a (evidence artifact) | DONE `852a169` — R3 found **17 wrongful PASSes / 5 mechanisms**, 2 of them evasions of the same day's fixes; all closed as OI-MOAT-11..15. **R4 (41 drafts) found 25 more over 4 mechanisms — again all evasions of the same day's fixes** → OI-MOAT-16..19 closed, **OI-MOAT-20 left OPEN with a strict-xfail tripwire** (verb-final header; closing it deterministically needs either Error-A on every multi-word heading or a POS tagger, which is ADR-004 Q3 territory). **R5 (50 drafts) found 23 more over 4 mechanisms** → OI-MOAT-22/-23/-24 closed; **OI-MOAT-21 ESCALATED** (T2 is not sound: it is an F1 ratio over attacker-controlled length, PASSes at lex_tau 0.99; demoting it changes the gate's meaning and invalidates the calibration ⇒ Escalation #1+#3). **Convergence:** drafts/mechanism 7.4→10.3→12.5, every R4 fix attacked directly HELD (a first), but surviving attacks are MORE natural, not less. R5's verdict: *the process is converging; the T2 design is not.* |
| D-12 | **OI-DEC-01/OI-NUM-02 hygiene** (decomposer citation detachment, trailing-space numeric token) — fixed if red-first tests land cleanly inside budget; else left OPEN with evidence. | Fail-safe-direction UX fixes; zero moat interaction. | revert commit | OI-NUM-02 DONE `9ddf4f1`; **OI-DEC-01 ESCALATED, not fixed** (`64f6644`) — its fix is the first PASS-*enabling* change in the cohort, so Escalation #1 applies and it is Sai's call. |

---

## Addendum — 2026-09-03 (session `d2b27b1f`, overnight under standing order)

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-15 | **OI-ABS-01 fixed: an absence claim's SCOPE must be searched, not just its subject.** A query counts toward the two-search minimum only if it also addresses the trailing scope phrase (in/within/across/throughout/among/under/outside/beyond). | Fail-closed — it can only REMOVE queries from the count, so no absence can move toward ABSENCE_SUPPORTED. Inside the ratified Escalation-#1 reading (reversibility, not importance). Closes the last two Error-B rows in the corpus (q14, q37, both gold=violation): Error-B 0.074 → 0.000 with Error-A unchanged at 0.320 — a strict improvement, not a trade. Corpus diff: exactly 2 rows moved, both correctly. CR-004. | revert commit (single commit) | DONE |
| D-16 | **Corrected `test_specific_subject_supported_when_corroborated`**, which asserted `ABSENCE_SUPPORTED` for corpus row q37 — a row Sai gold-labeled **violation**. Split into a scope-refusal test and a proper Error-A guard that keeps the stemming property. | The test contradicted a ratified human label and had been green for weeks. It was named "Error-A guard", which is why it was never questioned — a test named for a property must assert that property (INS-005). Not a judgement call: the gold label is authoritative over a test's expectation. | revert commit | DONE |

**Note for the ratifier.** D-15 is a moat change made while Sai slept, under the
standing order. It is fail-closed and its full evidence is in CR-004, including
the reason "Error-B = 0.000" must NOT be quoted as zero: on 0/27 the 95% upper
bound on the true rate is ~10.5%, and every red-team round so far has found
violation classes the corpus does not contain.

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-17 | **OI-DEC-03: HTML comments are stripped before decomposition.** Only WELL-FORMED `<!-- ... -->` pairs; an unterminated `<!--` is left in place. | An authoring comment is not prose — not rendered, not published, not read. The gate was scoring a writer's own TODO notes and store paths as ungrounded claims. Denominator-reducing in form, so flagged for ratification; but a comment cannot be a claim in the document the reader receives under any reading. The well-formed-only restriction is the load-bearing half: stripping to end-of-file would let one stray `<!--` silently delete every claim below it. | revert commit | DONE |
| D-18 | **OI-DEC-04: the conjunction splitter strips its own trailing punctuation.** | Purely cosmetic — no verdict moves, punctuation is dropped before tokenizing. But `"The written statement is in,"` is a COMPLETE clause wearing the splitter's comma, and it is what the user reads in the report. The gate should quote the writer, not the splitter. | revert commit | DONE |
| D-19 | **OI-DEC-05: a span with ZERO content words is NON_CLAIM.** Numerics and citations override, so `"99% [S9]"` stays scored. | `---`, `***`, `\|---\|---\|` were classified FACTUAL and flagged UNGROUNDED. The rule is ZERO, not "few": round 3 defeated a `>=6 content tokens` floor with a five-token fabrication and round 4 defeated its capitalisation replacement with the Shift key. Zero is not a line to step under — a span with no content words has no subject and no predicate, so there is nothing to assert and nothing to smuggle. | revert commit | DONE |
| D-20 | **`_content_words` now requires at least one alphanumeric character.** | The tokenizer is `\w+`, and Python's `\w` includes UNDERSCORE — so `___` tokenized as the content word `___`, making an underscore horizontal rule a scored claim while the identical `---` was ignored. Whether a rule is drawn with dashes or underscores is not a fact about the document. Fail-closed in the tiers: a token nobody can match was inflating both sides of an F1. | revert commit | DONE |

**Measurement-neutral:** the calibration corpus regenerated BYTE-IDENTICAL after
all four, so CR-004's rates stand unchanged and no new CR is due (ADR-025).

**Real-prose effect** (10 cpc-book chapters, 1,121 scored claims): mechanical
decomposition artifacts fell from **31.3% to 3.2%**. What remains is
**9.4% rhetorical questions — J-15/OI-DEC-02, still Sai's** because exempting
them is PASS-enabling — and a 9.7% "short sentence" bucket that is mostly
genuine claims my crude <4-content-token metric miscounts, not a defect.

---

## Addendum — 2026-09-12 overnight run (session `d2b27b1f`)

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-21 | **The intra-rater sample is STRATIFIED, not random: all 4 divergent rows (q14, q16, q37, q49) + 16 random from the other 48.** Seed 20260912. | `init_labels.py` seeds every row with Claude's `candidate_verdict`; the ratifier corrects it. On 48 of 52 rows gold == candidate, so on those rows *"Sai agrees with himself"* and *"Sai agrees with the machine"* are the same observation. Only the 4 overruled rows separate them. The first, plain-random draw of 20 contained **none** of the four (p = 0.133 — it rolled that 13%), so the instrument would have been blind to the anchoring branch it exists to detect. This is the standing trap again: the filter and the measurement were the same operation. | Delete `calibration/intra-rater/`; nothing else reads it. No moat code touched. | DONE |
| D-22 | **Nothing is pooled across the two strata.** κ is computed on the 16 random rows alone; the 4 probe rows are printed individually with the machine's original call beside each. | The enrichment is deliberate, so any pooled statistic is biased by construction. Reporting one number over 20 would be a fabricated operating point — the exact failure CR-003 records for `tier_sensitive`. Verified by dry-run: an anchored respondent scores **κ = +1.000** on the random stratum, so a pooled figure would have certified "corpus sound" on the one result that means the corpus is not ground truth at all. | n/a — a reporting rule, not a code path | DONE |
| D-23 | **`score.py` has an explicit INDETERMINATE branch** for high κ with 2 of 4 probe rows moved. | A catch-all that reports a confident conclusion is the `claim_rate=None` bug in prose form: every "I don't know" must point away from a verdict. 2 of 4 is too few for anchoring and too many for clean, and saying so is the only honest output. | n/a | DONE |

**Nothing in the moat was touched by D-21…D-23.** `ground_check.py` is byte-identical;
the suite is unaffected. These are calibration-instrument decisions only.

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-24 | **OI-MOAT-26: HTML comments are stripped from the RAW text, BEFORE NFKC.** One-line reorder in `_iter_raw_sentences`. | NFKC folds `＜！－－` and `－－＞` into `<!--` and `-->`, so an author could MANUFACTURE a comment delimiter out of characters no renderer hides. The demonstrated attack welded a pair into mid-sentence and **reversed** the claim: draft `"The appliance ships with ＜！－－at most one, and never with－－＞ dual power supplies [S6]"` → judged `"The appliance ships with dual power supplies"` → **GROUNDED, PASS, 100.0**, with the rewritten sentence printed back to the author as theirs. Fail-closed after the fix (the lookalike stays in the text and is scored): attack now **FAIL**. Genuine ASCII comments still strip (D-17 verified intact). Suite 492 passed / 2 skipped / 11 xfailed; calibration corpus regenerated **BYTE-IDENTICAL**, so CR-004's rates stand and no new CR is due (ADR-025). | revert commit | **DONE, BUT ITS BASIS WAS WRONG — SEE BELOW** |
| D-25 | **`_content_words`' docstring made a raw string.** | It contained `\w`, raising `SyntaxWarning: invalid escape sequence` on every single run of the gate — and becoming a hard error in a future Python. Zero behaviour change; verified under `-W error::SyntaxWarning`. | revert commit | DONE |

**Not fixed tonight, deliberately — and this is the important half of round 7.**
Round 7 found **~22 wrongful PASSes over 11 mechanisms**. Rounds 3 and 4 are on
record closing the fixture they were written against and leaving the class open,
*every time*. Shipping eleven narrow rules into the moat at 3am, with no
adversarial round against them, is that failure by appointment. Everything not
listed above is **tripwired as a strict xfail and counted**, with the two
class-level calls escalated with a written recommendation.

### D-24's basis is retracted (2026-09-12, same night, by the round-7 solo gate)

**I justified D-24 as fail-closed and that justification is false.** I claimed
the reorder removes strictly less-or-equal text in every case, and used it to
place the change inside agent authority. An independent reviewer found the
mixed-delimiter shape my eight-case enumeration never contained:

```
"A <!-- note －－＞ FABRICATED --> B"
  OLD -> 'A   FABRICATED --> B'   (scored)
  NEW -> 'A   B'                  (deleted from the denominator)
```

Text leaving the denominator points TOWARD PASS, so the change is not
fail-closed and was not mine to take on that reasoning.

**The change stays in place** — reverting reinstates OI-MOAT-26, which certified
the OPPOSITE of the author's own sentence, and that is strictly worse. Its real
defence is **renderer-faithfulness**: a Markdown renderer treats the ASCII
`-->` as the closer and does hide `FABRICATED`, so the new order judges the text
the reader actually sees. Sound — but it holds only while **OI-MOAT-29 is
closed, and it is open.**

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-26 | **Keep D-24 in place but move it to Sai's ratification queue, with its fail-closed claim retracted in writing and the mixed-delimiter case tripwired as OI-MOAT-33.** | Reverting costs more than keeping (OI-MOAT-26 is the worse hole). Silently keeping it under a justification now known false is the thing the register exists to prevent: the undo stays available, the reasoning is corrected in public, and the authority question goes to the person whose call it actually is. | `git revert aad2ee1` — reinstates OI-MOAT-26, so do it only deliberately | **AWAITING SAI** |
| D-27 | **Corrected the OI-MOAT-27 recommendation from a `that`-complement refusal to a factive-verb whitelist + negation conjunct.** | My stated reason — "no deterministic rule separates the attack from the honest case" — was false. The discriminator is the VERB's factivity, not the subject, proved by a subject-swap control. A whitelist also has the right polarity (unlisted verbs REFUSE) and satisfies CLAUDE.md's law: to ground a mined span the attacker must find a source using a factive verb, and a factive verb means the source asserts the claim. My rule additionally left 3 of my own 5 tripwires uncovered — I had silently narrowed the Path C agent's broader proposal and inherited an undisclosed gap. | n/a — a recommendation, not a code change; nothing shipped | **RECOMMENDATION ONLY** |

**Corrected round-7 count:** 22 found · **3 closed** (all by D-24; D-25 closed
zero) · **19 open** · 7 tripwired classes. The earlier "closed 2" was wrong.

---

## SAI'S RULINGS — 2026-09-12

**"ratify, yes"** — in response to the two asks put to him at the close.

| id | Ruling | Effect |
|---|---|---|
| **D-24** | **RATIFIED.** Comment-stripping stays before NFKC. | The change is now Sai's decision, not an agent call taken on a justification that turned out false. D-26 closes. `git revert aad2ee1` remains the undo, but it is no longer *my* undo to reach for. **The retraction stands on the record** — the change is right, my stated reason for taking it alone was not, and ratification does not erase that. |
| **OI-MOAT-27** | **APPROVED — build the factive-verb whitelist + negation conjunct.** | J-19 unblocked. **J-20 lands FIRST** (the `n't` tokenizer repair): the whitelist's negation conjunct cannot see `haven't` today, so shipping the whitelist alone would ground `Critics haven't shown that P`. Neither fix is sufficient alone and the order is not a preference. |

**Still open and NOT covered by this ruling:** J-15 (rhetorical questions),
D-07 (`install.sh` shipping pytest to end users), `docs/consulting/` privacy,
D-01 (park-list reading), and the D-15…D-20 cohort.

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-28 | **J-20 / OI-MOAT-25 CLOSED: `_expand_negation_contractions` expands the `n't` suffix before tokenizing.** Applied at 4 sites — `_tokenize` plus the three `_ABSENCE_NEGATION_RE` reads, which operate on raw text rather than tokens. | Approved by Sai ("ratify, yes"). **One rule, not a token list:** every contracted negation in English is the suffix `n't`, so a list of forms would be a blacklist over a class the author draws from — the rule shape that has now failed five times here. **Both apostrophes matched:** NFKC does not fold U+2019 to U+0027, so a curly apostrophe would have walked through a straight-quote-only rule, the same surface evasion one layer down. Irregulars deliberately NOT special-cased: `can't`→`ca not` is not English but IS symmetric, claim and source pass through the same function, and the `not` the guards need is present. Round-7 attack PASS(100.0) → **FAIL**; uncontracted control unchanged; suite **512 passed / 2 skipped / 20 xfailed**; corpus **byte-identical**, so CR-004 stands. | revert commit — reopens OI-MOAT-25 | DONE |

**OI-MOAT-25's two strict xfails XPASSED and their markers are removed.** The
tests stay as permanent guards. Open Error-B classes: **19 → 18.**

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-29 | **J-19 / OI-MOAT-27 (partial): `_span_under_nonfactive_complement` — a factive-verb WHITELIST + negation conjunct.** Purely additive to `_span_is_hedged`; it only ever adds refusals. | Approved by Sai ("ratify, yes"). **The first rule here keyed on a whitelist, and the inversion is the point:** every moat rule that has failed in this project was a blacklist over a class the attacker draws from. An unlisted verb now REFUSES — `posit` fails without being enumerated anywhere. It satisfies CLAUDE.md's actual test (a property the attacker cannot set without giving up the attack): to ground a mined span he must find a source whose verb *asserts* the claim, at which point grounding is correct. Subject-swap control verified end to end — endorsement follows the VERB, not the subject. Honest-attribution mirror stays GREEN, so OI-T2-01 does not return. Suite **524 passed / 2 skipped / 17 xfailed**; corpus **byte-identical**, CR-004 stands. | revert commit | DONE |

**Scope stated, not implied.** J-19 closes the `that`-COMPLEMENT family only —
round-7 tripwires c1, c2, c4 XPASSED and are now permanent guards. **c3
(zero-complementizer complement) and c5 (retraction AFTER the span) remain OPEN
and tripwired.** The solo gate caught an earlier version of this work silently
narrowing its own claim; the scope line exists so that cannot recur.

**Open Error-B classes: 18 → 15.**

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-30 | **OI-MOAT-29 CLOSED: comments are no longer stripped inside code spans.** `_strip_html_comments_outside_code` passes fenced blocks and inline code through verbatim. | A `` `<!--` `` a writer is *talking about* is not a comment to any renderer, but it paired with a genuine `-->` downstream and swallowed every sentence between — the demonstrated draft lost a whole fabricated sentence from the report, never scored so never flagged. D-17 restricted stripping to well-formed pairs while reasoning about an unterminated opener running to EOF; a stray opener finding a real closer is well-formed *by construction*. Same renderer-faithfulness principle as D-24. Fail-closed: strictly less text removed, strictly more scored. | revert commit | DONE |
| D-31 | **OI-MOAT-30 CLOSED: a blank line is forced after every Markdown header line.** | syntok does not break after an unpunctuated header, so the body line below was welded into the header's sentence and inherited its NON_CLAIM exemption — `"### TODO\nMongoDB lost all data"` scored **nothing**, while the same line alone scored. A blank line is a paragraph boundary to syntok and changes no character of the header or the body, only where the segmenter may cut. Fail-closed: it can only ADD claims to the denominator. | revert commit | DONE |
| D-32 | **OI-MOAT-32 CLOSED: a span carrying a citation is never zero-content NON_CLAIM.** | D-19's docstring promised "numerics and citations are checked FIRST and override" — the code checked only numerics, and `_strip_citations` ran *before* the test, so the marker it was meant to notice had already been deleted. `"It is not [S1]."` left the denominator. Lowest severity of the round; fixed because **a gap between a docstring's guarantee and its code is worse than no guarantee** — the next reader builds on something that is not there. | revert commit | DONE |
| D-33 | **`import re as _re` hoisted to the top of `ground_check.py`.** | Systemic, not cosmetic. Three separate `NameError`s in this file have had one cause: a module-level `_re.compile(...)` constant placed beside the function that used it, above an import sitting 400 lines down. Two of the three were mine, one of them today. Every one failed loudly at import time, which is the only reason they were cheap. Hoisting makes the class impossible rather than survivable. Zero behaviour change; suite green. | revert commit | DONE |

**OI-MOAT-31 is DELIBERATELY NOT PATCHED — escalated to Sai.** `_header_asserts`
asks *"is this an assertion?"* and **defaults to NO**, so a header escapes
scoring whenever the test is inconclusive: a default pointing toward PASS.
`### Redis lost all data` is caught only because "Redis" ends in "s"; `###
MongoDB lost all data` is not, because "lost" is an irregular past form no
suffix rule reaches. Every narrow fix available is the shape this project has
watched fail five times — a list of irregular verbs is a blacklist over an open
class, a content-word count is the length rule round 3 already killed. **The
sound fix inverts the default** (score headers, group uncited ones separately in
the report — exactly the J-15 remedy), **but that moves the Error-A/Error-B
trade-off, which is Escalation #1 clause 1.**

**Open Error-B classes: 15 → 12.** Suite **527 passed / 2 skipped / 14 xfailed**;
corpus **byte-identical**, CR-004 stands.

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-34 | **`label_basis` column added to the scaffold (DERIVED), plus `reliability_eligible()` in `calibrate.py`.** Policy rows are excluded from κ and **included in every error rate**. | INTRA-RATER-2026-09-12: the corpus mixes items whose label follows from the evidence with items whose label follows from a gate POLICY not visible in the item. Only `haiku_summary` qualifies today (q24, q44). Three raters judged those two rows — **0/6, same direction, including the author of the labels judging blind.** Including them dragged intra-rater κ from **+0.857 to +0.636** and was a large part of why the inter-rater round read as total failure. Scaffold-side only; `labels-v2.csv` untouched and all **52 labels still load as gold with zero stale**, because a new COLUMN does not change `claim_sha` (the same reasoning that made `source_type` safe in 2026-09-02). | revert commit; the column is regenerable and nothing depends on it | DONE |

**The line this draws, and the one it must NOT.** κ excludes policy rows —
agreement there measures rule-memorisation. **Error-A and Error-B include them,
always.** A test asserts by source inspection that `error_rates`,
`loo_operating_point` and `select_operating_point` never consult
`reliability_eligible`, because the tempting next step after "exclude them from
κ" is "exclude them from the rates", and that would score the gate only on the
questions it finds easy — the identical failure already found in three of this
project's own instruments.

**Retraction carried forward:** the 2026-09-03 report blamed the review page's
wording for these two rows. The rebuilt page stated the provenance outright and
the answer did not move. The wording was not the cause.

Suite **532 passed / 2 skipped / 14 xfailed**; corpus regenerates stably.

---

## D-35 — OI-UX-01: the absence of evidence must be ASSERTED, never shown as nothing

| id | Decision | Basis | Undo | Status |
|---|---|---|---|---|
| D-35 | **`evidence_basis(claim, store)` added to `ground_check.py`, emitted on every `per_claim` and `retained_appendix` entry.** One prose sentence naming what the gate consulted and what it found, branch-ordered to mirror `ground()` exactly. | Sai stalled on **6 of 20** intra-rater rows on 2026-09-12 and asked *"nothing here?"*. Every one of the six was a row whose evidence reads as absent. The gate's own author could not tell **"the tool looked and there was nothing"** from **"the tool broke"** — and those are opposite verdicts on the gate's trustworthiness. A stranger reading a grounding report has strictly less context than he did. | `git revert <this commit>`; the field is additive and no verdict consults it | DONE |

**The law, stated so the next surface inherits it:** *never render the absence
of a thing by showing nothing.* State what was consulted and what was found, as
an assertion.

**Three surfaces broke the same law three ways**, and the middle one is the
moat's flagship case rendered as a template failure:

| state | rendered as | read as |
|---|---|---|
| claim cites nothing | `""` | the generator broke |
| cited id never retrieved (**fabrication**) | `S19: [NOT IN STORE]` | a placeholder that failed to fill |
| absence claim | a bare query list joined by `\|\|\|` | an internal dump |

**Chesterton's Fence — the fence was mine, and it was a case resolution.**
`build_corpus._evidence_text`'s docstring already records this exact bug being
fixed *once*, for the ABSENCE branch only ("Showing `""` for these rows — the
original bug this function replaces"). The systemic issue was never named, so
the other two branches kept it, **and the patched branch still stalled him** —
showing the queries was not enough, because it never asserts that the list is
complete and that this is what an absence is checked against. A case fix that
does not name its class buys one row and leaves the law unwritten.

**Why the product surface and not the calibration scaffold.** Changing the
scaffold's `evidence` column changes `claim_sha = hash(claim_text, evidence)`
and marks the affected **gold labels STALE** — re-ratification is Sai's
(standing gate), so that path is blocked, and it is the *less* important one
anyway. **Detectability (FMEA):** the scaffold defect is highly detectable — a
human hit it on first read, twice. The grounding report's version is
*undetectable by the current process*: `per_claim` carried **no evidence field
at all**, and no test asserted that a report explains itself. High severity ×
low detectability is the one to fix, and it is the surface a customer actually
reads.

**Deliberately NOT one shared renderer.** The report's summary branch states
the governing policy outright ("Agent-Assure never grounds a claim on a summary,
whatever the summary says") because a user acting on a verdict needs the reason.
The labelling instrument must **not** say it: a display that tells the rater the
answer makes reliability measure rule-reading — **Goodhart**, and the very
contamination D-34 avoided by quarantining those rows out of κ rather than
explaining them. Two surfaces, opposite requirements; the divergence is recorded
in the function's own docstring so it is not "simplified" later.

**Fail-closed by construction.** `evidence_basis` is a display function. It adds
no branch to `ground()`, alters no verdict, and a source-inspection test asserts
that `ground`, `check_absence`, `ground_relational` and `classify` never consult
it — so it cannot become a decision path. Not Escalation #1: nothing moves the
Error-A/Error-B trade-off.

**Evidence.** `tests/test_evidence_basis.py`, 13 tests, **12 proven RED against
pre-fix `ground_check.py`** (`AttributeError: no attribute 'evidence_basis'`).
The 13th — the source-inspection guard — passed pre-fix *vacuously*, because a
function that does not exist is consulted by nothing; it is a standing guard,
not a regression test, and is reported as such rather than counted as 13/13.
`test_score.py::test_per_claim_fields` was kept an **exact** field-set
assertion rather than relaxed to a subset: the report is of-record, and adding
a field should cost one deliberate edit.

Suite **545 passed / 2 skipped / 14 xfailed** (was 532). Corpus
**byte-identical**; 52 labels still gold, zero stale — `evidence` is untouched,
so no `claim_sha` moves. CR-001 regenerates byte-identical. No CR is due.
