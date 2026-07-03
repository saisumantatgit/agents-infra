"""Agent-Assure: calibration harness — per-claim raw feature emission.

Phase 2a, Task 2. Runs decompose -> classify -> ground per claim over a
(query_id, draft_text, store) triple and records the RAW tier features
(t1_verbatim, t2_f1, numeric_ok) alongside the CURRENT predicted verdict —
so a later calibration sweep (Tasks 3+) can re-threshold lex_tau /
min_quote_len post-hoc over stored scores, without re-running decompose,
classify, or ground.

Phase 2a, Task 3 adds the human-labeling round trip: export_labeling_csv
turns ClaimFeatureRow rows into a CSV a human fills in with a
"grounded"/"violation" verdict per claim; load_labels reads that filled CSV
back, failing loud on any unlabeled or mislabeled row; join_labels
inner-joins emitted rows against those labels by claim_id, failing loud if
any emitted claim has no label.

Pure functions only, except export_labeling_csv and load_labels, which are
the explicit file I/O boundary — neither mutates its inputs.
"""

from __future__ import annotations

import csv
import unicodedata
from collections import Counter
from dataclasses import dataclass

from scripts.ground_check import (
    Claim,
    RetrievedSource,
    classify,
    decompose,
    ground,
    numeric_ok,
    resolve,
    t1_verbatim,
    t2_lexical_score,
)


@dataclass(frozen=True)
class ClaimFeatureRow:
    """One row of raw per-claim grounding features for calibration.

    Captures the tier features BEFORE the ground() dispatcher collapses them
    into a single verdict, so a calibration sweep can re-threshold lex_tau /
    min_quote_len post-hoc over the stored t1_verbatim/t2_f1 values.
    """

    claim_id: str
    query_id: str
    claim_text: str
    kind: str
    cited_source_ids: tuple[str, ...]
    citations_resolved: bool
    t1_verbatim: bool
    t2_f1: float
    numeric_ok: bool
    predicted_verdict: str
    # True iff predicted_verdict can change under a different lex_tau, i.e.
    # (predicted_verdict == "UNGROUNDED") or (predicted_verdict == "GROUNDED"
    # and not t1_verbatim). Only these two states are lex_tau-sensitive:
    # GROUNDED-via-T2 (t1_verbatim False) can become UNGROUNDED at a higher
    # lex_tau, and UNGROUNDED can become GROUNDED at a lower one. Every other
    # verdict is FIXED regardless of lex_tau — including GROUNDED-via-T1
    # (t1_verbatim never consults lex_tau) and UNGROUNDABLE (ground() never
    # reaches the tier check at all for that claim; see _resolve_verbatim_
    # sources docstring). A calibration sweep re-thresholding lex_tau over
    # t2_f1 MUST skip rows where tier_sensitive is False, or it will miscount
    # verdicts that cannot possibly flip.
    tier_sensitive: bool


def _bare_source_id(citation: str) -> str:
    """Strip the surrounding brackets from a citation marker.

    '[S1]' -> 'S1'; a bare id with no brackets is returned unchanged. Mirrors
    the bracket-stripping in ground_check.resolve(), but skips re-running
    NFKC normalization: classify() already NFKC-normalizes claim.text (and
    therefore the citations extracted from it) before this function ever
    sees them.
    """
    if citation.startswith("[") and citation.endswith("]"):
        return citation[1:-1]
    return citation


