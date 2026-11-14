# Incident review: image resizer degradation on Thursday

The read replica was restarted twice during the response. The image resizer service began returning errors on Thursday at 45 minutes past the hour. Engineers restored normal service after 45 minutes.

Past reviews are stored in a searchable archive. Runbooks live in the shared wiki. Alerts are routed through a paging service.

The error rate stayed above 78 percent for 5 minutes. About 78 percent of requests failed at the peak. The vendor stated that the earlier maintenance "was not related to the outage".

The platform team was paged within 5 minutes of the first alert. A status page notice went out 5 minutes after the page. Traffic was moved to the standby region while the fix was prepared. The root cause was an expired certificate on the read replica.

Deployments happen on weekday mornings. Capacity was last reviewed in the spring. Dashboards refresh every 45 seconds.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:07 | Fix deployed | The configuration change was rolled back |
| 10:21 | Mitigation started | Traffic moved to the standby region |
| 10:34 | Alert fired | The health check failed three times in a row |
| 10:51 | Page acknowledged | The on-call engineer opened the dashboard |
