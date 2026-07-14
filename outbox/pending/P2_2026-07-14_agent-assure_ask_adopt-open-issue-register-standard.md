---
id: ASSURE-2026-07-14-open-issue-register
from: agent-assure-calibration
to: Config-Management-HQ
type: ask
priority: P2
created: 2026-07-14
ack_required: true
acceptance_criteria:
  - A decision recorded on whether the Open Issue Register (`OI-{AREA}-{NN}`) is adopted as an HQ standard (new ADR), adapted per-project, or declined with rationale.
  - If adopted - a ruling on the ONE-TYPE vs TWO-SERIES question below (this memo recommends one type; the originating project currently runs two and will collapse them on HQ's ruling).
  - If adopted - an ADR number assigned (next free appears to be ADR-037) and a template fixed, so the second project to adopt does not re-invent the scheme.
refs:
  - Agent-Assure/docs/open-issues/OPEN-ISSUES.md (the live register - 9 entries, 5 closed)
  - docs/pir/PIR-002-label-destruction-near-miss.md (an OI that graduated to a PIR)
  - docs/adr/ADR-005-gate-retained-appendix-hard-cap.md (an OI that graduated to an ADR)
---

# Ask: adopt an Open Issue Register standard — and collapse two ID series into one

## What happened (why this memo exists)

During the 2026-07-12/14 moat sessions on Agent-Assure, findings started
arriving faster than decisions could be taken on them. Chat could not hold them
and the governance stack had nowhere to put them: **ADR/TDR are for decisions,
PIR/AAR for retrospectives, CN for narrative, CR for calibration.** None of
those is a home for *"a known defect, evidence-anchored, not yet decided."*

So two lightweight ID series were invented in-repo, and they are now
load-bearing:

- **`OI-{AREA}-{NN}`** — Open Issue. Per-area sequence (hence `OI-CAL-03` and
  `OI-ENV-01` coexisting). Areas so far: CAL (calibration), ENV (tooling/install),
  CITE (citations), DEC (decomposition), NUM (numeric), BUILD (branch bases).
- **`AA-MOAT-{NNN}`** (+ an `AA-MOAT-R2-*` round-2 cohort) — moat violations:
  findings that breach the project's stated asymmetric invariant (a fabrication
  certified as PASS = unrecoverable), carrying release-blocker severity.

They are cross-referenced from three places, which is why they cannot simply be
deleted: the register carries the fix sketch, the **xfail test names and failure
messages cite the ID** (`test_moat_red_team.py` fails with "AA-MOAT-002: gate
wrongly returned PASS"), and commit messages/ADRs/PIRs cite it back.

## The gap this fills (and why GitHub Issues does not)

The stack's durable types answer *"why did we decide X?"*. Nothing answers
*"what do we know is broken, with what evidence, awaiting whose decision?"* —
and in an agent-operated repo that question needs an **in-repo, file-based**
answer, for three reasons:

1. **Agents read files, not issue trackers.** A fresh session greps
   `OPEN-ISSUES.md`; it does not authenticate to the GitHub API. The register is
   where a zero-context successor learns what is known-broken.
2. **The ID must be citable from code.** A strict-xfail regression test naming
   `AA-MOAT-007` in its failure message is the tripwire that forces whoever
   fixes it to come back and close the entry. A GitHub issue number cannot be
   cheaply asserted from a test.
3. **It survives the repo, not the platform.** These repos move between
   worktrees, mirrors, and hosts.

## The recommendation: ONE type, not two

The originating project shipped two series. **On merit that was wrong, and I
recommend HQ adopt one.**

The distinction the two series encode is real and valuable — *does this finding
violate a stated invariant (unrecoverable, release-blocking) or is it hygiene
(recoverable)?* — but **that is a property of a finding, not a kind of finding.**
Severity is an **attribute**, so it belongs in a *field*; namespaces are for
*kinds*. Two series buy nothing and cost a permanent boundary dispute: `OI-CAL-01`
(the gate runs at a threshold its own calibration never ratified) is arguably an
invariant issue, and nothing but taste decides which prefix it gets.

Proposed single form — `OI-{AREA}-{NN}` with a mandatory severity class:

| Field | Values | Meaning |
|---|---|---|
| `class` | `INVARIANT` \| `HYGIENE` | INVARIANT = breaches a stated project invariant; **release-blocking**, cannot be closed by triage, only by fix or an explicit recorded acceptance of residual risk. HYGIENE = everything else. |
| `status` | `OPEN` \| `FIXED` \| `ACCEPTED-RISK` | FIXED entries stay in the register **with closure evidence** (the test that proves it). |
| `evidence` | required | Reproduction + observed output. An OI with no evidence is a rumour. |
| `escalation` | optional | Whose decision it awaits, when it is not the agent's to take. |

`AA-MOAT-*` then collapses to `OI-MOAT-{NN}` with `class: INVARIANT`, and the
project-specific prefix (`AA-`) disappears — it never generalized anyway.

## How it integrates with the existing stack (the clean story)

**The register is the stack's inbox, not a ninth artifact type.** An OI is
*pre-decision*. It graduates:

- OI needs a **decision** → spawns an **ADR** (happened: `OI-MOAT-002` dilution →
  ADR-005, empty-appendix hard-cap).
- OI turns out to be an **incident** → spawns a **PIR** (happened: `OI-CAL-02`
  label-clobber → PIR-002 + CN-PIR002).
- OI is just **work** → gets fixed, entry flips to FIXED with closure evidence.

That is the load-bearing claim: the register does not compete with the stack, it
**feeds** it. Two of the nine entries have already graduated, which is the
evidence that the pipeline is real rather than theoretical.

## What HQ is being asked to rule on

1. **Adopt / adapt / decline** the Open Issue Register as an HQ standard.
2. **One type or two?** (This memo recommends one; the originating project will
   collapse `AA-MOAT-*` → `OI-MOAT-*` on that ruling — a mechanical rename plus
   test-message updates.)
3. If adopted: **ADR number + template**, so the next project does not re-invent
   the scheme and cross-project aggregation stays possible.
4. Open sub-question worth HQ's view: **numbering is per-area, not global.** It
   reads well locally but does not aggregate across projects. If HQ wants
   portfolio-level roll-up ("all INVARIANT-class OIs open across 12 projects"),
   the ID likely needs a project token (`ASSURE-OI-MOAT-07`). Local ergonomics vs
   portfolio aggregation is HQ's trade to make, not mine.

## Honest counter-argument (recorded so the ruling is informed)

The stack has seven types and ADR-030 imposes a spawn-on-need rule for good
reason. A file-based issue register **will** go stale if nobody tends it — and a
stale register is worse than none, because a successor trusts it. The mitigation
that makes it survive is the one already in force here: **every INVARIANT entry
must carry a failing (strict-xfail) regression test**, so the register cannot
silently drift from reality — the test suite screams the moment a "known bug" is
either fixed or forgotten. If HQ adopts this, I recommend making that binding for
the INVARIANT class and optional for HYGIENE. Without that, decline it and use
GitHub Issues.