def _resolve_verbatim_sources(
    claim: Claim, store: dict[str, RetrievedSource]
) -> tuple[list[RetrievedSource | None], list[RetrievedSource]]:
    """Return (resolved_sources, verbatim_sources) for claim.citations.

    resolved_sources parallels claim.citations positionally (None where a
    citation does not resolve against *store*). verbatim_sources is the
    subset that resolved AND carries full_text_source == "verbatim" with
    non-empty text.

    NOT parity with ground()'s internal filtering: ground() (spec §4.4) runs
    its "any resolved source has falsy text" and "no verbatim source among
    cited" checks over ALL resolved citations (verbatim + non-verbatim)
    BEFORE narrowing to verbatim, and short-circuits to UNVERIFIED_CITATION /
    UNGROUNDABLE / UNVERIFIED_NUMBER without ever reaching the T1/T2 tier
    check for many claims. This helper narrows to verbatim FIRST, so it can
    report t1_verbatim/t2_f1 even for claims where ground() never computed
    them. A claim can score t1_verbatim=True, t2_f1=1.0 here while
    ground()'s predicted_verdict is UNGROUNDABLE (e.g. a co-cited
    non-verbatim source with empty text trips ground()'s earlier check).
    predicted_verdict is always authoritative; raw t1_verbatim/t2_f1 are only
    meaningfully re-thresholdable for rows where ClaimFeatureRow.tier_sensitive
    is True.
    """
    resolved_sources = [resolve(c, store) for c in claim.citations]
    verbatim_sources = [
        s for s in resolved_sources
        if s is not None and s.full_text_source == "verbatim" and s.text
    ]
    return resolved_sources, verbatim_sources


def emit_claim_features(
    query_id: str,
    draft_text: str,
    store: dict[str, RetrievedSource],
) -> list[ClaimFeatureRow]:
    """Run decompose -> classify -> ground over *draft_text* against *store*
    and return one ClaimFeatureRow per decomposed claim, in claim order.

    For each claim, t1_verbatim/t2_f1/numeric_ok are computed over the
    verbatim-filtered cited sources (t2_f1 is the MAX t2_lexical_score across
    them, 0.0 when none exist), independent of the predicted_verdict — so the
    raw features survive even when the verdict short-circuits before running
    the tiers (e.g. UNVERIFIED_CITATION, UNGROUNDABLE).

    These raw t1_verbatim/t2_f1 values are NOT guaranteed to be the features
    ground() actually consulted to reach predicted_verdict — ground() may
    short-circuit (on an unresolved citation, a falsy-text source anywhere in
    the citation list, no verbatim source, or a NUMERIC/numeric_ok failure)
    before ever reaching the T1/T2 tier check. predicted_verdict is always
    authoritative. tier_sensitive marks the rows where a re-thresholded
    lex_tau could plausibly change predicted_verdict; a calibration sweep
    over t2_f1 must restrict itself to tier_sensitive rows, or it will
    miscount claims whose verdict cannot flip.

    Pure function — no I/O, no mutation of *store* or *draft_text*.
    """
    rows: list[ClaimFeatureRow] = []
    for raw_claim in decompose(draft_text):
        claim = classify(raw_claim)
        cited_source_ids = tuple(_bare_source_id(c) for c in claim.citations)

        _resolved, verbatim_sources = _resolve_verbatim_sources(claim, store)
        citations_resolved = all(s is not None for s in _resolved)

        t1 = t1_verbatim(claim, verbatim_sources)
        t2 = max(
            (t2_lexical_score(claim.text, s.text) for s in verbatim_sources),
            default=0.0,
        )
        num_ok = numeric_ok(claim, verbatim_sources)

        verdict = ground(claim, store)

        # Only these two verdict states flip under a different lex_tau:
        # GROUNDED-via-T2 (t1 False; a higher lex_tau can drop it to
        # UNGROUNDED) and UNGROUNDED (a lower lex_tau can raise it to
        # GROUNDED). Every other verdict — including GROUNDED-via-T1
        # (lex_tau-invariant) and UNGROUNDABLE (ground() never reached the
        # tier check) — is fixed regardless of lex_tau.
        tier_sensitive = (verdict.value == "UNGROUNDED") or (
            verdict.value == "GROUNDED" and not t1
        )

        rows.append(ClaimFeatureRow(
            claim_id=f"{query_id}#{claim.index}",
            query_id=query_id,
            claim_text=claim.text,
            kind=claim.kind.value,
            cited_source_ids=cited_source_ids,
            citations_resolved=citations_resolved,
            t1_verbatim=t1,
            t2_f1=t2,
            numeric_ok=num_ok,
            predicted_verdict=verdict.value,
            tier_sensitive=tier_sensitive,
        ))
    return rows


