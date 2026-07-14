# Insights Log — Agents Infra

> Cross-cutting observations captured during development. See TEMPLATE.md for entry format and graduation criteria.

---

### [2026-07-08] Citation regex silently rejects letter-suffixed source IDs

**Category:** gotcha
**Source:** session observation (α1 corpus build)
**Products affected:** Assure

**Insight:**
The claim-decomposition citation regex accepts only `[S\d+]`-shaped markers; a letter-suffixed ID like `[S12a]` is not matched, so the citation silently detaches and the claim is misclassified (e.g. NUMERIC/UNCITED from the bracket digits). A validation gate that silently narrows its input class is a fail-quiet seam in a fail-loud system.

**Evidence:**
α1 corpus build 2026-07-08: an early multi-source relational fixture using `[S12a]`/`[S12b]` lost its citations and misclassified; fixed by numeric-only IDs (see `docs/plans/reports/ALPHA1-EXECUTION-REPORT.md`). Case resolution applied; systemic fix (widen regex or fail loud on near-miss brackets) is an open item in the 2026-07-08 logbook.

**Graduation target:**
- [ ] Sub-project `CLAUDE.md` — if it is product-specific (Assure Gotchas, once the systemic fix lands or is ADR-rejected)

### [2026-07-08] Judgment-in-the-spec lets executors drop a tier without quality loss

**Category:** pattern
**Source:** session observation (Fable→Opus/Sonnet handoff)
**Products affected:** suite-wide (orchestration practice)

**Insight:**
When the spec carries the decisions (failure-mode taxonomy, invariants, escalation triggers, checkable exit criteria) and the executor carries only assembly + verification, agents one tier down produce discipline-conformant work on the first pass. The measurable tell: red-first tests actually proven red, and fail-loud catches surfaced instead of papered over.

