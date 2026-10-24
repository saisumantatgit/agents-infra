"""R1 — the deployed rates must be re-derivable by one command, and that
command must not write.

Two properties, and the second is the one with teeth.

1. **The number reproduces.** ``measure_rates`` recomputes Error-A and Error-B
   from the LIVE gate — not read back from ``feature_rows-v2.jsonl`` — and gets
   the deployed pair. If a change to ``ground()`` moves a gold row, this test
   goes red with the new counts, which is the point: the number that describes
   the product is pinned to the code that produces it.

2. **"Read-only" is ENFORCED, not asserted in a docstring.** This is the
   R15-01 / ADR-008 class — a docstring promising a property the code lacks —
   and it is a live hazard here, because the one pre-existing calibration
   runner (``calibration.run_calibration``) silently REWRITES ``CR-001`` as a
   side effect of measuring. So the read-only test carries a POSITIVE CONTROL:
   the same harness is pointed at that known writer and must DETECT it. A
   no-write assertion whose detector cannot see a real write certifies nothing.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

_AGENT_ASSURE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_AGENT_ASSURE))

from calibration.measure_rates import measure  # noqa: E402

CALIBRATION = _AGENT_ASSURE / "calibration"


def _fingerprint() -> dict[str, str]:
    """Content hash of every tracked artifact in calibration/.

    Content, not mtime: a writer that rewrites identical bytes is not a
    corruption risk, and an mtime-based detector would fail the suite on a
    harmless touch while a real rewrite of DIFFERENT bytes is what matters.
    """
    out: dict[str, str] = {}
    for path in sorted(CALIBRATION.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            out[str(path.relative_to(CALIBRATION))] = hashlib.sha256(
                path.read_bytes()).hexdigest()
    return out


def test_the_deployed_rates_reproduce_from_the_live_gate():
    # R27-01 (2026-10-25): Error-A 11/25 -> 12/25. q03 ("...without failure",
    # source "...without failure UNDER A RANGE OF TEMPERATURES") is now refused
    # by the negated-claim limiter guard that closes B1's regression. q03 is a
    # Sai-ratified grounded row: this price is shown to him in the PR, his call.
    rates, labeled = measure()
    assert rates.n == 52, "the gold corpus is n=52"
    # J-97 branch: one gold row (q13, the only certified gold-grounded absence) is now refused — the measured price of the demotion.
    assert (rates.fp, rates.tn) == (12, 13), "Error-A's cells"
    assert (rates.fn, rates.tp) == (0, 27), "Error-B's cells"
    assert rates.error_a == pytest.approx(0.480)
    assert rates.error_b == pytest.approx(0.000)
    # Denominators are asserted separately from the ratio: a rate can be
    # reproduced by a corpus that has SHRUNK, and a smaller Error-B
    # denominator is a weaker claim wearing the same number.
    assert rates.fp + rates.tn == 25
    assert rates.fn + rates.tp == 27
    assert len(labeled) == 52


def test_measuring_the_rates_writes_nothing():
    before = _fingerprint()
    measure()
    after = _fingerprint()
    changed = {k for k in before.keys() | after.keys()
               if before.get(k) != after.get(k)}
    assert not changed, f"measure() wrote to calibration/: {sorted(changed)}"


def test_POSITIVE_CONTROL_the_same_detector_catches_the_known_writer():
    """Without this, the test above is satisfiable by a blind detector.

    ``calibration.run_calibration`` is the n=12 bootstrap sweep and it writes
    ``CR-001``. It is run in a subprocess and its output is restored
    afterwards, so this control cannot leave the tree dirty even when it fails.
    """
    cr1 = CALIBRATION / "CR-001-bootstrap-lex-tau.md"
    original = cr1.read_bytes()
    mutated = original + b"\n<!-- positive control: detector must see this -->\n"
    try:
        cr1.write_bytes(mutated)
        before = _fingerprint()
        subprocess.run(
            [sys.executable, "-m", "calibration.run_calibration"],
            cwd=_AGENT_ASSURE, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        after = _fingerprint()
        changed = {k for k in before.keys() | after.keys()
                   if before.get(k) != after.get(k)}
        assert "CR-001-bootstrap-lex-tau.md" in changed, (
            "the detector did NOT see a write it was pointed straight at, so "
            "test_measuring_the_rates_writes_nothing proves nothing")
    finally:
        cr1.write_bytes(original)