# ---------------------------------------------------------------------------
# Task 3: labeling-CSV export + fail-loud label ingestion.
# ---------------------------------------------------------------------------

_ALLOWED_HUMAN_LABELS = frozenset({"grounded", "violation"})

_EXPORT_FIELDNAMES = [
    "claim_id",
    "query_id",
    "claim_text",
    "cited_source_ids",
    "predicted_verdict",
    "t2_f1",
    "human_label",
]


@dataclass(frozen=True)
class HumanLabel:
    """One human-provided ground-truth label for a claim, read back from a
    hand-filled labeling CSV.

    label is NFKC-normalized and guaranteed (by load_labels) to be exactly
    "grounded" or "violation" — never blank, never anything else.
    """

    claim_id: str
    label: str
    violation_kind: str | None


@dataclass(frozen=True)
class LabeledClaim:
    """A ClaimFeatureRow joined with its human label.

    Carries every ClaimFeatureRow field plus the human-assigned label, so a
    calibration sweep can compare predicted_verdict against ground truth at
    every candidate threshold without re-joining on claim_id each time.
    """

    claim_id: str
    query_id: str
    claim_text: str
    kind: str
    cited_source_ids: tuple[str, ...]
    citations_resolved: bool
    t1_verbatim: bool
    t2_f1: float
    numeric_ok: bool
    predicted_verdict: str
    tier_sensitive: bool
    label: str


def export_labeling_csv(rows: list[ClaimFeatureRow], path: str) -> None:
    """Write *rows* to *path* as a CSV for a human to label.

    Columns, in this exact order: claim_id, query_id, claim_text,
    cited_source_ids, predicted_verdict, t2_f1, human_label. human_label is
    left blank — a human fills it in with "grounded" or "violation" before
    the file is fed to load_labels(). cited_source_ids (a tuple) is
    serialized "|"-joined so multi-citation claims stay in one cell.

    I/O boundary — the file write is the only side effect; *rows* is not
    mutated.
    """
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(_EXPORT_FIELDNAMES)
        for row in rows:
            writer.writerow([
                row.claim_id,
                row.query_id,
                row.claim_text,
                "|".join(row.cited_source_ids),
                row.predicted_verdict,
                row.t2_f1,
                "",
            ])


def load_labels(path: str) -> dict[str, HumanLabel]:
    """Read a hand-filled labeling CSV at *path* and return
    {claim_id: HumanLabel}.

    Fails loud (ValueError) the moment any row's human_label — after
    unicodedata.normalize("NFKC", ...), per the repo's NFKC-before-
    validation safety-gate convention — is not exactly "grounded" or
    "violation", including a blank cell. An unlabeled or mislabeled row
    must never silently default to a verdict; that would corrupt every
    threshold a calibration sweep later derives from this file.

    violation_kind is read from an optional "violation_kind" column — not
    written by export_labeling_csv, but a human may add it by hand when
    labeling a violation. A missing column or blank cell resolves to None;
    it is not part of the fail-loud gate.
    """
    labels: dict[str, HumanLabel] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for line_no, record in enumerate(reader, start=2):
            claim_id = record["claim_id"]
            raw_label = record.get("human_label") or ""
            label = unicodedata.normalize("NFKC", raw_label)
            if label not in _ALLOWED_HUMAN_LABELS:
                raise ValueError(
                    f"load_labels: {path!r} line {line_no} "
                    f"(claim_id={claim_id!r}) has human_label "
                    f"{raw_label!r}, which is not one of "
                    f"{sorted(_ALLOWED_HUMAN_LABELS)}. Every row must be "
                    "labeled by hand before calibration — an unlabeled or "
                    "mislabeled row is never silently defaulted."
                )
            raw_kind = (record.get("violation_kind") or "").strip()
            violation_kind = raw_kind or None
            labels[claim_id] = HumanLabel(
                claim_id=claim_id, label=label, violation_kind=violation_kind
            )
    return labels


