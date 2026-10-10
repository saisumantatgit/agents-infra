"""Incremental, provenance-carrying label ingestion (multi-batch corpora).

WHY THIS EXISTS
---------------
``load_gold_labels`` binds ONE labels file to ONE scaffold and fails loud when
any scaffold claim is unlabeled — the check that stops a silently-shrinking n
from biasing every derived threshold. That check also makes the single-corpus
design structurally unable to accept work that arrives in small increments:
an expert who labels 8 of 400 claims produces a corpus that is 392 rows
"unlabeled", and the loader (correctly) refuses it.

The cpc-book pilot (HQ ask ``agents-infra-2026-07-19-001``) is exactly that
shape, and by binding constraint: the labeler receives **5-10 items at a time**,
weeks apart, each batch framed as a citation-audit pass on his own chapter.

The resolution is NOT to relax the completeness check — it is to change the
unit the check applies to. **A BATCH is the atomic labeled unit.** Each batch
is its own (scaffold, labels) pair and must be internally complete: every claim
in that batch's scaffold carries a gold label bound by ``claim_sha``. The
corpus is then the UNION of complete batches (accumulate-then-derive). Nothing
is weakened — the same six fail-loud properties hold per batch — and a partial
delivery is simply a corpus with fewer batches in it, not a corrupt one.

WHAT A BATCH CARRIES BEYOND LABELS
----------------------------------
Provenance, because a multi-source corpus that cannot say WHO labeled WHAT in
WHICH domain cannot support a per-domain operating point, and cannot be audited
after the fact. ``labeler`` is recorded so the gold-vs-candidate rule stays
checkable per row (a Claude-proposed label is never gold, whatever file it
lands in), and ``domain`` is recorded because the calibration question "does
legal-paraphrase data confound a research-prose operating point?" can only be
ANSWERED if the rows remember which domain they came from.

Pure functions apart from the manifest/CSV reads, which are the I/O boundary.
"""

from __future__ import annotations

import csv
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from scripts.calibrate import (
    ClaimFeatureRow,
    HumanLabel,
    LabeledClaim,
    join_labels,
    load_gold_labels,
)

_REQUIRED_MANIFEST_FIELDS: tuple[str, ...] = (
    "batch_id",
    "domain",
    "labeler",
    "labeled_on",
    "scaffold",
    "labels",
    "features",
)

# A label is GOLD only when a human ratified it. This is the machine-checkable
# half of CLAUDE.md failure-mode 5 ("Claude-generated labels are candidate;
# only Sai-ratified labels are gold"): a batch whose labeler is an assistant
# is refused at ingestion rather than trusted because its CSV said "gold".
_NON_HUMAN_LABELERS: frozenset[str] = frozenset({
    "claude", "assistant", "ai", "model", "gpt", "llm", "auto", "generated",
})


@dataclass(frozen=True)
class BatchManifest:
    """Provenance + file bindings for one incremental label batch.

    ``batch_id``  stable identifier, unique within a corpus.
    ``domain``    corpus domain tag (e.g. "research-prose", "cpc-legal").
                  Carried so a per-domain operating point is derivable and a
                  cross-domain confound is MEASURABLE rather than assumed.
    ``labeler``   who ratified these rows. Refused if non-human (see above).
    ``labeled_on`` ISO date the ratification happened.
    ``scaffold`` / ``labels`` / ``features`` — paths, relative to the manifest.
    """

    batch_id: str
    domain: str
    labeler: str
    labeled_on: str
    scaffold: str
    labels: str
    features: str

    def __post_init__(self) -> None:
        for field in ("batch_id", "domain", "labeler", "labeled_on"):
            if not str(getattr(self, field)).strip():
                raise ValueError(
                    f"BatchManifest: {field!r} is empty. Provenance is not "
                    "optional — a batch that cannot say who labeled it, when, "
                    "and in what domain cannot be audited or per-domain "
                    "calibrated, and must not enter a corpus."
                )
        who = unicodedata.normalize("NFKC", self.labeler).strip().lower()
        if any(token in who.split() or token == who for token in _NON_HUMAN_LABELERS):
            raise ValueError(
                f"BatchManifest: labeler {self.labeler!r} is not a human "
                "ratifier. Claude-generated labels are CANDIDATE, never gold; "
                "calibrating on them validates the gate against the same "
                "judgment the gate encodes (circular). Route this batch "
                "through a human ratifier first."
            )


def read_manifest(path: str) -> BatchManifest:
    """Read a single batch manifest (JSON) from *path*. Fails loud on any
    missing field — never defaults one."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [f for f in _REQUIRED_MANIFEST_FIELDS if f not in raw]
    if missing:
        raise ValueError(
            f"read_manifest: {path!r} is missing required field(s) "
            f"{missing}. A manifest field is never defaulted — a batch with "
            "unknown provenance is unusable as calibration evidence."
        )
    unknown = sorted(set(raw) - set(_REQUIRED_MANIFEST_FIELDS))
    if unknown:
        raise ValueError(
            f"read_manifest: {path!r} carries unrecognised field(s) {unknown}. "
            "Refusing rather than ignoring them: a silently-dropped field is "
            "how a provenance claim goes missing without a signal."
        )
    return BatchManifest(**raw)


def read_feature_rows(path: str) -> list[ClaimFeatureRow]:
    """Read a batch's feature rows (one JSON object per line)."""
    rows: list[ClaimFeatureRow] = []
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"read_feature_rows: {path!r} line {line_no} is not valid "
                    f"JSON ({exc}). The corpus is audit evidence; a malformed "
                    "line is raised, never skipped."
                ) from exc
            obj["cited_source_ids"] = tuple(obj.get("cited_source_ids", ()))
            rows.append(ClaimFeatureRow(**obj))
    return rows


