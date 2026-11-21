# Adversarial review: Error-A map (OVN-1121, 2026-11-21)

Target: `/Users/saisumanth/vibe-coding/Agents/ai-overnight-1121/Agent-Assure/reports/ERROR-A-MAP-2026-11-21.md`
Base measured: agents-infra main `d8c2ec0`. The ai-overnight-1121 worktree has identical `scripts/` and the
same Error-A `results.json` (cmp), but it lacks `tests/error_b_corpus_v2`, so all gate runs used the main
checkout.

Read-only on repo files. The candidate gates are scratch WRAPPERS that import the real `ground_check.py`
and monkeypatch one function:
- `map/pbase/scripts/ground_check.py`: hedge window stops at a sentence boundary.
- `map/c2base/scripts/ground_check.py`: claim-side `percent` suffix.

Each mirror's other files are symlinks to main. No repo file was edited.

**Verdict: the decomposition reproduces exactly; the headline figure and the hedge recommendation do not
hold.** Measured, the sentence-boundary stop frees 351 claims, not up to 658 or 541. It also certifies
2 more fabrication drafts, which fails the map's own ship criterion, and it opens 5 attack shapes. The
attacks the map names are not among the 5. Separately, main certifies a live attribution fabrication today.

Format: claim | verdict | evidence. Ordered by severity.

## 1. Hedge window: the sentence-boundary stop (recommendation 2)

**1a.** Claim: a hedge that governs across a full stop exists ("Critics disagree. They claim X." or
"That is false: X"), so the stop needs an Error-B check (l.40). The coordinator's brief adds "Not so. X".
| **CORRECTED: the named examples are not the attacks** |
Evidence (`map/probe.py`, main vs patched, same draft `<claim> [S1].`): all three stay refused on the
patched gate.
- "They claim X": the hedge sits in X's own sentence.
- "That is false: X": a colon is not a sentence boundary.
- "Not so. X": the paragraph rule refuses it.

The shapes that DO become new PASSes (main refuses, patched certifies PASS):
- `The vendor says:\n<claim>.` (attribution, colon, line break)
- `A spokesman said:\n\n> <claim>.` (blockquoted attribution)
- `Larch Holdings denies the report. <claim>.` (the previous sentence denies the claim and names its subject)
- `Suppose the worst happens. <claim>.`
- `In the bad scenario the board would act. <claim>.`

5 of 15 probes. Colon-introduced quotes and blockquotes are ordinary news and report prose.

**1b.** Claim: "541 of 682 hedge refusals have the hedge word in an earlier sentence"; 37 in the claim's
own sentence; 104 not found (l.32-36).
| **CORRECTED** |
Evidence (`map/hedge.py`, the gate's own `_tokenize`, `_SPAN_HEDGE_TOKENS` and `_SPAN_HEDGE_LOOKBACK`=5,
`ground_check.py:1646-1665`): all 682 claims are found (**0 not found**; the 104 came from the map's own
tokenizer). The split is:

| Where the hedge sits | Claims |
|---|---:|
| Every occurrence's last hedge is in an earlier sentence | 576 |
| At least one occurrence hedged in its own sentence | 51 |
| An occurrence with no hit in the window (the hedged segment is a later unit inside the claim) | 26 |
| Mixed | 29 |

The upper bound by the map's own definition is therefore 576, not 541.

**1c.** Claim: the stop could free up to 541 segments (l.38, l.47).
| **CORRECTED by measurement** |
Evidence: full corpus run on the patched gate (`map/ea_patched.json`): **+351 claims (2044→2395), 0 lost,
PASS drafts 5→11**. All 351 have hedge as their first cause. The rest stay refused because the next rule in
line catches them: previous-sentence or paragraph denial. Example: "…is not documented here." holds a
forward-pointing "here", so DENIAL_PREVIOUS refuses the claim. The patch fails closed if the token-to-text
mapping breaks; the fallback count was 0 in the 12 drafts checked (`map/stats.py`).

**1d.** Claim: it ships only if both fabrication corpora show no rise in any class; "even one new certified
fabrication" flips it (l.47).
| **The candidate FAILS this criterion** |
Evidence (`map/eb_patched.json` vs main `results.json`):
- **v1: certified PASS 7→9, in class denied_2back (1→3: faq_17, hr_policy_11)**. In both drafts the
  fabrication already escaped through the "cooked up" hole (D-122). The stop freed the draft's other
  refused claims, so the draft is now certified.
- v1: escaped 11→11, unchanged. v2: 0/0, unchanged.

Under any Error-A relaxation, a draft that carries an already-escaping fabrication can tip to PASS. So a
"no new certified fabrication" criterion also measures existing holes, and the cooked-up hole has to be
closed before this measurement means anything.

**1e.** Missing from the map: the code says this stop cannot be written where the map implies.
| **OMISSION** |
Evidence: `ground_check.py:7006-7010` says `_span_is_hedged` receives a token list, `_tokenize` strips
punctuation, and "sentence boundaries are unrecoverable inside it… this is the reason J-70's narrow repair
cannot be written at that layer". The scratch patch only works by recovering the text through an
object-id registry, which is not shippable. The candidate needs a restructure of the T1 call path. That is
real build cost, and Codex's brief needs to say so.

## 2. Live Error-B on main, found along the way (not caused by any candidate)

