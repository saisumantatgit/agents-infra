"""Agent-Assure calibration: Phase α1 widened corpus builder (n>=50).

Extends the Phase-2a bootstrap (calibration/build_corpus.py, n=12) to a
ratification-ready corpus of >=50 single-claim queries spanning the full
grounding-failure taxonomy (references/grounding-failure-types.md), curated
for class balance (>=30% violation, the pinned positive class) and HARDNESS:
near-miss paraphrases below/above lex_tau, subtle numeric drift (value and
unit), plausible fabricated citations, negation-inverted lexical matches,
relational over-association, and absence head-noun edge cases.

Reuses the bootstrap's proven mechanisms (build_corpus._source,
_evidence_text, write_feature_rows_jsonl, emit_rows_for_cases) rather than
re-implementing them. Each case is deliberately SINGLE-CLAIM (one query ->
one decomposed claim) so a human-facing candidate label can be attached to
each claim unambiguously; the builder FAILS LOUD if any draft decomposes to
!= 1 claim.

Two artifacts written:

  calibration/feature_rows-v2.jsonl   one ClaimFeatureRow per line (internal;
                                      carries predicted_verdict for the α2
                                      calibration run and for our sanity check).
  calibration/labeling-v2.csv         the CANDIDATE labeling package a human
                                      (Sai) ratifies. Columns:
                                        claim_id, query_id, claim_text,
                                        evidence, human_label,
                                        candidate_verdict, rationale,
                                        label_status
                                      label_status="candidate" on EVERY row.
                                      human_label carries the candidate verdict
                                      (grounded/violation) so a ratifier edits
                                      in place; candidate_verdict preserves the
                                      original machine-assisted proposal even
                                      after human_label is corrected. The
                                      calibration loader (scripts.calibrate.
                                      load_labels) REFUSES to ingest any file
                                      whose label_status is not "gold" — this
                                      package cannot enter a calibration run
                                      until Sai flips label_status to gold.

NOTE on anchoring bias: the bootstrap labeling.csv deliberately OMITS the
gate's predicted verdict to keep a blind labeler unbiased. This α1 package is
a different workflow — CANDIDATE ratification, not blind labeling — so it
surfaces a candidate verdict and rationale by design (Sai reviews and
corrects, he does not label from scratch). The tradeoff is explicit and
documented in the ratification brief.

Pure functions except main(), the file-I/O boundary.
"""

from __future__ import annotations

import csv
import hashlib
import unicodedata
from dataclasses import dataclass

from calibration.build_corpus import (
    CorpusCase,
    _evidence_text,
    _source,
    emit_rows_for_cases,
    write_feature_rows_jsonl,
)
from scripts.calibrate import ClaimFeatureRow
from scripts.ground_check import RetrievedSource

_FEATURE_ROWS_PATH = "calibration/feature_rows-v2.jsonl"
_LABELING_CSV_PATH = "calibration/labeling-v2.csv"

_CANDIDATE_LABELS = frozenset({"grounded", "violation"})
_LABEL_STATUS = "candidate"


def _summary_source(source_id: str, text: str, query_provenance: str) -> RetrievedSource:
    """Build a NON-verbatim (haiku_summary) RetrievedSource.

    Mirrors build_corpus._source but sets full_text_source="haiku_summary",
    so ground() reaches UNGROUNDABLE (no verbatim text to run the tiers
    against) — the taxonomy's summary-only failure class.
    """
    normalized = unicodedata.normalize("NFKC", text)
    return RetrievedSource(
        source_id=source_id,
        url=None,
        file_path=None,
        fetched_at="2026-07-08T00:00:00Z",
        tool="calibration_fixture",
        content_sha256=hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        text=text,
        full_text_source="haiku_summary",
        captured_via="inline",
        query_provenance=query_provenance,
    )


@dataclass(frozen=True)
class CandidateCase:
    """A single-claim CorpusCase paired with its human-facing candidate label.

    candidate_label is the ground-truth grounding judgment (grounded/violation)
    a ratifier reviews — INDEPENDENT of the gate's mechanical predicted_verdict
    (they diverge on the hard rows, which is the point). rationale is the
    one-line justification shown in the labeling package. low_confidence marks
    the rows flagged for closest human attention in the ratification brief.
    """

    case: CorpusCase
    candidate_label: str
    rationale: str
    low_confidence: bool = False

    def __post_init__(self) -> None:
        if self.candidate_label not in _CANDIDATE_LABELS:
            raise ValueError(
                f"CandidateCase({self.case.query_id!r}): candidate_label "
                f"{self.candidate_label!r} is not one of "
                f"{sorted(_CANDIDATE_LABELS)}."
            )


