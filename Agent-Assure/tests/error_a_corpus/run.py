"""Error-A corpus runner: honest drafts, measured against a checkout of the gate.

    uv run python tests/error_a_corpus/run.py --base <Agent-Assure dir> [--limit N] [--no-ablate]

Reuses the usage_genres instrument (store building through the real capture hook,
`ground_check.py --json`, authored-claim verdict mapping). Adds: per-genre and per-shape
rates, and a refusal-cause label for every refused segment. The gate prints no refusing
token, so causes come from ISOLATION (re-run the claim alone against only its own
sentence: GROUNDED alone means the refusal came from context) plus a scan of the
neighbouring source sentences for denial words. Causes are therefore attributions, not
the gate's own report; `results.json` keeps the raw verdict and diagnostic beside them.

Writes results.json next to this file. Every draft is honest by construction, so every
refusal here is a false refusal (Error-A) unless the corpus itself is wrong; the runner
asserts each cited claim is verbatim in its source.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
import threading
import hashlib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

_spec = importlib.util.spec_from_file_location("usage_genres_run", HERE.parent / "usage_genres" / "run.py")
assert _spec and _spec.loader
UG = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = UG
_spec.loader.exec_module(UG)

DENIAL_WORDS = re.compile(
    r"\b(not|no|never|without|unless|cannot|can't|n't|none|nobody|neither|nor|false|fake|myth|myths|"
    r"fabricated|untrue|made up|fiction|rumou?rs?|lies|invented)\b|\w+n't\b", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class Spec:
    id: str
    genre: str
    sources: tuple[Path, ...]
    claims: tuple[dict, ...]


def load_manifest(limit: int | None) -> list[Spec]:
    entries = json.loads((HERE / "manifest.json").read_text())
    if limit:
        by_genre: dict[str, list[dict]] = defaultdict(list)
        for e in entries:
            by_genre[e["genre"]].append(e)
        per = max(1, limit // len(by_genre))
        entries = [e for g in by_genre.values() for e in g[:per]]
    return [Spec(e["id"], e["genre"], tuple(HERE / s for s in e["sources"]), tuple(e["claims"]))
            for e in entries]


def locate(text: str, segs: list[tuple[str, str]]) -> list[tuple[int, int, int]]:
    """(start, end, seg_index) of each checker segment in the draft; raises when one cannot be found."""
    flat, origin = [], []
    for i, ch in enumerate(re.sub(r"\[S\d\]", lambda m: " " * len(m.group()), text)):
        if ch.isalnum():
            flat.append(ch.lower())
            origin.append(i)
    flat_s = "".join(flat)
    out, cursor = [], 0
    for k, (seg, _v) in enumerate(segs):
        key = "".join(c.lower() for c in re.sub(r"\[S\d\]", "", seg) if c.isalnum())
        if not key:
            continue
        pos = flat_s.find(key, cursor)
        if pos < 0:
            raise RuntimeError(f"segment not locatable in draft: {seg!r}")
        out.append((origin[pos], origin[pos + len(key) - 1] + 1, k))
        cursor = pos + len(key)
    return out


def features(text: str) -> list[str]:
    f = []
    if "`" in text:
        f.append("code_span")
    if "(" in text:
        f.append("parenthesis")
    if re.search(r"\bmade up\b", text, re.I):
        f.append("made_up")
    if re.search(r"=\s*(False|false)\b|\bfalse\b|\bFalse\b", text):
        f.append("false_word")
    if re.search(r"\bnever\b", text, re.I):
        f.append("never")
    if re.search(r"\b(not|no|without|unless|cannot|can't)\b|n't\b", text, re.I):
        f.append("negation_in_claim")
    if '"' in text:
        f.append("quote")
    if re.search(r"\d", text):
        f.append("digits")
    if ":" in text:
        f.append("colon")
    return f


def neighbour_denial(source: str, claim: str) -> str:
    """Nearest denial word in the 3 sentences before / 1 after the claim's sentence."""
    sents = [s for s in SENT_SPLIT.split(source) if s.strip()]
    flat_claim = " ".join(claim.split())
    idx = next((i for i, s in enumerate(sents) if flat_claim in " ".join(s.split())), None)
    if idx is None:
        return "context:claim_not_found_in_sentences"
    for off in (-1, 1, -2, -3):
        j = idx + off
        if 0 <= j < len(sents):
            m = DENIAL_WORDS.search(sents[j])
            if m:
                return f"context:neighbour[{off:+d}]:{m.group(0).lower()}"
    return "context:no_denial_word_within_-3..+1"


