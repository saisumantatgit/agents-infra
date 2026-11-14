# Incident review: image resizer degradation on Tuesday

Engineers restored normal service after 17 minutes. A follow-up review is scheduled for the following week. The payments team was paged within 3 minutes of the first alert.

The service is run by a team of 3 engineers. Runbooks live in the shared wiki. Alerts are routed through a paging service.

It was deployed without a staged rollout. The fix was reviewed by a second engineer. The dashboard did not show the error rate until the second minute. The alert fired on the first failed health check.

The planned disk alert never reached the payments team. About 68 percent of requests failed at the peak. The response group was made up of the on-call engineer, a database specialist and an incident lead. The error rate stayed above 68 percent for 3 minutes. The vendor stated that the earlier maintenance "was not related to the outage".

The primary database was restarted twice during the response. Traffic was moved to the standby region while the fix was prepared. A status page notice went out 3 minutes after the page. The image resizer service began returning errors on Tuesday at 17 minutes past the hour.

Past reviews are stored in a searchable archive. The standby region is kept warm at all times. Deployments happen on weekday mornings.