def _case(
    query_id: str,
    draft_text: str,
    store: dict[str, RetrievedSource],
    intent: str,
    candidate_label: str,
    rationale: str,
    low_confidence: bool = False,
) -> CandidateCase:
    """Construct a CandidateCase (thin constructor; pure)."""
    return CandidateCase(
        case=CorpusCase(
            query_id=query_id,
            draft_text=draft_text,
            store=store,
            intent=intent,
        ),
        candidate_label=candidate_label,
        rationale=rationale,
        low_confidence=low_confidence,
    )


def build_candidate_cases() -> list[CandidateCase]:
    """Return the widened Phase-α1 candidate corpus. Pure function."""
    c: list[CandidateCase] = []

    # ---------------------------------------------------------------- GROUNDED
    # --- Verbatim (T1) factual/attribution ---
    c.append(_case(
        "q01",
        "The aluminum chassis reduces overall unit weight by twelve percent compared to steel [S1].",
        {"S1": _source(
            "S1",
            "The aluminum chassis reduces overall unit weight by twelve percent "
            "compared to steel used in the legacy design.",
            "chassis materials comparison",
        )},
        "FACTUAL verbatim >=8-token span -> GROUNDED via T1",
        "grounded",
        "Claim is a contiguous verbatim span of the cited source; fully supported.",
    ))
    c.append(_case(
        "q02",
        "The X200 drone uses a carbon-fiber frame rated for extended field operation [S2].",
        {"S2": _source(
            "S2",
            "The X200 drone uses a carbon-fiber frame rated for extended field "
            "operation in harsh environments.",
            "X200 drone frame specification",
        )},
        "FACTUAL verbatim -> GROUNDED via T1",
        "grounded",
        "Verbatim span present in the cited source; no over-reach.",
    ))
    c.append(_case(
        "q03",
        "According to the engineering team, the new battery pack lasts through extended field tests without failure [S3].",
        {"S3": _source(
            "S3",
            "According to the engineering team, the new battery pack lasts through "
            "extended field tests without failure under a range of temperatures.",
            "battery pack field test report",
        )},
        "ATTRIBUTION verbatim -> GROUNDED via T1",
        "grounded",
        "Attribution matches the source verbatim including the attributed team.",
    ))
    c.append(_case(
        "q04",
        "Quorum DB maintains strong consistency across all replicated partitions by default [S4].",
        {"S4": _source(
            "S4",
            "Quorum DB maintains strong consistency across all replicated "
            "partitions by default, even under network partition.",
            "Quorum DB consistency model",
        )},
        "FACTUAL verbatim -> GROUNDED via T1",
        "grounded",
        "Verbatim span present; claim does not exceed the source.",
    ))

    # --- Numeric match (value+unit) ---
    c.append(_case(
        "q05",
        "Meridian Robotics shipped 4,200 units in the third quarter [S5].",
        {"S5": _source(
            "S5",
            "In the third quarter, Meridian Robotics shipped 4,200 units to "
            "distributors across North America and Europe.",
            "Meridian Robotics Q3 shipment report",
        )},
        "NUMERIC match -> GROUNDED",
        "grounded",
        "Number 4,200 and surrounding claim both present in the source.",
    ))
    c.append(_case(
        "q06",
        "Revenue grew 12% year over year across the segment [S6].",
        {"S6": _source(
            "S6",
            "Company filings show that revenue grew 12% year over year across the "
            "segment during the reporting period.",
            "segment revenue filing",
        )},
        "NUMERIC match -> GROUNDED",
        "grounded",
        "12% and the growth statement match the source value and unit.",
    ))
    c.append(_case(
        "q07",
        "Quorum DB sustains 100,000 writes per second on commodity hardware [S7].",
        {"S7": _source(
            "S7",
            "Quorum DB sustains 100,000 writes per second on commodity hardware in "
            "independent benchmark tests.",
            "Quorum DB benchmark results",
        )},
        "NUMERIC match -> GROUNDED via T1",
        "grounded",
        "Throughput figure and phrasing appear verbatim in the source.",
    ))
    c.append(_case(
        "q08",
        "The NovaChip process reached a 78% yield in pilot production [S8].",
        {"S8": _source(
            "S8",
            "Pilot production of the NovaChip process reached a 78% yield in the "
            "most recent quarter.",
            "NovaChip pilot yield report",
        )},
        "NUMERIC match -> GROUNDED",
        "grounded",
        "78% yield in pilot production is stated in the source.",
    ))
    c.append(_case(
        "q31",
        "The acquisition closed at $4M in total consideration [S31].",
        {"S31": _source(
            "S31",
            "The acquisition closed at $4,000,000 in total consideration according "
            "to the disclosed filings.",
            "acquisition filing summary",
        )},
        "NUMERIC unit-normalized match ($4M == $4,000,000) -> GROUNDED",
        "grounded",
        "$4M normalizes to $4,000,000, which the source states; supported.",
    ))
    c.append(_case(
        "q33",
        "The fleet logged 1.2 million flight hours last year [S33].",
        {"S33": _source(
            "S33",
            "The fleet logged 1.2 million flight hours last year across all "
            "operating regions.",
            "fleet operations annual summary",
        )},
        "NUMERIC match (1.2 million) -> GROUNDED",
        "grounded",
        "1.2 million flight hours matches the source value.",
    ))
    c.append(_case(
        "q38",
        "Adverse events occurred in 3% of the treatment arm [S38].",
        {"S38": _source(
            "S38",
            "Adverse events occurred in 3% of the treatment arm during the study "
            "period.",
            "Zentara phase II safety table",
        )},
        "NUMERIC match (3%) -> GROUNDED",
        "grounded",
        "3% adverse-event rate for the treatment arm is stated in the source.",
    ))
    c.append(_case(
        "q52",
        "The trial enrolled 1,050 participants across twelve sites [S52].",
        {"S52": _source(
            "S52",
            "The trial enrolled 1,050 participants across twelve sites in three "
            "countries.",
            "trial enrollment summary",
        )},
        "NUMERIC match (1,050) -> GROUNDED",
        "grounded",
        "Enrollment count and site count match the source.",
    ))

    # --- Faithful paraphrase clearly above lex_tau (T2) ---
    c.append(_case(
        "q09",
        "The upgraded rotor motor delivers longer flight time than the previous model [S9].",
        {"S9": _source(
            "S9",
            "The upgraded rotor motor delivers a longer flight time than the "
            "previous model in repeated bench testing.",
            "rotor motor bench testing",
        )},
        "Faithful paraphrase, high overlap -> GROUNDED via T2",
        "grounded",
        "Paraphrase preserves meaning; source states the same comparison.",
    ))
    c.append(_case(
        "q10",
        "Larkspur reduced the average onboarding time for new accounts substantially [S10].",
        {"S10": _source(
            "S10",
            "The new onboarding flow at Larkspur reduced the average onboarding "
            "time for new accounts substantially this quarter.",
            "Larkspur onboarding analysis",
        )},
        "Faithful paraphrase, high overlap -> GROUNDED via T2",
        "grounded",
        "Claim is a faithful restatement of the cited source.",
    ))
    c.append(_case(
        "q35",
        "Quorum DB replicates every write to a majority of nodes before acknowledging it [S35].",
        {"S35": _source(
            "S35",
            "Before acknowledging a write, Quorum DB replicates it to a majority of "
            "nodes in the cluster.",
            "Quorum DB write path",
        )},
        "Faithful paraphrase (reordered) -> GROUNDED via T2",
        "grounded",
        "Reordered paraphrase; every asserted fact is in the source.",
    ))
    c.append(_case(
        "q51",
        "The onboarding redesign shipped to all enterprise customers this quarter [S51].",
        {"S51": _source(
            "S51",
            "The onboarding redesign shipped to all enterprise customers this "
            "quarter after a staged rollout.",
            "release notes onboarding redesign",
        )},
        "FACTUAL verbatim -> GROUNDED via T1",
        "grounded",
        "Verbatim span present in the source.",
    ))
    c.append(_case(
        "q11",
        "According to the safety team, the X200 passed all mandated crash tests [S11].",
        {"S11": _source(
            "S11",
            "According to the safety team, the X200 passed all mandated crash tests "
            "conducted this year.",
            "X200 crash test attestation",
        )},
        "ATTRIBUTION verbatim -> GROUNDED via T1",
        "grounded",
        "Attributed claim matches the source verbatim.",
    ))
    c.append(_case(
        "q32",
        "Solar panels reduce carbon emissions across the regional grid over time [S32].",
        {"S32": _source(
            "S32",
            "Solar panels reduce carbon emissions across the regional grid over "
            "time as deployment scales.",
            "regional grid emissions study",
        )},
        "FACTUAL verbatim -> GROUNDED via T1",
        "grounded",
        "Verbatim span present; supported.",
    ))
    c.append(_case(
        "q34",
        "According to the finance team, quarterly bookings exceeded internal targets [S34].",
        {"S34": _source(
            "S34",
            "According to the finance team, quarterly bookings exceeded internal "
            "targets by a wide margin.",
            "finance team bookings note",
        )},
        "ATTRIBUTION verbatim -> GROUNDED via T1",
        "grounded",
        "Attribution and claim both present verbatim.",
    ))

    # --- Relational genuinely grounded (two distinct sources, link stated) ---
    c.append(_case(
        "q12",
        "Insulin resistance causes type 2 diabetes [S121][S122].",
        {
            "S121": _source(
                "S121",
                "Insulin resistance impairs glucose uptake and is a central "
                "mechanism that causes type 2 diabetes to develop.",
                "insulin resistance mechanism review",
            ),
            "S122": _source(
                "S122",
                "Type 2 diabetes develops when insulin resistance progresses and "
                "the pancreas can no longer compensate.",
                "type 2 diabetes pathophysiology",
            ),
        },
        "RELATIONAL, two distinct sources each stating the causal link -> GROUNDED",
        "grounded",
        "Both sources independently assert the causal mechanism, not just co-occurrence.",
    ))
    c.append(_case(
        "q36",
        "Elevated cortisol leads to impaired sleep [S361][S362].",
        {
            "S361": _source(
                "S361",
                "Elevated cortisol leads to impaired sleep by delaying sleep "
                "onset and fragmenting the night.",
                "cortisol and sleep review",
            ),
            "S362": _source(
                "S362",
                "Impaired sleep is commonly observed together with elevated "
                "cortisol in stress studies.",
                "stress sleep cohort study",
            ),
        },
        "RELATIONAL, two distinct sources supporting the link -> GROUNDED",
        "grounded",
        "Link is asserted in the sources; two distinct verbatim sources present.",
    ))

    # --- Absence supported (>=2 distinct queries mention the subject) ---
    c.append(_case(
        "q13",
        "We found no evidence of a safety recall affecting the X200 drone.",
        {
            "SA1": _source(
                "SA1",
                "No recall evidence was found in the manufacturer's safety bulletin "
                "archive for the X200 drone line.",
                "recall evidence search X200 drone",
            ),
            "SA2": _source(
                "SA2",
                "The public recall database returned zero results for X200 drone "
                "safety evidence.",
                "regulatory database evidence query X200",
            ),
        },
        "ABSENCE, 2 distinct queries mention subject 'evidence' -> ABSENCE_SUPPORTED",
        "grounded",
        "Two distinct targeted searches substantiate the absence.",
    ))
    c.append(_case(
        "q14",
        "There is no recall of the Zentara inhaler in any regulated market.",
        {
            "SB1": _source(
                "SB1",
                "A search of the recall notices for the Zentara inhaler returned no "
                "active recall in any market.",
                "Zentara inhaler recall search",
            ),
            "SB2": _source(
                "SB2",
                "The regulator's recall database lists no recall for the Zentara "
                "inhaler product family.",
                "FDA recall database Zentara recall",
            ),
        },
        "ABSENCE, 2 distinct queries mention subject 'recall' -> ABSENCE_SUPPORTED",
        "grounded",
        "Two distinct recall searches back the negative claim.",
    ))
    c.append(_case(
        "q37",
        "There is no antidote approved for the toxin in current guidelines.",
        {
            "SC1": _source(
                "SC1",
                "Current guidelines list no antidote for the toxin; supportive care "
                "is the only recommendation.",
                "toxin antidote guideline search",
            ),
            "SC2": _source(
                "SC2",
                "A literature review found no approved antidote for the toxin to "
                "date.",
                "antidote literature review toxin",
            ),
        },
        "ABSENCE, 2 distinct queries mention subject 'antidote' -> ABSENCE_SUPPORTED",
        "grounded",
        "Absence of an antidote is backed by two distinct targeted searches.",
    ))

    # --------------------------------------------------------------- VIOLATION
    # --- Numeric mismatch (value) ---
    c.append(_case(
        "q15",
        "Meridian Robotics shipped 9,800 units in the third quarter [S15].",
        {"S15": _source(
            "S15",
            "In the third quarter, Meridian Robotics shipped 4,200 units to "
            "distributors across North America and Europe.",
            "Meridian Robotics Q3 shipment report",
        )},
        "NUMERIC mismatch (9,800 vs 4,200) -> UNVERIFIED_NUMBER",
        "violation",
        "Claimed 9,800 units contradicts the source's 4,200.",
    ))
    c.append(_case(
        "q41",
        "The compound showed a 62% response rate in phase II [S41].",
        {"S41": _source(
            "S41",
            "The compound showed a 48% response rate in phase II of the study.",
            "compound phase II efficacy",
        )},
        "NUMERIC mismatch (62% vs 48%) -> UNVERIFIED_NUMBER",
        "violation",
        "Claimed 62% response rate does not match the source's 48%.",
    ))

    # --- Numeric drift, HARD (unit / magnitude / decimal) ---
    c.append(_case(
        "q16",
        "The segment margin was 25% in the fourth quarter [S16].",
        {"S16": _source(
            "S16",
            "Company filings list the segment margin as 25 for the fourth quarter.",
            "segment margin filing",
        )},
        "NUMERIC unit drift (25% vs bare 25) -> UNVERIFIED_NUMBER",
        "violation",
        "Source says 25 (no percent unit); claiming 25% is unsupported unit drift.",
        low_confidence=True,
    ))
    c.append(_case(
        "q17",
        "Quorum DB sustains 100,000 writes per second on commodity hardware [S17].",
        {"S17": _source(
            "S17",
            "Quorum DB sustains 10,000 writes per second on commodity hardware in "
            "benchmark tests.",
            "Quorum DB benchmark results",
        )},
        "NUMERIC magnitude drift (100,000 vs 10,000) -> UNVERIFIED_NUMBER",
        "violation",
        "Claimed 100,000 is an order of magnitude above the source's 10,000.",
        low_confidence=True,
    ))
    c.append(_case(
        "q50",
        "The chip runs at 3.5 GHz base clock [S50].",
        {"S50": _source(
            "S50",
            "The chip runs at 3.2 GHz base clock in standard operating mode.",
            "NovaChip clock specification",
        )},
        "NUMERIC decimal drift (3.5 vs 3.2) -> UNVERIFIED_NUMBER",
        "violation",
        "Claimed 3.5 GHz differs from the source's 3.2 GHz.",
        low_confidence=True,
    ))

    # --- Fabricated citation (cited id absent from store) ---
    c.append(_case(
        "q18",
        "Meridian Robotics achieved carbon-neutral manufacturing across all facilities [S18].",
        {},
        "Fabricated citation (S18 absent) -> UNVERIFIED_CITATION",
        "violation",
        "Cited source S18 was never retrieved this session; citation is fabricated.",
    ))
    c.append(_case(
        "q40",
        "The grid absorbed record solar output in July [S40].",
        {},
        "Fabricated citation (S40 absent) -> UNVERIFIED_CITATION",
        "violation",
        "Cited S40 is not in the store; nothing to check against.",
    ))
    c.append(_case(
        "q19",
        "The Zentara trial reported a 62% response rate [S19].",
        {},
        "Plausible fabricated citation on a specific number -> UNVERIFIED_CITATION",
        "violation",
        "Even a plausible-sounding number is a violation when its citation was never retrieved.",
        low_confidence=True,
    ))

    # --- Uncited factual/numeric ---
    c.append(_case(
        "q20",
        "The drone's carbon-fiber frame is lighter than earlier aluminum designs.",
        {},
        "No citation on a factual claim -> UNCITED",
        "violation",
        "Factual comparison carries no citation to any retrieved source.",
    ))
    c.append(_case(
        "q39",
        "The device sold 250,000 units in its first month.",
        {},
        "No citation on a numeric claim -> UNCITED",
        "violation",
        "Specific sales figure with no citation is unverifiable.",
    ))

    # --- Cited real source but unsupported (UNGROUNDED over-reach) ---
    c.append(_case(
        "q21",
        "The X200 drone dominates the entire commercial mapping market [S21].",
        {"S21": _source(
            "S21",
            "The X200 drone includes an upgraded GPS module for improved "
            "positioning accuracy.",
            "X200 GPS module note",
        )},
        "Cited verbatim source, claim over-reaches -> UNGROUNDED",
        "violation",
        "Source describes a GPS module; it says nothing about market dominance.",
        low_confidence=True,
    ))
    c.append(_case(
        "q42",
        "Larkspur is the market leader in workflow automation [S42].",
        {"S42": _source(
            "S42",
            "Larkspur released a new workflow automation feature this quarter.",
            "Larkspur product release",
        )},
        "Cited verbatim source, claim over-reaches -> UNGROUNDED",
        "violation",
        "A single feature release does not support a market-leadership claim.",
        low_confidence=True,
    ))

    # --- Unverified absence (0 distinct queries mention subject) ---
    c.append(_case(
        "q22",
        "There is no mention of battery defects in the X200 manual.",
        {
            "SD1": _source(
                "SD1",
                "The X200 drone specification sheet lists battery capacity and "
                "flight time.",
                "X200 drone product specifications",
            ),
            "SD2": _source(
                "SD2",
                "Retail pricing for the X200 drone starts at a fixed list price.",
                "X200 drone pricing information",
            ),
        },
        "ABSENCE, 0 queries mention subject 'mention' -> UNVERIFIED_ABSENCE",
        "violation",
        "No search targeted battery defects; the absence is unsubstantiated.",
    ))
    c.append(_case(
        "q45",
        "There is no competing product with comparable range.",
        {
            "SE1": _source(
                "SE1",
                "The internal roadmap lists upcoming range improvements for the "
                "product.",
                "internal roadmap review",
            ),
            "SE2": _source(
                "SE2",
                "The pricing page lists the current subscription tiers.",
                "pricing page capture",
            ),
        },
        "ABSENCE, 0 queries mention subject 'competing' -> UNVERIFIED_ABSENCE",
        "violation",
        "No competitive search was run; 'no competitor' is absence of evidence.",
    ))

    # --- Unverified relation (single verbatim source) ---
    c.append(_case(
        "q23",
        "Faster onboarding leads to higher retention [S23].",
        {"S23": _source(
            "S23",
            "The new onboarding flow reduced time-to-first-value for new accounts.",
            "onboarding flow analysis",
        )},
        "RELATIONAL, single citation -> UNVERIFIED_RELATION",
        "violation",
        "A relation needs a distinct source per side; only one is cited.",
    ))
    c.append(_case(
        "q43",
        "Higher throughput results in lower per-query cost [S43].",
        {"S43": _source(
            "S43",
            "The new engine roughly doubled sustained query throughput.",
            "query engine benchmark",
        )},
        "RELATIONAL, single citation -> UNVERIFIED_RELATION",
        "violation",
        "Only the throughput side is cited; the cost side has no distinct source.",
    ))

    # --- Ungroundable (summary-only source) ---
    c.append(_case(
        "q24",
        "The compound showed strong efficacy in phase II trials [S24].",
        {"S24": _summary_source(
            "S24",
            "The compound showed strong efficacy in phase II trials with a "
            "favorable safety profile.",
            "compound phase II summary",
        )},
        "Cited source is haiku_summary (non-verbatim) -> UNGROUNDABLE",
        "violation",
        "Only a model summary was captured; there is no verbatim text to ground against.",
    ))
    c.append(_case(
        "q44",
        "The vendor confirmed full GDPR compliance [S44].",
        {"S44": _summary_source(
            "S44",
            "The vendor confirmed full GDPR compliance in the due-diligence "
            "questionnaire.",
            "vendor due diligence summary",
        )},
        "Cited source is haiku_summary (non-verbatim) -> UNGROUNDABLE",
        "violation",
        "Compliance claim rests on a summary, not verbatim source text.",
    ))

    # ------------------------------------------------- HARD DIVERGENCE (flagged)
    # --- Relational over-association: gate GROUNDED, truth violation ---
    c.append(_case(
        "q25",
        "Increased marketing spend drives higher customer signups [S251][S252].",
        {
            "S251": _source(
                "S251",
                "Marketing spend increased twenty percent quarter over quarter "
                "according to the finance team.",
                "marketing spend analysis",
            ),
            "S252": _source(
                "S252",
                "Customer signups rose sharply in the weeks following the campaign "
                "launch.",
                "signup funnel analysis",
            ),
        },
        "RELATIONAL over-association: two sides in distinct sources, causal link unstated -> gate GROUNDED, truth violation",
        "violation",
        "Each source states one fact; neither asserts that spend CAUSES signups (over-association).",
        low_confidence=True,
    ))
    c.append(_case(
        "q26",
        "Higher API latency causes increased customer churn [S261][S262].",
        {
            "S261": _source(
                "S261",
                "Median API latency rose noticeably after the last infrastructure "
                "change.",
                "latency monitoring dashboard",
            ),
            "S262": _source(
                "S262",
                "Customer churn increased in the same quarter across several "
                "segments.",
                "churn cohort report",
            ),
        },
        "RELATIONAL over-association -> gate GROUNDED, truth violation",
        "violation",
        "Latency up and churn up are two independent facts; causation is not stated.",
        low_confidence=True,
    ))
    c.append(_case(
        "q48",
        "Remote work leads to lower operating costs [S481][S482].",
        {
            "S481": _source(
                "S481",
                "The company expanded remote work eligibility to most roles last "
                "year.",
                "remote work policy update",
            ),
            "S482": _source(
                "S482",
                "Operating costs declined compared with the prior fiscal year.",
                "operating cost review",
            ),
        },
        "RELATIONAL over-association -> gate GROUNDED, truth violation",
        "violation",
        "Neither source ties the cost decline to remote work; the link is inferred.",
        low_confidence=True,
    ))

    # --- Negation-inverted lexical match: gate GROUNDED via T2, truth violation ---
    c.append(_case(
        "q28",
        "The battery pack failed repeatedly during extended field tests [S28].",
        {"S28": _source(
            "S28",
            "The battery pack lasted through extended field tests without failure.",
            "battery pack field test report",
        )},
        "Lexical overlap high but meaning INVERTED (failed vs without failure) -> gate may GROUND, truth violation",
        "violation",
        "Shares words with the source but asserts the opposite outcome; not supported.",
        low_confidence=True,
    ))

    # --- Single-word subject swap under high overlap: gate GROUNDED, truth violation ---
    c.append(_case(
        "q46",
        "Revenue grew 12% year over year in the mapping division [S46].",
        {"S46": _source(
            "S46",
            "Revenue grew 12% year over year in the logistics division.",
            "divisional revenue filing",
        )},
        "High overlap + matching number, but WRONG division (mapping vs logistics) -> gate GROUNDED, truth violation",
        "violation",
        "Number matches but the division is wrong; the source is about logistics, not mapping.",
        low_confidence=True,
    ))

    # --- Faithful paraphrase BELOW lex_tau: gate UNGROUNDED, truth grounded ---
    c.append(_case(
        "q27",
        "The rotor upgrade extends how long the drone can stay airborne [S27].",
        {"S27": _source(
            "S27",
            "Engineers reported the new motor lets this drone remain in flight "
            "considerably longer than before.",
            "rotor field report",
        )},
        "Faithful paraphrase, LOW lexical overlap -> gate UNGROUNDED, truth grounded",
        "grounded",
        "Meaning is fully supported; wording diverges enough that lexical F1 may fall below lex_tau.",
        low_confidence=True,
    ))
    c.append(_case(
        "q47",
        "The new motor keeps the drone flying longer between charges [S47].",
        {"S47": _source(
            "S47",
            "Field reports indicate the redesigned motor extends the drone's "
            "airborne duration per charge.",
            "motor field report",
        )},
        "Faithful paraphrase, LOW lexical overlap -> gate UNGROUNDED, truth grounded",
        "grounded",
        "Same claim in different words; supported despite low lexical overlap.",
        low_confidence=True,
    ))

    # --- Absence head-noun edge cases (mechanism weakness in both directions) ---
    c.append(_case(
        "q30",
        "We found no evidence of fraud in the audited accounts.",
        {
            "S301": _source(
                "S301",
                "No evidence of a data-loss incident was found in the backup logs.",
                "evidence data loss backup review",
            ),
            "S302": _source(
                "S302",
                "No evidence of a latency regression was found in the traces.",
                "evidence latency regression trace",
            ),
        },
        "ABSENCE: subject 'evidence' matches 2 queries by substring, but searches were UNRELATED to fraud -> gate ABSENCE_SUPPORTED, truth violation",
        "violation",
        "The two searches mention 'evidence' but concern data loss and latency, not fraud; the absence of fraud is not actually substantiated.",
        low_confidence=True,
    ))
    c.append(_case(
        "q49",
        "We found no independent replication reported for the result.",
        {
            "S491": _source(
                "S491",
                "A search for replication attempts of the result returned nothing.",
                "replication study search result",
            ),
            "S492": _source(
                "S492",
                "The literature review found no replication of the result.",
                "replication literature review result",
            ),
        },
        "ABSENCE: head noun 'independent' matches 0 queries -> gate UNVERIFIED_ABSENCE, truth arguably grounded (two replication searches were run)",
        "grounded",
        "Two distinct replication searches substantiate 'no replication'; the gate's head-noun ('independent') misses them.",
        low_confidence=True,
    ))
    c.append(_case(
        "q29",
        "The Zentara trial enrolled 4,200 patients [S29].",
        {"S29": _source(
            "S29",
            "In the third quarter, Meridian Robotics shipped 4,200 units to "
            "distributors.",
            "Meridian Robotics Q3 shipment report",
        )},
        "Numeric coincidence: 4,200 matches but subject unrelated (patients vs units) -> UNGROUNDED, truth violation",
        "violation",
        "The number 4,200 appears in the source but describes shipped units, not enrolled patients.",
        low_confidence=True,
    ))

    return c


