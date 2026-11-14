# Incident review: report builder degradation on Tuesday

- A status page notice went out 8 minutes after the page [S1].
- The root cause was an expired certificate on the read replica [S1].
- The alert fired on the first failed health check [S1].
- The dashboard did not show the error rate until the second minute [S1].
- It does not cover a full disk on the read replica [S1].
- The runbook covers the restart steps [S1].
- The read replica held 1688 queued jobs when it was restarted [S1].
- Overnight traffic is made up mostly of scheduled exports [S1].
- The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1].
- About 21% of requests failed at the peak [S1].
- The planned disk alert never reached the data team [S1].
- Traffic was moved to the standby region while the fix was prepared [S1].
- The report builder service began returning errors on Tuesday at 32 minutes past the hour [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:00 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:28 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
| 10:49 | Service restored | Error rates returned to normal [S1]. |
| 10:53 | Mitigation started | Traffic moved to the standby region [S1]. |
