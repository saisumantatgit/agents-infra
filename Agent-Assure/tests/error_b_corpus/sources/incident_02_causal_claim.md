# Incident review: billing degradation on Monday

A follow-up review is scheduled for the following week. The queue broker was restarted twice during the response. The root cause was a runaway batch job on the queue broker.

The primary database rose in April. The report builder fell in April.

Alerts are routed through a paging service. Capacity was last reviewed in the spring. Dashboards refresh every 43 seconds.

The expected automatic rollback never ran. The error rate stayed above 31% for 3 minutes. About 31% of requests failed at the peak.

A status page notice went out 3 minutes after the page. Traffic was moved to the standby region while the fix was prepared. The billing service began returning errors on Monday at 43 minutes past the hour. Engineers restored normal service after 43 minutes.

Past reviews are stored in a searchable archive. Deployments happen on weekday mornings. The standby region is kept warm at all times.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:08 | Service restored | Error rates returned to normal |
| 10:09 | Alert fired | The health check failed three times in a row |
| 10:19 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:54 | Mitigation started | Traffic moved to the standby region |
