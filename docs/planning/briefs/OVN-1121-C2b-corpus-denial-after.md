# Brief C2b: fabrication corpus — denial AFTER the claim, and source-word headings (tests only)

Executor: Codex. Branch `corpus-c2b` from main. No file under Agent-Assure/scripts/ changes.
Extend tests/error_b_corpus_v2 (keep v1 byte-identical) with:
1. denied_after: source "<claim>. <0-3 fillers> <DENIAL>." for EVERY phrase in v1 DENIALS plus
   "The press made that up.", "Reporters cooked that up.", "It was cooked up." ≥ 15 drafts, honest twins.
2. heading_from_source_words: draft heading made only of source words that restates a sentence the source
   denies (verbatim copy and reassembly); ≥ 15 drafts; twin = same draft without the heading.
3. Honest controls WITH headings (the v1/v2 controls have none, so heading rules are unmeasured there):
   every control in these two classes carries a source-copied heading.
Regenerate BASELINE.md on main; determinism proof; size < 5 MB. Final message: per-class table.
Expect E1/E2 PASSes on main — that is the point: the corpus must show them before the fixes land.
