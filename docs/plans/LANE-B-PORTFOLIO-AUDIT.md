# Lane B — Portfolio Audit (Repo-Derivable Half)

Date: 2026-07-08
Scope: read-only sweep of `~/vibe-coding/` git history, governance artifacts, and READMEs. No offer, pricing, revenue, or pipeline data — none of that exists in any repo, and this audit does not fabricate it. Every such gap is marked `[NEEDS SAI INPUT: …]`.

Evidence method: `git log --since="90 days ago"`, `git log -1 --format=%ci`, `git ls-files | wc -l`, `find` for `docs/logbook/`, `*adr*`, `*aar*`, `*pir*` paths, and `README.md` head, run against each project directory on 2026-07-08. Counts for ADR/AAR/PIR are path-substring matches (`-ipath "*adr*"` etc.) — a sweep-level approximation, not an exact governance-doc census.

---

## 1. Evidence Table

| Project | Last commit | Days since | 90-day commits | Governance recency | ADR / AAR / PIR | Tracked files | One-line status |
|---|---|---|---|---|---|---|---|
| Agents/agents-infra | 2026-07-04 17:41 | 4 | 53 | logbook stale 110d (2026-03-20) | 12 / 9 / 12 | 91 | 6-plugin governance suite, LIVE on GitHub, active dev, logbook not kept current |
| Agents/agent-assure-calibration | 2026-07-08 00:10 | 0 | 51 (shared history w/ agents-infra) | logbook stale 110d; but CR-001 + AAR-003 (Phase 2a) filed outside docs/logbook, dated today | 1 / 3 / 1 (this branch's checkout) | 97 | Git **worktree/branch** of agents-infra (`agent-assure-calibration-run`, not an independent repo), active calibration workstream, in-flight today |
| Agents/ml-ops | 2026-04-20 15:57 | 79 | 1 | no logbook ever established | 0 / 0 / 3 | 14 | 3 near-duplicate preflight scaffolds (ml/kaggle/colab-preflight), minimal README, effectively dormant |
| Agents/financial-advisor-india | 2026-07-07 23:14 | ~1 | 13 | current (2026-07-07) | 21 / 3 / 3 | 217 | White-label AI research assistant for Indian brokerages, active, well-governed |
| ProSure | 2026-07-07 17:02 | ~1 | 176 | current (2026-07-07) | 48 / 9 / 2 | 6,499 | UK/EU regulatory compliance platform, 1,600+ tests, CI integrity gates, highest maturity signal in portfolio |
| 361DM/361 Digital Marketing | — | — | — | no logbook, not a git repo | 0 / 0 / 0 | — | Not started: only a `docs/` folder with one readiness report + `.env`. No code, no history. |
| 361DM/361-brain | 2026-07-03 19:24 | 5 | 99 | no logbook ever established | 9 / 2 / 0 | 249 | RAG+Graph knowledge layer for 361DM, actively building (1,409-file ingest documented), no PIR closed yet |
| GordonAI | 2026-07-04 17:40 | 4 | 4 | logbook stale 101d (2026-03-29) | 53 / 14 / 8 | 679 | AI mental-performance coach; **2nd-highest governance footprint in the entire portfolio against near-zero recent commit velocity** |
| Misc/shellac | 2026-07-04 19:23 | 4 | 16 | no logbook ever established | 6 / 3 / 2 | 130 | Self-hosted YouTube→social content repurposer, steady moderate activity, governance scaled to size |
| AICodingBook | 2026-07-07 14:15 | ~1 | 95 | stale 21d (2026-06-17) | 9 / 1 / 0 | 815 | "Anybody Can Code" book, very active, no root README (has SOUL.md/CLAUDE.md instead) |
| ival_2.0 | 2026-07-07 23:18 | ~1 | 249 | current-ish, 4d stale (2026-07-04b) | 33 / 3 / 3 | 637 | Payroll statutory compliance engine; **highest 90-day commit count in the portfolio** |
| ai-learning-studio | 2026-07-07 23:17 | ~1 | 59 | current (2026-07-07) | 8 / 1 / 1 | 150 | AI study-aid layer for corporate LMS, active, supervised cross-project by Config Mgmt HQ |
| Sais_Creative_Expression | 2026-06-17 20:30 | 21 | 79 | stale 34d — **latest logbook entry is literally titled "paused_to_pivot_aicodingbook" (2026-06-04)** | 25 / 0 / 0 | 2,683 | Creative portfolio; **self-declared paused** in its own logbook, never formally closed in README/PIR |

Note on agents-infra / agent-assure-calibration: these are **not two independent projects**. `agent-assure-calibration` is a git worktree (`.git` is a 107-byte pointer file to `agents-infra/.git/worktrees/agent-assure-calibration`) checked out on branch `agent-assure-calibration-run`. Commit counts overlap substantially. Treat as one codebase with two live working trees, not 13 separate projects.

---

## 2. Ranked Moves (highest expected return first)

Return = unblocking shippable value or freeing Sai's time, reasoned from the evidence above — not from any assumption about what each project is "supposed" to be worth.

### Move 1 — Converge and merge the `agent-assure-calibration-run` worktree back into `agents-infra` main
**Why (evidence):** This worktree has the single most recent commit in the entire portfolio (2026-07-08 00:10, i.e. today) and an active calibration record (`Agent-Assure/calibration/CR-001-bootstrap-lex-tau.md`, referenced in commit `86a7f46`). But its checked-out `docs/adr/` contains only 1 file (`ADR-003-unbundling-rule.md`) versus 12 on the main branch — meaning either this branch has diverged from main's governance docs, or the two have never been reconciled. Every day this worktree stays unmerged, the divergence risk (and eventual merge-conflict cost) compounds — this is exactly the "concurrent trees clobbering each other" risk class flagged in this repo's own operating rules.
**Steps:**
1. From the main `agents-infra` checkout, run `git log main..agent-assure-calibration-run --oneline` to see exactly what's unmerged.
2. Run `git diff main..agent-assure-calibration-run -- docs/adr docs/aar docs/pir` to see whether the branch's thinner governance folder is a real deletion or just an artifact of a partial checkout.
3. Confirm Phase 2a (lex_tau=0.71, CR-001, dup-key guard — per commit `86a7f46`) is the current milestone's stopping point, not mid-flight.
4. If stopping point confirmed: open a PR from `agent-assure-calibration-run` into `agents-infra`'s default branch.
5. After merge, run `git worktree remove` on the calibration worktree to retire it cleanly (or keep it if a Phase 2b is imminently planned — check `docs/plans/HANDOFF-MASTER-PLAN.md` in this same directory first).
**Done looks like:** PR merged, `git log main..agent-assure-calibration-run` returns empty, worktree either removed or explicitly retained with a stated reason.
**Instructions for a weaker model:** "Do not run any destructive git command (`worktree remove`, `reset --hard`) until step 4's PR is merged and confirmed by the user. Steps 1–3 are read-only; run them first and report findings before proceeding to step 4."

### Move 2 — Force a kill/revive decision on GordonAI
**Why (evidence):** 53 ADRs, 14 AARs, 8 PIRs — the 2nd largest governance footprint of all 13 directories audited (only ProSure's 48/9/2 is comparable, and ProSure has 176 commits/90d to GordonAI's 4). GordonAI's logbook has not been touched in 101 days. This is the starkest planning-outstrips-shipping signature in the portfolio: more decision records than commits by an order of magnitude.
**Steps:**
1. Read the most recent 3 ADRs by filename/date in `GordonAI/docs/adr/` to find the last stated architectural intent.
2. Read the most recent AAR to find the last after-action summary — this will say what was last actually attempted.
3. In one timeboxed sitting (recommend ≤ 90 minutes), decide: revive with a scoped next commit within 2 weeks, or kill.
4. If kill: write one PIR at `GordonAI/docs/pir/` stating why, and update the README status line to "Paused — see PIR-XXX."
5. If revive: write a TDR (Tactical Decision Record, per house convention) naming the exact next 1–2 week scope, so this doesn't relapse into open-ended planning.
**Done looks like:** GordonAI's README states an explicit current status (not silently ambiguous), and either a PIR or a scoped TDR exists dated this week.
**Instructions for a weaker model:** "This step requires a human decision (kill vs revive) — do not make this call yourself. Read the 3 most recent ADRs and the most recent AAR, summarize them for Sai in under 15 lines, and stop. Wait for his decision before writing any PIR or TDR."
**Classification note:** flagged PROVISIONAL in Section 3 below — this audit did not read ADR content, only counted files.

### Move 3 — Kill or consolidate `Agents/ml-ops`
**Why (evidence):** 1 commit in 90 days, 14 tracked files, zero logbook/ADR/AAR ever established, README is a single line (`# ml-ops`). Contains three near-identical subtools (`ml-preflight/`, `kaggle-ml-preflight/`, `colab-ml-preflight/`), each with its own LICENSE/README/CLAUDE.md/package.json but no differentiating logic visible from directory structure alone. Low sunk cost (14 files) makes this the cheapest kill in the portfolio.
**Steps:**
1. Read the README of each of the 3 subtools to check whether they're genuinely differentiated (platform-specific preflight checks) or copy-pasted boilerplate.
2. If genuinely differentiated but unused: decide keep-dormant vs archive — this is a low-stakes call a weaker model can make with a one-line rationale.
3. If copy-pasted duplication: consolidate into one parameterized tool, or archive two of the three.
4. Update `Agents/ml-ops/README.md` beyond the current one-liner to state actual purpose and status either way.
**Done looks like:** README states real purpose/status; a decision (keep/archive/consolidate) is recorded, even if the decision is "keep as-is, revisit in Q4."
**Instructions for a weaker model:** "Read all three subtool READMEs before deciding anything. If they look identical apart from tool name, flag that explicitly to Sai rather than guessing intent."

### Move 4 — Ratify the already-declared pause on Sais_Creative_Expression
**Why (evidence):** The project's own most recent logbook entry (2026-06-04) is literally titled `paused_to_pivot_aicodingbook.md`. Sai already made this call in writing. But the README carries no status marker, and there's no PIR closing the workstream — meaning it still shows up as "active" in any file-count/commit sweep (2,683 tracked files, 79 commits/90d — much of that is likely pre-pause tail activity or asset commits, not open development). This costs nothing to fix and removes one recurring false-positive from every future portfolio audit.
**Steps:**
1. Add a one-line status banner to the top of `Sais_Creative_Expression/README.md`: "Status: Paused (2026-06-04) — creative energy redirected to AICodingBook. See `docs/logbook/2026-06-04_ainterprise_paused_to_pivot_aicodingbook.md`."
2. No PIR is strictly required (this isn't a failure, it's a redirection) but a 5-line closure note in the logbook confirming the pause is still in effect as of today would remove ambiguity.
**Done looks like:** README states "Paused" explicitly; next portfolio sweep does not need to re-derive this from a logbook filename.
**Instructions for a weaker model:** "This is a documentation-only edit. Do not touch any code or delete any files. Only edit README.md's header."

### Move 5 — Resolve 361DM/361 Digital Marketing
**Why (evidence):** Not a git repository. Contains only a `docs/` folder with a single file (`kodus-readiness-report-2026-03-27.md`) plus a stray `.env`. No code was ever committed. Meanwhile `361DM/361-brain` is the actual active RAG/knowledge-layer product for the same client (99 commits/90d, 249 files). This directory may simply be a stale planning shell that predates 361-brain and was never cleaned up.
**Steps:**
1. Confirm with Sai whether `361 Digital Marketing/` is superseded by `361-brain/` or serves a distinct purpose (e.g., separate from the RAG layer — client-facing marketing ops docs vs. the AI knowledge layer).
2. If superseded: move the one readiness report into `361-brain/docs/` (or delete if truly redundant with content already in 361-brain), then remove the directory.
3. If distinct: `git init` it properly and give it a real README before more files accumulate outside version control (note: `.env` in an ungitted directory is itself a minor exposure risk if this directory is ever zipped/shared — flag for cleanup regardless of the kill/keep decision).
**Done looks like:** directory either removed or properly initialized as a real repo with a stated purpose distinct from 361-brain.
**Instructions for a weaker model:** "Do not delete the directory or move any files without Sai's explicit confirmation on step 1 — this step requires a business-context decision you cannot infer from the repo alone."

---

## 3. Kill / Finish / Ship Classification

| Project | Classification | Justification |
|---|---|---|
| Agents/agents-infra | **SHIP** | Per project memory, all 6 plugins are "LIVE on GitHub" — this is already a shipped artifact receiving ongoing incremental commits (53/90d). The open item is governance hygiene (logbook 110d stale against active commits), not shippability. |
| Agents/agent-assure-calibration | **FINISH** (merge-then-retire branch) | Not a separate product — an in-flight calibration workstream on a worktree, most recent commit in the whole portfolio (today). Phase 2a bootstrap explicitly named as complete in commit `86a7f46`; the finishing move is the merge in Move 1, not new feature work. |
| Agents/ml-ops | **KILL** (or consolidate) | 1 commit/90d, zero logbook/ADR/AAR ever, one-line README, 3 undifferentiated-looking subtools. Every governance signal available from the repo alone points to abandonment; only the subtool READMEs (not read in this sweep) could overturn this. |
| Agents/financial-advisor-india | **FINISH** — *PROVISIONAL* | Active (13 commits/90d, logbook current) and well-governed (21 ADRs), but this sweep cannot determine how close to externally shippable it is — that requires reading `PRODUCT_BLUEPRINT.md` and knowing customer/pilot status, which is offer/pipeline data out of this audit's scope. |
| ProSure | **SHIP** | Highest governance maturity in the portfolio (48 ADR, badges claiming 1,600+ passing tests, CI integrity gates on push), by far the highest commit velocity (176/90d), logbook current to yesterday. All observable signals point to production-grade, actively shipping software. |
| 361DM/361 Digital Marketing | **KILL** — *PROVISIONAL* | Never became a repo; zero code. Provisional only because whether it's genuinely dead vs. simply mis-placed (its one doc might belong inside 361-brain) requires Sai's confirmation (Move 5), not more repo evidence — there is no more repo evidence to gather. |
| 361DM/361-brain | **FINISH** | Actively building (99 commits/90d, 5 days since last commit, 1,409-file ingest documented in README), 9 ADRs recorded, but zero PIRs — no milestone has been formally closed yet. This is mid-build, not yet at a shippable checkpoint by its own governance record. |
| GordonAI | **KILL** — *PROVISIONAL, see Move 2* | 53 ADRs / 14 AARs / 8 PIRs against 4 commits/90d and a 101-day-stale logbook is the starkest stall signature in the portfolio. Marked provisional because the actual kill-or-revive call requires reading ADR content (what was the last stated direction) — this sweep only counted files, per its read-only/efficiency mandate. |
| Misc/shellac | **FINISH** | Governance scaled proportionately to size (6/3/2 against 130 files), moderate steady commit cadence (16/90d, 4 days since last commit). No stall or over-governance signal — looks like a normally-progressing side project. |
| AICodingBook | **FINISH** | Very active (95 commits/90d, 1 day since last commit), and per project memory "Chapters 1-2 complete" — this is the confirmed current creative priority (see Sais_Creative_Expression's own pause note naming this as the pivot destination). |
| ival_2.0 | **SHIP** | Highest 90-day commit count of any project audited (249), logbook current to 4 days, 33 ADRs, deterministic/spec-first framing in README reads as production-oriented. Matches ProSure's shipped-and-shipping profile. |
| ai-learning-studio | **FINISH** | Active (59 commits/90d, logbook current to yesterday, 8 ADRs), explicitly described as supervised cross-project by Config Management HQ — mid-build with active oversight, not yet at a "ship" milestone by its own governance record (only 1 PIR closed so far). |
| Sais_Creative_Expression | **KILL** (ratify existing pause) | Self-declared paused in its own logbook (2026-06-04, filename literally says "paused_to_pivot_aicodingbook"). This is not this audit's judgment — it is Sai's own recorded decision, unexecuted in the README. Move 4 just makes it visible. |

---

## 4. Three Things to Stop Doing

**1. Stop running more active workstreams than can be individually finished.**
Evidence: 11 of the 13 audited directories show git commits within the last 90 days (all except `361DM/361 Digital Marketing`, which never started, and treating `agents-infra`+`agent-assure-calibration` as one). Total 90-day commit volume across the portfolio is roughly 900+, spread across a dozen codebases — this is not a small side-project count, it's a dozen live fronts. The instruction to look for "governance scaffolding but no commits in N months" as a starting-not-finishing signal is directly confirmed twice in this data (GordonAI, and to a lesser extent ml-ops) — but the deeper pattern is that even the *non-stalled* projects (ProSure, ival_2.0, 361-brain, ai-learning-studio, AICodingBook, financial-advisor-india, agents-infra) are all simultaneously active. Depth is being traded for breadth by construction, not by accident — no single project gets undivided attention in any given week.

**2. Stop letting governance-doc production decouple from shipping cadence.**
Evidence, both directions of the same failure: GordonAI has 75 combined ADR+AAR+PIR files against 4 commits in 90 days — governance is being produced with no corresponding code motion. agents-infra/agent-assure-calibration shows the inverse: 51-53 commits in 90 days but the logbook (the mechanism this very repo's own CLAUDE.md calls "authoritative") has not been touched in 110 days — code is moving but the record isn't. Both are the same underlying failure: the discipline this project's own house rules mandate (logbook-first orientation, session-end logbook entry as "non-negotiable if project has governance") is not being applied uniformly across the portfolio. A rule enforced in the CLAUDE.md of the repo doing this audit is visibly not enforced in sibling repos.

**3. Stop leaving paused or never-started projects formally undeclared.**
Evidence: Sais_Creative_Expression has an explicit pause decision sitting in a logbook filename since 2026-06-04, but no PIR and no README status change — meaning it still reads as "active" to any repo-level sweep (which is exactly what happened at the start of this audit, before the logbook filename was inspected). 361DM/361 Digital Marketing has existed long enough to accumulate one planning document but was never even `git init`'d — it has no recorded status at all, active or otherwise. Both cost real time on every future audit or status check: this exercise alone spent extra evidence-gathering cycles determining that these two were dormant, cycles that a one-line README status would have made unnecessary.

---

## 5. To Complete the Full Consultant Audit

This repo-derivable sweep cannot answer the commercial half of Lane B. To complete it, Sai must supply:

1. **Offers** — for each active/finish/ship project that has (or is intended to have) external users: what is being sold, to whom, at what stage (concept / pilot / paying customers).
2. **Pricing** — current or planned price points per offer, and whether pricing has been validated with any real prospect/customer conversation.
3. **Pipeline** — for each offer: number of live conversations, stage (lead / discovery / proposal / signed), and expected close timing.
4. **Revenue** — actual revenue booked to date per project, if any, and run-rate if applicable.
5. **Hours allocation** — how Sai's own time is currently split across these ~12 workstreams in a typical week, and how he *wants* it split. (This audit found the commit-activity proxy for this — Section 1's 90-day commit counts — but commit count is not hours, and doesn't capture non-coding consulting/client time at all.)
6. **Constraints** — any contractual, licensing, or client-confidentiality constraints on any of these projects that would affect a kill/finish/ship call (e.g., is GordonAI under contract with a specific client or academic partner? Is 361DM a paying client relationship or an internal bet?).

**Drop format — `Temp-DDmmm-Consulting.md` (≤20 lines):**

```
# Consulting Input — [DDmmm]

## Offers (one line each: project → what's sold → stage)
- ProjectName: [offer] — [concept/pilot/paying]

## Pricing (project → price point → validated? Y/N)
- ProjectName: [price] — [Y/N, with whom]

## Pipeline (project → # live convos → stage → expected close)
- ProjectName: [n] — [stage] — [date/quarter]

## Revenue booked to date (project → amount → period)
- ProjectName: [amount] — [period]

## Hours allocation (actual last 4 weeks vs desired going forward)
- Actual: [rough % or hrs/wk per project]
- Desired: [rough % or hrs/wk per project]

## Constraints (contractual/confidentiality flags, if any)
- ProjectName: [constraint]
```

This file should be dropped at the Desktop or project-root location per the existing `Temp-DDmmm-{Project}` convention — it will be treated as conversation input, not a governance artifact, and consumed (then archived/emptied) rather than overwritten mid-flight.
