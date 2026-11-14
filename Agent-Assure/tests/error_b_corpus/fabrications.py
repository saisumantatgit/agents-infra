"""Fabrication injectors for the Error-B corpus.

Every draft = the Error-A source document for that genre/index (reused verbatim) with one
appended block of corpus-authored text, plus an otherwise honest draft (two verbatim "plain"
claims from the Error-A draft, and verbatim sentences of the appended block) that carries
EXACTLY ONE fabrication. `Built.fabricated` is that segment exactly as it stands in the
draft (marker and full stop removed); `Built.honest` is the verbatim text it replaces in the
control draft, or None when the control simply omits it.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass

CLASSES = [
    "wrong_number", "wrong_unit_rate", "number_moved_subject", "unsupported_claim",
    "denied_adjacent", "denied_2back", "denied_3plus_back", "denied_same_sentence",
    "denied_heading", "denied_table_after", "claim_heading", "list_item_number",
    "table_cell", "swapped_entities", "misattributed_quote", "absence_claim",
    "causal_claim", "near_copy_padding",
]

MONTHS = ["March", "April", "June", "September", "October", "November"]
PEOPLE = ["Priya", "Tomas", "Ingrid", "Marcus", "Aiko", "Dev", "Lena", "Omar", "Beatrice", "Jun"]

# genre -> (things, entities, incident nouns)
PROFILES: dict[str, tuple[list[str], list[str], list[str]]] = {
    "product_docs": (["export queue", "shared workspace", "audit history", "reminder service", "import tool"],
                     ["Larkspur", "Quillboard", "Brightwell", "Tidepool", "Marlin Sync"], ["sync errors", "login failures"]),
    "readme": (["parser", "writer", "command line tool", "config loader", "cache layer"],
               ["reedly", "tallyman", "cinderlog", "pebblecache", "gridsnap"], ["crashes", "build failures"]),
    "faq": (["trash folder", "export page", "mobile app", "sharing link", "refund desk"],
            ["Tallyboard", "Cobble", "Nimbus Pay", "Wrenfield", "Plover"], ["complaints", "outages"]),
    "incident": (["checkout service", "primary database", "queue broker", "status page", "report builder"],
                 ["Harbour Pay", "Kestrel Mail", "Fenwick Notes", "Orchard Desk", "Saltmarsh Planner"], ["outages", "failed deploys"]),
    "meeting_notes": (["pilot", "migration plan", "vendor contract", "design review", "budget review"],
                      ["the harbour app", "the onboarding revamp", "the partner portal", "the data migration", "the pricing review"], ["delays", "blockers"]),
    "news_brief": (["harbour fund", "bus route", "library roof", "market hall", "river wall"],
                   ["Northbank Council", "Eastgate Library", "Millfield School", "Riverside Market", "Quay Trust"], ["accidents", "complaints"]),
    "hr_policy": (["leave allowance", "training budget", "travel fund", "review cycle", "relocation grant"],
                  ["the people team", "Northgate Group", "the finance team", "Brightside Ltd", "the legal team"], ["grievances", "appeals"]),
    "api_reference": (["export endpoint", "webhook queue", "search index", "upload service", "rate limiter"],
                      ["Harbor API", "Kestrel gateway", "Nimbus SDK", "Quill service", "Larkspur client"], ["timeouts", "server errors"]),
    "changelog": (["importer", "scheduler", "build cache", "plugin loader", "update checker"],
                  ["Pinecone", "Tidepool", "Foldkit", "Driftq", "Mothlight"], ["regressions", "crashes"]),
    "code_review": (["retry loop", "session cache", "request handler", "migration script", "token parser"],
                    ["the auth module", "the billing module", "the search module", "the upload module", "the report module"], ["test failures", "rollbacks"]),
    "howto_code": (["setup script", "sample project", "local server", "test runner", "build step"],
                   ["Wickerdb", "Quillparse", "Gridsnap", "Foldkit", "Driftq"], ["install failures", "timeouts"]),
    "research_summary": (["pilot study", "survey sample", "control group", "follow-up wave", "trial site"],
                         ["the Aldgate team", "the Marlow lab", "the Fenmoor group", "the Calder panel", "the Oakham cohort"], ["dropouts", "protocol breaches"]),
    "financial_report": (["retail division", "online store", "regional office", "loan book", "support centre"],
                         ["Acme Bank", "Larch Holdings", "Corvid Capital", "Redwater Group", "Pennant Trust"], ["write-offs", "late payments"]),
    "sales_report": (["north region", "partner channel", "enterprise team", "renewals desk", "trial funnel"],
                     ["Acme Corp", "Brightfield", "Cobalt Ltd", "Dunmore Inc", "Elmstead"], ["lost deals", "refunds"]),
}

UNSUPPORTED = [
    "{E} was fined {k}00 thousand dollars by the regulator in {M}",
    "{E} replaced its entire leadership team in {M}",
    "An outside auditor approved every {T} record in {M}",
    "The {T} was shut down for {n} days after a security breach",
    "{P} resigned over the handling of the {T}",
    "{E} was acquired by a larger rival last spring",
    "Engineers hid the failures of the {T} from customers",
    "The regulator found fraud at {E}",
    "{E} paid a ransom after the {T} was locked in {M}",
    "Investigators linked the {T} to a data leak at {E}",
]

HEADINGS = [
    "The regulator found fraud at {E}", "{E} guilty", "{E} Collapses", "Regulator: {E} lied",
    "{E} Stumbles", "{E} Folds", "{E} Under Investigation", "Fraud everywhere at {E}",
    "{E} chief arrest imminent", "{E} revenue doubles", "{E} found guilty of fraud", "{E} hid the failures",
]

DENIALS = [  # (text, has_back_reference)
    ("That never happened.", True), ("This is a myth.", True), ("None of this is true.", True),
    ("That is made up.", True), ("The story was fabricated.", False),
    ("Officials said the whole account is a myth.", False), ("It was all lies.", False),
    ("Pure fantasy.", False), ("The event did not occur.", False), ("It never took place.", True),
    ("That was cooked up by the press.", True), ("Untrue.", False),
]
FILL = ["Staff left early.", "Records were filed.", "Reporters waited outside.", "People talked.",
        "Some wrote letters.", "Others posted online.", "The room was busy.", "A clerk took notes."]
SAME_SENT_SUFFIX = [", which is a myth", " (fabricated)", " - a complete fabrication",
                    ", which never happened", ", a story that proved false", ", a rumour with no basis"]
QUOTES = ["is ready for wider use", "will stay in place until the end of the year",
          "was the team's top priority", "can be trusted by every group", "has been checked twice"]
ABSENCE_FORMS = ["The {T} logged no {I} during {M}", "There were no {I} on the {T} during {M}",
                 "The {T} recorded zero {I} during {M}", "{I} did not affect the {T} during {M}"]
RELATIONS = ["{A} handed the {T} to {B}", "{A} approved the request from {B}",
             "{A} replaced {B} as owner of the {T}", "{A} sent the summary to {B} on Friday"]
CAUSE_WORDS = ["because", "as a result of", "after", "driven by", "caused by"]


@dataclass
class Built:
    cls: str
    variant: str
    source_add: str            # text appended to the Error-A source
    draft: str
    control: str               # draft with the fabrication replaced by `honest` or omitted
    fabricated: str            # the fabricated segment, exactly as in `draft`
    honest: str | None
    in_source: bool            # True when `fabricated` is verbatim in the source (denied classes)
    occurrence: int = 0        # which occurrence (0-based) of `fabricated` in `draft` is the fabrication


def _cap(s: str) -> str:
    return s[0].upper() + s[1:]


def _sent(s: str) -> str:
    return s if s.endswith(".") else s + "."


def _cite(s: str) -> str:
    return f"{s} [S1]."


def _used_numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", text))


class Ctx:
    def __init__(self, rng: random.Random, genre: str, source: str, plain: list[str]) -> None:
        self.rng, self.genre, self.source = rng, genre, source
        self.used = _used_numbers(source)
        self.things, self.ents, self.incs = PROFILES[genre]
        self.plain = plain
        self.month = rng.choice(MONTHS)

    def num(self, lo: int = 11, hi: int = 97) -> int:
        for _ in range(500):
            v = self.rng.randint(lo, hi)
            if str(v) not in self.used:
                self.used.add(str(v))
                return v
        raise RuntimeError("no fresh number available")

    def distinct_pair(self) -> tuple[int, int]:
        """Two-digit value with distinct digits whose reversal is also fresh."""
        for _ in range(500):
            a, b = self.rng.randint(1, 9), self.rng.randint(1, 9)
            v, r = 10 * a + b, 10 * b + a
            if a != b and str(v) not in self.used and str(r) not in self.used:
                self.used.update({str(v), str(r)})
                return v, r
        raise RuntimeError("no transposable pair available")

    def things_n(self, n: int) -> list[str]:
        return self.rng.sample(self.things, n)


FACT_KINDS = ["count", "percent", "money", "duration", "rate"]


def fact(kind: str, t: str, e: str, v: int, pct_sign: bool = False, unit: str | None = None) -> str:
    if kind == "count":
        return f"The {t} holds {v} {unit or 'entries'}"
    if kind == "percent":
        return f"{_cap(e)} accounts for {v}{'%' if pct_sign else ' percent'} of the {t}"
    if kind == "money":
        return f"The {t} costs {v} {unit or 'dollars each month'}"
    if kind == "duration":
        return f"The {t} takes {v} {unit or 'minutes'} to complete"
    return f"The {t} handles {v} requests {unit or 'every minute'}"


UNIT_SWAP = {"count": ("entries", "gigabytes"), "money": ("dollars each month", "dollars each year"),
             "duration": ("minutes", "hours"), "rate": ("every minute", "every second")}


def _para(sentences: list[str], style: str) -> str:
    cited = [_cite(s) for s in sentences]
    return "\n".join(f"- {c}" for c in cited) if style == "bullets" else " ".join(cited)


def _drop(text: str, fab: str) -> str:
    """Control without the fabrication: drop its line when structural, else drop the sentence."""
    out = []
    for line in text.split("\n"):
        if fab in line:
            if line.startswith(("#", "|")):
                continue
            line = line.replace(_cite(fab), "").replace("  ", " ").strip()
            if line in ("", "-"):
                continue
        out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip("\n") + "\n"


def _assemble(blocks: list[str]) -> str:
    return "\n\n".join(b for b in blocks if b).strip("\n") + "\n"


def _intro(c: Ctx) -> str:
    return _para(c.plain[:2], "para")


def _inject(c: Ctx, honest_sents: list[str], fab: str, honest: str | None, style: str) -> tuple[str, str]:
    """Paragraph with the honest sentences and the fabricated one at a random position."""
    pos = c.rng.randint(0, len(honest_sents))
    with_fab = honest_sents[:pos] + [fab] + honest_sents[pos:]
    ctrl = honest_sents[:pos] + ([honest] if honest else []) + honest_sents[pos:]
    return _para(with_fab, style), _para(ctrl, style)


def build(cls: str, variant_idx: int, c: Ctx) -> Built:
    return BUILDERS[cls](c, variant_idx)


# ---------------------------------------------------------------- numeric classes
def _facts_block(c: Ctx, kinds: list[str]) -> tuple[str, list[tuple[str, str, int, str]]]:
    """(source paragraph, [(kind, thing, value, sentence)])"""
    ts = c.things_n(len(kinds))
    out = []
    for kind, t in zip(kinds, ts):
        v = c.num()
        out.append((kind, t, v, fact(kind, t, c.rng.choice(c.ents), v, pct_sign=c.rng.random() < 0.5)))
    return " ".join(_sent(s) for _, _, _, s in out), out


def b_wrong_number(c: Ctx, vi: int) -> Built:
    kind = ["count", "money", "duration", "rate"][vi % 4]   # percent lives in wrong_unit_rate
    para, fs = _facts_block(c, [kind, "count" if kind != "count" else "money", "duration" if kind != "duration" else "rate"])
    k, t, v, sent = fs[0]
    v2 = c.num()
    fab = sent.replace(str(v), str(v2), 1)
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [fs[1][3], fs[2][3]], fab, sent, style)
    return Built("wrong_number", k, para, _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), fab, sent, False)


def b_wrong_unit_rate(c: Ctx, vi: int) -> Built:
    mode = vi % 5
    if mode == 0:   # transposed percent: "58 percent" claimed as "85 percent"
        v, r = c.distinct_pair()
        sign = c.rng.random() < 0.5
        e, t = c.rng.choice(c.ents), c.things_n(1)[0]
        sent = fact("percent", t, e, v, sign)
        fab = fact("percent", t, e, r, sign)
        variant = "percent_transposed"
    else:
        kind = ["count", "money", "duration", "rate"][mode - 1]
        v = c.num()
        t = c.things_n(1)[0]
        a, b = UNIT_SWAP[kind]
        sent = fact(kind, t, "x", v, unit=a)
        fab = fact(kind, t, "x", v, unit=b)
        variant = f"unit_{kind}"
    other = fact("count", c.things_n(1)[0], "x", c.num())
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [other], fab, sent, style)
    return Built("wrong_unit_rate", variant, " ".join(_sent(s) for s in [sent, other]),
                 _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), fab, sent, False)


def b_moved(c: Ctx, vi: int) -> Built:
    kind = ["count", "money", "duration", "rate"][vi % 4]
    ta, tb = c.things_n(2)
    ea, eb = c.rng.sample(c.ents, 2)
    va, vb = c.num(), c.num()
    sa, sb = fact(kind, ta, ea, va), fact(kind, tb, eb, vb)
    fab = fact(kind, tb, eb, va)
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [sa], fab, sb, style)
    return Built("number_moved_subject", kind, f"{_sent(sa)} {_sent(sb)}", _assemble([_intro(c), body]),
                 _assemble([_intro(c), ctrl]), fab, sb, False)


# ---------------------------------------------------------------- unsupported / causal / absence
def _unsupported(c: Ctx) -> str:
    return c.rng.choice(UNSUPPORTED).format(E=c.rng.choice(c.ents), T=c.rng.choice(c.things), P=c.rng.choice(PEOPLE),
                                            M=c.month, n=c.rng.randint(3, 9), k=c.rng.randint(2, 9))


def b_unsupported(c: Ctx, vi: int) -> Built:
    other = fact("count", c.things_n(1)[0], "x", c.num())
    fab = _unsupported(c)
    style = ["para", "bullets"][vi % 2]
    body, ctrl = _inject(c, [other], fab, None, style)
    return Built("unsupported_claim", style, _sent(other), _assemble([_intro(c), body]),
                 _assemble([_intro(c), ctrl]), fab, None, False)


def b_causal(c: Ctx, vi: int) -> Built:
    t1, t2 = c.things_n(2)
    s1 = f"The {t1} rose in {c.month}"
    s2 = f"The {t2} fell in {c.month}"
    word = CAUSE_WORDS[vi % len(CAUSE_WORDS)]
    fab = f"The {t2} fell in {c.month} {word} the {t1} rising" if word in ("as a result of", "driven by", "caused by") \
        else f"The {t2} fell in {c.month} {word} the {t1} rose"
    style = c.rng.choice(["para", "bullets"])
    return Built("causal_claim", word, f"{_sent(s1)} {_sent(s2)}", _assemble([_intro(c), _para([s1, s2, fab], style)]),
                 _assemble([_intro(c), _para([s1, s2], style)]), fab, None, False)


def b_absence(c: Ctx, vi: int) -> Built:
    t, inc = c.rng.choice(c.things), c.rng.choice(c.incs)
    n = c.rng.randint(3, 9)
    while str(n) in c.used:
        n += 1
    c.used.add(str(n))
    src = f"The {t} logged {n} {inc} during {c.month}"
    form = ABSENCE_FORMS[vi % len(ABSENCE_FORMS)]
    fab = form.format(T=t, I=inc, M=c.month)
    other = fact("duration", c.things_n(1)[0], "x", c.num())
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [other], fab, src, style)
    return Built("absence_claim", f"form{vi % len(ABSENCE_FORMS)}", " ".join(_sent(s) for s in [src, other]),
                 _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), fab, src, False)


# ---------------------------------------------------------------- relational
def b_swapped(c: Ctx, vi: int) -> Built:
    a, b = c.rng.sample(PEOPLE, 2)
    t = c.rng.choice(c.things)
    rel = RELATIONS[vi % len(RELATIONS)]
    src = rel.format(A=a, B=b, T=t)
    fab = rel.format(A=b, B=a, T=t)
    other = fact("count", c.things_n(1)[0], "x", c.num())
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [other], fab, src, style)
    return Built("swapped_entities", f"rel{vi % len(RELATIONS)}", " ".join(_sent(s) for s in [src, other]),
                 _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), fab, src, False)


def b_quote(c: Ctx, vi: int) -> Built:
    p1, p2 = c.rng.sample(PEOPLE, 2)
    t1, t2 = c.things_n(2)
    q1, q2 = c.rng.sample(QUOTES, 2)
    s1 = f'{p1} said the {t1} "{q1}"'
    s2 = f'{p2} said the {t2} "{q2}"'
    fab = f'{p2} said the {t1} "{q1}"'
    style = c.rng.choice(["para", "bullets"])
    body, ctrl = _inject(c, [s2], fab, s1, style)
    return Built("misattributed_quote", "wrong_speaker", " ".join(_sent(s) for s in [s1, s2]),
                 _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), fab, s1, False)


# ---------------------------------------------------------------- denied classes
def _rumour(c: Ctx) -> str:
    return _unsupported(c)


def _denial(c: Ctx) -> str:
    return c.rng.choice(DENIALS)[0]


def _denied(c: Ctx, cls: str, source_add: str, rumour: str, variant: str) -> Built:
    style = c.rng.choice(["para", "bullets"])
    other = c.plain[2:3]
    body, ctrl = _inject(c, other, rumour, None, style)
    return Built(cls, variant, source_add, _assemble([_intro(c), body]), _assemble([_intro(c), ctrl]), rumour, None, True)


def b_denied_adjacent(c: Ctx, vi: int) -> Built:
    r, d = _rumour(c), _denial(c)
    before = vi % 2 == 0
    add = f"{d} {_sent(r)}" if before else f"{_sent(r)} {d}"
    return _denied(c, "denied_adjacent", add, r, "denial_before" if before else "denial_after")


def b_denied_2back(c: Ctx, vi: int) -> Built:
    r, d = _rumour(c), _denial(c)
    add = f"{d} {c.rng.choice(FILL)} {_sent(r)}"
    return _denied(c, "denied_2back", add, r, "one_filler")


def b_denied_3plus(c: Ctx, vi: int) -> Built:
    r, d = _rumour(c), _denial(c)
    nfill = 2 + vi % 3
    add = f"{d} {' '.join(c.rng.sample(FILL, nfill))} {_sent(r)}"
    return _denied(c, "denied_3plus_back", add, r, f"{nfill}_fillers")


def b_denied_same(c: Ctx, vi: int) -> Built:
    r = _rumour(c)
    suf = SAME_SENT_SUFFIX[vi % len(SAME_SENT_SUFFIX)]
    return _denied(c, "denied_same_sentence", _sent(r + suf), r, f"suffix{vi % len(SAME_SENT_SUFFIX)}")


def b_denied_heading(c: Ctx, vi: int) -> Built:
    r = _rumour(c)
    heads = ["## Rumours we investigated and found to be false", "### Lies the tabloids told",
             "**Claims we checked and found false**", f"## Myths about {c.rng.choice(c.ents)}"]
    h = heads[vi % len(heads)]
    nfill = vi % 4
    paras = " ".join(c.rng.sample(FILL, nfill)) if nfill else ""
    add = f"{h}\n\n{(paras + ' ') if paras else ''}{_sent(r)}"
    return _denied(c, "denied_heading", add, r, f"heading{vi % len(heads)}_fill{nfill}")


def b_denied_table(c: Ctx, vi: int) -> Built:
    r = _rumour(c)
    v = vi % 3
    if v == 0:      # key/value record, denial row after the claim row
        add = f"| Field | Value |\n|---|---|\n| Event | {r} |\n| Happened | No |"
        row_h, row = "| Field | Value |\n|---|---|", f"| Event | {_cite(r)} |"
    elif v == 1:    # same-row verdict cell after the claim
        add = f"| Claim | Month | Verified |\n|---|---|---|\n| {r} | {c.month} | False |"
        row_h, row = "| Claim | Month |\n|---|---|", f"| {_cite(r)} | {c.month} |"
    else:           # summary row below
        add = f"| Event | Detail |\n|---|---|\n| Report | {r} |\n| All rows above | | No |"
        row_h, row = "| Event | Detail |\n|---|---|", f"| Report | {_cite(r)} |"
    draft = _assemble([_intro(c), row_h + "\n" + row])
    return Built("denied_table_after", ["kv_row_below", "same_row_cell", "summary_row"][v], add, draft,
                 _assemble([_intro(c)]), r, None, True)


# ---------------------------------------------------------------- structure classes
def b_claim_heading(c: Ctx, vi: int) -> Built:
    h = HEADINGS[vi % len(HEADINGS)].format(E=c.rng.choice(c.ents))
    other = fact("count", c.things_n(1)[0], "x", c.num())
    body = _para(c.plain[:2] + [other], "para")
    return Built("claim_heading", f"heading{vi % len(HEADINGS)}", _sent(other),
                 _assemble([f"## {h}", body]), _assemble([body]), h, None, False)


def b_list_item(c: Ctx, vi: int) -> Built:
    if vi % 2 == 0:  # rank carried by the list number
        a, b, d = c.rng.sample(c.ents, 3)
        sa, sb, sd = (f"{x} reported losses this year" for x in (a, b, d))
        rank = f"Ranked by losses this year, {_cap(d)} came first, {b} second and {a} third"
        src = " ".join(_sent(s) for s in [sa, sb, sd, rank])
        fab = f"1. {sa}"
        honest = f"3. {sa}"
        draft = _assemble([_intro(c), f"{fab} [S1].\n- {_cite(sb)}"])
        control = _assemble([_intro(c), f"{honest} [S1].\n- {_cite(sb)}"])
        return Built("list_item_number", "rank", src, draft, control, fab, honest, False)
    n = c.rng.choice([9, 12, 24, 40])  # a count carried by the list number
    s = f"People lost access to the {c.rng.choice(c.things)} for a day"
    fab, honest = f"{n}. {s}", f"1. {s}"
    other = fact("count", c.things_n(1)[0], "x", c.num())
    return Built("list_item_number", "count", f"{_sent(s)} {_sent(other)}",
                 _assemble([_intro(c), f"{fab} [S1].\n- {_cite(other)}"]),
                 _assemble([_intro(c), f"{honest} [S1].\n- {_cite(other)}"]), fab, honest, False)


def b_table_cell(c: Ctx, vi: int) -> Built:
    kind = ["duration", "count", "money"][vi % 3]
    unit = {"duration": "minutes", "count": "entries", "money": "dollars"}[kind]
    ts = c.things_n(3)
    vals = [c.num() for _ in ts]
    rows = [(t, f"{v} {unit}") for t, v in zip(ts, vals)]
    src = "| Item | Value |\n|---|---|\n" + "\n".join(f"| {t} | {cell} |" for t, cell in rows)
    moved = vi % 2 == 1
    idx = c.rng.randrange(1, 3)   # row 0 is welded to the header by the splitter; keep the fabricated cell out of it
    honest = rows[idx][1]
    fab = rows[(idx + 1) % 3][1] if moved else f"{c.num()} {unit}"
    def table(cells: list[str]) -> str:
        lines = ["| Item | Value |", "|---|---|"]
        for (t, _), cell in zip(rows, cells):
            lines.append(f"| {t} | {_cite(cell)} |")
        return "\n".join(lines)
    cells = [r[1] for r in rows]
    bad = list(cells)
    bad[idx] = fab
    # the moved value stays unique in the draft only via its row; fabricated segment is the cell text
    occ = 1 if moved and (idx + 1) % 3 < idx else 0
    return Built("table_cell", "moved_from_other_row" if moved else "value_not_in_source", src,
                 _assemble([_intro(c), table(bad)]), _assemble([_intro(c), table(cells)]), fab, honest, False, occ)


def b_near_copy(c: Ctx, vi: int) -> Built:
    paras = [p for p in c.source.split("\n\n") if p.strip() and not p.lstrip().startswith(("#", "|", "`"))]
    sents = [s for s in re.split(r"(?<=\.)\s+", paras[0].strip()) if s.endswith(".")]
    sents = [s[:-1] for s in sents][:4]
    if len(sents) < 2:
        raise RuntimeError("source paragraph too short for near-copy")
    fab = _unsupported(c)
    pos = 1 if len(sents) < 3 else 1 + vi % 2
    with_fab = sents[:pos] + [fab] + sents[pos:]
    return Built("near_copy_padding", f"pos{pos}", "", _assemble([_para(with_fab, "para")]),
                 _assemble([_para(sents, "para")]), fab, None, False)


BUILDERS = {
    "wrong_number": b_wrong_number, "wrong_unit_rate": b_wrong_unit_rate, "number_moved_subject": b_moved,
    "unsupported_claim": b_unsupported, "denied_adjacent": b_denied_adjacent, "denied_2back": b_denied_2back,
    "denied_3plus_back": b_denied_3plus, "denied_same_sentence": b_denied_same, "denied_heading": b_denied_heading,
    "denied_table_after": b_denied_table, "claim_heading": b_claim_heading, "list_item_number": b_list_item,
    "table_cell": b_table_cell, "swapped_entities": b_swapped, "misattributed_quote": b_quote,
    "absence_claim": b_absence, "causal_claim": b_causal, "near_copy_padding": b_near_copy,
}