def join_labels(
    rows: list[ClaimFeatureRow], labels: dict[str, HumanLabel]
) -> list[LabeledClaim]:
    """Inner-join *rows* against *labels* by claim_id, preserving row order.

    Fails loud (ValueError) the moment any row's claim_id has no entry in
    *labels* — a claim silently dropped from the labeled set would bias
    every threshold the calibration sweep derives from it, with no signal
    that data went missing.
    """
    joined: list[LabeledClaim] = []
    for row in rows:
        human_label = labels.get(row.claim_id)
        if human_label is None:
            raise ValueError(
                f"join_labels: claim_id {row.claim_id!r} has no human "
                "label in labels. Every emitted claim must be labeled "
                "before calibration — no claim is silently dropped."
            )
        joined.append(LabeledClaim(
            claim_id=row.claim_id,
            query_id=row.query_id,
            claim_text=row.claim_text,
            kind=row.kind,
            cited_source_ids=row.cited_source_ids,
            citations_resolved=row.citations_resolved,
            t1_verbatim=row.t1_verbatim,
            t2_f1=row.t2_f1,
            numeric_ok=row.numeric_ok,
            predicted_verdict=row.predicted_verdict,
            tier_sensitive=row.tier_sensitive,
            label=human_label.label,
        ))
    return joined


# ---------------------------------------------------------------------------
# Task 4: Error-A / Error-B at a threshold — THE CRUX.
#
# The positive class is pinned to "claim is a grounding VIOLATION": the gate is
# a violation detector. The two error types are asymmetric, and every threshold
# the calibration sweep later derives depends on keeping them distinct:
#
#   * Error A (false positive, fp) — a truly-GROUNDED claim FLAGGED as a
#     violation. RECOVERABLE: it lands in an appendix a human sees.
#   * Error B (false negative, fn) — a truly-VIOLATION claim PASSED as grounded.
#     UNRECOVERABLE: a fabrication ships inside a "verified" report. This is THE
#     error the whole tool exists to prevent.
# ---------------------------------------------------------------------------

# Verdicts that count as "grounded" (not a violation) for a FIXED, non-tier
# row — the numerator set of ground_check.score_report (spec §4.5). Every other
# verdict (UNGROUNDED, UNVERIFIED_*, UNGROUNDABLE, ...) is a violation.
_GROUNDED_VERDICTS: frozenset[str] = frozenset({"GROUNDED", "ABSENCE_SUPPORTED"})


def predicted_is_violation(
    row: ClaimFeatureRow | LabeledClaim, lex_tau: float
) -> bool:
    """Recompute the gate's violation call for *row* at a candidate *lex_tau*.

    Keys on row.tier_sensitive (added in Task 2), because only tier_sensitive
    rows can flip under a different lex_tau:

    * tier_sensitive: the verdict is GROUNDED-via-T2 or UNGROUNDED, both decided
      purely by whether t2_f1 clears the T2 threshold. The claim is a violation
      iff ``row.t2_f1 < lex_tau`` (strictly below → UNGROUNDED). The stored
      predicted_verdict is IGNORED — it reflects the ORIGINAL lex_tau and is
      recomputed here from the raw t2_f1 score.

    * NOT tier_sensitive: the verdict is FIXED regardless of lex_tau (the
      ground() dispatcher never reached the tier check, or reached it via
      lex_tau-invariant T1). The claim is a violation iff its verdict is not in
      _GROUNDED_VERDICTS. A row with high t1_verbatim/t2_f1 but verdict
      UNGROUNDABLE stays a violation at EVERY lex_tau — lowering lex_tau must
      never spuriously re-ground it (the Task-2 review's correctness case).

    Pure function — reads *row*, mutates nothing.
    """
    if row.tier_sensitive:
        return row.t2_f1 < lex_tau
    return row.predicted_verdict not in _GROUNDED_VERDICTS


