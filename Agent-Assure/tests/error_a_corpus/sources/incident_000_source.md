# Incident review: report builder degradation on Tuesday

A status page notice went out 5 minutes after the page. Engineers restored normal service after 26 minutes. The cache cluster was restarted twice during the response.

The standby region is kept warm at all times.

No orders were lost during the failover. The standby region took over automatically. They could not complete a purchase. Customers could browse the catalogue during the incident.

Overnight traffic is made up mostly of scheduled exports. The planned disk alert never reached the payments team. The vendor stated that the earlier maintenance "was not related to the outage". The error rate stayed above 42 percent for 5 minutes. The cache cluster held 3768 queued jobs when it was restarted.

The payments team was paged within 5 minutes of the first alert. The root cause was a runaway batch job on the cache cluster. A follow-up review is scheduled for the following week. The report builder service began returning errors on Tuesday at 26 minutes past the hour.

The service is run by a team of 5 engineers.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:10 | Service restored | Error rates returned to normal |
| 10:17 | Alert fired | The health check failed three times in a row |
| 10:35 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:46 | Fix deployed | The configuration change was rolled back |
