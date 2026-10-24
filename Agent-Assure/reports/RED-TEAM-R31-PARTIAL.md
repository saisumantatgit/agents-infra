# RED-TEAM-R31 — adversarial review of hardening-2026-10-25 (H1-H5) vs main e92075b

Claim under attack: commits 82821cf..9662c48 are fail-closed (only add refusals).
Method: code diff review of every changed decision path, then executable differentials
(main worktree at e92075b vs branch), then bypass probes. All scripts under r31/w/.

## Findings

### R31-01 — MEDIUM (latent Error-B; masked today by ADR-009) — H5 widens the absence rule chain via the D-54 denominator trap. NEW.
H5 makes `_self_source_ids` match MORE `Read` records. `_session_queries` drops self-sources
from the query population, and that population is the DENOMINATOR of check_absence's
blanket-corpus-word refusal (`len(distinct) >= 3 and majority contain head noun`). Shrinking
it switches the refusal OFF — the exact trap documented at R11B-01 / D-54 in the same function.
Repro (`w/absence.py`): draft "# Widget controller notes / There is no benchmark of the widget
controller."; two exa fetches with queries "widget controller benchmark" and "published
benchmark widget controller review"; one Read of `benchmark-widget-controller-copy.md` = draft
+ 6 filler lines (diluted copy; path contains the head noun).
- main: `absence_diagnostic = searches_do_not_qualify` (3 queries, 3/3 carry "benchmark" -> refused)
- branch: `absence_diagnostic = searches_would_qualify` (Read now self -> 2 queries -> gate off)
Verdict both sides: UNVERIFIED_ABSENCE, because ground() unconditionally demotes
ABSENCE_SUPPORTED (J-97/ADR-009, ground_check.py:4460). So no PASS today; the chain itself
certifies what main refused, and the diagnostic now tells the author the searches qualify.
Becomes a live Error-B the day ADR-009's demotion is lifted. Fix shape: exclude self-sources
from the COUNT only, keep them in the gate denominator (or conjoin with a main-population call),
as R20-04 already does for failed fetches.
