# R7 PATH B — Citation propagation red team

Date: 2026-09-12. Target: `_propagate_sentence_citation` (~L203),
`_propagate_across_semicolon` (~L238), `_conjunction_split` (~L173) of
`scripts/ground_check.py`. No file under `scripts/` or `tests/` was modified;
all drafts and stores live in the session scratchpad
(`/private/tmp/claude-501/.../scratchpad`, reproduced verbatim below).

## Verdict up front

- **Confirmed Error-B (gate PASS with an unsupported claim): 2 drafts, 1 distinct
  mechanism** — and that mechanism is **NOT propagation**. It is T1's
  residual-coverage check (set membership over the source's vocabulary).
- **The ";" hypothesis is CONFIRMED as behaviour and REFUTED as a hole.**
  Punctuation alone flips FAIL→PASS on byte-identical prose (evidence §2), and
  propagation crosses paragraph breaks and Markdown list-item boundaries
  (§4) — but propagation is *formally equivalent to the author typing the
  marker on that clause*, so it can never certify a claim that a direct
  citation would not also certify (§5, control run). It removes the `UNCITED`
  blocker; it does not widen the set of false claims that can reach PASS.

---

## 1. Store used for the primary findings

`storeB3.jsonl` (single verbatim source, field shape copied from
`tests/red_team_moat/fixtures/store_containment.jsonl`):

```json
{"source_id": "S1", "url": "https://example.com/s1", "file_path": null, "fetched_at": "2026-09-02T00:00:00Z", "tool": "mcp__exa__web_fetch_exa", "content_sha256": "aa", "text": "Redis handles 100K ops per second in our benchmark. AOF persistence was disabled during the run. The cluster was tested for three hours.", "full_text_source": "verbatim", "captured_via": "inline", "query_provenance": "redis benchmark aof"}
```

The source says the benchmark ran with **AOF persistence disabled**.

---

## 2. FINDING B3 — Error-B. Semicolon propagation + T1 residual coverage → PASS

Draft (`b3.md`), verbatim:

```
Redis handles 100K ops per second in our benchmark with AOF persistence; the cluster was tested for three hours [S1].
```

Gate JSON:

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark with AOF persistence [S1]", "verdict": "GROUNDED"}, {"index": 1, "kind": "FACTUAL", "text": "the cluster was tested for three hours [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 2, "vacuous": false}
EXIT=0
```

**Unsupported claim:** claim 0. S1 states AOF persistence was *disabled* during
the run; the draft asserts the 100K figure was obtained *with* AOF persistence.
The source nowhere supports that, and it is the exact opposite of what it says.

**Mechanism (one sentence):** the sentence-final `[S1]` propagates onto the
uncited left clause, and T1's span path then certifies it because the first
8 claim tokens are a verbatim n-gram of S1 anchored at the claim's subject and
every remaining content token (`aof`, `persistence`) merely *appears somewhere*
in S1 — set membership carries no notion of polarity, so `disabled` in the
source licenses `with` in the claim.

### 2a. The punctuation control — this is the hypothesis, isolated

Byte-identical prose with `.` in place of `;` (`b3ctl.md`):

```
Redis handles 100K ops per second in our benchmark with AOF persistence. The cluster was tested for three hours [S1].
```

```json
{"gate": "FAIL", "grounding_score": 50.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark with AOF persistence.", "verdict": "UNCITED"}, {"index": 1, "kind": "FACTUAL", "text": "The cluster was tested for three hours [S1].", "verdict": "GROUNDED"}], "retained_appendix": [{"index": 0, "text": "Redis handles 100K ops per second in our benchmark with AOF persistence.", "verdict": "UNCITED"}], "scored_claims": 2, "vacuous": false}
EXIT=1
```

**One keystroke — `;` vs `.` — is the entire difference between FAIL and PASS
for the same assertion against the same store.** The docstring's defence ("the
trailing `;` … is set by the author for grammatical reasons, not to satisfy the
gate") is an assumption about intent that an adversary simply declines to
honour. The project's own law — *never key a moat rule on a surface property
the author controls* — is violated on its face. What saves it is §5, not §2.

### 2b. Negative control — propagation alone buys nothing

`b1.md`: `Redis silently discards every write after a reboot; the cluster was tested for three hours [S1].`

```json
{"gate": "FAIL", "grounding_score": 50.0, "per_claim": [{"index": 0, "kind": "FACTUAL", "text": "Redis silently discards every write after a reboot [S1]", "verdict": "UNGROUNDED"}, ...], "retained_appendix": [{"index": 0, "verdict": "UNGROUNDED"}], ...}
EXIT=1
```

The inherited citation converts `UNCITED` → *run the tiers*, exactly as the
docstring claims. A fabrication with no lexical purchase on S1 still fails.
Propagation is an amplifier of tier holes, never a hole by itself.

---

## 3. FINDING B8 — Error-B. Same hole via the `" and "` path

Draft (`b8.md`), same store:

```
Redis handles 100K ops per second in our benchmark with AOF persistence and the cluster was tested for three hours [S1].
```

```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark with AOF persistence [S1]", "verdict": "GROUNDED"}, {"index": 1, "kind": "FACTUAL", "text": "the cluster was tested for three hours [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 2, "vacuous": false}
EXIT=0
```

Same unsupported claim, same mechanism; `_propagate_sentence_citation` rather
than `_propagate_across_semicolon` supplies the marker. Both propagation paths
are interchangeable for the attacker, which means a fix aimed at `;` alone
would close nothing.

---

## 4. Mechanism findings (no Error-B on their own, but they enlarge the blast radius)

### 4a. Propagation crosses a PARAGRAPH break (`b4.md`)

```
Redis handles 100K ops per second in our benchmark with AOF persistence;

The cluster was tested for three hours [S1].
```
→ `{"gate": "PASS", ... "retained_appendix": []}` (EXIT=0).

`_iter_raw_sentences` flattens syntok paragraphs, so "the IMMEDIATELY following
segment" is not "the rest of the same sentence" — it is the next sentence in
the *document*, blank line or not.

### 4b. Propagation crosses a Markdown LIST-ITEM boundary (`b6.md`)

```
- Redis handles 100K ops per second in our benchmark with AOF persistence;
- The cluster was tested for three hours [S1].
```
→ `{"gate": "PASS", ...}` (EXIT=0), claim 0 emitted as
`"- Redis handles 100K ops per second in our benchmark with AOF persistence [S1]"`.

This is the weakest point of the docstring's intent argument. A semicolon at the
end of a bullet is *standard list punctuation*, not a run-on sentence, and the
citation on the next bullet is by any ordinary reading a citation for that
bullet only. Here it silently certifies the previous bullet.

### 4c. A heading DOES stop it (`b5.md`)

Inserting `## Method` between the two blocks leaves claim 0 `UNCITED` and the
gate FAILs. The heading becomes an intervening raw sentence with no trailing
citation. Block-level containment is therefore accidental, not designed: it
depends on whether the intervening text happens to end in a marker.

---

## 5. Why the `;` rule is nonetheless not a NEW hole — the decisive control

Propagation's entire output is `left + " [Sx]"`. Everything downstream
(`classify`, `resolve`, `t1_verbatim`, `numeric_ok`) strips citation markers
before tokenizing, so a propagated claim is **bit-for-bit the claim the author
would have produced by typing `[Sx]` on that clause**. Direct control
(`b3direct.md`):

```
Redis handles 100K ops per second in our benchmark with AOF persistence [S1].
```
```json
{"gate": "PASS", "grounding_score": 100.0, "per_claim": [{"index": 0, "kind": "NUMERIC", "text": "Redis handles 100K ops per second in our benchmark with AOF persistence [S1].", "verdict": "GROUNDED"}], "retained_appendix": [], "scored_claims": 1, "vacuous": false}
EXIT=0
```

Same PASS, no semicolon, no propagation. **Propagation cannot manufacture a
verdict that a self-cited clause could not.** An adversary who wants a claim
grounded against S1 has a strictly simpler move available: cite S1. The
`;` rule's real cost is therefore *attribution*, not certification —

1. the gate rewrites the author's text and quotes it back with a marker they
   never typed (visible in every `per_claim.text` above), which is corrosive in
   the one artifact whose job is fidelity; and
2. an honest human author who deliberately left a clause uncited (because they
   knew it was their own inference) gets it silently certified whenever it
   happens to overlap the neighbouring source's vocabulary. That is a real-world
   Error-B *path*, but the defect it walks through is T1's, not propagation's.

**Recommendation:** do not patch the `;` discriminator — patching it would not
move Error-B, because §5 shows the same PASS is one keystroke away by direct
citation. Fix instead the mechanism §2 actually rode in on: T1's residual
coverage is unordered set membership, so a claim may append any content tokens
the source happens to contain (`aof`, `persistence`) in any polarity and stay
GROUNDED. That is the same family as RT4-03's argument swap, unclosed for
*modifiers* rather than subjects. Separately, and as a fidelity rather than moat
matter, propagation should not cross a paragraph or list-item boundary (§4a/4b):
restrict `following` to the same syntok paragraph, and require that the
semicolon segment and its donor be adjacent within it.

**Load-bearing assumption of this report:** that no code path downstream of
`decompose` treats a propagated marker differently from an authored one. I
verified this by reading (`_strip_citations` / `_CITATION_RE.sub` precede every
tokenization in `classify`, `t1_verbatim`, `numeric_ok`) and by the §5 control,
which produces an identical verdict. If some future tier reads marker position
rather than marker presence, §5 collapses and the `;` rule becomes a live hole.

---

## Families tried and unbroken

| # | Family | Result | What stopped it |
|---|---|---|---|
| 1 | Fabricated clause inherits a citation with no lexical purchase on the source (`b1.md`) | FAIL, `UNGROUNDED` | Propagation only converts `UNCITED` → run the tiers; T1 still has to fire. |
| 2 | Three-segment `;` chain — `A is one; B is two; C is three [S1].` | First segment stays `UNCITED` | `_propagate_across_semicolon` consults only the immediately following segment, and that segment's trailing regex needs a marker at *its* end. Chains do not cascade backwards. |
| 3 | Donor segment ending `[S1];` — `A is one; B is two [S1]; C is three [S2].` | No propagation to `A` | `_TRAILING_CITATIONS_RE` allows only `[.!?]` after the marker; `;` is not terminal punctuation, so `B is two [S1];` is not a donor. |
| 4 | Mid-sentence marker made to read as sentence-final (`... confirmed [S1] in a rebuttal.`, `... in Table 1 [S1] and ...`, `Acme Corp. [S1] disputes it.`) | No propagation | The `$` anchor on `_TRAILING_CITATIONS_RE` holds; I could not get syntok to end a segment immediately after a mid-sentence marker. |
| 5 | Overwriting a clause's own citation | Not reachable | Both propagators guard on `_CITATION_RE.search(...)` of the receiving text, and `_propagate_sentence_citation` runs on the already-semicolon-propagated string, so a clause that has a marker (its own or inherited) is skipped. |
| 6 | Propagation across a full stop | Not reachable | `body.endswith(";")` is required; a terminated sentence never inherits (confirmed by §2a). |
| 7 | Propagation across a heading (`b5.md`) | FAIL | The heading is an intervening raw sentence with no trailing citation. |
| 8 | Widening the source set for `numeric_ok` by inheriting `[S1][S2]` | Not exploitable | T1 runs per-source (RT3-03), and a number is a content token, so it must be in the *same* source's vocabulary to clear residual coverage. Cross-source number + span fails. |
| 9 | Quote-mining via `" and "` propagation (`b7.md`, `storeQM.jsonl`: a vendor-brochure line republished as fact) | PASS (EXIT=0) — **but not a Path B finding**: the direct-citation control `The appliance sustains 40 gigabits per second [S1].` also PASSes (EXIT=0). Propagation contributes nothing. This is the exact-containment / `_span_is_hedged` class (Path A): `brochure opened with a bold line:` contains no token in `_SPAN_HEDGE_TOKENS`, and the disclaimer sits in the *next* sentence, outside the 5-token lookback. Handing to whoever owns Path A. |
