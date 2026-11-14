# Incident review: image resizer degradation on Tuesday

The root cause was an expired certificate on the primary database. A status page notice went out 8 minutes after the page. Traffic was moved to the standby region while the fix was prepared.

The checkout service holds 81 entries.

The status page is hosted separately from the main site.

They could not complete a purchase. Customers could browse the catalogue during the incident. The standby region took over automatically. No orders were lost during the failover.

The vendor stated that the earlier maintenance "was not related to the outage". The error rate stayed above 65 percent for 8 minutes. Overnight traffic is made up mostly of scheduled exports. The expected automatic rollback never ran. The primary database held 4960 queued jobs when it was restarted.

The primary database was restarted twice during the response. The image resizer service began returning errors on Tuesday at 7 minutes past the hour. The platform team was paged within 8 minutes of the first alert. A follow-up review is scheduled for the following week.

Past reviews are stored in a searchable archive.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:06 | Service restored | Error rates returned to normal |
| 10:36 | Fix deployed | The configuration change was rolled back |
| 10:43 | Alert fired | The health check failed three times in a row |
| 10:55 | Page acknowledged | The on-call engineer opened the dashboard |
