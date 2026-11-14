"""Technical and numeric genres: API reference, changelog, code review, how-to with code,
research summary, financial report, sales report. All text is original to this corpus."""
from __future__ import annotations

import random

from corpus_core import Body, Draft, Piece, Slots, pick, sentence
from genres_prose import Spec, assemble

API = Spec(
    "api_reference",
    banks={
        "res": ["invoices", "customers", "webhooks", "exports", "labels", "shipments"],
        "verb": ["list", "create", "archive", "fetch"],
        "field": ["status", "created_after", "limit", "cursor"],
        "unit": ["requests", "calls"],
    },
    title="API reference: {res}",
    neutral=[
        "The {res} endpoint returns JSON.",
        "Every request must carry an API key in the `Authorization` header.",
        "Responses include a `request_id` that support can look up.",
        "The `{field}` parameter is optional.",
        "Timestamps use the UTC time zone.",
        "Results are returned newest first.",
        "A page holds at most {n} items.",
        "Use the `cursor` value from one page to request the next.",
    ],
    neg=[
        ("The {res} endpoint supports filtering by `{field}`.", "It does not support filtering by free text."),
        ("Archived {res} remain readable.", "They cannot be modified once archived."),
        ("Keys can be rotated at any time.", "A rotated key stops working immediately and cannot be restored."),
        ("The server retries failed webhooks.", "It stops after {k} attempts unless the endpoint returns a success code."),
        ("Requests with a body must set a content type.", "Requests without one are rejected."),
    ],
    madeup=[
        "A page of results is made up of an `items` array and a `next_cursor` field.",
        "Every error body is made up of a code, a message and a request id.",
    ],
    quoted=[
        "The changelog says that the old `v1` path \"is not covered by the new limits\".",
    ],
    never=[
        "The beta `{field}` filter never left preview and is not documented here.",
    ],
    numbers=[
        "The rate limit is {m} {unit} per minute for each key.",
        "A `limit` above {n} is capped at {n}.",
        "Version {f} of the API is the current release.",
    ],
    headings=["Rate limits", "Error codes", "Query parameters", "Response fields", "Breaking changes"],
)


