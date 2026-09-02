"""BASE-RATE-V2 citation-resolved probe (2026-09-02).

READ-ONLY measurement script. Imports gate internals from scripts/ground_check.py
but does not modify them. Reuses the gate's own tokenizer/scorer so every number
here is provably the gate's own arithmetic, not an approximation of it.

Run from Agent-Assure/:
    PYTHONPATH=. uv run python docs/reports/base_rate_v2_probe.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ground_check import (  # noqa: E402
    ClaimKind,
    _content_words,
    _nfkc,
    _strip_citations,
    _tokenize,
    classify,
    decompose,
    t2_lexical_score,
)

MANUSCRIPT_DIR = Path("/Users/saisumanthbattepati/vibe-coding/cpc-book/manuscript")
STATUTE_PATH = Path(
    "/Users/saisumanthbattepati/vibe-coding/cpc-book/reference/cpc-1908-fulltext-layout.txt"
)
OUT_JSON = Path(__file__).resolve().parent / "base_rate_v2_probe_results.json"

KEEP_KINDS = {ClaimKind.FACTUAL, ClaimKind.NUMERIC, ClaimKind.ATTRIBUTION, ClaimKind.RELATIONAL}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def checkpoint(data: dict) -> None:
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Step 1 — statute index
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(
    r"(?:^|\n)\s*\[?\s*(\d{1,3}[A-Za-z]{0,2})\.\s+([A-Za-z][^\n]{1,150}?)\.\s?—",
)
_ORDER_RE = re.compile(r"(?:^|\n)\s*ORDER\s+([IVXLCM]+[A-Za-z]?)\b")

# OCR layout uses ". —" (period-space-dash) for a handful of genuine headers
# (e.g. "21. Objections to jurisdiction. —") but the SAME pattern also appears
# inside page-footnotes ("9. Subs. by Act 104 of 1976, s. 23, ... Explanation
# 2. —in clauses ..."). Footnotes are amendment-history prose; a real section/
# rule title never opens with these verbs. Combined with the monotonicity
# guard below, this keeps the space-tolerant match from re-admitting footnote
# noise that the strict "no space" form already excluded.
_FOOTNOTE_TITLE_START_RE = re.compile(
    r"^(Subs\.|Ins\.|Omitted|Rep\.|Added|See\b|Cl\.|Clause\b|The word|Explanation \d)",
)


def _num_value(num: str) -> float:
    """Sort key for a section/rule label like '35A' -> 35.1 (letter breaks ties)."""
    m = re.match(r"(\d+)([A-Za-z]*)", num)
    base = int(m.group(1))
    suffix = m.group(2)
    frac = sum(ord(c) for c in suffix) / 10000.0
    return base + frac


def build_statute_index(text: str) -> tuple[dict[str, str], dict[tuple[str, str], str], int, int]:
    """Return (sections_index, orders_index, token_count, schedule_start_offset).

    sections_index: {"80": unit_text, ...}
    orders_index:   {("VII", "11"): unit_text, ...}
    """
    text = _nfkc(text)
    total_tokens = len(_tokenize(text))

    body_marker = re.search(
        r"1\.\s+Short title, commencement and extent\.—", text
    )
    if not body_marker:
        raise RuntimeError(
            "INDEX BUILD FAILED: could not locate Section 1 body start marker. "
            "Statute layout has changed or file is not the expected text."
        )
    body_start = body_marker.start()

    schedule_marker = re.search(r"THE FIRST SCHEDULE", text[body_start:])
    if not schedule_marker:
        raise RuntimeError(
            "INDEX BUILD FAILED: could not locate 'THE FIRST SCHEDULE' after body start."
        )
    schedule_start = body_start + schedule_marker.start()

    sections_region = text[body_start:schedule_start]
    orders_region = text[schedule_start:]

    # --- Sections ---
    sections_index: dict[str, str] = {}
    matches = list(_HEADER_RE.finditer(sections_region))
    last_val = -1.0
    accepted: list[tuple[int, str]] = []  # (start_offset, number)
    for m in matches:
        num = m.group(1)
        title = m.group(2)
        if _FOOTNOTE_TITLE_START_RE.match(title.strip()):
            continue
        val = _num_value(num)
        if val < last_val - 0.5:  # monotonicity guard vs. footnote noise
            continue
        last_val = max(last_val, val)
        accepted.append((m.start(), num))
    for i, (start, num) in enumerate(accepted):
        end = accepted[i + 1][0] if i + 1 < len(accepted) else len(sections_region)
        sections_index[num] = sections_region[start:end].strip()

    # --- Orders / Rules ---
    orders_index: dict[tuple[str, str], str] = {}
    order_spans: list[tuple[int, str]] = [
        (m.start(), m.group(1)) for m in _ORDER_RE.finditer(orders_region)
    ]
    for oi, (ostart, roman) in enumerate(order_spans):
        oend = order_spans[oi + 1][0] if oi + 1 < len(order_spans) else len(orders_region)
        order_text = orders_region[ostart:oend]
        rule_matches = list(_HEADER_RE.finditer(order_text))
        last_val = -1.0
        raccepted: list[tuple[int, str]] = []
        for m in rule_matches:
            num = m.group(1)
            title = m.group(2)
            if _FOOTNOTE_TITLE_START_RE.match(title.strip()):
                continue
            val = _num_value(num)
            if val < last_val - 0.5:
                continue
            last_val = max(last_val, val)
            raccepted.append((m.start(), num))
        for ri, (rstart, rnum) in enumerate(raccepted):
            rend = raccepted[ri + 1][0] if ri + 1 < len(raccepted) else len(order_text)
            orders_index[(roman, rnum)] = order_text[rstart:rend].strip()

    return sections_index, orders_index, total_tokens, schedule_start


# ---------------------------------------------------------------------------
# Step 2 — citation extraction from claim text
# ---------------------------------------------------------------------------

_SECTION_CITE_RE = re.compile(r"\bSections?\s+(\d{1,3}[A-Za-z]{0,2})\b")
_ORDER_RULE_CITE_RE = re.compile(
    r"\bOrder\s+([IVXLCM]+)\s*,?\s+Rules?\s+(\d{1,3}[A-Za-z]{0,2})\b"
)
_CITE_SHAPED_RE = re.compile(
    r"\bSections?\s+\S+|\bOrder\s+[IVXLCM]+\s*,?\s+Rules?\s+\S+", re.IGNORECASE
)


def extract_statutory_citations(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (resolvable_refs, all_citation_shaped_strings).

    resolvable_refs: list of ("section", num) or ("order_rule", "roman|num")
    all_citation_shaped_strings: every citation-shaped substring found (for
    UNRESOLVED reporting), regardless of whether it later resolves.
    """
    refs: list[tuple[str, str]] = []
    for m in _SECTION_CITE_RE.finditer(text):
        refs.append(("section", m.group(1)))
    for m in _ORDER_RULE_CITE_RE.finditer(text):
        refs.append(("order_rule", f"{m.group(1)}|{m.group(2)}"))
    shaped = [m.group(0) for m in _CITE_SHAPED_RE.finditer(text)]
    return refs, shaped