@dataclass(frozen=True)
class ErrorRates:
    """Confusion-matrix counts and the two asymmetric error rates at one lex_tau.

    Positive class = violation. n is the total labeled claims; tp/fp/tn/fn are
    the four confusion cells; error_a and error_b are the two rates the whole
    calibration exists to trade off.

    * tp — violation-labeled, predicted violation (caught fabrication).
    * fp — grounded-labeled, predicted violation (**Error A**, recoverable false
      alarm).
    * tn — grounded-labeled, predicted grounded (correct pass).
    * fn — violation-labeled, predicted grounded (**Error B**, UNRECOVERABLE —
      a fabrication shipped inside a "verified" report).
    * error_a = fp / (fp + tn) — false-alarm rate over truly-grounded claims.
    * error_b = fn / (fn + tp) — miss rate over truly-violation claims.

    A zero denominator yields the corresponding rate as 0.0 while the counts stay
    exposed, so an empty class is never a silent NaN or a crash.
    """

    n: int
    tp: int
    fp: int
    tn: int
    fn: int
    error_a: float
    error_b: float


def error_rates(labeled: list[LabeledClaim], lex_tau: float) -> ErrorRates:
    """Aggregate *labeled* into an ErrorRates at *lex_tau* (positive = violation).

    For each claim: truth = (label == "violation"); prediction =
    predicted_is_violation(claim, lex_tau). The four cells follow directly, and
    error_a / error_b are computed over the truly-grounded and truly-violation
    denominators respectively (0.0 on a zero denominator, counts still exposed).

    Pure function — reads *labeled*, mutates nothing.
    """
    tp = fp = tn = fn = 0
    for claim in labeled:
        truth_violation = claim.label == "violation"
        pred_violation = predicted_is_violation(claim, lex_tau)
        if truth_violation and pred_violation:
            tp += 1
        elif truth_violation and not pred_violation:
            fn += 1
        elif not truth_violation and pred_violation:
            fp += 1
        else:
            tn += 1

    grounded_total = fp + tn      # truly-grounded denominator for Error A
    violation_total = fn + tp     # truly-violation denominator for Error B
    error_a = fp / grounded_total if grounded_total else 0.0
    error_b = fn / violation_total if violation_total else 0.0

    return ErrorRates(
        n=len(labeled),
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        error_a=error_a,
        error_b=error_b,
    )


# ---------------------------------------------------------------------------
# Task 5: threshold sweep + moat-integrity operating-point selection.
#
# select_operating_point encodes THE differentiated bias of the whole tool. It is
# deliberately NOT an F1/accuracy-maximizing selection: F1 weights the two errors
# EQUALLY, which contradicts the asymmetry the gate is built around. Because
# Error B (a fabrication passing as grounded) is UNRECOVERABLE and Error A (a real
# claim flagged) is recoverable, the rule drives Error B under a hard bound FIRST,
# then minimizes the recoverable Error A among the taus that clear the bound. If
# no tau can meet the bound it RAISES — never silently degrading to a least-bad or
# F1-max point. The moat bias must not be bypassable.
# ---------------------------------------------------------------------------


def sweep_thresholds(
    labeled: list[LabeledClaim], taus: list[float]
) -> list[tuple[float, ErrorRates]]:
    """Evaluate error_rates(labeled, tau) at every tau in *taus*.

    Returns a list of (tau, ErrorRates) pairs sorted by ascending tau, so a
    downstream selector sees the sweep in monotone-threshold order. Pure
    function — reads *labeled* and *taus*, mutates neither (sorted() copies).
    """
    return [(tau, error_rates(labeled, tau)) for tau in sorted(taus)]


