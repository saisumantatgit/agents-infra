"""ROUND 14 — four CRITICAL Error-B shapes against the code that ships.

Every test here asserts the CORRECT behaviour and is `xfail(strict=True)`, the
project's convention for a DELIBERATELY-OPEN finding: it records the hole today
and goes RED the day someone closes it, forcing the register to be updated in
the same commit. A rising xfail count is holes being recorded, not decay.

ALL FOUR WERE REPRODUCED BY THE ORCHESTRATOR from the adversary's own fixtures
before being written here — round 13's lesson was that a described fixture is
not a reproduced one. Stores and drafts below are byte-identical to
`reports/RED-TEAM-R14-2026-10-02.md`.

THE ONE MECHANISM BEHIND TWO OF THEM (R14-01, R14-04). T1 anchors its >=8-token
contiguous span at the claim's FIRST content word, so a claim with a long
subject phrase matches a span lying entirely inside its own subject. The
predicate is then checked only by set-membership coverage — "do these words
appear anywhere in this source" — and `_span_is_hedged` inspects only the
`_SPAN_HEDGE_LOOKBACK` (5) tokens BEFORE the span. A denial sitting between the
subject and the predicate is therefore never read, and `no` is in `_STOP_WORDS`
so coverage discards it. Measured: the SAME denial moved before the subject
refuses the claim (FAIL 0.0) and after it certifies (PASS 100.0).

This is not an exotic attack. "We found no evidence that X" is the ordinary way
a real source reports a negative finding, so the shape arises from honest
retrieval, with no adversarial control of the source required.

WHY NO FIX LANDS HERE. Priced on the n=52 gold corpus 2026-10-02: scanning the
whole source for a hedge closes R14-01 and both R14-04 cases, Error-B stays
0.000, and Error-A goes 0.400 -> 0.560 (+4 false alarms / 25 grounded rows).
That alters the Error-A/Error-B trade-off, which is Escalation #1 — Sai's, not
the agent's. The narrower sentence-scoped variant CANNOT be written at this
layer: `_tokenize` strips punctuation, so `_span_is_hedged` receives a token
list with no sentence boundaries and a sentence-scoped repair needs a signature
change across its call sites. Registered J-69..J-71.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"


def _row(source_id: str, text: str, query: str) -> str:
    return json.dumps({
        "source_id": source_id, "url": f"https://e.com/{source_id}",
        "file_path": None, "fetched_at": "1970-01-01T00:00:00Z",
        "tool": "mcp__exa__web_fetch_exa", "content_sha256": source_id,
        "text": text, "full_text_source": "verbatim", "captured_via": "inline",
        "query_provenance": query, "session_id": "",
    })


def _gate(tmp_path: Path, draft: str, rows: list[str]) -> tuple[dict, int]:
    """Run the SHIPPED CLI end to end and return (report, exit code)."""
    store = tmp_path / "store.jsonl"
    store.write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(draft + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(_GATE), "--draft", str(draft_path),
         "--store", str(store), "--json"],
        capture_output=True, text=True, cwd=str(_ROOT), check=False,
    )
    return json.loads(proc.stdout), proc.returncode


_DENIAL_SOURCE = (
    "The 2019 federal review of interbank settlement latency across the "
    "eurozone found no evidence that the migration triggered widespread "
    "customer refunds."
)
_DENIAL_CLAIM = (
    "The 2019 federal review of interbank settlement latency across the "
    "eurozone triggered widespread customer refunds [S1]."
)


@pytest.mark.xfail(strict=True, reason=(
    "R14-01 OPEN, CRITICAL: the D-76 flat relational refusal is gated on "
    "classify, and _RELATIONAL_RE is a ten-member blacklist over an open "
    "class. 'triggered' is not in it, so the claim is kind=NUMERIC, takes the "
    "verbatim path, and T1 certifies it against a source that DENIES it. "
    "The one-word delta 'causes'->'triggered' flips FAIL 0.0/exit 1 to "
    "PASS 100.0/exit 0 on the same store."))
def test_a_causal_claim_its_source_DENIES_is_refused_whatever_verb_it_uses(tmp_path):
    """J-80: asserts the VERDICT, not just the gate.

    A `gate != "PASS"` assertion is satisfiable by ANY unrelated fail-closed
    change — on 2026-10-03 the J-62+J-71 figure check satisfied a J-33 tripwire
    that way and made an open finding read as closed (D-46). This finding is
    "the claim is CERTIFIED", so the closed state is a non-GROUNDED verdict and
    nothing weaker expresses it.
    """
    report, code = _gate(tmp_path, _DENIAL_CLAIM, [_row("S1", _DENIAL_SOURCE, "q")])
    entry = report["per_claim"][0]
    assert entry["verdict"] != "GROUNDED", (
        f"still certified: {entry['verdict']} — if this now refuses for some "
        f"OTHER reason, that is masking, not closure")
    assert report["gate"] != "PASS", report
    assert code != 0


def test_CONTROL_the_same_sentence_with_causes_IS_refused(tmp_path):
    """Not an xfail. Pins the one-word delta that makes R14-01 a routing bug.

    If this ever starts PASSing, the relational refusal itself has broken and
    the finding above has stopped being about the classifier.
    """
    report, code = _gate(
        tmp_path, _DENIAL_CLAIM.replace("triggered", "causes"),
        [_row("S1", _DENIAL_SOURCE, "q")])
    assert report["gate"] == "FAIL"
    assert code == 1
    assert report["per_claim"][0]["verdict"] == "UNVERIFIED_RELATION"


_AUDIT_CLAIM = (
    "The quarterly audit of custodial reconciliation controls at the Frankfurt "
    "desk identified material weaknesses [S1]."
)


@pytest.mark.parametrize("source,label", [
    pytest.param(
        "The quarterly audit of custodial reconciliation controls at the "
        "Frankfurt desk identified no material weaknesses whatsoever.",
        "h1-negated", id="h1-negated"),
    pytest.param(
        "The quarterly audit of custodial reconciliation controls at the "
        "Frankfurt desk identified material weaknesses, contrary to what the "
        "record shows; that finding was withdrawn.",
        "h3-withdrawn", id="h3-withdrawn"),
])
@pytest.mark.xfail(strict=True, reason=(
    "R14-04 OPEN, CRITICAL (J-67): a plain FACTUAL claim with NO causal "
    "vocabulary is certified PASS 100.0 against a source that explicitly "
    "denies or withdraws it. The matched >=8-token span lies inside the "
    "claim's 9-token subject; _span_is_hedged reads only the 5 tokens BEFORE "
    "it, so the denial that follows is invisible. Proof that extending "
    "_RELATIONAL_RE cannot fix R14-01 — this takes the same path with no "
    "causal word in the sentence."))
def test_a_factual_claim_its_source_denies_or_withdraws_is_refused(
        tmp_path, source, label):
    """J-80: asserts the VERDICT, not just the gate — see the note above."""
    report, code = _gate(tmp_path, _AUDIT_CLAIM, [_row("S1", source, "q")])
    entry = report["per_claim"][0]
    assert entry["verdict"] != "GROUNDED", (
        f"[{label}] still certified: {entry['verdict']}")
    assert report["gate"] != "PASS", (label, report)
    assert code != 0


def test_CONTROL_the_same_denial_BEFORE_the_span_is_caught(tmp_path):
    """Not an xfail. Proves the hedge guard WORKS and only its scope is wrong.

    Identical denial, identical claim; only its POSITION in the source moves.
    Without this control, the two xfails above could be read as "the gate has
    no denial check at all", which would point at the wrong repair.
    """
    report, code = _gate(
        tmp_path, _AUDIT_CLAIM,
        [_row("S1", "It is not true that the quarterly audit of custodial "
                    "reconciliation controls at the Frankfurt desk identified "
                    "material weaknesses.", "q")])
    assert report["gate"] == "FAIL"
    assert code == 1


@pytest.mark.xfail(strict=True, reason=(
    "R14-02 OPEN, CRITICAL: _SPELLED_NUMBER_WORDS deliberately EXCLUDES "
    "'one' — a CEILING recorded during J-43 — and that exclusion BREAKS the "
    "word run, so 'one million' is checked only as 'million', which the "
    "source does contain. A fabricated magnitude certifies while the "
    "'ninety million' and '1 million' controls are refused. The recorded "
    "ceiling is the attack."))
def test_a_fabricated_magnitude_spelled_with_one_is_refused(tmp_path):
    """J-80: a fabricated FIGURE must be refused AS a figure problem.

    `UNVERIFIED_NUMBER` is the only verdict that means "the number is not in the
    source". Any other refusal here — UNGROUNDED, UNCITED — would mean the
    spelled-figure guard is still blind and something else caught the draft.
    """
    report, code = _gate(
        tmp_path,
        "The 2019 federal review of interbank settlement latency across the "
        "eurozone documented one million customer refunds [S1].",
        [_row("S1", "The 2019 federal review of interbank settlement latency "
                    "across the eurozone documented nine million customer "
                    "refunds in one quarter.", "eurozone settlement review")])
    entry = report["per_claim"][0]
    assert entry["verdict"] == "UNVERIFIED_NUMBER", (
        f"refused as {entry['verdict']}, not as a figure problem — the spelled "
        f"guard may still be blind and something else caught this")
    assert report["gate"] != "PASS", report
    assert code != 0


def test_CONTROL_ninety_million_on_the_same_store_is_refused(tmp_path):
    """Not an xfail. Pins that the spelled-figure guard itself works."""
    report, code = _gate(
        tmp_path,
        "The 2019 federal review of interbank settlement latency across the "
        "eurozone documented ninety million customer refunds [S1].",
        [_row("S1", "The 2019 federal review of interbank settlement latency "
                    "across the eurozone documented nine million customer "
                    "refunds in one quarter.", "eurozone settlement review")])
    assert report["gate"] == "FAIL"
    assert report["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER"
    assert code == 1


def test_a_fabricated_figure_inside_a_supported_absence_is_refused(tmp_path):
    """CLOSED 2026-10-03 (J-62+J-71, Sai's GO). Was a strict xfail; now passes.

    `ground()` returned from the ABSENCE branch ABOVE the D-77 figure checks,
    so `numeric_ok` was unreachable for an absence claim and the digit 4200 —
    present in no source text — certified ABSENCE_SUPPORTED at PASS 100.0 /
    exit 0. The two checks now run before the absence verdict, verbatim-only,
    strictly fail-closed. Measured: Error-A 0.400 and Error-B 0.000 UNCHANGED.

    It also closed J-62, the same hole for a figure spelled in words — one
    defect, two spellings. And it MASKED a J-33 tripwire on the way through;
    see the de-masking note in test_moat_j33_unrecognised_citation_open.py."""
    report, code = _gate(
        tmp_path,
        "There is no fatality record for the 4200 aviation deaths.",
        [_row("S1", "Quarterly revenue rose on strong fleet orders.",
              "4200 fatality record aviation"),
         _row("S2", "The plant added a second shift in June.",
              "aviation 4200 fatality register")])
    # R16-06: this asserted only `gate != "PASS"` — the J-80 weakness, in the
    # regression test for the very change that caused J-80's masking. It was
    # proven red pre-fix at ABSENCE_SUPPORTED so it was never a tautology; it
    # simply could not tell a figure refusal from any other refusal.
    assert report["per_claim"][0]["verdict"] == "UNVERIFIED_NUMBER", (
        f"refused as {report['per_claim'][0]['verdict']}, not as a figure "
        f"problem — the absence figure check may not be what caught this")
    assert report["gate"] != "PASS", report
    assert code != 0
