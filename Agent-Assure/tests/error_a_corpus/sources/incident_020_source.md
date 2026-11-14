# Incident review: image resizer degradation on Tuesday

The primary database was restarted twice during the response. The root cause was a runaway batch job on the primary database. Engineers restored normal service after 32 minutes.

Alerts are routed through a paging service. Capacity was last reviewed in the spring. The standby region is kept warm at all times.

The expected automatic rollback never ran. The error rate stayed above 78% for 7 minutes. About 78% of requests failed at the peak.

Traffic was moved to the standby region while the fix was prepared. The data team was paged within 7 minutes of the first alert. A status page notice went out 7 minutes after the page. A follow-up review is scheduled for the following week.

Dashboards refresh every 32 seconds. The service is run by a team of 7 engineers. Runbooks live in the shared wiki.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:29 | Service restored | Error rates returned to normal |
| 10:39 | Fix deployed | The configuration change was rolled back |
| 10:55 | Alert fired | The health check failed three times in a row |
| 10:56 | Page acknowledged | The on-call engineer opened the dashboard |