def _assert_one_claim_per_case(
    cases: list[CandidateCase], rows_by_query: dict[str, list[ClaimFeatureRow]]
) -> None:
    """Fail loud if any case did not decompose to exactly one claim.

    Single-claim-per-query is the invariant that lets one candidate label
    attach to one claim unambiguously. A draft that splits (conjunction, extra
    sentence) would silently mis-align labels.
    """
    for cc in cases:
        qid = cc.case.query_id
        n = len(rows_by_query.get(qid, []))
        if n != 1:
            raise ValueError(
                f"build_corpus_v2: query {qid!r} decomposed to {n} claims, "
                "expected exactly 1. Every α1 case must be single-claim so its "
                "candidate label maps to one claim; reword the draft."
            )


def write_labeling_v2_csv(
    rows: list[ClaimFeatureRow],
    cases_by_query: dict[str, CandidateCase],
    path: str,
) -> None:
    """Write the CANDIDATE labeling package.

    Columns: claim_id, query_id, claim_text, evidence, human_label,
    candidate_verdict, rationale, label_status.

    human_label AND candidate_verdict both carry the candidate label so a
    ratifier edits human_label in place while candidate_verdict preserves the
    original proposal. label_status is "candidate" on every row — the loader
    refuses the file until Sai flips it to "gold".

    I/O boundary — the file write is the only side effect.
    """
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            "claim_id", "query_id", "claim_text", "evidence",
            "human_label", "candidate_verdict", "rationale", "label_status",
        ])
        for row in rows:
            cc = cases_by_query[row.query_id]
            writer.writerow([
                row.claim_id,
                row.query_id,
                row.claim_text,
                _evidence_text(row, cc.case.store),
                cc.candidate_label,
                cc.candidate_label,
                cc.rationale,
                _LABEL_STATUS,
            ])


