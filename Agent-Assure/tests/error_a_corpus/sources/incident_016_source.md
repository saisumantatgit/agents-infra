# Incident review: image resizer degradation on Saturday

The primary database was restarted twice during the response. The root cause was an expired certificate on the primary database. Engineers restored normal service after 27 minutes.

Deployments happen on weekday mornings. The status page is hosted separately from the main site. The standby region is kept warm at all times.

The alert fired on the first failed health check. The dashboard did not show the error rate until the second minute. Customers could browse the catalogue during the incident. They could not complete a purchase.

The primary database held 2922 queued jobs when it was restarted. The expected automatic rollback never ran. The incident lead wrote that the dashboards "cannot show per-region errors yet". About 84 percent of requests failed at the peak. Overnight traffic is made up mostly of scheduled exports.

Traffic was moved to the standby region while the fix was prepared. The platform team was paged within 5 minutes of the first alert. The image resizer service began returning errors on Saturday at 27 minutes past the hour. A follow-up review is scheduled for the following week.

Dashboards refresh every 27 seconds. Past reviews are stored in a searchable archive. Capacity was last reviewed in the spring.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:13 | Alert fired | The health check failed three times in a row |
| 10:26 | Service restored | Error rates returned to normal |
| 10:27 | Mitigation started | Traffic moved to the standby region |
| 10:33 | Page acknowledged | The on-call engineer opened the dashboard |
