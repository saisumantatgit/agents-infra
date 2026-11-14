# Incident review: billing degradation on Monday

The billing service began returning errors on Monday at 35 minutes past the hour. The on-call engineer was paged within 6 minutes of the first alert. A status page notice went out 6 minutes after the page.

Engineers hid the failures of the report builder from customers - a complete fabrication.

Deployments happen on weekday mornings. The status page is hosted separately from the main site. The standby region is kept warm at all times.

The expected automatic rollback never ran. The primary database held 1756 queued jobs when it was restarted. About 40 percent of requests failed at the peak.

The primary database was restarted twice during the response. A follow-up review is scheduled for the following week. Engineers restored normal service after 35 minutes. The root cause was a bad configuration push on the primary database.

Past reviews are stored in a searchable archive. Alerts are routed through a paging service. Capacity was last reviewed in the spring.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:12 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:22 | Fix deployed | The configuration change was rolled back |
| 10:25 | Mitigation started | Traffic moved to the standby region |
| 10:45 | Service restored | Error rates returned to normal |