def load_batch(manifest: BatchManifest, root: str) -> list[LabeledClaim]:
    """Load ONE batch into LabeledClaims, enforcing per-batch completeness.

    Every fail-loud property of ``load_gold_labels`` applies unchanged, scoped
    to this batch: gold-only, valid label, no duplicate id, no orphan label, no
    unlabeled scaffold claim, no STALE (``claim_sha``-mismatched) label.

    Pure apart from the three file reads.
    """
    base = Path(root)
    labels: dict[str, HumanLabel] = load_gold_labels(
        str(base / manifest.labels), str(base / manifest.scaffold)
    )
    rows = read_feature_rows(str(base / manifest.features))
    return join_labels(rows, labels)


def load_corpus(
    manifest_paths: list[str], root: str, domain: str | None = None
) -> list[LabeledClaim]:
    """Accumulate many batches into one labeled corpus (accumulate-then-derive).

    ``domain`` filters to a single domain when a per-domain operating point is
    wanted; ``None`` (default) returns every batch, which is what a pooled
    cross-domain sweep needs. Deriving BOTH and comparing is how the
    "does domain X confound the operating point?" question gets answered with
    a measurement instead of an opinion.

    Fails loud on a duplicate ``batch_id`` (two manifests claiming the same
    identity) and on a duplicate ``claim_id`` ACROSS batches — the cross-batch
    collision the single-file design never had to consider, and the one that
    would let a re-labeled claim silently count twice with two different
    truths.
    """
    seen_batches: set[str] = set()
    seen_claims: dict[str, str] = {}
    corpus: list[LabeledClaim] = []

    for path in manifest_paths:
        manifest = read_manifest(path)
        if manifest.batch_id in seen_batches:
            raise ValueError(
                f"load_corpus: duplicate batch_id {manifest.batch_id!r} "
                f"(manifest {path!r}). Two batches claiming one identity make "
                "provenance unresolvable."
            )
        seen_batches.add(manifest.batch_id)

        if domain is not None and manifest.domain != domain:
            continue

        for claim in load_batch(manifest, root):
            prior = seen_claims.get(claim.claim_id)
            if prior is not None:
                raise ValueError(
                    f"load_corpus: claim_id {claim.claim_id!r} appears in both "
                    f"batch {prior!r} and batch {manifest.batch_id!r}. A claim "
                    "labeled twice would be counted twice — and if the two "
                    "labels disagree, the corpus would carry two contradictory "
                    "truths for one claim. Resolve by hand."
                )
            seen_claims[claim.claim_id] = manifest.batch_id
            corpus.append(claim)

    return corpus


def corpus_provenance(manifest_paths: list[str], root: str) -> list[dict]:
    """Return one provenance record per batch: what a CR cites to show which
    human labeled which domain, and how many rows each contributed.

    A calibration record that reports n without reporting its composition
    hides exactly the thing a reader needs to judge whether the operating
    point transfers to their domain.
    """
    out: list[dict] = []
    for path in manifest_paths:
        manifest = read_manifest(path)
        rows = load_batch(manifest, root)
        violations = sum(1 for c in rows if c.label == "violation")
        out.append({
            "batch_id": manifest.batch_id,
            "domain": manifest.domain,
            "labeler": manifest.labeler,
            "labeled_on": manifest.labeled_on,
            "n": len(rows),
            "violation": violations,
            "grounded": len(rows) - violations,
        })
    return out


def export_batch_scaffold(
    rows: list[ClaimFeatureRow],
    scaffold_src: str,
    out_path: str,
    claim_ids: list[str],
) -> int:
    """Write a batch-sized SCAFFOLD slice (the 5-10 rows a labeler receives).

    Slices the generator-owned scaffold; writes no label column and never
    touches a labels file. Returns the number of rows written.

    Refuses to write a slice containing a claim_id absent from the source
    scaffold — a labeler must never be shown a claim the corpus cannot bind
    a judgment back to.
    """
    with open(scaffold_src, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        by_id = {r["claim_id"]: r for r in reader}

    missing = [cid for cid in claim_ids if cid not in by_id]
    if missing:
        raise ValueError(
            f"export_batch_scaffold: claim_id(s) {missing} are not in "
            f"{scaffold_src!r}. Refusing to hand a labeler a claim that cannot "
            "be bound back to the corpus."
        )

    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for cid in claim_ids:
            writer.writerow(by_id[cid])
    return len(claim_ids)
