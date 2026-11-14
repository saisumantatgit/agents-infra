# Incident review: billing degradation on Tuesday

- The read replica was restarted twice during the response [S1].
- The root cause was an expired certificate on the read replica [S1].
- The dashboard did not show the error rate until the second minute [S1].
- The alert fired on the first failed health check [S1].
- The fix was reviewed by a second engineer [S1].
- It was deployed without a staged rollout [S1].
- The read replica held 3350 queued jobs when it was restarted [S1].
- The planned disk alert never reached the data team [S1].
- The error rate stayed above 30% for 3 minutes [S1].
- The vendor stated that the earlier maintenance "was not related to the outage" [S1].
- The data team was paged within 3 minutes of the first alert [S1].
- Traffic was moved to the standby region while the fix was prepared [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:14 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:21 | Service restored | Error rates returned to normal [S1]. |
| 10:30 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:51 | Alert fired | The health check failed three times in a row [S1]. |
