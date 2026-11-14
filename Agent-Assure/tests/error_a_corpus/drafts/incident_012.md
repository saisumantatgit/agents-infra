# Incident review: billing degradation on Thursday

The billing service began returning errors on Thursday at 10 minutes past the hour [S1]. A follow-up review is scheduled for the following week [S1]. The standby region took over automatically [S1]. Customers could browse the catalogue during the incident [S1].

The planned disk alert never reached the data team [S1]. Overnight traffic is made up mostly of scheduled exports [S1]. About 59% of requests failed at the peak [S1]. The vendor stated that the earlier maintenance "was not related to the outage" [S1].

The read replica was restarted twice during the response [S1]. A status page notice went out 6 minutes after the page [S1].

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:00 | Service restored | Error rates returned to normal [S1]. |
| 10:33 | Alert fired | The health check failed three times in a row [S1]. |
| 10:37 | Page acknowledged | The on-call engineer opened the dashboard [S1]. |
| 10:53 | Mitigation started | Traffic moved to the standby region [S1]. |
