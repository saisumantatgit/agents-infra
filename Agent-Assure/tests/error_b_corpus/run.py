"""Error-B corpus runner: drafts with exactly one fabrication, measured against a checkout of the gate.

    uv run python tests/error_b_corpus/run.py --base <Agent-Assure dir> [--limit N] [--no-control]

Per draft: the real capture hook builds the store from the draft's source, `ground_check.py --json`
checks the draft, and the fabricated segment (located by its character offset in the draft) is mapped to
the checker segments overlapping it. ESCAPE = every overlapping segment is GROUNDED (a NON_CLAIM line is
reported GROUNDED by the gate, so an unscored fabricated heading escapes). CERTIFIED = the draft's gate is
PASS, i.e. the fabrication was certified. The control draft (same draft, fabrication replaced by its honest
text or omitted) is run too, so a PASS rate can be read against what the honest draft earns anyway.

Writes results.json next to this file. Raises on any segment that cannot be located.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "error_a_corpus"))

_spec = importlib.util.spec_from_file_location("usage_genres_run", HERE.parent / "usage_genres" / "run.py")
assert _spec and _spec.loader
UG = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = UG
_spec.loader.exec_module(UG)

_spec_a = importlib.util.spec_from_file_location("error_a_run", HERE.parent / "error_a_corpus" / "run.py")
assert _spec_a and _spec_a.loader
EA = importlib.util.module_from_spec(_spec_a)
sys.modules[_spec_a.name] = EA
_spec_a.loader.exec_module(EA)


def load_manifest(limit: int | None) -> list[dict]:
    entries = json.loads((HERE / "manifest.json").read_text())
    if limit:
        by_class: dict[str, list[dict]] = defaultdict(list)
        for e in entries:
            by_class[e["class"]].append(e)
        per = max(1, limit // len(by_class))
        entries = [e for g in by_class.values() for e in g[:per]]
    return entries


def check_draft(base: Path, spec: dict, folder: str, work: Path) -> dict:
    draft = HERE / folder / f"{spec['id']}.md"
    text = draft.read_text()
    source = HERE / spec["source"]
    store = work / f"{spec['id']}.jsonl"
    UG.build_store(base, UG.DraftSpec(spec["id"], spec["genre"], "fabricated", (source,)), store)
    report = UG.check(base, draft, store)
    out = {"gate": report["gate"], "score": report["grounding_score"]}
    if folder == "drafts":
        segs = [(c["text"], c["verdict"]) for c in report["per_claim"]]
        located = EA.locate(text, segs)
        a, b = spec["offset"], spec["offset"] + len(spec["fabricated"])
        if text[a:b] != spec["fabricated"]:
            raise RuntimeError(f"{spec['id']}: manifest offset does not point at the fabricated segment")
        hit = [k for s, e, k in located if s < b and e > a]
        if not hit:
            raise RuntimeError(f"{spec['id']}: no checker segment overlaps the fabrication {spec['fabricated']!r}")
        out["fab_verdicts"] = sorted({report["per_claim"][k]["verdict"] for k in hit})
        out["fab_kinds"] = sorted({report["per_claim"][k]["kind"] for k in hit})
        out["escaped"] = all(report["per_claim"][k]["verdict"] == "GROUNDED" for k in hit)
        refused_other = [k for s, e, k in located if not (s < b and e > a)
                         and report["per_claim"][k]["verdict"] != "GROUNDED"]
        out["other_refused"] = len(refused_other)
    return out


def run_one(base: Path, spec: dict, work: Path, control: bool) -> dict:
    row = {"id": spec["id"], "genre": spec["genre"], "class": spec["class"], "variant": spec["variant"],
           **check_draft(base, spec, "drafts", work)}
    if control:
        c = check_draft(base, spec, "controls", work)
        row["control_gate"] = c["gate"]
    return row


def rate(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def summarise(rows: list[dict]) -> dict:
    def block(group: list[dict]) -> dict:
        n = len(group)
        esc = sum(r["escaped"] for r in group)
        pas = sum(r["gate"] == "PASS" for r in group)
        d = {"drafts": n, "escaped": esc, "escaped_pct": rate(esc, n), "pass": pas, "pass_pct": rate(pas, n),
             "NEEDS_WORK": sum(r["gate"] == "NEEDS_WORK" for r in group), "FAIL": sum(r["gate"] == "FAIL" for r in group)}
        if group and "control_gate" in group[0]:
            d["control_pass"] = sum(r["control_gate"] == "PASS" for r in group)
        return d

    def by(key: str) -> dict:
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        return {k: block(v) for k, v in sorted(groups.items())}

    classes: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        classes[(r["class"], r["variant"])].append(r)
    return {"all": block(rows), "by_class": by("class"), "by_genre": by("genre"),
            "by_class_variant": {f"{c}/{v}": block(g) for (c, v), g in sorted(classes.items())}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--work", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=None, help="run about N drafts, spread over classes")
    ap.add_argument("--no-control", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "results.json")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    base = args.base.resolve()
    work = args.work or Path(tempfile.mkdtemp(prefix="error_b_corpus_"))
    work.mkdir(parents=True, exist_ok=True)
    specs = load_manifest(args.limit)
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        rows = list(ex.map(lambda s: run_one(base, s, work, not args.no_control), specs))
    summary = summarise(rows)
    args.out.write_text(json.dumps({"summary": summary, "drafts": rows}, indent=1) + "\n")
    a = summary["all"]
    print(f"drafts: {a['drafts']} | fabrication GROUNDED (escaped): {a['escaped']} | draft PASS (certified): {a['pass']}")
    print("class | drafts | escaped | PASS | control PASS")
    for c, v in summary["by_class"].items():
        print(f"{c} | {v['drafts']} | {v['escaped']} | {v['pass']} | {v.get('control_pass', '-')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
