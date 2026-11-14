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
# REASONS-FOR-REFUSAL (2026-11-15): when the claim WAS found verbatim and a
# named rule disowned the match, the UNGROUNDED hint ("replace the claim with
# the source's own sentence") is advice the author has already followed. These
# support_diagnostic codes get this hint instead. Must equal
# ground_check.VERBATIM_REFUSAL_CODES (pinned by tests/test_reason_names_denial.py).
_VERBATIM_REFUSAL_HINT = (
    "Your copy matched the source exactly; the 'why' line names the source words "
    "that made it not count. Copying it again will not help. Cite a different "
    "sentence that states the fact, or leave it out. If the named words plainly do "
    "not deny or hedge this sentence, it is a known over-refusal: please report it.")
VERBATIM_REFUSAL_CODES: frozenset[str] = frozenset({
    "verbatim_but_hedge_word_before_it",
    "verbatim_but_under_non_asserting_verb",
    "verbatim_but_under_disowning_label",
    "verbatim_but_after_denial_of_what_follows",
    "verbatim_but_paragraph_has_falsity_statement",
    "verbatim_but_under_denying_heading",
    "verbatim_but_denial_earlier_in_sentence",
    "verbatim_but_previous_sentence_denies",
    "verbatim_but_previous_line_denies",
    "verbatim_but_sentence_two_back_denies",
    "verbatim_but_next_sentence_says_false",
    "verbatim_but_previous_sentence_says_false",
    "verbatim_but_next_sentence_denies",
    "verbatim_but_source_sentence_negates_differently",
    "verbatim_but_negation_limited_in_source",
})
_WIDTH = 88


def fix_hint(claim: dict[str, object]) -> str | None:
    """The fix line for one per-claim row: the verbatim-refusal hint when its
    support_diagnostic is one of VERBATIM_REFUSAL_CODES, else the verdict's.
    Pure; decides nothing."""
    if claim.get("support_diagnostic") in VERBATIM_REFUSAL_CODES:
        return _VERBATIM_REFUSAL_HINT
    return FIX_HINTS.get(str(claim["verdict"]))


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
        hint = fix_hint(c)
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
