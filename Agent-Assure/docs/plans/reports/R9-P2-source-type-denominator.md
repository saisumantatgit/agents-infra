# R9-P2 — Provenance: source type + denominator (red-team round 9)

Date: 2026-09-13. Scope: provenance only — (a) summary-only never certified, (b) untrusted store rejected loudly, (c) every assertion scored.
Harness: `/private/tmp/claude-501/-Users-saisumanthbattepati-vibe-coding-Agents-agent-assure-calibration/d2b27b1f-f3bd-4dea-8c6a-e58508ad626d/scratchpad/r9p2/run.py` (writes D.md + S.jsonl, runs `uv run python scripts/ground_check.py --draft --store --json`, prints gate/score/scored/per-claim). Code read at HEAD 13c2f4e.
Common fixture: source text `The Redis cluster replicates every write to three replicas before acknowledging the client request.`; draft GOOD = that sentence + ` [S1].`

## FINDINGS

### R9P2-01 — duplicate source_id: silent last-record-wins, launders a summary to verbatim
Severity: silent-repair (PASS-enabling; verdict depends on line order).
Mechanism: `load_store` does `store[source_id] = source` with no membership check (ground_check.py:112). Two records with the same id load without error; the later one silently replaces the earlier. Whether a claim citing [S1] is UNGROUNDABLE or GROUNDED depends only on line order.
Reproduction: store = [rec(S1, haiku_summary), rec(S1, verbatim)] vs the reverse order; draft GOOD.
Output:
```
== dup_sum_then_verb exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "...client request [S1]."]]}
== dup_verb_then_sum exit=1
{"gate": "FAIL", "score": 0.0, "scored": 1, "claims": [["FACTUAL", "UNGROUNDABLE", "...client request [S1]."]]}
```
Human reading: the store says S1 is an AI summary AND says S1 is verbatim. A store that contradicts itself about the one field promise (a) rests on cannot be trusted; the gate picks a side silently and certifies. Violates CLAUDE.md "duplicate key -> raise". Capture assigns ids under a file lock (capture_core.py:425), so this needs a merged/concatenated/hand-edited store — but that is exactly the input promise (b) exists for.

### R9P2-02 — NFKC id collision: `Ｓ1` and `S1` become one key, silently
Severity: silent-repair (same class as -01, second entry path).
Mechanism: ids are NFKC-folded BEFORE insertion (ground_check.py:98), so distinct raw ids `Ｓ1` (full-width) and `S1` collide and the later overwrites; a store holding only `Ｓ1` answers citations to `[S1]`.
Output:
```
== nfkc_id_collision exit=0     (store: Ｓ1 haiku_summary "unrelated", then S1 verbatim)
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "...[S1]."]]}
== nfkc_id_only_fullwidth exit=0   (store: only Ｓ1 verbatim)
{"gate": "PASS", "score": 100.0, "scored": 1, ...}
```
Human reading: two different source records are merged into one without notice. A duplicate check must run on the NORMALIZED id to close -01 fully.

### R9P2-03 — duplicate JSON key inside ONE record: `full_text_source` last-key-wins
Severity: silent-repair (PASS-enabling laundering within a single line).
Mechanism: `json.loads` without `object_pairs_hook` keeps the last of duplicated keys. A line carrying `"full_text_source":"haiku_summary"` and later `"full_text_source":"verbatim"` (and `"tool":"WebFetch"`) loads as verbatim.
Reproduction line: `{"source_id":"S1",...,"tool":"WebFetch",...,"full_text_source":"haiku_summary",...,"full_text_source":"verbatim"}`
Output:
```
== dupkey_in_object exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "...[S1]."]]}
```
Human reading: the record declares itself a summary; the gate certifies against it. Violates the CLAUDE.md "duplicate key -> raise" convention literally.

