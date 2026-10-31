# Gate conditions

| Gate | Condition |
|---|---|
| `PASS` | **empty retained appendix** (zero violation-class verdicts) AND score ≥ threshold [S1] |
| `NEEDS_WORK` | score ≥ 60 AND (any retained violation OR below threshold) [S1] |
| `FAIL` | score < 60 — **checked first**, so a sub-60 score is `FAIL` even when other overrides apply [S1] |
