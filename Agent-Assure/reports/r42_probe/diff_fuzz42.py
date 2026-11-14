"""R42 side-by-side differential fuzzer: bce1ac7 (branch, scripts/ground_check.py) vs origin/main
(/private/tmp/claude-501/ovn1115-r42/gc_main.py), each through its OWN main() with --json.

Extends reports/r41_probe/diff_fuzz.py (its multi-source / self-source / near-copy source kinds are reused
unchanged) with a 'denial_ctx' source kind: the claim sentence embedded in random structure drawn from
R40/R40b-relevant pools -- FAQ headings carrying R40-only falsity shapes, markdown headings inside a paragraph,
forward-pointing denials of 7-24 tokens, event negations (took place / occur, pointing and non-pointing
subjects, with and without adjuncts), trailing falsity, look-alike / invisible characters.

Usage: uv run python reports/r42_probe/diff_fuzz42.py <seed> <n>
Prints one JSON summary line then examples. branch_better must be 0.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r41", str(HERE.parent / "r41_probe" / "diff_fuzz.py"))
# r41 loads its base module from a fixed path; repoint before exec.
src = (HERE.parent / "r41_probe" / "diff_fuzz.py").read_text()
src = src.replace("/private/tmp/claude-501/ovn1115-r41/gc_main.py", "/private/tmp/claude-501/ovn1115-r42/gc_main.py")
src = src.replace("AA = Path(__file__).resolve().parents[2]", f"AA = Path({str(HERE.parents[1])!r})")
r41 = type(sys)("r41")
r41.__file__ = str(HERE / "_r41_embedded.py")
sys.modules["r41"] = r41
exec(compile(src, "r41_embedded", "exec"), r41.__dict__)

HEADINGS = [
    "## Facts and costs we fabricate", "## Fact vs fabricating", "## Truth or fabricating", "## Myths and facts",
    "## Facts and figures", "## Myths vs facts: apocryphal", "## Facts and costs, falsified", "## Rumours and facts",
    "## Wrong claims", "## False claims", "## Lies about the bank", "## Lie groups", "## Results", "# Notes",
    "### The facts", "### Installation", "**Myths**", "Myths about the bank", "More", "## Fake news",
    "## Facts and trumped up", "## Facts or falsely claimed", "## Real or fabricates", "## Facts and costs we fabricate.",
    "## What went wrong", "# Acme Stumbles", "## Facts & fabricating", "## Truth and things we fabricate",
]
POINTING = [
    "We do not believe the next short part.", "We do not believe the next part.",
    "None of the figures in the next section are accurate.", "None of the numbers below are accurate.",
    "Nothing in the next section is true.", "What comes after is untrue.", "We dispute the following.",
    "Not one of the items in the next list was verified by anyone at all.",
    "We checked each of the items below and not one of them holds up.",
    "This page does not list every case, and the figures below are not final or verified by anyone.",
    "None of the reports this page collected from the forums last winter is accurate.",
    "We do not believe the next short part of this long internal memo about costs.",
]
EVENT = [
    "The launch never took place in May.", "It never took place.", "The collapse never took place.",
    "The tale I tell did not occur.", "That never took place last year.", "None of it took place.",
    "The event did not occur in 2024.", "This did not occur.", "The audit did not occur last year.",
    "Funding ended this year, so the wave never took place in May.", "The merger never took place because funding ended.",
    "The meeting never takes place on time.", "It did not take place as described.", "The story never took place.",
    "The planned follow-up wave never took place.", "Things never took place here.", "The data migration never took place.",
    "Nothing occurs.", "None of this occurs in practice.",
]
TRAIL = [", which is a myth", " (fabricated)", "; none of it is true", ", a complete fabrication", ", dispelling the myth of safety",
         ", which never took place", ", which did not occur in May", ""]
CONF = {"a": "ɑ", "i": "ı", "o": "о", "e": "е"}


def perturb(rng: random.Random, s: str) -> str:
    r = rng.random()
    if r < 0.08:
        k = rng.randrange(len(s))
        return s[:k] + "​" + s[k:]
    if r < 0.16:
        ch = rng.choice(list(CONF))
        return s.replace(ch, CONF[ch], 1)
    if r < 0.20:
        k = rng.randrange(len(s))
        return s[:k] + "­" + s[k:]
    return s


def denial_ctx(rng: random.Random, t0: str) -> str:
    pool = [lambda: rng.choice(HEADINGS), lambda: rng.choice(POINTING), lambda: rng.choice(EVENT),
            lambda: rng.choice(r41.FILL)]
    before = [perturb(rng, rng.choice(pool)()) for _ in range(rng.randint(0, 4))]
    after = [perturb(rng, rng.choice(pool)()) for _ in range(rng.randint(0, 3))]
    claim = t0 + rng.choice(TRAIL) + "."
    parts = before + [claim] + after
    out = parts[0]
    for p in parts[1:]:
        out += rng.choice(["\n", "\n", "\n\n", " "]) + p
    return out


_orig_source = r41.source


def source(rng: random.Random, sid: str, claims, plain: str) -> dict:
    if rng.random() < 0.6:
        t0, _, _ = rng.choice(claims)
        t0 = r41.mutate_fig(rng, t0, claims) if rng.random() < 0.1 else t0
        return {"source_id": sid, "url": f"https://e.com/{sid}", "file_path": None,
                "fetched_at": "2026-11-15T00:00:00Z", "tool": "mcp__exa__web_fetch_exa", "content_sha256": None,
                "text": denial_ctx(rng, t0), "full_text_source": "verbatim", "captured_via": "inline",
                "query_provenance": "R42", "retrieval_status": "", "read_extent": "", "_kind": "denial_ctx"}
    return _orig_source(rng, sid, claims, plain)


r41.source = source

if __name__ == "__main__":
    r41.main()