### R9P2-04 — no internal-consistency check: `tool:"WebFetch"` + `full_text_source:"verbatim"`, bad sha, null/mistyped fields all certify
Severity: silent-repair (PASS on a self-contradicting record; type confusion loads).
Mechanism: `load_store` reads `full_text_source` as a free string and never cross-checks it against `tool` (capture_core.py:28 HARD SPEC: WebFetch is ALWAYS haiku_summary), never recomputes `content_sha256` against `text`, and type-checks nothing except by accident (`_nfkc` on source_id/text). The provenance of a claim therefore rests on one self-declared string.
Output:
```
== tool_webfetch_but_verbatim exit=0   {"gate": "PASS", "score": 100.0, ...GROUNDED}
== sha_mismatch exit=0                 {"gate": "PASS", "score": 100.0, ...GROUNDED}   (content_sha256 = "0"*64)
== fetched_at_null exit=0              {"gate": "PASS", ...}  (fetched_at=null, tool=null, content_sha256=null, captured_via=12)
== url_int exit=0                      {"gate": "PASS", ...}  (url=7, file_path=["x"])
== query_prov_list exit=0              {"gate": "PASS", ...}  (query_provenance=["a"])
```
Human reading: a store record that no capture path could have produced (WebFetch never yields verbatim; hash does not match text) is accepted as audit evidence. The WebFetch/verbatim and sha cases change the verdict relative to a validating loader (which would reject); the null/int cases do not change this verdict but are silent acceptance of wrong types.

### R9P2-05 — tilde-fenced `<!--` / `-->` delete visible prose from the denominator (gate PASS)
Severity: denominator-escape (PASS with three uncited fabrications visible to the reader).
Mechanism: OI-MOAT-29's repair protects comment delimiters only inside BACKTICK code (`_CODE_SPAN_RE`, ground_check.py:311: ```` ``` ````, ` `` `, `` ` ``). CommonMark also has TILDE fences (`~~~`). A `<!--` inside a tilde fence is rendered as literal code, but `_strip_html_comments_outside_code` does not see it as code, pairs it with a `-->` in a later tilde fence, and removes every paragraph between.
Draft (repr): `'<GOOD> [S1].\n\n~~~\n<!--\n~~~\n\nMongoDB lost all customer data under sustained write load. PostgreSQL silently corrupts indexes after every failover.\n\nRedis drops writes above ten thousand clients.\n\n~~~\n-->\n~~~\n'`
Output:
```
== tilde_multi2 exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "<GOOD> [S1]."], ["NON_CLAIM", "GROUNDED", "~~~"], ["NON_CLAIM", "GROUNDED", "~~~"]]}
```
Renderer check (`pandoc -f commonmark -t html`): all three sentences render as `<p>` paragraphs; the delimiters render as `<pre><code>&lt;!--</code></pre>` and `<pre><code>--&gt;</code></pre>`.
Human reading: the draft claims (1) Redis replicates to three replicas [cited], (2) MongoDB lost all customer data under load, (3) PostgreSQL corrupts indexes after every failover, (4) Redis drops writes above ten thousand clients. Gate scores 1 claim, PASS 100.0. Note a `~~~html` info string is itself scored (UNCITED) and blocks PASS — the attacker simply omits it.

### R9P2-06 — 4-space indented code block carries the delimiters (gate PASS)
Severity: denominator-escape. Same mechanism as -05, second code-block syntax (indented code is not matched by `_CODE_SPAN_RE` either), and leaves NO residue claim at all.
Draft (repr): `'<GOOD> [S1].\n\n    <!--\n\nMongoDB lost all customer data under sustained write load.\n\nPostgreSQL silently corrupts indexes after every failover.\n\nRedis drops writes above ten thousand clients.\n\n    -->\n'`
Output:
```
== indent_multi2 exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "<GOOD> [S1]."]]}
```
Renderer check: pandoc renders `<pre><code>&lt;!--</code></pre>`, three `<p>` fabrications, `<pre><code>--&gt;</code></pre>`.
Human reading: identical to -05 — four claims, one cited; the report lists exactly one claim and prints no trace that anything was removed.

