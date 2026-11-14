# Incident review: report builder degradation on Tuesday

Engineers restored normal service after 16 minutes. The data team was paged within 12 minutes of the first alert. The report builder service began returning errors on Tuesday at 16 minutes past the hour.

Deployments happen on weekday mornings.

The dashboard did not show the error rate until the second minute. The alert fired on the first failed health check. The runbook covers the restart steps. It does not cover a full disk on the primary database.

About 41 percent of requests failed at the peak. The response group was made up of the on-call engineer, a database specialist and an incident lead. The error rate stayed above 41 percent for 12 minutes. The planned disk alert never reached the data team. The vendor stated that the earlier maintenance "was not related to the outage".

A follow-up review is scheduled for the following week. Traffic was moved to the standby region while the fix was prepared. The primary database was restarted twice during the response. A status page notice went out 12 minutes after the page.

The status page is hosted separately from the main site.