def select_operating_point(
    sweep: list[tuple[float, ErrorRates]], error_b_bound: float
) -> float:
    """Return the moat-integrity operating-point tau from a *sweep*.

    THE differentiated rule (NOT F1/accuracy maximization):

    * Among the taus whose ``error_b <= error_b_bound``, return the one with the
      LOWEST ``error_a``. Ties are broken toward the HIGHER tau (stricter
      grounding) — stricter grounding can only help Error B without costing the
      already-minimal Error A.
    * If NO tau meets the bound, raise ``ValueError`` naming the best achievable
      Error-B. Never silently fall back to an F1-max or least-bad point: Error B
      (a fabrication passing as grounded) is unrecoverable, and the bound is a
      hard floor the selection is not permitted to bypass.

    Rationale: F1 weights Error A and Error B equally, which contradicts the
    asymmetry the whole gate exists to encode. Driving Error B under a hard bound
    first, then minimizing the recoverable Error A, is the bias that makes the
    tool trustworthy — keeping it here keeps it out of a caller's discretion.

    Pure function — reads *sweep*, mutates nothing.
    """
    if not sweep:
        raise ValueError(
            "select_operating_point: empty sweep — no operating point to "
            "select. Run sweep_thresholds over a non-empty tau list first."
        )

    compliant = [
        (tau, rates) for tau, rates in sweep if rates.error_b <= error_b_bound
    ]
    if not compliant:
        best_tau, best_rates = min(
            sweep, key=lambda pair: (pair[1].error_b, -pair[0])
        )
        raise ValueError(
            f"select_operating_point: no tau meets error_b_bound="
            f"{error_b_bound}; best achievable error_b is {best_rates.error_b} "
            f"at tau={best_tau}. Error B (a fabrication passing as grounded) is "
            "unrecoverable — the moat-integrity bias forbids silently falling "
            "back to an F1-max or least-bad operating point. Raise the bound or "
            "improve the detector; do not bypass it."
        )

    # Lowest error_a wins; ties broken toward the higher tau (-pair[0] makes the
    # larger tau sort first among equal error_a).
    best_tau, _ = min(compliant, key=lambda pair: (pair[1].error_a, -pair[0]))
    return best_tau


# ---------------------------------------------------------------------------
# Task 6: overfit guard — leave-one-out genuinely-HELD-OUT error rates.
#
# THE HONESTY GUARANTEE of the whole harness. select_operating_point (Task 5)
# tunes tau to the data it is handed; scoring that same data at that tau reports
# an IN-SAMPLE optimism — the detector graded on the exam it was tuned on. To
# report the error the caller will actually face on unseen claims, each claim
# must be scored at a tau chosen WITHOUT seeing it:
#
#   for each held-out claim i:
#     tau_i = select_operating_point over the OTHER n-1 claims   (i is NOT in it)
#     accumulate the single held-out prediction of claim i at tau_i
#
# The held-out claim is NEVER in the set its own tau was selected on — that
# leakage is the exact bug this function exists to prevent. Leakage would collapse
# the held-out rates back onto the in-sample rates, hiding overfitting.
# ---------------------------------------------------------------------------


