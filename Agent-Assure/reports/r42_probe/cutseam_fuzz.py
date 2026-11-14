"""R42 targeted fuzz for the cut-token seam (B1/B2): a heading that main's `_heading_line_denies` clears and
the branch's widened `_has_strong_denial` makes denying is no longer cut out of the welded sentence by
`_strong_tokens`, so (B1) a forward-pointing denial is pushed past `_SCOPE_MAX_TOKENS` or (B2) the code-value
exemption cancels main's predicative "is false". Both modules through main() (r41 harness `run`).
Usage: uv run python reports/r42_probe/cutseam_fuzz.py <seed> <n>"""
from __future__ import annotations
import json, random, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv_saved = list(sys.argv)
import importlib
sys.path.insert(0, str(HERE))
import diff_fuzz42 as F  # noqa: E402  (loads both modules once)
r41 = F.r41
HEADS = ["## Facts and costs we fabricate", "## Fact vs fabricating", "## Truth or fabricating", "## Why the launch never took place",
         "## The launch never took place", "## It never took place", "## How the account was cooked up", "## Apocryphal quotes",
         "## The hypothesis was falsified", "## The story was trumped up", "## When the event did not occur",
         "## None of it is real", "## Rivals falsely claimed solvency", "## Reporters called it false",
         "## Facts and flags we fabricate", "## Facts and flag values we fabricate", "## The tale did not occur",
         "## Why the merger did not occur", "## Myths and facts", "## Results", "## Facts and figures"]
POINT = ["We do not believe the next short part.", "None of the figures in the next section are accurate.",
         "Nothing in the next section is accurate.", "We do not believe the next part.", "Not one figure in the next list is correct.",
         "Is false.", "Is fake.", "None of the next section is verified.", "We could not confirm the next few lines."]
SECT = ["# Notes", "## Results", "## Notes", "### Details", ""]
CLAIMS = ["Revenue rose to 90000 dollars after the audit", "The regional bank lost 25000 customers in March",
          "The regulator fined Acme 25000 euros in June"]
FILL = ["Staff left.", "Records were filed.", "The board met twice.", "Officials declined to comment."]

def build(rng):
    c = rng.choice(CLAIMS)
    h, p, sec = rng.choice(HEADS), rng.choice(POINT), rng.choice(SECT)
    fills = " ".join(rng.sample(FILL, rng.randint(0, 3)))
    if rng.random() < 0.5:   # B1 layout: heading, pointing line, section heading, fillers, claim
        body = f"{h}\n{p}\n" + (sec + "\n" if sec else "") + (fills + " " if fills else "") + c + "."
    else:                    # B2 layout: fillers, claim, heading, line
        body = (fills + " " if fills else "") + c + ".\n" + h + "\n" + p
    return c, body

def main():
    seed, n = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed); cnt = Counter(); ex = {}
    for _ in range(n):
        c, body = build(rng)
        recs = [{"source_id": "S1", "url": "https://e.com/S1", "file_path": None, "fetched_at": "2026-11-15T00:00:00Z",
                 "tool": "mcp__exa__web_fetch_exa", "content_sha256": None, "text": body, "full_text_source": "verbatim",
                 "captured_via": "inline", "query_provenance": "R42", "retrieval_status": "", "read_extent": "", "_kind": "cut"}]
        r41.materialise(c + " [S1].\n", recs)
        rb, rm = r41.run(r41.B), r41.run(r41.M)
        if isinstance(rb, str) or isinstance(rm, str):
            cnt["nonreport"] += 1; continue
        cnt["n"] += 1
        vb, vm = rb["per_claim"][0]["verdict"], rm["per_claim"][0]["verdict"]
        if vb in r41.GOOD and vm not in r41.GOOD:
            cnt["branch_better"] += 1
            head = body.split("\n")[0] if body.startswith("#") else body.split("\n")[1]
            ex.setdefault(head, body)
        elif vm in r41.GOOD and vb not in r41.GOOD:
            cnt["branch_worse"] += 1
    print(json.dumps({"seed": seed, **cnt, "distinct_headings_better": len(ex)}))
    for k, v in ex.items():
        print(json.dumps(k), "|", json.dumps(v))

if __name__ == "__main__":
    main()
