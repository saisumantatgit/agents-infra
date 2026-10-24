# RED-TEAM W2B — numeric figure checks (2026-10-24)

**Verdict:** Error-B found. A claim with a wrong figure certifies **PASS 100.0 / exit 0** in 11 of 12 runs that remove or change what sits in front of the number (a sign, a comparator, a currency symbol, a leading decimal point, a per-mille sign). All are NEW. None is J-53 or J-72. One run (`(12)` accounting negative) held.

Branch `capture-contract-2026-10-10`. No repo edits apart from this report. Method: for each case, one verbatim source (store shaped like `demo/evidence-store.jsonl`, `retrieval_status: ok`) and a one-claim draft, run through `uv run python scripts/ground_check.py --draft d.md --store s.jsonl --json`. Harnesses and raw outputs: scratchpad `w2b/h.py`, `h2.py`, `h3.py`, `<case>/out.json`.

**Structural observation:** the verbatim and lexical tiers fire before `numeric_ok` and reject most figure swaps that need new words. ~60 such attempts came back UNGROUNDED, so for those cases the figure check was never the barrier. Any figure attack that gets through has to leave the claim a near-substring of the source. Deleting a prefix character does exactly that, and so does every finding below.

## W2B-01 — Sign dropped: a negative becomes a positive | CRITICAL
- **Mechanism:** `_NUMERIC_RE` (scripts/ground_check.py:907) and `_SOURCE_NUMERIC_RE` (:1955) both start at `\$?\d`. A leading `-` or U+2212 `−` is never captured, so the source's `-12%` parses as `(12.0, percent)` and the comparison at :2338 matches it against the claim's `12%`.
- **Reproduction (real output):** source `Acme posted a net margin of -12% in 2023 according to the annual report.` and claim `Acme posted a net margin of 12% in 2023 according to the annual report [S1].` gave `exit 0 PASS 100.0 [('GROUNDED', ...)]`. The U+2212 variant gave the same result: `exit 0 PASS 100.0`.
- **Status:** new.
- **Sibling:** W2B-02. Same root cause: characters in front of the digits are thrown away.

## W2B-02 — Comparator or approximation dropped (~, >, <, ≈, ≤, ±) | HIGH
- **Mechanism:** same regexes, :907 and :1955. A qualifier glyph in front of the number is not part of the token and nothing compares it.
- **Reproduction (real output, each source/claim pair differs only by the glyph):**
  - `~40%` → `40%`: `exit 0 PASS 100.0`
  - `>40%` → `40%`: `exit 0 PASS 100.0`
  - `<4%` → `4%`: `exit 0 PASS 100.0`
  - `≈40%` → `40%`: `exit 0 PASS 100.0`
  - `≤4%` → `4%`: `exit 0 PASS 100.0`
  - `±40%` (source says "changed by") → `40%`: `exit 0 PASS 100.0`
- **Status:** new.
- **Note:** the WORD forms ("about", "up to") were refused, but by the lexical tier (UNGROUNDED), not by the figure check.

## W2B-03 — Currency is never compared; only `$` is even recognised | HIGH
- **Mechanism:** `_parse_numeric_token` does `raw.lstrip("$")` (:2222) and returns a unit of `absolute` or `percent`, with no currency field. `€`, `£`, `¥` and `₹` are not in either regex, so they are dropped silently.
- **Reproduction (real output):**
  - source `Acme raised ¥40M ...`, claim `Acme raised $40M ... [S1]`: `exit 0 PASS 100.0`
  - `€40M` → `$40M`: `exit 0 PASS 100.0`
  - `₹40M` → `$40M`: `exit 0 PASS 100.0`
  - `£40M` → `$40M` (first batch): `exit 0 PASS 100.0`
- **Status:** new.
- **Sibling:** the docstring at :2297 promises "4 million USD", but the unit model has no currency dimension at all.

## W2B-04 — Leading decimal point dropped: .5% becomes 5% (10x) | HIGH
- **Mechanism:** both regexes require `\d` as the first character, so the source's `.5%` is matched as `5%`.
- **Reproduction (real output):** source `.5% of Acme users churned in 2023 ...` and claim `5% of Acme users churned in 2023 ... [S1]` gave `exit 0 PASS 100.0`.
- **Status:** new.
- **Note:** a mid-number truncation was refused: `1,240` → `240` gave UNVERIFIED_NUMBER.

## W2B-05 — Per-mille sign ignored: 4‰ becomes a bare 4 | MEDIUM
- **Mechanism:** `‰` is not a suffix in either regex. The source token reads as `4 absolute`, so it matches a claim's bare `4`.
- **Reproduction (real output):** `4‰` → `4`: `exit 0 PASS 100.0`.
- **Status:** new.
- **Limit:** a claim of `4%` would need the lexical tier to pass, and that was not demonstrated.

## W2B-06 — Rank marker dropped: #3 becomes a bare 3 | LOW
- **Reproduction (real output):** `ranked #3` → `ranked 3`: `exit 0 PASS 100.0`.
- **Meaning:** the claim keeps its meaning here. Recorded only as more evidence of the prefix blindness, not as a separate defect.

## Registered items (not counted as new)
- **J-53 ("per cent", Error-A):** probed with source `40 per cent` and claim `40`. Refused (UNGROUNDED, lexical tier), so no Error-B.
- **J-72 (X200 → 200):** probed with `Q3` → `Q2`. Refused (UNVERIFIED_NUMBER), the fail-closed direction that J-72 already records.

## TRIED AND HELD (all refused; real verdicts in scratchpad `<case>/out.json`)
- **Lexical tier refused (UNGROUNDED):** million/billion swaps, 1.5 billion vs 1500 million, bps vs %, basis points vs percent, percentage points vs % (also UNVERIFIED_NUMBER: `5% points`, `5 percent points`), kg→40000, `5 m` (metres) → `5M`, fell vs grew, ranges (10–20% → 20%, 10% to 20% → 20%), "about"/"up to" removed, figures in different sentences (3 variants), swapping which subject a % belongs to, fractions 1/2 and 3/4, `3x` → 3 and → 3%, 2 trillion → $2, 40K → 40000, lakh/crore, Rs, `4e6`, percentile, ordinals.
- **Figure check refused (UNVERIFIED_NUMBER):** 41% vs 40% (control), year shifted, date as a count (2019 stores), date as money, thousand/dozen/hundred inserted or removed, 4.5% → 4% and → 5%, 3rd/10 swapped, `$40MM` → `$40`, bn → billion with a different currency word, `(12) million` → `12 million`, `1,240` → `240`, spelled/digit swap, 3 min → 3 million, 5000000 m.
- **Absence path:** `There is no evidence ... 40%` gave UNVERIFIED_ABSENCE. No Error-B was found through the absence branch in this pass.

## Recommended repair (Systemic Fix)
Widen both numeric regexes to capture an optional leading sign, comparator or currency glyph (`[-−+±~≈<>≤≥]`, `[$€£¥₹]`), plus a leading `.` and a trailing `‰`. Carry `sign`, `comparator` and `currency` as fields on the parsed value, and require each one to match whenever the SOURCE has it, not only when the claim does. That direction matters: every finding above is the source qualifying a figure and the claim dropping the qualifier, and the existing rule only enforces dimensions the claim asserts. This repair is fail-closed, so it cannot create a new PASS, but it will refuse some claims that pass today (Error-A cost), so it needs Sai's call under the PASS-enabling/disabling escalation rule.
