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

## Added 2026-10-01 (overnight run, D-38)

**J-25 is CLOSED** (D-39). It was NOT sequenced behind J-24 after all: the
product call does not gate it, because entailment layers ON provenance rather
than replacing it — a citation must resolve to a genuinely retrieved source
under either branch. The same reasoning frees J-26 and J-27.

| id | Thread | Owner | Blocking reason / waits on |
|---|---|---|---|
| J-31 | **A correctly-cited absence claim is REFUSED; the identical uncited claim is CERTIFIED.** `ABSENCE_SUPPORTED`/PASS uncited vs `UNVERIFIED_ABSENCE`/FAIL with two real citations. Verified pre-existing on the pre-J-25 tree. Error-A, fail-closed, no moat breach — but the product asks authors to cite and then penalises them for it (Jobs-to-be-Done defect, not just a rate). Any repair moves the Error-A/Error-B trade-off. Tripwired in `test_moat_r9_provenance_closed.py`. | **Sai** (Escalation #1) + Claude to diagnose | a ruling once round 10 has characterised it |
| J-32 | **`content_sha256` is required to be a str but never recomputed against `text`.** A record whose text was edited after capture still loads. Deliberately out of J-26's scope: the threat model is the DRAFTING model's text, not an edited store, and an attacker who can rewrite the store can rewrite the digest too — so this defends against corruption and lazy tampering, not an adversary. Cost is the binding constraint: 76 placeholder digests across 33 test files must be swept in the same commit. Upgrade path: assert `sha256(NFKC(text)).hexdigest() == content_sha256`, which holds by construction because `capture_core._sha256_nfkc` hashes the NFKC form. | Claude | not blocked; cost/benefit says after launch |
| J-33 | **STILL OPEN, and now fully MASKED on the relational path (D-67).** `_CITATION_RE` cannot parse these markers, so they are NO citation rather than an unresolved one. Three spellings are masked by J-40's digit leak; the fourth, `[Sxx]`, is masked as of 2026-10-02 by J-39 — the leftover "sxx" is swallowed into side_A. Re-pinned as an ACCIDENT with a verdict-level assertion (`UNVERIFIED_RELATION`, explicitly NOT `UNVERIFIED_CITATION`) so the day it is really closed the assertion flips. **Live and strict on the ABSENCE path**, which extracts no arguments — that is the only remaining demonstrator. | Claude | nothing |

## Added 2026-10-01 — ROUND 10 (13 ERROR-B over three adversaries)

**Read this before J-24.** Round 10 moved the product question. The gate's
deterministic logic is in decent shape; **the CAPTURE layer is where the promise
breaks**, and almost nothing below is fixable by changing `ground_check.py`.

| id | Thread | Owner | Blocking reason / waits on |
|---|---|---|---|
| J-34 | **J-28B has not faced an adversary.** The block-structure rule replacing J-27's scanner landed tonight and closed all 5 of adversary A's shapes, but the last two closure claims in this area were refuted within the hour of being made. Also carries adversary A's residue: forged line boundaries (`splitlines` splits on U+2028/U+2029/U+0085/\f/\v, CommonMark does not) and code spans crossing a newline. **No closure claim may be made for J-28B until round 11 runs.** | Claude | round 11 |
| J-35 | **Write-then-Read laundering (R10B-01, R10B-03) — ERROR-B.** `capture_core.py:311` maps `Read` → `verbatim` UNCONDITIONALLY, and `RetrievedSource` has no field recording a file's ORIGIN. An agent writes a fabrication to a file, Reads it back, cites it → **PASS 100.0 / GROUNDED**, numeric tier "verifying" figures the same model invented. The same text via `WebFetch` correctly reads UNGROUNDABLE. **The laundering happens BEFORE the store, so no loader validation can ever see it.** | **Sai** | Escalation #4 (capture contract) |
| J-36 | **The absence ledger is attacker-written (R10B-02, R10C-01) — ERROR-B.** No SEARCH tool is in `_RETRIEVAL_TOOLS`, so `_derive_query_provenance` can only ever yield a URL, a file path, or a session id. The absence rule's "two distinct search queries" are therefore **two strings the drafting agent chose.** Certified from two Reads of self-named files, from two off-topic pages whose URLs carry the right words, and from ONE page fetched twice distinguished only by a URL fragment the server never receives. `evidence_basis` then prints those file paths to the user as "the queries were". | **Sai** | Escalation #4 |
| J-37 | **ALREADY CLOSED — this row was STALE, and it cost a cycle. Closed 2026-10-01 in `15baf1e`, not tonight.** The row described the PRE-FIX state in the present tense: it said the builders carry `tool="calibration_fixture"` and that **CR-004/CR-005 were "measured on stores the shipped gate would reject"**. `15baf1e` had already changed `_source` → `tool="Read"` and `_summary_source` → `tool="WebFetch"` and added `tests/test_corpus_stores_survive_the_loader.py`. Re-measured 2026-10-02: **52/52 corpus stores round-trip through the shipped `load_store`, 0 refused**, under a control confirming a refusal is still reachable. CR-005's statement ("corpus fixtures use real tool names; loader-parity test added") was ACCURATE; nothing is wrong with the launch numbers on this account and no CR needs re-deriving. **What tonight actually added:** the existing file contained no `pytest.raises` at all, so all three of its tests were satisfiable by a `load_store` whose validation had been deleted — a green round-trip is evidence only while a red one is reachable. A fourth test now pins the refusal (mutation-checked: `DID NOT RAISE` when fed a recognised tool). **Cost of the stale row:** I wrote a duplicate test before searching the suite, because I trusted this row's mechanism instead of deriving it from code — violating the instrument's own "code first, register second" rule within an hour of writing it. Duplicate deleted. **A register row that states a mechanism in the present tense must be re-derived before it is acted on.** | Claude — done | — |
| J-38 | **There is no "this session" (R10B-04) — ERROR-B, and a DOCUMENTED guarantee is false.** `session_id` is never written to a record; `fetched_at` is the constant sentinel `1970-01-01T00:00:00Z`; the store is opened `mode="a"` forever and never rotated. A later session's draft citing a prior session's `[S2]` → **PASS 100.0**. `CLAUDE.md` states "Store is per-session … a draft citing prior-session sources fails, correctly" — **that is unenforced and, as fielded, unenforceable.** This one strikes the founding spec's own one-sentence promise: "actually retrieved THIS SESSION". | **Sai** | Escalation #4 |
| J-39 | **MOOT 2026-10-02 (ADR-007).** The endpoint-phrase fix landed and is retained, but relational corroboration no longer produces a verdict, so the finding can no longer be an Error-B. Its tripwires are re-pointed at `relation_diagnostic` and stay strict. | — | moot |
| J-40 | **A number inside a RELATIONAL claim is never checked (R10C-04) — ERROR-B.** `classify` orders RELATIONAL before NUMERIC and `ground()` returns from the relational branch above the numeric branch, so "causes 97% of all silent data loss" passes against a store containing no percentage. ABSENCE is only incidentally protected (a digit becomes a strong anchor — a ceiling, not a defence). Fail-closed to fix. | Claude | nothing — sequenced after J-34 |
| J-41 | **STOP STRIPPING HTML COMMENTS — delete the class instead of fixing it a fourth time.** The comment-stripper has now lost rounds 7, 8, 9, 10 AND 11 across three implementations (backtick-only → code-region scanner → block-structure rule), producing 12 ERROR-B tonight alone. Root cause is structural: the gate is reimplementing a Markdown renderer's block model against an adversary who writes the document. Removing the feature deletes the class permanently and turns ~7 functions into dead code. Trade: an unrecoverable Error-B becomes a recoverable Error-A (a draft carrying an authoring note fails — arguably correct for a verification gate). **Unmeasured:** no row of the n=52 corpus contains an HTML comment. Only other option that ends the sequence: adopt a real CommonMark parser as the oracle. | **Sai** | Escalation #1 (moves the Error-A/Error-B trade-off and the author contract) |
| J-42 | **A summary can still supply a counting query for an absence claim.** Reopened deliberately on 2026-10-01: the fix for it shrank a list that is also the blanket-corpus-word refusal's denominator, switching that refusal off (net Error-B), so it was withdrawn. Correct repair: pass the FULL query list for the denominator and a verbatim-only set for matching — needs `check_absence`'s signature to change. | Claude | daylight; needs care, two directions in one function |
| J-43 | **MOOT as a verdict defect 2026-10-02 (ADR-007).** The spelled-figure check is retained inside `relational_diagnostic` and its tripwires stay strict, but it no longer decides anything on the relational path. **RESIDUE STILL LIVE: J-62**, the ABSENCE branch, which was NOT demoted. | — | moot (see J-62) |
| J-44 | **MOOT 2026-10-02 (ADR-007).** The Error-A it was trying to fix was in endpoint matching, which no longer votes. The withdrawal (D-69) stands and the collision guard is retained as a permanent tripwire — a stem must never match a different word. | — | moot |
| J-45 | **`evidence_basis` announces queries that did not count.** It still calls `_session_queries`, so an absence report tells the user "N distinct search queries" listing some the verdict ignored. Display contradicting the verdict is the D-35 class. | Claude | nothing |
| J-48 | **CLOSED 2026-10-02 as DOCUMENTATION (D-62), per Sai's ruling.** All three Markdown surfaces now tell authors to keep authoring notes on ONE line, with the syntax shown and the reason named: a block-comment stripper is an UNBOUNDED DELETION primitive, four designs have lost on it, and refusing a note is Error-A where deleting a claim is Error-B. The three strict xfails STAY as the record of the behaviour. Two new parametrised guards in `test_product_claim.py` give the prose a runtime, because nothing fails when documentation is deleted. | — | closed |
| J-49 | **Wire `--session-id` into the skill and command so session scoping is the DEFAULT, not opt-in.** J-38 built the enforcement and the CLI flag; what is missing is a reliable way for the skill to learn the current session id (the hook gets it from the PostToolUse event; the skill has no equivalent). Until this lands, every claim surface must say session scoping is available *on request*. | Claude + **Sai** (it likely needs a hook/settings surface, which is Escalation #4) | a way to expose the session id to a skill |
| J-50 | **A session-refused store exits 1 with a Python traceback, not a message.** α4 friction F3. "You reused a store from an earlier session" is an EXPECTED condition and deserves a one-line message. Left alone deliberately — every other store error behaves this way, and special-casing one would make the CLI's error register inconsistent. Fix them together or not at all. | Claude | nothing; do it with F2/F4 as one UX pass |
| J-51 | **Nothing tells a user how to obtain the session id `--session-id` wants** (α4 friction F4), and `install.sh` never mentions the flag at all (F2). Both need `install.sh` text, which is Escalation #4. | **Sai** | Escalation #4 (install.sh) |
| J-52 | **The Claude Code PLUGIN path is still unvalidated.** α4 proved install.sh, the engine, the hook and the CLI work in an unrelated repo, but NOT `claude --plugin-dir`, the marketplace entry, or the hook firing from a live session. Those need hook registration into a live config. **This is the last unproven step before launch.** Exact command in the α4 report. | **Sai** | Escalation #4 — a live session + hook registration |
| J-53 | **STILL OPEN, and deliberately untouched by J-43.** `_RATE_BEFORE_RE` reads "per <word>" out of the window BEFORE a number, so the words "per cent" make an UNRELATED bare digit read as a rate of "cent" and the source's absolute 2 cannot match. Error-A, fail-closed. Fixing it is **PASS-ENABLING** — a claim refused today would certify — which is Escalation #1. Its tripwire was RE-PINNED 2026-10-02 (D-64) to the isolated repro with a control, plus a helper asserting the fixture carries no spelled number, because J-43 would otherwise have masked it. | **Sai** | Escalation #1 |
| J-54 | **The last human step: confirm the plugin's hook fires in an INTERACTIVE session.** `claude --plugin-dir /path/to/Agent-Assure` → `/hooks` (expect PostToolUse listing `capture_hook.py`) → read any file (expect `.assure/evidence-store.jsonl` to appear) → `/assure-verify <draft>`. **Proven unreachable non-interactively** (D-60): `claude -p` executes no PostToolUse hooks under any of three registrations. Everything this would confirm is already proven in parts — hook command works when invoked, matcher covers the tools, layout is the documented one. Two minutes. | **Sai** | needs an interactive terminal |
| J-55 | **Agent-Assure cannot capture in `claude -p` / CI mode** — the hook never runs, so the store is empty and the gate fails everything. Documented on README + SKILL and pinned as a disclosed limitation. **Open question for the roadmap:** if CI use is wanted, capture must come from somewhere other than a PostToolUse hook (a wrapper that records retrievals, or an SDK-level capture). That is a design decision, not a bug fix. | **Sai** | a product decision about whether CI is a target |
| J-56 | **CLOSED 2026-10-02** — `evidence_basis` claimed "this session" in two branches (missing-citation and no-queries) when the gate cannot know it without `--session-id`. Found by a real `claude -p` session running `/assure-verify`, which noticed the overclaim in its own output; the sibling was then found by the new AST guard after a three-kind grep had missed it. Fixed to wording that is true either way, guarded, and the pinning assertions strengthened with a negative. | — | closed |

| J-57 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007 + D-76)** — not repaired, and NOT closed by the first attempt. Round 13 showed the fall-through implementation MOVED this shape onto T1: "causes no X" certified PASS 100.0 against "causes X", because `no` is a stop word. The FLAT REFUSAL closes it; the fall-through did not. | — | closed by demotion |
| J-58 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007)** — not repaired. `side_B`'s anchor still behaves exactly as round 12 described; it just has no verdict consequence. R12-11's preposition question dies with it. | — | closed by demotion |
| J-59 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007)** — not repaired, and this is the finding that decided the ADR: closing it needed the trigger's ARGUMENTS, i.e. parsing, which the moat forbids. Demotion closes it without parsing. | — | closed by demotion |
| J-60 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007 + D-76)** — not repaired, and MOVED ONTO T1 by the first attempt: direction reversal certified PASS 100.0 with zero planted vocabulary. The flat refusal closes it. | — | closed by demotion |
| J-61 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007 + D-76)** — not repaired, and MOVED ONTO T1 by the first attempt: a source that explicitly DENIES the relation certified it at PASS 100.0 via T1's span+coverage rule. The verbatim path's hedge check did NOT fire. The flat refusal closes it; **whether that hedge check is adequate for other kinds is now J-67.** | — | closed by demotion |
| J-62 | **STILL OPEN — the one round-12 Error-B that ADR-007 does NOT close.** The ABSENCE branch was deliberately not demoted, and its spelled-figure hole is demonstrated: a spelled count inside a supported absence certifies at PASS 100.0 where the digit form is refused on the identical store. Same guard (`spelled_quantity_ok`), different branch. | Claude | nothing — it is the next piece of work |
| J-64 | **CLOSED BY DEMOTION 2026-10-02 (ADR-007)** — not repaired. Two endpoints resolving to the same phrase no longer certifies anything. Retained as a diagnostic tripwire. | — | closed by demotion |
| J-63 | **J-43 taxes the honest spelled form (R12-12) — ERROR-A, disclosed by design.** A draft that writes "type two diabetes" or "ninety-seven percent" against a source writing "type 2" / "97%" is refused, because the rule is verbatim presence and proving the two equal needs a parser the moat does not have. This is the ruling working as ruled, not a bug — but it is an UNMEASURED Error-A on honest prose and belongs on the tin. | **Sai** | a claim-text decision + corpus rows to measure it |

