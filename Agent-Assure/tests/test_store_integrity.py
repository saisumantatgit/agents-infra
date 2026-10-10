"""J-26 — `load_store` must REFUSE a self-contradicting store (R9P2-01..04).

The store is audit evidence. Every silent repair below decides a verdict by
something that is not evidence: line order, JSON key order, or a single
self-declared string that nothing cross-checks.

Written BEFORE the fix and run against pre-fix code to see each one FAIL.

The project convention is "fail loud, never fallback": a malformed record
raises with the offending line or key. These tests assert the raise, and the
controls assert that a WELL-FORMED store still loads — a loader that refuses
everything would pass every test above and ship nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import ground_check as g  # noqa: E402

VALID_TOOL = "Read"


def _rec(sid="S1", text="Redis handles 100K ops per second.",
         fts="verbatim", tool=VALID_TOOL, **over):
    rec = {"source_id": sid, "url": None, "file_path": "/tmp/a",
           "fetched_at": "2026-09-13T00:00:00Z", "tool": tool,
           "content_sha256": "a" * 64, "text": text,
           "full_text_source": fts, "captured_via": "inline",
           "query_provenance": "q-" + sid}
    rec.update(over)
    return rec


def _write(tmp_path, *lines):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(
        (line if isinstance(line, str) else json.dumps(line)) + "\n"
        for line in lines), encoding="utf-8")
    return str(p)


# --- R9P2-01: duplicate source_id, last-record-wins ------------------------

def test_duplicate_source_id_raises(tmp_path):
    """Two records, one id. Today the LATER silently wins, so whether a claim
    citing [S1] is UNGROUNDABLE or GROUNDED depends only on line order."""
    path = _write(tmp_path,
                  _rec(fts="haiku_summary", tool="WebFetch"),
                  _rec(fts="verbatim"))
    with pytest.raises(Exception) as exc:
        g.load_store(path)
    assert "S1" in str(exc.value)


def test_duplicate_source_id_raises_in_the_other_order_too(tmp_path):
    """SIBLING: order must not decide whether we refuse. Reversed."""
    path = _write(tmp_path,
                  _rec(fts="verbatim"),
                  _rec(fts="haiku_summary", tool="WebFetch"))
    with pytest.raises(Exception):
        g.load_store(path)


def test_duplicate_source_id_raises_even_when_records_are_identical(tmp_path):
    """SIBLING: the null case. Two byte-identical records still make the store
    self-contradicting about how many times the session retrieved the source,
    and a loader that permits this permits the laundering case by accident."""
    path = _write(tmp_path, _rec(), _rec())
    with pytest.raises(Exception):
        g.load_store(path)


# --- R9P2-02: NFKC id collision -------------------------------------------

def test_nfkc_id_collision_raises(tmp_path):
    """Full-width 'S1' folds onto 'S1'. Two DISTINCT raw ids become one key."""
    path = _write(tmp_path,
                  _rec(sid="Ｓ１", text="Something unrelated entirely.",
                       fts="haiku_summary", tool="WebFetch"),
                  _rec(sid="S1"))
    with pytest.raises(Exception):
        g.load_store(path)


# --- R9P2-03: duplicate JSON key inside ONE record ------------------------

def test_duplicate_json_key_in_one_record_raises(tmp_path):
    """json.loads keeps the LAST of duplicated keys, so one line can declare
    haiku_summary and then verbatim and load as verbatim."""
    line = ('{"source_id":"S1","url":null,"file_path":"/tmp/a",'
            '"fetched_at":"2026-09-13T00:00:00Z","tool":"WebFetch",'
            '"content_sha256":"' + "a" * 64 + '",'
            '"text":"Redis handles 100K ops per second.",'
            '"full_text_source":"haiku_summary","captured_via":"inline",'
            '"query_provenance":"q1","full_text_source":"verbatim"}')
    path = _write(tmp_path, line)
    with pytest.raises(Exception) as exc:
        g.load_store(path)
    assert "full_text_source" in str(exc.value)


def test_duplicate_json_key_raises_for_any_key_not_just_source_type(tmp_path):
    """SIBLING: the rule is about duplicated keys, not about one field."""
    line = ('{"source_id":"S1","source_id":"S2","url":null,'
            '"file_path":"/tmp/a","fetched_at":"2026-09-13T00:00:00Z",'
            '"tool":"Read","content_sha256":"' + "a" * 64 + '",'
            '"text":"Redis handles 100K ops per second.",'
            '"full_text_source":"verbatim","captured_via":"inline",'
            '"query_provenance":"q1"}')
    path = _write(tmp_path, line)
    with pytest.raises(Exception):
        g.load_store(path)


# --- R9P2-04: no internal-consistency or type checking --------------------

def test_webfetch_declaring_verbatim_raises(tmp_path):
    """capture_core's HARD SPEC: native WebFetch is ALWAYS haiku_summary.
    A record claiming otherwise contradicts the capture contract."""
    path = _write(tmp_path, _rec(tool="WebFetch", fts="verbatim"))
    with pytest.raises(Exception) as exc:
        g.load_store(path)
    assert "WebFetch" in str(exc.value) or "verbatim" in str(exc.value)


def test_verbatim_tool_declaring_haiku_summary_raises(tmp_path):
    """SIBLING — the OTHER direction. Mislabelling a verbatim tool as a summary
    is Error-A not Error-B, but the store is still lying about itself and the
    convention is fail-loud in both directions."""
    path = _write(tmp_path, _rec(tool="Read", fts="haiku_summary"))
    with pytest.raises(Exception):
        g.load_store(path)


def test_unknown_full_text_source_raises(tmp_path):
    """The enum is closed: verbatim | haiku_summary."""
    path = _write(tmp_path, _rec(fts="probably_fine"))
    with pytest.raises(Exception):
        g.load_store(path)


def test_unrecognised_tool_raises(tmp_path):
    """An unknown tool makes the source type UNVERIFIABLE, and in this gate
    every 'I don't know' must point AWAY from PASS. Silently trusting the
    record's own 'verbatim' is the one thing that must not happen."""
    path = _write(tmp_path, _rec(tool="SomeNewReaderNobodyToldTheGateAbout"))
    with pytest.raises(Exception):
        g.load_store(path)


