# CR-006 — the delivery queue (J-48, J-43, J-39, J-44)

**SKELETON — in flight.** Written at step 5 of 6 per ADR-044 clause 3 (create the
output at run START; an artifact whose whole existence is one final write
delivers 0% when the run dies at 95%).

- Window: 2026-10-02, branch `delivery-queue-2026-10-02`, after PR #6 merged.
- Ratifications: D-62 … D-68.
- Suite at step 4: 785 passed, 2 skipped, 59 xfailed (from 751/2/63).
- Corpus: byte-identical at every step; gold md5 `6215b526d03147295b003d7ccb0d171f`.
- PENDING: round 12 adversary verdict, final suite counts, projection-vs-actual table.
