"""J-37 — the corpus adversary must be able to SEE a loader change.

The project's standing discipline is "regenerate the calibration corpus after
any tier/classify change and diff it — it is the fix's own adversary." Round 10
found that the adversary was **blind to the loader by construction**:
`build_corpus*.py` builds `RetrievedSource` objects DIRECTLY and never calls
`load_store`, so no amount of regeneration could detect a loader change. Worse,
the fixtures carried `tool="calibration_fixture"`, which `load_store` now
REFUSES — meaning **CR-004's A=0.320 / B=0.000 was measured on stores the
shipped gate would reject.**

This test closes the gap without changing a single corpus row: every store the
corpus builds is serialised and read back through the REAL `load_store`, and
must survive. From now on, a loader rule the fixtures violate fails HERE, loudly,
instead of being silently invisible to the corpus diff.

It also pins the round-trip itself, so a future loader change that quietly
rewrites evidence text (NFKC, whitespace) is caught rather than absorbed.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from calibration.build_corpus_v2 import build_candidate_cases  # noqa: E402
from scripts.ground_check import load_store  # noqa: E402


def _all_corpus_stores():
    for case in build_candidate_cases():
        inner = getattr(case, "case", case)
        store = getattr(inner, "store", None)
        if store:
            yield getattr(inner, "query_id", getattr(inner, "id", "?")), store


def test_the_corpus_builds_at_least_one_store():
    """Guards the guard: if build_cases() ever stops exposing stores, every
    assertion below would vacuously pass and this file would go silent — the
    exact failure mode it exists to prevent."""
    assert list(_all_corpus_stores()), "no corpus stores found to validate"


def test_every_corpus_store_survives_the_real_loader(tmp_path):
    """The point of the file. Each fixture store must LOAD."""
    for qid, store in _all_corpus_stores():
        path = tmp_path / f"{qid}.jsonl"
        path.write_text(
            "".join(json.dumps(asdict(s)) + "\n" for s in store.values()),
            encoding="utf-8")
        try:
            load_store(str(path))
        except Exception as exc:  # noqa: BLE001 - we re-raise with context
            pytest.fail(
                f"corpus store for {qid} does not survive load_store: "
                f"{type(exc).__name__}: {exc}. The calibration corpus is "
                f"measured on stores the shipped gate would reject.")


def test_the_loader_round_trip_preserves_evidence_text(tmp_path):
    """A loader that rewrites text would silently change what the corpus was
    labelled against, which is the `claim_sha` staleness problem arriving by a
    side door."""
    for qid, store in _all_corpus_stores():
        path = tmp_path / f"{qid}.jsonl"
        path.write_text(
            "".join(json.dumps(asdict(s)) + "\n" for s in store.values()),
            encoding="utf-8")
        loaded = load_store(str(path))
        assert set(loaded) == set(store), f"{qid}: source ids changed on load"
        for sid, source in store.items():
            assert loaded[sid].text == source.text, (
                f"{qid}/{sid}: load_store rewrote the evidence text")
            assert loaded[sid].full_text_source == source.full_text_source, (
                f"{qid}/{sid}: load_store changed the source type")