### R9P2-07 — backslash-escaped opener `\<!--` (plain paragraph, no code at all) (gate PASS)
Severity: denominator-escape. Third shape: CommonMark backslash-escape makes `\<!--` literal text; the regex `<!--.*?--> ` ignores the backslash, pairs it with a bare `-->` line (which also renders as literal text), and strips everything between. The only residue is `\`, which has zero content words and is NON_CLAIM.
Draft: `<GOOD> [S1].` / blank / `\<!--` / blank / X / blank / Y / blank / Z / blank / `-->` (X, Y, Z = the three fabrications above).
Output:
```
== bs_escaped_line exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "<GOOD> [S1]."], ["NON_CLAIM", "GROUNDED", "\\"]]}
```
Renderer check: pandoc renders `<p>&lt;!--</p>`, X, Y, Z as `<p>`, then `<p>--&gt;</p>`.
Human reading: four visible claims, one cited, gate PASS.
Class note for -05/-06/-07: the root is that the comment stripper decides "is this a comment" by a regex over raw text rather than by the renderer's block structure. Enumerating more code syntaxes is the blacklist shape this repo has watched fail; the fail-closed alternative is to strip a comment only if the text between the delimiters contains no blank line / no paragraph break (a real authoring note is allowed to be multi-line, so that itself has Error-A cost), or to strip only when `<!--` begins a line with <=3 spaces indent and is not preceded by `\` and is not inside any fence — i.e. CommonMark HTML-block rule 2, which is a positional property the author cannot set without giving up the hiding.

### R9P2-08 — stop-word-only assertions are NON_CLAIM
Severity: cosmetic (by design of the ZERO-content rule; recorded so it is a known seam, not a discovery later).
Output:
```
== stopword_only exit=0
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["FACTUAL", "GROUNDED", "<GOOD> [S1]."], ["NON_CLAIM", "GROUNDED", "It was not."], ["NON_CLAIM", "GROUNDED", "They did not."], ["NON_CLAIM", "GROUNDED", "No, it does not."]]}
```
Human reading: "It was not." after a claim can deny it, but the content lives in the referent, which is scored elsewhere (in `yes_no_answer`, the question "Did the Redis cluster pass the durability audit?" is scored UNCITED and blocks PASS). No draft found where this alone smuggles a fact past PASS.

### R9P2-09 — relational "two distinct sources" is satisfied by the SAME document captured twice
Severity: silent-repair / provenance (corroboration laundered). Not classed ERROR-B: in the repro the relation IS asserted verbatim by the one real document, so no fabrication is certified — what is defeated is the independence the two-source rule promises. Parent to adjudicate whether §4.8 intends independence.
Mechanism: `ground_relational` dedupes by `source_id` only (ground_check.py:2466). Two records with identical `url`, identical `text` and identical `content_sha256` but ids S1/S2 count as two distinct sources. This needs NO tampering: capture assigns a fresh id per fetch, so re-fetching one URL yields S1 and S2. Same result with a full-width `Ｓ2` id.
Output (source text "Write amplification causes latency spikes in the storage engine.", draft "Write amplification causes latency spikes in the storage engine [S1][S2]."):
```
== rel_verbatim exit=1   (store: S1 only)
{"gate": "FAIL", "score": 0.0, "scored": 1, "claims": [["RELATIONAL", "UNVERIFIED_RELATION", ...]]}
== rel_sameurl exit=0    (store: S1 and S2, same url, same text, same sha)
{"gate": "PASS", "score": 100.0, "scored": 1, "claims": [["RELATIONAL", "GROUNDED", "...[S1][S2]."]]}
== rel_sid_fullwidth_dup exit=0  (S1 + Ｓ2, different url)
{"gate": "PASS", "score": 100.0, ...}
== rel_mixed exit=1      (S1 verbatim + S2 haiku_summary)  -> UNVERIFIED_RELATION (summary correctly excluded)
```
Human reading: "two independent sources support this causal link" when one page was simply fetched twice.

## KNOWN ITEMS RE-CONFIRMED STILL OPEN (not re-reported)
- R8B-03 `#`+TAB -> PASS; 7 hashes `#######` -> PASS; full-width `＃` -> PASS (all NON_CLAIM, gate PASS 100.0).
- OI-MOAT-20 verb-final header `### PostgreSQL Fails` -> NON_CLAIM, PASS.
- OI-MOAT-31 header default `### Catastrophic MongoDB corruption` -> NON_CLAIM, PASS. (My NBSP variant lost the NBSP in the heredoc and reproduced this default instead; NBSP itself not re-tested.)


