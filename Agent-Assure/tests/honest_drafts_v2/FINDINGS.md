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

## Correction and re-measure, 2026-10-25 (after D-97's fixes B1 + B2)

**Two cause attributions above were wrong.** "16 MB" and "ac77b8e" were never
figure failures — both were refused on word overlap (B2's agent showed this).
The "causes, ranked" list took its causes from the batch agents' testimony; the
verdict COUNTS were recounted from the report files and stand.

**Re-measured on readiness-a-b (A + B1 + B2), same 20 drafts, same stores:**

| | Before | After |
|---|---|---|
| GROUNDED | 6 | **6** |
| UNVERIFIED_ABSENCE | 23 | **5** |
| UNGROUNDED | 121 | 126 |
| UNVERIFIED_NUMBER | 19 | 32 |

**What B changed:** the REASON for refusal, not the pass count. Negations stopped
being misread as absence claims and are now refused as unquoted paraphrase,
which is the accurate reason and the one the tester guide (A) explains.
**What B did not change:** paraphrase is still refused — by design under A.
B1 also closed a previously unregistered Error-B (an affirmative claim grounding
against a source that negates it, when the "not" fell outside the 8-word span).
