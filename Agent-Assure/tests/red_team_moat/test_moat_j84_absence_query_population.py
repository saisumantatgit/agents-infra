"""J-84 / J-85: the draft's own `Read` records are not SEARCHES, so they may
form neither the COUNT nor the DENOMINATOR of the absence rule.

WHY A MIXED STORE, AND WHY THAT IS THE WHOLE POINT. The all-self fixtures in
`test_moat_self_citation_across_all_kinds.py` refuse at the BASIS rule — "at
least one verbatim source that is NOT the draft must exist" — and that rule
fires *before* the query arithmetic is ever reached. So those fixtures cannot
see this hole, and a guard written against them stays GREEN against it. That
already happened once, to the cross-kind guard, on 2026-10-03.

The basis rule is therefore a TRIPWIRE, not a grounding requirement: **ONE
wholly irrelevant real source satisfies it** while the draft's own records go on
supplying every query that counts. A rainfall report licenses an absence about a
drone recall.

TWO DEFECTS, ONE POPULATION. `check_absence` derives a single `distinct` list
from `_session_queries(store)` and uses it for three different jobs:

  1. the COUNT  — `match_count >= min_absence_searches`
  2. the DENOMINATOR — `2 * len(head-noun queries) > len(distinct)`
  3. the ACTIVATION of (2) — `len(distinct) >= 3`

  * **J-84** inflates job 1: two self-`Read`s supply both qualifying queries.
  * **J-85** inflates job 2: extra `query_provenance` values dilute the
    blanket-corpus-word denominator and switch a LIVE refusal off. D-54 recorded
    that SHRINKING this list is fail-open; round 18 showed that GROWING it is
    fail-open too, through the same gate.

WHY NO SIGNATURE CHANGE IS NEEDED, against what the register said. The register
claimed both defects need `check_absence` to separate COUNT from DENOMINATOR.
Re-derived from the code (the instrument's §2 rule: never act on a register row
without re-deriving its mechanism), that is true of **J-42** and not of these:
a summary IS a real search, so it must leave the numerator and STAY in the
denominator — that genuinely needs two populations. **A self-`Read` is not a
search at all.** It belongs in neither job, so the fix is to stop putting it in
the one population, at the call site. Smaller, and it cannot create the D-54
direction trap because nothing is being kept in one role and dropped from
another.

PROVEN RED: both tests below fail against the pre-fix gate, where the mixed
store certifies ABSENCE_SUPPORTED at PASS 100.0 / exit 0.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "scripts"))

import ground_check as g  # noqa: E402

# An absence with an entity-free, specific subject, so the entity-free branch
# (head noun + one other content word) is the one under test — that is where
# the denominator gate lives.
_DRAFT = "We found no evidence of a safety recall affecting the drone programme."

# Wholly irrelevant, and deliberately so: it exists only to satisfy the BASIS
# rule. If this document could license the absence, the rule is a tripwire.
_IRRELEVANT = (
    "Monsoon rainfall in the Konkan belt measured 2,410 mm between June and "
    "September, the fourth consecutive year above the decadal mean."
)


def _record(source_id, text, path, query, tool):
    return json.dumps({
        "source_id": source_id,
        "url": None,
        "file_path": str(path) if path else None,
        "fetched_at": "2026-10-03T00:00:00Z",
        "tool": tool,
        "content_sha256": hashlib.sha256(
            unicodedata.normalize("NFKC", text).encode()).hexdigest(),
        "text": text,
        "full_text_source": "verbatim",
        "captured_via": "hook",
        "query_provenance": query,
        "session_id": "S-LIVE",
    })


def _mixed_store(draft_path, extra_queries=()):
    """Two self-Reads supplying the qualifying queries + one irrelevant source."""
    draft = _DRAFT
    lines = [
        # The two records that ARE the draft. Their query_provenance carries the
        # head noun AND a corroborating content word, so they qualify under the
        # entity-free rule — the fixture must refuse on the self-source rule,
        # not incidentally on the query rule.
        _record("S1", draft, draft_path,
                "safety recall drone programme evidence", "Read"),
        _record("S2", draft, draft_path,
                "drone programme recall evidence register", "Read"),
        # The tripwire-satisfier: a real, verbatim, non-self source.
        _record("S3", _IRRELEVANT, None,
                "konkan monsoon rainfall totals", "mcp__exa__web_fetch_exa"),
    ]
    for i, q in enumerate(extra_queries, start=4):
        lines.append(_record(f"S{i}", _IRRELEVANT, None, q, "mcp__exa__web_fetch_exa"))
    return "".join(ln + "\n" for ln in lines)


def _verdict(tmp_path, extra_queries=()):
    draft_path = tmp_path / "draft.md"
    draft_path.write_text(_DRAFT, encoding="utf-8")
    store_path = tmp_path / "store.jsonl"
    store_path.write_text(_mixed_store(draft_path, extra_queries),
                          encoding="utf-8")
    store = g.load_store(str(store_path))
    # `decompose` stamps kind=FACTUAL as a PLACEHOLDER; `classify` is a separate
    # pass (ground_check.py:4473). Omitting it is how the first version of this
    # fixture "failed" — the positive control below caught it, which is the only
    # reason it is not a silent pass-for-the-wrong-reason.
    claims = [g.classify(c) for c in g.decompose(_DRAFT)]
    assert len(claims) == 1, f"fixture drifted: {len(claims)} claims"
    claim = claims[0]
    assert claim.kind is g.ClaimKind.ABSENCE, (
        f"POSITIVE CONTROL FAILED: classified {claim.kind}, not ABSENCE — "
        "this fixture would pass for the wrong reason")
    self_ids = g._self_source_ids(str(draft_path), _DRAFT, store)
    assert self_ids == frozenset({"S1", "S2"}), (
        f"POSITIVE CONTROL FAILED: self-sources detected as {sorted(self_ids)}, "
        "expected S1 and S2 — the identity test, not the absence rule, is broken")
    return g.ground(claim, store, self_source_ids=self_ids)


def test_j84_one_irrelevant_source_cannot_license_a_self_searched_absence(tmp_path):
    """The BASIS rule is satisfied by a rainfall report; the absence must still refuse.

    TWO genuine irrelevant queries, deliberately. With only ONE the store has
    three distinct queries, the blanket-word gate fires on its own arithmetic
    (`len=3, head_in=2, 2*2 > 3`) and this test passes against the UNFIXED
    gate — refusing for the wrong reason, which proves nothing. At four
    distinct queries `4 > 4` is false, the gate falls silent, and the only
    thing that can refuse is the rule under test.
    """
    assert _verdict(tmp_path, extra_queries=(
        "konkan rainfall decadal mean",
    )) is not g.Verdict.ABSENCE_SUPPORTED


def test_the_hole_is_in_the_population_not_in_the_arithmetic():
    """A LIVE differential, so "proven red" is a measurement and not a memory.

    `check_absence` is called twice on identical claim and arithmetic, differing
    only in whether the draft's own `query_provenance` values are in the
    population. Including them CERTIFIES; excluding them REFUSES. The test
    therefore goes red if the call site ever reverts to the whole store, and
    also if someone "fixes" this inside the arithmetic instead — where the D-54
    direction trap lives.

    This replaces the usual pre-fix red run, which would mean disabling a live
    protection to watch it fail. The differential proves the same thing without
    ever putting the gate in that state.
    """
    claim = [g.classify(c) for c in g.decompose(_DRAFT)][0]
    assert claim.kind is g.ClaimKind.ABSENCE

    self_queries = [
        "safety recall drone programme evidence",
        "drone programme recall evidence register",
    ]
    genuine = [
        "konkan monsoon rainfall totals",
        "konkan rainfall decadal mean",
        "monsoon onset dates maharashtra",
        "rainfall gauge calibration konkan",
    ]

    # The pre-fix population: the draft's own reads counted as searches.
    assert g.check_absence(claim, self_queries + genuine) is (
        g.Verdict.ABSENCE_SUPPORTED), (
        "the hole has changed shape — re-derive it before trusting this guard")

    # The post-fix population: genuine searches only.
    assert g.check_absence(claim, genuine) is g.Verdict.UNVERIFIED_ABSENCE

    # And it must refuse at the COUNT, not at the blanket-word gate — a gate
    # that padding can switch off is not what this fix may rest on.
    _, head, _ = g._extract_absence_anchors(g._nfkc(_DRAFT))
    distinct = [g._nfkc(q).casefold().strip() for q in genuine]
    head_bearing = len([q for q in distinct if head in q])
    assert not (len(distinct) >= 3 and 2 * head_bearing > len(distinct)), (
        "the blanket-word gate is firing, so this fixture would refuse even "
        "without the fix")


def test_j85_extra_queries_cannot_switch_the_blanket_word_refusal_off(tmp_path):
    """Growing the query list must not buy an absence that a smaller list refused.

    The head noun is a blanket corpus word here: it appears in a strict majority
    of the genuine session queries, which is the signature the gate exists to
    catch. Padding the store with unrelated `query_provenance` values moves
    `len(distinct)` up until `2 * matching > len(distinct)` goes false and the
    refusal silently disables — fail-open by INFLATION, the mirror of D-54's
    fail-open by shrinkage.
    """
    padded = _verdict(tmp_path, extra_queries=(
        "konkan rainfall decadal mean",
        "monsoon onset dates maharashtra",
        "rainfall gauge calibration konkan",
    ))
    assert padded is not g.Verdict.ABSENCE_SUPPORTED
