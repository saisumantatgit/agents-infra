# 2026-10-10 — the day run, and the seam between two documents

**Branch** `testing-live-2026-10-10` · **Instrument** `docs/planning/DAYRUN-2026-10-10.md`
· **Ratification** D-93 · **Cron** `5888aa27`, still armed, hard stop 22:00 IST.

## What

Four of six committed rows built. R1 made the deployed error rates re-derivable
by one read-only command. R2 (J-50) made the first-run refusals legible without
softening them. R3 proved a stranger can install the branch and the moat holds
on their machine. R4 priced the merge to `main` — and inverted it. R5 ran round
20 against `capture_core.py`. R6 is partly done (CR-012, register rows).

## Why it mattered

**`main` is the vulnerable build.** It already ships Agent-Assure, at the
Phase-1 engine — 1,388 lines, before all nineteen red-team rounds. One draft
citing only itself: `main` returns **PASS 100.0 GROUNDED**, the branch returns
**FAIL 0.0 UNGROUNDABLE**. Declining the merge keeps the dangerous build as the
one a stranger reaches by default. PR #10 is open for Sai; nothing was merged.

## The finding of the day, and it is not on the branch — it is under it

**R20-01. The capture layer MANUFACTURES verbatim text.** `_coerce_text_value`
joins MCP content blocks with `"\n"`; `_tokenize` is `re.findall(r"\w+")`, so
the seam is invisible and the last tokens of document A sit adjacent to the
first tokens of document B. A contiguous span straddling two **different**
fetched documents satisfies T1 — the moat's one remaining deterministic tier.

**Reproduced by me with my own fixture, not the adversary's:** a claim present
in neither document certified **PASS 100.0**, and **also PASS 100.0 under
`--session-id`**, where the report printed "traceable to text in a source
retrieved this session" over a sentence no retrieved page contains.

**Why nineteen rounds missed it.** Every one of them attacked
`ground_check.py`, and `ground_check.py` is correct here: it faithfully reports
a contiguous span of the text it was given. The lie is written into the store
before the gate ever runs, and **the document boundary is discarded at
ingestion, so no loader validation can ever recover it.** This is the estate's
signature defect in its purest form — a control correct about what it examines
and silent about what it does not.

## Decisions

- **D-93** armed the run with its undo (branch deletion; nothing else touched).
- **A-5-01 routed to Sai, not fixed:** `install.sh`'s own session-id snippet
  crashes in a fresh install. Escalation #4, park list.
- **R4-Q1 routed to Sai:** does anyone actually install from `main`? It is the
  one fact that flips my merge recommendation, and no search of this repo
  answers it.
- **R5 marked HOSTILITY INSTRUMENT ONLY.** No live session store was available
  (`claude -p` runs no PostToolUse hooks, D-60), so every fixture is a shape
  the adversary invented. A zero finding on a shape nobody tried is
  non-measurement, not safety.

## Agents

One Opus adversary, 151K tokens, 31 tool calls, ~10 minutes. Returned 3
CRITICAL, 2 HIGH, 1 MEDIUM, 3 speculative. It logged its own protocol deviation
unprompted (ran `git status` once against instruction, read-only). **Its report
is testimony: R20-01 is confirmed by my own independent reproduction; R20-02
and R20-03 are NOT yet reproduced by me and must not be quoted as facts until
they are.**

## Reflection

The lesson of 2026-10-02 was that *for Error-B the instrument is an adversary,
never a corpus*. Today sharpened it: **the instrument also has to be pointed at
the right file.** Nineteen rounds of genuine adversarial pressure produced a
gate I would defend — and they produced it against the half of the system that
was already being watched. The capture layer had never been attacked once, and
the first serious hour against it found three ways to certify a fabrication at
100.0. What I had been calling "the moat" was one of two walls, and the
unexamined one is upstream, where a lie becomes evidence rather than being
judged as a claim. My named competence boundary this morning was *auditing the
layer where the measurement lives rather than where the work lives*. I wrote
that down as a risk at 13:40 and walked into the room it describes by 16:00 —
with the difference that this time the instrument was aimed at it on purpose.

## Next

R20-02 and R20-03 reproduced by me, then the remaining HIGH/MEDIUM, then CR-012
updated with R5's actuals and the 7-step close. **PR #10 and PR #11 are open and
must not be merged by me.**
