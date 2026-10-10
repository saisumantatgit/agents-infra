"""Score the 2026-09-12 intra-rater round.

WHY THE SAMPLE IS NOT A PLAIN RANDOM DRAW
-----------------------------------------
The 52 gold labels were not produced by blind labelling. `init_labels.py` seeds
every row with Claude's `candidate_verdict` and the ratifier corrects it, so on
48 of 52 rows gold == candidate. On those rows "Sai agrees with himself" and
"Sai agrees with the machine" are the SAME observation, and no amount of them
separates the two.

Only 4 rows carry that information -- q14, q16, q37, q49, where the ratifier
overruled the candidate. A random draw of 20 misses all four with probability
0.133, and the first draw did exactly that. The instrument would have been
blind to the branch it was built to detect.

So the sample is stratified: all 4 divergent rows + 16 random from the other 48.
The enrichment is deliberate and it BIASES any pooled statistic, which is why
nothing here pools them. Kappa is computed on the 16 random rows alone; the 4
divergent rows are reported one by one.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent
ANSWER_TO_LABEL = {"yes": "grounded", "no": "violation"}


@dataclass(frozen=True)
class Row:
    claim_id: str
    gold: str
    candidate: str
    stratum: str
    answer: str


def cohen_kappa(pairs: tuple[tuple[str, str], ...]) -> float:
    """Cohen's kappa for two raters over a binary nominal scale.

    Raises on an empty input rather than returning a misleading 0.0 -- a
    calibration number with no observations behind it is the failure mode this
    project keeps finding in its own instruments.
    """
    if not pairs:
        raise ValueError("cohen_kappa: no observations")
    n = len(pairs)
    observed = sum(1 for a, b in pairs if a == b) / n
    cats = {c for pair in pairs for c in pair}
    expected = sum(
        (sum(1 for a, _ in pairs if a == c) / n) * (sum(1 for _, b in pairs if b == c) / n)
        for c in cats
    )
    if expected == 1.0:
        raise ValueError(
            "cohen_kappa: both raters used a single category for every item; "
            "kappa is undefined, not zero"
        )
    return (observed - expected) / (1 - expected)


def parse_answers(text: str) -> dict[str, str]:
    """Parse the block the instrument page produces. Fails loud on anything else."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"\s*\d+\s+(q\d+#\d+)\s+(yes|no)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
        elif line.strip() and not line.startswith("INTRA-RATER"):
            raise ValueError(f"unparseable line in answer block: {line!r}")
    if not out:
        raise ValueError("answer block contained no answers")
    return out


def load_rows(answers: dict[str, str]) -> tuple[Row, ...]:
    key = json.loads((HERE / "KEY-2026-09-12.json").read_text())["key"]
    missing = {k["claim_id"] for k in key} - set(answers)
    if missing:
        raise ValueError(f"answers missing for {sorted(missing)}")
    return tuple(
        Row(k["claim_id"], k["gold"], k["candidate_verdict"], k["stratum"],
            ANSWER_TO_LABEL[answers[k["claim_id"]]])
        for k in key
    )


def report(rows: tuple[Row, ...]) -> str:
    rand = tuple(r for r in rows if r.stratum == "random")
    div = tuple(r for r in rows if r.stratum == "divergent")

    k = cohen_kappa(tuple((r.gold, r.answer) for r in rand))
    agree = sum(1 for r in rand if r.gold == r.answer)

    # On a divergent row, gold != candidate. So a re-label that lands on the
    # candidate is a move TOWARD the machine, and that is the anchoring signal.
    toward_machine = [r for r in div if r.answer == r.candidate]

    lines = [
        "# Intra-rater round — 2026-09-12",
        "",
        f"**Random stratum (n={len(rand)}, unbiased):** agreement "
        f"{agree}/{len(rand)} = {agree / len(rand):.1%}, Cohen's κ = **{k:+.3f}**",
        "",
        "## The four anchoring-probe rows, individually (never pooled)",
        "",
        "| row | machine candidate | gold (then) | now | lands on |",
        "|---|---|---|---|---|",
    ]
    for r in div:
        lands = "the machine" if r.answer == r.candidate else "his own gold"
        lines.append(f"| {r.claim_id} | {r.candidate} | {r.gold} | {r.answer} | **{lands}** |")

    lines += ["", "## Branch", ""]
    if k > 0.8 and len(toward_machine) <= 1:
        lines.append(
            "**Corpus is sound.** He reproduces his own judgment, and the rows "
            "where he overruled the machine he overrules again. The inter-rater "
            "failure was the reader population. Next: recruit ONE "
            "domain-competent reader; Alpha criterion #5 is reachable."
        )
    elif len(toward_machine) >= 3:
        lines.append(
            f"**Anchoring.** {len(toward_machine)} of {len(div)} rows where he "
            "once overruled the machine now land on the machine's original "
            "call. The gold labels are not independent of the gate's own "
            "output, so every rate calibrated against them is partly circular. "
            "This is more serious than an ambiguous corpus and it invalidates "
            "the corpus as ground truth, not merely its precision."
        )
    elif k > 0.8:
        lines.append(
            f"**Indeterminate — do not conclude.** κ = {k:+.3f} says he "
            f"reproduces himself on ordinary rows, but {len(toward_machine)} of "
            f"{len(div)} probe rows moved to the machine's call. That is too few "
            "to call anchoring and too many to call clean. The honest next step "
            "is to enlarge the probe: re-label the remaining divergent rows the "
            "corpus can supply, or accept that this instrument cannot separate "
            "the branches at n=4."
        )
    elif not toward_machine:
        lines.append(
            f"**Anchoring refuted; self-agreement below the bar.** All "
            f"{len(div)} probe rows landed on his own gold, AGAINST the machine "
            f"— the labels are not a mirror of the gate's output. But κ = "
            f"{k:+.3f} on the unbiased stratum is under 0.8, so some items are "
            "not being judged consistently. **Do not stop at the κ: find out "
            "WHICH rows moved and whether they share a property.** If they do, "
            "the corpus is mixed rather than ambiguous, and mixed is fixable."
        )
    else:
        lines.append(
            f"**Indeterminate.** κ = {k:+.3f} and {len(toward_machine)} of "
            f"{len(div)} probe rows moved toward the machine. Neither the "
            "anchoring nor the ambiguity reading is supported. Report the rows "
            "individually and do not summarise."
        )
    return "\n".join(lines)


def _self_check() -> None:
    """Hand-computed kappa, so the reported number is not the only witness to itself."""
    # 10 items: 7 agree. Rater A: 6 grounded / 4 violation. Rater B: 5 / 5.
    pairs = (("grounded", "grounded"),) * 4 + (("violation", "violation"),) * 3 \
        + (("grounded", "violation"),) * 2 + (("violation", "grounded"),)
    # po = 7/10 = 0.70 ; pe = 0.6*0.5 + 0.4*0.5 = 0.50 ; k = 0.2/0.5 = 0.40
    got = cohen_kappa(pairs)
    assert abs(got - 0.40) < 1e-12, got
    for bad in ((), (("grounded", "grounded"),) * 5):
        try:
            cohen_kappa(bad)
        except ValueError:
            continue
        raise AssertionError(f"cohen_kappa accepted a degenerate input: {bad!r}")


if __name__ == "__main__":
    _self_check()
    blob = sys.stdin.read()
    if not blob.strip():
        print("Paste the answer block on stdin.", file=sys.stderr)
        raise SystemExit(2)
    print(report(load_rows(parse_answers(blob))))