def _print_summary(
    cases: list[CandidateCase], rows_by_query: dict[str, list[ClaimFeatureRow]]
) -> None:
    """Print class balance + a per-row table (candidate vs gate verdict).

    Terminal only — never written to the labeler's file. Divergence rows
    (candidate label disagrees with the gate's mechanical verdict) are the
    calibration-interesting rows and are marked with '<<'.
    """
    n = len(cases)
    n_viol = sum(1 for cc in cases if cc.candidate_label == "violation")
    n_low = sum(1 for cc in cases if cc.low_confidence)
    print(f"n={n} claims / {n} queries | "
          f"violation={n_viol} ({100*n_viol/n:.0f}%) grounded={n-n_viol} | "
          f"low-confidence flagged={n_low}")
    print()
    print(f"{'query':<6} {'kind':<11} {'gate_verdict':<21} {'t2_f1':<7} "
          f"{'cand':<10} div")
    _grounded_verdicts = {"GROUNDED", "ABSENCE_SUPPORTED"}
    for cc in cases:
        row = rows_by_query[cc.case.query_id][0]
        gate_grounded = row.predicted_verdict in _grounded_verdicts
        cand_grounded = cc.candidate_label == "grounded"
        div = "<<" if gate_grounded != cand_grounded else ""
        print(f"{row.query_id:<6} {row.kind:<11} {row.predicted_verdict:<21} "
              f"{row.t2_f1:<7.3f} {cc.candidate_label:<10} {div}")


def main() -> None:
    """Build the widened corpus, emit features, and write both artifacts."""
    cases = build_candidate_cases()
    corpus_cases = [cc.case for cc in cases]
    rows = emit_rows_for_cases(corpus_cases)

    rows_by_query: dict[str, list[ClaimFeatureRow]] = {}
    for row in rows:
        rows_by_query.setdefault(row.query_id, []).append(row)

    _assert_one_claim_per_case(cases, rows_by_query)

    cases_by_query = {cc.case.query_id: cc for cc in cases}

    write_feature_rows_jsonl(rows, _FEATURE_ROWS_PATH)
    write_labeling_v2_csv(rows, cases_by_query, _LABELING_CSV_PATH)

    _print_summary(cases, rows_by_query)
    print(f"\n{len(rows)} claims written to {_FEATURE_ROWS_PATH} and "
          f"{_LABELING_CSV_PATH}")


if __name__ == "__main__":
    main()
