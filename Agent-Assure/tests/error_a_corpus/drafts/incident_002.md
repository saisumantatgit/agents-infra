# Incident review: billing degradation on Monday

- A follow-up review is scheduled for the following week [S1].
- The queue broker was restarted twice during the response [S1].
- The root cause was a runaway batch job on the queue broker [S1].
- The expected automatic rollback never ran [S1].
- About 31% of requests failed at the peak [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:08 | Service restored | Error rates returned to normal [S1]. |
| 10:09 | Alert fired | The health check failed three times in a row [S1]. |
| 10:19 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
| 10:54 | Mitigation started | Traffic moved to the standby region [S1]. |