**Evidence:**
2026-07-08 session: 4 parallel agents (2 Opus, 2 Sonnet) against Fable-authored specs; zero re-dispatches, zero refutations, 2 unsolicited fail-loud catches (missing `calibration-plan.md`; gitignored `.claude/skills/`). Telemetry in the 2026-07-08 logbook.

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions or Gotchas — if it is a cross-cutting rule (candidate for the global model-routing table's operating rules after a second validating session)

### [2026-07-12] A verification gate's own test suite cannot measure its moat

**Category:** principle
**Source:** session observation (26-agent red-team sweep + hand reproduction)
**Products affected:** Assure (generalizes to any verification/safety gate)

**Insight:**
A gate's test suite encodes its authors' threat model, so it structurally cannot
find the attack the authors never imagined — it verifies that intended mechanisms
behave as intended, which is the authors agreeing with themselves. The moat's
*actual* boundary (as opposed to its advertised one) is found only by an outside
process with no stake in the gate being right: an adversary generating
unanticipated inputs, scored by the gate's own mechanical verdict. Corollary
("audit the article"): "**a** fabricated citation cannot pass" and "**no**
fabrication can pass" are different guarantees; products drift from the first to
the second in the pitch, never in the code. Write down the property the code
actually earns, in its exact words. Fix: the adversary belongs *in* the suite, as
a permanent strict-xfail-to-green tripwire, not as a one-off audit.

**Evidence:**
2026-07-12: 334 tests green throughout while a 12-class adversarial sweep found —
and hand-reproduction confirmed — 6 Error-B moat violations (`gate=PASS` on
unsupported claims). Two independent roots (score-bar dilution; per-claim
over-grounding), where the sweep's synthesis had claimed one — the contradiction
"it's all dilution" vs "two scored a clean 100 with empty appendix" located the
second root. Recorded as `tests/red_team_moat/` (6 strict xfail), AA-MOAT-001..006
in `docs/open-issues/`, ADR-005, CN-ADR005. Sibling to the load-bearing-assumption
rule and INS-098 (adversarial review finds the adjacent hole).

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions — candidate cross-cutting rule ("ship the
      adversary as a regression tripwire") after a second validating instance.

### [2026-07-14] Artifacts have the same asymmetry as verdicts — classify them derived vs authored

**Category:** principle
**Source:** incident (PIR-002 — corpus builder blanked the human labels)
**Products affected:** Assure; any project with a human-in-the-loop data asset

**Insight:**
Every artifact a toolchain writes is either **derived** (the machine can remake it,
identically — feature rows, reports, scores) or **authored** (a human made it; only
a human can remake it — labels, ratifications, annotations). The two have the same
recoverable/unrecoverable asymmetry that this project reasons about obsessively for
*verdicts* (Error-A vs Error-B) — and we had never once applied that reasoning to
*files*. A template generator, written before any labels existed, blanked the
`human_label` column of the twelve labels CR-001 rests on; it was doing exactly what
it was written to do. **The question no generator's author asks: what does this do if
the file it is about to write already contains a human's work?** If the answer is
"overwrite it", that is not a bug yet — it is an appointment.
Corollary (**detection is not prevention**): what caught this was the fail-loud label
*loader* — downstream of the destruction — plus git, plus the coincidence that the
next command I typed happened to read the labels. Two recoveries and one piece of
luck; zero prevention.
Corollary (**a guard with no door gets torn out**): the guard makes a labeled corpus
un-regenerable, which collides with the standing post-change drift-check discipline.
Left there, the honest engineer hits the guard every time they do the right thing —
so `--features-only` was added to make the safe path the easy path. Safety rails that
obstruct correct work are removed by good people, not bad ones.

**Evidence:**
2026-07-14: `python -m calibration.build_corpus` blanked all 12 `human_label` cells
(`build_corpus.py:460` writes `""` by design); `load_labels` raised on the next
command; restored from git; CR-001 then reproduced byte-identically. Post-ratification
the same keystroke destroys Sai's 52 gold labels (~45 min of irreproducible judgment,
the α1 gate for all of Phase 2). Guard: `assert_labels_not_clobbered`, red-first,
3 tests. Root cause (generator owns a file holding human input) still open as OI-CAL-03.

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions — landed ("labels are audit evidence, clobber-guarded")
- [ ] HQ cross-project insights — strong candidate: this generalizes to any repo with
      labeled data, annotations, or human ratifications sitting in a generated file.

### [2026-07-14] A fix inherits the imagination of whoever wrote it — red-team the fix

**Category:** principle
**Source:** session observation (red-team round 2 against round 1's fixes)
**Products affected:** Assure (generalizes to any verification/safety gate)

**Insight:**
A fix is normally verified against the attack that motivated it, which tests
whether the fix stops *that* attack — not what the fix actually *checks*. Round 1
closed "128000 operations per minute"; the gate then certified "each minute",
"every minute", "a minute", "per-minute", "hourly", the qualifier placed before
the number, and a Cyrillic homoglyph in "рer" — nine phrasings, fourteen wrongful
PASSes, all against a fix that was real. The corollary is a scheduling rule, not
a coding one: **the adversarial sweep must be re-run after the remediation, not
only before it**, and the adversary should live in the suite (permanent guards),
because there is no reason to think round three comes back empty.
Sub-lesson (homoglyph): NFKC does NOT fold Cyrillic 'р'→'p'. A homoglyph did not
defeat the rate check — it made the rate *invisible*, and an unread qualifier
fell back to "no rate asserted." **Audit what your extractor does when it fails
to extract**; a fail-open fallback inside a fail-closed gate is a hole shaped
exactly like the thing you thought you were checking.

**Evidence:**
2026-07-14: 22 drafts / 6 attack families against the post-remediation gate;
14 wrongful PASSes hand-reproduced. Recorded as AA-MOAT-R2-001..003 (fixed) and
AA-MOAT-007 (open) in `Agent-Assure/docs/open-issues/OPEN-ISSUES.md`; guards in
`tests/red_team_moat/test_moat_red_team_r2.py`; narrative in CN-ADR005 "Round Two".

**Graduation target:**
- [ ] Root `CLAUDE.md` Conventions — landed this session ("A fix to the moat gets
      red-teamed too"); promote to HQ cross-project insights after a second instance.

### [2026-07-14] Threshold-fitting wears the costume of a bug fix

**Category:** anti-pattern
**Source:** session observation (absence-rule repair, corpus row q37)
**Products affected:** Assure; any thresholded classifier or gate

**Insight:**
When a validation corpus rejects your new rule on one row, the cheapest repair is
almost always to move a constant — and it is almost always wrong. My subject-
coverage rule (">=50% of the negated subject's content words must appear in a
query") closed the attack but flipped a labeled-GROUNDED row to a false alarm,
because it was counting adjectives no researcher would ever type. Lowering 0.5 to
0.4 would have turned every test green in one character, leaving a rule fitted to
exactly two examples and principled about nothing. The tell: **the constant had no
meaning I could state in a sentence.** Rewriting the rule's *semantics* — head
noun plus one corroborating content word, with plural stemming — cost twenty
minutes and generalizes to cases not yet seen. Distinguish "the session searched
for this thing" from "the session used this word"; a fraction cannot express that,
so no value of the fraction was ever going to be right.

**Evidence:**
2026-07-14, corpus q37 ("There is no antidote approved for the toxin in current
guidelines", labeled grounded, backed by two targeted searches) flipped to
UNVERIFIED_ABSENCE under the coverage rule; restored by the semantic rewrite,
with the attack (streaming-ingest fabrication) still dying. Final corpus drift:
2 rows, both improvements. See CN-ADR005 "The corpus, again, as the fix's own
adversary".

**Graduation target:**
- [ ] `SOUL.md` Anti-Patterns — candidate ("tuning a constant until the corpus
      agrees") after a second instance.

<!-- Graduated insights log:
     (record destination when an insight is promoted)
-->
