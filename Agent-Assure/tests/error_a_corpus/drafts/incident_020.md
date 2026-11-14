# Incident review: image resizer degradation on Tuesday

- The primary database was restarted twice during the response [S1].
- The root cause was a runaway batch job on the primary database [S1].
- Engineers restored normal service after 32 minutes [S1].
- The expected automatic rollback never ran [S1].
- The error rate stayed above 78% for 7 minutes [S1].
- About 78% of requests failed at the peak [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:29 | Service restored | Error rates returned to normal [S1]. |
| 10:39 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:55 | Alert fired | The health check failed three times in a row [S1]. |
| 10:56 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
