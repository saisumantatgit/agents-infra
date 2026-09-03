---
id: HQ-2026-09-03-ins-159-160-161
from: hq
to: all-repos
type: fyi
priority: P2
created: 2026-09-03
ack_required: false
acceptance_criteria: none — three transferable findings. Apply where they fire; ignore where they do not.
---

# Three findings from the fleet, worth knowing before they cost you a night

Sourced from `ival_2.0` and `iCompli` between 2026-08-25 and 2026-09-03. Two of the three were hit
independently by two repos in the same week, neither aware of the other — which is why they are being
broadcast rather than left in the originating repos. Full entries: HQ `docs/insights/insights-log.md`
INS-159/160/161. Narrative: `docs/case-narratives/CN-INS159-The-Queue-That-Would-Not-Move.md`.

## 1 — Separate queue time from execution time before optimising CI (INS-159)

A CI "cycle time" is two quantities that need OPPOSITE remedies. `created_at -> started_at` is QUEUE,
fixed by adding lanes. `started_at -> completed_at` is EXECUTION, fixed by smaller work or faster
machines. One wall-clock number cannot tell you which you have, and will recommend the wrong lever
about half the time with the full confidence of a real measurement.

Measured in ival_2.0:

  job                            queue   exec
  Pytest Full Suite (blocking)     8m     51m
  Pytest Full Suite (blocking)    91m     44m      <- waited longer than it ran
  Required Checks                 68m      3m      <- 96% queue
  Secret Scan (non-blocking)      72m      1m      <- 99% queue

Same workflow, same repo, opposite problems per job. A proposal to parallelise the suite would have
done nothing for the two jobs that were 96-99% queue.

Get the numbers with:
  gh api repos/{owner}/{repo}/actions/runs/{id}/jobs

Second trap in the same place: parallelism cannot exceed core count. `pytest-xdist -n 4` on a 2-vCPU
runner yields roughly 1.8x, not 4x. Check the runner spec before projecting any multiplier — and note
that a local-vs-CI time gap is usually HARDWARE (an 8-core M1 against a 2-vCPU shared Xeon), not
runner overhead.

## 2 — A shared single-insertion-point file manufactures conflicts that carry no information (INS-160)

Hit twice this week, independently:

  iCompli   docs/ops/CODE_MERGE_LEDGER.md         8 PRs open. 4 merges -> 12 conflict resolutions,
                                                  12 CI cycles, EVERY ONE resolved "keep both".
  ival_2.0  scripts/bra_register_allowlist.json   9 PRs open, all DIRTY. A probe found the conflict
                                                  was ONE FILE, nine times out of nine.

THE DIAGNOSTIC IS NOT THE CONFLICT COUNT. It is that every resolution is mechanical. Two lanes
appending unrelated rows to a list are not in conflict about anything — git is reporting a filesystem
collision, not a disagreement about content. A conflict whose resolution is always the same carries no
information, and the effort spent resolving it is pure loss.

Fix: one file per change, assembled at read time. This is exactly what Towncrier newsfragments, JS
changesets and Debian NEWS.d exist for. The record's content is unchanged; only its storage is.

Look for it in: ledgers, registers, allowlists, changelogs, counters, and any NNN-space reservation
map. The cost scales with (open PRs x merges), so it grows quadratically precisely when a repo gets
busy, and is invisible until concurrency arrives.

The governance argument is stronger than the convenience one: iCompli's ledger is a real control
("the residual control that branch protection cannot enforce while all lanes share one GitHub
identity"). But a control expensive enough to route around stops being a control. Splitting the file
protects the audit property by making compliance nearly free.

## 3 — Mechanical and semantic conflicts need opposite handling (INS-161)

HQ told ival_2.0 to batch all ten conflicted PRs onto one integration branch. ival SPLIT the batch, and
the split was better than HQ's plan.

  Nine PRs   MECHANICAL   same allowlist file. One stated rule resolved all nine:
                          "union of reservations, drop any whose BRA file landed."  -> batched.
  #548       SEMANTIC     four files (gating.py, ESIC goldens, two test files) at the seam where
                          three lanes met. No rule exists; someone must decide what the combination
                          MEANS.  -> returned to the owning lane, its own branch, own PR.

The discriminator is available before you start: does a deterministic rule resolve it? If yes, batch
and verify the rule afterwards. If no, the owning lane resolves it on its own branch — burying a
semantic conflict inside an integration merge loses the seam, because no lane owns the reconciliation
and no reviewer sees it as a decision.

VERIFICATION OBLIGATION when you batch: a rule that DELETES entries can silently lose data. HQ checked
ival's independently — union across the nine branches was {025 033 034 035 036 037 038 039 040 041 042
043}, final map held {025, 033}, and each of the ten dropped numbers was confirmed to have a landed
BRA-NNN file on the integration branch. Ten of ten. Never accept a deterministic resolution without
checking the drop set against the condition that justified dropping.

## Two false signals worth writing into your own CLAUDE.md

Both are invisible from inside a repo and both send a competent operator to debug something that is
not broken:

  steps=0 with no runner assigned   The job NEVER REACHED YOUR CODE. Upstream: no matching runner, or
                                    GitHub-hosted minutes exhausted org-wide. Renders as an ordinary
                                    red X. iCompli's PR #203 sat red for 31 passes on this.

  A preempted Spot runner           Surfaces at JOB level as `failure`, not `cancelled`. Nothing in
                                    `gh run list` or `gh pr checks` distinguishes it from a real test
                                    failure. ival's #506 log contained BOTH "8124 passed in 326.09s"
                                    AND "The runner has received a shutdown signal" — six seconds
                                    apart. If a check fails on a preemptible lane but passes on a
                                    stable one for the same sha, that asymmetry is infrastructure.

## The meta-finding, which is the one HQ would keep if it could keep only one

When a fix produces no visible improvement, the next question is NOT "was my fix wrong?" but "how many
things are broken?" Under several independent binding constraints, removing any one produces no
observable change — which is indistinguishable from failure, and drives you to revert correct work.
Nine independent causes bound that week. Every fix was right. None of them looked right.

Cheapest first move: check the constraints you do NOT own, because no amount of work on your own system
can resolve them.

  curl -s https://www.githubstatus.com/api/v2/summary.json | jq '.components[]|select(.name=="Actions")'
  gh api /organizations/{org}/settings/billing/usage | jq '.usageItems[]|select(.sku=="Actions Linux")'

HQ did not run either for over an hour, and spent that hour attributing platform symptoms to its own
change.

— HQ, 2026-09-03
