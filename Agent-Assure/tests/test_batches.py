"""Tests for incremental multi-batch label ingestion (calibration.batches).

Each test names the property it asserts. The fail-loud properties are the
point of the module: a batch layer that silently accepted a partial, a
duplicate, or a non-human label would be worse than no batch layer at all,
because a calibration derived from it looks exactly like a good one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from calibration.batches import (
    BatchManifest,
    corpus_provenance,
    export_batch_scaffold,
    load_batch,
    load_corpus,
    read_manifest,
)
from calibration.init_labels import claim_sha


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

def _write_batch(
    root: Path,
    batch_id: str,
    domain: str,
    claims: list[tuple[str, str, str, str]],  # (claim_id, text, evidence, label)
    labeler: str = "Vardhan (author, practising advocate)",
) -> Path:
    """Write a complete batch (scaffold + labels + features + manifest)."""
    scaffold = root / f"scaffold-{batch_id}.csv"
    labels = root / f"labels-{batch_id}.csv"
    features = root / f"features-{batch_id}.jsonl"

    with scaffold.open("w", encoding="utf-8", newline="") as fh:
        fh.write("claim_id,query_id,claim_text,evidence,candidate_verdict,rationale\n")
        for cid, text, ev, _ in claims:
            fh.write(f'{cid},{cid.split("#")[0]},"{text}","{ev}",grounded,r\n')

    with labels.open("w", encoding="utf-8", newline="") as fh:
        fh.write("claim_id,human_label,label_status,claim_sha,note\n")
        for cid, text, ev, label in claims:
            fh.write(f"{cid},{label},gold,{claim_sha(text, ev)},\n")

    with features.open("w", encoding="utf-8") as fh:
        for cid, text, _, label in claims:
            fh.write(json.dumps({
                "claim_id": cid,
                "query_id": cid.split("#")[0],
                "claim_text": text,
                "kind": "FACTUAL",
                "cited_source_ids": ["S1"],
                "citations_resolved": True,
                "t1_verbatim": False,
                "t2_f1": 0.8 if label == "grounded" else 0.1,
                "numeric_ok": True,
                "predicted_verdict": "GROUNDED" if label == "grounded" else "UNGROUNDED",
                "tier_sensitive": True,
            }) + "\n")

    manifest = root / f"manifest-{batch_id}.json"
    manifest.write_text(json.dumps({
        "batch_id": batch_id,
        "domain": domain,
        "labeler": labeler,
        "labeled_on": "2026-08-30",
        "scaffold": scaffold.name,
        "labels": labels.name,
        "features": features.name,
    }), encoding="utf-8")
    return manifest


_B1 = [
    ("c1#0", "Order 7 Rule 11 permits rejection of a plaint.", "S1: Order 7 Rule 11 provides for rejection of a plaint.", "grounded"),
    ("c2#0", "Section 9 bars suits of a civil nature.", "S1: Section 9 provides courts shall try all suits of a civil nature.", "violation"),
]
_B2 = [
    ("c3#0", "A written statement is filed within thirty days.", "S2: The defendant shall file a written statement within thirty days.", "grounded"),
]


# ---------------------------------------------------------------------------
# Accumulate-then-derive: the load-bearing capability
# ---------------------------------------------------------------------------

def test_partial_delivery_is_a_valid_corpus(tmp_path: Path):
    """THE cpc-book constraint: 5-10 items at a time, weeks apart.

    A single small batch must load cleanly. Under the single-corpus design this
    was structurally impossible — an 8-of-400 delivery read as 392 unlabeled
    claims and load_gold_labels (correctly) refused it.
    """
    m1 = _write_batch(tmp_path, "cpc-ch1-b1", "cpc-legal", _B1)
    corpus = load_corpus([str(m1)], str(tmp_path))
    assert len(corpus) == 2
    assert {c.label for c in corpus} == {"grounded", "violation"}


def test_batches_accumulate_across_deliveries(tmp_path: Path):
    """Two batches weeks apart accumulate into one corpus, order preserved."""
    m1 = _write_batch(tmp_path, "cpc-ch1-b1", "cpc-legal", _B1)
    m2 = _write_batch(tmp_path, "cpc-ch1-b2", "cpc-legal", _B2)
    corpus = load_corpus([str(m1), str(m2)], str(tmp_path))
    assert [c.claim_id for c in corpus] == ["c1#0", "c2#0", "c3#0"]


def test_domain_filter_enables_per_domain_operating_point(tmp_path: Path):
    """Per-domain selection is the mechanism that lets the confound question
    ('does legal paraphrase move the research-prose operating point?') be
    ANSWERED by deriving both and comparing, rather than assumed either way."""
    m1 = _write_batch(tmp_path, "cpc-ch1-b1", "cpc-legal", _B1)
    m2 = _write_batch(tmp_path, "research-b1", "research-prose", _B2)
    assert len(load_corpus([str(m1), str(m2)], str(tmp_path))) == 3
    assert len(load_corpus([str(m1), str(m2)], str(tmp_path), domain="cpc-legal")) == 2
    assert len(load_corpus([str(m1), str(m2)], str(tmp_path), domain="research-prose")) == 1


# ---------------------------------------------------------------------------
# Fail-loud properties (each would silently corrupt a derived threshold)
# ---------------------------------------------------------------------------

def test_incomplete_batch_still_refused(tmp_path: Path):
    """Completeness is scoped to the batch, NOT relaxed: a batch whose own
    scaffold carries an unlabeled claim is still refused."""
    m = _write_batch(tmp_path, "b", "d", _B1)
    scaffold = tmp_path / "scaffold-b.csv"
    scaffold.write_text(
        scaffold.read_text() + 'c9#0,c9,"An extra unlabeled claim.","S1: x",grounded,r\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="no label"):
        load_corpus([str(m)], str(tmp_path))


def test_stale_label_still_refused_within_a_batch(tmp_path: Path):
    """claim_sha binding survives batching: editing the claim text after
    ratification must fail loud, not silently re-point the human's judgment."""
    m = _write_batch(tmp_path, "b", "d", _B1)
    scaffold = tmp_path / "scaffold-b.csv"
    scaffold.write_text(
        scaffold.read_text().replace(
            "Order 7 Rule 11 permits rejection of a plaint.",
            "Order 7 Rule 11 REQUIRES rejection of a plaint.",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="STALE"):
        load_corpus([str(m)], str(tmp_path))


def test_candidate_label_still_refused_within_a_batch(tmp_path: Path):
    """A non-gold row anywhere in a batch refuses the whole batch."""
    m = _write_batch(tmp_path, "b", "d", _B1)
    labels = tmp_path / "labels-b.csv"
    labels.write_text(labels.read_text().replace("gold", "candidate", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="gold labels only"):
        load_corpus([str(m)], str(tmp_path))


def test_cross_batch_duplicate_claim_id_refused(tmp_path: Path):
    """The collision the single-file design never had to consider: one claim
    labeled in two batches would be counted twice — and if the labels disagree,
    the corpus carries two contradictory truths for one claim."""
    m1 = _write_batch(tmp_path, "b1", "d", _B1)
    m2 = _write_batch(tmp_path, "b2", "d", [
        ("c1#0", "Order 7 Rule 11 permits rejection of a plaint.",
         "S1: Order 7 Rule 11 provides for rejection of a plaint.", "violation"),
    ])
    with pytest.raises(ValueError, match="appears in both"):
        load_corpus([str(m1), str(m2)], str(tmp_path))


def test_duplicate_batch_id_refused(tmp_path: Path):
    m1 = _write_batch(tmp_path, "same", "d", _B1)
    m2 = _write_batch(tmp_path, "same", "d", _B2)
    with pytest.raises(ValueError, match="duplicate batch_id"):
        load_corpus([str(m1), str(m2)], str(tmp_path))


def test_non_human_labeler_refused():
    """CLAUDE.md failure-mode 5, made machine-checkable: a Claude-labeled batch
    is candidate data however its CSV is marked, and calibrating on it would
    validate the gate against the judgment the gate itself encodes."""
    with pytest.raises(ValueError, match="not a human ratifier"):
        BatchManifest("b", "d", "Claude", "2026-08-30", "s.csv", "l.csv", "f.jsonl")


@pytest.mark.parametrize("field", ["batch_id", "domain", "labeler", "labeled_on"])
def test_blank_provenance_refused(field: str):
    kwargs = dict(batch_id="b", domain="d", labeler="Someone",
                  labeled_on="2026-08-30", scaffold="s.csv",
                  labels="l.csv", features="f.jsonl")
    kwargs[field] = "  "
    with pytest.raises(ValueError, match=field):
        BatchManifest(**kwargs)


def test_manifest_missing_field_refused(tmp_path: Path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"batch_id": "b", "domain": "d"}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required field"):
        read_manifest(str(p))


def test_manifest_unknown_field_refused(tmp_path: Path):
    """A silently-ignored field is how a provenance claim goes missing."""
    p = tmp_path / "m.json"
    p.write_text(json.dumps({
        "batch_id": "b", "domain": "d", "labeler": "S", "labeled_on": "2026-08-30",
        "scaffold": "s.csv", "labels": "l.csv", "features": "f.jsonl",
        "labelled_by": "typo-field",
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="unrecognised field"):
        read_manifest(str(p))


# ---------------------------------------------------------------------------
# Provenance reporting + labeler-facing slice
# ---------------------------------------------------------------------------

def test_corpus_provenance_reports_composition(tmp_path: Path):
    """A CR that reports n without composition hides the thing a reader needs
    to judge whether the operating point transfers to their domain."""
    m1 = _write_batch(tmp_path, "cpc-ch1-b1", "cpc-legal", _B1)
    m2 = _write_batch(tmp_path, "research-b1", "research-prose", _B2)
    prov = corpus_provenance([str(m1), str(m2)], str(tmp_path))
    assert prov[0] == {
        "batch_id": "cpc-ch1-b1", "domain": "cpc-legal",
        "labeler": "Vardhan (author, practising advocate)",
        "labeled_on": "2026-08-30", "n": 2, "violation": 1, "grounded": 1,
    }
    assert prov[1]["n"] == 1 and prov[1]["domain"] == "research-prose"


def test_export_batch_scaffold_writes_only_requested_rows(tmp_path: Path):
    _write_batch(tmp_path, "b", "d", _B1)
    out = tmp_path / "slice.csv"
    n = export_batch_scaffold([], str(tmp_path / "scaffold-b.csv"), str(out), ["c2#0"])
    assert n == 1
    body = out.read_text(encoding="utf-8")
    assert "c2#0" in body and "c1#0" not in body
    assert "human_label" not in body  # a scaffold slice never carries a label column


def test_export_batch_scaffold_refuses_unknown_claim(tmp_path: Path):
    _write_batch(tmp_path, "b", "d", _B1)
    with pytest.raises(ValueError, match="not in"):
        export_batch_scaffold([], str(tmp_path / "scaffold-b.csv"),
                              str(tmp_path / "o.csv"), ["nope#0"])
