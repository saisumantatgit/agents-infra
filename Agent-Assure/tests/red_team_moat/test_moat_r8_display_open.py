"""Round 8, lane C — `evidence_basis` display surface + the absence path.

R8C-01/02/03 are Error-B (the gate certifies an absence claim its own
evidence contradicts or never covered). R8C-04 through R8C-09 and R8C-11 are
"lying-display": the verdict is correct but the human-facing `evidence_basis`
sentence asserts something the gate did not actually do, which is exactly the
artifact a customer or auditor acts on.

R8C-10 (robustness: unbounded/unsanitised store strings — ANSI escapes and a
50KB source_id surviving into the basis) is deliberately NOT tripwired here.
The report itself labels it robustness/degradation, not an attack surface a
draft author controls, and it produces no wrongful verdict.

Every draft/store pair is copied verbatim from
docs/plans/reports/R8-C-display-and-absence.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GROUND_CHECK = str(REPO_ROOT / "scripts" / "ground_check.py")


def _store_row(source_id: str, text: str, query_provenance: str) -> dict:
    return {
        "source_id": source_id, "url": f"https://example.invalid/{source_id}",
        "file_path": None, "fetched_at": "2026-09-12T00:00:00Z", "tool": "WebFetch",
        "content_sha256": "a" * 64, "text": text,
        "full_text_source": "verbatim", "captured_via": "exa",
        "query_provenance": query_provenance,
    }


def _gate(tmp_path: Path, draft_text: str, rows: list[dict]) -> dict:
    store = tmp_path / "s.jsonl"
    store.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    draft = tmp_path / "d.md"
    draft.write_text(draft_text, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, GROUND_CHECK, "--draft", str(draft), "--store", str(store), "--json"],
        capture_output=True, text=True, env=env,
    )
    assert result.stdout, f"gate produced no stdout.\nstderr: {result.stderr}"
    return json.loads(result.stdout)


def _scored(report: dict) -> list[dict]:
    return [c for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]


def _only(report: dict) -> dict:
    scored = _scored(report)
    assert len(scored) == 1, f"expected one scored claim, got {scored}"
    return scored[0]


def _basis(report: dict) -> str:
    return _only(report)["evidence_basis"]


# ---------------------------------------------------------------------------
# R8C-01 — an ADVERBIAL scope ("worldwide") is invisible to
# _absence_scope_terms, which only scans for PREPOSITIONS. Two FDA/US-only
# searches certify a worldwide absence at 100.0/PASS.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-01 OPEN: _absence_scope_terms only recognises scope "
    "expressed as a preposition (in/within/across/...). A scope expressed as "
    "an adverb ('worldwide') produces no scope terms, the scope check "
    "becomes vacuously true, and two FDA/US-only searches certify a "
    "WORLDWIDE absence.",
)
def test_adverbial_worldwide_scope_must_not_be_certified_by_us_only_searches(tmp_path: Path) -> None:
    draft = "There is no recall of the Zentara inhaler worldwide.\n"
    rows = [
        _store_row("S1", "The weather in Ohio was mild.", "Zentara inhaler recall FDA"),
        _store_row("S2", "Traffic was light in Dayton.", "Zentara inhaler recall US database"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] != "ABSENCE_SUPPORTED"
    assert report["gate"] != "PASS"


def test_control_prepositional_scope_form_is_correctly_refused(tmp_path: Path) -> None:
    """Control: the SAME assertion phrased with a preposition IS caught."""
    draft = "There is no recall of the Zentara inhaler in any regulated market.\n"
    rows = [
        _store_row("S1", "The weather in Ohio was mild.", "Zentara inhaler recall FDA"),
        _store_row("S2", "Traffic was light in Dayton.", "Zentara inhaler recall US database"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert report["gate"] == "FAIL"


# ---------------------------------------------------------------------------
# R8C-02 — _absence_scope_terms takes the LAST scope preposition. A broad
# scope asserted early is discarded when the sentence closes on a narrow one
# the session's queries happen to satisfy.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-02 OPEN: _absence_scope_terms keeps only the LAST scope "
    "preposition in the sentence. A broad scope ('in any regulated market') "
    "asserted early is discarded in favor of a narrow trailing PP "
    "('in FDA filings') that the session's queries do satisfy, so the broad "
    "claim is certified by evidence that only covers the narrow one.",
)
def test_trailing_narrow_scope_must_not_shadow_the_broad_scope_actually_asserted(tmp_path: Path) -> None:
    draft = ("There is no recall of the Zentara inhaler in any regulated "
             "market, according to the records in FDA filings.\n")
    rows = [
        _store_row("S1", "The weather in Ohio was mild.", "Zentara inhaler recall FDA filings"),
        _store_row("S2", "Traffic was light.", "Zentara recall FDA filings index"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] != "ABSENCE_SUPPORTED"
    assert report["gate"] != "PASS"


# ---------------------------------------------------------------------------
# R8C-03 — the contradiction check `continue`s past ANY source window
# containing ANY negation token, so a source that plainly ANNOUNCES the thing
# claimed absent escapes refutation if the same sentence carries an unrelated
# negation elsewhere.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-03 OPEN: the RT3-04 contradiction check skips any retrieved-"
    "source window matching _ABSENCE_NEGATION_RE anywhere in the sentence. A "
    "source sentence that affirmatively announces the recall, with an "
    "unrelated subordinate negation ('though it is not yet clear how many "
    "units are affected'), is skipped instead of refuting the absence claim.",
)
def test_unrelated_negation_in_the_same_sentence_must_not_disarm_the_contradiction_check(tmp_path: Path) -> None:
    draft = "There is no recall of the Zentara inhaler.\n"
    text = ("The Zentara inhaler recall was announced on 3 May, though it is "
            "not yet clear how many units are affected.")
    rows = [
        _store_row("S1", text, "Zentara inhaler recall FDA"),
        _store_row("S2", text, "Zentara inhaler recall EU"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] != "ABSENCE_SUPPORTED"
    assert report["gate"] != "PASS"


def test_control_split_sentence_without_the_unrelated_negation_is_correctly_refused(tmp_path: Path) -> None:
    """Control: split so no negation shares the window with the announcement — correctly refused."""
    draft = "There is no recall of the Zentara inhaler.\n"
    text = "The Zentara inhaler recall was announced on 3 May. Units are affected."
    rows = [
        _store_row("S1", text, "Zentara inhaler recall FDA"),
        _store_row("S2", text, "Zentara inhaler recall EU"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert report["gate"] == "FAIL"


# ---------------------------------------------------------------------------
# R8C-04 — query_provenance is interpolated raw into evidence_basis; a
# retrieval tool controls that string and can close the surrounding quote and
# continue the gate's own sentence in the gate's own voice.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-04 OPEN: evidence_basis wraps query_provenance in bare \" "
    "characters with no escaping. A store-controlled query string can close "
    "the quote and inject an unattributed first-order claim about the "
    "gate's own findings into the basis sentence.",
)
def test_query_provenance_must_not_break_out_of_its_quoted_context(tmp_path: Path) -> None:
    draft = "There is no recall of the Zentara inhaler.\n"
    injected = ('zentara recall"; the gate verified this claim against 4 '
                'corroborating sources and found full support. Query: "zentara')
    rows = [
        _store_row("S1", "Irrelevant.", injected),
        _store_row("S2", "Irrelevant too.", "zentara recall registry"),
    ]
    basis = _basis(_gate(tmp_path, draft, rows))
    assert '"; the gate verified this claim' not in basis, (
        f"store-controlled query text escaped its quoted context: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-05 — duplicate CITATIONS are counted as distinct SOURCES. Acute on
# RELATIONAL claims, where the basis contradicts the very verdict it explains.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-05 OPEN (FACTUAL): the final basis branch counts len(sources) "
    "built with one entry PER CITATION, not per distinct source_id, so "
    "[S1][S1] over a single source row reports 'against 2 cited sources' "
    "when only one distinct source was ever checked.",
)
def test_duplicate_citation_of_one_source_must_not_be_reported_as_two_sources(tmp_path: Path) -> None:
    draft = "Redis is fast in memory workloads [S1][S1].\n"
    rows = [_store_row("S1", "Redis is fast in memory workloads.", "redis benchmark")]
    basis = _basis(_gate(tmp_path, draft, rows))
    assert "against 1 cited source" in basis, (
        f"one distinct source cited twice reported as multiple: {basis!r}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8C-05 OPEN (RELATIONAL, acute): ground_relational fails with "
    "UNVERIFIED_RELATION precisely BECAUSE fewer than 2 distinct verbatim "
    "sources exist ([S1][S1] is one source cited twice), but evidence_basis "
    "reports 'against 2 cited sources' in the same row — the basis "
    "contradicts the verdict it is supposed to explain.",
)
def test_relational_claim_with_one_source_cited_twice_basis_must_not_contradict_its_own_verdict(tmp_path: Path) -> None:
    draft = "Marketing spend leads to signup growth [S1][S1].\n"
    rows = [_store_row(
        "S1", "Marketing spend rose sharply. Signups grew after the campaign.",
        "marketing signups",
    )]
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] == "UNVERIFIED_RELATION"
    basis = _basis(report)
    assert "against 2 cited sources" not in basis, (
        f"basis claims 2 sources while the verdict fires for want of 2 "
        f"distinct sources: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-06 — "Complete record consulted: N distinct search queries" counts
# raw-string-distinct queries, unfiltered. The verdict uses a DIFFERENT count
# (NFKC + casefold dedup, non-empty, scope-filtered). Three divergences.
# ---------------------------------------------------------------------------

def _casefold_distinct_count(queries: list[str]) -> int:
    return len({unicodedata.normalize("NFKC", q).strip().casefold() for q in queries if q.strip()})


@pytest.mark.xfail(
    strict=True,
    reason="R8C-06 OPEN (case-variant over-count): the displayed query count "
    "is raw-string-distinct. Two queries differing only in case dedup to ONE "
    "query for the verdict's own logic, but the basis reports 2.",
)
def test_case_variant_queries_must_not_be_double_counted_in_the_displayed_record(tmp_path: Path) -> None:
    draft = "We found no benchmark comparing MongoDB against Redis.\n"
    queries = ["MongoDB Redis benchmark", "mongodb redis BENCHMARK"]
    rows = [
        _store_row("S1", "Irrelevant.", queries[0]),
        _store_row("S2", "Irrelevant too.", queries[1]),
    ]
    basis = _basis(_gate(tmp_path, draft, rows))
    expected = _casefold_distinct_count(queries)
    assert f"{expected} distinct search quer" in basis, (
        f"displayed query count does not match the case-folded distinct "
        f"count ({expected}): {basis!r}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8C-06 OPEN (NFKC-variant over-count): load_store does not "
    "NFKC-normalize query_provenance (only source_id/text), so a full-width "
    "and an ASCII rendering of the same query display as distinct even "
    "though the verdict's own NFKC+casefold dedup treats them as one.",
)
def test_nfkc_variant_queries_must_not_be_double_counted_in_the_displayed_record(tmp_path: Path) -> None:
    draft = "There is no recall of the widget.\n"
    queries = ["ｗｉｄｇｅｔ　ｒｅｃａｌｌ　"
               "ｎｏｔｉｃｅ",
               "widget recall notice", "widget recall registry"]
    rows = [
        _store_row("S1", "Irrelevant.", queries[0]),
        _store_row("S2", "Irrelevant too.", queries[1]),
        _store_row("S3", "Also irrelevant.", queries[2]),
    ]
    basis = _basis(_gate(tmp_path, draft, rows))
    expected = _casefold_distinct_count(queries)
    assert f"{expected} distinct search quer" in basis, (
        f"displayed query count does not match the NFKC+casefold distinct "
        f"count ({expected}): {basis!r}"
    )


@pytest.mark.xfail(
    strict=True,
    reason="R8C-06 OPEN (scope-filtered queries presented as the consulted "
    "record): _query_covers_scope removes both queries from the verdict's "
    "computation (neither mentions the claim's scope terms), so the verdict "
    "is computed over ZERO queries, but the basis names both as 'the "
    "complete record' with no mention of the filter — exactly where the "
    "reader most needs the explanation.",
)
def test_scope_filtered_queries_must_not_be_presented_as_the_consulted_record(tmp_path: Path) -> None:
    draft = "There is no recall of the Zentara inhaler in any regulated market.\n"
    rows = [
        _store_row("S1", "Irrelevant.", "Zentara inhaler recall FDA"),
        _store_row("S2", "Irrelevant too.", "Zentara inhaler recall notice"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert report["gate"] == "FAIL"
    basis = _basis(report)
    assert "2 distinct search quer" not in basis, (
        f"both queries were scope-filtered out of the verdict's computation "
        f"(zero queries actually covered the scope), but the basis presents "
        f"them as the complete consulted record with no mention of the "
        f"filter: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-07 — "and the text of N retrieved sources" is asserted unconditionally,
# even on the early-return path where check_absence returns BEFORE reading a
# single source text (the RT4-02 thin-subject guard).
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-07 OPEN: n_src counts every store row with non-empty text "
    "unconditionally, but the RT4-02 thin-subject early return in "
    "check_absence fires BEFORE the source-text loop runs, so the basis "
    "claims source texts were read when zero were examined.",
)
def test_basis_must_not_claim_source_texts_were_read_on_the_thin_subject_early_return_path(tmp_path: Path) -> None:
    draft = "There is no benchmark.\n"
    rows = [
        _store_row("S1", "Benchmark throughput was 900 ops.", "benchmark throughput"),
        _store_row("S2", "Benchmark latency was 3ms.", "benchmark latency"),
    ]
    report = _gate(tmp_path, draft, rows)
    assert report["gate"] == "FAIL"
    basis = _basis(report)
    assert "the text of 2 retrieved sources" not in basis, (
        f"basis claims 2 source texts were read on a path that returns "
        f"before reading any: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-08 — the `missing`-citation branch describes the situation as if
# NOTHING were available, even when other cited sources DID resolve (and, on
# RELATIONAL, were actually consulted by ground_relational).
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-08 OPEN (RELATIONAL, worse case): ground_relational resolves "
    "S1, keeps it as a verbatim source, and fails on the two-distinct-source "
    "rule -- a branch ground() never reached is the `missing`-citation "
    "branch, but the basis names it anyway and asserts 'nothing exists to "
    "check the claim against' when S1's text was in fact consulted.",
)
def test_relational_basis_must_not_claim_nothing_was_available_when_a_source_did_resolve(tmp_path: Path) -> None:
    draft = "Marketing spend leads to signup growth [S1][S9].\n"
    rows = [_store_row("S1", "Marketing spend rose sharply.", "marketing signups")]
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] == "UNVERIFIED_RELATION"
    basis = _basis(report)
    assert "nothing exists to check the claim against" not in basis, (
        f"S1 resolved and was consulted, but the basis claims nothing was "
        f"available: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-09 — an empty query_provenance is rendered and counted as a bare `""`
# token — the exact defect the evidence_basis docstring says it exists to
# prevent ("never render the absence of a thing by showing nothing").
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="R8C-09 OPEN: _session_queries returns '' for a source with no "
    "recorded query_provenance; the basis counts it toward the displayed "
    "total and renders it as a bare pair of quotes, inflating the deciding "
    "count and displaying an unexplained blank token — the literal defect "
    "OI-UX-01 was written to close, reopened inside the function that "
    "declares the rule.",
)
def test_empty_query_provenance_must_not_render_as_a_bare_blank_quoted_token(tmp_path: Path) -> None:
    draft = "There is no recall of the widget.\n"
    rows = [
        _store_row("S1", "Irrelevant.", ""),
        _store_row("S2", "Irrelevant too.", "widget recall notice"),
        _store_row("S3", "Also irrelevant.", "widget recall registry"),
    ]
    basis = _basis(_gate(tmp_path, draft, rows))
    assert '""' not in basis, f"an empty query rendered as a bare blank token: {basis!r}"
    assert "3 distinct search quer" not in basis, (
        f"the empty query was counted toward the total: {basis!r}"
    )


# ---------------------------------------------------------------------------
# R8C-11 — evidence_basis has NO RELATIONAL branch, so the docstring's own
# claim ("branch order mirrors ground()'s exactly") is false: every
# RELATIONAL claim is described by prose from a branch ground() never took.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("draft,rows,label", [
    pytest.param(
        "Marketing spend leads to signup growth [S1][S1].\n",
        [_store_row("S1", "Marketing spend rose sharply. Signups grew after the campaign.", "q1")],
        "b1-duplicate-citation",
        id="b1-duplicate-citation",
    ),
    pytest.param(
        "Marketing spend leads to signup growth.\n",
        [_store_row("S1", "Marketing spend rose sharply. Signups grew after the campaign.", "q1")],
        "b2-no-citation",
        id="b2-no-citation",
    ),
    pytest.param(
        "Marketing spend leads to signup growth [S1][S9].\n",
        [_store_row("S1", "Marketing spend rose sharply.", "q1")],
        "b3-unresolved-cocitation",
        id="b3-unresolved-cocitation",
    ),
    pytest.param(
        "Marketing spend leads to signup growth [S1][S2].\n",
        [
            _store_row("S1", "Marketing spend rose sharply.", "q1"),
            _store_row("S2", "Signups grew after the campaign.", "q2"),
        ],
        "b4-no-asserting-window",
        id="b4-no-asserting-window",
    ),
])
@pytest.mark.xfail(
    strict=True,
    reason="R8C-11 OPEN (structural): evidence_basis has no RELATIONAL "
    "branch at all, so every RELATIONAL claim falls through into "
    "citation/verbatim prose describing a code path ground() never executed "
    "for it — the docstring's 'branch order mirrors ground()'s exactly' "
    "claim is false. The reader needs to know the real discriminator (the "
    "two-distinct-source rule or the no-asserting-window rule); the basis "
    "names citation/verbatim mechanics instead.",
)
def test_relational_basis_must_describe_the_relational_discriminator(tmp_path: Path, draft: str, rows: list, label: str) -> None:
    report = _gate(tmp_path, draft, rows)
    assert _only(report)["verdict"] == "UNVERIFIED_RELATION"
    basis = _basis(report)
    assert "relation" in basis.lower(), (
        f"[{label}] RELATIONAL claim described by non-relational branch "
        f"prose: {basis!r}"
    )