**2a.** Finding.
| **NEW, live on main** |
Evidence (`map/probe.py`, `map/probe2.py`):
- `According to an anonymous forum post, <claim>.` certifies **PASS**, claim GROUNDED. "according" is the
  6th token back, one past the 5-token window. Control: `According to a forum post, <claim>.` (5 back) is
  refused.
- `According to an anonymous forum post:\n\n<claim>.` also PASSes, as does
  `Per the vendor's press release.\n<claim>.`.

The only signal is the display-only diagnostic `cited_sentence_may_not_assert_claim`, which per ADR-008
never gates. The window length is a property the author controls: one adjective defeats it, which is the
CLAUDE.md "never key a moat rule on a surface property" class. Its factivity whitelist covers verbs, not
"according to" / "per". I did not find it registered: one vector, a grep of `according` across
`tests/red_team_moat` and `tests/test_*.py`.

## 3. The headline and the map table

**3a.** Claim: the cause decomposition of 1,946 refused claims (first refused segment; list-ordinal and
spelled-percent overrides).
| **UPHELD, exact** |
Evidence (`map/decomp.py`): hedge 658, list ordinal 406, next-sentence denial 174, UNVERIFIED_ABSENCE 120,
spelled percent 103, UNCITED 99, other 386 (11 kinds); 3,990 claims, 1,946 refused. 9 claims satisfy both
the ordinal and the percent override, and the ordinal wins. The first-cause attribution hides 24 hedge
claims behind another cause. Sole-cause counts: hedge 650/658, ordinal 399/406, percent 103/103.

**3b.** Claim: three rulings "would address up to 1,167 of the 1,946 honest claims (60%)" (l.3, l.27).
| **CORRECTED** |
The sum uses refused counts (658+406+103) where measured gains exist, including the map's own:

| Ruling | Measured gain |
|---|---:|
| Hedge stop (this review) | 351 |
| C1u (15 Nov pack, at `10373da`) | 286 |
| C2 (re-measured on `d8c2ec0`, 3c) | 69 |
| **Sum** | **706 (36%)** |

The map's own body names 541 as the hedge bound, yet the headline uses 658. "Up to 1,167" is not an upper
bound on any ruling actually proposed.

**3c.** Claim: recommendation 1, C2 "N percent", YES (+69, 0 of 11 attacks pass).
| **UPHELD, re-measured on `d8c2ec0`** |
The map cites a measurement taken on `10373da`. The 15 Nov attack tools under `/private/tmp/claude-501/
ovn1115-q4/tools/` no longer exist, so "0 of 11" cannot be re-run. Re-measured here (`map/c2base`):
- Error-A: **+69, 0 lost**, PASS 5→8.
- v1: no fabrication draft moved to PASS (2 FAIL→NEEDS_WORK); control PASS 190→195.
- v2: 0 certified; control PASS 93→103.
- My own 12 attacks (`map/c2probe.py`) produce **0 new PASS**: count, percentile, percentage points, `%`
  symbol, other subject, 8.5, denied, `per cent`, fell, hedged, basis points, "of X, 85 percent".

The recommendation holds on current main.

**3d.** Claim: C1u row: "2026-11-15 pack measured +292"; status "my recommendation was NO" (l.24); rec 4
"I'm keeping my 15 Nov NO".
| **CORRECTED, twice** |
1. +292 is **C1 as stated** (8 of 12 targeted fabrications PASS). C1u is **+286** (4 of 12 still PASS)
   (`ERROR-A-RULING-PACK-2026-11-15.md`, results table and C1 section).
2. The 15 Nov record disagrees with itself. The pack says **"SHIP-WITH-CEILING (C1u form)"**, and so does
   the system-of-record row `RATIFICATION-REGISTER-2026-08-30.md:1895` (D-116). Only
   `docs/logbook/overnight-2026-11-15-progress.md:51` says "recommend NO". Saying "my recommendation was
   NO" to Sai hides that the register says otherwise. The register row needs an amendment, or the map
   should state the reversal and its date.

**3e.** Claim: rec 4's reason, "keyed on capitalisation, which this project has already lost to twice
(round 4)".
| **CORRECTED (minor); the recommendation stands** |
CLAUDE.md records one capitalisation loss (round 4, Title Case); round 3 was a length rule. The objection
itself is sound: the 4 C1u slips are exactly the capitalised forms an attacker can choose. Keeping NO is
defensible. The proposed redesign (drop the ordinal only where the source line starts with the same
ordinal) is unmeasured.

**3f.** Claim: row 3 cites "about 91 of 174".
| **CORRECTED (minor)** |
My estimate was about 91 of **183**: claims with any next-sentence-denial segment, by a rough lexical
classification. It was not of the 174 first-cause claims.

**3g.** Claims: the fabrication corpora hold 504 drafts (v1+v2); the hedge window is 5 tokens with the
listed words.
| **UPHELD** | 280+224; `ground_check.py:1646-1665`.

## Load-bearing assumption

The patched hedge gate in 1c and 1d stands in for the candidate Codex would build. It treats `[.!?]` plus
whitespace, or a newline, as the boundary. A boundary that also stops at `:` or `;` would free more and
open more; one that ignores newlines would close the colon/line-break attacks in 1a and free less.
Codex's candidate has to fix the definition before any of these numbers apply.