@pytest.mark.parametrize("field,bad", [
    ("source_id", 7),
    ("text", None),
    ("fetched_at", None),
    ("tool", None),
    ("content_sha256", None),
    ("full_text_source", None),
    ("captured_via", 12),
    ("query_provenance", ["x"]),
    ("url", 7),
    ("file_path", ["x"]),
])
def test_mistyped_field_raises(tmp_path, field, bad):
    """Type confusion must not load. url/file_path are OPTIONAL (may be null)
    but must be strings when present."""
    path = _write(tmp_path, _rec(**{field: bad}))
    with pytest.raises(Exception):
        g.load_store(path)


def test_missing_required_field_raises(tmp_path):
    """SIBLING of the mistyped case: absent, not wrong-typed."""
    rec = _rec()
    del rec["full_text_source"]
    path = _write(tmp_path, rec)
    with pytest.raises(Exception):
        g.load_store(path)


# --- CONTROLS: a loader that refuses everything is not a fix --------------

def test_well_formed_store_still_loads(tmp_path):
    path = _write(tmp_path, _rec(sid="S1"), _rec(sid="S2", text="Other text."))
    store = g.load_store(path)
    assert set(store) == {"S1", "S2"}
    assert store["S1"].full_text_source == "verbatim"


def test_legitimate_haiku_summary_record_still_loads(tmp_path):
    path = _write(tmp_path, _rec(tool="WebFetch", fts="haiku_summary"))
    store = g.load_store(path)
    assert store["S1"].full_text_source == "haiku_summary"


def test_null_url_and_file_path_still_load(tmp_path):
    """Both are genuinely optional — Read has no url, fetches have no path."""
    path = _write(tmp_path, _rec(url=None, file_path=None))
    assert g.load_store(path)["S1"].url is None


def test_blank_lines_are_still_skipped(tmp_path):
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps(_rec()) + "\n\n\n", encoding="utf-8")
    assert set(g.load_store(str(p))) == {"S1"}


def test_every_verbatim_tool_is_accepted(tmp_path):
    """Parity guard: the allowlist must not silently omit a shipped tool."""
    import capture_core  # noqa: PLC0415
    for i, tool in enumerate(sorted(capture_core._VERBATIM_TOOLS)):
        path = _write(tmp_path, _rec(sid=f"S{i}", tool=tool, fts="verbatim"))
        assert g.load_store(path)[f"S{i}"].full_text_source == "verbatim"


def test_tool_source_type_mapping_matches_capture_core(tmp_path):
    """The gate keeps its OWN copy of the mapping to avoid importing the
    capture layer into the moat. This test is what makes the copy safe: it
    fails loudly the day capture_core learns a tool the gate does not know."""
    import capture_core  # noqa: PLC0415
    assert g._VERBATIM_TOOLS == capture_core._VERBATIM_TOOLS
    assert g._HAIKU_SUMMARY_TOOLS == capture_core._HAIKU_SUMMARY_TOOLS
