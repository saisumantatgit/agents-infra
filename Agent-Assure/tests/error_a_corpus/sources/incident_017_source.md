# Incident review: report builder degradation on Monday

The root cause was a bad configuration push on the primary database. The payments team was paged within 12 minutes of the first alert. The report builder service began returning errors on Monday at 48 minutes past the hour.

Deployments happen on weekday mornings. The standby region is kept warm at all times. The status page is hosted separately from the main site.

The vendor stated that the earlier maintenance "was not related to the outage". The primary database held 6527 queued jobs when it was restarted. About 85 percent of requests failed at the peak.

Engineers restored normal service after 48 minutes. Traffic was moved to the standby region while the fix was prepared. The primary database was restarted twice during the response. A follow-up review is scheduled for the following week.

Past reviews are stored in a searchable archive. Runbooks live in the shared wiki. Dashboards refresh every 48 seconds.