# ---------------------------------------------------------------------------
# Step 3 — decomposition-artifact detection
# ---------------------------------------------------------------------------

_NON_TERMINAL_END = set(",;:—-")


def is_artifact(text: str) -> tuple[bool, str]:
    stripped = text.strip()
    if stripped.endswith("?"):
        return True, "INTERROGATIVE"
    if stripped and stripped[-1] in _NON_TERMINAL_END:
        return True, "FRAGMENT"
    content = _content_words(_tokenize(_strip_citations(stripped)))
    if len(content) < 4:
        return True, "FRAGMENT"
    return False, ""


# ---------------------------------------------------------------------------
# Step 4 — bucketing CITED, non-artifact claims against their own cited unit
# ---------------------------------------------------------------------------

def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def bucket_claim(claim_text: str, unit_text: str) -> tuple[str, float]:
    claim_tokens = _tokenize(_strip_citations(claim_text))
    unit_tokens = _tokenize(_strip_citations(unit_text))
    n = len(claim_tokens)
    if n == 0 or not unit_tokens:
        return "F", 0.0

    # A: EXACT — whole claim is a contiguous span of the unit.
    width = n
    for start in range(len(unit_tokens) - width + 1):
        if unit_tokens[start : start + width] == claim_tokens:
            return "A", 1.0

    # B: LONG-SPAN — some contiguous >=8-token claim span appears in the unit.
    if n >= 8:
        unit_8grams = _ngrams(unit_tokens, 8)
        for j in range(n - 8 + 1):
            if tuple(claim_tokens[j : j + 8]) in unit_8grams:
                return "B", 1.0

    claim_content = _content_words(claim_tokens)
    unit_content = _content_words(unit_tokens)
    unit_counter = Counter(unit_content)
    claim_counter = Counter(claim_content)

    missing_tokens: list[str] = []
    remaining = unit_counter.copy()
    for tok, cnt in claim_counter.items():
        avail = remaining.get(tok, 0)
        if cnt > avail:
            missing_tokens.extend([tok] * (cnt - avail))

    t2 = t2_lexical_score(claim_text, unit_text)

    if not missing_tokens:
        return "C", t2
    if len(set(missing_tokens)) <= 3 and t2 >= 0.60:
        return "D", t2
    return "F", t2


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log("Loading statute...")
    statute_text = STATUTE_PATH.read_text(encoding="utf-8")
    sections_index, orders_index, total_tokens, schedule_start = build_statute_index(statute_text)
    log(
        f"Statute index built: {len(sections_index)} sections, {len(orders_index)} "
        f"order/rule units, {total_tokens} tokens."
    )

    samples = []
    sample_keys = (
        [("section", k) for k in list(sections_index)[:3]]
        + [("order_rule", k) for k in list(orders_index)[:2]]
    )
    for kind, key in sample_keys:
        unit = sections_index[key] if kind == "section" else orders_index[key]
        samples.append({"kind": kind, "key": str(key), "first_100_chars": unit[:100]})
        log(f"  SAMPLE [{kind} {key}]: {unit[:100]!r}")

    if len(sections_index) < 100 or len(orders_index) < 100:
        log(
            "INDEX LOOKS BROKEN (too few units) — STOPPING per task instructions. "
            f"sections={len(sections_index)} orders={len(orders_index)}"
        )
        checkpoint({"status": "ABORTED_BAD_INDEX", "sections": len(sections_index), "orders": len(orders_index)})
        sys.exit(1)

    chapters = sorted(MANUSCRIPT_DIR.glob("*.md"))
    log(f"Found {len(chapters)} chapters.")

    results = {
        "status": "IN_PROGRESS",
        "index": {
            "sections_count": len(sections_index),
            "orders_rules_count": len(orders_index),
            "statute_tokens": total_tokens,
            "samples": samples,
        },
        "per_chapter": {},
        "unresolved_strings": {},
        "artifact_samples": [],
        "f_samples": [],
    }
    checkpoint(results)

    totals = Counter()
    unresolved_strings_counter: Counter = Counter()
    artifact_samples: list[dict] = []
    f_samples: list[dict] = []
    bucket_totals = Counter()

    claim_counter_global = 0

    for chap_path in chapters:
        chap_name = chap_path.name
        log(f"--- Chapter: {chap_name} ---")
        raw = chap_path.read_text(encoding="utf-8")
        claims = decompose(raw)
        claims = [classify(c) for c in claims]
        kept = [c for c in claims if c.kind in KEEP_KINDS]
        log(f"{chap_name}: decomposed={len(claims)} kept={len(kept)}")

        chap_artifact = 0
        chap_cited = chap_uncited = chap_unresolved = 0
        chap_buckets = Counter()

        for c in kept:
            claim_counter_global += 1
            if claim_counter_global % 200 == 0:
                log(f"  heartbeat: {claim_counter_global} claims processed so far")

            artifact, artifact_kind = is_artifact(c.text)
            if artifact:
                chap_artifact += 1
                if len(artifact_samples) < 10:
                    artifact_samples.append(
                        {"chapter": chap_name, "kind": artifact_kind, "text": c.text}
                    )
                continue  # excluded from Step 4 population

            refs, shaped = extract_statutory_citations(c.text)
            resolved_units: list[str] = []
            for kind, key in refs:
                if kind == "section" and key in sections_index:
                    resolved_units.append(sections_index[key])
                elif kind == "order_rule":
                    roman, rnum = key.split("|")
                    if (roman, rnum) in orders_index:
                        resolved_units.append(orders_index[(roman, rnum)])

            if resolved_units:
                chap_cited += 1
                unit_text = "\n".join(resolved_units)
                bucket, score = bucket_claim(c.text, unit_text)
                chap_buckets[bucket] += 1
                if bucket == "F" and len(f_samples) < 10:
                    f_samples.append(
                        {
                            "chapter": chap_name,
                            "claim": c.text,
                            "cited_unit_excerpt": unit_text[:300],
                            "t2_score": round(score, 3),
                        }
                    )
            elif shaped:
                chap_unresolved += 1
                for s in shaped:
                    unresolved_strings_counter[s] += 1
            else:
                chap_uncited += 1

        totals["kept"] += len(kept)
        totals["artifact"] += chap_artifact
        totals["cited"] += chap_cited
        totals["uncited"] += chap_uncited
        totals["unresolved"] += chap_unresolved
        bucket_totals.update(chap_buckets)

        results["per_chapter"][chap_name] = {
            "kept": len(kept),
            "artifact": chap_artifact,
            "cited": chap_cited,
            "uncited": chap_uncited,
            "unresolved": chap_unresolved,
            "buckets": dict(chap_buckets),
        }
        results["unresolved_strings"] = dict(unresolved_strings_counter)
        results["artifact_samples"] = artifact_samples
        results["f_samples"] = f_samples
        results["totals"] = dict(totals)
        results["bucket_totals"] = dict(bucket_totals)
        checkpoint(results)
        log(
            f"{chap_name} done: cited={chap_cited} uncited={chap_uncited} "
            f"unresolved={chap_unresolved} artifact={chap_artifact} buckets={dict(chap_buckets)}"
        )

    a = bucket_totals.get("A", 0)
    b = bucket_totals.get("B", 0)
    c_ = bucket_totals.get("C", 0)
    d = bucket_totals.get("D", 0)
    f = bucket_totals.get("F", 0)
    denom_with_f = a + b + c_ + d + f
    denom_no_f = a + b + c_ + d
    headline_with_f = (c_ + d) / denom_with_f if denom_with_f else 0.0
    headline_no_f = (c_ + d) / denom_no_f if denom_no_f else 0.0
    artifact_rate = totals["artifact"] / totals["kept"] if totals["kept"] else 0.0

    results["status"] = "DONE"
    results["headline"] = {
        "A": a, "B": b, "C": c_, "D": d, "F": f,
        "denom_with_f": denom_with_f,
        "denom_no_f": denom_no_f,
        "headline_rate_incl_F_as_grounded_denom": round(headline_with_f, 4),
        "headline_rate_excl_F": round(headline_no_f, 4),
        "artifact_rate_overall": round(artifact_rate, 4),
    }
    checkpoint(results)

    log("=" * 70)
    log("FINAL SUMMARY")
    log(f"Statute index: {len(sections_index)} sections, {len(orders_index)} order/rule units")
    log(f"Population: kept={totals['kept']} cited={totals['cited']} uncited={totals['uncited']} unresolved={totals['unresolved']}")
    log(f"Artifact rate (of kept): {artifact_rate:.1%} ({totals['artifact']}/{totals['kept']})")
    log(f"Buckets A={a} B={b} C={c_} D={d} F={f}")
    log(f"HEADLINE (C+D)/(A+B+C+D+F) = {headline_with_f:.1%}")
    log(f"HEADLINE excl. F: (C+D)/(A+B+C+D) = {headline_no_f:.1%}")
    log("=" * 70)


if __name__ == "__main__":
    main()