def structural_label(text: str) -> str:
    t = text.strip()
    if t.startswith("#"):
        return "uncited:heading"
    if t.startswith("```") or t.startswith("|---") or re.match(r"^\|?\s*-{3}", t):
        return "uncited:fence_or_delimiter"
    if t.startswith("|"):
        return "uncited:table_header_row"
    return "uncited:other_line_or_code"


_LOCK_GUARD = threading.Lock()
_KEY_LOCKS: dict[str, threading.Lock] = {}


def isolate(base: Path, claim_text: str, work: Path, cache: dict) -> str:
    """Verdict of the claim cited against ONLY its own sentence."""
    with _LOCK_GUARD:
        lock = _KEY_LOCKS.setdefault(claim_text, threading.Lock())
    with lock:
        return _isolate_locked(base, claim_text, work, cache)


def _isolate_locked(base: Path, claim_text: str, work: Path, cache: dict) -> str:
    if claim_text in cache:
        return cache[claim_text]
    key = hashlib.sha256(claim_text.encode()).hexdigest()[:16]
    src = work / f"iso_{key}_src.md"
    drf = work / f"iso_{key}_draft.md"
    src.write_text(claim_text + ". This line is neutral filler for the isolation run.\n")
    drf.write_text(f"{claim_text} [S1].\n")
    spec = UG.DraftSpec("iso", "iso", "iso", (src,))
    store = work / f"iso_{key}.jsonl"
    UG.build_store(base, spec, store)
    report = UG.check(base, drf, store)
    verdicts = [c["verdict"] for c in report["per_claim"] if c["kind"] != "NON_CLAIM"]
    cache[claim_text] = "GROUNDED" if verdicts and all(v == "GROUNDED" for v in verdicts) else (verdicts[0] if verdicts else "NONE")
    return cache[claim_text]


def run_one(base: Path, spec: Spec, work: Path, ablate: bool, iso_cache: dict) -> dict:
    draft = HERE / "drafts" / f"{spec.id}.md"
    text = draft.read_text()
    corpus = " ".join(" ".join(p.read_text().split()) for p in spec.sources)
    bad = [c["text"] for c in spec.claims if " ".join(c["text"].split()) not in corpus]
    if bad:
        raise RuntimeError(f"{spec.id}: corpus defect, cited text not verbatim in source: {bad}")
    source = "\n".join(s.read_text() for s in spec.sources)
    store = work / f"{spec.id}.jsonl"
    UG.build_store(base, UG.DraftSpec(spec.id, spec.genre, "copied", spec.sources), store)
    report = UG.check(base, draft, store)
    segs = [(c["text"], c["verdict"]) for c in report["per_claim"]]
    spans = UG.authored_spans(text)
    if len(spans) != len(spec.claims):
        raise RuntimeError(f"{spec.id}: {len(spans)} cited spans in draft vs {len(spec.claims)} claims in manifest")
    located = locate(text, segs)
    claims_out, struct_out = [], []
    for (a, b), claim in zip(spans, spec.claims):
        hit = [k for s, e, k in located if s < b and e > a]
        refused = [k for k in hit if report["per_claim"][k]["verdict"] != "GROUNDED"
                   and report["per_claim"][k]["kind"] != "NON_CLAIM"]
        row = {"text": claim["text"], "shape": claim["shape"], "features": features(claim["text"]),
               "grounded": bool(hit) and not refused,
               "segments": [{"verdict": report["per_claim"][k]["verdict"],
                             "diagnostic": report["per_claim"][k].get("support_diagnostic", "")} for k in hit]}
        if refused:
            row["verdicts"] = sorted({report["per_claim"][k]["verdict"] for k in refused})
            row["diagnostics"] = sorted({report["per_claim"][k].get("support_diagnostic", "") for k in refused})
            numbered = bool(re.match(r"\s*\d+\.\s", text[a:b]))
            row["numbered_list_item"] = numbered
            if row["verdicts"] == ["UNGROUNDABLE"]:
                row["cause"] = "gate:ungroundable(source treated as a copy of the draft)"
            elif "UNVERIFIED_NUMBER" in row["verdicts"] and numbered:
                row["cause"] = "list_marker:number_of_numbered_list_item"
            elif ablate:
                alone = isolate(base, claim["text"], work, iso_cache)
                if alone == "GROUNDED":
                    row["cause"] = neighbour_denial(source, claim["text"])
                    if "table" in claim["shape"] and row["cause"].startswith("context:no_denial"):
                        row["cause"] = "context:table_row_merge"
                else:
                    ff = [f for f in row["features"] if f != "colon"]
                    row["cause"] = "intrinsic:" + (ff[0] if ff else "plain_sentence")
            else:
                row["cause"] = "not_ablated"
        claims_out.append(row)
    in_span = {k for s, e, k in located for a, b in spans if s < b and e > a}
    for s, e, k in located:
        c = report["per_claim"][k]
        if k not in in_span and c["kind"] != "NON_CLAIM" and c["verdict"] != "GROUNDED":
            struct_out.append({"text": c["text"], "verdict": c["verdict"], "cause": structural_label(c["text"])})
    return {"id": spec.id, "genre": spec.genre, "gate": report["gate"], "score": report["grounding_score"],
            "claims": claims_out, "structural_refusals": struct_out}


