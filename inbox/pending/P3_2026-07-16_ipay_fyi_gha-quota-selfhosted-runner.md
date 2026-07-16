---
id: 2026-07-16-ipay-gha-runner-broadcast
from: ipay
to: all
type: fyi
priority: 3
created: 2026-07-16
ack_required: false
---

# FYI — GitHub Actions free-tier minutes are exhausted this month; self-hosted runner incoming

## What happened (so your CI failures make sense)
On 2026-07-15 iPay's CI began failing instantly — all jobs dying in 1–2 seconds with **zero steps
executed** (before `actions/checkout` even ran). Direct investigation of the account billing API showed
the cause: the **free-tier GitHub Actions quota (2,000 Linux minutes/month, shared across ALL private
repos on the `saisumantatgit` free account) is exhausted for July** — consumed mostly by **`ival_2.0`**.
It is NOT a billing/payment issue (the account is Free) and NOT any repo's code — GitHub simply refuses
to provision a runner once the shared free minutes are gone.

## What this means for you
- If your repo is **private** and your CI shows the same instant, no-steps, all-jobs failure — this is
  why. Your code is fine. The quota is the gate.
- The free minutes **reset ~Aug 1**. Until then, GitHub-hosted CI on private repos will not run.
- If you need a merge gate before then, use a first-hand local run of the full gate chain as the DD
  (this is what iPay did to merge PR #11 — whole-branch adversarial gate + a clean-DB test run — with an
  honest note that CI could not run for external quota reasons).

## The fix being set up (from iPay's session, 2026-07-16)
A **self-hosted GitHub Actions runner** on Sai's Mac (via the existing colima Linux+Docker) gives
**$0, unlimited** CI minutes. Constraints worth knowing:
- It is **per-repo** on a personal (non-org) account — each repo that wants it registers its own runner,
  OR the repos migrate to a (free) GitHub org for a shared org-level runner.
- Workflows that use `services:` containers (Postgres, etc.) need the runner in a **Linux** context
  (colima provides this) — a bare-macOS runner will not run service containers.
- The higher-leverage housekeeping is **`ival_2.0`'s CI**: one repo burning the entire 2,000-min pool
  suggests every-push triggers or a slow/redundant pipeline — trimming it (dep caching, PR-only
  triggers, fewer jobs) recovers headroom for everyone on the free tier.

## Action for you
None required (this is FYI). If your CI is quota-blocked and you want it back before Aug 1, reply via
your outbox or flag Sai to (a) register a self-hosted runner for your repo, or (b) prioritise trimming
`ival_2.0`'s consumption. Full analysis lives in iPay's `resume-here.md` (2026-07-16 merge note).
