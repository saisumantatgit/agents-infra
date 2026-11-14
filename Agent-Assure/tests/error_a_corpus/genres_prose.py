"""Prose-first genres: product docs, README, FAQ, incident, meeting notes, news brief, HR policy.

Every template is original text written for this corpus. Slots in {braces} are filled
once per draft from the genre banks (consistent within a draft). Each source gets a
neutral paragraph, a negation-neighbour paragraph, and a paragraph of "everyday honest
shapes" (made up of / quoted denial / never happened / numbers).
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from corpus_core import Body, Draft, Piece, Slots, pick, sentence
from fillers import FILLER


@dataclass(frozen=True)
class Spec:
    name: str
    banks: dict[str, list[str]]
    title: str
    neutral: list[str]
    neg: list[tuple[str, str]]          # (honest claim, negated neighbour sentence)
    madeup: list[str]
    quoted: list[str]
    never: list[str]
    numbers: list[str]
    headings: list[str]                 # plural-noun headings (draft only)


def assemble(spec: Spec, rng: random.Random, idx: int, extra=None) -> Draft:
    """Compose source + draft from a Spec. `extra(rng, slots, src_lines, body)` may append a
    table or code block to both.

    Density cycles with idx: 0 = dense (heavy quoting of a short source, many shapes),
    1 = normal (shapes plus six uncited background sentences), 2 = light (one shape pair,
    no negation neighbours, plain and numeric claims, background padding).
    """
    sl = Slots(rng, spec.banks)
    mode = idx % 3
    neutral = [sl.fill(t) for t in pick(rng, spec.neutral, 7)]
    filler = [sl.fill(t) for t in pick(rng, FILLER[spec.name], 2 if mode == 0 else 6)]
    negpairs = [] if mode == 2 else [(sl.fill(a), sl.fill(b)) for a, b in pick(rng, spec.neg, 2)]
    shapes: list[tuple[str, str]] = []  # (sentence, shape) in the 3rd paragraph
    pools = ((spec.madeup, "made_up_of", 1), (spec.quoted, "quoted_denial", 1),
             (spec.never, "never_happened", 1), (spec.numbers, "number", 2))
    if mode == 2:
        pools = ((spec.numbers, "number", 2), (rng.choice([spec.madeup, spec.quoted, spec.never]), None, 1))
    for pool, tag, k in pools:
        for t in pick(rng, pool, k):
            tg = tag or ("made_up_of" if pool is spec.madeup else "quoted_denial" if pool is spec.quoted else "never_happened")
            shapes.append((sl.fill(t), tg))
    rng.shuffle(shapes)

    title = sl.fill(spec.title)
    src: list[str] = [f"# {title}", "", " ".join(neutral[:3]), ""]
    if filler[:len(filler) // 2]:
        src += [" ".join(filler[:len(filler) // 2]), ""]
    p2: list[str] = []
    for a, b in negpairs:
        p2 += [b, a] if rng.random() < 0.5 else [a, b]
    if p2:
        src += [" ".join(p2), ""]
    src += [" ".join(s for s, _ in shapes), "", " ".join(neutral[3:]), ""]
    if filler[len(filler) // 2:]:
        src += [" ".join(filler[len(filler) // 2:]), ""]

    body = Body()
    if rng.random() < 0.45:
        body.heading(2, sl.fill(rng.choice(spec.headings)))
    else:
        body.heading(1, title)

    claims: list[Piece] = [sentence(s, "plain") for s in neutral[:2 if mode != 2 else 3]]
    for a, b in negpairs:
        claims.append(sentence(a, "neg_neighbour"))
        if rng.random() < 0.5:
            claims.append(sentence(b, "neg_sentence"))
    claims += [sentence(s, tag) for s, tag in shapes if rng.random() < 0.85] or \
        [sentence(shapes[0][0], shapes[0][1])]
    if mode != 2:
        claims += [sentence(s, "plain") for s in neutral[3:5]]
    source_text = "\n".join(src)
    claims.sort(key=lambda c: source_text.index(c.text))   # draft follows source order
    style = rng.choices(["bullets", "para", "numbered"], weights=[8, 6, 2])[0]
    if style == "para":
        for i in range(0, len(claims), 4):   # paragraphs of at most four sentences
            body.para(claims[i:i + 4])
    elif style == "numbered":
        body.numbered(claims)
    else:
        body.bullets(claims)

    if extra is not None:
        extra(rng, sl, src, body)
    return Draft(f"{spec.name}_{idx:03d}", spec.name, {"source.md": "\n".join(src).rstrip() + "\n"},
                 body.text(), body.claims)


# ---------------------------------------------------------------- product docs
PRODUCT_DOCS = Spec(
    "product_docs",
    banks={
        "prod": ["Larkspur", "Quillboard", "Tandem Ledger", "Brightwell", "Pinecone Queue", "Tidepool", "Marlin Sync", "Orchard Desk", "Kestrel Mail", "Fenwick Notes", "Harrow Forms", "Saltmarsh Planner"],
        "feat": ["scheduled exports", "shared workspaces", "audit history", "offline mode", "role templates", "bulk import", "custom fields", "reminder rules"],
        "plan": ["Team", "Business", "Starter", "Studio"],
        "unit": ["workspace", "project", "board", "folder"],
        "thing": ["attachments", "comments", "exports", "drafts"],
    },
    title="{prod}: working with {feat}",
    neutral=[
        "{prod} stores every {unit} in the account that created it.",
        "The {plan} plan includes {feat} for up to {n} members.",
        "Each {unit} keeps its {thing} for {n} days after a member removes them.",
        "Owners can rename a {unit} from the settings page.",
        "{prod} sends a summary email to the owner every Monday morning.",
        "The sidebar lists the {n} most recently opened items first.",
        "Members open {feat} from the toolbar above the {unit} list.",
        "A {unit} can hold up to {m} {thing}.",
        "Search covers titles, tags and the first {n} lines of every note.",
        "Changes made on one device appear on the others within a few seconds.",
    ],
    neg=[
        ("Owners can restore a removed {unit} from the trash.", "Members cannot restore a {unit} that an owner has removed."),
        ("The {plan} plan includes {feat}.", "The Starter plan does not include {feat}."),
        ("{prod} syncs {thing} in the background.", "Sync pauses unless the device is connected to a network."),
        ("Guests can view a shared {unit}.", "Guests cannot change its settings."),
        ("Exports download as a single archive.", "The archive is created without the original file permissions."),
        ("An owner may invite {n} guests per {unit}.", "Guests are not counted as members for billing."),
    ],
    madeup=[
        "Each {unit} is made up of folders, pages and a shared activity log.",
        "The {plan} plan is made up of the core editor, {feat} and priority support.",
        "A weekly summary is made up of the {n} busiest {unit}s and a list of overdue items.",
    ],
    quoted=[
        "Support told the {plan} customers that the delay \"was not caused by the new release\".",
        "The release notes say the change \"does not affect existing {thing}\".",
    ],
    never=[
        "The planned redesign of the {unit} list never shipped in the {y} cycle.",
        "The {feat} beta never left the {plan} plan.",
    ],
    numbers=[
        "The free trial lasts {n} days and needs no card.",
        "Uploads larger than {m} MB are rejected.",
        "The {plan} plan costs {n} dollars per member each month.",
        "Version {f} added {feat} to every plan.",
    ],
    headings=["Price rises", "Plan limits", "Release notes", "Sharing rules", "Storage limits", "Account bans", "Recent arrests"],
)


def _feature_matrix(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    feats = pick(rng, ["Single sign-on", "Audit export", "Offline mode", "Guest access", "Custom domains", "API access", "Priority support"], 4)
    plans = ["Starter", "Team"]
    rows = [[f] + [rng.choice(["Yes", "No"]) for _ in plans] for f in feats]
    src += ["## Feature matrix", "", "| Feature | " + " | ".join(plans) + " |", "|---|" + "---|" * len(plans)]
    src += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    body.heading(2, "Feature matrix")
    body.table(["Feature"] + plans, [[r[0]] + [Piece(c, "table_no_false" if c == "No" else "table_cell") for c in r[1:]] for r in rows])


# ---------------------------------------------------------------- README
README = Spec(
    "readme",
    banks={
        "lib": ["reedly", "tallyman", "cinderlog", "pebblecache", "gridsnap", "quillparse", "mothlight", "driftq", "foldkit", "wickerdb"],
        "lang": ["Python", "Go", "Rust", "TypeScript"],
        "thing": ["records", "events", "rows", "messages"],
        "opt": ["strict", "verbose", "dry_run", "follow_links"],
    },
    title="{lib}",
    neutral=[
        "{lib} is a small {lang} library for reading and writing {thing}.",
        "The library has no runtime dependencies beyond the {lang} standard library.",
        "Install it with the package manager that ships with {lang}.",
        "Every public function is documented in the docs folder.",
        "The test suite runs in under {n} seconds on a laptop.",
        "Releases follow semantic versioning.",
        "The `{opt}` option is read from the config file at startup.",
        "Contributions are welcome through pull requests.",
        "Bug reports should include the version printed by `{lib} --version`.",
    ],
    neg=[
        ("The parser accepts trailing commas.", "The parser does not accept comments inside values."),
        ("Reads are buffered.", "Writes are not buffered unless the `flush` option is set."),
        ("The `{opt}` option defaults to off.", "It cannot be changed after the first {thing} is read."),
        ("Files are opened in binary mode.", "Text encoding is left alone unless a codec is named."),
        ("The command exits with status 0 on success.", "It exits without printing anything when the input is empty."),
    ],
    madeup=[
        "The package is made up of a reader, a writer and a small command line tool.",
        "Each batch is made up of at most {m} {thing}.",
    ],
    quoted=[
        "The maintainers wrote that the old API \"cannot be removed before version 2\".",
    ],
    never=[
        "The planned Windows installer never reached a stable release.",
    ],
    numbers=[
        "Version {f} reduced memory use by {pc} on large inputs.",
        "The default batch size is {m} {thing}.",
        "The project supports {lang} versions from the last {k} releases.",
    ],
    headings=["Install notes", "Known limits", "Supported platforms", "Breaking changes", "Planned features"],
)


def _readme_code(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    lib = sl["lib"]
    opt = sl["opt"]
    shape = rng.choice(["eqfalse", "eqfalse2", "plain"])
    if shape == "plain":
        s1 = f"Call `open_reader` with a path to start reading."
        s2 = f"The reader yields one record at a time."
        code = f"from {lib} import open_reader\n\nfor rec in open_reader('data.log'):\n    print(rec)"
        tag = "code_span"
    else:
        s1 = f"Pass `{opt}=False` to turn the check off for a single call."
        s2 = f"The default for `{opt}` is True."
        code = f"from {lib} import load\n\nrows = load('data.log', {opt}=False)\nprint(len(rows))"
        tag = "code_false"
    src += ["## Usage", "", s1 + " " + s2, "", "```python", code, "```", ""]
    body.heading(2, "Usage")
    body.para([sentence(s1, tag), sentence(s2, "plain")])
    body.code("python", code)


# ---------------------------------------------------------------- FAQ
FAQ_TOPICS = [
    ("the {app} app", "{app}", ["Does {app} work offline?", "Can I use {app} on two phones?"]),
]
FAQ = Spec(
    "faq",
    banks={
        "app": ["Tallyboard", "Cobble", "Nimbus Pay", "Wrenfield", "Plover", "Harvest Desk", "Mosswood"],
        "item": ["receipts", "invoices", "tickets", "recipes", "photos"],
        "plan": ["Free", "Plus", "Pro"],
    },
    title="{app}: questions and answers",
    neutral=[
        "{app} keeps {item} in the account that uploaded them.",
        "You can export your {item} at any time from the account page.",
        "The {plan} plan allows {n} devices per account.",
        "Support replies to most messages within {n} hours on weekdays.",
        "Passwords are stored as salted hashes.",
        "{app} is available in {k} languages.",
        "Deleted {item} stay in the trash for {n} days.",
    ],
    neg=[
        ("You can use {app} on a tablet.", "The tablet version cannot scan {item} with the camera."),
        ("Offline edits are saved on the device.", "They sync once the connection returns, unless the account is locked."),
        ("The {plan} plan removes the banner.", "It does not change the storage limit."),
        ("{app} accepts photos of {item}.", "It rejects files without a readable date."),
    ],
    madeup=[
        "Your monthly report is made up of totals, a category chart and a list of unusual items.",
    ],
    quoted=[
        "A company statement said that the outage \"did not expose any stored {item}\".",
        "The founder wrote that the app \"has never sold user data\".",
    ],
    never=[
        "The rumoured shutdown of the {plan} plan never happened.",
        "The announced price cut never took effect for annual accounts.",
    ],
    numbers=[
        "The {plan} plan includes {m} MB of storage.",
        "Each account can hold up to {m} {item}.",
        "Refunds are available for {n} days after purchase.",
    ],
    headings=["Myths and facts", "Common questions", "Billing questions", "Price rises", "Account limits"],
)


def _faq_myths(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    app, item = sl["app"], sl["item"]
    pairs = pick(rng, [
        (f"Myth: {app} reads your {item} to show adverts.", f"Fact: {app} does not read the contents of your {item}."),
        (f"Myth: Deleted {item} are gone at once.", f"Fact: Deleted {item} stay in the trash for {sl['n']} days."),
        (f"Myth: The Pro plan is required for exports.", f"Fact: Every plan can export {item}."),
        (f"Myth: {app} stops working when the phone is offline.", f"Fact: Offline edits are saved on the device and sync later."),
        (f"Myth: Only the owner can see the activity log.", f"Fact: Members with the viewer role can read the activity log."),
    ], 3)
    src += ["## Myths and facts", ""]
    for m, f in pairs:
        src += [f"{m} {f}", ""]
    body.heading(2, "Myths and facts")
    body.bullets([sentence(f, "faq_fact") for _, f in pairs])


# ---------------------------------------------------------------- incident reports
INCIDENT = Spec(
    "incident",
    banks={
        "svc": ["checkout", "search", "notifications", "billing", "login", "image resizer", "report builder"],
        "db": ["primary database", "read replica", "queue broker", "cache cluster"],
        "day": ["Tuesday", "Thursday", "Saturday", "Monday"],
        "team": ["platform team", "payments team", "on-call engineer", "data team"],
        "cause": ["an expired certificate", "a full disk", "a bad configuration push", "a runaway batch job"],
    },
    title="Incident review: {svc} degradation on {day}",
    neutral=[
        "The {svc} service began returning errors on {day} at {n} minutes past the hour.",
        "The {team} was paged within {k} minutes of the first alert.",
        "The root cause was {cause} on the {db}.",
        "Engineers restored normal service after {n} minutes.",
        "A status page notice went out {k} minutes after the page.",
        "The {db} was restarted twice during the response.",
        "Traffic was moved to the standby region while the fix was prepared.",
        "A follow-up review is scheduled for the following week.",
    ],
    neg=[
        ("Customers could browse the catalogue during the incident.", "They could not complete a purchase."),
        ("The standby region took over automatically.", "No orders were lost during the failover."),
        ("The alert fired on the first failed health check.", "The dashboard did not show the error rate until the second minute."),
        ("The fix was reviewed by a second engineer.", "It was deployed without a staged rollout."),
        ("The runbook covers the restart steps.", "It does not cover a full disk on the {db}."),
    ],
    madeup=[
        "The response group was made up of the on-call engineer, a database specialist and an incident lead.",
        "Overnight traffic is made up mostly of scheduled exports.",
    ],
    quoted=[
        "The vendor stated that the earlier maintenance \"was not related to the outage\".",
        "The incident lead wrote that the dashboards \"cannot show per-region errors yet\".",
    ],
    never=[
        "The planned disk alert never reached the {team}.",
        "The expected automatic rollback never ran.",
    ],
    numbers=[
        "About {pc} of requests failed at the peak.",
        "The error rate stayed above {pc} for {k} minutes.",
        "The {db} held {m} queued jobs when it was restarted.",
    ],
    headings=["Action items", "Contributing factors", "Customer impacts", "Lessons learned", "Follow-ups"],
)


def _incident_timeline(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    ev = pick(rng, [
        ("Alert fired", "The health check failed three times in a row"),
        ("Page acknowledged", "The on-call engineer opened the dashboard"),
        ("Mitigation started", "Traffic moved to the standby region"),
        ("Fix deployed", "The configuration change was rolled back"),
        ("Service restored", "Error rates returned to normal"),
    ], 4)
    times = sorted(rng.sample(range(0, 59), 4))
    rows = [[f"10:{t:02d}", a, b] for t, (a, b) in zip(times, ev)]
    src += ["## Timeline", "", "| Time | Event | Detail |", "|---|---|---|"]
    src += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    body.heading(2, "Timeline")
    body.table(["Time", "Event", "Detail"], [[r[0], r[1], Piece(r[2], "table_cell")] for r in rows])


# ---------------------------------------------------------------- meeting notes
MEETING = Spec(
    "meeting_notes",
    banks={
        "proj": ["the harbour app", "the Q3 roadmap", "the onboarding revamp", "the data migration", "the partner portal", "the pricing review"],
        "who": ["Priya", "Tomas", "Ingrid", "Marcus", "Aiko", "Dev"],
        "who2": ["Lena", "Omar", "Beatrice", "Jun", "Carla"],
        "day": ["Friday", "Wednesday", "next Monday", "the end of the month"],
    },
    title="Notes: weekly sync on {proj}",
    neutral=[
        "{who} presented the current status of {proj}.",
        "The group agreed to review the draft again on {day}.",
        "{who2} will update the shared tracker after the call.",
        "Attendance was {n} people, including two from the design team.",
        "The next sync is booked for the same time next week.",
        "{who} reported that {k} tasks are now complete.",
        "The team prefers a single owner for each open item.",
        "Budget questions were moved to the finance review.",
    ],
    neg=[
        ("{who} confirmed the vendor contract was signed.", "The vendor has not delivered the test environment yet."),
        ("The pilot ran for {n} days.", "It did not include the mobile client."),
        ("{who2} will lead the interviews.", "Nobody from legal can attend unless the date moves."),
        ("The design is approved.", "Copy changes cannot start without the final layout."),
        ("The migration plan was accepted.", "The cutover date was not fixed."),
    ],
    madeup=[
        "The steering group is made up of {who}, {who2} and two external advisers.",
    ],
    quoted=[
        "{who2} said the earlier estimate \"was not based on the final scope\".",
        "{who} noted that the vendor \"cannot support the old format\".",
    ],
    never=[
        "The security review of {proj} never took place last quarter.",
        "The promised dashboard demo never happened.",
    ],
    numbers=[
        "The estimate for {proj} is {m} hours.",
        "{pc} of the survey responses came from existing customers.",
        "The review will take {k} working days.",
    ],
    headings=["Action items", "Decisions made", "Open questions", "Budget notes", "Next steps"],
)


def _meeting_actions(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    owners = pick(rng, ["Priya", "Tomas", "Ingrid", "Marcus", "Aiko", "Dev"], 3)
    acts = pick(rng, ["Send the revised plan", "Book the review room", "Update the tracker", "Draft the customer note", "Confirm the vendor date"], 3)
    done = [rng.choice(["Yes", "No"]) for _ in acts]
    src += ["## Action items", "", "| Action | Owner | Done |", "|---|---|---|"]
    src += [f"| {a} | {o} | {d} |" for a, o, d in zip(acts, owners, done)] + [""]
    body.heading(2, "Action items")
    body.table(["Action", "Owner", "Done"], [[a, Piece(o, "table_cell"), Piece(d, "table_no_false" if d == "No" else "table_cell")] for a, o, d in zip(acts, owners, done)])


# ---------------------------------------------------------------- news briefs
NEWS = Spec(
    "news_brief",
    banks={
        "town": ["Aldermoor", "Westbrook", "Kingsferry", "Marlow Bay", "Stonebridge", "Hartley"],
        "org": ["the town council", "the harbour authority", "the county library", "the bus operator", "the school board"],
        "site": ["the old mill", "the riverside car park", "the market hall", "the east depot"],
        "month": ["March", "June", "September", "November"],
    },
    title="{town} briefing: {org}",
    neutral=[
        "{org} announced the plan on a Tuesday afternoon.",
        "Work at {site} is expected to start in {month}.",
        "The measure passed by {n} votes to {k}.",
        "Residents can read the full proposal at the front desk.",
        "The meeting was held in the main hall and lasted {n} minutes.",
        "A public comment period opens next week.",
        "The cost will be shared between the town and the county.",
        "Local shops were told about the change by letter.",
    ],
    neg=[
        ("{org} will publish the survey results in {month}.", "The report will not name individual respondents."),
        ("Parking at {site} stays free for residents.", "Visitors cannot park there overnight."),
        ("The bus route will run every {n} minutes.", "It will not stop at the east depot unless a rider requests it."),
        ("The council backed the plan.", "No councillor spoke against it."),
    ],
    madeup=[
        "The review panel is made up of {k} residents and one council officer.",
        "The fund is made up of grants, local donations and a small council contribution.",
    ],
    quoted=[
        "A spokesperson for {org} said the closure \"is not permanent\".",
        "The chair said the rumours about a sale \"are not true\".",
    ],
    never=[
        "The earlier bid for {site} never went to a vote.",
        "The widely discussed ferry link never opened.",
    ],
    numbers=[
        "The project will cost about {m} thousand pounds.",
        "{pc} of respondents backed the change.",
        "Around {m} people live within a mile of {site}.",
    ],
    headings=["Price rises", "Council decisions", "Road closures", "Recent arrests", "Planning updates"],
)


# ---------------------------------------------------------------- HR / policy
HR = Spec(
    "hr_policy",
    banks={
        "policy": ["Remote work", "Parental leave", "Expense claims", "Equipment loans", "Training budget", "On-call pay"],
        "role": ["employees", "contractors", "managers", "new starters"],
        "form": ["the HR portal", "the finance form", "the shared request sheet"],
        "unit": ["days", "hours", "weeks"],
    },
    title="{policy} policy",
    neutral=[
        "This policy applies to all {role} who have completed their probation.",
        "Requests are submitted through {form}.",
        "Managers respond to a request within {n} working days.",
        "The policy is reviewed once a year by the HR team.",
        "Records are kept for {k} years.",
        "Questions about the policy go to the people team.",
        "Part-time staff receive a pro-rated allowance.",
        "The allowance resets on the first day of each year.",
    ],
    neg=[
        ("{role} may carry over unused {unit} into the next year.", "Carried-over {unit} cannot exceed {n}."),
        ("Claims need a receipt.", "Claims without a receipt are not paid unless a manager approves them."),
        ("{policy} is open to full-time staff.", "Contractors are not eligible."),
        ("Approval is given in writing.", "Verbal approval does not count."),
        ("Staff may work from another city for up to {n} days.", "They must not work from abroad without a signed agreement."),
    ],
    madeup=[
        "The allowance is made up of a base amount and a length-of-service bonus.",
        "The review committee is made up of two managers and one HR partner.",
    ],
    quoted=[
        "The handbook states that the rule \"does not apply during probation\".",
        "HR clarified that the change \"cannot be applied to past claims\".",
    ],
    never=[
        "The proposed cap on {policy} never came into force.",
        "The earlier pilot of a four-day week never extended past one team.",
    ],
    numbers=[
        "The standard allowance is {n} {unit} per year.",
        "Claims above {m} dollars need director approval.",
        "Notice of at least {k} weeks is required.",
    ],
    headings=["Eligibility rules", "Pay rises", "Allowance limits", "Approval steps", "Policy changes"],
)


def _hr_eligibility(rng: random.Random, sl: Slots, src: list[str], body: Body) -> None:
    groups = pick(rng, ["Full-time staff", "Part-time staff", "Contractors", "Interns", "Managers"], 4)
    rows = [[g, rng.choice(["Yes", "No", "Yes"])] for g in groups]
    src += ["## Eligibility", "", "| Group | Eligible |", "|---|---|"] + [f"| {g} | {e} |" for g, e in rows] + [""]
    body.heading(2, "Eligibility")
    body.table(["Group", "Eligible"], [[g, Piece(e, "table_no_false" if e == "No" else "table_cell")] for g, e in rows])


def build_all(rng: random.Random, per_genre: int) -> list[Draft]:
    plan = [(PRODUCT_DOCS, _feature_matrix), (README, _readme_code), (FAQ, _faq_myths),
            (INCIDENT, _incident_timeline), (MEETING, _meeting_actions), (NEWS, None), (HR, _hr_eligibility)]
    out: list[Draft] = []
    for spec, hook in plan:
        for i in range(per_genre):
            use = hook if (hook is not None and i % 2 == 0) else None
            out.append(assemble(spec, random.Random(rng.random()), i, use))
    return out