def rate(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def summarise(results: list[dict]) -> dict:
    genres: dict[str, dict] = {}
    for r in results:
        g = genres.setdefault(r["genre"], {"drafts": 0, "PASS": 0, "NEEDS_WORK": 0, "FAIL": 0,
                                           "claims": 0, "grounded": 0, "structural_refusals": 0})
        g["drafts"] += 1
        g[r["gate"]] += 1
        g["claims"] += len(r["claims"])
        g["grounded"] += sum(c["grounded"] for c in r["claims"])
        g["structural_refusals"] += len(r["structural_refusals"])
    for g in genres.values():
        g["grounded_rate_pct"] = rate(g["grounded"], g["claims"])
    shapes: dict[str, dict] = {}
    for r in results:
        for c in r["claims"]:
            s = shapes.setdefault(c["shape"], {"claims": 0, "grounded": 0})
            s["claims"] += 1
            s["grounded"] += c["grounded"]
    for s in shapes.values():
        s["grounded_rate_pct"] = rate(s["grounded"], s["claims"])
    def family(cause: str) -> str:
        return re.sub(r"\[[+-]\d\]", "", cause)   # drop the sentence offset: neighbour[-1]:not -> neighbour:not

    causes: Counter = Counter()
    examples: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        for c in r["claims"]:
            if not c["grounded"]:
                causes[family(c["cause"])] += 1
                if len(examples[family(c["cause"])]) < 3:
                    examples[family(c["cause"])].append({"draft": r["id"], "text": c["text"], "verdicts": c["verdicts"]})
        for s in r["structural_refusals"]:
            causes[s["cause"]] += 1
            if len(examples[s["cause"]]) < 3:
                examples[s["cause"]].append({"draft": r["id"], "text": s["text"], "verdicts": [s["verdict"]]})
    modes = {0: "dense", 1: "normal", 2: "light"}
    by_mode: dict[str, dict] = {}
    for r in results:
        m = by_mode.setdefault(modes[int(r["id"][-3:]) % 3], {"drafts": 0, "PASS": 0, "NEEDS_WORK": 0, "FAIL": 0,
                                                              "claims": 0, "grounded": 0})
        m["drafts"] += 1
        m[r["gate"]] += 1
        m["claims"] += len(r["claims"])
        m["grounded"] += sum(c["grounded"] for c in r["claims"])
    for m in by_mode.values():
        m["grounded_rate_pct"] = rate(m["grounded"], m["claims"])
    gates = Counter(r["gate"] for r in results)
    total = sum(len(r["claims"]) for r in results)
    ok = sum(c["grounded"] for r in results for c in r["claims"])
    return {"drafts": len(results), "gates": dict(gates), "claims": total, "grounded": ok,
            "grounded_rate_pct": rate(ok, total), "by_genre": genres, "by_shape": shapes, "by_density": by_mode,
            "causes": [{"cause": k, "count": n, "examples": examples[k]} for k, n in causes.most_common()]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--work", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=None, help="run about N drafts, spread over genres")
    ap.add_argument("--no-ablate", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "results.json")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    base = args.base.resolve()
    work = args.work or Path(tempfile.mkdtemp(prefix="error_a_corpus_"))
    work.mkdir(parents=True, exist_ok=True)
    specs = load_manifest(args.limit)
    iso_cache: dict = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(lambda s: run_one(base, s, work, not args.no_ablate, iso_cache), specs))
    summary = summarise(results)
    args.out.write_text(json.dumps({"summary": summary, "drafts": results}, indent=1) + "\n")
    print("drafts:", summary["drafts"], "gates:", summary["gates"],
          f"| authored claims grounded {summary['grounded']}/{summary['claims']} ({summary['grounded_rate_pct']}%)")
    print("genre | drafts | PASS | NW | FAIL | grounded%")
    for g, v in sorted(summary["by_genre"].items()):
        print(f"{g} | {v['drafts']} | {v['PASS']} | {v['NEEDS_WORK']} | {v['FAIL']} | {v['grounded_rate_pct']}")
    print("top causes:")
    for c in summary["causes"][:15]:
        print(" ", c["count"], c["cause"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
