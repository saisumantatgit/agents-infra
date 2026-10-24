# CSTC-001-L: Building a Mechanical Fabrication Detector for AI Research — Fourteen Days, Three Real Bugs, One Self-Correcting Blind Spot
## From zero to a calibrated, adversarially-tested grounding gate: 46 commits, 326 tests, and the discovery that the calibration corpus itself needed independent verification

---

## Metadata

| Field | Value |
|-------|-------|
| **Case ID** | CSTC-001-L |
| **Organization** | agents-infra (AI agent governance CLI suite), Agent-Assure product |
| **Domain** | AI agent tooling — mechanical fact-verification for LLM-generated research |
| **Time Period** | 2026-06-20 to 2026-07-04 (14 calendar days, non-continuous — build paused at least twice on stated budget/sequencing decisions) |
| **Author(s)** | Sai Sumanth Battepati (direction, review, sole ground-truth labeler) — Claude (Opus 4.8 through 2026-07-03, Sonnet 5 from 2026-07-04) implementing across multiple sessions |
| **Status** | Draft |
| **Short Form** | None yet |

---

## Abstract

Agent-Assure is a plugin that mechanically proves every claim in an AI-generated research report is grounded in a source the agent actually retrieved during that session — not merely a source that exists, but one that was fetched, and whose text supports the specific claim. The core problem: LLM citation hallucination sits at 11-57% depending on domain, and existing citation checkers verify that a cited path exists on disk, not that the cited text says what the claim says. Built over 14 days across 46 commits, the system now passes 326 automated tests and, in its first calibration run against 12 hand-labeled claims, derived a grounding threshold of 0.71 (up from an admittedly-unvalidated 0.65 default) with a held-out false-negative rate of 14.3%. Three real defects were caught during the build, not before it: a header-wrapped fabrication that bypassed the entire gate, three of four assumed data-capture formats that were simply wrong when tested against a live session, and — during calibration itself — a structural weakness in the relational-claim checker that let two unrelated true facts pass as a causal claim. That last finding surfaced only because the labeling process was designed to resist the same anchoring bias it was built to catch, and it was independently confirmed by three blind AI judges before being accepted rather than dismissed as a data-entry error.

---

## Glossary

| Term | Definition |
|------|-----------|
| **EvidenceStore** | The JSONL log of every source an agent actually retrieved during a session (web fetches, file reads, search results), written by a hook as retrieval happens — the ground truth against which claims are checked. |
| **Grounding gate** | The deterministic (no-LLM) engine that decomposes a draft into individual claims, classifies each, and checks each against the EvidenceStore. |
| **T1 / T2 / T3** | Three planned tiers of support-checking: T1 = exact verbatim span match; T2 = lexical/content-word overlap above a threshold; T3 = semantic (NLI-based) entailment, not yet built. |
| **lex_tau** | The T2 lexical-overlap threshold. A claim needs at least this much content-word overlap with a source to count as T2-grounded. Started as an admittedly unvalidated default of 0.65. |
| **Error A / Error B** | The two ways a grounding verdict can be wrong. Error A: a genuinely-grounded claim gets flagged as a violation (recoverable — a human sees an unnecessary flag). Error B: a genuinely-fabricated claim gets marked grounded (unrecoverable — a fabrication ships inside a report labeled "verified"). |
| **RELATIONAL claim** | A claim asserting a causal or comparative relationship between two things ("X drives Y," "X causes Y"), checked by a rule requiring each side to be independently supported by a source. |
| **Leave-one-out (LOO)** | A validation method where a threshold is chosen using every labeled example except one, then tested against that held-out example — repeated for every example, to catch a threshold that only looks good because it was tuned on the data it's being graded against. |
| **Calibration Record (CR)** | A short, size-capped document recording a threshold-derivation run: the provisional value, the derived value, and the honestly-reported held-out error rates. |

---

## 1. Context

### 1.1 Background

Agent-Assure is one of six plugins in agents-infra, a CLI suite providing lifecycle governance for AI coding and research agents (siblings: PROVE for pre-execution thinking validation, Cite for citation auditing, Trace for blast-radius mapping, Drift for intent-drift detection, Scribe for governance docs, Litmus for test-quality analysis). Agent-Assure's stated purpose is to replace reliance on a third-party deep-research skill by making the eventual output mechanically provable: every claim in a report either traces to a real, session-retrieved source that actually supports it, or is explicitly flagged.

