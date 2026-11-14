"""Render a `ground_check.py --json` report in plain words. Computes NO verdict.

    uv run python scripts/ground_check.py --draft D.md --store S.jsonl --json | \
        uv run python scripts/explain_report.py
    uv run python scripts/explain_report.py report.json

Per claim: verdict, the full claim text, the engine's own reason (evidence_basis)
and a one-line fix hint per verdict (from docs/ALPHA-TESTER-GUIDE.md, "What to do
about each verdict"). NON_CLAIM lines are listed apart as "not scored".
Exit 0 if the report's gate is PASS, else 1 (so scripts can branch on it).
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap

FIX_HINTS: dict[str, str] = {
    "UNCITED": "Add [Sn] inside the sentence, before the full stop. For a heading or "
               "table, see the guide's 'What counts as a claim'.",
    "UNVERIFIED_CITATION": "Retrieve the source in-session, or fix the id. In a "
                           "hand-built store, add the line with scripts/add_source.py.",
    "UNGROUNDED": "Replace the claim with the source's own sentence and cite it. "
                  "This is not evidence the claim is false.",
    "UNVERIFIED_NUMBER": "Copy the figure as the source writes it, or cite the "
                         "source that has it.",
    "UNGROUNDABLE": "Re-fetch with Exa or Read. If the source is verbatim and "
                    "non-empty, cite the full source document, not an excerpt.",
    "UNVERIFIED_ABSENCE": "Quote a source that says it, or soften the claim.",
    "UNVERIFIED_RELATION": "Quote a source that says it, or soften the claim.",
}
_WIDTH = 88


def _wrap(prefix: str, text: str) -> str:
    return textwrap.fill(" ".join(text.split()), width=_WIDTH, initial_indent=prefix,
                         subsequent_indent=" " * len(prefix))


def render(report: dict[str, object]) -> str:
    """Return the readable text for *report*. Pure; reads fields, decides nothing."""
    per_claim = report["per_claim"]
    assert isinstance(per_claim, list)
    scored = [c for c in per_claim if c["kind"] != "NON_CLAIM"]
    unscored = [c for c in per_claim if c["kind"] == "NON_CLAIM"]
    out = [f"gate: {report['gate']} | score: {report['grounding_score']} | "
           f"scored claims: {report.get('scored_claims', len(scored))}",
           _wrap("scope: ", str(report.get("scope", ""))), ""]
    for c in scored:
        out.append(f"[{c['index']}] {c['verdict']}")
        out.append(_wrap("    claim: ", c["text"]))
        out.append(_wrap("    why:   ", c["evidence_basis"]))
        hint = FIX_HINTS.get(c["verdict"])
        if hint is not None:
            out.append(_wrap("    fix:   ", hint))
        out.append("")
    if unscored:
        out.append("not scored (headings and other non-claims):")
        out.extend(_wrap(f"  [{c['index']}] ", c["text"]) for c in unscored)
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="explain_report",
        description="Explain a ground_check --json report. Exit 0 iff gate is PASS.")
    parser.add_argument("report", nargs="?", metavar="REPORT.json",
                        help="Report file; omit to read stdin.")
    args = parser.parse_args()
    raw = open(args.report, encoding="utf-8").read() if args.report else sys.stdin.read()
    try:
        report = json.loads(raw)
        if not {"gate", "grounding_score", "per_claim"} <= set(report):
            raise ValueError("missing gate / grounding_score / per_claim")
    except (ValueError, TypeError) as exc:
        print(f"REFUSED: input is not a ground_check --json report ({exc}). "
              "Pipe the output of ground_check.py --json.", file=sys.stderr)
        sys.exit(1)
    sys.stdout.write(render(report))
    sys.exit(0 if report["gate"] == "PASS" else 1)


if __name__ == "__main__":
    main()
