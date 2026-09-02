# Open Jobs Register — Agent-Assure

Per ADR-045: one entry per open thread, **every entry with a named owner**.
`owner: Sai` entries carry the reason they cannot move without him.
Last reconciled: **2026-09-02** (session `d2b27b1f`, α2 close).

---

## owner: Sai — blocked on a decision, not on work

| id | Thread | Blocking reason | Cost once ruled |
|---|---|---|---|
| J-01 | **OI-MOAT-21 — T2 is not sound** | T2 alone suffices for GROUNDED, and T2 is an F1 *ratio* over the claim's own length, which the author writes. Demonstrated: a reordering scoring f1=0.840 passes at lex_tau 0.71, 0.76 **and** 0.83. The fix (demote T2 from sufficient-for-GROUNDED) changes what the gate MEANS and invalidates the calibration lex_tau derives from — Escalation #1 **and** #3. **α5 cannot honestly precede this.** | 1.2–2.0M incl. CR-003 |
| J-02 | **ADR-004 Q1–Q6 — NLI tier** | Redefines the moat boundary and amends the "ZERO LLM calls" claim. Read the 2026-08-30 addendum: T3's case has *inverted*, not shrunk. | 3.6–6.1M |
| J-03 | **OI-DEC-01 — citation propagation across a conjunction split** | The first PASS-*enabling* change in the cohort; every other fix this cycle was fail-closed. Escalation #1. | ~0.2M |
| J-04 | **OI-T2-01 — a verbatim short quote reads UNGROUNDED** | Three candidate fixes (short-span T1 / claim-recall instead of F1 / defer to T3); all three move the Error-A/Error-B trade-off. | 0.2–0.4M |
| J-05 | **OI-MOAT-20 — verb-final header escapes scoring** | Deterministic closure needs either Error-A on every multi-word heading or a POS tagger — the latter is exactly what J-02 governs. | ~0.1M |
| J-06 | **Second blind labeller** on the 52 | Only Sai can hand the review page to a person. Converts CR-002 from single-ratifier to independent. **0 tokens.** | free |
| J-07 | **Ratify the 2026-08-30 register** (D-01…D-14) | 14 autonomous calls await ratify-or-reverse; each carries its undo. Includes the disclosed `install.sh` side effect. | free |
| J-08 | **`docs/consulting/` visibility coupling** | Committed to the HQ repo on the stated assumption that it stays PRIVATE. It names a client and records that they have no signed paper. One settings toggle, not a property a file can enforce. | free |

## owner: Claude — buildable, sequenced behind the rulings above

| id | Thread | Waits on |
|---|---|---|
| J-09 | Red-team round 6 against the CR-002 deployment + any J-01 rework | J-01 |
| J-10 | Ingest the second labeller's set: agreement stats, adjudicate disagreements, amend CR-002's independence caveat | J-06 |
| J-11 | OI-BUILD-01 — two reference worktrees still cut from the wrong base; rebase or discard | nothing (low value) |
| J-12 | Batch ingestion is built but **never exercised on real data** — cpc-book has sent no batch yet | cpc-book |

## owner: HQ / other repos

| id | Thread | State |
|---|---|---|
| J-13 | cpc-book calibration corpus (`agent-assure-cpc-pilot`) | Answered 2026-08-30; ingestion built. Waiting on their ch.1 to exist. |
| J-14 | HQ retraction filed (`hq-repo-unpushed-100-days`) | Delivered and pushed; no action pending. |

---

## Closed this session (do NOT redo)

α2 — 52 gold labels ratified, CR-002 emitted (lex_tau 0.76, held-out
Error-A 0.200 / Error-B 0.111, n=52), 0.76 deployed measurement-neutrally.
`source_type` scaffold column added, closing the corpus defect ratification
exposed. Red-team rounds 3, 4 and 5 (65 wrongful PASSes found, 11 of 12
mechanisms closed). Error-A harness built. OI-CAL-01, OI-ENV-01, OI-NUM-02,
OI-MOAT-03/-05/-07/-11…-19/-22/-23/-24 all closed.