def loo_operating_point(
    labeled: list[LabeledClaim],
    taus: list[float],
    error_b_bound: float,
) -> tuple[float, ErrorRates]:
    """Leave-one-out held-out operating point over *labeled*.

    For EACH claim, select the moat-integrity operating point on the OTHER n-1
    claims (``select_operating_point`` over a sweep of *taus* computed from just
    those n-1), predict the single held-out claim at that tau, and accumulate the
    held-out confusion cell. Returns ``(modal selected tau, held-out ErrorRates)``
    where the ErrorRates are aggregated over all n held-out predictions — GENUINELY
    held-out, because no claim ever influenced the tau it was scored at.

    Fold-selection failure — DOCUMENTED DECISION: PROPAGATE, never skip. When a
    fold's n-1 training set cannot meet *error_b_bound*, ``select_operating_point``
    raises ``ValueError``; this function re-raises it enriched with the failing
    fold's ``claim_id`` (``from`` the original). Skipping such a fold would drop
    exactly the hardest claims from the held-out estimate, biasing it
    OPTIMISTICALLY — the precise dishonesty this function exists to prevent. A
    hard floor the detector cannot clear is a real result the caller must see, not
    paper over (mirrors select_operating_point's own no-silent-fallback stance).

    Modal-tau tie-break: when two taus are selected equally often across folds,
    the HIGHER tau wins — consistent with select_operating_point's stricter-
    grounding tie-break. The returned tau is a representative operating point; the
    load-bearing output is the held-out ErrorRates.

    Raises ``ValueError`` on an empty *labeled* (no folds, no held-out prediction,
    no modal tau to report).

    Pure/deterministic — reads *labeled* and *taus*, mutates neither.
    """
    if not labeled:
        raise ValueError(
            "loo_operating_point: empty labeled set — no folds to leave one out "
            "of, so no held-out rates and no operating point to report."
        )

    selected_taus: list[float] = []
    tp = fp = tn = fn = 0
    for i, held_out in enumerate(labeled):
        others = labeled[:i] + labeled[i + 1:]
        sweep = sweep_thresholds(others, taus)
        try:
            tau = select_operating_point(sweep, error_b_bound)
        except ValueError as exc:
            raise ValueError(
                f"loo_operating_point: fold holding out claim_id "
                f"{held_out.claim_id!r} could not select an operating point on "
                f"its n-1 training claims. Propagating rather than skipping — a "
                f"dropped fold would optimistically bias the held-out estimate. "
                f"Underlying: {exc}"
            ) from exc

        selected_taus.append(tau)
        # Score the single held-out claim at its own fold's tau, reusing the
        # tested confusion logic (predicted_is_violation + truth). Exactly one
        # cell of this single-claim ErrorRates is 1; accumulate it.
        fold = error_rates([held_out], tau)
        tp += fold.tp
        fp += fold.fp
        tn += fold.tn
        fn += fold.fn

    grounded_total = fp + tn      # truly-grounded denominator for Error A
    violation_total = fn + tp     # truly-violation denominator for Error B
    error_a = fp / grounded_total if grounded_total else 0.0
    error_b = fn / violation_total if violation_total else 0.0

    held_out_rates = ErrorRates(
        n=len(labeled),
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        error_a=error_a,
        error_b=error_b,
    )

    # Modal selected tau; ties broken toward the HIGHER tau (stricter grounding).
    counts = Counter(selected_taus)
    max_count = max(counts.values())
    modal_tau = max(tau for tau, count in counts.items() if count == max_count)

    return modal_tau, held_out_rates


# ---------------------------------------------------------------------------
# Task 7: report-gate derivation — separation-point (spec §5.4).
#
# Replaces the provisional 0.90 report-gate placeholder
# (ground_check.score_report's `threshold` default) with the EMPIRICAL score
# that best separates human-approved (trustworthy) reports from
# human-rejected (untrustworthy) ones, over a whole-report grounding_score
# rather than a per-claim one. Does NOT touch the UNVERIFIED_CITATION hard
# override — that stays categorical regardless of this derived gate (spec
# §5.4); wiring the derived value back into score_report's default is a
# separate later step, out of scope here.
#
# THE RULE: a candidate threshold t predicts "trustworthy" iff
# grounding_score >= t. Correctness only changes AT an observed score value
# — never strictly between two adjacent ones — so every achievable distinct
# accuracy corresponds to a whole OPEN INTERVAL of tied t values, bounded by
# two adjacent distinct observed scores. derive_report_gate finds the
# interval(s) whose t maximizes total correct classifications, then resolves
# the interval to a single float via the documented tie-break: the MIDPOINT
# of its two bounding scores. In the perfectly-separable case those two
# bounding scores are exactly the highest untrustworthy score and the lowest
# trustworthy score (the brief's own phrasing); under overlap they are
# simply the two scores immediately straddling the winning interval — the
# same rule, generalized.
#
# Multi-modal tie (two or more DISJOINT winning intervals achieve the exact
# same max count — not rare with genuine overlap): the brief does not
# specify this case, so this task documents its own secondary rule — prefer
# the WIDER bounding interval (a larger margin is a more robustly separated
# candidate), and if still tied on width, prefer the HIGHER interval,
# mirroring select_operating_point's existing stricter-grounding tie-break
# (Task 5) elsewhere in this file.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReportLabel:
    """One human holistic judgment of a whole report's trustworthiness,
    paired with the report's grounding_score, for report-gate calibration.

    Distinct from ClaimFeatureRow/LabeledClaim (Tasks 2–3), which label
    individual CLAIMS for the per-claim lex_tau gate; ReportLabel labels one
    entire REPORT (one grounding_score, one human verdict) for the report-
    level gate derived by derive_report_gate.
    """

    query_id: str
    grounding_score: float
    trustworthy: bool


