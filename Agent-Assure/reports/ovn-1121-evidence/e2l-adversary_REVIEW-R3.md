# E2-lite round 3: pre-merge adversary review (ovn-1121-e2l @ 6ca9a90 vs origin/main 0c0ddc4)

**Verdict: 0 BLOCKERS.** Nothing that main refuses passes on the branch. The cache cannot return another source's units, and it changes no verdict. 1 of the 21 honest labels is still refused. The latency regression is gone.

## 1. Blocker question: does anything main refuses now pass? No.

**Structure (unchanged from round 2):** E2 only promotes an uncited NON_CLAIM heading to FACTUAL, which then scores UNCITED. So E2 can only lower a score. The round-3 diff touches only `_e2_heading_asserts` and the one call site in `main()`. `classify`, `decompose`, `ground` and `score_report` are byte-identical to main.

**What the cache is keyed by, and how it is invalidated:**
- **Lifetime:** `e2_cache = {}` is a local inside `main()`, so it lives for one process run. It is passed explicitly and has no mutable default argument. Nothing is shared across runs or callers. The only caller is `main()`.
- **`units` and `normalized_sources`:** both are keyed by `source.text`, which is content-addressed. `_denial_units(source_text)` is documented Pure and takes only the text. So two sources with identical text sharing an entry is correct, and different text can never collide. Stale data is impossible: the store is not changed between headings.
- **`words`:** a single unkeyed entry, built from the first call's `sources`. It is correct only because `main()` passes the same `store.values()` every time. This is a latent hazard for any future caller that varies the sources, and there is no `CEILING:` note naming it. Not a blocker today.
- **Empirical equivalence:** I re-ran `_e2_heading_asserts` with one shared cache and with a fresh cache per heading over every corpus draft and store: 1,435 drafts and 422 eligible headings. The two disagreed 0 times (`r3/cachecheck.py`).
- **Pre-filter:** `body not in normalized_sources[...]` skips a source before the per-sentence loop. If it is ever wrong it can only remove refusals, never add a pass that main refuses.

**Empirical comparison, frozen main worktree vs branch:**

| Instrument | Drafts | Gate up | Score up | Control gate up | Gate down |
|---|---:|---:|---:|---:|---:|
| Error-B v1 | 280 | 0 | 0 | 0 | 5 (the 5 `claim_heading` escapes closed; escaped 5 -> 0) |
| Error-B v2 | 269 | 0 | 0 | 0 | 0 |
| Error-B v3 | 510 | 0 | 0 | 0 | 0 (escaped 490 -> 490) |
| Error-A (`--no-ablate`) | 336 | 0 | 0 (0 claims gained grounded) | n/a | 0 |
| Usage genres | 40 | output byte-identical | | | |
| Differential fuzz | 600 | 0 up, 0 crashes, 5 kind changes | | | |
| Probes: scored / evade / evade2 / self | 38 / 22 / 11 / 2 | 0 UP, 0 CRASH | | | |

**Minor finding (not a blocker):** `original_words` comes from the *untrimmed* body, while `words` comes from the trimmed one. They line up only when trimming removes no `\w` character. A leading run of connector punctuation such as `__` breaks that, and the index can then point at a different word. The worst outcome is a wrong refusal decision or an IndexError, and an IndexError exits non-PASS.

## 2. Honest labels: 1 of 21 still refused

The test is `probe/honest.py`: one neutral source and a fully grounded body.
- **Round 2:** 21 labels passed on main and failed on the branch.
- **Round 3:** only `## Lost and found` still fails (50.0). The other 20 are back to PASS on the branch: `Charges`, `Charging`, `Finding`, `Found`, `Fail`, `Ban`, `Fines`, `Arrests`, `Suing`, `Crash`, `Fraud`, `Quitting`, `Double`, `Doubling`, `Hacking`, `Memory leaks`, `Code folding`, `Fast charging`, `Productivity hacks`, and others.
- **Also still refused:** `## How the regulator found fraud`, a question-shaped label.
- **True positive kept:** `## Quay Trust lied` (main PASS, branch FAIL).
- **Evasions:** `Police arrest Quay Trust directors` and `Possible lies` still pass on both main and branch.

## 3. Latency

The probe is 30 plain headings, 200 sources, 40 sentences each (`probe/perf.py`), measured on an idle machine.
- **Plain headings:** main 0.18-0.20 s, branch 0.19-0.21 s. Round 2 took 24.2 s, so that regression is gone. At 50 sources: main 0.18 s, branch 0.19 s.
- **Disowned-span path:** headings equal to a source sentence and carrying a predicate, so `_denial_units` really runs, over 200 distinct sources. Main 0.20 s, branch 1.22 s. Each distinct source text is computed once per run, not once per heading.
- **Missing ceiling:** there is still no `CEILING:` note for that per-run cost.
