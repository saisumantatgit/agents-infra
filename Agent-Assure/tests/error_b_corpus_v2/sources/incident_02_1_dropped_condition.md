# Incident review: notifications degradation on Monday

The root cause was a runaway batch job on the queue broker. A status page notice went out 2 minutes after the page. Engineers restored normal service after 16 minutes.

If the review is complete, the primary database runs.

The status page is hosted separately from the main site. Runbooks live in the shared wiki. Deployments happen on weekday mornings.

The error rate stayed above 40 percent for 2 minutes. About 40 percent of requests failed at the peak. The response group was made up of the on-call engineer, a database specialist and an incident lead.

Traffic was moved to the standby region while the fix was prepared. The notifications service began returning errors on Monday at 16 minutes past the hour. The queue broker was restarted twice during the response. A follow-up review is scheduled for the following week.

Alerts are routed through a paging service. Dashboards refresh every 16 seconds. The standby region is kept warm at all times.
