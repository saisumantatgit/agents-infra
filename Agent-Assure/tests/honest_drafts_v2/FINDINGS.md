# Usage instrument v2 — what an honest writer actually sees (2026-10-24)

**20 honest drafts, 177 claims, every claim true to its cited source (CANDIDATE
labels by AI agents — NOT gold). Stores built through the REAL capture hook.**

| | |
|---|---|
| Drafts that PASS | **0 of 20** (all FAIL) |
| Claims GROUNDED | **6 of 177** |
| Claims refused | **171 (97%)** — UNGROUNDED 121 · UNVERIFIED_ABSENCE 23 · UNVERIFIED_NUMBER 19 · UNCITED 6 · other 2 |

Recounted by the orchestrator from `batch_*/report_*.json`, not taken from the
agents' reports.

**Causes, ranked:** (1) natural paraphrase has no 8-token verbatim span — T1 is
the only grounding tier (T2 demoted ADR-006; T3/NLI parked); (2) ordinary
negations ("not reproduced", "deletes no files") classified as ABSENCE claims;
(3) figures misparsed ("16 MB" → "16 M", hashes, "GPT-4"); (4) sentence
splitting at commas, "and", ".py"; (5) headings scored as uncited claims.

**What it means.** The gold corpus's Error-A of 0.400 understated the real
experience (J-66 predicted this). As built, the gate passes a draft only when
its claims QUOTE their sources. Every remedy — paraphrase tolerance, a narrower
absence classifier, looser number parsing — is PASS-enabling, so each is
Escalation #1 and Sai's.

**Caveats:** AI-written drafts and AI labels; repo sources are markdown-heavy
(tables, bullets); one writer style per batch. None of these closes 0-of-20.
