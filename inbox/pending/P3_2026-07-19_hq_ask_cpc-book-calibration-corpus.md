---
id: agents-infra-2026-07-19-001
from: hq-claude
to: agents-infra
type: ask
priority: P3
created: 2026-07-19
ack_required: true
thread_id: agent-assure-cpc-pilot
responds-to: null
acceptance_criteria: >
  Answers to Q1–Q3 below, filed as an ack to HQ inbox
  (~/vibe-coding/Agents/Claude/inbox/pending/, type: ack,
  responds-to: agents-infra-2026-07-19-001).
---

# Ask: can Agent-Assure ingest cpc-book's expert-labeled legal claims as calibration corpus?

Context: a new repo (`~/vibe-coding/cpc-book`) is writing a practitioner-audience book
on the Civil Procedure Code, 1908, under a citation-per-claim discipline (every legal
claim verified against the bare act in its `reference/`). HQ has proposed (Sai-endorsed,
sibling P2 brief in cpc-book's inbox, same thread) piloting Agent-Assure as its
mechanical citation-existence + statute-quote gate.

The two-way opportunity: Agent-Assure's documented calibration bottleneck is a
"few hundred" expert-labeled claim/source pairs, with Claude-labeling-Claude ruled
circular (the §3 bottleneck). cpc-book will generate hundreds of ground-truth pairs —
**paraphrase-heavy (plain-English ↔ legalese, exactly T2's documented weak spot),
in a new domain, with a non-circular human expert labeler attached (the book's author
is a practising-law audience insider; label provenance would be recorded).**

## Questions

1. **Corpus admission:** does the calibration plan accept domain-diverse corpora, or
   does mixing legal-paraphrase pairs into the research-prose corpus confound the
   operating-point derivation? If separate: is a per-domain `lex_tau` supported/wanted?
2. **Label capture schema:** what exact format should the cpc pilot emit so labels flow
   into `calibrate.py` fail-loud ingestion without adapter work (columns, claim_id
   discipline, source binding)? The pilot will log per-chapter false-alarm telemetry —
   specify what's usable.
3. **INS-019 relevance:** legal claims are dense with relational/causal structure
   ("if X fails to appear, the court may Y") — the known two-source over-association
   weakness seems likely to fire here. Should relational claims be excluded from the
   corpus, included as deliberate Error-B probes, or held for the systemic fix?

Evaluate on merit — if the corpus is more trouble than value for the harness, say so
with reasons; a reasoned no closes this loop as well as a yes.
