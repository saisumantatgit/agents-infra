"""J-38 — "this session" becomes a fact instead of an aspiration.

The founding spec's one sentence is that a claim traces to a source "actually
retrieved THIS SESSION". Round 10 showed there was no such thing as a session in
the code: no record carried a session id, the store was opened append-only and
never rotated, so a draft citing a PRIOR session's [S2] certified at PASS 100.0.
`CLAUDE.md` documented the guarantee anyway.

WHAT THIS DOES NOT DO, and why. My own recommendation said "stamp `fetched_at`
for real". That was WRONG and is withdrawn: the sentinel is deliberate —
PostToolUse events carry no trustworthy fetch time and CLAUDE.md forbids
wall-clock in logic, so a real timestamp would break the capture layer's
determinism. Session scoping needs an IDENTITY, not a clock, and
`event["session_id"]` already exists.

THE DESIGN DECISION THAT MATTERS: enforcement RAISES on a foreign record; it does
NOT filter it out.

Filtering looks obviously safer and is not. Proven on 2026-10-01 (D-54): the
store feeds `check_absence` through two arguments at once, and shrinking it moves
them in OPPOSITE directions —
  * fewer cited sources  -> citations fail to resolve  -> refuse   (fail-closed)
  * fewer source_texts   -> fewer refutations found    -> CERTIFY  (fail-OPEN)
  * fewer distinct queries -> can drop below the 2-query bar -> refuse, but ALSO
    disables the blanket-corpus-word refusal, which CERTIFIES   (fail-OPEN)
So a filtered store is not a weaker store, it is a DIFFERENTLY weak store.
Refusing to produce a verdict at all is the only unambiguously fail-closed
response: a store holding another session's evidence is not this session's audit
record.

Enforcement is OPT-IN (`--session-id`). Without it, behaviour is unchanged, which
is what keeps every existing store and the demo working (close-after-open).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import ground_check as g  # noqa: E402


def _rec(sid="S1", session="sess-A", text="Redis replicates to three replicas."):
    return {"source_id": sid, "url": None, "file_path": "/tmp/a",
            "fetched_at": "1970-01-01T00:00:00Z", "tool": "Read",
            "content_sha256": "a" * 64, "text": text,
            "full_text_source": "verbatim", "captured_via": "inline",
            "query_provenance": "q-" + sid, "session_id": session}


def _write(tmp_path, *records):
    p = tmp_path / "s.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return str(p)


# --- the field exists and round-trips ---------------------------------------

def test_a_record_carries_its_session_id(tmp_path):
    store = g.load_store(_write(tmp_path, _rec(session="sess-A")))
    assert store["S1"].session_id == "sess-A"


def test_a_legacy_record_without_a_session_id_still_loads(tmp_path):
    """CLOSE-AFTER-OPEN: every store written before J-38 must keep loading, or
    the demo and 47 corpus fixtures break on an unrelated change."""
    legacy = _rec()
    del legacy["session_id"]
    store = g.load_store(_write(tmp_path, legacy))
    assert store["S1"].session_id == ""


def test_a_mistyped_session_id_raises(tmp_path):
    with pytest.raises(Exception):
        g.load_store(_write(tmp_path, {**_rec(), "session_id": 7}))


# --- enforcement ------------------------------------------------------------

def test_a_foreign_session_record_raises(tmp_path):
    """THE FINDING. A prior session's source must not be usable as evidence."""
    store = g.load_store(_write(tmp_path, _rec("S1", "sess-A"),
                                _rec("S2", "sess-B")))
    with pytest.raises(Exception) as exc:
        g.assert_single_session(store, "sess-A")
    assert "sess-B" in str(exc.value)


def test_an_unattributable_record_raises_under_enforcement(tmp_path):
    """"I don't know" must point AWAY from PASS: a record with no session id
    cannot be attributed to this session, so it cannot be certified against."""
    legacy = _rec()
    del legacy["session_id"]
    store = g.load_store(_write(tmp_path, legacy))
    with pytest.raises(Exception):
        g.assert_single_session(store, "sess-A")


def test_a_single_session_store_is_accepted(tmp_path):
    """CONTROL. Without this the feature could be 'refuse everything'."""
    store = g.load_store(_write(tmp_path, _rec("S1", "sess-A"),
                                _rec("S2", "sess-A")))
    g.assert_single_session(store, "sess-A")  # must not raise


def test_enforcement_is_opt_in(tmp_path):
    """A mixed store is fine when no session is asserted — that is today's
    behaviour and it is what keeps existing stores working."""
    store = g.load_store(_write(tmp_path, _rec("S1", "sess-A"),
                                _rec("S2", "sess-B")))
    assert set(store) == {"S1", "S2"}


def test_enforcement_does_NOT_filter(tmp_path):
    """The load-bearing design assertion. If someone replaces the raise with a
    filter, this fails — and the docstring above explains why a filtered store
    is fail-OPEN on the absence path, not merely weaker."""
    import inspect
    src = inspect.getsource(g.assert_single_session)
    assert "raise" in src
    for banned in ("del store[", ".pop(", "filter(", "store = {"):
        assert banned not in src, (
            f"assert_single_session appears to FILTER ({banned!r}). Filtering is "
            f"fail-OPEN on the absence path — see D-54.")


# --- END TO END: the field must survive capture -> disk -> load --------------
#
# Written because my first patch touched only the dataclass and the constructor.
# `append_record` serializes via an EXPLICIT FIELD LIST and
# `_record_with_source_id` rebuilds field by field, so the new field would have
# been dropped on the exact path every captured record takes — while the tests
# above, which write JSONL by hand, kept passing. A new field needs the
# dataclass, the constructor, the COPY and the SERIALIZER.

def test_session_id_survives_capture_to_disk_to_load(tmp_path):
    sys.path.insert(0, str(_SCRIPTS))
    import capture_core  # noqa: PLC0415

    record = capture_core.make_record(
        tool_name="Read",
        tool_input={"file_path": "/tmp/notes.md"},
        tool_response="Redis replicates to three replicas.",
        source_id="UNASSIGNED",
        query_provenance="/tmp/notes.md",
        fetched_at="1970-01-01T00:00:00Z",
        session_id="sess-REAL",
    )
    assert record is not None and record.session_id == "sess-REAL"

    store_path = tmp_path / "evidence.jsonl"
    assigned = capture_core.assign_and_append(record, str(store_path))
    assert assigned

    on_disk = json.loads(store_path.read_text(encoding="utf-8").strip())
    assert on_disk["session_id"] == "sess-REAL", (
        "session_id did not reach disk — append_record's explicit field list "
        "must include it")

    loaded = g.load_store(str(store_path))
    assert next(iter(loaded.values())).session_id == "sess-REAL"
    g.assert_single_session(loaded, "sess-REAL")
    with pytest.raises(Exception):
        g.assert_single_session(loaded, "sess-OTHER")


def test_the_hook_reads_the_session_id_off_the_event():
    sys.path.insert(0, str(_SCRIPTS))
    import capture_hook  # noqa: PLC0415

    assert capture_hook._event_session_id({"session_id": "abc"}) == "abc"
    assert capture_hook._event_session_id({}) == ""
    assert capture_hook._event_session_id({"session_id": 7}) == ""
