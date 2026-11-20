# Incident review: billing degradation on Tuesday

The read replica was restarted twice during the response. The root cause was an expired certificate on the read replica. The billing service began returning errors on Tuesday at 4 minutes past the hour.

Only when the review is complete does the report builder run.

Alerts are routed through a paging service. The review follows the blameless format used by the company. Capacity was last reviewed in the spring.

The dashboard did not show the error rate until the second minute. The alert fired on the first failed health check. The fix was reviewed by a second engineer. It was deployed without a staged rollout.

The read replica held 3350 queued jobs when it was restarted. The response group was made up of the on-call engineer, a database specialist and an incident lead. The planned disk alert never reached the data team. The error rate stayed above 30% for 3 minutes. The vendor stated that the earlier maintenance "was not related to the outage".

The data team was paged within 3 minutes of the first alert. Traffic was moved to the standby region while the fix was prepared. A follow-up review is scheduled for the following week. Engineers restored normal service after 4 minutes.

The service is run by a team of 3 engineers. Dashboards refresh every 4 seconds. The status page is hosted separately from the main site.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:14 | Fix deployed | The configuration change was rolled back |
| 10:21 | Service restored | Error rates returned to normal |
| 10:30 | Mitigation started | Traffic moved to the standby region |
| 10:51 | Alert fired | The health check failed three times in a row |
