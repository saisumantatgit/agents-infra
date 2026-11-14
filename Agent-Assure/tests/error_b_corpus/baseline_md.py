"""Writes BASELINE.md from results.json + manifest.json.

    uv run python tests/error_b_corpus/baseline_md.py --commit <sha>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    args = ap.parse_args()
    res = json.loads((HERE / "results.json").read_text())
    man = {m["id"]: m for m in json.loads((HERE / "manifest.json").read_text())}
    s, rows = res["summary"], res["drafts"]
    a = s["all"]
    out: list[str] = []
    w = out.append
    w("# Error-B corpus baseline\n")
    w(f"**Verdict: {a['pass']} of {a['drafts']} drafts carrying one fabrication certify PASS ({a['pass_pct']}%); "
      f"the fabricated segment is GROUNDED in {a['escaped']} ({a['escaped_pct']}%).** "
      f"Every other draft content is verbatim from its source, so each PASS is a certified fabrication (Error-B).\n")
    w(f"Measured on main `{args.commit}` (worktree ovn1115-q10, no scripts edited). Command, from `Agent-Assure/`:\n")
    w("    uv run python tests/error_b_corpus/run.py --base .")
    w(f"    uv run python tests/error_b_corpus/baseline_md.py --commit {args.commit}\n")
    w("## What the corpus is, and is not\n")
    w(f"- **Size:** {a['drafts']} drafts, 14 genres x 20, 18 fabrication classes (15 or 16 drafts each). Each draft reuses the Error-A source document "
      "for its genre and index, with one authored block appended after the source's first paragraph, plus one draft with exactly one fabrication "
      "(`manifest.json` names its class, variant, and the fabricated segment). Regenerate with `build_corpus.py` (seed fixed; it asserts every other cited "
      "claim is verbatim in the source and the fabrication is not, except the denied classes where it is verbatim and denied).")
    w("- **Two measures per draft.** ESCAPE: every checker segment overlapping the fabricated segment is GROUNDED (the gate reports an unscored "
      "heading as GROUNDED, so a fabricated heading that is not scored escapes). CERTIFIED: the whole draft gate is PASS. Certified implies escaped; "
      "escaped without PASS means another segment of the draft was refused, which hides the fabrication only by accident.")
    w("- **Control column.** The same draft with the fabrication replaced by its honest text (or omitted) is run too. `Control PASS` is how many "
      "of the class's honest twins the gate certifies; a low value means the class cannot reach PASS on this gate whatever it does with the "
      "fabrication, so read PASS against it (a PASS count of 0 over a control of 0 is no evidence of safety).")
    w("- **Not a prevalence sample, not a red team.** Classes are spread evenly by construction; variants within a class are fixed shapes drawn from "
      "reports R36, R37 and the Error-A ruling pack. A 0 means not found by these shapes.\n")
    w("## Per class\n")
    w("| Class | Drafts | Fabrication GROUNDED | PASS (certified) | NEEDS_WORK | FAIL | Control PASS |")
    w("|---|---|---|---|---|---|---|")
    for c, v in s["by_class"].items():
        w(f"| {c} | {v['drafts']} | {v['escaped']} ({v['escaped_pct']}%) | {v['pass']} ({v['pass_pct']}%) | {v['NEEDS_WORK']} | {v['FAIL']} | {v['control_pass']} |")
    w(f"| **All** | {a['drafts']} | {a['escaped']} ({a['escaped_pct']}%) | {a['pass']} ({a['pass_pct']}%) | {a['NEEDS_WORK']} | {a['FAIL']} | {a['control_pass']} |\n")
    w("## Per class and variant (classes with any escape)\n")
    w("| Class / variant | Drafts | Fabrication GROUNDED | PASS | Control PASS |")
    w("|---|---|---|---|---|")
    hot = {c for c, v in s["by_class"].items() if v["escaped"]}
    for k, v in s["by_class_variant"].items():
        if k.split("/")[0] in hot:
            w(f"| {k} | {v['drafts']} | {v['escaped']} | {v['pass']} | {v['control_pass']} |")
    w("")
    w("## Per genre\n")
    w("| Genre | Drafts | Fabrication GROUNDED | PASS | Control PASS |")
    w("|---|---|---|---|---|")
    for g, v in s["by_genre"].items():
        w(f"| {g} | {v['drafts']} | {v['escaped']} | {v['pass']} | {v['control_pass']} |")
    w("")
    certified = [r for r in rows if r["gate"] == "PASS"]
    w(f"## Certified fabrications: every PASS draft ({len(certified)})\n")
    w("| Draft | Class / variant | Fabricated segment |")
    w("|---|---|---|")
    for r in certified:
        m = man[r["id"]]
        seg = m["fabricated"].replace("|", "\\|").replace("\n", " ")
        w(f"| {r['id']} | {r['class']} / {r['variant']} | {seg} |")
    w("")
    esc_np = [r for r in rows if r["escaped"] and r["gate"] != "PASS"]
    w(f"## Escaped but not certified ({len(esc_np)})\n")
    w("The fabrication is GROUNDED but another segment of the draft is refused. These would certify if the honest neighbour were accepted.\n")
    w("| Draft | Class / variant | Gate | Fabricated segment |")
    w("|---|---|---|---|")
    for r in esc_np:
        seg = man[r["id"]]["fabricated"].replace("|", "\\|").replace("\n", " ")
        w(f"| {r['id']} | {r['class']} / {r['variant']} | {r['gate']} | {seg} |")
    w("")
    w("## Load-bearing assumption\n")
    w("That every non-fabricated cited segment is true to its source and the one labelled segment is the only falsehood. The builder asserts the first "
      "(verbatim) and the second (absent from the source, or present and denied), but a fabrication that happens to restate a fact the source supports in "
      "another place (a moved number whose value reappears) is labelled by construction, not by independent review. The drafts have not been read by a "
      "second reviewer.")
    (HERE / "BASELINE.md").write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
