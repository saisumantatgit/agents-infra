# PIR-002: The Corpus Builder Silently Destroyed Its Own Human Labels

## Metadata

| Field | Value |
|-------|-------|
| **PIR ID** | PIR-002 |
| **Date** | 2026-07-14 |
| **Severity** | P3 actual (full recovery, zero loss) — **P1 latent** (would have destroyed the n=52 gold labels post-ratification) |
| **Status** | Final |
| **Incident date** | 2026-07-14, autonomous session |
| **Detection date** | 2026-07-14, ~90 seconds after the destructive write |
| **Resolution date** | 2026-07-14, same session (`fd55e46`) |
| **Related** | OI-CAL-02 (open-issues), CN-PIR002 (narrative), ADR-025 (CRs) |

## Zone Check

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Severity** | P3 actual / **P1 latent** | Nothing was lost. The same command, run one week later, destroys evidence that cannot be regenerated. |
| **Containment** | Contained | Guard implemented, red-first proven, verified live against both real labeled files. |
| **Blast Radius** | **Latent: high** | The α1 ratification package — 52 gold labels, ~30–45 min of irreplaceable human judgment, the gate that unblocks all of Phase 2. |

## 1. Summary

While drift-checking the calibration corpus after a tier-logic change, a routine
`python -m calibration.build_corpus` run **regenerated `labeling.csv` and blanked
the `human_label` column on all 12 rows** — the labels CR-001 was calibrated on.
The builder is a template writer; writing `""` into `human_label` is what it has
always done (`build_corpus.py:460`). Nobody had noticed, because nobody had run
it after the labels existed.

Detection was immediate but **accidental**: the very next command was the
calibration run, whose fail-loud label loader refused to proceed on blank labels.
Restored from git; CR-001 subsequently re-ran and reproduced byte-identically.

The same defect lives in `build_corpus_v2.py` / `labeling-v2.csv`. **Once Sai
ratifies the 52 gold labels, the first corpus regeneration destroys them.**

## 2. Timeline

| Time | Event | Actor |
|------|-------|-------|
| (pre-existing) | `build_corpus.py` written as a template generator: writes `human_label` as `""` on every run | Agent (Phase 2a) |
| (pre-existing) | Bootstrap labels filled; CR-001 calibrated on them; file committed | Agent + Human |
| 2026-07-14 T0 | Tier logic changed (numeric + absence fixes) → standing discipline requires a corpus drift check | Agent |
| T0 + 1m | `uv run python -m calibration.build_corpus` — **12 human labels silently blanked** | Agent |
| T0 + 2m | `uv run python -m calibration.run_calibration` → `ValueError: ... has human_label '', which is not one of ['grounded','violation']` | Fail-loud loader |
| T0 + 3m | `git checkout -- calibration/labeling.csv` → 12 labels restored | Agent |
| T0 + 4m | Calibration re-run → CR-001 reproduces byte-identically (lex_tau 0.71, Error-A 0.20, Error-B 0.143) | Agent |
| T0 + ~40m | `assert_labels_not_clobbered` implemented (red-first), wired into both writers, `--features-only` added | Agent |
| T0 + ~50m | Verified live: both builders now refuse to touch the 12 + 52 labeled rows | Agent |

## 3. Five Whys

1. **Why were the human labels destroyed?** `build_corpus.py` regenerates the
   whole labeling CSV on every run and writes `human_label` as an empty string.
2. **Why does it write an empty column over a labeled one?** It was written as a
   one-shot *template generator* — it emits the file a human then fills in. It has
   no concept of the file having been filled in.
3. **Why did it have no such concept?** Because the labeling CSV is a **single file
   that mixes machine-generated scaffolding** (`claim_id`, `claim_text`, `evidence`)
   **with irreplaceable human judgment** (`human_label`) — and the generator owns
   the file. Ownership was never split, so "regenerate the scaffold" and "destroy
   the judgment" are the same operation.
4. **Why was that co-location never questioned?** Because the project's entire
   preservation discipline — "the store is audit evidence; fail loud; never
   silently repair" — was reasoned about for the *evidence store*. The labels are
   the **other** audit evidence, and nothing in the toolchain treated them as such.
5. **Why did the asymmetry go unseen?** Careful asymmetric reasoning had been
   applied to *verdicts* (Error-B unrecoverable vs Error-A recoverable) but never
   to *artifacts*. Feature rows are derived and reproducible; human labels are
   scarce and irreproducible. The builder treated both as "outputs to regenerate."

**Root cause:** a generator owns a file that also holds irreplaceable human input,
and the artifact asymmetry (derived vs irreproducible) was never modeled.

## 4. What actually saved us — and why that is not reassuring

Three things stood between the write and permanent loss. **Not one of them was
designed to prevent it:**

| Defense | Designed for this? | Detection or prevention? |
|---|---|---|
| Labels were committed to git | No — general hygiene | Recovery, and only if noticed |
| Fail-loud label loader (`load_labels`) | No — designed to reject *unlabeled/mislabeled* rows | **Detection, downstream of destruction** |
| The next command happened to be the calibration run | **No — luck** | Detection, by coincidence |

Had the sequence been `build_corpus` → `git add -A` → `commit` (an ordinary
close-out), the blanked file would have been committed over the labels, and the
loss would have surfaced only at the next calibration — with the labels one
`git log` archaeology away, or gone entirely if the labels had been ratified but
not yet committed.

**Detection is not prevention.** The system had no prevention.

## 5. Resolution

- `scripts/calibrate.py::assert_labels_not_clobbered` — raises when a labeling CSV
  carrying ANY non-empty `human_label` is about to be overwritten; names the file,
  the count, and the first labeled row. Called first by **both** writers.
- `tests/test_labeling_overwrite_guard.py` — 3 tests, **proven red** (both writers
  clobbered a labeled file happily before the guard).
- `build_corpus_v2 --features-only` — regenerates gate predictions for the standing
  post-change drift check **without touching the labeling CSV**. Rationale: without
  it, drift-checking a labeled corpus trips the guard, and *that friction is exactly
  how someone eventually deletes the labels to "make it work."*
- Verified live: both builders now refuse to overwrite the 12 bootstrap and 52
  candidate labels.

## 6. Case vs Systemic

**This is a Systemic Fix for the destruction class** (no writer can now clobber any
human label) — but it is **not** the systemic fix for the root cause.

**Remaining systemic issue (open):** the labeling CSV still co-locates generated
scaffolding with human judgment in one generator-owned file. The guard makes that
file *immutable-once-labeled*, which means **the corpus can no longer be extended
after ratification** without a manual merge — a real limitation, traded knowingly
against silent destruction. The true systemic fix is **separation**: the generator
writes the scaffold; human labels live in their own append-only file joined by
`claim_id`. Then regenerating the corpus and preserving judgment stop being the
same operation.

Carried forward as **OI-CAL-03** in `docs/open-issues/OPEN-ISSUES.md`. Sequence it
before any post-ratification corpus change.

## 7. Transferable rule

**Any generator that regenerates a file containing irreplaceable human input must
be able to tell the two apart — and must refuse, loudly, rather than rebuild.**
Better still: do not co-locate them. Classify every artifact as *derived*
(regenerable, cheap) or *authored* (irreproducible, expensive), and let no tool
treat the second like the first.

Recorded in `docs/insights/insights-log.md`; narrative in
`docs/case-narratives/CN-PIR002-The-Labels-That-Almost-Werent.md`.
