"""REASONS-FOR-REFUSAL differential fuzzer: this branch vs origin/main 7d2da1b, through each module's own main().

Usage: uv run python reports/refusal_probe/diff_fuzz.py <seed> <n>
Base copy: git show origin/main:Agent-Assure/scripts/ground_check.py > /private/tmp/claude-501/ovn1115-q8/gc_main.py

Built on reports/r41_probe/diff_fuzz.py (same in-process main() runner, so CLI wiring incl. self_source_ids and
inferred_self_ids is exercised) with a grammar aimed at the code this change touches: verbatim copies of source
sentences placed next to every denial / hedge / heading / label shape of reports/r38_probe/fuzz3.py, ", and" joins
that the splitter cuts, "N percent" figures, mutated copies, and r41's summary / failed / near-copy store records.

The change is display-only, so the required result is: verdict_diff == gate_diff == score_diff == kind_diff ==
claimcount_diff == 0. Also counted: rows that carry a new verbatim_but_* code (must all be UNGROUNDED) and crashes.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import random
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

AA = Path(__file__).resolve().parents[2]
WORK = Path("/private/tmp/claude-501/ovn1115-q8/work")


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


B = load("gc_branch", str(AA / "scripts" / "ground_check.py"))
M = load("gc_base", "/private/tmp/claude-501/ovn1115-q8/gc_main.py")

TMP = Path(tempfile.mkdtemp(prefix="rfr-fz-"))
DRAFT = TMP / "draft.md"
STORE = TMP / "store.jsonl"

BASES = [p.read_text(encoding="utf-8") for p in sorted(WORK.glob("s*-*.txt"))]
BASE_SENTS = [s for t in BASES for s in re.split(r"(?<=[.?!])\s+", t) if len(s.split()) >= 3]
DENIALS = ["None of this is true.", "This never happened.", "The story was fabricated.", "That is made up.",
           "Pure fantasy.", "It is a fairy tale.", "What follows never happened.", "It is false.", "Not true.",
           "Lies.", "No.", "Debunked.", "The board is made up of rumours.", "This did not affect depositors.",
           "None of this changed the outcome.", "There is no evidence for any of this.", "Not one bit of this is true.",
           "Of these, no more than five may be audio-visual items.", "This is not how it works in the release.",
           "The figures were made up.", "When the strict flag is false, the parser accepts trailing commas.",
           "Prosecutors said the invoices were fabricated.", "None of the following is true.",
           "Every word of this page is invented.", "No rollback was needed.", "Customers could not complete purchases."]
PREFIXES = ["Critics argued that ", "According to the vendor, ", "It is not true that ", "Our own benchmark has shown that ",
            "If the gateway fails, ", "Nobody, after a long and careful discussion by the board, agreed that ",
            "The team found that ", "Some say ", "Without question, ", ""]
SRC_HEADS = ["", "## Myths about the bank", "Rumours found to be false", "## Results", "Made up stories", "## Myths and facts",
             "## Fact or fiction", "How the committee is made up", "## Fiction", "Common myths:", "## Rumours debunked"]
DRAFT_HEADS = ["", "# Summary", "# Meeting notes", "## Results", "# Q3 sales summary", "## Limits", "# Incident summary"]
PCT = ["3.1 percent", "9 percent", "61 percent", "4.0 percent", "12%", "40 per cent", "100 percent"]
FIGS = ["2.1 million", "16,500", "3,900", "9,300", "forty", "twenty", "five", "47", "14:03"]


def source_text(rng: random.Random) -> tuple[str, list[str]]:
    """A source built from walkthrough sentences with denial/hedge/heading/label context. Returns (text, sentences
    a draft may copy)."""
    paras: list[str] = []
    copyable: list[str] = []
    hostility = rng.choice([0.0, 0.0, 0.1, 0.3, 0.6])  # share of non-plain sentences
    for _ in range(rng.randint(1, 4)):
        sents: list[str] = []
        for _ in range(rng.randint(1, 4)):
            r = rng.random()
            if r >= hostility:
                s = rng.choice(BASE_SENTS)
            elif r < hostility * 0.35:
                b = rng.choice(BASE_SENTS)
                s = rng.choice(PREFIXES) + b[0].lower() + b[1:]
            elif r < hostility * 0.8:
                s = rng.choice(DENIALS)
            else:
                s = f"Customer churn fell to {rng.choice(PCT)} from {rng.choice(PCT)} in the second quarter."
            if rng.random() < 0.15:
                s = s.rstrip(".") + ", and the limit can be changed without restarting the scheduler."
            sents.append(s)
            copyable.append(s)
        if rng.random() < hostility * 0.4:
            items = "\n".join("- " + rng.choice(BASE_SENTS).rstrip(".") for _ in range(rng.randint(1, 3)))
            paras.append(rng.choice(["Myths:", "Common myths:", "Facts:", "Here are the rumours that circulated:"]) + "\n" + items)
            copyable.extend(line[2:] + "." for line in items.split("\n"))
        paras.append(rng.choice([" ", "\n"]).join(sents))
        h = rng.choice(SRC_HEADS)
        if h and rng.random() < hostility:
            paras.append(h)
    rng.shuffle(paras)
    return "\n\n".join(paras), copyable


def mutate(rng: random.Random, s: str) -> str:
    r = rng.random()
    if r < 0.25:
        return s
    if r < 0.4:
        for f in FIGS + PCT:
            if f in s:
                return s.replace(f, rng.choice(FIGS + PCT), 1)
    if r < 0.55:
        w = s.split()
        if len(w) > 4:
            del w[rng.randrange(len(w))]
            return " ".join(w)
    if r < 0.65:
        return s.replace(" is ", " is not ", 1).replace(" was ", " was not ", 1)
    if r < 0.75:
        return s.replace(", and", " and", 1)
    return s


def build(rng: random.Random):
    nsrc = rng.choice([1, 1, 1, 2, 3])
    ids = [f"S{i}" for i in range(1, nsrc + 1)]
    texts, pools = zip(*(source_text(rng) for _ in ids))
    lines: list[str] = []
    h = rng.choice(DRAFT_HEADS)
    if h and rng.random() < 0.4:
        lines.append(h)
    for _ in range(rng.choice([1, 1, 2, 3, 5])):
        k = rng.randrange(nsrc)
        s = rng.choice(pools[k]).strip()
        if rng.random() < 0.15:
            s = s.rstrip(".") + ", and " + rng.choice(pools[k]).strip()[0].lower() + rng.choice(pools[k]).strip()[1:]
        s = mutate(rng, s) if rng.random() < 0.35 else s
        s = s.rstrip(".?!")
        mk = rng.random()
        marker = (f" [{ids[k]}]" if mk < 0.75 else f" [{ids[k]}][{rng.choice(ids)}]" if mk < 0.85
                  else " [S9]" if mk < 0.9 else "")
        lines.append(s + marker + rng.choice([".", ".", ".", "?"]))
    draft = rng.choice(["\n\n", "\n", " "]).join(lines) + "\n"
    recs = []
    for sid, text in zip(ids, texts):
        kind = rng.choices(["verbatim", "summary", "failed", "empty", "nearcopy"], [80, 5, 5, 3, 7])[0]
        tool, fts, status, fp, extent = "mcp__exa__web_fetch_exa", "verbatim", rng.choice(["", "ok"]), None, ""
        if kind == "summary":
            tool, fts = "WebFetch", "haiku_summary"
        elif kind == "failed":
            status = "failed"
        elif kind == "empty":
            text = ""
        elif kind == "nearcopy":
            tool, text, extent = "Read", re.sub(r"\[S\d+\]", "", draft), rng.choice(["", "whole", "partial"])
        recs.append({"source_id": sid, "url": None if tool == "Read" else f"https://e.com/{sid}", "file_path": fp,
                     "fetched_at": "2026-11-15T00:00:00Z", "tool": tool,
                     "content_sha256": hashlib.sha256(text.encode()).hexdigest(), "text": text,
                     "full_text_source": fts, "captured_via": "inline", "query_provenance": "refusal fuzz " + sid,
                     "retrieval_status": status, "read_extent": extent})
    return draft, recs


def run(mod) -> dict | str:
    argv = sys.argv
    sys.argv = ["ground_check", "--draft", str(DRAFT), "--store", str(STORE), "--json"]
    buf, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            mod.main()
    except SystemExit:
        pass
    except Exception as e:  # noqa: BLE001 -- a crash is a finding, recorded not swallowed
        return f"CRASH:{type(e).__name__}:{str(e)[:80]}"
    finally:
        sys.argv = argv
    out = buf.getvalue()
    if not out:
        return "REFUSED_INPUT:" + err.getvalue().strip()[:80]
    return json.loads(out)


def main() -> None:
    seed, n = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    c: Counter = Counter()
    codes: Counter = Counter()
    ex: dict = {}
    for _ in range(n):
        draft, recs = build(rng)
        DRAFT.write_text(draft, encoding="utf-8")
        STORE.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
        rb, rm = run(B), run(M)
        if isinstance(rb, str) or isinstance(rm, str):
            same = isinstance(rb, str) and isinstance(rm, str) and rb.split(":")[0] == rm.split(":")[0]
            c["nonreport_same" if same else "nonreport_DIFF"] += 1
            if not same or rb.startswith("CRASH"):
                ex.setdefault(("NONREPORT", str(rb)[:60], str(rm)[:60]), (draft, recs))
            continue
        c["n"] += 1
        diff = []
        if rb["gate"] != rm["gate"]:
            diff.append("gate")
        if rb["grounding_score"] != rm["grounding_score"]:
            diff.append("score")
        if (rb["scored_claims"], rb["vacuous"]) != (rm["scored_claims"], rm["vacuous"]):
            diff.append("scored")
        if len(rb["per_claim"]) != len(rm["per_claim"]):
            diff.append("claimcount")
        for pb, pm in zip(rb["per_claim"], rm["per_claim"]):
            c["claims"] += 1
            if pb["verdict"] != pm["verdict"]:
                diff.append("verdict")
            if pb["kind"] != pm["kind"]:
                diff.append("kind")
            if pb["text"] != pm["text"]:
                diff.append("text")
            code = pb.get("support_diagnostic", "")
            if code.startswith("verbatim_but_"):
                codes[code] += 1
                if pb["verdict"] != "UNGROUNDED":
                    diff.append("code_on_non_ungrounded")
            if pb["verdict"] == "UNGROUNDED":
                c["ungrounded_rows"] += 1
            if pb["evidence_basis"] != pm["evidence_basis"]:
                c["basis_changed_rows"] += 1
        if [a["verdict"] for a in rb["retained_appendix"]] != [a["verdict"] for a in rm["retained_appendix"]]:
            diff.append("appendix")
        for d in sorted(set(diff)):
            c[d + "_diff"] += 1
            ex.setdefault((d,), (draft, recs, [p["verdict"] for p in rb["per_claim"]],
                                 [p["verdict"] for p in rm["per_claim"]]))
        c["gate_" + rb["gate"]] += 1
    print(json.dumps({"seed": seed, **dict(c), "codes": dict(codes)}))
    for k, v in ex.items():
        print(json.dumps(k), "|", json.dumps(v, default=str)[:900])


if __name__ == "__main__":
    main()
