# Incident review: image resizer degradation on Saturday

The primary database was restarted twice during the response [S1]. The root cause was an expired certificate on the primary database [S1]. The alert fired on the first failed health check [S1]. Customers could browse the catalogue during the incident [S1].

The expected automatic rollback never ran [S1]. The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1]. About 84 percent of requests failed at the peak [S1]. Overnight traffic is made up mostly of scheduled exports [S1].

Traffic was moved to the standby region while the fix was prepared [S1]. The platform team was paged within 5 minutes of the first alert [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:13 | Alert fired | The health check failed three times in a row [S1]. |
| 10:26 | Service restored | Error rates returned to normal [S1]. |
| 10:27 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:33 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