### 1.2 The Problem Being Solved

Two failure modes converge in AI-generated research: the model can cite a source that was never actually retrieved (fabricated citation), or cite a real, retrieved source whose text simply doesn't say what the claim says (misattribution). A path-existence checker — verifying a citation points to a file that exists — catches neither. The design work preceding this build explicitly quantified the gap against a sibling tool: "Cite proves a cited path exists on the file system; Assure proves the citation target was retrieved this session and its text supports the claim" — two different ground truths, not a superset relationship.

### 1.3 The Protagonist

Sai Sumanth Battepati directed the build across multiple sessions, made every scoping and sequencing decision (build the gate before the research pipeline; Claude-Code-only for v1; defer the NLI tier), and was the sole human labeler for the calibration ground truth — a role the design explicitly could not delegate to the AI building the system, since an AI labeling its own gate's output is circular by construction.

---

## 2. The Challenge

The differentiated value of a grounding gate is also its highest-stakes failure surface: if the gate is wrong in the permissive direction (a fabrication passes), it is worse than having no gate at all, because a report stamped "verified" carries false authority. The build therefore had three intertwined technical challenges, not one:

1. **Build a claim-decomposition and classification engine** that correctly identifies what kind of claim each sentence makes (a factual assertion, a number, an absence claim, a causal relationship) without an LLM in the loop, because an LLM-based classifier would reintroduce the same hallucination risk the gate exists to catch.
2. **Build a capture mechanism** that reliably records what an agent actually retrieved, in an environment (Claude Code's hook system) whose exact data shapes were not fully known in advance — assumptions here could not be verified without running against a live, real session.
3. **Calibrate the resulting thresholds** against real human judgment, while avoiding the trap the design itself named: an AI cannot generate its own ground-truth labels, because "AI labeling AI's own grounding" is circular and would validate nothing.

---

## 3. What Was Done

### 3.1 Phase 1a — The Grounding Engine (2026-06-20 to 2026-06-21)

Nine feature/fix commits (`d693f1a` through `364dd16`) built the core: EvidenceStore data model, claim decomposition (sentence segmentation + conservative conjunction splitting), claim classification into six kinds (FACTUAL, NUMERIC, ABSENCE, ATTRIBUTION, RELATIONAL, NON_CLAIM), the T1/T2 support tiers, the relational-claim checker, the report-level scoring function, and a CLI entry point. A whole-branch final review (`8661512`) then caught something none of the per-task reviews had: a verbless, header-wrapped, or purely narrative-looking sentence carrying a real citation or a real number was being excluded from scoring as "not a claim" — meaning a fabricated number wrapped in a markdown header, or stated without a verb, could pass through the entire denominator uncounted. Fixed in `32be315`. This was not a hypothetical: the fix's own regression test is named for the exact failure it closes.

### 3.2 Phase 1b/1c — Live Capture and Packaging

The capture hook (`5155b55` through `bf96641`) writes the EvidenceStore as an agent's tool calls happen. Every payload-shape assumption made during design was checked against a real, headless Claude Code session before being trusted — and three of the four assumed shapes were wrong. The `Read` tool's payload was assumed to carry a line-numbered ("cat -n" style) rendering; it does not — it's the raw file text, and a `strip_cat_n_prefix` function built to undo the assumed formatting had to be deleted. Truncation of long tool output was assumed to be offloaded to a separate preview/file-path structure; it is inline, under a `truncatedByTokenCap` field. `WebFetch`'s response was assumed to be a raw string; it's wrapped in a `{result: str}` envelope. Only the Exa search tool's shape matched the original assumption. Separately, `.claude-plugin/hooks.json` — the file registering the hook — was silently ignored by the plugin loader entirely; it had to be relocated to `hooks/hooks.json` before the hook fired at all. All of this was fixed in one commit (`bce055b`) after the live-validation pass this whole PR had been deliberately held open to force. Packaging (plugin manifest, the `/assure-verify` command, an offline demo) followed in `2dc08b2`.

### 3.3 Phase 2a — The Calibration Harness (2026-06-27 to 2026-07-03)

Ten commits (`680b530` through `80340ce`) built the machinery to turn hand-labeled claims into derived thresholds: per-claim feature emission, a labeling-CSV export with fail-loud ingestion (an unlabeled or invalid label raises rather than silently defaulting), the Error-A/Error-B metric with the positive class pinned to "this claim is a violation" (not the more common but wrong choice of accuracy or F1, which would weight a recoverable false alarm equally against an unrecoverable fabrication passing as verified), a moat-integrity operating-point selector that picks the lowest Error-A among thresholds meeting an Error-B bound — and raises rather than silently degrading if no threshold clears the bound — leave-one-out held-out validation, report-gate derivation, and Calibration Record emission. A whole-branch review here caught a second cross-task seam bug invisible to every individual task review: claims decided by rules that never consult the lexical threshold (relational and absence claims) were being marked "sensitive to that threshold" anyway, which would have reported a completely fictional protection in the eventual Calibration Record.

### 3.4 The First Calibration Run (2026-07-03 to 2026-07-04)

With the harness proven, a 12-claim bootstrap corpus was built spanning every violation class the gate handles, run through `emit_claim_features`, and handed to Sai for independent, blind labeling — deliberately excluding the gate's own predicted verdict from what the labeler saw, to prevent anchoring on the very verdict being validated. Two things happened during this pass that the harness alone could not have caught.

First, the labeler flagged an absence-claim row as a violation with no evidence to judge from — because the CSV export had genuinely omitted the actual evidence for that claim kind (the session's search queries, not a citation) — exposing a real gap in the corpus tooling, not a labeling mistake. Fixed, and the row was re-shown with the real evidence before being finalized.

Second, the labeler flagged a relational claim as a violation that the mechanical rule had marked grounded. Rather than accept or dismiss this on either side's word, three independent AI agents were given only the claim and its two cited sources — no access to the mechanical verdict or the human's reasoning — and asked to judge blind. All three converged on the identical diagnosis: the two sources each independently confirmed one half of the claim, but neither ever asserted the causal relationship the claim made. The mechanical rule's "two distinct sources" check was satisfied by mere co-occurrence, not by anything establishing the claimed relationship.

The threshold sweep itself surfaced a third finding: an error bound chosen from the full-sample error floor worked when tested against all 12 claims at once, but broke leave-one-out validation, because removing any other true-violation claim from a fold's training set shrank that fold's violation count enough that the one fixed miss above cost a larger fraction of it. The bound had to be widened, and the fix was confirmed by re-running the validation, not by re-deriving the arithmetic by hand.

---

## 4. Evidence and Results

**Exhibit 1 — Build timeline and volume**

| Metric | Value | Source |
|---|---|---|
| Elapsed calendar time | 14 days (2026-06-20 to 2026-07-04), non-continuous | `git log` first/last commit dates, `Agent-Assure/` path |
| Total commits | 46 (45 merged to `main`, 1 on the calibration branch) | `git log --oneline --all -- Agent-Assure/` |
| Test count, start | 0 | Repo did not exist before 2026-06-20 |
| Test count, Phase 1a complete | 134 | Phase 1a final review |
| Test count, post-live-validation | 222 | `bce055b` commit report |
| Test count, current `main` | 326, all passing | Verified directly: `uv run pytest -q` → `326 passed in 6.22s` |
| Test count, calibration branch (uncommitted to main) | 327 | Includes one proven-red-then-fixed regression for a duplicate-label-ID bug found this session |

**Exhibit 2 — Named defects found and fixed during the build (not before it)**

| Defect | Class | Found by | Fixed in |
|---|---|---|---|
| Verbless/header-wrapped claim with a real citation or number silently excluded from scoring | Moat bypass — CRITICAL | Whole-branch review, Phase 1a | `32be315` |
| Same class of bug, specifically for markdown-header-wrapped claims | Moat bypass — CRITICAL | Adversarial final review | `e01c58e` |
| 3 of 4 assumed hook payload shapes wrong (Read, truncation, WebFetch); hook registration file silently ignored by the plugin loader | Live-capture correctness | Deliberate live-validation pass against a real session, held open until run | `bce055b` |
| Claims decided by threshold-independent rules (relational, absence) incorrectly marked "threshold-sensitive" | Calibration integrity | Whole-branch review, Phase 2a | `ff24a82` |
| Duplicate claim IDs in a labeling file silently overwrote an earlier human label with no signal data was lost | Data-integrity | This session, proven red before fixing | committed alongside the calibration run |
| Relational two-source check satisfied by co-occurrence, not by any source asserting the claimed relationship | Moat weakness — open | Independent human label + 3/3 blind AI judges, this session's calibration run | Not yet fixed — logged as an open design item |

**Exhibit 3 — First calibration result (CR-001)**

| Metric | Provisional (unvalidated) | Derived (n=12, held-out) | Delta |
|---|---|---|---|
| `lex_tau` (T2 threshold) | 0.65 | 0.71 | +9.2% |
| Report-level gate | 0.90 | Deferred — corpus can't support derivation yet (see §5) | — |
| Error-A (recoverable false alarm), held-out | — | 0.20 | — |
| Error-B (unrecoverable missed fabrication), held-out | — | 0.143 | — |

---

## 5. Analysis and Lessons

### 5.1 What Worked

**Holding a PR open specifically to force live validation, rather than trusting design-time assumptions, is what caught the payload-shape bugs.** Three of four assumed data shapes were wrong. None of these would have been caught by unit tests against synthetic fixtures, because the fixtures were built from the same wrong assumptions the live capture code was built from — testing an assumption against itself proves nothing. The only thing that surfaced the gap was running against a real session and reading the actual bytes.

**Whole-branch review catches a category of bug that per-task review structurally cannot.** Twice in this build (Phase 1a's header-bypass, Phase 2a's threshold-sensitivity tagging), a defect was invisible to every individual task's review because each task's diff looked locally correct — the bug lived in the interaction between two tasks' assumptions, not inside either task. This is not a claim that per-task review is worthless; it's a claim that it is insufficient alone, and a final integration-level pass is not optional overhead.

**Adversarial verification with independent, blind judges is not theater when the judges genuinely have no access to the thing being verified.** The relational-claim finding depended entirely on the three verifying agents having zero visibility into the mechanical verdict or each other's reasoning. Had any of them seen the gate's "GROUNDED" verdict first, the risk of anchoring on it — reasoning backward to justify a verdict already seen — would have been real. The design decision to withhold that verdict from the human labeler for the identical reason turned out to matter for the AI verifiers too.

### 5.2 What Failed (or Nearly Did)

**The calibration corpus itself was authored by the same system it calibrates, and this created a real, if narrower, version of the exact circularity problem the design had already named for labels.** The design correctly identified that an AI cannot generate ground-truth *labels* for its own output — that's why a human did the labeling. But the *examples themselves* (the synthetic claims and sources) were still hand-authored by the AI, with wording iteratively tuned against the live scoring function until each example hit its intended verdict. That process is legitimate for proving the harness runs end-to-end, which it does. It is a real weakness for anything claiming to represent genuine field variance, because a corpus built with foreknowledge of the exact mechanism can be shaped by that foreknowledge in ways neither the builder nor a single reviewer would necessarily notice. This was surfaced honestly in the build's own documentation rather than smoothed over, and it is the single largest open question blocking the next calibration round.

**An error bound that looks safe against the full sample can be unsafe against a leave-one-out fold, and this is easy to miss without actually running the validation.** The in-sample floor for the false-negative rate was 1-in-7; a bound just above that floor felt like a safe, well-reasoned choice. It broke the first time it was tested against genuinely held-out folds, because a small sample means removing even one more example from a class shifts that class's error rate more than intuition suggests. The fix — widening the bound — was correct, but the *process* that found the problem (running the validation rather than trusting the arithmetic) is the actual lesson; the specific numbers are an artifact of this particular 12-claim corpus and will not generalize.

**A "clean, correctly-grounded" design example turned out to be the opposite once independently checked.** The relational-claim example was authored and documented, before any human saw it, as a textbook case of correct two-source grounding. It was wrong. The mechanism that caught this — independent human judgment plus three blind AI verifiers, none primed by the author's stated intent — is the same mechanism the whole gate exists to provide for research claims generally. The build accidentally became a live demonstration of its own thesis: unverified self-assessment misses things that independent verification catches.

---

## 6. Transferability

**Applies when:** building any system whose job is to catch a specific category of error, where the builder is also capable of unconsciously constructing test material that avoids exactly the errors they know to avoid. The mitigation — independent labeling, blind verification, and withholding the system's own verdict from whoever is judging it — generalizes to any fact-checking, content-moderation, or anomaly-detection system, not just citation grounding.

**Applies when:** a capture or integration layer depends on a third-party platform's exact data shapes, and those shapes are not fully documented or stable. The mitigation is not "write more unit tests" — it is "hold the merge open until the assumption is checked against one real, live run," because synthetic fixtures built from a wrong assumption will pass tests built from the same wrong assumption.

**Does not apply, or applies more weakly, when:** the validation sample is large enough that leave-one-out fold variance is negligible — the small-n LOO fragility finding here (§5.2) is a small-sample artifact, not a general property of leave-one-out validation itself. Do not generalize "our bound broke at n=12" into "leave-one-out bounds are generally unreliable" — the correct generalization is narrower: verify any bound against genuinely held-out folds before trusting it, especially at small n.

**Scope:** the specific two-source-corroboration weakness found in the relational-claim checker (Exhibit 2, last row) is a transferable pattern for any system that verifies a compound or causal claim by checking its parts independently rather than checking whether any source actually asserts the connection between them — documented separately as a standalone engineering insight (INS-019, Config Management HQ insights log) because it is not specific to this codebase.

---

## 7. Takeaways for Future AI-Directed Builds

1. **A held-open PR gate ("do not merge until live-validated") is a cheap, high-value control** for any capture/integration code whose correctness depends on a live external system's exact behavior. It cost one delayed merge and caught three real bugs that no amount of additional unit testing would have found.
2. **Whole-branch review is not redundant with per-task review — budget for both, deliberately**, on any build where individual tasks compose into a mechanism whose correctness depends on the composition, not just the parts.
3. **When a human is asked to independently verify an AI-authored artifact, do not show them the AI's own conclusion first.** This was applied once by design (withholding predicted verdicts from the labeler) and once by accident becoming a second, load-bearing instance (the blind AI verifiers) — both times it is what surfaced a real finding rather than a rubber stamp.
4. **A system that generates its own test/calibration data, even when a human supplies the final labels, still carries a narrower version of the circularity problem the human-labeling step was meant to solve.** Name this limitation explicitly in the documentation rather than let a partial fix (human labels) create false confidence that the whole problem is handled.
5. **When a validated threshold is chosen at small n, treat the number as directional and the *process* as the deliverable.** The specific `lex_tau=0.71` here should not outlive the 12-claim corpus that produced it; the sweep → leave-one-out → honest-reporting pipeline that produced it should.

---

## Source Index

| # | Claim | Source | Confidence |
|---|---|---|---|
| 1 | 11-57% citation-hallucination band; Cite/Assure ground-truth distinction | `docs/superpowers/specs/2026-06-20-agent-assure-design.md` (Config Management HQ) | High — primary design document |
| 2 | Build timeline, commit count, commit messages | `git log --oneline --all -- Agent-Assure/` in `agents-infra`, run directly for this case study | High — direct repository inspection |
| 3 | Test counts (134, 222, 326, 327) | Prior session reports (134, 222) + direct verification this session (`uv run pytest -q` → 326 passed on `main`) | High for 326 (directly re-run); medium for 134/222 (prior session's own reported figures, not independently re-verified against historical commits) |
| 4 | Header-wrapped fabrication bug and fix | Commits `32be315`, `e01c58e` | High — commit messages + prior session's documented root-cause analysis |
| 5 | Live-validation payload-shape corrections | Commit `bce055b` and its accompanying validation report from the session that ran it | High — direct commit + prior session's first-hand test report |
| 6 | Calibration harness whole-branch finding (`tier_sensitive` mis-tagging) | Commit `ff24a82` | High — commit message + this session's own reading of `calibrate.py`'s `_LEX_TAU_GOVERNED_KINDS` guard |
| 7 | 12-claim bootstrap corpus, labeling process, and the two findings (absence-evidence gap, relational over-association) | `calibration/build_corpus.py`, `calibration/labeling.csv`, `calibration/CR-001-bootstrap-lex-tau.md` (this session, `agent-assure-calibration` worktree, commit `86a7f46`) | High — authored and run directly in this session, independently re-verified via 3 blind adversarial judge subagents |
| 8 | Small-n leave-one-out bound failure and fix | `calibration/run_calibration.py` module docstring + direct execution log, this session | High — reproduced by running `loo_operating_point` live, not derived by hand |
| 9 | Relational-checker weakness as a transferable pattern | HQ `docs/insights/insights-log.md`, INS-019 | High — same evidence as row 7, cross-referenced |
