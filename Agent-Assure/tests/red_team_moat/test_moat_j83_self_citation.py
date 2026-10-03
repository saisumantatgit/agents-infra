"""J-83 — a draft may not certify ITSELF.

HOW THIS WAS FOUND, because it matters. Not by an adversary: by Sai running the
J-54 plugin smoke test on 2026-10-03. The capture hook's matcher includes
`Read`, so the agent reading the draft captured the draft AS A SOURCE. Adding a
citation to it produced `gate=PASS score=100.0 exit=0 verdict=GROUNDED` — the
gate certifying a claim against its own text.

**`--session-id` does not close it**, and that is the uncomfortable part: the
draft genuinely WAS retrieved this session, so session scoping is satisfied by a
self-citation. An agent reading the draft it is about to verify is ordinary
behaviour, not an attack, which makes this reachable with no adversary at all.

WHY `UNGROUNDABLE`. The verdict taxonomy is closed — a new state needs an ADR —
and `UNGROUNDABLE` already means "cited evidence exists but cannot ground
anything", which is exactly the `haiku_summary` case. A self-source has the same
shape: present in the store, incapable of certifying. So the fix narrows the
cited VERBATIM set in the same breath as the summary rule, rather than inventing
a state or stretching `UNVERIFIED_CITATION`, whose documented meaning is that
the marker is ABSENT from the store.

WHAT THIS DOES NOT CLOSE — pinned by `test_LIMITATION_*` below so it cannot be
quietly assumed. **J-35's general write-then-Read laundering is untouched and
remains Sai's (Escalation #4).**
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_GATE = _ROOT / "scripts" / "ground_check.py"
sys.path.insert(0, str(_ROOT / "scripts"))

import ground_check as g  # noqa: E402

_SENTENCE = ("The install script provisions a runtime virtual environment "
             "with Python 3.11 or newer.")


def _sha(text: str) -> str:
    return hashlib.sha256(unicodedata.normalize("NFKC", text).encode()).hexdigest()


def _record(source_id: str, text: str, file_path: str) -> str:
    return json.dumps({
        "source_id": source_id, "url": None, "file_path": file_path,
        "fetched_at": "2026-10-03T00:00:00Z", "tool": "Read",
        "content_sha256": _sha(text), "text": text,
        "full_text_source": "verbatim", "captured_via": "hook",
        "query_provenance": file_path, "session_id": "S-LIVE",
    })


def _gate(tmp_path: Path, draft_name: str, draft: str, rows: list[str],
          *, session: str | None = None) -> tuple[dict, int]:
    store = tmp_path / "store.jsonl"
    store.write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    draft_path = tmp_path / draft_name
    draft_path.write_text(draft, encoding="utf-8")
    cmd = [sys.executable, str(_GATE), "--draft", str(draft_path),
           "--store", str(store), "--json"]
    if session is not None:
        cmd += ["--session-id", session]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(tmp_path), check=False)
    return json.loads(proc.stdout), proc.returncode


def test_a_draft_cited_by_DIGEST_cannot_certify_itself(tmp_path):
    """The realistic shape: the agent read the draft, then a marker was added.

    The captured text has NO marker, so the digests differ unless citations are
    stripped first. The first version of this check hashed the RAW draft and
    silently failed to fire — missing the real case by one bracketed token.
    """
    report, code = _gate(
        tmp_path, "cited.md", f"{_SENTENCE[:-1]} [S1].\n",
        [_record("S1", _SENTENCE + "\n", "/elsewhere/DRAFT.md")])
    assert report["per_claim"][0]["verdict"] == "UNGROUNDABLE", report
    assert report["gate"] == "FAIL"
    assert code == 1


def test_a_draft_cited_by_PATH_cannot_certify_itself(tmp_path):
    """The other half: the cited source IS the file under verification."""
    draft_path = tmp_path / "self.md"
    report, code = _gate(
        tmp_path, "self.md", f"{_SENTENCE[:-1]} [S1].\n",
        [_record("S1", "entirely different text here", str(draft_path))])
    assert report["per_claim"][0]["verdict"] == "UNGROUNDABLE", report
    assert code == 1


def test_SESSION_SCOPE_does_not_rescue_it(tmp_path):
    """Pins why --session-id was never the answer: the draft really was
    retrieved this session, so scoping is satisfied by the self-citation."""
    report, code = _gate(
        tmp_path, "cited.md", f"{_SENTENCE[:-1]} [S1].\n",
        [_record("S1", _SENTENCE + "\n", "/elsewhere/DRAFT.md")],
        session="S-LIVE")
    assert report["per_claim"][0]["verdict"] == "UNGROUNDABLE", report
    assert code == 1


def test_CONTROL_a_real_source_alongside_the_self_source_still_grounds(tmp_path):
    """POSITIVE CONTROL. Only the self-source is removed from the certifying
    set; a genuine corroborating source must still work, or this fix would be a
    blanket refusal wearing a narrow name."""
    report, code = _gate(
        tmp_path, "cited.md", f"{_SENTENCE[:-1]} [S1][S2].\n",
        [_record("S1", _SENTENCE + "\n", "/elsewhere/DRAFT.md"),
         _record("S2", "Install notes: " + _SENTENCE + " Confirmed on macOS.",
                 "/real/notes.md")])
    assert report["per_claim"][0]["verdict"] == "GROUNDED", report
    assert report["gate"] == "PASS"
    assert code == 0


def test_CONTROL_an_ordinary_draft_and_source_are_untouched(tmp_path):
    """The null case: nothing about an unrelated source may change."""
    report, code = _gate(
        tmp_path, "d.md", "Redis handles 100K ops per second [S1].\n",
        [_record("S1", "Redis handles 100K ops per second in testing.",
                 "/real/redis.md")])
    assert report["gate"] == "PASS", report
    assert code == 0


def test_LIMITATION_write_then_read_to_ANOTHER_file_is_NOT_closed(tmp_path):
    """J-35 IS STILL OPEN AND STILL SAI'S — pinned so it cannot be assumed shut.

    Write fabricated claims to a DIFFERENT file, Read it, cite it: the path
    differs from the draft's and so does the digest, so J-83's identity test
    cannot fire. `capture_core` maps `Read` → `verbatim` unconditionally and no
    field records a file's ORIGIN, so the laundering happens BEFORE the store
    and no gate-side check can see it. Escalation #4.

    If this test ever starts FAILING, J-35 has been closed capture-side and this
    file's limitation note is stale — update both.
    """
    report, code = _gate(
        tmp_path, "draft.md",
        "The 2019 audit found losses of 4.2 billion euro [S1].\n",
        [_record("S1", "The 2019 audit found losses of 4.2 billion euro.",
                 "/tmp/fabricated-notes.md")])
    assert report["gate"] == "PASS", "J-35 may now be closed — re-read this test"
    assert report["per_claim"][0]["verdict"] == "GROUNDED"
    assert code == 0


def test_the_identity_helper_matches_on_either_signal(tmp_path):
    """Unit-level, so a failure localises to the helper rather than the gate."""
    store = {
        "S1": g.RetrievedSource(
            source_id="S1", url=None, file_path="/elsewhere/DRAFT.md",
            fetched_at="x", tool="Read", content_sha256=_sha(_SENTENCE + "\n"),
            text=_SENTENCE + "\n", full_text_source="verbatim",
            captured_via="hook", query_provenance="q"),
        "S2": g.RetrievedSource(
            source_id="S2", url=None, file_path="/real/other.md",
            fetched_at="x", tool="Read", content_sha256=_sha("unrelated"),
            text="unrelated", full_text_source="verbatim",
            captured_via="hook", query_provenance="q"),
    }
    ids = g._self_source_ids("/some/draft.md", f"{_SENTENCE[:-1]} [S1].\n", store)
    assert ids == frozenset({"S1"}), ids
