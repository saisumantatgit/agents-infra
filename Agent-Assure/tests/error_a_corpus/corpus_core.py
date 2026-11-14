"""Framework for the Error-A corpus: honest drafts whose every claim is a verbatim
sentence (or table cell) of a source written for this corpus.

A `Piece` is one cited claim: `text` is exactly as it appears in the source (with
its final full stop dropped for sentences, as in tests/usage_genres), `shape` names
the honest everyday shape the claim exercises (so the baseline can attribute
refusals to shapes, not just to genres).
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Piece:
    text: str          # verbatim substring of the source, no trailing full stop
    shape: str


@dataclass
class Draft:
    id: str
    genre: str
    sources: dict[str, str]          # filename -> text
    body: str                        # draft markdown
    claims: list[Piece]              # cited claims, in draft order
    shapes: list[str] = field(default_factory=list)


def cite(text: str) -> str:
    """`Sentence text` -> `Sentence text [S1]` (marker inside, before the full stop)."""
    return f"{text} [S1]"


class Body:
    """Builds draft markdown while recording the cited claims in order."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.claims: list[Piece] = []

    def heading(self, level: int, text: str) -> None:
        self.lines += ["#" * level + " " + text, ""]

    def para(self, pieces: list[Piece]) -> None:
        self.claims += pieces
        self.lines += [" ".join(cite(p.text) + "." for p in pieces), ""]

    def bullets(self, pieces: list[Piece]) -> None:
        self.claims += pieces
        self.lines += [f"- {cite(p.text)}." for p in pieces] + [""]

    def numbered(self, pieces: list[Piece]) -> None:
        self.claims += pieces
        self.lines += [f"{i}. {cite(p.text)}." for i, p in enumerate(pieces, 1)] + [""]

    def table(self, header: list[str], rows: list[list[str | Piece]]) -> None:
        self.lines.append("| " + " | ".join(header) + " |")
        self.lines.append("|" + "|".join("---" for _ in header) + "|")
        for row in rows:
            cells = []
            for c in row:
                if isinstance(c, Piece):
                    self.claims.append(c)
                    cells.append(cite(c.text) + ".")
                else:
                    cells.append(c)
            self.lines.append("| " + " | ".join(cells) + " |")
        self.lines.append("")

    def code(self, lang: str, text: str) -> None:
        self.lines += [f"```{lang}", text.rstrip("\n"), "```", ""]

    def raw(self, text: str) -> None:
        self.lines += [text, ""]

    def text(self) -> str:
        return "\n".join(self.lines).rstrip("\n") + "\n"


def sentence(s: str, shape: str) -> Piece:
    """A source sentence ending in '.' becomes a Piece without the full stop."""
    if not s.endswith("."):
        raise ValueError(f"sentence must end with a full stop: {s!r}")
    return Piece(s[:-1], shape)


def norm(s: str) -> str:
    return " ".join(s.split())


def verify_verbatim(d: Draft) -> None:
    """Every cited claim must be a verbatim substring of some source (whitespace-folded)."""
    corpus = " ".join(norm(t) for t in d.sources.values())
    for p in d.claims:
        if norm(p.text) not in corpus:
            raise AssertionError(f"{d.id}: claim not verbatim in source: {p.text!r}")


class Slots(dict):
    """Per-draft slot values, consistent within a draft."""

    def __init__(self, rng: random.Random, banks: dict[str, list[str]]) -> None:
        super().__init__()
        for k, v in banks.items():
            self[k] = rng.choice(v)
        self["n"] = str(rng.randint(3, 48))
        self["m"] = str(rng.randint(120, 9800))
        self["p"] = str(rng.randint(6, 94))
        self["y"] = str(rng.randint(2019, 2026))
        self["k"] = str(rng.choice([2, 3, 4, 5, 6, 7, 8, 12]))
        self["pc"] = f"{self['p']}%" if rng.random() < 0.5 else f"{self['p']} percent"
        self["f"] = f"{rng.randint(1, 9)}.{rng.randint(1, 9)}"

    def fill(self, template: str) -> str:
        out = re.sub(r"\{(\w+)\}", lambda m: self[m.group(1)], template)
        return out[0].upper() + out[1:]


def pick(rng: random.Random, pool: list, k: int) -> list:
    k = min(k, len(pool))
    return rng.sample(pool, k)
