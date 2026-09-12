# Open Jobs Register — Agent-Assure

Per ADR-045: one entry per open thread, **every entry with a named owner**.
`owner: Sai` entries carry the reason they cannot move without him.
Last reconciled: **2026-09-12** (session `d2b27b1f`, overnight round-7 run).
**Demo and Alpha readiness are DEFINED as criteria in `RESUME-HERE.md` — read that first.**

---

## owner: Sai — blocked on a decision, not on work

| id | Thread | Blocking reason | Cost once ruled |
|---|---|---|---|
| J-01 | **OI-MOAT-21** | **CLOSED 2026-09-02** — approved by Sai; T2 demoted, `lex_tau` retired (ADR-006 + CR-003). Error-A 0.200→0.320, Error-B 0.111→0.074. The coverage repair was rejected on trace: it leaves reordering open. | done |
| J-02 | **ADR-004 Q1–Q6 — NLI tier** | **APPROVED 2026-09-02, now LOAD-BEARING.** After ADR-006 it is the only mechanism that can separate a synonym substitution from an argument substitution, and the only way to buy back Error-A 0.320. **Correct the plan first:** its stated guarantee "can never CREATE a PASS" is FALSE — UNGROUNDED→GROUNDED empties the appendix and ADR-005 yields PASS. | 3.6–6.1M |
| J-03 | **OI-DEC-01** | **CLOSED 2026-09-02** — ratified by Sai with a red-team gate; propagation implemented on both paths (conjunction split + semicolon segment), corpus diff byte-identical. | done |
| J-04 | **OI-T2-01** | **CLOSED 2026-09-02** — exact-containment T1 (whole claim verbatim in a cited source grounds at any length). Was blocking: 31/52 gold claims are under 8 tokens, and the gate's own end-to-end fixture failed. Quote-mining guard red-teamed (OI-QM-01). | done |
| J-15 | **OI-DEC-02 — rhetorical questions and clause fragments are scored as FACTUAL claims** | Found on real prose by the base-rate run: `classify('Is he wrong?')` -> FACTUAL, scored, flagged UNGROUNDED. On 10 chapters this was the ONLY observed false-alarm source — zero were paraphrase. But exempting questions moves them OUT of the denominator, which is PASS-enabling and is exactly the smuggling hole rounds 3-4 closed: `classify("Isn't Redis capable of 128000 operations per second [S1]?")` -> NUMERIC, scored today. Escalation #1. | ~0.3M |
| J-05 | **OI-MOAT-20 — verb-final header escapes scoring** | Deterministic closure needs either Error-A on every multi-word heading or a POS tagger — the latter is exactly what J-02 governs. | ~0.1M |
| J-06 | **Inter-rater reliability** | **ATTEMPTED AND FAILED 2026-09-03** — κ 0.54 / 0.16 vs Sai, **0.09 between the two readers**. Two page defects were Claude's (label-sorted item order leaked the answer; the AI-summary question asked about content when the rule is provenance). **Next step is INTRA-rater, not another reader:** Sai re-labels 20 of his own rows blind, ~20 min. That fork — wrong readers vs ambiguous corpus — decides whether the 52-row corpus is salvageable. `docs/reports/INTER-RATER-2026-09-03.md` | free |
| J-07 | **Ratify the 2026-08-30 register** (D-01…D-14) | 14 autonomous calls await ratify-or-reverse; each carries its undo. Includes the disclosed `install.sh` side effect. | free |
| J-18 | **Ratify or reverse D-24** | I shipped a moat change justifying it as fail-closed; the solo gate proved that claim FALSE on a mixed-delimiter shape my enumeration never contained. The change stays because reverting reinstates the worse hole (OI-MOAT-26 certified the OPPOSITE of the author's sentence), but the authority call is yours. Undo: `git revert aad2ee1`. | free |
| J-19 | **OI-MOAT-27 — the quote-mining class** | Recommendation CORRECTED after the solo gate: a **factive-verb whitelist + negation conjunct**, not the large-Error-A `that`-complement refusal I first proposed. Unlisted verbs refuse, so the attacker is off the enumerating side. Needs calibration on n=52 and must compose with J-20. | ~0.5M |
| J-08 | **`docs/consulting/` visibility coupling** | Committed to the HQ repo on the stated assumption that it stays PRIVATE. It names a client and records that they have no signed paper. One settings toggle, not a property a file can enforce. | free |

## owner: Claude — buildable, sequenced behind the rulings above

| id | Thread | Waits on |
|---|---|---|
| J-09 | Red-team round 6 against the CR-002 deployment + any J-01 rework | J-01 |
| J-10 | ~~Ingest the second labeller's set~~ **DONE 2026-09-03** — stats computed, CR-004 and RESUME-HERE amended with the κ figures. Raw sets in `calibration/second-reader/`; nothing written to `labels-v2.csv`. | — |
| J-16 | ~~Fix the review page + run red-team round 7~~ **DONE 2026-09-12.** Page defects fixed in the new intra-rater instrument; round 7 ran (22 findings / 11 mechanisms / 3 closed / 19 tripwired). | — |
| J-17 | **Red-team round 8** — owed. Round 7's 19 open findings are *recorded*, not *accepted*, and D-24/OI-MOAT-27 need Sai first. Alpha #7. | J-18, J-19 |
| J-20 | **OI-MOAT-25 tokenizer repair** — expand the `n't` suffix before tokenizing, one rule covering every contracted negation. Fail-closed. Must land BEFORE the OI-MOAT-27 whitelist, which needs a negation conjunct that cannot see `haven't` today. | nothing — sequenced |
| J-11 | OI-BUILD-01 — two reference worktrees still cut from the wrong base; rebase or discard | nothing (low value) |
| J-12 | Batch ingestion is built but **never exercised on real data** — cpc-book has sent no batch yet | cpc-book |

## owner: HQ / other repos

| id | Thread | State |
|---|---|---|
| J-13 | cpc-book calibration corpus (`agent-assure-cpc-pilot`) | Answered 2026-08-30; ingestion built. Waiting on their ch.1 to exist. |
| J-14 | HQ retraction filed (`hq-repo-unpushed-100-days`) | Delivered and pushed; no action pending. |

---

## Closed 2026-09-02/03 (do NOT redo)

OI-MOAT-21 (T2 demoted, `lex_tau` retired — ADR-006/CR-003) · OI-T2-01 (exact-containment T1) · OI-DEC-01 (citation propagation, both paths) · OI-ABS-01 (absence scope — Error-B 0.074→0.000, CR-004) · OI-QM-01 (quote-mining guard) · OI-DEC-03…06 (HTML comments, splitter punctuation, zero-content NON_CLAIM, underscore tokenizing — real-prose artifacts 31.3%→3.2%). Red-team round 6 (matched pairs). Second-reader page rebuilt.

**Round 7 is OWED:** D-15…D-20 landed AFTER round 6, so the current tree has never been attacked. Alpha criterion #7.

## Closed in the α2 session (do NOT redo)

α2 — 52 gold labels ratified, CR-002 emitted (lex_tau 0.76, held-out
Error-A 0.200 / Error-B 0.111, n=52), 0.76 deployed measurement-neutrally.
`source_type` scaffold column added, closing the corpus defect ratification
exposed. Red-team rounds 3, 4 and 5 (65 wrongful PASSes found, 11 of 12
mechanisms closed). Error-A harness built. OI-CAL-01, OI-ENV-01, OI-NUM-02,
OI-MOAT-03/-05/-07/-11…-19/-22/-23/-24 all closed.

## Environment note (2026-09-03 close)

`.claude/worktrees/agent-a60c96d40d924ec2c` was **left in place**: it is LOCKED by
a live `claude` process (pid 55364, 26h uptime), and the dead-run rule says prove
death before acting. Nothing is at risk — its artifacts (base-rate v1 report,
probe script, results JSON) were copied into `Agent-Assure/docs/reports/` before
the close. Remove with `git worktree remove --force` once that process exits.
The two `wf_*` worktrees belong to another session and were not touched.

## Added 2026-09-12 (round 8)

| id | Thread | Owner | Blocking reason / waits on |
|---|---|---|---|
| J-21 | **Sentence-bounded complement detection.** Bound the complementizer search AND the factive prefix to the SOURCE SENTENCE containing the matched span, using the `syntok` segmenter `decompose` already depends on. Closes the R8A-01/02 residue (attribution and denial certify at PASS/100.0 whenever any non-determiner function word sits between `that` and the span) **and** R8A-03 (the factive prefix window is currently the whole document). One structurally-correct rule instead of a third leftward-scan patch. **Needs its own adversarial round before it can be called closed** — two patches for this class shipped on 2026-09-12 and one was wrongly reported CLOSED. | Claude | nothing — sequenced after round 8 |
| J-22 | **Whitelist additions are Sai's (Escalation #1).** D-36 newly refuses honest sources that endorse with a verb not on `_FACTIVE_VERBS` — `concluded that`, `indicates that` grounded before and FAIL now. Adding them is **PASS-enabling**. `reported` must NOT be added: "The blog reported that X" is attribution and adding it opens Error-B. The class is absent from the n=52 corpus, so the deployed **A=0.320 does not bound it** — it is unmeasured, not small. | **Sai** | a ruling; ~free once ruled |
| J-23 | **19 open round-8 findings**, tripwired as 43 strict xfails across four files in `tests/red_team_moat/`. Recorded is not accepted (Alpha #7). Includes 3 absence-path Error-B (R8C-01/02/03), 2 preprocessing Error-B (R8B-01/02), a 4-trigger denominator escape (R8B-03), and 7 lying-display findings against D-35 (R8C-04…09, R8C-11). | Claude + Sai | J-21 first |

## Added 2026-09-13

| id | Thread | Owner | Blocking reason / waits on |
|---|---|---|---|
| J-24 | **THE PRODUCT CALL — ship provenance-only, or fund entailment.** Evidence: STORM genesis + LLM-judge research + HHEM diagnostic (`docs/research/`). Recommendation: provenance. | **Sai** | a decision; everything below is sequenced on it |
| J-25 | **R9P1-01/02 — fabricated citation certifies PASS 100.0 on RELATIONAL and ABSENCE claims.** Move the unresolved-citation check in `ground()` ahead of the kind dispatch. Fail-closed. Tripwired. | Claude | J-24 (useful either way; do first if provenance) |
| J-26 | **R9P2-01…04 — `load_store` silently repairs a self-contradicting store.** Raise on duplicate normalised ids, duplicate keys, wrong types, tool/source-type mismatch. Fail-closed. -01 tripwired. | Claude | J-24 |
| J-27 | **Comment-stripper code detection** — tilde fences, indented code, escaped openers delete visible prose from the denominator. R8B-01/02 + R9P2-05/06/07. -06 tripwired. | Claude | J-24 |
| J-28 | **Spec §7.5 — absence claims fail OPEN on an incomplete store.** Remedy (session taint on uncaptured retrieval, or wider matcher) is hook registration. | **Sai** | Escalation #4 |
| J-29 | **Round 10, provenance only**, after J-25…J-27. | Claude | J-25, J-26, J-27 |
| J-30 | **MiniCheck diagnostic** — harness ready (`docs/research/diagnostic/`), download failed twice on network. Confirmation, not decision-relevant. | Claude | a stable connection |
