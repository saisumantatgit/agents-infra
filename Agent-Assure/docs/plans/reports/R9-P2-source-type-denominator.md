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

## KNOWN ITEMS RE-CONFIRMED STILL OPEN (not re-reported)
- R8B-03 `#`+TAB -> PASS; 7 hashes `#######` -> PASS; full-width `＃` -> PASS (all NON_CLAIM, gate PASS 100.0).
- OI-MOAT-20 verb-final header `### PostgreSQL Fails` -> NON_CLAIM, PASS.
- OI-MOAT-31 header default `### Catastrophic MongoDB corruption` -> NON_CLAIM, PASS. (My NBSP variant lost the NBSP in the heredoc and reproduced this default instead; NBSP itself not re-tested.)

