# Incident review: image resizer degradation on Tuesday

The payments team was paged within 8 minutes of the first alert [S1]. The image resizer service began returning errors on Tuesday at 23 minutes past the hour [S1]. The standby region took over automatically [S1]. No orders were lost during the failover [S1].

It does not cover a full disk on the read replica [S1]. The runbook covers the restart steps [S1]. The error rate stayed above 74 percent for 8 minutes [S1]. The expected automatic rollback never ran [S1].

The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1]. The read replica held 1967 queued jobs when it was restarted [S1]. Engineers restored normal service after 23 minutes [S1]. Traffic was moved to the standby region while the fix was prepared [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:39 | Service restored | Error rates returned to normal [S1]. |
| 10:40 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:41 | Alert fired | The health check failed three times in a row [S1]. |
| 10:45 | Fix deployed | The configuration change was rolled back [S1]. |