def _api_params(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    ps = pick(rng, [("limit", "No", "The number of items to return"), ("cursor", "No", "The position to continue from"),
                    ("status", "No", "Restricts results to one status"), ("api_key", "Yes", "Identifies the caller"),
                    ("customer_id", "Yes", "The customer that owns the resource"), ("expand", "No", "Includes related objects in the response")], 4)
    src += ["## Parameters", "", "| Name | Required | Description |", "|---|---|---|"]
    src += [f"| `{n}` | {r} | {d} |" for n, r, d in ps] + [""]
    body.heading(2, "Parameters")
    body.table(["Name", "Required", "Description"],
               [[f"`{n}`", Piece(r, "table_no_false" if r == "No" else "table_cell"), Piece(d, "table_cell")] for n, r, d in ps])


CHANGELOG = Spec(
    "changelog",
    banks={
        "prod": ["Fieldnote", "Cairn", "Lumen CLI", "Pylon", "Ferrule", "Tessel"],
        "area": ["importer", "scheduler", "settings screen", "search index", "exporter", "login flow"],
        "flag": ["strict_mode", "auto_retry", "legacy_sort", "compact_view"],
    },
    title="{prod} changelog, version {f}",
    neutral=[
        "Added a new {area} that loads in under a second.",
        "The {area} now shows the time of the last change.",
        "Fixed a crash that happened when a name contained an emoji.",
        "Improved the wording of {k} error messages.",
        "The installer now checks for free disk space first.",
        "Updated the bundled certificates.",
        "Documentation for the {area} has been rewritten.",
        "Startup is about {pc} faster on cold caches.",
    ],
    neg=[
        ("The `{flag}` setting is now on by default.", "It can still be turned off in the configuration file."),
        ("The old export format is still readable.", "It is no longer written."),
        ("The {area} keeps working offline.", "It cannot refresh until the network returns."),
        ("Support for version {k} has been removed.", "Upgrading does not delete existing data."),
        ("Scheduled jobs run as before.", "Jobs without an owner are skipped unless they are marked as shared."),
    ],
    madeup=[
        "This release is made up of {k} new features and {n} fixes.",
    ],
    quoted=[
        "The earlier note claimed the change \"does not alter stored data\", and testing confirmed it.",
    ],
    never=[
        "The long-requested dark theme for the {area} never made it into this release.",
        "The deprecated `{flag}` option never worked on the command line.",
    ],
    numbers=[
        "The release contains {n} commits from {k} contributors.",
        "The download is {m} KB smaller than the previous release.",
        "Support for the {f} series ends in {y}.",
    ],
    headings=["Bug fixes", "New features", "Known issues", "Breaking changes", "Deprecations", "Price rises"],
)


def _changelog_flags(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    flag = sl["flag"]
    s1 = f"Set `{flag}=False` to restore the old behaviour."
    s2 = "The setting is read at startup."
    code = f"[settings]\n{flag} = false"
    src += ["## Migration", "", s1 + " " + s2, "", "```toml", code, "```", ""]
    body.heading(2, "Migration")
    body.para([sentence(s1, "code_false"), sentence(s2, "plain")])
    body.code("toml", code)


CODE_REVIEW = Spec(
    "code_review",
    banks={
        "fn": ["parse_header", "load_rules", "flush_batch", "render_row", "sync_state", "build_index"],
        "mod": ["importer", "scheduler", "cache layer", "report writer", "auth helper"],
        "who": ["Nadia", "Pavel", "Greta", "Haruto", "Sofia"],
    },
    title="Review notes: {mod} change",
    neutral=[
        "The `{fn}` function now returns early when the input is empty.",
        "{who} split the {mod} into two files.",
        "The change adds {n} tests for the new branch.",
        "Variable names in `{fn}` follow the project style.",
        "The new loop runs once per record instead of once per field.",
        "Logging was moved to the top of the {mod}.",
        "The pull request touches {k} files.",
        "The error message now names the file that failed.",
    ],
    neg=[
        ("The retry logic handles timeouts.", "It does not handle connection resets."),
        ("`{fn}` validates its arguments.", "It does not check the encoding of the path."),
        ("The cache is cleared on startup.", "It is not cleared when the configuration reloads unless the reviewer asks for it."),
        ("The tests pass locally.", "They have not been run on the Windows runner."),
        ("The helper is safe to call twice.", "It cannot be called from a signal handler."),
    ],
    madeup=[
        "The test fixture is made up of {k} small files and one large archive.",
    ],
    quoted=[
        "{who} commented that the old loop \"is not thread safe\".",
    ],
    never=[
        "The planned rewrite of `{fn}` never landed in this pull request.",
    ],
    numbers=[
        "The new code removes {m} lines and adds {n}.",
        "Run time dropped from {n} seconds to {k} seconds in the benchmark.",
        "Coverage for the {mod} is now {pc}.",
    ],
    headings=["Review comments", "Open issues", "Test results", "Suggested changes", "Style notes"],
)


def _review_snippet(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    fn = sl["fn"]
    opt = rng.choice(["autoflush", "check_same_thread", "verify", "delete", "shell"])
    s1 = f"The call in `{fn}` passes `{opt}=False` on purpose."
    s2 = "A comment above it explains why."
    code = f"def {fn}(conn, rows):\n    conn.execute(rows, {opt}=False)"
    src += ["## Snippet", "", s1 + " " + s2, "", "```python", code, "```", ""]
    body.heading(2, "Snippet")
    body.para([sentence(s1, "code_false"), sentence(s2, "plain")])
    body.code("python", code)


HOWTO = Spec(
    "howto_code",
    banks={
        "tool": ["rsync", "git", "curl", "sqlite3", "tar", "ssh"],
        "task": ["back up a folder", "move a branch", "download a file", "inspect a table", "pack a release", "copy a key"],
        "dir": ["notes", "reports", "photos", "builds"],
    },
    title="How to {task} with {tool}",
    neutral=[
        "This guide assumes `{tool}` is already installed.",
        "Open a terminal in the folder that holds your {dir}.",
        "Run the command once to see what it would do.",
        "The command prints one line for each file it handles.",
        "Check the exit status with `echo $?` after the command ends.",
        "The whole procedure takes about {n} minutes.",
        "Keep a copy of the {dir} until you have checked the result.",
        "Each step below can be repeated safely.",
    ],
    neg=[
        ("The `--dry-run` flag shows the plan.", "It does not change any files."),
        ("Run the command from the {dir} folder.", "It will not work from a folder without write access."),
        ("Use `sudo` only when the target is a system folder.", "Do not use it for files in your home folder."),
        ("The tool prints a summary when it finishes.", "It stays silent unless an error occurs or `--verbose` is set."),
        ("Existing files are kept.", "Nothing is deleted without the `--delete` flag."),
    ],
    madeup=[
        "The archive is made up of the {dir} folder and a small manifest file.",
    ],
    quoted=[
        "The manual warns that the option \"cannot be undone\".",
    ],
    never=[
        "The older `--legacy` mode never supported symbolic links.",
    ],
    numbers=[
        "The default timeout is {n} seconds.",
        "Large folders of more than {m} files may take several minutes.",
        "Version {f} or later is required.",
    ],
    headings=["Common errors", "Next steps", "Useful flags", "Safety checks", "Prerequisites"],
)


def _howto_code(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    tool, d = sl["tool"], sl["dir"]
    opt = rng.choice(["--no-clobber", "--delete=False", "-n", "--verify=False"])
    if "False" in opt:
        s1 = f"The `{opt}` option is spelled out so the intent is clear to readers."
        tag = "code_false"
    else:
        s1 = f"Add `{opt}` to keep existing files in place."
        tag = "code_span"
    s2 = f"Replace `{d}` with the folder you want to handle."
    code = f"{tool} {opt} {d}/ backup/"
    src += ["## Command", "", s1 + " " + s2, "", "```bash", code, "```", ""]
    body.heading(2, "Command")
    body.para([sentence(s1, tag), sentence(s2, "code_span")])
    body.code("bash", code)


RESEARCH = Spec(
    "research_summary",
    banks={
        "subj": ["urban beekeeping", "sleep and memory", "cold-chain logistics", "reading speed", "soil carbon", "commuter cycling"],
        "grp": ["adults aged 25 to 40", "first-year students", "small farms", "city households"],
        "method": ["a survey", "a field trial", "a literature review", "a two-year panel study"],
    },
    title="Research summary: {subj}",
    neutral=[
        "The study used {method} of {m} participants.",
        "Participants were recruited from {grp}.",
        "Data were collected between {y} and {y}.",
        "The authors report their methods in an appendix.",
        "Results are grouped by age and region.",
        "The paper was reviewed by {k} external readers.",
        "Raw data are available from the corresponding author.",
        "The sample was weighted to match census figures.",
    ],
    neg=[
        ("The effect was larger in the first year.", "It was not significant after adjusting for age."),
        ("Participants kept a daily log.", "Logs without a date were excluded."),
        ("The authors found a link between {subj} and the outcome.", "They do not claim the link is causal."),
        ("The sample covers {grp}.", "It does not cover people under 18."),
        ("Response rates were reported for each group.", "Rates below {pc} were flagged unless a reminder had been sent."),
    ],
    madeup=[
        "The sample was made up of {m} people, about half of them women.",
        "The control group was made up of participants who joined late.",
    ],
    quoted=[
        "The authors wrote that the earlier estimate \"is not supported by the new data\".",
    ],
    never=[
        "The planned follow-up wave never took place because funding ended.",
    ],
    numbers=[
        "The average effect was {f} points on a ten-point scale.",
        "Roughly {pc} of participants completed all waves.",
        "The study ran for {k} years.",
    ],
    headings=["Key findings", "Study limits", "Sample details", "Open questions", "Recent trials"],
)


def _research_table(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    grps = pick(rng, ["Group A", "Group B", "Group C", "Control"], 3)
    rows = [[g, str(rng.randint(40, 400)), (lambda v: f"{v}%" if rng.random() < 0.5 else f"{v} percent")(rng.randint(5, 90))] for g in grps]
    src += ["## Results", "", "| Group | Participants | Improved |", "|---|---|---|"]
    src += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    body.heading(2, "Results")
    body.table(["Group", "Participants", "Improved"], [[r[0], Piece(r[1], "table_cell"), Piece(r[2], "table_cell")] for r in rows])


FINANCE = Spec(
    "financial_report",
    banks={
        "co": ["Harbor Freight Co", "Northgate Foods", "Brightline Energy", "Calder Textiles", "Pennant Labs", "Rowan Logistics"],
        "seg": ["retail", "wholesale", "services", "online"],
        "qtr": ["first", "second", "third", "fourth"],
        "cur": ["dollars", "pounds", "euros"],
    },
    title="{co}: {qtr} quarter results {y}",
    neutral=[
        "{co} reported results for the {qtr} quarter on Thursday.",
        "Revenue from the {seg} segment grew in the quarter.",
        "The board declared a dividend payable next month.",
        "Management expects stable demand in the coming quarter.",
        "The company ended the quarter with {m} employees.",
        "Operating costs were lower than a year earlier.",
        "The auditors reviewed the interim figures.",
        "The full statements are filed with the exchange.",
    ],
    neg=[
        ("Revenue rose in the {seg} segment.", "Revenue did not rise in the {seg} segment of the smallest region."),
        ("Cash flow from operations was positive.", "Free cash flow was not positive after the new plant."),
        ("The company repaid part of its loan.", "It has not drawn on the credit line this year."),
        ("The dividend was kept.", "It will not be raised unless profits exceed the plan."),
        ("Capital spending rose.", "The increase was without any new debt."),
    ],
    madeup=[
        "Revenue is made up of {seg} sales, services and a small licensing line.",
        "The cost base is made up mostly of staff, freight and rent.",
    ],
    quoted=[
        "The finance chief said the margin decline \"was not caused by pricing\".",
        "The chair said the company \"cannot rule out further charges\".",
    ],
    never=[
        "The rumoured takeover approach never materialised.",
        "The planned plant closure never went ahead.",
    ],
    numbers=[
        "Revenue was {m} million {cur}, up {pc} on the previous year.",
        "Net profit was {n} million {cur}.",
        "The dividend is {f} cents per share.",
    ],
    headings=["Price rises", "Segment results", "Outlook", "Cost pressures", "Cash flow"],
)


def _finance_table(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    segs = pick(rng, ["Retail", "Wholesale", "Services", "Online", "Licensing"], 4)
    rows = [[s, f"{rng.randint(10, 900)}", (lambda v: f"{v}%" if rng.random() < 0.5 else f"{v} percent")(rng.randint(1, 30)), rng.choice(["Yes", "No"])] for s in segs]
    src += ["## Segment table", "", "| Segment | Revenue (millions) | Margin | Beat plan |", "|---|---|---|---|"]
    src += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    body.heading(2, "Segment table")
    body.table(["Segment", "Revenue (millions)", "Margin", "Beat plan"],
               [[r[0], Piece(r[1], "table_cell"), Piece(r[2], "table_cell"), Piece(r[3], "table_no_false" if r[3] == "No" else "table_cell")] for r in rows])


SALES = Spec(
    "sales_report",
    banks={
        "region": ["North", "South", "East", "West", "Central"],
        "prod": ["the Alder line", "the Birch line", "the Cedar range", "subscription plans", "service contracts"],
        "rep": ["Anika", "Bruno", "Camille", "Dmitri", "Esther"],
        "mo": ["January", "April", "July", "October"],
    },
    title="Sales report: {region} region, {mo}",
    neutral=[
        "The {region} team closed {n} new accounts in {mo}.",
        "{rep} led the region in orders for {prod}.",
        "Average deal size was steady compared with the prior month.",
        "Renewals were handled by the account management group.",
        "The pipeline review is held every second Tuesday.",
        "Customer calls rose during the last week of the month.",
        "Discounts were approved by the regional director.",
        "The team met the training goal for the quarter.",
    ],
    neg=[
        ("Orders for {prod} grew.", "Orders for the older range did not grow."),
        ("The {region} region met its target.", "It did not meet the stretch target without the late renewals."),
        ("{rep} closed the largest deal.", "The deal cannot be booked until the contract is countersigned."),
        ("Returns were low.", "No returns were recorded for {prod}."),
        ("New leads came from events.", "Cold outreach produced no new accounts."),
    ],
    madeup=[
        "Regional revenue is made up of {prod}, support plans and training fees.",
        "The sales team is made up of {k} account executives and two analysts.",
    ],
    quoted=[
        "{rep} wrote that the delay \"was not the fault of the customer\".",
    ],
    never=[
        "The promised launch of the {region} showroom never took place in {mo}.",
    ],
    numbers=[
        "Sales reached {m} thousand dollars in {mo}.",
        "The win rate was {pc}.",
        "The average sales cycle was {n} days.",
    ],
    headings=["Price rises", "Top deals", "Pipeline notes", "Regional targets", "Rep results"],
)


def _sales_table(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    reps = pick(rng, ["Anika", "Bruno", "Camille", "Dmitri", "Esther"], 4)
    rows = [[r, str(rng.randint(2, 40)), f"{rng.randint(30, 400)}", rng.choice(["Yes", "No", "False"])] for r in reps]
    hdr = ["Rep", "Deals", "Sales (thousands)", "Target met"]
    src += ["## Rep results", "", "| " + " | ".join(hdr) + " |", "|---|---|---|---|"]
    src += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    body.heading(2, "Rep results")
    body.table(hdr, [[r[0], Piece(r[1], "table_cell"), Piece(r[2], "table_cell"),
                      Piece(r[3], "table_no_false" if r[3] in ("No", "False") else "table_cell")] for r in rows])


def build_all(rng: random.Random, per_genre: int) -> list[Draft]:
    plan = [(API, _api_params), (CHANGELOG, _changelog_flags), (CODE_REVIEW, _review_snippet),
            (HOWTO, _howto_code), (RESEARCH, _research_table), (FINANCE, _finance_table), (SALES, _sales_table)]
    out: list[Draft] = []
    for spec, hook in plan:
        for i in range(per_genre):
            use = hook if i % 2 == 0 else None
            out.append(assemble(spec, random.Random(rng.random()), i, use))
    return out
