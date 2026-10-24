# OVERNIGHT-2026-10-25 — the instrument

**Goal:** by morning Sai knows, with measured evidence, whether a writer who
follows the tester guide's "quote your sources" advice actually gets a PASS —
and, if not, has priced fixes ready on PRs — plus the fail-closed residue from
rounds 26–27 closed and attacked.

## §0 STATE FROM CODE (01:09 IST)
`main` 80196b2; open PR #20 (docs). Suite 996/2/61; gold md5
6215b526d03147295b003d7ccb0d171f; Error-A 12/25 = 0.480, Error-B 0/27.
**The tester guide's OWN quoting example FAILS (UNGROUNDED)**: a 5-word quotation
inside a paraphrased frame never forms the 8-token span T1 needs. Option A, as
written in the guide, is not yet workable. Re-derive each cycle; never quote this.

## §1 DIFF RULE · §2 GATES · §4 LADDER · §5 PARK LIST · §6 DISK
As `docs/planning/OVERNIGHT-2026-10-10.md`, with these overrides:
- **Escalation #1:** anything that makes a quoted claim PASS that does not pass
  today is PASS-ENABLING — built on a branch, priced (Error-A, Error-B, usage
  pass rate) and attacked, never merged. Sai rules in the morning. D-97 covered
  only B (negation, figures).
- **The guide is a claim surface.** If the guide's advice is false, the guide is
  corrected tonight (docs), not left standing.
- Adversaries: no outbound network. Gold md5 or HALT. Error-B must not move.

## §7 COMPETENCE BOUNDARY (named before the night)
I wrote the guide's example without running it. That is the "control correct
about what it examines" defect, in a document. Every example tonight is RUN.
