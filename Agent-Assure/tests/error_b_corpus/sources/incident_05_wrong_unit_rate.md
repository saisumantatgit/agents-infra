# Incident review: image resizer degradation on Tuesday

The payments team was paged within 8 minutes of the first alert. The image resizer service began returning errors on Tuesday at 23 minutes past the hour. The read replica was restarted twice during the response.

The checkout service takes 35 minutes to complete. The checkout service holds 32 entries.

The standby region is kept warm at all times.

The standby region took over automatically. No orders were lost during the failover. It does not cover a full disk on the read replica. The runbook covers the restart steps.

The error rate stayed above 74 percent for 8 minutes. Overnight traffic is made up mostly of scheduled exports. The expected automatic rollback never ran. The incident lead wrote that the dashboards "cannot show per-region errors yet". The read replica held 1967 queued jobs when it was restarted.

Engineers restored normal service after 23 minutes. Traffic was moved to the standby region while the fix was prepared. A follow-up review is scheduled for the following week. A status page notice went out 8 minutes after the page.

Capacity was last reviewed in the spring.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:39 | Service restored | Error rates returned to normal |
| 10:40 | Mitigation started | Traffic moved to the standby region |
| 10:41 | Alert fired | The health check failed three times in a row |
| 10:45 | Fix deployed | The configuration change was rolled back |
