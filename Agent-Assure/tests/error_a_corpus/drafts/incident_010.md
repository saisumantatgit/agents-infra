## Lessons learned

Engineers restored normal service after 21 minutes [S1]. The search service began returning errors on Thursday at 21 minutes past the hour [S1]. They could not complete a purchase [S1]. Customers could browse the catalogue during the incident [S1].

The standby region took over automatically [S1]. The response group was made up of the on-call engineer, a database specialist and an incident lead [S1]. The vendor stated that the earlier maintenance "was not related to the outage" [S1]. About 48 percent of requests failed at the peak [S1].

The error rate stayed above 48 percent for 6 minutes [S1]. A status page notice went out 6 minutes after the page [S1]. Traffic was moved to the standby region while the fix was prepared [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:23 | Service restored | Error rates returned to normal [S1]. |
| 10:26 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
| 10:52 | Mitigation started | Traffic moved to the standby region [S1]. |
| 10:53 | Alert fired | The health check failed three times in a row [S1]. |
