"""Closed-loop integration test: hook output → engine input.

Simulates 2-3 tool events through make_record + append_record into a temp
store, then feeds a draft citing those source_ids (plus one absent [S9])
through the full engine pipeline:

    decompose → classify → score_report (which calls ground internally)

Asserts:
  - The supported claim (cited, verbatim text present, T1-matchable) → GROUNDED
  - The absent-citation claim [S9] → UNVERIFIED_CITATION

If a real contract mismatch between hook output and load_store is found, the
test fails loudly with an explanatory message rather than papering over it.

No LLM, no network, no wall-clock, no random.  All timestamps fixed.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from scripts.capture_core import make_record, append_record
from scripts.ground_check import (
    Verdict,
    ClaimKind,
    decompose,
    classify,
    load_store,
    score_report,
)


# ---------------------------------------------------------------------------
# Fixed deterministic constants
# ---------------------------------------------------------------------------

FIXED_AT = "2026-06-27T10:00:00Z"

# Source text for S1 — must contain a verbatim-matchable span of ≥8 tokens.
# The draft claim below quotes this text verbatim so T1 fires.
# NOTE: no " and " in _S1_TEXT so the conjunction-split rule does not fracture
# the claim sentence, which would leave only the post-"and" tail carrying [S1].
_S1_TEXT = (
    "Redis handles 100K operations per second on commodity hardware "
    "with sub-millisecond latency."
)

# Source text for S2 — second verbatim source (different topic).
_S2_TEXT = (
    "PostgreSQL supports ACID transactions, full-text search, "
    "and JSON document storage in a single unified engine."
)

# Source text for S3 — a Read-tool file source (also verbatim).
_S3_TEXT = (
    "The deployment pipeline runs on Kubernetes and uses Helm charts "
    "for versioned release management across all production clusters."
)

# Draft text:
#   - Claim A: quotes _S1_TEXT verbatim and cites [S1] → should be GROUNDED.
#   - Claim B: makes a factual claim citing [S9] which does NOT exist → UNVERIFIED_CITATION.
#
# Design constraints on _DRAFT to guarantee reliable decompose behaviour:
#   1. No " and " or "; " within either sentence — avoids conjunction-split
#      fracturing the claim so only a short tail carries the citation.
#   2. Each sentence ends with a period so syntok segments them cleanly.
#   3. Claim A must quote ≥8 content tokens from _S1_TEXT verbatim so T1 fires.
#   4. Claim A is NUMERIC (contains 100K) — numeric_ok must also pass, which
#      it will since 100K appears in _S1_TEXT.
_DRAFT = (
    "Redis handles 100K operations per second on commodity hardware "
    "with sub-millisecond latency [S1]. "
    "The system also achieves remarkable distributed consensus throughput [S9]."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_store(store_path: str) -> None:
    """Simulate 3 tool events through make_record + append_record."""
    # Event 1: exa web fetch → S1 (verbatim)
    r1 = make_record(
        tool_name="mcp__exa__web_fetch_exa",
        tool_input={"url": "https://redis.io/performance"},
        tool_response={"text": _S1_TEXT},
        source_id="S1",
        query_provenance="redis throughput benchmark",
        fetched_at=FIXED_AT,
    )
    assert r1 is not None, "make_record must return a RetrievedSource for exa fetch"
    append_record(r1, store_path)

    # Event 2: DDG fetch → S2 (verbatim)
    r2 = make_record(
        tool_name="mcp__ddg-search__fetch_content",
        tool_input={"url": "https://postgresql.org/docs/features"},
        tool_response={"text": _S2_TEXT},
        source_id="S2",
        query_provenance="postgresql feature set",
        fetched_at=FIXED_AT,
    )
    assert r2 is not None, "make_record must return a RetrievedSource for DDG fetch"
    append_record(r2, store_path)

    # Event 3: Read tool → S3 (verbatim, file source)
    r3 = make_record(
        tool_name="Read",
        tool_input={"file_path": "/project/docs/deployment.md"},
        tool_response=_S3_TEXT,
        source_id="S3",
        query_provenance="deployment pipeline docs",
        fetched_at=FIXED_AT,
    )
    assert r3 is not None, "make_record must return a RetrievedSource for Read tool"
    append_record(r3, store_path)


# ---------------------------------------------------------------------------
# Contract-mismatch checks (run before engine assertions)
# ---------------------------------------------------------------------------

def _assert_no_contract_mismatch(store_path: str) -> dict:
    """Load the store and assert the round-trip contract holds.

    Contract: every record written by append_record must be readable by
    load_store and must produce a RetrievedSource with the exact same
    field values.  Any deviation is a real contract mismatch — do NOT
    paper over it; raise with a descriptive message.

    Returns the loaded store dict for downstream use.
    """
    store = load_store(store_path)

    # --- Structural: all three source_ids must be present ---
    for expected_key in ("S1", "S2", "S3"):
        assert expected_key in store, (
            f"CONTRACT MISMATCH: source_id '{expected_key}' written by append_record "
            f"is not present in the dict returned by load_store.  "
            f"Keys found: {list(store.keys())!r}.  "
            f"Check that append_record serializes 'source_id' and that load_store "
            f"indexes by the NFKC-normalized source_id string."
        )

    # --- Content: text round-trips without corruption ---
    assert store["S1"].text == _S1_TEXT, (
        f"CONTRACT MISMATCH: S1 text did not round-trip cleanly.  "
        f"Expected: {_S1_TEXT!r}  Got: {store['S1'].text!r}"
    )
    assert store["S2"].text == _S2_TEXT, (
        f"CONTRACT MISMATCH: S2 text did not round-trip cleanly."
    )
    assert store["S3"].text == _S3_TEXT, (
        f"CONTRACT MISMATCH: S3 text did not round-trip cleanly.  "
        f"Note: Read tool applies strip_cat_n_prefix — if _S3_TEXT contains "
        f"cat-n prefixes the stored text will differ.  _S3_TEXT must be plain prose."
    )

    # --- full_text_source: all three must be 'verbatim' ---
    for key in ("S1", "S2", "S3"):
        assert store[key].full_text_source == "verbatim", (
            f"CONTRACT MISMATCH: source {key!r} has full_text_source="
            f"{store[key].full_text_source!r}; expected 'verbatim'.  "
            f"Only verbatim sources participate in T1/T2 grounding."
        )

    # --- S9 must NOT be in the store (it was never appended) ---
    assert "S9" not in store, (
        f"CONTRACT MISMATCH: source_id 'S9' found in store but was never written.  "
        f"Check for off-by-one or stale state in load_store."
    )

    return store


# ---------------------------------------------------------------------------
# Integration test class
# ---------------------------------------------------------------------------

class TestCaptureIntegration:
    """Closed-loop: hook capture → JSONL store → engine pipeline."""

    def test_grounded_claim_is_grounded_and_absent_citation_is_unverified(
        self, tmp_path
    ):
        """Core integration assertion: the two-verdict proof.

        Steps:
          1. Write S1, S2, S3 via make_record + append_record.
          2. Assert no contract mismatch in the round-trip.
          3. Run decompose → classify on _DRAFT.
          4. Run score_report.
          5. Assert claim citing [S1] (verbatim match present) → GROUNDED.
          6. Assert claim citing [S9] (no such source) → UNVERIFIED_CITATION.
        """
        store_path = str(tmp_path / "evidence.jsonl")

        # Step 1: populate store via hook pipeline
        _build_store(store_path)

        # Step 2: contract mismatch check — fail loud before touching the engine
        store = _assert_no_contract_mismatch(store_path)

        # Step 3 + 4: full engine pipeline
        claims = [classify(c) for c in decompose(_DRAFT)]
        report = score_report(claims, store)

        # Sanity: we must have scored at least 2 claims
        assert report["scored_claims"] >= 2, (
            f"Expected ≥2 scored claims from the draft; got {report['scored_claims']}.  "
            f"per_claim: {report['per_claim']}"
        )

        # Build a lookup from stripped claim text → verdict for assertion clarity.
        verdict_by_text: dict[str, str] = {
            entry["text"]: entry["verdict"]
            for entry in report["per_claim"]
        }

        # Step 5: find the claim that cites [S1] and assert GROUNDED
        s1_claim_entry = next(
            (e for e in report["per_claim"] if "[S1]" in e["text"]),
            None,
        )
        assert s1_claim_entry is not None, (
            "Could not find a claim containing '[S1]' in per_claim.  "
            f"per_claim texts: {[e['text'] for e in report['per_claim']]!r}"
        )
        assert s1_claim_entry["verdict"] == Verdict.GROUNDED.value, (
            f"Expected claim citing [S1] to be GROUNDED; got "
            f"{s1_claim_entry['verdict']!r}.  "
            f"Claim text: {s1_claim_entry['text']!r}.  "
            f"Store S1 full_text_source: {store.get('S1') and store['S1'].full_text_source!r}.  "
            f"Store S1 text (first 120 chars): {store.get('S1') and store['S1'].text[:120]!r}"
        )

        # Step 6: find the claim that cites [S9] and assert UNVERIFIED_CITATION
        s9_claim_entry = next(
            (e for e in report["per_claim"] if "[S9]" in e["text"]),
            None,
        )
        assert s9_claim_entry is not None, (
            "Could not find a claim containing '[S9]' in per_claim.  "
            f"per_claim texts: {[e['text'] for e in report['per_claim']]!r}"
        )
        assert s9_claim_entry["verdict"] == Verdict.UNVERIFIED_CITATION.value, (
            f"Expected claim citing [S9] to be UNVERIFIED_CITATION; got "
            f"{s9_claim_entry['verdict']!r}.  "
            f"'S9' in store: {'S9' in store}."
        )

    def test_store_file_is_valid_jsonl(self, tmp_path):
        """Every line written by append_record must be valid JSON with all 10 fields."""
        store_path = str(tmp_path / "evidence.jsonl")
        _build_store(store_path)

        required_fields = {
            "source_id", "url", "file_path", "fetched_at", "tool",
            "content_sha256", "text", "full_text_source", "captured_via",
            "query_provenance",
        }

        with open(store_path, encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]

        assert len(lines) == 3, (
            f"Expected 3 JSONL lines for 3 appended records; got {len(lines)}"
        )

        for i, line in enumerate(lines, start=1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                pytest.fail(f"Line {i} is not valid JSON: {exc}\nLine: {line!r}")

            missing = required_fields - set(obj.keys())
            assert not missing, (
                f"CONTRACT MISMATCH: line {i} is missing fields: {missing!r}.  "
                f"append_record must serialize all 10 RetrievedSource fields."
            )

    def test_non_retrieval_tool_not_stored(self, tmp_path):
        """Bash tool events must be silently dropped (make_record returns None)."""
        store_path = str(tmp_path / "evidence.jsonl")
        _build_store(store_path)

        # Simulate a Bash event — make_record must return None
        bash_result = make_record(
            tool_name="Bash",
            tool_input={"command": "ls -la /project"},
            tool_response="total 4\ndrwxr-xr-x 1 user group 64 Jun 27 10:00 .",
            source_id="S_BASH",
            query_provenance="directory listing",
            fetched_at=FIXED_AT,
        )
        assert bash_result is None, (
            "make_record must return None for Bash (non-retrieval) tool; "
            f"got {bash_result!r}"
        )

        # Store must still have exactly 3 lines (Bash event was never appended)
        store = load_store(store_path)
        assert len(store) == 3, (
            f"Store should contain exactly 3 sources; found {len(store)} keys: "
            f"{list(store.keys())!r}"
        )

    def test_gate_is_needs_work_due_to_unverified_citation(self, tmp_path):
        """score_report gate must be NEEDS_WORK (or FAIL) because [S9] is UNVERIFIED_CITATION.

        The UNVERIFIED_CITATION hard override caps the gate at NEEDS_WORK even when
        the grounding score would otherwise be high enough to PASS (spec §4.5).
        """
        store_path = str(tmp_path / "evidence.jsonl")
        _build_store(store_path)
        store = load_store(store_path)

        claims = [classify(c) for c in decompose(_DRAFT)]
        report = score_report(claims, store)

        assert report["gate"] in ("NEEDS_WORK", "FAIL"), (
            f"Expected gate to be NEEDS_WORK or FAIL due to UNVERIFIED_CITATION [S9]; "
            f"got {report['gate']!r}.  "
            f"grounding_score: {report['grounding_score']}"
        )