## ATTACKS THAT FAILED (fail-closed or loud, verified by run)
Store / promise (a),(b):
1. `full_text_source` = "Verbatim", "verbatim " (trailing space), "VERBATIM", full-width "ｖｅｒｂａｔｉｍ", "verbatim"+ZWSP, null, ["verbatim"], true -> all UNGROUNDABLE, FAIL. The `== "verbatim"` exact compare is not NFKC'd, so no variant launders. (Silent acceptance of an illegal value is still a -04 type issue, but it points away from PASS.)
2. `full_text_source` key missing -> KeyError, exit 1 (loud; raw traceback, not a clean message).
3. `text` int, `source_id` int -> TypeError from normalize(), exit 1 (loud by accident, not by validation).
4. Non-JSON line -> JSONDecodeError; JSON array line -> TypeError. Loud.
5. Empty `text` -> UNGROUNDABLE; whitespace-only text -> UNGROUNDED. Fail-closed.
6. Summary-only citation -> UNGROUNDABLE (promise (a) holds for FACTUAL); NUMERIC summary-only -> UNGROUNDABLE; RELATIONAL summary-only -> UNVERIFIED_RELATION; relational verbatim+summary -> UNVERIFIED_RELATION.
7. Mixed cite [S1 verbatim][S2 summary] -> GROUNDED via the verbatim source only; tiers ran on verbatim only. Per spec, not a finding.
8. Citation id forms: `[s1]` -> UNCITED; `[S01]` -> UNVERIFIED_CITATION; `[source:S1]` -> UNVERIFIED_CITATION. All fail closed.
9. Extremely long text (~1MB filler + sentence) -> GROUNDED correctly, no crash/timeout. Store text equal to the claim itself -> GROUNDED: by design (store is trusted evidence); forging it is a store-tampering question covered by -04, not a new hole.
10. Absence claim over summary-only store: my fixture failed the 2-query rule for BOTH verbatim and summary stores (UNVERIFIED_ABSENCE), so summary-laundering of absence was NOT demonstrated either way. Note (unrun): `ground` passes `source_texts` from ALL store records without a `full_text_source` filter (ground_check.py:2575) — worth a targeted probe next round.
Denominator / promise (c) — each appended to a cited grounded sentence, all scored UNCITED -> gate FAIL/NEEDS_WORK:
11. blockquote `> X`; list item `- X`; table cell; image alt `![X](x.png)`; link text `[X](url)`; footnote `[^1]: X`; `<p>X</p>`; `<details><summary>X</summary>`; `<script>X</script>`; inline code span `` `X` ``; no terminal punctuation; setext header `X\n===`; `#X` without space; zero-width-space inside words; `## Incidents` + list item.
12. HTML entity `&lt;!--` ... `-->`; `<pre>&lt;!--</pre>`: not stripped, all text scored.
13. Backslash-escaping BOTH delimiters (`\<!--` ... `--\>`): closer not matched, all scored (only the `-->` bare closer in -07 works).
14. Double-backtick multi-line span inside a tilde fence to desynchronise `_CODE_SPAN_RE` pairing: over-protects, all scored (fail-closed).
15. Nested comment `<!-- a <!-- b --> X -->`: X scored. Unterminated `<!-- X`: scored.
16. `X;` + blank + cited sentence (semicolon propagation across paragraphs): X inherited [S1] and read UNGROUNDED — scored, not escaped.
17. `A [S1] and X.` compound: not split (left has citation mid-sentence), whole sentence UNGROUNDED.
18. Yes/no answer "No, it did not." is NON_CLAIM but the question carrying the content is scored UNCITED -> FAIL.
19. Regional-indicator letters "🇲🇴🇳🇬🇴 🇱🇴🇸🇹 🇩🇦🇹🇦." -> NON_CLAIM, PASS — refuted as a finding: they render as flag emoji, not readable text.
20. Transition glue "Therefore." -> NON_CLAIM (correct; no content).

Attack count: 83 gate runs across 6 batches (a1-a6 in scratch), 9 findings (0 ERROR-B, 3 denominator-escape, 5 silent-repair incl. provenance, 1 cosmetic).