| J-65 | **ANSWERED 2026-10-02 — round 13 reported and it REFUTED the first implementation.** 16 findings, all reproduced: 6 NEW Error-B (5 CRITICAL), 1 Error-A, 4 test-defect, 4 doc-defect. Response landed in `fff0514` (D-76, D-77). Report committed. **Residual: no adversary has run against the CURRENT state** — round 13 attacked the fall-through, not the flat refusal. Round 14 is the next session's first item. | Claude | nothing |
| J-66 | **The real-draft Error-A is unmeasured and 0.360 understates it.** ADR-005 makes a retained violation a hard cap, so ANY draft containing an unquoted causal sentence now fails. The corpus has 7 relational rows in 52; a research draft can be half relational. This is the number to watch after launch. | **Sai** | needs real drafts, and a decision about whether the hard cap is right for relational claims specifically |

| J-67 | **T1's span+coverage rule is the new frontier, and the hedge check did not fire (R13 residue).** T1 certifies on an 8-token contiguous span anchored at the claim's SUBJECT plus set-membership coverage, so a long-subject claim has its PREDICATE checked only by "do these words appear anywhere in this source". For RELATIONAL claims that is now moot (they are refused outright), but FACTUAL claims take the same path, and round 13 found a source that explicitly DENIED a statement still satisfying it. **No corpus row has a subject phrase of 8+ tokens, so the corpus cannot detect this class at all.** | Claude | round 14, and corpus rows carrying long subjects (gold labels → Sai) |
| J-68 | **Round 14 must run against the FLAT REFUSAL before launch.** Round 13 attacked the fall-through implementation, which no longer exists. The current state — unconditional relational refusal plus kind-independent figure checks — has never faced an adversary. Two prior implementations in this area were refuted within hours. | Claude | nothing; it is the next session's first item |