def derive_report_gate(reports: list[ReportLabel]) -> float:
    """Return the report-gate threshold that best separates *reports* into
    trustworthy (human-approved) vs untrustworthy (human-rejected), per the
    module-level rule documented above.

    Degenerate inputs raise ValueError rather than return a silently-wrong
    sentinel — none of the following has a real empirical threshold to
    report:
      * *reports* is empty — nothing to separate.
      * every report is trustworthy, or every report is untrustworthy — no
        example of the missing class exists to anchor a separation boundary
        from the other side.
      * every report shares one identical grounding_score across both
        classes — no threshold value places any two reports on different
        sides, so there is no breakpoint to derive a gate from.

    Pure function — reads *reports*, mutates nothing.
    """
    if not reports:
        raise ValueError(
            "derive_report_gate: empty reports — no reports to separate, so "
            "no gate to derive."
        )

    trustworthy_scores = [r.grounding_score for r in reports if r.trustworthy]
    untrustworthy_scores = [
        r.grounding_score for r in reports if not r.trustworthy
    ]
    if not trustworthy_scores:
        raise ValueError(
            "derive_report_gate: no trustworthy reports in the input — "
            "there is no example of the approved class to anchor a "
            "separation boundary from above. Returning a sentinel gate "
            "(e.g. 0.0, letting everything pass) would be a silently "
            "fabricated threshold with zero empirical support."
        )
    if not untrustworthy_scores:
        raise ValueError(
            "derive_report_gate: no untrustworthy reports in the input — "
            "there is no example of the rejected class to anchor a "
            "separation boundary from below. Returning a sentinel gate "
            "(e.g. 1.0, failing everything) would be a silently fabricated "
            "threshold with zero empirical support."
        )

    distinct_scores = sorted({r.grounding_score for r in reports})
    if len(distinct_scores) < 2:
        raise ValueError(
            "derive_report_gate: every report shares one identical "
            f"grounding_score ({distinct_scores[0]!r}) across both classes "
            "— no threshold value places any two reports on different "
            "sides, so there is no breakpoint to derive a gate from."
        )

    best_count = -1
    best_intervals: list[tuple[float, float]] = []
    for lower, upper in zip(distinct_scores, distinct_scores[1:]):
        candidate = (lower + upper) / 2
        correct = sum(
            1
            for r in reports
            if (r.grounding_score >= candidate) == r.trustworthy
        )
        if correct > best_count:
            best_count = correct
            best_intervals = [(lower, upper)]
        elif correct == best_count:
            best_intervals.append((lower, upper))

    if len(best_intervals) > 1:
        # Multi-modal tie: prefer the widest margin, then the higher interval.
        lower, upper = max(
            best_intervals, key=lambda pair: (pair[1] - pair[0], pair[0])
        )
    else:
        lower, upper = best_intervals[0]

    return (lower + upper) / 2
