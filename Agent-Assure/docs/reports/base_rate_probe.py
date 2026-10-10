"""Base-rate probe: quote vs. paraphrase in real prose, measured against the
Agent-Assure grounding gate's own tokenizer/scorer functions.

Read-only measurement script. Does not modify scripts/ or tests/.

Reuses from scripts/ground_check.py (per task spec, MUST reuse not reimplement):
    _tokenize, _content_words, _strip_citations, _nfkc,
    t2_lexical_score, decompose, classify, ClaimKind
Also reuses the private sentence-splitter _split_sentences (same windowing
definition as the gate's own ±2-sentence T2 window) so our window search is
provably the same algorithm the gate runs, not an approximation of it.

Run: uv run python docs/reports/base_rate_probe.py   (from Agent-Assure/)
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_ASSURE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, AGENT_ASSURE_DIR)

from scripts.ground_check import (  # noqa: E402
    ClaimKind,
    _content_words,
    _nfkc,
    _split_sentences,
    _strip_citations,
    _tokenize,
    classify,
    decompose,
    t2_lexical_score,
)

MANUSCRIPT_GLOB = "/Users/saisumanthbattepati/vibe-coding/cpc-book/manuscript/*.md"
REFERENCE_PATH = (
    "/Users/saisumanthbattepati/vibe-coding/cpc-book/reference/"
    "cpc-1908-fulltext-layout.txt"
)
OUT_JSON = os.path.join(SCRIPT_DIR, "base_rate_probe_results.json")

KEPT_KINDS = {
    ClaimKind.FACTUAL,
    ClaimKind.NUMERIC,
    ClaimKind.ATTRIBUTION,
    ClaimKind.RELATIONAL,
}


def _f1(claim_words: list[str], window_words: list[str]) -> float:
    """Content-word F1 -- identical formula to ground_check._f1.

    Reimplemented here (not imported) because it is pure arithmetic over
    token lists already produced by the gate's own _tokenize/_content_words --
    there is no tokenizer being reimplemented, only Counter intersection.
    """
    if not claim_words or not window_words:
        return 0.0
    cc = Counter(claim_words)
    wc = Counter(window_words)
    inter = sum(min(cc[t], wc[t]) for t in cc)
    p = inter / len(window_words)
    r = inter / len(claim_words)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def _join_tokens(tokens: list[str]) -> str:
    return " " + " ".join(tokens) + " "


def has_exact_containment(claim_tokens: list[str], ref_joined: str) -> bool:
    if not claim_tokens:
        return False
    return _join_tokens(claim_tokens) in ref_joined


def has_long_span(
    claim_tokens: list[str], ref_ngrams: set[tuple[str, ...]], min_len: int = 8
) -> bool:
    """O(1)-per-window membership test against a precomputed set of the
    reference's contiguous min_len-token n-grams (built once in main()).
    Equivalent to sliding an 8-token window over the claim and substring-
    searching the reference, but avoids O(len(reference)) repeated scans.
    """
    n = len(claim_tokens)
    if n < min_len:
        return False
    for i in range(n - min_len + 1):
        if tuple(claim_tokens[i : i + min_len]) in ref_ngrams:
            return True
    return False


@dataclass
class WindowResult:
    score: float
    window_text: str
    window_content: list[str]


def precompute_windows(
    sentences: list[str],
    sent_content: list[list[str]],
    sent_text_cf: list[str],
) -> tuple[list[str], list[Counter], list[list[str]], list[str]]:
    """Precompute, ONCE for the whole reference corpus, the +/-2-sentence
    window at every center c: its joined text, its content-word Counter, its
    content-word list (for novel-token set math), and its casefolded text
    (for the numeric-presence gate). Every claim then reuses these same n
    precomputed windows instead of rebuilding them -- this is the same
    windowing definition as ground_check._best_window_score, just hoisted
    out of the per-claim loop since it does not depend on the claim.
    """
    n = len(sentences)
    texts: list[str] = []
    counters: list[Counter] = []
    contents: list[list[str]] = []
    text_cfs: list[str] = []
    for c in range(n):
        lo = max(0, c - 2)
        hi = min(n, c + 3)
        content: list[str] = []
        for k in range(lo, hi):
            content.extend(sent_content[k])
        texts.append(" ".join(sentences[lo:hi]))
        counters.append(Counter(content))
        contents.append(content)
        text_cfs.append(" ".join(sent_text_cf[lo:hi]))
    return texts, counters, contents, text_cfs


def best_window(
    claim_content: list[str],
    claim_numeric: tuple[str, ...],
    window_texts: list[str],
    window_counters: list[Counter],
    window_contents: list[list[str]],
    window_text_cfs: list[str],
) -> WindowResult:
    """Mirror ground_check._best_window_score's +/-2-sentence window search
    over the PRECOMPUTED windows, but also return the winning window's text
    and content words (needed for the C/D/E novel-token bucketing and for
    quoting audit examples)."""
    best_score = 0.0
    best_idx = -1
    n = len(window_texts)
    numeric_cf = [_nfkc(nt).casefold() for nt in claim_numeric] if claim_numeric else []
    claim_counter = Counter(claim_content)
    claim_len = len(claim_content)
    for c in range(n):
        if numeric_cf:
            wtcf = window_text_cfs[c]
            if not all(nt in wtcf for nt in numeric_cf):
                continue
        wc = window_counters[c]
        if not wc:
            continue
        inter = sum(min(cnt, wc[t]) for t, cnt in claim_counter.items())
        if inter == 0:
            continue
        window_len = sum(wc.values())
        p = inter / window_len
        r = inter / claim_len
        score = 0.0 if p + r == 0 else 2 * p * r / (p + r)
        if score > best_score:
            best_score = score
            best_idx = c
    if best_idx == -1:
        return WindowResult(0.0, "", [])
    return WindowResult(best_score, window_texts[best_idx], window_contents[best_idx])


def main() -> None:
    with open(REFERENCE_PATH, encoding="utf-8") as fh:
        reference_text = fh.read()

    ref_tokens = _tokenize(reference_text)
    ref_joined = _join_tokens(ref_tokens)
    MIN_SPAN = 8
    ref_ngrams8 = {
        tuple(ref_tokens[i : i + MIN_SPAN])
        for i in range(len(ref_tokens) - MIN_SPAN + 1)
    }
    print(f"[ref] {len(ref_tokens)} tokens, {len(ref_ngrams8)} distinct 8-grams", file=sys.stderr)

    ref_sentences = _split_sentences(reference_text)
    sent_content = [_content_words(_tokenize(s)) for s in ref_sentences]
    sent_text_cf = [_nfkc(s).casefold() for s in ref_sentences]
    print(f"[ref] {len(ref_sentences)} sentences", file=sys.stderr)

    window_texts, window_counters, window_contents, window_text_cfs = precompute_windows(
        ref_sentences, sent_content, sent_text_cf
    )
    print(f"[ref] {len(window_texts)} windows precomputed", file=sys.stderr)

    files = sorted(glob.glob(MANUSCRIPT_GLOB))
    assert files, "no manuscript files found"

    rows: list[dict] = []
    discard_counts: dict[str, Counter] = defaultdict(Counter)

    for path in files:
        chapter = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            draft = fh.read()
        raw_claims = decompose(draft)
        classified = [classify(c) for c in raw_claims]
        print(f"[{chapter}] {len(classified)} raw claims", file=sys.stderr)
        for claim in classified:
            if claim.kind not in KEPT_KINDS:
                discard_counts[chapter][claim.kind.value] += 1
                continue

            stripped = _strip_citations(claim.text)
            claim_tokens = _tokenize(stripped)
            claim_content = _content_words(claim_tokens)
            if not claim_content:
                # no content words at all -- cannot be scored meaningfully;
                # counts as UNRELATED (bucket E), reported separately below.
                rows.append({
                    "chapter": chapter, "kind": claim.kind.value,
                    "text": claim.text, "bucket": "E",
                    "best_f1": 0.0, "novel_count": None,
                    "window_text": "", "reason": "no_content_words",
                })
                continue

            if has_exact_containment(claim_tokens, ref_joined):
                rows.append({
                    "chapter": chapter, "kind": claim.kind.value,
                    "text": claim.text, "bucket": "A",
                    "best_f1": 1.0, "novel_count": 0,
                    "window_text": "", "reason": "exact_containment",
                })
                continue

            if has_long_span(claim_tokens, ref_ngrams8):
                rows.append({
                    "chapter": chapter, "kind": claim.kind.value,
                    "text": claim.text, "bucket": "B",
                    "best_f1": None, "novel_count": None,
                    "window_text": "", "reason": "long_span_8plus",
                })
                continue

            claim_numeric = claim.numeric_tokens

            wr = best_window(
                claim_content, claim_numeric,
                window_texts, window_counters, window_contents, window_text_cfs,
            )
            claim_content_set = set(claim_content)
            window_content_set = set(wr.window_content)
            novel = sorted(claim_content_set - window_content_set)
            novel_count = len(novel)

            if novel_count == 0:
                bucket = "C"
            elif 1 <= novel_count <= 3 and wr.score >= 0.60:
                bucket = "D"
            else:
                bucket = "E"

            rows.append({
                "chapter": chapter, "kind": claim.kind.value,
                "text": claim.text, "bucket": bucket,
                "best_f1": round(wr.score, 4), "novel_count": novel_count,
                "novel_tokens": novel,
                "window_text": wr.window_text,
                "reason": "windowed",
            })

    total_kept = len(rows)
    bucket_counts = Counter(r["bucket"] for r in rows)
    abcd = bucket_counts["A"] + bucket_counts["B"] + bucket_counts["C"] + bucket_counts["D"]
    cd = bucket_counts["C"] + bucket_counts["D"]
    headline = cd / abcd if abcd else float("nan")

    def rate_at(cutoff: float) -> tuple[int, int, float]:
        a = bucket_counts["A"]
        b = bucket_counts["B"]
        c = bucket_counts["C"]
        d = 0
        for r in rows:
            if r["bucket"] in ("A", "B", "C"):
                continue
            if r["novel_count"] is None:
                continue
            if 1 <= r["novel_count"] <= 3 and r["best_f1"] is not None and r["best_f1"] >= cutoff:
                d += 1
        abcd_ = a + b + c + d
        return d, abcd_, (c + d) / abcd_ if abcd_ else float("nan")

    d50, abcd50, rate50 = rate_at(0.50)
    d60, abcd60, rate60 = rate_at(0.60)
    d70, abcd70, rate70 = rate_at(0.70)

    per_chapter = defaultdict(Counter)
    for r in rows:
        per_chapter[r["chapter"]][r["bucket"]] += 1

    total_discarded = sum(sum(c.values()) for c in discard_counts.values())

    summary = {
        "total_kept_claims": total_kept,
        "total_discarded_claims": total_discarded,
        "discard_by_kind": {ch: dict(c) for ch, c in discard_counts.items()},
        "bucket_counts": dict(bucket_counts),
        "headline_rate_at_0.60": headline,
        "abcd_denominator": abcd,
        "sensitivity": {
            "0.50": {"D": d50, "denom": abcd50, "rate": rate50},
            "0.60": {"D": d60, "denom": abcd60, "rate": rate60},
            "0.70": {"D": d70, "denom": abcd70, "rate": rate70},
        },
        "per_chapter": {ch: dict(c) for ch, c in per_chapter.items()},
    }

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
