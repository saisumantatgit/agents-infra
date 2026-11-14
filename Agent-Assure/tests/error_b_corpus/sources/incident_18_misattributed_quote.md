# Incident review: report builder degradation on Tuesday

A status page notice went out 8 minutes after the page. The root cause was an expired certificate on the read replica. A follow-up review is scheduled for the following week.

Jun said the report builder "will stay in place until the end of the year". Omar said the queue broker "can be trusted by every group".

The review follows the blameless format used by the company. Dashboards refresh every 32 seconds. Runbooks live in the shared wiki.

The alert fired on the first failed health check. The dashboard did not show the error rate until the second minute. It does not cover a full disk on the read replica. The runbook covers the restart steps.

The read replica held 1688 queued jobs when it was restarted. Overnight traffic is made up mostly of scheduled exports. The incident lead wrote that the dashboards "cannot show per-region errors yet". About 21% of requests failed at the peak. The planned disk alert never reached the data team.

Traffic was moved to the standby region while the fix was prepared. The report builder service began returning errors on Tuesday at 32 minutes past the hour. The read replica was restarted twice during the response. Engineers restored normal service after 32 minutes.

The status page is hosted separately from the main site. Capacity was last reviewed in the spring. The service is run by a team of 8 engineers.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:00 | Fix deployed | The configuration change was rolled back |
| 10:28 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:49 | Service restored | Error rates returned to normal |
| 10:53 | Mitigation started | Traffic moved to the standby region |
