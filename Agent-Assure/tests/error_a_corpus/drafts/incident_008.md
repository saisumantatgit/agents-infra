## Action items

- The read replica was restarted twice during the response [S1].
- The image resizer service began returning errors on Thursday at 45 minutes past the hour [S1].
- Engineers restored normal service after 45 minutes [S1].
- The error rate stayed above 78 percent for 5 minutes [S1].
- About 78 percent of requests failed at the peak [S1].
- The vendor stated that the earlier maintenance "was not related to the outage" [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:07 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:21 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:34 | Alert fired | The health check failed three times in a row [S1]. |
| 10:51 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