## Sai's rulings 2026-10-02 (all recommendations approved)

| id | Ruling | What it changes |
|---|---|---|
| J-54 | **APPROVED — Sai will run it.** Interactive `claude --plugin-dir` → `/hooks` → read a file → `/assure-verify`. | The last launch gate. 2 min, his terminal. |
| J-55 | **APPROVED as recommended: CI is NOT a launch target.** Interactive-only, stated plainly. | No build. The README/SKILL disclosure already shipped IS the fix. Revisit only if a customer asks. |
| J-43 | **APPROVED as recommended: check it, scoped to RELATIONAL claims, via VERBATIM PRESENCE — not a number parser.** | Measured 2026-10-02: FACTUAL is already protected (verbatim containment forces the figure to appear); the hole is RELATIONAL only. Corpus extension needed to measure the Error-A — that half is Sai's (gold labels). |
| J-44 | **REOPENED 2026-10-02 (D-69) — the fix was an ERROR-B and is withdrawn.** `_stem` maps the NOUN "news" to the ADJECTIVE "new", so "The recall causes negative news [S1][S2]" certified GROUNDED / PASS 100.0 against two sources containing no "news". Same class: species/specie, ethics/ethic, damages/damage, lens/len. **No repair stays inside the file** — telling "news"/"new" from "cost"/"costs" is a DICTIONARY fact, and an incomplete blacklist of s-final singulars on a LOOSENING is an Error-B generator. The Error-A is real and stays open: a claim its cited sources assert verbatim is refused over one letter. Two candidate designs, both Sai's: (a) a real morphological analyser — a dependency the verdict path may not import; (b) accept the Error-A permanently and say so on the tin. **The SEAM half of J-44 is closed and stays closed** — there is one definition of containment. | **Sai** | Escalation #1 |
| J-48 | **APPROVED as recommended: documentation, not code.** "Keep authoring notes on one line." | Four designs have lost trying to strip multi-line comments safely. The three strict xfails stay as the record. |
| J-51 | **APPROVED — Sai will add the `install.sh` text.** | 2 lines: mention `--session-id`, and where a session id comes from. His file (Escalation #4). |
| q25 | **APPROVED — Sai will adjudicate.** | One gold label: a causal claim supported by two correlational sources. Never Claude's. |

## Round 14 — opened 2026-10-02, against the code that actually ships

All three reproduced by the orchestrator from the adversary's own fixtures, all
tripwired strict-xfail in `tests/red_team_moat/test_moat_r14_hedge_classifier_absence.py`,
**none repaired.** Each alters which claims can pass, so each is Escalation #1.

| id | Finding | Owner | Blocked on |
|---|---|---|---|
| J-69 | **The flat relational refusal is routed around by ONE WORD (R14-01, CRITICAL).** `ground()` refuses only on `kind == RELATIONAL`, and `classify` sets that only from `_RELATIONAL_RE` — a **ten-member blacklist over an open class** (`causes`, `caused by`, `leads to`, `results in`, `drives`, `because of`, `due to`, `gives rise to`, `is responsible for`, `the reason for`). 22/22 probed ordinary causal expressions route around it. `causes`→`triggered` flips the same sentence on the same store from FAIL/`UNVERIFIED_RELATION`/exit 1 to **PASS 100.0 / GROUNDED / exit 0** against a source reading *"found no evidence that the migration triggered widespread customer refunds"*. **Do NOT fix by extending the lexicon:** J-70 proves the same certification happens with no causal word at all, so lexicon extension closes 22 fixtures and leaves the class open — the comment stripper's five-round pattern. | **Sai** | Escalation #1 |
| J-70 | **THE ROOT CAUSE, and it is kind-independent (R14-04, CRITICAL; supersedes J-67's framing).** T1 anchors its ≥8-token contiguous span at the claim's FIRST content word, so a claim with a long subject matches a span lying **entirely inside its own subject**; the predicate is then checked only by set-membership coverage, and `_span_is_hedged` inspects only the **5 tokens BEFORE** the span. A denial between subject and predicate is never read, and `no` is a `_STOP_WORD` so coverage discards it. **Measured: the SAME denial moved BEFORE the subject refuses (FAIL 0.0); left AFTER it certifies (PASS 100.0).** Reproduced on plain `FACTUAL` with no causal vocabulary, and on a source whose finding was explicitly *withdrawn*. **This is not an exotic attack — "we found no evidence that X" is how real sources report a negative finding, so the shape arises from honest retrieval with no adversarial control of the source.** **PRICED on the n=52 gold corpus:** a whole-source hedge scan closes R14-01 and both R14-04 cases, Error-B stays **0.000**, Error-A goes **0.400 → 0.560** (+4 false alarms / 25 grounded rows). The narrower sentence-scoped variant **cannot be written at that layer**: `_tokenize` strips punctuation, so `_span_is_hedged` receives no sentence boundaries and scoping needs a signature change across its call sites. **No corpus row has a subject phrase of 8+ tokens, so a zero corpus delta here is non-measurement.** | **Sai** | Escalation #1 — it is a priced Error-A/Error-B trade |
| J-71 | **`ABSENCE` returns ABOVE the figure checks, so `numeric_ok` is unreachable for it (R14-03, CRITICAL).** The digit `4200`, present in **no** source text, certifies `ABSENCE_SUPPORTED` at **PASS 100.0 / exit 0**. This is the same class as J-62 (spelled figures) but with digits, and it is the one D-77 was believed to have closed — see the ADR-007 Amendment 2026-10-02C correcting that overclaim. Also open within it: `_extract_absence_anchors` reads only POST-trigger text, so a figure or entity placed before the trigger is checked by nothing. | **Sai** | Escalation #1 (moving the checks above the kind dispatch changes which claims can pass) |

**Recommendation to Sai, with the why.** Fix **J-70**, not J-69. J-70 is the
mechanism; J-69 and J-62/J-71 are its symptoms plus their own gating bugs, and
J-69's tempting repair (add strings to a refusal lexicon) is the exact pattern
that lost five rounds to the comment stripper. The price of the blunt repair is
measured and small on the recoverable side — **+0.160 Error-A, Error-B
unchanged at 0.000** — against a CRITICAL unrecoverable class that arises
without any adversary. **What would flip this:** if real-draft Error-A at 0.560
makes the gate unusable in practice (J-66 is the open question about exactly
that), then the structural repair — giving T1 sentence-scoped source text — is
worth its larger cost instead.

### J-62 + J-71 are ONE class, priced 2026-10-02 — and the price is the cheapest on the table

| id | Finding | Owner | Blocked on |
|---|---|---|---|
| J-62+J-71 | **MERGED. The absence branch's figure hole, spelled (J-62) and digit (J-71) forms, is one defect with one repair.** They were briefly split across two owners, which would have made this register incoherent — one class cannot be half Claude's and half Sai's. **PRICED:** running the two figure checks before the absence verdict closes R14-03a (digit `4200` → `UNVERIFIED_NUMBER`, exit 1) at **Error-A 0.400 unchanged, Error-B 0.000** on the n=52 gold corpus. **Unlike J-70's zero-deltas, this one IS a measurement, not non-measurement:** the corpus holds 7 ABSENCE claims and 2 of them carry a figure (q13, q22), so rows of this shape exist and did not move. **The caveat that matters:** both of those "figures" are product model numbers, not quantities — `X200` extracts as `200`, and `X200 manual` extracts as **`200 m`** — so the corpus exercises the check on an unrepresentative shape. Whether an honest absence claim naming a model number differently from its source would newly fail is **UNVERIFIED**: I predicted it, built the fixture, and the baseline already refused that draft for an unrelated reason, so the test did not isolate the effect. | **Sai** | Escalation #1 — but this is the cheapest measured repair of the three, and the only one with no observed Error-A cost |
| J-72 | **`numeric_tokens` misparses a model number as a quantity-with-unit (NEW, found while pricing J-62).** `X200 manual` yields the numeric token **`200 m`** — the extractor took the model's digits and the next word's first letter as a unit. Direction is fail-closed (it can only refuse), so this is Error-A, not Error-B, and it is why two gold corpus rows exercise the figure path at all. It also means any corpus-measured price for a figure check is partly measured on model numbers rather than quantities. | Claude | nothing; after launch, and it needs its own Error-A measurement |

### WITHDRAWAL 2026-10-02, same night, before anything landed — J-70's priced repair is UNSHIPPABLE

**I recommended the whole-source hedge scan for J-70 on the strength of a
corpus price of +0.160 Error-A. That recommendation is WITHDRAWN.** The
honest-draft harness (`tests/honest_drafts/`) — the Error-A instrument the gold
corpus cannot substitute for — goes from **7 passed / 3 xfailed** to **5 FAILED
/ 2 passed / 3 xfailed** under the same patch:

| honest draft | result |
|---|---|
| `honest-long-verbatim-quote` | **FAILS** |
| `honest-numeric-with-rate-and-quantity` | **FAILS** |
| `honest-full-sentence-with-comparison` | **FAILS** |
| `honest-structured-document-with-headings` | **FAILS** |
| `test_short_verbatim_quotation_should_ground` | **FAILS** |

**A verbatim quotation of the cited source reads UNGROUNDED.** That harness
exists because of exactly this failure (OI-T2-01) and its docstring names it as
"the worst user experience this product can produce". The mechanism is obvious
once measured and invisible before: nearly every real source sentence contains
some `_SPAN_HEDGE_TOKENS` member somewhere, so scanning the WHOLE source makes
nearly every source look hedged.

**Why this matters more than the finding itself.** The corpus said +0.160 — four
extra false alarms out of 25, which reads as tolerable. The honest-draft harness
said five of seven real drafts break, which is not shippable. Same patch, same
hour, two instruments, opposite verdicts — and **the corpus is the one I had
already written into the recommendation.** This is D-68 and D-74's pattern for
the third time in three days: a correct measurement from an instrument that
cannot represent the cost. The only difference tonight is that it was caught
BEFORE landing, by deliberately running the second instrument, which is the
discipline the overnight instrument file was written to enforce.

**REVISED RECOMMENDATION for J-70.** Not the blunt scan. Either:

1. **The structural repair** — give T1 sentence-scoped source text so a hedge is
   read within the span's own sentence rather than across the whole document.
   This is the only option that can close the class without the false-alarm
   blowup, and it is NOT a small change: `_tokenize` strips punctuation, so
   `_span_is_hedged` has no sentence boundaries and the fix needs a signature
   change across its call sites, plus its own adversarial round. **Recommended
   if Agent-Assure's claim is to refuse a claim its source denies.**
2. **Accept the hole and disclose it** — ship with a stated limitation that the
   gate verifies *presence* in a source, not *agreement* with it, and that a
   source denying the claim can still satisfy T1. Cheap, honest, and it keeps
   Error-A where it is. **Recommended if launch timing dominates** — the gate's
   advertised job is traceability, and this makes the boundary explicit rather
   than implied.

**What I will NOT do:** pick between these overnight. Option 1 is a moat
redesign and option 2 changes the product claim; both are Escalation #1 and #4
respectively. **Owner: Sai.**

## ADR-008 shipped — 2026-10-03 day run (D-80). The claim changed; the engine did not.

| id | Finding / work | Owner | State |
|---|---|---|---|
| J-73 | **Every report states its own scope.** A `scope` field on the report plus a line on the human CLI path, printed on every verdict — not a README footnote, because trust RISES with citations even when the citations are random (Ding et al., AAAI 2025), so a disclosure the reader never opens does not spend that trust back. **Two variants:** the research's recommended wording said "retrieved this session", which per **J-56** the gate may not claim without `--session-id`; shipping it unconditionally would have been a fresh overclaim inside the fix for overclaiming. Neither variant contains "verified" or "verify". | Claude | **DONE** `a7c0e62` |
| J-74 | **`support_diagnostic` — the contradiction signal as a MEASUREMENT.** Sentence-scoped on the RAW source text (which keeps punctuation, unlike `_span_is_hedged`'s token list — the measured reason J-70's narrow repair cannot live at that layer). Reuses `_SPAN_HEDGE_TOKENS` rather than inventing a lexicon (a new list owns new gaps — J-44 was that bill). Emitted for EVERY claim, not gated on kind, because R14-01 proved a kind-gated check is routable by one word. **Flags both round-14 CRITICALs that still certify at PASS 100.0.** Fire rate PUBLISHED not tuned: **26.7% of claims the gate passes** are false alarms. AST-guarded against all six verdict functions. | Claude | **DONE** `3ba4216` + `49d1bfa` |
| J-75 | **Claim surfaces say what PASS does not mean** — and **two stale error rates corrected**: `README.md` and `SKILL.md` still quoted Error-A 0.320 / CR-004 after ADR-007 raised it to 0.400, understating the user's cost by a fifth on the two documents read first. Verdict NAMES untouched: closed taxonomy, renaming needs an ADR. | Claude | **DONE** `26bfd0a` |
| J-76 | **The support diagnostic's RECALL is unmeasured.** 26.7% is its FALSE-ALARM rate; how often it MISSES a denying source is unknown, and the gold corpus cannot say — no corpus row has the long subject phrase R14-04 needs. Round 15 was dispatched against exactly this. **Do not quote the diagnostic as catching the agreement gap; quote it as reporting what it can detect.** | Claude | open — needs round 15's answer, then corpus rows carrying long subjects (gold labels → **Sai**) |
| J-77 | **A commit was made on a RED gate with a message stating a false result** (`3ba4216`, corrected in `49d1bfa`). Cause recorded rather than smoothed: the pre-check grepped for a top-level report key set and not a PER-CLAIM one — one KIND of search where the standing order requires three. `test_per_claim_fields` worked exactly as designed; the process around it did not. **No code fix. The lesson is the artifact.** | Claude | recorded, closed |
| J-78 | **`/tmp/claude-501` holds 2.1 GB, and 1.9 GB of it belongs to OTHER projects** — `ival_2.0` 1.3G, `iPay` 600M, `Agents-Claude` 111M, `attestor` 97M. **NOT deleted by this run:** a session may be live in any of them and destroying another session's working state is a one-way door. Command for Sai, to run or decline: `du -sh /tmp/claude-501/*/ \| sort -rh` then `rm -rf /tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-ival-2-0` (and siblings) **only when no session is live in that project**. **Measured, not assumed: this repo is 18M with no file over 1MB, so there are no large datasets to move to drive or cloud.** | **Sai** | queued — one-way door |

### Round 15 — 2026-10-03, against the surfaces that landed the same morning

**0 CRITICAL. Attack 1 found nothing across 215 pairs:** `session_scoped=True`
vs `False` is byte-identical once `scope` is popped, `per_claim` verdicts equal
direct `ground()`, no mutation, no crash, deterministic. **The display-only
property of both deliverables held under attack** — that was the run's primary
risk and it is now evidence rather than intention.

| id | Finding | Owner | State |
|---|---|---|---|
| R15-01 | **HIGH — J-56's overclaim reproduced BY the J-73 disclosure built to prevent it.** `--session-id ""` scored the shipped demo store at PASS 100.0 and printed the session-scoped wording over records carrying no session data. `assert_single_session` compares `source.session_id != session_id`, so a blank expected id against blank record ids evaluates `"" != ""`, finds nothing foreign, and returns — **while its own docstring already promised "An EMPTY session_id is UNATTRIBUTABLE and also raises."** A docstring asserting a property the code lacks, which is the exact class ADR-008 exists to prevent. **FIXED systemically in `assert_single_session`, not in the CLI**: the emptiness of the expected id is a fact about the REQUEST, so no comparison against the store can establish it and the guard must be explicit and first. Fail-closed. PROVEN-RED 4/5. | Claude | **FIXED** |
| R15-02 | **HIGH — my own published number was wrong, in a CR about a diagnostic's error rate.** CR-009 read `7/27 = 0.259` using the labelled-VIOLATION denominator; gold is **25 grounded / 27 violation**, so it is **7/25 = 0.280**. Round 15 reproduced the 26.7% headline, the 10/52, Error-A 0.400 and Error-B 0.000 exactly — this one row was wrong. | Claude | **CORRECTED** |
| R15-03 | **DOC-DEFECT — README documented T2 as LIVE** at `lex_tau` 0.71 with a working `--lex-tau` override, a month after ADR-006 retired it and the flag began exiting 2. Corrected to state the demotion, why it happened, and the current operating point. | Claude | **CORRECTED** |
| R15-04 | **DOC-DEFECT — README's "every captured record now carries a `session_id`" masked the hole R15-01 used.** Records written before the field existed carry a blank one. Corrected, and reworded to avoid the retired phrase rather than widening the guard's escape hatch. | Claude | **CORRECTED** |
| J-79 | **The support diagnostic has four demonstrated MISS vectors — all missed WARNINGS, nothing is refused, so none is Error-B.** (a) the denial sits one sentence away from the highest-overlap sentence; (b) the denial is inside the inspected sentence but in words absent from `_SPAN_HEDGE_TOKENS` — `debunked`, `erroneous`, `retracted`; (c) **the equal-overlap tie-break discards the denying sentence, so sentence ORDER in the source flips the flag**; (d) `per` is a hedge token, so every "operations per second" claim fires **for the wrong reason** — which means part of the published 26.7% false-alarm rate is this artefact and not genuine ambiguity. **Deliberately NOT fixed:** (b) is a lexicon, and a list licensing an ACCEPTANCE makes its own gap the attack — the J-44 lesson — while (a), (c) and (d) are the same structural limit the recorded `CEILING:` names. The honest upgrade is J-70, which is Sai's. | Claude (characterised) + **Sai** (J-70 is the real fix) | open, tripwire-worthy |

### J-62+J-71 CLOSED 2026-10-03 under Sai's GO — and it masked a J-33 tripwire on the way

| id | Outcome |
|---|---|
| **J-62 + J-71** | **CLOSED.** The two figure checks now run before the absence verdict, verbatim-only (a summary may refuse, never certify — R10C-03), against `store.values()` rather than citations because an absence claim is checked against what was SEARCHED and often cites nothing at all. Strictly fail-closed. **Measured: Error-A 10/25 = 0.400 and Error-B 0/27 = 0.000 UNCHANGED**; 2 of the corpus's 7 ABSENCE rows carry a figure, so the zero delta is a measurement, not non-measurement. R14-03a's strict-xfail tripwire converted to a passing test. |
| **J-33** | **STILL OPEN — and it nearly stopped looking that way.** The fix made the J-33 absence tripwire XPASS, which under strict xfail reads as "fixed". It was not: the draft's subject is `the X200 drone`, `X200` extracts as the numeric token `200` (**J-72**), `200` appears in no source, and the claim was refused as `UNVERIFIED_NUMBER` **while the marker was still never checked.** D-46, caught by its own forcing function. |
| **J-80** | **A `gate != "PASS"` assertion cannot tell refused from refused-for-the-right-reason — and that is a class, not an incident.** My first repair of the J-33 tripwire dropped the model number from the subject; that introduced a SECOND mask, because the store's queries read `recall evidence search X200 drone` and a subject of `the drone fleet` no longer matched the query ledger, so it was refused as `UNVERIFIED_ABSENCE` instead. Two different wrong reasons in one afternoon. The fixture was never the problem. **Repair: assert the VERDICT, not the gate.** The J-33 tripwire now requires `verdict == "UNVERIFIED_CITATION"`, so it xfails today and will XPASS only when the citation is what refuses it. **Sweep every other `gate != "PASS"` tripwire for the same weakness** — a refusal-only assertion is satisfiable by any unrelated fail-closed change. | Claude | open — the sweep is the work |
| **J-72** | **Promoted from "after launch".** It is no longer only an Error-A curiosity: the model-number misparse is now load-bearing in two places — it is what masked J-33, and it is what two of the corpus's ABSENCE rows exercise the new figure check with, so the measured zero delta for J-62+J-71 rests partly on a misparse rather than on a quantity. | Claude | open, raised priority |

### J-80 swept 2026-10-03 — measured, with the remainder named

**AST sweep of every `xfail` tripwire in the suite: 10 assert only a non-PASS
gate; 13 also assert a verdict or a diagnostic.** A gate-only assertion is
satisfiable by ANY unrelated fail-closed change, which is how J-62+J-71's figure
check made an open J-33 finding read as closed.

**Strengthened (3 — mine, written 2026-10-02, guarding CRITICAL classes):**
`test_a_causal_claim_its_source_DENIES_is_refused_whatever_verb_it_uses` and
`test_a_factual_claim_its_source_denies_or_withdraws_is_refused` now assert
`verdict != "GROUNDED"` (the finding is "it certifies", so only a non-certifying
verdict expresses closure); `test_a_fabricated_magnitude_spelled_with_one_is_refused`
now requires `verdict == "UNVERIFIED_NUMBER"`, because any other refusal would
mean the spelled-figure guard is still blind and something else caught the draft.

**NOT touched (7), deliberately — each needs its own judgement about what its
"right reason" verdict IS, and a blanket edit across tripwires I did not author
is how four unrelated calibrate rows were damaged on 2026-10-02:**

| Tripwire | The question to answer before strengthening it |
|---|---|
| `test_moat_j27::test_a_genuine_multi_line_comment_is_still_stripped` | What verdict means "the comment was stripped" rather than "the draft failed"? |
| `test_moat_oi_moat_21::test_verb_synonym_claim_must_still_ground` | This one expects a PASS, so the weakness is inverted — it needs `verdict == GROUNDED`, not a non-PASS gate. |
| `test_moat_r10c03::test_summaries_cannot_supply_the_distinct_searches` | `UNVERIFIED_ABSENCE` for the query-count reason, vs for the verbatim-basis reason — the two are different findings. |
| `test_moat_r8_display_open` (×2) | Both are DISPLAY findings; the right assertion is on `evidence_basis` text, not on any verdict. |
| `test_moat_r9::test_absence_control_with_real_citations_still_passes` | A control expecting PASS — same inversion as the oi_moat_21 row. |
| `test_moat_red_team_r4::test_verb_final_header_must_not_escape_denominator` | The property is about `scored_claims`, not about the gate at all. |

| id | Work | Owner | State |
|---|---|---|---|
| J-80 | 3 of 10 strengthened; **7 named above with the specific question each needs answered.** The two marked "inversion" are the interesting ones: a control that expects PASS is weakened by a gate-only assertion in the OPPOSITE direction — it would keep passing if the gate started certifying for a wrong reason. | Claude | open — 7 remain, one at a time |

### J-80 corrected twice, and the X200 family unravelled — 2026-10-03 afternoon

**MY OWN CENSUS WAS WRONG TWICE, in the same direction, and that is the finding.**
The first AST sweep reported **10** gate-only tripwires; it matched only literal
dict keys in a test's own body, so any test whose strong assertion lives in a
HELPER was misreported as weak. The second sweep followed helpers and reported
**3**; it still missed `test_moat_j27`, because my own keyword list did not
include `per_claim`. **The real count is 2.** A control correct about what it
examines and silent about what it does not — this estate's signature defect,
committed by the audit tool written to find it. `test_moat_j27`'s helper has
asserted the right property all along, and says so in its docstring.

| id | Finding | Owner | State |
|---|---|---|---|
| J-80 | **CLOSED.** The 2 genuinely weak tripwires are strengthened to assert the VERDICT: `test_summaries_cannot_supply_the_distinct_searches` now requires `UNVERIFIED_ABSENCE` (its finding is the query count, so any other refusal means something else fired first), and the J-31 control is superseded by an instrument that asserts `ABSENCE_SUPPORTED`. The other 8 were already strong. | Claude | **DONE** |
| J-81 | **`[SA1]` IS NOT A CITATION, and a whole fixture family was built on the assumption that it is.** `_CITATION_RE` is `\[(?:S\d+[a-zA-Z]*\|source:[^\]]+)\]` — `S` then DIGITS — so `[S1]`, `[S1a]` match and `[SA1]` does not. `test_moat_r9`'s absence store names its sources **`SA1`/`SA2`: ids that can never be cited.** Two consequences: the markers stay in the claim text, and their digits become numeric tokens (`('200','1','2')` for that draft); and since J-62+J-71 reached the ABSENCE branch, the claim is refused as `UNVERIFIED_NUMBER` while `check_absence` alone still returns `UNVERIFIED_ABSENCE`. **The figure check masked the original mechanism** — the third masking instance of the day. The old tripwire is kept and annotated (its xfail is the historical record of how J-31 was first reported), superseded by a correct instrument. **Sweep every other fixture for source ids that cannot be cited.** | Claude | open — the sweep is the work |
| J-31 | **CONFIRMED REAL, not a fixture artefact — and re-specified.** With citable ids the same absence claim is `ABSENCE_SUPPORTED` uncited and `UNVERIFIED_ABSENCE` when it cites the two sources that support it. `numeric_tokens` is `('200',)` in BOTH and `200` is present in S2's text, so the figure check does not fire and cannot be what refuses it. The gate penalises the one behaviour the product asks authors for. Error-A, fail-closed, no moat breach. | Claude | open, now with an honest instrument |
| J-72 | **Second mechanism found.** Beyond `X200` → `200` and `X200 manual` → `200 m`, an UNRECOGNISED citation marker leaks its digits into `numeric_tokens` (`[SA1][SA2]` → `('1','2')`; `[S7]` and `[S12][S34]` correctly strip). So an author adding a marker the gate does not recognise changes the claim's numeric content — and since this morning, on the absence path, that can decide the verdict. | Claude | open, raised again |
