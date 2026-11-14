## Follow-ups

The billing service began returning errors on Monday at 35 minutes past the hour [S1]. The on-call engineer was paged within 6 minutes of the first alert [S1]. A status page notice went out 6 minutes after the page [S1]. The expected automatic rollback never ran [S1].

The primary database held 1756 queued jobs when it was restarted [S1]. About 40 percent of requests failed at the peak [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:12 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
| 10:22 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:25 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:45 | Service restored | Error rates returned to normal [S1]. |
