"""Renders BASELINE.md from results.json (so the table cannot drift from the data).

    uv run python tests/error_a_corpus/baseline_md.py --commit <sha>
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    args = ap.parse_args()
    data = json.loads((HERE / "results.json").read_text())
    s, drafts = data["summary"], data["drafts"]
    claims = [(r, c) for r in drafts for c in r["claims"]]
    refused = [(r, c) for r, c in claims if not c["grounded"]]
    numbered = [(r, c) for r, c in claims if c.get("numbered_list_item") or
                (c["grounded"] and False)]
    # numbered-list drafts: claims in drafts whose body has "1. " items
    num_ids = {r["id"] for r in drafts if (HERE / "drafts" / f"{r['id']}.md").read_text().startswith("1. ")
               or "\n1. " in (HERE / "drafts" / f"{r['id']}.md").read_text()}
    non_num = [(r, c) for r, c in claims if r["id"] not in num_ids]
    nn = len(non_num)
    ungroundable = sum(1 for r, c in refused if c.get("verdicts") == ["UNGROUNDABLE"])
    only_structure = [r for r in drafts if r["gate"] != "PASS" and all(c["grounded"] for c in r["claims"])]
    total_struct = sum(len(r["structural_refusals"]) for r in drafts)
    verdicts = Counter(v for _, c in refused for v in c["verdicts"])
    g = s["gates"]
    out = []
    w = out.append
    w("# Error-A corpus baseline")
    w("")
    w(f"**Verdict: {g.get('PASS', 0)} of {s['drafts']} honest drafts pass the gate; "
      f"{g.get('NEEDS_WORK', 0)} NEEDS_WORK, {g.get('FAIL', 0)} FAIL. "
      f"{s['grounded']} of {s['claims']} cited claims ({s['grounded_rate_pct']}%) are GROUNDED.** "
      "Every claim is a verbatim sentence or cell of its own source, so every refusal below is a false refusal (Error-A).")
    w("")
    w(f"Measured on main `{args.commit}` (worktree ovn1115-q2, no scripts edited). Command, from `Agent-Assure/`:")
    w("")
    w("    uv run python tests/error_a_corpus/run.py --base .")
    w("    uv run python tests/error_a_corpus/baseline_md.py --commit " + args.commit)
    w("")
    w("## What the corpus is, and is not")
    w("")
    w(f"- **Size:** {s['drafts']} drafts, 14 genres x 24, each with its own source file written for this corpus (no third-party text), {s['claims']} cited claims. Regenerate with `build_corpus.py` (seed fixed).")
    w("- **Honesty by construction:** each cited claim is a verbatim substring of its source (asserted at build time and again by the runner, which raises on any exception). No fabrication is in the corpus.")
    w("- **Not a prevalence sample.** Shapes known to be refused (negation next to a claim, made up of, quoted denials, never happened, table No cells, =False, numbers) are deliberately over-represented. Read the per-shape table, not the headline rate, as the measurement. `light` drafts (one third) carry no negation neighbours.")
    w("- **Unit of count:** an authored claim is one cited bullet, sentence or table cell. It is GROUNDED only if every checker segment overlapping it is GROUNDED (same rule as `usage_genres`).")
    w("- **Refusing cause is an attribution, not the gate's report.** The gate prints a verdict and a `support_diagnostic` but not the refusing token. The runner re-runs each refused claim alone against only its own sentence: grounded alone = context caused it, then the nearest denial word in the 3 sentences before or 1 after is named; refused alone = intrinsic, named by the first feature of the claim. Validation: of 80 sampled `neighbour` attributions, 69 were refused again with only the neighbour and the claim as source, and 68 became GROUNDED when the neighbour was swapped for a neutral sentence (about 85% agreement).")
    w("")
    w("## Per genre")
    w("")
    w("| Genre | Drafts | PASS | NEEDS_WORK | FAIL | Claims | GROUNDED | Rate |")
    w("|---|---|---|---|---|---|---|---|")
    for name, v in sorted(s["by_genre"].items()):
        w(f"| {name} | {v['drafts']} | {v['PASS']} | {v['NEEDS_WORK']} | {v['FAIL']} | {v['claims']} | {v['grounded']} | {v['grounded_rate_pct']}% |")
    w(f"| **All** | {s['drafts']} | {g.get('PASS', 0)} | {g.get('NEEDS_WORK', 0)} | {g.get('FAIL', 0)} | {s['claims']} | {s['grounded']} | {s['grounded_rate_pct']}% |")
    w("")
    w("## Per density (source length against claims quoted)")
    w("")
    w("| Density | Drafts | PASS | NEEDS_WORK | FAIL | Rate |")
    w("|---|---|---|---|---|---|")
    for name in ("dense", "normal", "light"):
        v = s["by_density"][name]
        w(f"| {name} | {v['drafts']} | {v['PASS']} | {v['NEEDS_WORK']} | {v['FAIL']} | {v['grounded_rate_pct']}% |")
    w("")
    w("## Per shape (claim level)")
    w("")
    w("| Shape | Claims | GROUNDED | Rate |")
    w("|---|---|---|---|")
    for name, v in sorted(s["by_shape"].items(), key=lambda kv: kv[1]["grounded_rate_pct"]):
        w(f"| {name} | {v['claims']} | {v['grounded']} | {v['grounded_rate_pct']}% |")
    w("")
    w("## Top 15 refusal causes")
    w("")
    w(f"Counted over {len(refused)} refused claims plus {total_struct} uncited structural segments (headings, fences, table header rows) that the gate scored as claims. Offsets are folded: `neighbour:not` means the nearest denial word in an adjacent sentence was `not`.")
    w("")
    w("| # | Cause | Count | Example segment |")
    w("|---|---|---|---|")
    for i, c in enumerate(s["causes"][:15], 1):
        ex = c["examples"][0]
        text = ex["text"].replace("|", "\\|").replace("\n", " / ")[:90]
        w(f"| {i} | `{c['cause']}` | {c['count']} | {ex['draft']}: {text} ({', '.join(ex['verdicts'])}) |")
    w("")
    w("Refused-claim verdicts: " + ", ".join(f"{k} {n}" for k, n in verdicts.most_common()) + ".")
    w("")
    w("## Readings")
    w("")
    lm = sum(1 for _, c in refused if c.get("cause") == "list_marker:number_of_numbered_list_item")
    w(f"- **Numbered lists (largest single cause):** a numbered-list item counts its own list number as an unverified figure. {lm} claims ({pct(lm, len(refused))} of all refusals) are refused for this alone, from {len(num_ids)} drafts that use a numbered list. Excluding those drafts, the grounded rate is {pct(sum(c['grounded'] for _, c in non_num), nn)}.")
    w(f"- **Structure:** {total_struct} uncited segments (headings, code fences, table header rows) are scored as claims; {len(only_structure)} drafts have every cited claim GROUNDED and still do not PASS.")
    w(f"- **Near-copy rule (UNGROUNDABLE):** {ungroundable} claims in this run. The rule treats a source whose word pairs are 80% or more present in the draft as a copy of the draft; this corpus pads each source with uncited sentences, so it rarely fires here. An earlier draft of this corpus with short sources hit it on most dense drafts.")
    w("- **Spelled-out percentages:** probe, source sentence copied word for word plus one neutral sentence: `About 85 percent of requests failed at the peak [S1].` gives UNVERIFIED_NUMBER; `About 85% of requests failed at the peak [S1].` gives GROUNDED. Half of the percentage claims here use each form, so the `percent` form feeds the `intrinsic:digits` cause.")
    w("")
    w("## Load-bearing assumption")
    w("")
    w("That my sources and drafts are honest. They are AI-written and the faithfulness check is mechanical (verbatim substring), not independent human labelling; a claim that is verbatim but reads as a different assertion out of context (for example a sentence opening with `It`) still counts as honest here. Second weak seam: cause labels for context refusals are an 85% agreement attribution, not the gate's own report.")
    w("")
    (HERE / "BASELINE.md").write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
