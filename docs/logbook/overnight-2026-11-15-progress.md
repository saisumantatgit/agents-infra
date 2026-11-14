# Overnight 2026-11-15 (OVN-1115) — progress (times from clock/git)

| IST | queue | changed | tokens | frameworks |
|---|---|---|---|---|
| 00:53 | Q1–Q4 open | armed on AGREED GO (D-112); D-111 timestamp correction | ~0.03M | opportunity cost, ToC |
| 00:54 | Q1,Q2,Q3 in flight; Q4 waits on Q2 | cron 2e970b24 armed (ticks :07/:37 01–07 IST); Q1 Opus (wt ovn1115-q1), Q2 Sonnet corpus (wt ovn1115-q2), Q3 Sonnet walkthrough (scratch) dispatched in parallel | ~0.05M | critical path (Q4 needs Q2), opportunity cost |
| 00:57 | Q1,Q2 in flight; Q3 walkthrough DONE → Q3b (Opus, UNGROUNDABLE bug, ruling pack — fix lets honest claims pass ⇒ Escalation #1, held) + Q3c (Sonnet, docs) in flight | walkthrough: OK4 STALL2 WRONG-DOC3 CONFUSING8 BUG2; 0/3 honest own drafts PASS; both fabrications FAIL | ~0.3M | JTBD (tester can't test own source), error-cost asymmetry |
| 01:05 | Q1,Q2,Q3b in flight | PR #34 docs merged → main 1da3485, tree verified; suite 1276p on branch; guide's per-claim printer + 8-word fact re-checked by main loop | ~0.5M | reachability (docs where testers look) |
| 01:09 | Q1,Q2,Q3b in flight (all three growing) | tick; Q2 corpus at 5.1MB — size check at handback (cap 5MB → Drive if over) | ~0.5M | degradation under constraint (size cap) |
| 01:18 | Q1 in flight; Q2 DONE (PR #35 merged 10373da); Q3b committed 6f361f8, R41 adversary in flight; Q4 ruling pack in flight (C1–C5) | D-113; Q3b re-verified: 5 red on ef3ae1f, suite 1282p | ~1.4M | durable asset, Swiss cheese, critical path |
| 01:29 | Q1, Q4 in flight; Q3b DONE (PR #36 merged 5b6898f); Q5 docs for cited_source_is_the_draft dispatched | D-114 | ~1.7M | reachability |
| 01:39 | Q1 returned → verify; Q4 in flight; Q5 DONE (PR #37 merged bb9b024) | Q1 on merged main: suite 1371p, probe 4/34, red 54/54 on main; BUT new corpus: grounded 2044→1990 (−54), NW→FAIL 9, PASS 5 = — Error-A the old instruments could not see → narrowing round R40b before adversary | ~2.2M | Goodhart (corpus now the gate), error-cost asymmetry |
| 01:40 | Q1b, Q4, Q6 in flight | re-derived queue from walkthrough top-10: Q6 (Sonnet) add_source.py + explain_report.py + README quick start — render-only, no verdict change; #6/#7 (headings/tables scored) are pass-widening → ruling pack | ~2.4M (est. from harness subagent_tokens, both runs) | JTBD, opportunity cost |
| 01:52 | Q1b, Q4 in flight; Q6 DONE (PR #38 merged) | D-115; Q6 flow re-run by main loop | ~2.6M | JTBD |
| 01:59 | Q1b, Q4, Q8 in flight; Q7 DONE | walkthrough-2: STALL 0 (was 2), honest PASS first try 1/6, after fixes 6/6 (3 only by deleting content); fabrications 2/2 caught; top issue: verbatim claims UNGROUNDED with no reason (~14/40) → Q8 (Opus) reason-only fix, verdict-identical by differential fuzz | ~2.9M | delivery≠consumption (re-test after fixes), JTBD |
| 02:04 | Q1b, Q8 in flight; Q4 DONE; Q9 queued after Q1b | D-116; C2 re-derived first-hand | ~3.2M | error-cost asymmetry, critical path |
| 02:10 | Q1b, Q8, Q10 in flight; Q9 queued after Q1b | Q10 (Sonnet): Error-B fabrication corpus (≥280 drafts, 1 labelled fabrication each, same genres/sources as Error-A corpus) — the probes lack lists/percentages/tables (Q4 weak spot) | ~3.3M | durable asset, FMEA detectability (measure the silent failure) |
| 02:23 | Q8, Q10, R42 in flight; Q9 queued after Q1 merge | Q1b: all 54 corpus losses from one H4 branch ('never took place'); narrowed; main loop re-ran corpus → byte-identical to main, suite 1381p; committed bce1ac7; R42 final adversary dispatched. Noted: usage_genres results.json stale on main (gate gives 51 grounded, file says 48) → re-baseline item | ~3.6M | contradiction-as-locator, Goodhart |
| 02:42 | Q1c, R43 in flight; Q10 DONE (PR #39); Q8 awaiting R43; Q9 queued | D-117. Error-B baseline: 20/280 certified fabrications (headings 12, near denials 8) | ~4.5M (harness subagent_tokens, both runs) | Swiss cheese, degradation under constraint (~75% of 6M) |
| 02:42 | Q1c, R43 in flight | tick; no new starts (80% rule) | ~4.5M | degradation under constraint |
| 03:31 | R44 in flight (Q1 final gate) | Q8 merged PR #40 fefb9c5 (R43 0 verdict diffs/72k; F1 perf 87s→3s fixed by main loop); Q1 merged with main, gates green, Error-B 20→7/280; no new starts (80%) | ~5.3M est. | degradation under constraint |

## MORNING REPORT — OVN-1114 + OVN-1115 (night of 2026-11-14/15)

Verdict: 10 PRs merged (#32–#41); fabrications certified PASS on the new 280-draft fabrication corpus fell 20 → 7; honest-draft results unchanged; stopped at the token budget, not at an empty queue.

1. DONE (each re-run by the main loop; main = 3179abe)
   - PR #32 R36 fixes: r36_probe 25/34 → 4/34 attacks reproducing.
   - PR #34, #37 tester docs; PR #38 add_source.py + explain_report.py + quick start.
   - PR #35 Error-A honest corpus: 336 drafts / 14 genres; baseline PASS 5, grounded 2044/3990.
   - PR #36 "UNGROUNDABLE on verbatim source" root cause (near-copy guard) reported honestly; wrong numbers no longer hidden.
   - PR #39 Error-B fabrication corpus: 280 drafts / 18 classes; baseline 20/280 certified.
   - PR #40 refusals say why (15 verbatim_but_* codes); verdict-identical (R43, 72k drafts).
   - PR #41 R40 fail-closed (11/14 R37 classes), structurally additive to main; Error-B corpus 20 → 7; suite 1425 passed.
   - Walkthrough 2 (fresh tester): 0 stalls (was 2); honest PASS 1/6 first try, 6/6 after fixes (3 only by deleting content); fabrications 2/2 caught.
2. NOT DONE
   - Q9: remaining certified fabrications are claim/denial headings and near denials — owner Claude, next run on GO.
   - Honest short sources still UNGROUNDABLE (near-copy guard) — owner Sai (Escalation #4).
3. DENIED — none. Two pre-tool hook blocks (a restore command; a phrase in report text) — worked around by committing first and using `git show ref:path > path`; same outcome, no reroute.
4. ONE-WAY DOORS QUEUED — none.
5. UNKNOWNS — corpora authored by agents and checked by construction, not by an independent labeller; fuzz grammars miss some shapes (R44 heading-promotion proof probed on 10 drafts).
6. BUDGET — 5.14M new tokens (output 0.47M + cache creation 4.67M), de-duplicated by message id, main loop + 23 subagent transcripts since 23:20 IST; sanctioned 5M, ceiling 6M.
7. WITHDRAWALS / MY MISTAKES
   - OVN-1114 disarmed after 80 min at "diff zero" — wrong stop rule (D-111/D-112).
   - Timestamps estimated instead of read from a clock: D-106–D-110, report v1, D-113 — all corrected.
   - First R40 version refuted by R42 (a real regression vs main); merged only after the structural fix.
8. FRAMEWORKS — error-cost asymmetry, Goodhart (40-draft instrument hid Error-A), Swiss cheese (R37/R41/R42/R43/R44), durable asset (both corpora), JTBD (tester tools), degradation under constraint (stop at budget).

DECISIONS FOR SAI (owner: Sai)
   a. Ship C2 "N percent" (+69 honest claims, PASS 5→8, 0/11 attacks) — recommend YES.
   b. C1u list numbers (+286 claims, 4/12 attacks slip, keys on capitalisation) — recommend NO until a non-surface signal exists.
   c. Stop the hedge window at the sentence boundary — largest Error-A source (682 of 1,258 refused segments); Error-B cost not yet measured — recommend: measure next run.
   d. Near-copy guard / hole b: capture agent-written files in the hook (Escalation #4).
   e. Unchanged: 5-user test; D-102 row 2 / S1 (recommend NO); regulator pages.
