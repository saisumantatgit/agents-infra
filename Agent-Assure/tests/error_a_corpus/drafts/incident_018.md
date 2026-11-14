# Incident review: image resizer degradation on Tuesday

The root cause was an expired certificate on the primary database [S1]. A status page notice went out 8 minutes after the page [S1]. Customers could browse the catalogue during the incident [S1]. The standby region took over automatically [S1].

The vendor stated that the earlier maintenance "was not related to the outage" [S1]. The error rate stayed above 65 percent for 8 minutes [S1]. Overnight traffic is made up mostly of scheduled exports [S1]. The expected automatic rollback never ran [S1].

The primary database was restarted twice during the response [S1]. The image resizer service began returning errors on Tuesday at 7 minutes past the hour [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:06 | Service restored | Error rates returned to normal [S1]. |
| 10:36 | Fix deployed | The configuration change was rolled back [S1]. |
| 10:43 | Alert fired | The health check failed three times in a row [S1]. |
| 10:55 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
