# Round 12 — my conclusion, written BEFORE the adversary was dispatched

Solo gate (global rules): the conclusion is fixed first, the adversary is read
only after, and the outcome is logged `challenged | upheld/corrected`. A check
whose severity the checked party sets unobserved is not a check.

**Scope of this round:** D-63 (J-43 spelled quantities), D-65/D-66 (J-39
endpoint phrases + the shared `_endpoint_in_window` predicate), D-68 (J-44
symmetric plural stem). Nothing else in the gate changed in this window.

## What I claim

1. **No new Error-B.** All three changes are net-tightening on the relational
   branch. J-43 adds a refusal that did not exist. J-39 grows the needle
   (anchors unchanged, phrase extends leftward only). J-44 is the one
   loosening — and it is bounded to the NUMBER of an endpoint word, under the
   longer needle J-39 installed, with triggers excluded by an AST guard.
2. **The one loosening cannot reach a trigger.** `_relation_asserted` matches
   the trigger lexicon with `_contains_word` directly; `_stem` is never called
   in it.
3. **Every new "I don't know" points away from PASS.** `spelled_quantity_ok`
   returns False when there are phrases and no sources. `extract_arguments`
   returns None (→ UNVERIFIED_RELATION) when either side resolves to the empty
   phrase, including the all-numeric side that previously fell back to a bare
   digit. `_endpoint_in_window("")` is False, never vacuously True.
4. **The corpus measures J-39 and partly J-44, and does NOT measure J-43.**
   7/7 relational rows now carry multi-token endpoints (previously one token
   each) and no verdict moved; 3/7 carry an s-final endpoint token. Zero rows
   carry a spelled number inside a relational claim, so D-63's Error-A is
   unmeasured and stated as such.
5. **A=0.320 / B=0.000 (n=52, CR-004 provenance) is preserved**, on the
   evidence that the regenerated corpus is byte-identical and the gold md5 is
   unchanged.

## Where I think the adversary will find something

Named in advance so the round cannot be graded on a moving target:

- **`_ENDPOINT_PHRASE_STOPS` is a list I wrote by hand.** I argue function
  words are a closed class; a missing member is an Error-A, and a member that
  should NOT be there shortens a phrase toward the single-token state J-39
  exists to leave. `"no"` is in `_STOP_WORDS`/`_HEAD_NOUN_STOPS` reuse — if a
  NEGATION can end a run, an endpoint may lose the word that reverses it.
- **The clause-break rule reads the RAW token's trailing punctuation.** A
  parenthetical or a quoted phrase may end a run where no clause ends.
- **`_is_quantity_token` treats any digit-bearing token as a quantity.** An
  identifier that is part of an endpoint's identity — "S3 bucket", "GPT-4",
  "Type 1" — is therefore dropped from the phrase.
- **The plural stem can collide**: a word whose singular is another word
  ("lens" → "len"), or an s-final non-plural ("diabetes" → "diabete").
- **J-43 scoped to RELATIONAL only** leaves the ABSENCE path's spelled-figure
  hole open, as the register says. I claim that is a scope decision, not an
  oversight — the adversary should test whether it is reachable as Error-B.
