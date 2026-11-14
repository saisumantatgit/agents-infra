# Incident review: billing degradation on Saturday

Engineers restored normal service after 48 minutes. The primary database was restarted twice during the response. A follow-up review is scheduled for the following week.

Deployments happen on weekday mornings.

They could not complete a purchase. Customers could browse the catalogue during the incident. No orders were lost during the failover. The standby region took over automatically.

The incident lead wrote that the dashboards "cannot show per-region errors yet". The response group was made up of the on-call engineer, a database specialist and an incident lead. The expected automatic rollback never ran. The primary database held 3165 queued jobs when it was restarted. About 31% of requests failed at the peak.

The payments team was paged within 6 minutes of the first alert. Traffic was moved to the standby region while the fix was prepared. The billing service began returning errors on Saturday at 48 minutes past the hour. A status page notice went out 6 minutes after the page.

Past reviews are stored in a searchable archive.
